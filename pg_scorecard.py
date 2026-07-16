# pg_scorecard.py — Executive Scorecard
import streamlit as st
import plotly.graph_objects as go
from utils.database import get_all_assessments, get_assessment_by_id, get_questions
from utils.scoring import compute_domain_scores, get_maturity_label, identify_gaps
from utils.ml_model import get_risk_color, get_risk_emoji
from utils.questions_data import DOMAINS
from datetime import datetime

TRAFFIC = {
    (0.0, 2.0): ("🔴", "RED",    "#ef4444", "Immediate action required"),
    (2.0, 3.5): ("🟡", "AMBER",  "#f59e0b", "Improvement needed"),
    (3.5, 5.1): ("🟢", "GREEN",  "#22c55e", "Meets expectations"),
}

def get_traffic(score):
    for (lo, hi), result in TRAFFIC.items():
        if lo <= score < hi:
            return result
    return ("⚪", "UNKNOWN", "#6b7280", "")


def render():
    st.markdown("""
    <style>
    .exec-header {
        background:linear-gradient(135deg,#1e3a5f,#0f172a);
        border-radius:14px; padding:28px 32px; margin-bottom:24px;
        border:1px solid #2563eb44;
    }
    .traffic-card {
        border-radius:12px; padding:20px; text-align:center;
        margin-bottom:8px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="exec-header">
        <h2 style="color:white;margin:0;">📋 Executive Scorecard</h2>
        <p style="color:#93c5fd;margin:6px 0 0 0;">
            Board-level cybersecurity summary with traffic light ratings
            for senior leadership and auditors.
        </p>
    </div>
    """, unsafe_allow_html=True)

    assessments = get_all_assessments()
    if not assessments:
        st.warning("No assessments found. Complete a New Assessment first.")
        return

    options = {
        f"ID {a['id']} — {a['org_name']} ({a['created_at'][:10]})": a["id"]
        for a in assessments
    }

    col_sel, col_date = st.columns([3, 1])
    chosen = col_sel.selectbox("Select assessment:", list(options.keys()))
    col_date.markdown(f"""
    <div style="padding:28px 0 0 0;color:#64748b;font-size:0.85rem;">
        📅 {datetime.now().strftime("%d %B %Y")}
    </div>""", unsafe_allow_html=True)

    row = get_assessment_by_id(options[chosen])
    qs  = get_questions()
    domain_scores = compute_domain_scores(row["answers"], qs)
    overall  = row["maturity_score"]
    risk     = row["risk_level"]
    gaps     = row["gaps"]
    risk_clr = get_risk_color(risk)
    risk_em  = get_risk_emoji(risk)
    _, mat_em, _ = get_maturity_label(overall)

    # Executive header strip
    st.markdown(f"""
    <div style="background:#0f172a;border:1px solid #334155;
                border-radius:14px;padding:24px 28px;margin-bottom:24px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <h3 style="color:white;margin:0;font-size:1.4rem;">
                    {row['org_name']}
                </h3>
                <p style="color:#64748b;margin:4px 0 0 0;">
                    Assessor: {row['assessor']} &nbsp;·&nbsp;
                    Assessment ID: #{row['id']} &nbsp;·&nbsp;
                    {row['created_at'][:10]}
                </p>
            </div>
            <div style="text-align:right;">
                <div style="color:white;font-size:2rem;font-weight:700;">
                    {mat_em} {overall:.2f}/5.00
                </div>
                <div style="color:{risk_clr};font-weight:600;">
                    {risk_em} {risk} Risk
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Traffic light summary
    st.markdown("### 🚦 Domain Traffic Light Summary")
    cols = st.columns(6)
    for i, domain in enumerate(DOMAINS):
        sc = domain_scores.get(domain, {}).get("score", 0)
        em, label, color, msg = get_traffic(sc)
        with cols[i]:
            st.markdown(f"""
            <div style="background:#1e293b;border:2px solid {color};
                        border-radius:12px;padding:16px;text-align:center;">
                <div style="font-size:2rem;">{em}</div>
                <div style="color:#e2e8f0;font-size:0.82rem;
                            font-weight:600;margin:6px 0 2px 0;">{domain}</div>
                <div style="color:{color};font-size:1.2rem;
                            font-weight:700;">{sc:.1f}</div>
                <div style="color:{color};font-size:0.7rem;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Executive summary table
    st.markdown("### 📊 Executive Summary Table")
    summary_data = []
    for domain in DOMAINS:
        sc = domain_scores.get(domain, {}).get("score", 0)
        em, label, color, msg = get_traffic(sc)
        lbl, _, _ = get_maturity_label(sc)
        summary_data.append({
            "Domain":         domain,
            "Score":          f"{sc:.2f}/5.00",
            "Maturity Level": lbl,
            "Status":         f"{em} {label}",
            "Action":         msg,
        })

    import pandas as pd
    st.dataframe(
        pd.DataFrame(summary_data),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # Key metrics for board
    st.markdown("### 📌 Key Metrics for Board")
    crit = sum(1 for g in gaps if g.get("severity") == "Critical")
    high = sum(1 for g in gaps if g.get("severity") == "High")
    red_domains   = sum(1 for d in DOMAINS
                        if domain_scores.get(d,{}).get("score",0) < 2.0)
    green_domains = sum(1 for d in DOMAINS
                        if domain_scores.get(d,{}).get("score",0) >= 3.5)

    m1, m2, m3, m4, m5 = st.columns(5)
    for col, val, label, color in [
        (m1, f"{overall:.2f}/5", "Overall Maturity",   "#60a5fa"),
        (m2, f"{risk_em} {risk}","Risk Level",          risk_clr),
        (m3, str(crit),          "Critical Gaps",       "#ef4444"),
        (m4, str(red_domains),   "Red Domains",         "#ef4444"),
        (m5, str(green_domains), "Green Domains",       "#22c55e"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#1e293b;border:1px solid #334155;
                        border-radius:10px;padding:16px;text-align:center;">
                <div style="font-size:1.6rem;font-weight:700;
                            color:{color};">{val}</div>
                <div style="font-size:0.72rem;color:#64748b;
                            text-transform:uppercase;letter-spacing:1px;
                            margin-top:4px;">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Top 5 risks for board
    st.markdown("### ⚠️ Top Risks Requiring Board Attention")
    crit_gaps = [g for g in gaps if g.get("severity") == "Critical"][:5]
    if not crit_gaps:
        st.success("✅ No critical risks identified.")
    else:
        for i, g in enumerate(crit_gaps, 1):
            st.markdown(f"""
            <div style="background:#1e0505;border:1px solid #ef4444;
                        border-radius:10px;padding:14px 16px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;">
                    <div>
                        <span style="color:#ef4444;font-weight:700;">
                            Risk #{i}
                        </span>
                        <span style="color:#e2e8f0;margin-left:8px;
                                     font-weight:500;">
                            {g['domain']} — {g['subdomain']}
                        </span>
                        <p style="color:#94a3b8;margin:6px 0 0 0;
                                  font-size:0.85rem;">
                            {g['question'][:120]}...
                        </p>
                    </div>
                    <div style="color:#ef4444;font-weight:700;
                                min-width:50px;text-align:right;">
                        {g['score']}/5
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Executive recommendation
    st.markdown("---")
    st.markdown("### 💼 Executive Recommendation")
    if overall >= 3.5:
        msg = ("The organisation demonstrates a **managed** cybersecurity posture. "
               "Continue monitoring and focus on optimising existing controls. "
               "Regular assessments are recommended to maintain this level.")
        st.success(msg)
    elif overall >= 2.5:
        msg = ("The organisation has **defined** basic security controls but "
               "significant gaps remain. The Board should approve a formal "
               "cybersecurity improvement budget and 90-day remediation roadmap.")
        st.warning(msg)
    else:
        msg = ("The organisation faces **critical** cybersecurity exposure. "
               "Immediate Board-level intervention is required. Emergency budget "
               "allocation and external security expertise are strongly recommended.")
        st.error(msg)