# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
import json
import socket
from .errors import VMError

def qmp(path, command):
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            sock.connect(str(path))
            with sock.makefile("rwb", buffering=0) as stream:
                json.loads(stream.readline())
                for cmd in ("qmp_capabilities", command):
                    stream.write((json.dumps({"execute": cmd}) + "\n").encode())
                    while True:
                        line = stream.readline()
                        if not line:
                            raise ValueError("QMP disconnected")
                        response = json.loads(line)
                        if "error" in response:
                            raise ValueError(response["error"].get("desc", "QMP error"))
                        if "return" in response:
                            break
                return response["return"]
    except (OSError, ValueError) as exc:
        raise VMError(f"QMP unavailable: {exc}", 409) from exc

