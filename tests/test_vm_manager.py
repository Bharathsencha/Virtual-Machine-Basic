# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
import json
from unittest.mock import patch
import pytest
from backend.models import VMCreate
from backend.vm_manager import VMManager
from backend.errors import VMError


@pytest.fixture
def setup(tmp_path):
    image = tmp_path / 'linux.iso'
    image.write_bytes(b'fixture')
    return VMManager(tmp_path / 'data'), VMCreate(name='demo', image_path=str(image))


def test_create_and_safe_delete(setup):
    manager, spec = setup
    with patch('backend.vm_manager.subprocess.run') as run:
        vm = manager.create(spec)
    assert vm['status'] == 'stopped'
    assert run.call_args.args[0][-1] == '5G'
    assert json.loads((manager.directory(vm['id']) / 'config.json').read_text())['name'] == 'demo'
    manager.delete(vm['id'])
    assert manager.list() == []
    from pathlib import Path
    assert Path(spec.image_path).exists()


def test_invalid_and_duplicate(setup):
    manager, spec = setup
    with pytest.raises(VMError):
        manager.get('../outside')
    with patch('backend.vm_manager.subprocess.run'):
        manager.create(spec)
        with pytest.raises(VMError, match='already exists'):
            manager.create(spec)
    spec.name = 'other'
    spec.image_path = '/missing/source.iso'
    with pytest.raises(VMError, match='absolute file'):
        manager.create(spec)


def test_missing_dependency_rolls_back(setup):
    manager, spec = setup
    with patch('backend.qemu_service.shutil.which', return_value=None):
        with pytest.raises(VMError, match='Missing qemu-img'):
            manager.create(spec)
    assert manager.list() == []


def test_lifecycle_and_reconciliation(setup):
    manager, spec = setup
    with patch('backend.vm_manager.subprocess.run'):
        vm = manager.create(spec)
    with patch('backend.qemu_service.running', return_value=False), patch('backend.qemu_service.launch') as launch:
        manager.action(vm['id'], 'start')
        launch.assert_called_once()
    with patch('backend.qemu_service.running', return_value=True), patch('backend.qemu_service.qmp') as qmp:
        assert VMManager(manager.root).get(vm['id'])['status'] == 'running'
        for action, command in [('shutdown','system_powerdown'), ('restart','system_reset')]:
            manager.action(vm['id'], action)
            assert qmp.call_args.args[1] == command
        with pytest.raises(VMError, match='Stop'):
            manager.delete(vm['id'])
    with patch('backend.qemu_service.running', side_effect=[True, False, False]), patch('backend.qemu_service.qmp') as qmp:
        assert manager.action(vm['id'], 'stop')['status'] == 'stopped'
        assert qmp.call_args.args[1] == 'quit'
