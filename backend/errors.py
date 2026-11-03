# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
class VMError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status

