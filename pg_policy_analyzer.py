# pg_policy_analyzer.py - CyberMAP 2.0 Automated Policy Gap Analyzer
import streamlit as st
from utils.policy_analyzer import analyze_policy_document


def render():
    st.title("Automated Policy Gap Analyzer")
    st.markdown(
        "Upload an existing security policy document (PDF) to check "
        "which NIST CSF 2.0 and ISO 27001 governance requirements are "
        "explicitly covered in the text. This extends automated "
        "checking into the Govern domain, which cannot be verified "
        "through endpoint scanning since it covers policy and process "
        "controls rather than technical configuration."
    )

    uploaded_file = st.file_uploader(
        "Upload policy document (PDF)",
        type=["pdf"],
    )

    if uploaded_file is not None:
        if st.button("Analyze Policy Document", type="primary"):
            with st.spinner("Extracting text and checking requirements..."):
                file_bytes = uploaded_file.getvalue()
                result = analyze_policy_document(file_bytes, uploaded_file.name)

            if "error" in result and result["error"]:
                st.error(result["error"])
                return

            st.session_state["policy_analysis_result"] = result

    result = st.session_state.get("policy_analysis_result")

    if result:
        st.markdown("---")
        st.markdown(f"### Results for: {result['filename']}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Requirements", result["total_requirements"])
        col2.metric("Covered", result["covered_count"])
        col3.metric("Coverage %", f"{result['coverage_pct']}%")

        st.progress(result["coverage_pct"] / 100)

        st.markdown("---")
        st.markdown("### Requirement Coverage Detail")

        covered_rows = [r for r in result["results"] if r["status"] == "Covered"]
        missing_rows = [r for r in result["results"] if r["status"] == "Not Covered"]

        st.markdown(f"#### Covered ({len(covered_rows)})")
        if covered_rows:
            for r in covered_rows:
                with st.expander(f"{r['nist_ref']} / {r['iso_ref']} - {r['requirement']}"):
                    st.write(f"Matched keyword: **{r['matched_keyword']}**")
                    if r["snippet"]:
                        st.caption(r["snippet"])
        else:
            st.caption("No requirements matched in this document.")

        st.markdown(f"#### Not Covered ({len(missing_rows)})")
        if missing_rows:
            table_rows = [
                {
                    "NIST Ref": r["nist_ref"],
                    "ISO Ref": r["iso_ref"],
                    "Requirement": r["requirement"],
                }
                for r in missing_rows
            ]
            st.table(table_rows)
            st.warning(
                "The requirements above were not found in the uploaded "
                "document. This does not necessarily mean the control "
                "is absent in the organisation - it means the policy "
                "text does not explicitly document it, which is itself "
                "a governance gap worth addressing."
            )
        else:
            st.success("All checked requirements were found in this document.")
