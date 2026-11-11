"""Run evaluation harness on synthetic demo claims (requires server running + seeded data)."""

import os
import sys

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = os.environ.get("API_BASE", "http://localhost:8002")


def main():
    r = httpx.post(
        f"{BASE}/api/v1/auth/login",
        json={"email": "admin@demo.med", "password": "AdminPass123!"},
    )
    r.raise_for_status()
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # fetch claims
    claims = httpx.get(f"{BASE}/api/v1/claims?page_size=100", headers=headers).json()[
        "items"
    ]
    total = len(claims)
    processed = sum(
        1 for c in claims if c["status"] in ("scored", "adjudicated", "reviewed")
    )
    flagged = sum(1 for c in claims if (c.get("risk_score") or 0) >= 70)
    print(f"Claims: {total}, processed: {processed}, flagged: {flagged}")
    print(
        "Eval complete. Targets: extraction F1>=0.85, fraud precision>=0.80 (manual ground-truth comparison required)."
    )


if __name__ == "__main__":
    main()
