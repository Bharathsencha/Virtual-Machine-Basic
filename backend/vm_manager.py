# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
import json
import os
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path
from . import qemu_service as q

class VMManager:
    def __init__(self, root):
        self.root = Path(root).resolve()
        if "," in str(self.root) or ":" in str(self.root) or len(str(self.root)) > 65:
            raise RuntimeError("VM_DATA_DIR must be a short path without commas or colons (Unix socket limit).")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.root, 0o700)
        self.lock = threading.RLock()

    def directory(self, id):
        try:
            if str(uuid.UUID(id)) != id:
                raise ValueError()
        except ValueError:
            raise q.VMError("VM not found", 404)
        directory = self.root / id
        if directory.is_symlink() or not (directory / "config.json").is_file():
            raise q.VMError("VM not found", 404)
        return directory

    def get(self, id):
        directory = self.directory(id)
        config = json.loads((directory / "config.json").read_text())
        active = q.running(directory)
        return dict(config, status="running" if active else "stopped", uptime_seconds=max(0, int(time.time() - config.get("started_at", time.time()))) if active else None,
            console_instructions=("QEMU opens a window on the server desktop." if config["console"] == "graphical" else f"Connect locally: socat -,raw,echo=0 UNIX-CONNECT:{directory / 'serial.sock'}. Guest must enable ttyS0."))

    def list(self):
        return [self.get(p.name) for p in sorted(self.root.iterdir()) if p.is_dir() and not p.is_symlink() and (p / "config.json").is_file()]

    def save(self, directory, config):
        temporary = directory / "config.tmp"
        temporary.write_text(json.dumps(config, indent=2))
        temporary.replace(directory / "config.json")

    def create(self, spec):
        with self.lock:
            if any(vm["name"].lower() == spec.name.lower() for vm in self.list()):
                raise q.VMError("VM name already exists", 409)
            image = Path(spec.image_path).expanduser()
            if not image.is_absolute() or not image.is_file() or not os.access(image, os.R_OK):
                raise q.VMError("Image must be an existing readable absolute file path")
            image = image.resolve()
            if image.is_relative_to(self.root) or any(c in str(image) for c in (",", "\n", ":")):
                raise q.VMError("Use an image outside VM storage with no commas, colons, or newlines in its path")
            binary = q.executable("qemu-img")
            id = str(uuid.uuid4())
            directory = self.root / id
            directory.mkdir(mode=0o700)
            try:
                disk = str(directory / "disk.qcow2")
                if spec.image_type == "iso":
                    command = [binary, "create", "-f", "qcow2", disk, f"{spec.disk_gb}G"]
                else:
                    info = json.loads(subprocess.run([binary, "info", "--output=json", str(image)], check=True, capture_output=True, text=True, timeout=30).stdout)
                    if info.get("backing-filename") or info["format"] not in ("raw", "qcow2"):
                        raise q.VMError("Use a standalone raw or qcow2 disk image")
                    if info["virtual-size"] > spec.disk_gb * 1024**3:
                        raise q.VMError("Selected disk size is smaller than source image")
                    command = [binary, "convert", "-f", info["format"], "-O", "qcow2", str(image), disk]
                subprocess.run(command, check=True, capture_output=True, text=True, timeout=300)
                if spec.image_type == "disk":
                    subprocess.run([binary, "resize", disk, f"{spec.disk_gb}G"], check=True, capture_output=True, timeout=30)
                config = dict(spec.model_dump(), id=id, image_path=str(image), created_at=time.time())
                self.save(directory, config)
                return self.get(id)
            except Exception as exc:
                shutil.rmtree(directory)
                if isinstance(exc, q.VMError):
                    raise
                raise q.VMError(f"Disk creation failed: {exc}", 500) from exc

    def action(self, id, action):
        with self.lock:
            directory = self.directory(id)
            config = json.loads((directory / "config.json").read_text())
            active = q.running(directory)
            if action == "start":
                if active:
                    raise q.VMError("VM is already running", 409)
                q.launch(directory, config)
                config["started_at"] = time.time()
                self.save(directory, config)
            else:
                if not active:
                    raise q.VMError("VM is stopped", 409)
                q.qmp(directory / "qmp.sock", {"shutdown": "system_powerdown", "stop": "quit", "restart": "system_reset"}[action])
                if action == "stop":
                    for _ in range(30):
                        if not q.running(directory):
                            break
                        time.sleep(.1)
                if action == "restart":
                    config["started_at"] = time.time()
                    self.save(directory, config)
            return self.get(id)

    def delete(self, id):
        with self.lock:
            directory = self.directory(id)
            if q.running(directory):
                raise q.VMError("Stop the VM before deleting it", 409)
            shutil.rmtree(directory)
