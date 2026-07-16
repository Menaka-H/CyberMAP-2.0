# pages/pg_history.py — Professional History Page
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.database import get_all_assessments
from utils.ml_model import get_risk_emoji, get_risk_color

def render():
    st.markdown("""
    <style>
    .history-card {
        background:#1e293b; border:1px solid #334155;
        border-radius:12px; padding:18px 20px; margin-bottom:10px;
    }
    .section-header {
        font-size:1.05rem; font-weight:600; color:#e2e8f0;
        border-left:4px solid #3b82f6; padding-left:12px;
        margin:20px 0 12px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e3a5f,#0f172a);
                border-radius:14px;padding:24px 28px;margin-bottom:20px;
                border:1px solid #2563eb44">
        <h2 style="color:white;margin:0">📁 Assessment History</h2>
        <p style="color:#93c5fd;margin:6px 0 0 0">
            All past assessments stored in the database
        </p>
    </div>
    """, unsafe_allow_html=True)

    assessments = get_all_assessments()

    if not assessments:
        st.info("No assessments yet. Complete your first assessment to see history.")
        return

    # ── Summary stats ─────────────────────────────────────────────────────
    total     = len(assessments)
    avg_score = sum(a["maturity_score"] or 0 for a in assessments) / total
    best      = max(assessments, key=lambda x: x["maturity_score"] or 0)
    risk_dist = {}
    for a in assessments:
        r = a.get("risk_level","Unknown")
        risk_dist[r] = risk_dist.get(r,0)+1

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, color in [
        (c1, str(total),               "Total Assessments",  "#60a5fa"),
        (c2, f"{avg_score:.2f}/5.00",  "Average Score",      "#34d399"),
        (c3, f"{best['maturity_score']:.2f}", "Best Score",  "#a78bfa"),
        (c4, best["org_name"][:16],    "Top Organisation",   "#fb923c"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#1e293b;border:1px solid #334155;
                        border-radius:10px;padding:14px;text-align:center">
                <div style="font-size:1.3rem;font-weight:700;color:{color}">{val}</div>
                <div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;
                            letter-spacing:1px;margin-top:4px">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Assessment cards ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 All Assessments</div>',
                unsafe_allow_html=True)

    for a in assessments:
        score = a.get("maturity_score", 0)
        risk  = a.get("risk_level","—")
        pct   = int((score / 5) * 100)
        clr   = get_risk_color(risk)
        emoji = get_risk_emoji(risk)

        col_info, col_score, col_btn = st.columns([4, 3, 2])

        with col_info:
            st.markdown(f"""
            <div style="padding:8px 0">
                <div style="font-weight:600;color:#e2e8f0;font-size:1rem">
                    {a['org_name']}
                </div>
                <div style="color:#64748b;font-size:0.85rem;margin-top:2px">
                    👤 {a['assessor']} &nbsp;·&nbsp;
                    📅 {a['created_at'][:10]} &nbsp;·&nbsp;
                    ID #{a['id']}
                </div>
            </div>""", unsafe_allow_html=True)

        with col_score:
            st.markdown(f"""
            <div style="padding:8px 0">
                <div style="display:flex;align-items:center;gap:8px">
                    <div style="flex:1;background:#0f172a;border-radius:6px;
                                height:8px;overflow:hidden">
                        <div style="width:{pct}%;height:100%;
                                    background:{clr};border-radius:6px"></div>
                    </div>
                    <span style="color:{clr};font-weight:700;min-width:36px">
                        {score:.2f}
                    </span>
                </div>
                <div style="color:{clr};font-size:0.85rem;margin-top:4px">
                    {emoji} {risk} Risk
                </div>
            </div>""", unsafe_allow_html=True)

        with col_btn:
            if st.button("📊 View", key=f"view_{a['id']}"):
                for k in ["last_aid","last_domain_scores","last_overall_score",
                          "last_gaps","last_ml_result","last_org_name","last_assessor"]:
                    st.session_state.pop(k, None)
                st.session_state["last_aid"] = a["id"]
                st.session_state["nav"] = "📊 Results & Analysis"
                st.rerun()

        st.markdown("<hr style='border-color:#1e293b;margin:4px 0'>",
                    unsafe_allow_html=True)

    st.markdown("---")

    # ── Trend chart ───────────────────────────────────────────────────────
    if len(assessments) >= 2:
        st.markdown('<div class="section-header">📈 Score Trend Over Time</div>',
                    unsafe_allow_html=True)
        df = pd.DataFrame(assessments).sort_values("created_at")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["created_at"].str[:10],
            y=df["maturity_score"],
            mode="lines+markers+text",
            text=[f"{s:.2f}" for s in df["maturity_score"]],
            textposition="top center",
            textfont=dict(color="#e2e8f0", size=11),
            line=dict(color="#3b82f6", width=3),
            marker=dict(size=10, color="#60a5fa",
                        line=dict(color="#1e3a5f", width=2)),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.08)",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            yaxis=dict(range=[0,5.5], gridcolor="#1e293b"),
            xaxis=dict(gridcolor="#1e293b"),
            height=260, margin=dict(l=0,r=0,t=20,b=0),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)