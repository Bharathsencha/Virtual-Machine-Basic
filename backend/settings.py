# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
import os
from pathlib import Path
from .vm_manager import VMManager

BASE = Path(__file__).resolve().parent.parent
manager = VMManager(os.getenv("VM_DATA_DIR", str(BASE / "vm_data")))
