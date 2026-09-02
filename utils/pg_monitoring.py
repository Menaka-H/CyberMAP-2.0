# pg_monitoring.py - CyberMAP 2.0 Continuous Monitoring Dashboard
import streamlit as st
import subprocess
import json
from scanner import run_full_scan
from utils.database import (
    save_monitoring_snapshot, get_latest_snapshot,
    get_all_snapshots, detect_drift,
)

STATUS_COLOR = {"PASS": "green", "PARTIAL": "orange", "FAIL": "red", "ERROR": "gray"}
TASK_NAME = "CyberMAP_ScheduledScan"


def get_scheduled_task_status():
    """
    Query Windows Task Scheduler for the CyberMAP scheduled task
    and return its key status fields, so the app can show whether
    automated background scanning is actually configured and running.
    """
    try:
        result = subprocess.run(
            ["schtasks", "/query", "/tn", TASK_NAME, "/v", "/fo", "LIST"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return None

        info = {}
        for line in result.stdout.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                info[key.strip()] = value.strip()
        return info
    except Exception:
        return None


def render():
    st.title("Continuous Security Posture Monitoring")
    st.markdown(
        "Re-run the Endpoint Scanner against a registered endpoint and "
        "compare the result to the last recorded scan. This platform "
        "additionally verifies whether an actual Windows Task Scheduler "
        "job is configured to run this scan automatically in the "
        "background."
    )

    # ── Scheduled Task Status ────────────────────────────────
    st.markdown("### Automated Scan Schedule")
    task_info = get_scheduled_task_status()

    if task_info:
        status      = task_info.get("Status", "Unknown")
        next_run    = task_info.get("Next Run Time", "Unknown")
        last_run    = task_info.get("Last Run Time", "Unknown")
        last_result = task_info.get("Last Result", "Unknown")
        repeat      = task_info.get("Repeat: Every", "Unknown")

        never_run = last_run.startswith("30-11-1999") or last_run == "N/A"
        success   = last_result == "0"

        col1, col2, col3 = st.columns(3)
        col1.metric("Task Status", status)
        col2.metric("Repeat Interval", repeat if repeat != "Unknown" else "Not set")
        col3.metric("Next Run", next_run)

        if never_run:
            st.info(
                "Scheduled task is registered but has not run automatically "
                "yet. It will trigger at the Next Run time shown above with "
                "no action required."
            )
        elif success:
            st.success(
                f"Scheduled task last ran automatically at {last_run} "
                f"and completed successfully (result code 0) - confirming "
                f"unattended background execution is working."
            )
        else:
            st.warning(
                f"Scheduled task last ran at {last_run} but returned "
                f"result code {last_result}. Check scheduled_scan_log.txt "
                f"in the project folder for the detailed error."
            )

        with st.expander("View full scheduled task details"):
            for k, v in task_info.items():
                st.caption(f"**{k}:** {v}")
    else:
        st.warning(
            f"No scheduled task named '{TASK_NAME}' was found. "
            f"Automated background scanning is not currently configured "
            f"on this machine."
        )

    st.markdown("---")

    # ── Manual re-scan ────────────────────────────────────────
    st.markdown("### Manual Re-scan")
    endpoint_name = st.text_input(
        "Endpoint name to monitor",
        value="LAB-PC-01",
        help="Use the same name consistently to build a monitoring history for one endpoint.",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        rescan_clicked = st.button("Run Scan Now", type="primary", use_container_width=True)

    latest = get_latest_snapshot(endpoint_name)
    if latest:
        st.caption(f"Last recorded scan for '{endpoint_name}': {latest['scan_time']}")
    else:
        st.info(f"No previous scan found for '{endpoint_name}'. The next scan will become the baseline.")

    if rescan_clicked:
        with st.spinner("Running endpoint scan..."):
            filename = run_full_scan(endpoint_label=endpoint_name)
            with open(filename, "r", encoding="utf-8") as f:
                new_report = json.load(f)

        drift_events = detect_drift(endpoint_name, new_report)
        save_monitoring_snapshot(endpoint_name, new_report)

        st.success(f"Scan complete for '{endpoint_name}'.")

        if drift_events:
            st.markdown("### Posture Change Detected")
            for event in drift_events:
                st.markdown(
                    f"**{event['check']}**  \n"
                    f"Previous: `{event['previous_status']}` ({event['previous_time']})  \n"
                    f"Current: `{event['current_status']}` ({event['current_time']})"
                )
                st.markdown("---")
        elif latest is None:
            st.info("This scan is now the baseline for future comparisons.")
        else:
            st.success("No change detected since the last scan.")

    st.markdown("---")

    # ── History table for this endpoint ──────────────────────
    st.markdown("### Scan History")
    snapshots = get_all_snapshots(endpoint_name)
    if not snapshots:
        st.caption("No scans recorded yet for this endpoint.")
    else:
        for idx, snap in enumerate(reversed(snapshots)):
            summary = snap["report"].get("summary", {})
            st.markdown(
                f"**{snap['scan_time']}** - "
                f"{summary.get('passed', 0)} Passed, "
                f"{summary.get('partial', 0)} Partial, "
                f"{summary.get('failed', 0)} Failed"
            )
            results_list = snap["report"].get("results", [])
            with st.expander(f"View check details ({len(results_list)} checks)"):
                if not results_list:
                    st.caption("No check details available for this snapshot.")
                else:
                    table_rows = [
                        {"Check": r.get("check", "Unknown"), "Status": r.get("status", "Unknown")}
                        for r in results_list
                    ]
                    st.table(table_rows)