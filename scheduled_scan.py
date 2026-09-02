# scheduled_scan.py — Runs automatically via Windows Task Scheduler.
# Performs a scan and saves it directly into the monitoring database,
# so results appear in the Continuous Monitoring dashboard with no
# manual steps.

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scanner import run_full_scan
from utils.database import save_monitoring_snapshot, detect_drift
import json

ENDPOINT_NAME = "LAB-PC-01"

filename = run_full_scan(endpoint_label=ENDPOINT_NAME)

with open(filename, "r", encoding="utf-8") as f:
    report = json.load(f)

drift_events = detect_drift(ENDPOINT_NAME, report)
save_monitoring_snapshot(ENDPOINT_NAME, report)

if drift_events:
    print(f"DRIFT DETECTED: {len(drift_events)} change(s)")
    for e in drift_events:
        print(f"  {e['check']}: {e['previous_status']} -> {e['current_status']}")
else:
    print("No drift detected.")
