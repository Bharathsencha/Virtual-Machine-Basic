# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.vm_manager import VMManager


@pytest.fixture
def client(tmp_path):
    with patch('backend.routes.manager', VMManager(tmp_path / 'data')):
        with TestClient(app) as client:
            yield client


def test_health_dashboard_stats(client):
    assert client.get('/api/health').json() == {'status': 'ok'}
    assert client.get('/').status_code == 200
    assert client.get('/static/app.js').status_code == 200
    assert 'memory_percent' in client.get('/api/system/stats').json()
    assert client.get('/api/vms').json() == []


@pytest.mark.parametrize('change', [{'name':'../bad'}, {'ram_mb':100}, {'cpus':3}, {'disk_gb':1}])
def test_validation(client, change):
    data = {'name':'demo', 'image_path':'/missing.iso'} | change
    assert client.post('/api/vms', json=data).status_code == 422


def test_confirmations_and_origin(client):
    for path, method in [('/api/vms/test','delete'),('/api/vms/test/stop','post'),('/api/vms/test/restart','post')]:
        assert getattr(client, method)(path).status_code == 400
    assert client.post('/api/vms', headers={'Origin':'https://example.com'}, json={}).status_code == 403
    assert client.get('/api/vms/invalid').status_code == 404
