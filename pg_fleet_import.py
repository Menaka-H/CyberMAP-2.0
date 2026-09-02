# pg_fleet_import.py — CyberMAP 2.0 Fleet Scan Import
import streamlit as st
import os
from utils.database import (
    get_questions, bulk_import_scan_reports,
    save_scan_report_as_evidence, INCOMING_SCANS_FOLDER,
)

STATUS_ICON = {"PASS": "PASS", "PARTIAL": "PARTIAL", "FAIL": "FAIL", "ERROR": "ERROR"}


def render():
    st.title("Fleet Scan Import")
    st.markdown(
        "Import Endpoint Scanner reports collected from multiple "
        "machines across the organisation. In production this folder "
        "represents a shared network location populated by scheduled "
        "scans on each endpoint; for this demonstration, place scan "
        "report JSON files here manually."
    )

    st.info(f"Import folder: `{os.path.abspath(INCOMING_SCANS_FOLDER)}`")

    os.makedirs(INCOMING_SCANS_FOLDER, exist_ok=True)
    existing_files = [
        f for f in os.listdir(INCOMING_SCANS_FOLDER)
        if f.startswith("CyberMAP_ScanReport_") and f.endswith(".json")
    ]

    if existing_files:
        st.success(f"{len(existing_files)} scan report(s) found in the import folder.")
        with st.expander("View files found"):
            for f in existing_files:
                st.caption(f"- {f}")
    else:
        st.warning(
            "No scan reports found. Run scanner.py and move the "
            "resulting JSON file(s) into the import folder above, "
            "then refresh this page."
        )

    st.markdown("---")

    if st.button("Import All Reports", type="primary", disabled=not existing_files):
        questions = get_questions()
        with st.spinner("Importing and matching scan reports..."):
            results = bulk_import_scan_reports(questions)
        st.session_state["fleet_import_results"] = results
        st.success(f"Imported {len(results)} endpoint report(s).")

    results = st.session_state.get("fleet_import_results")
    if results:
        st.markdown("### Fleet Overview")

        all_checks = []
        seen = set()
        for r in results:
            if "error" in r:
                continue
            for m in r["matched_answers"]:
                if m["check"] not in seen:
                    seen.add(m["check"])
                    all_checks.append(m["check"])

        endpoint_names = [
            r["endpoint_name"] for r in results if "error" not in r
        ]

        cols = st.columns([2] + [1.3] * len(endpoint_names))
        cols[0].markdown("**Check**")
        for i, name in enumerate(endpoint_names):
            cols[i + 1].markdown(f"**{name}**")

        for check_name in all_checks:
            cols = st.columns([2] + [1.3] * len(endpoint_names))
            cols[0].markdown(check_name)
            for i, r in enumerate(results):
                if "error" in r:
                    continue
                match = next(
                    (m for m in r["matched_answers"] if m["check"] == check_name),
                    None
                )
                if match:
                    icon = STATUS_ICON.get(match["status"], "?")
                    cols[i + 1].markdown(f"{icon} {match['status']}")
                else:
                    cols[i + 1].markdown("-")

        st.markdown("---")
        st.markdown("### Aggregated Fleet Score")
        total_score = 0
        total_count = 0
        for r in results:
            if "error" in r:
                continue
            for m in r["matched_answers"]:
                total_score += m["score"]
                total_count += 1

        if total_count > 0:
            avg_score = total_score / total_count
            c1, c2, c3 = st.columns(3)
            c1.metric("Endpoints Imported", len(endpoint_names))
            c2.metric("Checks Aggregated", total_count)
            c3.metric("Average Score (0-5)", f"{avg_score:.2f}")

        errors = [r for r in results if "error" in r]
        if errors:
            st.markdown("### Import Errors")
            for r in errors:
                st.error(f"{r['endpoint_name']}: {r['error']}")

        st.markdown("---")
        st.caption(
            "Note: This demonstration simulates a multi-endpoint "
            "organisational fleet using repeated scans of a single "
            "controlled lab machine with distinct endpoint labels. "
            "The architecture - shared import folder, bulk parsing, "
            "aggregated scoring - is unchanged in a real multi-machine "
            "deployment."
        )
