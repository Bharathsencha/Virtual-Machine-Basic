# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
from .errors import VMError
from .qmp import qmp
import os
import shutil
import subprocess
import time
from pathlib import Path

def executable(name):
    path = shutil.which(name)
    if not path:
        raise VMError(f"Missing {name}. Install qemu-system-x86 and qemu-utils.", 503)
    return path

def kvm_available():
    return os.access("/dev/kvm", os.R_OK | os.W_OK)

def running(directory):
    try:
        return qmp(directory / "qmp.sock", "query-status")["status"] not in ("shutdown", "internal-error")
    except VMError as exc:
        # Refuse destructive operations if our QEMU is alive but QMP is unresponsive.
        try:
            pid = int((directory / "process.pid").read_text())
            args = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
            expected = f"unix:{directory / 'qmp.sock'},server=on,wait=off".encode()
            if expected in args:
                raise VMError("QEMU process is alive but QMP is unavailable; inspect its log and retry.", 409) from exc
        except (OSError, ValueError):
            pass
        return False

def launch(directory, config):
    binary = executable("qemu-system-x86_64")
    if config["console"] == "graphical" and not (os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY")):
        raise VMError("No graphical session available. Create a VM with serial console, or run the server from your desktop session.")
    (directory / "process.pid").unlink(missing_ok=True)
    for name in ("qmp.sock", "serial.sock"):
        (directory / name).unlink(missing_ok=True)
    command = [binary, "-name", config["name"], "-m", str(config["ram_mb"]), "-smp", str(config["cpus"]),
        "-accel", "kvm" if kvm_available() else "tcg", "-drive", f"file={directory / 'disk.qcow2'},format=qcow2,if=virtio",
        "-qmp", f"unix:{directory / 'qmp.sock'},server=on,wait=off", "-netdev", "user,id=net0", "-device", "virtio-net-pci,netdev=net0",
        "-serial", f"unix:{directory / 'serial.sock'},server=on,wait=off", "-monitor", "none"]
    if config["image_type"] == "iso":
        command += ["-cdrom", config["image_path"], "-boot", "order=dc"]
    if config["console"] == "serial":
        command += ["-display", "none"]
    with (directory / "qemu.log").open("ab") as log:
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    # Reap child exits without coupling VM lifetime to the web server.
    import threading
    threading.Thread(target=process.wait, daemon=True).start()
    for _ in range(40):
        if running(directory):
            (directory / "process.pid").write_text(str(process.pid))
            return
        if process.poll() is not None:
            raise VMError("QEMU failed: " + (directory / "qemu.log").read_text(errors="replace")[-1200:], 500)
        time.sleep(.1)
    raise VMError("QEMU is still starting. Refresh status before retrying.", 503)
