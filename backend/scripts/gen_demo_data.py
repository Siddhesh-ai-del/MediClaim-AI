"""Generate synthetic claim bundles with injected anomalies for demo/eval."""

import argparse
import os
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw


def make_bill(
    path: str,
    patient: str,
    amount: float,
    adm: str,
    dis: str,
    provider: str,
    anomaly: str | None = None,
):
    img = Image.new("RGB", (900, 700), "white")
    d = ImageDraw.Draw(img)
    lines = [
        "HEALTH INSURANCE CLAIM",
        f"Patient Name: {patient}",
        f"Age: {random.randint(20, 70)}  Gender: {'M' if random.random() > 0.5 else 'F'}",
        f"Policy Number: POL-{random.randint(1000, 9999)}",
        f"Provider: {provider}",
        f"Admission Date: {adm}",
        f"Discharge Date: {dis}",
        f"Total Claimed Amount: {amount:.2f}",
        f"Diagnosis: {'Viral fever' if not anomaly else 'Major surgery'}",
    ]
    if anomaly == "inflated":
        lines.append("Note: charges include premium room upgrade")
    if anomaly == "phantom":
        lines.append("Note: includes unused consumables")
    y = 20
    for l in lines:
        d.text((20, y), l, fill="black")
        y += 32
    img.save(path)


ANOMALIES = ["upcoding", "phantom", "inflated", "duplicate", None, None, None]


def main():
    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "demo"
    )
    os.makedirs(out_dir, exist_ok=True)
    providers = [
        "City Hospital",
        "Metro Clinic",
        "Care Diagnostics",
        "Wellness Center",
        "Apex Hospital",
    ]
    patients = [
        "John Doe",
        "Jane Smith",
        "Rahul Kumar",
        "Priya Sharma",
        "Amit Patel",
        "Sunita Devi",
        "Vikram Singh",
    ]
    base_date = date(2026, 1, 1)
    count = 0
    for i in range(40):
        anomaly = random.choice(ANOMALIES)
        patient = random.choice(patients)
        provider = random.choice(providers)
        adm = base_date + timedelta(days=random.randint(0, 200))
        dis = adm + timedelta(days=random.randint(1, 7))
        if anomaly == "inflated":
            amount = random.choice([600000, 750000, 900000])
        elif anomaly == "phantom":
            amount = random.choice([150000, 200000])
        else:
            amount = random.choice([15000, 25000, 45000, 80000, 120000])
        path = os.path.join(out_dir, f"claim_{i:03d}.png")
        make_bill(
            path, patient, amount, adm.isoformat(), dis.isoformat(), provider, anomaly
        )
        count += 1
    # duplicate: reuse one claim's number later handled by seed script
    print(f"Generated {count} synthetic bills in {out_dir}")


if __name__ == "__main__":
    main()
