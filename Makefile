# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
PYTHON ?= python3
.PHONY: all setup run test clean
all: setup
setup:
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt
run:
	@test "$$(id -u)" != 0 || (echo "Run as a regular user"; exit 1)
	.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
test:
	.venv/bin/python -m pytest -q
clean:
	find backend scripts tests -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache
