<!-- Copyright (C) 2026 Bharathsencha | SPDX-License-Identifier: GPL-3.0-only -->
# Verification on the development host

Python 3.12.3, qemu-system-x86_64, and qemu-img are installed. The host has approximately 23 GiB RAM and 145 GiB free disk space. /dev/kvm is absent, so acceleration must use TCG.

Python source compilation and JavaScript syntax checks passed. Real qemu-img QCOW2 creation succeeded. QEMU startup was attempted, but this execution sandbox rejects Unix socket binding with `Operation not permitted`. QMP lifecycle and Linux boot remain unverified here. No prepared Linux image was available in the workspace, and no operating system was downloaded.

`make` created the environment but dependency installation failed because the package index hostname could not resolve. `make test` cannot run because pytest is unavailable. FastAPI is also unavailable, so backend startup and browser behavior have not been verified in this environment. Run `make`, `make test`, and `RUN_QEMU_TESTS=1 make test` on an unrestricted Linux host, then perform the guest checks in DEMO_GUIDE.md.
