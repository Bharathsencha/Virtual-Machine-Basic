# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
"""Opt-in QEMU control test. Boots firmware, not a Linux operating system."""
import os
import shutil
import subprocess
import pytest
from backend import qemu_service as q


@pytest.mark.skipif(os.getenv('RUN_QEMU_TESTS') != '1', reason='Set RUN_QEMU_TESTS=1 to launch QEMU')
def test_real_qmp(tmp_path):
    if not shutil.which('qemu-system-x86_64') or not shutil.which('qemu-img'):
        pytest.skip('QEMU missing')
    subprocess.run(['qemu-img','create','-f','qcow2',str(tmp_path/'disk.qcow2'),'5G'], check=True)
    try:
        q.launch(tmp_path, {'name':'smoke','ram_mb':512,'cpus':1,'console':'serial','image_type':'disk'})
        assert q.running(tmp_path)
        q.qmp(tmp_path/'qmp.sock','system_reset')
    finally:
        if q.running(tmp_path):
            q.qmp(tmp_path/'qmp.sock','quit')
