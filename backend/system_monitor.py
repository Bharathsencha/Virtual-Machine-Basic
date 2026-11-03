# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
import shutil
import psutil
from .qemu_service import kvm_available

def stats(root):
    memory = psutil.virtual_memory()
    disk = shutil.disk_usage(root)
    return {"cpu_percent": psutil.cpu_percent(), "memory_percent": memory.percent, "memory_available_bytes": memory.available,
            "disk_free_bytes": disk.free, "kvm_available": kvm_available(),
            "warning": None if kvm_available() else "KVM unavailable; software emulation is slower.",
            "qemu_available": bool(shutil.which("qemu-system-x86_64")), "qemu_img_available": bool(shutil.which("qemu-img"))}
