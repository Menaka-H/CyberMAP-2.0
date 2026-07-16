"""
pg_results.py — Full results page: scores, radar, gap table, ML output, PDF download
"""
import streamlit as st
import pandas as pd
from utils.database import get_assessment_by_id, get_all_assessments, get_questions
from utils.scoring import get_maturity_label, compute_domain_scores, identify_gaps, build_feature_vector
from utils.ml_model import predict_risk, get_risk_color, get_risk_emoji, RISK_EMOJIS
from utils.questions_data import DOMAINS

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
        assessment_data = {
            "org_name":      org_name,
            "assessor":      assessor,
            "maturity_score": overall_score,
            "risk_level":    risk_level,
            "gaps":          gaps if isinstance(gaps, list) else [],
        }
        pdf_bytes = generate_pdf_report(assessment_data, domain_scores)
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

        # ── Bar chart ─────────────────────────────────────────────────
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
            bar_col = {
                "Critical": "#dc2626",
                "High":     "#f59e0b",
                "Medium":   "#fbbf24",
                "Low":      "#16a34a",
            }.get(lvl, "#6b7280")
            st.markdown(f"**{lvl}**")
            st.progress(pct / 100)

    with col_donut:
        try:
            st.plotly_chart(risk_donut(probs), use_container_width=True)
        except:
            pass

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