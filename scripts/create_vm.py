# Copyright (C) 2026 Bharathsencha
# SPDX-License-Identifier: GPL-3.0-only
"""Provision a VM through the running local API using only the standard library."""
import argparse
import json
import urllib.error
import urllib.request


def request(path, method="GET", data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request("http://127.0.0.1:8000/api" + path, data=body, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=360) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--shutdown", action="store_true")
    args = parser.parse_args()
    try:
        with open(args.config) as source:
            vm = request("/vms", "POST", json.load(source))
        print("Created:", vm["id"])
        vm = request(f"/vms/{vm['id']}/start", "POST")
        print(json.dumps(request(f"/vms/{vm['id']}"), indent=2))
        if vm["status"] != "running":
            raise RuntimeError("QEMU did not reach running state")
        if args.shutdown:
            print("Shutdown requested:", request(f"/vms/{vm['id']}/shutdown", "POST")["status"])
    except (OSError, urllib.error.URLError, RuntimeError) as exc:
        parser.exit(1, f"Automation failed: {exc}\n")


if __name__ == "__main__":
    main()
