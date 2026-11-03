<!-- Copyright (C) 2026 Bharathsencha | SPDX-License-Identifier: GPL-3.0-only -->
# 15 minute demonstration

Prepare a small x86_64 live Linux ISO or a standalone BIOS bootable disk image with known login credentials. Confirm it boots on this host before the demonstration. No image download is part of the application.

| Time | Action and explanation | Expected result |
| --- | --- | --- |
| 0:00-2:00 | Run `make run`, open localhost:8000. Explain QEMU virtualization and the API. | Dashboard and host resources appear. |
| 2:00-4:00 | Click Create VM, name `devops-demo`, 1 GB RAM, 1 CPU, 5 GB disk. Enter the prepared image path and correct source type. | A stopped VM appears; JSON and QCOW2 are saved. |
| 4:00-7:00 | Click Start, then Console. Use the local QEMU window. | Running status appears. Linux boots, possibly slowly with TCG. |
| 7:00-9:00 | Log in or open a live terminal. Run the commands below. | Kernel, guest memory, and block devices appear. |
| 9:00-11:00 | Return to the dashboard. Explain allocated RAM versus actual host metrics. Open `/docs` and GET `/api/vms`. | API reflects the running emulator. |
| 11:00-13:00 | Click Shut down and wait. If ACPI is unavailable, shut down inside Linux. | Status changes to stopped. |
| 13:00-15:00 | Edit `scripts/example.json` with a unique name and image path. Run the automation command below. | Script creates and starts a VM and prints its QMP based status. |

Guest terminal:

```sh
uname -a
free -h
lsblk
```

Host automation, while the server runs in another terminal:

```sh
.venv/bin/python scripts/demo.py scripts/example.json --shutdown
```

Shutdown is asynchronous; the script prints that the request was accepted, and the guest may take time to stop. Use a second unique name if rerunning the provisioning script.

## Faster backup

Create and boot a VM named `prepared-demo` before the demonstration. Complete any installation and verify the console and credentials. Shut it down. During the demonstration start this existing VM to skip provisioning and installation. For a fast running-state demonstration, leave it booted beforehand and explain that it was prepared. A source installed disk is usually more repeatable than installing from an ISO during the demonstration. TCG can exceed the time budget, so measure boot time in advance.

## Five common questions

1. What is the hypervisor here? QEMU runs the virtual hardware. With access to KVM, it uses Linux hardware acceleration.
2. Why QCOW2? It supports sparse allocation. The configured virtual capacity differs from host disk space consumed.
3. What makes this automation? JSON describes the desired configuration, and Python calls the same API to provision and control the VM repeatably.
4. Why QMP? Structured JSON commands query state, request ACPI shutdown, reset hardware, and quit QEMU through a local socket.
5. Is allocated RAM guest usage? No. It is the configured limit; the application measures host utilization separately and does not collect guest usage.
