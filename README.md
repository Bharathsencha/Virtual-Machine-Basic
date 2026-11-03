<!-- Copyright (C) 2026 Bharathsencha | SPDX-License-Identifier: GPL-3.0-only -->
# DevOps Mini VM Manager

Manage real local Linux VMs through FastAPI, a browser dashboard, and Python automation. QEMU supplies virtualization; this application provisions disks and controls QEMU through local QMP sockets. Licensed under GPL v3 only.

## Requirements and installation

Use Linux, Python 3.11 or newer, GNU Make, QEMU, and a prepared x86_64 Linux ISO or standalone BIOS bootable raw/QCOW2 image. Images are never downloaded automatically. Run as a regular user. A desktop session is required for graphical consoles. Serial guests must enable ttyS0 themselves. Cloud images often require cloud-init credentials and may not be suitable for a first demo.

On Ubuntu or Debian:

```sh
sudo apt update
sudo apt install python3 python3-venv make qemu-system-x86 qemu-utils socat
make
make run
```

Open http://127.0.0.1:8000 and http://127.0.0.1:8000/docs. `make` creates a virtual environment and installs runtime and test dependencies. `make test` runs tests. `make clean` removes Python caches and preserves VM disks. Stop the web server with Ctrl+C; running VMs continue. Restart the server to reconnect to their QMP sockets. Run only one server instance against a storage directory.

KVM is optional. Check `ls -l /dev/kvm` and ensure your user has access through the kvm group. Without it, QEMU uses TCG software emulation; booting can be much slower. Do not run the web server with sudo. Keep the service bound to localhost; it manages files accessible to your user and has no authentication.

## Create and use a VM

Click Create VM. Use `devops-demo`, 1024 MB, one CPU, 5 GB, and an absolute path to your prepared image. Select ISO for installation or live boot; select disk to copy a standalone existing image into a managed disk. The selected capacity must be at least the source virtual capacity. Disk resizing does not automatically expand guest partitions. Source images are preserved. An ISO is retained as first boot device for subsequent starts; use a live image for a simple demo, or import a prepared installed disk.

Start opens a local QEMU window on the server desktop. Console displays instructions; serial access requires `socat` and guest serial support. User networking provides outbound connectivity without exposing guest services. Graceful shutdown sends an ACPI power request and returns immediately; watch for stopped status. Reset is a hardware reset and requires confirmation. Force stop can lose unsaved guest data. Stop a VM before confirming deletion.

For automation, edit `scripts/example.json` with your image path and a unique VM name:

```sh
.venv/bin/python scripts/create_vm.py scripts/example.json
# Optional ACPI shutdown after the running check:
.venv/bin/python scripts/demo.py scripts/example.json --shutdown
```

Each execution provisions a new VM; names must be unique. The status check queries QEMU through QMP. It verifies a running emulator, not Linux readiness.

## Structure

```text
backend/
  main.py             FastAPI setup and static files
  routes.py           API endpoints
  settings.py         Storage configuration
  models.py           Request validation
  vm_manager.py       VM persistence and lifecycle orchestration
  qemu_service.py     QEMU commands and process startup
  qmp.py              Local QMP protocol
  errors.py           Domain errors
  system_monitor.py   Host metrics
frontend/             HTML, CSS, JavaScript dashboard
scripts/              API automation and sample configuration
tests/                API, manager, opt-in QEMU tests
vm_data/              Ignored managed storage
```

Browser and automation call the API. The manager creates a UUID directory, writes JSON atomically, and invokes qemu-img without a shell. QEMU exposes QMP and serial through private Unix sockets. Disk imports are full copies, avoiding a dependency on source files. Allocated VM RAM is displayed separately from host usage; guest usage is unavailable. Uptime measures time since application start/reset of a VM.

`VM_DATA_DIR` can select a short absolute storage path. Keep paths short for the Unix socket length limit. Names, resource choices, image paths, confirmation flags, host headers, and browser write origins are validated. Do not share VM storage with other users or edit its configuration while running.

## Tests and troubleshooting

```sh
make test
RUN_QEMU_TESTS=1 make test
```

The optional integration test creates a real QCOW2 disk and tests QEMU firmware startup and QMP reset/quit. It does not verify a Linux boot. Complete the guest checks in DEMO_GUIDE.md using your prepared image.

Missing executables: install qemu-system-x86 and qemu-utils. No display: start the server from your desktop terminal or use serial mode. An empty serial console usually means the guest has no ttyS0 console configured. Inspect `vm_data/<id>/qemu.log` after startup errors. Graceful shutdown depends on guest ACPI handling. Do not delete storage for a running QEMU process. A package index DNS failure requires working network access or locally available wheels before `make` can finish.
