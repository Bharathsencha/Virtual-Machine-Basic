# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .settings import BASE
from .routes import router
from .qemu_service import VMError

app = FastAPI(title="DevOps Mini VM Manager", license_info={"name": "GPL-3.0-only"})
app.include_router(router)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "[::1]", "testserver"])

@app.middleware("http")
async def local_origin(request: Request, call_next):
    origin = request.headers.get("origin")
    if request.method in {"POST", "DELETE", "PUT", "PATCH"} and origin and origin != str(request.base_url).rstrip("/"):
        return JSONResponse({"detail": "Cross-origin writes are disabled"}, status_code=403)
    return await call_next(request)

@app.exception_handler(VMError)
async def vm_error(request, exc):
    return JSONResponse({"detail": str(exc)}, status_code=exc.status)

@app.get("/")
def index():
    return FileResponse(BASE / "frontend/index.html")

app.mount("/static", StaticFiles(directory=BASE / "frontend"), name="static")
