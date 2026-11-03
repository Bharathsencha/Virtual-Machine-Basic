# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
from fastapi import APIRouter, Query
from .models import VMCreate
from .qemu_service import VMError
from .system_monitor import stats
from .settings import manager

router = APIRouter()

@router.get("/api/health")
def health():
    return {"status": "ok"}

@router.get("/api/vms")
def list_vms():
    return manager.list()

@router.post("/api/vms", status_code=201)
def create_vm(spec: VMCreate):
    return manager.create(spec)

@router.get("/api/vms/{id}")
def get_vm(id: str):
    return manager.get(id)

@router.post("/api/vms/{id}/start")
def start(id: str):
    return manager.action(id, "start")

@router.post("/api/vms/{id}/shutdown", status_code=202)
def shutdown(id: str):
    return manager.action(id, "shutdown")

@router.post("/api/vms/{id}/stop")
def stop(id: str, confirm: bool = Query(False)):
    if not confirm:
        raise VMError("Force stop requires confirm=true")
    return manager.action(id, "stop")

@router.post("/api/vms/{id}/restart")
def restart(id: str, confirm: bool = Query(False)):
    if not confirm:
        raise VMError("Reset requires confirm=true; unsaved data may be lost")
    return manager.action(id, "restart")

@router.delete("/api/vms/{id}", status_code=204)
def delete(id: str, confirm: bool = Query(False)):
    if not confirm:
        raise VMError("Deletion requires confirm=true")
    manager.delete(id)

@router.get("/api/system/stats")
def system_stats():
    return stats(manager.root)

