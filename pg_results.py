"""
pg_results.py — Full results page: scores, radar, gap table, ML output, PDF download
"""
import streamlit as st
import pandas as pd
from utils.database import get_assessment_by_id, get_all_assessments, get_questions
from utils.scoring import get_maturity_label, compute_domain_scores, identify_gaps, build_feature_vector
from utils.ml_model import predict_risk, get_risk_color, get_risk_emoji, RISK_EMOJIS, explain_prediction
from utils.questions_data import DOMAINS
from utils.remediation import get_remediation_suggestion, log_remediation_decision, execute_remediation, re_verify_fix
from utils.vulnerability_mapping import search_cves_for_gap, NIST_REF_TO_KEYWORD

def render():
    st.title("📊 Assessment Results & Analysis")

    # Load from session (freshly completed) or let user pick
    aid           = st.session_state.get("last_assessment_id")
    domain_scores = st.session_state.get("last_domain_scores")
    overall_score = st.session_state.get("last_overall_score")
    gaps          = st.session_state.get("last_gaps")
    ml_result     = st.session_state.get("last_ml_result")
    org_name      = st.session_state.get("last_org_name", "—")
    assessor      = st.session_state.get("last_assessor", "—")

    assessments = get_all_assessments()

    if not aid and not assessments:
        st.info("No assessments found. Complete a new assessment first.")
        return

    if not aid or not domain_scores:
        if not assessments:
            st.warning("No assessments found.")
            return
        options = {
            f"ID {a['id']} — {a['org_name']} ({a['created_at'][:10]})": a["id"]
            for a in assessments
        }
        chosen = st.selectbox("Select an assessment to view:", list(options.keys()))
        aid    = options[chosen]

        row = get_assessment_by_id(aid)
        if not row:
            st.error("Assessment not found.")
            return

        questions     = get_questions()
        domain_scores = compute_domain_scores(row["answers"], questions)
        overall_score = row["maturity_score"]
        gaps          = row["gaps"]
        feature_vec   = build_feature_vector(domain_scores)
        ml_result     = predict_risk(feature_vec)
        org_name      = row["org_name"]
        assessor      = row["assessor"]

    maturity_label, maturity_emoji, maturity_color = get_maturity_label(overall_score)
    risk_level = ml_result.get("risk_level", "Unknown")
    risk_color = get_risk_color(risk_level)
    risk_emoji = get_risk_emoji(risk_level)
    confidence = ml_result.get("confidence", 0)

    # ── Header strip ──────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1e3a5f,#2563eb);
                border-radius:12px;padding:20px 28px;margin-bottom:16px;">
        <h2 style="color:white;margin:0">🛡️ {org_name}</h2>
        <p style="color:#93c5fd;margin:4px 0 0 0">
            Assessor: {assessor} | Assessment ID: #{aid}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── PDF Download at top ───────────────────────────────────────────
    st.markdown("### 📄 Download PDF Report")
    try:
        from utils.report_gen import generate_pdf_report
        from utils.prioritization import prioritize_gaps
        from utils.database import get_all_evidence

        assessment_data = {
            "org_name":      org_name,
            "assessor":      assessor,
            "maturity_score": overall_score,
            "risk_level":    risk_level,
            "gaps":          gaps if isinstance(gaps, list) else [],
        }

        evidence_summary = None
        try:
            all_evidence = get_all_evidence(assessment_id=aid)
            eligible_count = sum(
                1 for d in domain_scores.values()
                if isinstance(d, dict)
            )
            evidence_summary = {
                "total_eligible": eligible_count if eligible_count else 40,
                "with_evidence": len(all_evidence),
                "coverage_pct": round(
                    (len(all_evidence) / (eligible_count if eligible_count else 40)) * 100, 1
                ) if all_evidence else 0.0,
            }
        except Exception:
            evidence_summary = None

        shap_explanation = None
        try:
            feature_vec_for_pdf = [
                domain_scores.get(d, {}).get("score", 0) for d in DOMAINS
            ]
            shap_explanation = explain_prediction(feature_vec_for_pdf)
        except Exception:
            shap_explanation = None

        priority_gaps = None
        try:
            if isinstance(gaps, list) and gaps:
                priority_gaps = prioritize_gaps(gaps)
        except Exception:
            priority_gaps = None

        pdf_bytes = generate_pdf_report(
            assessment_data,
            domain_scores,
            evidence_summary=evidence_summary,
            shap_explanation=shap_explanation,
            priority_gaps=priority_gaps,
        )
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name=f"CyberMAP_{org_name.replace(' ', '_')}_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
    except Exception as e:
        st.error(f"PDF error: {e}")

    st.markdown("---")

    # ── Top KPIs ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Score",      f"{overall_score:.2f} / 5.00")
    c2.metric("Maturity Level",     f"{maturity_emoji} {maturity_label}")
    c3.metric("Risk Level (AI/ML)", f"{risk_emoji} {risk_level}")
    c4.metric("Gaps Identified",    len(gaps) if isinstance(gaps, list) else 0)

    st.markdown("---")

    # ── Gauge + Radar ─────────────────────────────────────────────────
    try:
        from utils.charts import gauge_chart, radar_chart, bar_chart, risk_donut, gap_severity_bar
        col_g, col_r = st.columns([1, 2])
        with col_g:
            st.subheader("🎯 Overall Maturity")
            st.plotly_chart(gauge_chart(overall_score), use_container_width=True)
        with col_r:
            st.subheader("🕸️ Domain Radar")
            st.plotly_chart(radar_chart(domain_scores), use_container_width=True)

        st.subheader("📊 Domain Scores")
        st.plotly_chart(bar_chart(domain_scores), use_container_width=True)
    except Exception as e:
        st.warning(f"Chart error: {e}")

    # Domain score table
    dom_data = []
    for d, v in domain_scores.items():
        sc  = v.get("score", 0)
        lbl = get_maturity_label(sc)[0]
        dom_data.append({
            "Domain":   d,
            "Score":    f"{sc:.2f}/5.00",
            "Level":    lbl,
            "Coverage": f"{(sc/5)*100:.1f}%",
            "Questions": v.get("count", v.get("question_count", 0)),
        })
    st.dataframe(
        pd.DataFrame(dom_data),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # ── AI/ML Risk Panel ──────────────────────────────────────────────
    st.subheader("🤖 AI/ML Risk Classification")
    col_risk, col_donut = st.columns([1, 1])

    with col_risk:
        st.markdown(f"""
        <div style="background:{risk_color}22;border-left:5px solid {risk_color};
                    border-radius:8px;padding:16px;margin-bottom:8px;">
            <h3 style="color:{risk_color};margin:0">{risk_emoji} {risk_level} Risk</h3>
            <p style="margin:4px 0 0 0;color:#94a3b8">
                Model confidence: <b>{confidence:.1f}%</b>
            </p>
            <p style="margin:4px 0 0 0;color:#64748b;font-size:0.85rem">
                Algorithm: Gradient Boosting Classifier
            </p>
        </div>
        """, unsafe_allow_html=True)

        probs = ml_result.get("probabilities", {})
        st.markdown("**Probability Breakdown**")
        for lvl in ["Critical", "High", "Medium", "Low"]:
            pct = probs.get(lvl, 0)
            st.markdown(f"**{lvl}**")
            st.progress(pct / 100)

    with col_donut:
        try:
            st.plotly_chart(risk_donut(probs), use_container_width=True)
        except:
            pass

    # ── Explainable AI — Why this risk level? (CyberMAP 2.0) ───────────
    st.markdown("#### 🧠 Why This Risk Level? (Explainable AI)")
    with st.spinner("Computing SHAP explanation..."):
        try:
            feature_vec_for_explain = [
                domain_scores.get(d, {}).get("score", 0) for d in DOMAINS
            ]
            explanation = explain_prediction(feature_vec_for_explain)

            st.markdown(f"""
            <div style="background:#0f172a;border-left:4px solid #8b5cf6;
                        border-radius:8px;padding:14px 18px;margin-bottom:12px;">
                <p style="color:#e2e8f0;margin:0;font-size:0.95rem;line-height:1.5;">
                    {explanation['explanation_text']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Domain Contribution to This Prediction**")
            st.caption(
                "Positive values pushed the prediction toward the "
                f"'{explanation['predicted_class']}' class. "
                "Negative values pushed away from it."
            )

            contrib = explanation["domain_contributions"]
            for domain in DOMAINS:
                val = contrib.get(domain, 0)
                bar_color = "#ef4444" if val < 0 else "#22c55e"
                bar_width = min(abs(val) * 200, 100)
                direction = "◀" if val < 0 else "▶"
                col_label, col_bar = st.columns([1, 3])
                with col_label:
                    st.markdown(f"**{domain}**")
                with col_bar:
                    st.markdown(f"""
                    <div style="background:#1e293b;border-radius:4px;
                                height:20px;position:relative;overflow:hidden;
                                display:flex;align-items:center;">
                        <div style="width:{bar_width}%;height:100%;
                                    background:{bar_color};border-radius:4px;">
                        </div>
                        <span style="position:absolute;left:8px;color:#e2e8f0;
                                     font-size:0.75rem;">
                            {direction} {val:+.3f}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.warning(f"Could not generate SHAP explanation: {e}")

    st.markdown("---")

    # ── Human-in-the-Loop Remediation (CyberMAP 2.0) ────────────────────
    st.markdown("#### 🛠️ Suggested Remediation (Human Approval Required)")
    st.caption(
        "For reversible fixes, you may execute the command directly after "
        "explicit two-step confirmation — nothing runs on a single click. "
        "Non-reversible fixes (e.g. disk encryption) only support logging "
        "an approval decision, never automatic execution."
    )

    if isinstance(gaps, list):
        remediable_gaps = []
        for g in gaps[:20]:
            suggestion = get_remediation_suggestion(g.get("nist_ref", ""))
            if suggestion:
                remediable_gaps.append((g, suggestion))

        if remediable_gaps:
            for idx, (g, suggestion) in enumerate(remediable_gaps[:3]):
                with st.expander(f"{g['domain']} — {suggestion['fix']}"):
                    st.markdown(f"**Gap:** {g['question']}")
                    st.markdown(f"**NIST Ref:** `{g['nist_ref']}`")
                    st.markdown(f"**Proposed Fix:** {suggestion['fix']}")
                    st.code(suggestion['command'], language="powershell")
                    reversible_text = "Reversible" if suggestion['reversible'] else "Not easily reversible"
                    st.caption(f"Risk level: {reversible_text}")

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("📝 Log Approval Only", key=f"approve_{idx}"):
                            log_remediation_decision(
                                gap_question=g["question"],
                                nist_ref=g["nist_ref"],
                                proposed_fix=suggestion["fix"],
                                command_preview=suggestion["command"],
                                approved_by=assessor,
                                status="Approved (Not Executed)",
                            )
                            st.success("Approval logged. Not executed.")

                    with col_b:
                        if suggestion.get("reversible", False):
                            if st.button("⚡ Execute Now", key=f"execute_{idx}"):
                                st.session_state[f"confirm_exec_{idx}"] = True

                    with col_c:
                        if st.button("❌ Reject", key=f"reject_{idx}"):
                            log_remediation_decision(
                                gap_question=g["question"],
                                nist_ref=g["nist_ref"],
                                proposed_fix=suggestion["fix"],
                                command_preview=suggestion["command"],
                                approved_by=assessor,
                                status="Rejected",
                            )
                            st.info("Rejection logged.")

                    if st.session_state.get(f"confirm_exec_{idx}"):
                        st.warning(
                            f"⚠️ This will actually run the following command "
                            f"on THIS machine right now:\n\n`{suggestion['command']}`\n\n"
                            f"Confirm you want to proceed."
                        )
                        conf_a, conf_b = st.columns(2)
                        with conf_a:
                            if st.button("✅ Yes, execute", key=f"conf_yes_{idx}"):
                                with st.spinner("Executing fix..."):
                                    exec_result = execute_remediation(g["nist_ref"], suggestion["command"])

                                if exec_result["success"]:
                                    st.success(f"✅ Executed successfully.")
                                    if exec_result["output"]:
                                        st.code(exec_result["output"])

                                    with st.spinner("Re-verifying with a targeted re-scan..."):
                                        recheck = re_verify_fix(g["nist_ref"])
                                    if recheck:
                                        recheck_color = "green" if recheck["status"] == "PASS" else "orange"
                                        st.info(f"Re-scan result for {recheck['check']}: **{recheck['status']}**")

                                    log_remediation_decision(
                                        gap_question=g["question"],
                                        nist_ref=g["nist_ref"],
                                        proposed_fix=suggestion["fix"],
                                        command_preview=suggestion["command"],
                                        approved_by=assessor,
                                        status="Approved and Executed",
                                    )
                                else:
                                    st.error(f"❌ Execution failed: {exec_result['error']}")
                                    log_remediation_decision(
                                        gap_question=g["question"],
                                        nist_ref=g["nist_ref"],
                                        proposed_fix=suggestion["fix"],
                                        command_preview=suggestion["command"],
                                        approved_by=assessor,
                                        status="Execution Failed",
                                    )
                                st.session_state[f"confirm_exec_{idx}"] = False

                        with conf_b:
                            if st.button("Cancel", key=f"conf_no_{idx}"):
                                st.session_state[f"confirm_exec_{idx}"] = False
                                st.info("Execution cancelled.")
        else:
            st.caption("No automated remediation suggestions available for the current gaps.")

    st.markdown("---")

    # ── Vulnerability-to-Maturity Mapping (CyberMAP 2.0) ────────────────
    st.markdown("#### 🌐 Related Known Vulnerabilities (Live CVE Lookup)")
    st.caption(
        "Connects specific assessment gaps to real, currently known "
        "vulnerabilities from the NIST National Vulnerability Database, "
        "adding concrete threat context to abstract maturity scores. "
        "If the live database is unreachable, a small set of cached "
        "illustrative examples is shown instead, clearly labelled."
    )

    if isinstance(gaps, list):
        mappable_gaps = []
        seen_refs = set()
        for g in gaps:
            ref = g.get("nist_ref", "")
            if ref in NIST_REF_TO_KEYWORD and ref not in seen_refs:
                mappable_gaps.append(g)
                seen_refs.add(ref)

        if mappable_gaps:
            for idx, g in enumerate(mappable_gaps[:3]):
                with st.expander(f"{g['domain']} — {g['question'][:70]}"):
                    with st.spinner("Searching NVD for related CVEs..."):
                        cve_result = search_cves_for_gap(g["nist_ref"])

                    if cve_result["source"] == "live":
                        st.success(
                            f"🌐 Live results from NVD — search term: "
                            f"'{cve_result['keyword_used']}'"
                        )
                    elif cve_result["source"] == "cache-db":
                        age = cve_result.get("age_hours", "?")
                        st.info(
                            f"⚡ Loaded from cache (queried {age} hours ago) — "
                            f"faster than a live lookup, same real data."
                        )
                    elif cve_result["source"] == "cached":
                        st.warning(
                            "⚠️ Live NVD lookup unavailable — showing "
                            "cached illustrative examples instead."
                        )
                    else:
                        st.info("No CVE mapping available for this control type.")

                    for cve in cve_result["cves"]:
                        sev_color = {
                            "CRITICAL": "#dc2626", "Critical": "#dc2626",
                            "HIGH": "#f59e0b", "High": "#f59e0b",
                            "MEDIUM": "#fbbf24", "Medium": "#fbbf24",
                        }.get(cve["severity"], "#6b7280")
                        st.markdown(f"""
                        <div style="background:#0f172a;border-left:3px solid {sev_color};
                                    border-radius:6px;padding:10px 14px;margin-bottom:6px;">
                            <span style="color:{sev_color};font-weight:700;">
                                {cve['id']}
                            </span>
                            <span style="color:#64748b;font-size:0.78rem;margin-left:8px;">
                                {cve['severity']}
                            </span>
                            <p style="color:#94a3b8;margin:6px 0 0 0;font-size:0.85rem;">
                                {cve['description']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.caption("No gaps in this assessment have a defined CVE search mapping.")

    st.markdown("---")

    # ── Gap Analysis ──────────────────────────────────────────────────
    st.subheader("🔍 Gap Analysis")

    if not gaps or not isinstance(gaps, list) or len(gaps) == 0:
        st.success("✅ No significant gaps identified.")
    else:
        crit = sum(1 for g in gaps if g.get("severity") == "Critical")
        high = sum(1 for g in gaps if g.get("severity") == "High")
        med  = sum(1 for g in gaps if g.get("severity") == "Medium")

        gc1, gc2, gc3, gc4 = st.columns(4)
        gc1.metric("🔴 Critical", crit)
        gc2.metric("🟠 High",     high)
        gc3.metric("🟡 Medium",   med)
        gc4.metric("⚪ Total",    len(gaps))

        with st.expander(f"📋 View All {len(gaps)} Gaps in Detail", expanded=True):
            for i, g in enumerate(gaps[:50], 1):
                sev = g.get("severity", "")
                sev_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡"}.get(sev, "⚪")
                st.markdown(f"""
                <div style="background:#1e293b;border-left:4px solid {'#ef4444' if sev=='Critical' else '#f97316' if sev=='High' else '#eab308'};
                            border-radius:6px;padding:10px 14px;margin-bottom:8px;">
                    <span style="color:#ef4444;font-weight:700;font-size:0.8rem;">
                        {sev_icon} {sev}
                    </span>
                    <span style="color:#64748b;font-size:0.78rem;margin-left:8px;">
                        {g.get('domain','')} › {g.get('subdomain','')}
                    </span>
                    <p style="color:#e2e8f0;margin:6px 0 4px 0;font-size:0.9rem;">
                        {g.get('question','')[:100]}
                    </p>
                    <span style="background:#0f172a;color:#60a5fa;border-radius:4px;
                                 padding:2px 8px;font-size:0.75rem;">
                        {g.get('nist_ref','')}
                    </span>
                    <span style="background:#0f172a;color:#34d399;border-radius:4px;
                                 padding:2px 8px;font-size:0.75rem;margin-left:4px;">
                        {g.get('iso_ref','')}
                    </span>
                    <p style="color:#fbbf24;margin:6px 0 0 0;font-size:0.85rem;">
                        💡 {g.get('recommendation','')[:80]}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            if len(gaps) > 50:
                st.info(f"Showing 50 of {len(gaps)} gaps. Download PDF for complete list.")

    st.markdown("---")

    # ── Recommendations ───────────────────────────────────────────────
    st.subheader("💡 Recommendations by Domain")
    tabs = st.tabs(DOMAINS)
    for tab, domain in zip(tabs, DOMAINS):
        with tab:
            ds  = domain_scores.get(domain, {})
            sc  = ds.get("score", 0)
            lbl, em, _ = get_maturity_label(sc)
            st.markdown(f"**{domain} — Score: {sc:.2f}/5.00   {em} {lbl}**")
            domain_gaps = [g for g in (gaps or []) if g.get("domain") == domain]
            if domain_gaps:
                for g in domain_gaps[:5]:
                    st.markdown(f"› {g.get('recommendation','')}")
            else:
                st.success("✅ No gaps in this domain.")