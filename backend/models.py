# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
from typing import Literal
from pydantic import BaseModel, Field

class VMCreate(BaseModel):
    name: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,47}$")
    ram_mb: Literal[512, 1024, 2048, 4096] = 1024
    cpus: Literal[1, 2, 4] = 1
    disk_gb: Literal[5, 10, 20] = 5
    image_path: str = Field(min_length=1)
    image_type: Literal["iso", "disk"] = "iso"
    console: Literal["graphical", "serial"] = "graphical"
