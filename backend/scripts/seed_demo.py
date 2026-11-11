"""Seed demo claims via API (server must be running)."""

import os
import sys
import time

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = os.environ.get("API_BASE", "http://localhost:8002")
DEMO_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "demo"
)


def main():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json={"email": "admin@demo.med", "password": "AdminPass123!"},
    )
    r.raise_for_status()
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    files_list = sorted(f for f in os.listdir(DEMO_DIR) if f.endswith(".png"))
    for i, fn in enumerate(files_list):
        with open(os.path.join(DEMO_DIR, fn), "rb") as fh:
            resp = httpx.post(
                f"{BASE}/api/v1/claims",
                headers=headers,
                data={"claim_number": f"CLM-DEMO-{i:03d}"},
                files={"files": (fn, fh, "image/png")},
                timeout=60,
            )
        print(i, resp.status_code, fn)
        time.sleep(0.5)
    print("Seeded", len(files_list), "claims. Processing continues in background.")


if __name__ == "__main__":
    main()
