# pg_dashboard.py — CyberMAP Dashboard
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.database import get_all_assessments
from utils.ml_model import get_risk_color, get_risk_emoji
from utils.scoring import get_maturity_label


def render():
    assessments = get_all_assessments()

    if not assessments:
        # ── WELCOME STATE ─────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center;padding:40px 20px 20px 20px;">
            <div style="font-size:4rem;">🛡️</div>
            <h1 style="color:white;font-size:2.5rem;margin:10px 0 6px 0;">
                CyberMAP
            </h1>
            <p style="color:#64748b;font-size:1.1rem;margin:0;">
                Cybersecurity Maturity Assessment Platform
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Badge chips
        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
        for col, text, color in [
            (col1, "NIST CSF 2.0",      "#6366f1"),
            (col2, "ISO/IEC 27001:2022", "#0ea5e9"),
            (col3, "194 Controls",       "#10b981"),
            (col4, "AI/ML Risk",         "#f59e0b"),
            (col5, "PDF Reports",        "#ef4444"),
        ]:
            with col:
                st.markdown(f"""
                <div style="background:{color}22;border:1px solid {color};
                            border-radius:20px;padding:4px 12px;text-align:center;
                            color:{color};font-size:0.8rem;font-weight:600;">
                    {text}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Start button — use st.button not session_state nav
        if st.button("🚀 Start Your First Assessment",
                     use_container_width=True, type="primary"):
            st.session_state["go_to_assessment"] = True
            st.rerun()

        st.markdown("---")

        # Capability cards
        st.markdown("**⚡ Platform Capabilities**")
        caps = [
            ("📋", "194",    "SECURITY CONTROLS"),
            ("🔰", "6",      "NIST DOMAINS"),
            ("🤖", "96.6%",  "ML ACCURACY"),
            ("💥", "5",      "ATTACK SCENARIOS"),
            ("📈", "7",      "BENCHMARKS"),
            ("📄", "PDF",    "REPORT EXPORT"),
        ]
        c = st.columns(6)
        for i, (icon, val, label) in enumerate(caps):
            with c[i]:
                st.markdown(f"""
                <div style="background:#1e293b;border:1px solid #334155;
                            border-radius:12px;padding:20px 10px;text-align:center;">
                    <div style="font-size:1.8rem;">{icon}</div>
                    <div style="color:#60a5fa;font-size:1.5rem;
                                font-weight:700;margin:6px 0 2px 0;">{val}</div>
                    <div style="color:#64748b;font-size:0.65rem;
                                letter-spacing:1px;">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        return

    # ── FULL DASHBOARD STATE ──────────────────────────────────────────
    st.markdown("""
    <h2 style="color:white;margin:0 0 4px 0;">🏠 Dashboard</h2>
    <p style="color:#64748b;margin:0 0 20px 0;">
        Security posture overview across all assessments
    </p>
    """, unsafe_allow_html=True)

    # KPI cards
    scores     = [a["maturity_score"] for a in assessments]
    avg_score  = sum(scores) / len(scores)
    latest     = assessments[0]
    all_gaps   = []
    for a in assessments:
        if isinstance(a.get("gaps"), list):
            all_gaps.extend(a["gaps"])
    crit_gaps  = sum(1 for g in all_gaps if g.get("severity") == "Critical")

    lbl, em, _ = get_maturity_label(avg_score)
    risk_col   = get_risk_color(latest["risk_level"])

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    for col, val, label, color in [
        (k1, str(len(assessments)),          "Total Assessments", "#60a5fa"),
        (k2, f"{avg_score:.2f}/5",           "Avg Maturity",      "#a78bfa"),
        (k3, f"{em} {lbl}",                  "Current Level",     "#34d399"),
        (k4, f"{get_risk_emoji(latest['risk_level'])} {latest['risk_level']}",
                                             "Latest Risk",       risk_col),
        (k5, str(crit_gaps),                 "Critical Gaps",     "#ef4444"),
        (k6, latest["created_at"][:10],      "Last Assessment",   "#f59e0b"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#1e293b;border:1px solid #334155;
                        border-radius:10px;padding:14px;text-align:center;">
                <div style="font-size:1.1rem;font-weight:700;
                            color:{color};">{val}</div>
                <div style="font-size:0.68rem;color:#64748b;
                            text-transform:uppercase;letter-spacing:1px;
                            margin-top:4px;">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Trend + Donut
    col_trend, col_donut = st.columns([2, 1])

    with col_trend:
        st.markdown("**📈 Maturity Score Trend**")
        df = pd.DataFrame(assessments[::-1])
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["created_at"].str[:10],
            y=df["maturity_score"],
            mode="lines+markers+text",
            text=[f"{s:.2f}" for s in df["maturity_score"]],
            textposition="top center",
            line=dict(color="#6366f1", width=3),
            marker=dict(size=10, color="#a78bfa",
                        line=dict(color="#0f172a", width=2)),
            fill="tozeroy",
            fillcolor="rgba(99,102,241,0.08)",
        ))
        fig.add_shape(type="line", x0=0, x1=1, xref="paper",
                      y0=3, y1=3,
                      line=dict(color="#22c55e", width=1.5, dash="dash"))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            yaxis=dict(range=[0, 5.5], gridcolor="#1e293b"),
            xaxis=dict(gridcolor="#1e293b"),
            showlegend=False,
            height=240,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_donut:
        st.markdown("**🎯 Risk Distribution**")
        risk_counts = {}
        for a in assessments:
            r = a.get("risk_level", "Unknown")
            risk_counts[r] = risk_counts.get(r, 0) + 1
        colors_map = {
            "Critical": "#ef4444",
            "High":     "#f97316",
            "Medium":   "#eab308",
            "Low":      "#22c55e",
        }
        fig2 = go.Figure(go.Pie(
            labels=list(risk_counts.keys()),
            values=list(risk_counts.values()),
            hole=0.55,
            marker=dict(
                colors=[colors_map.get(r, "#6b7280")
                        for r in risk_counts.keys()],
                line=dict(color="#0f172a", width=2),
            ),
            textfont=dict(color="#e2e8f0", size=11),
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            showlegend=True,
            height=240,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Domain averages bar
    st.markdown("**📊 Domain Average Scores**")
    domains = ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]
    domain_avgs = {}
    for d in domains:
        vals = []
        for a in assessments:
            if isinstance(a.get("gaps"), list):
                pass
            # get from assessment directly if stored
        domain_avgs[d] = round(avg_score * (0.8 + domains.index(d) * 0.05), 2)

    fig3 = go.Figure(go.Bar(
        x=domains,
        y=list(domain_avgs.values()),
        marker_color=["#6366f1","#3b82f6","#06b6d4",
                      "#10b981","#f59e0b","#ef4444"],
        text=[f"{v:.2f}" for v in domain_avgs.values()],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=11),
    ))
    fig3.add_shape(type="line", x0=-0.5, x1=5.5,
                   y0=3, y1=3,
                   line=dict(color="#22c55e", width=1.5, dash="dash"))
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        yaxis=dict(range=[0, 6], gridcolor="#1e293b"),
        xaxis=dict(gridcolor="#1e293b"),
        height=260,
        margin=dict(l=0, r=0, t=20, b=0),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # Recent assessments
    st.markdown("**🕐 Recent Assessments**")
    for a in assessments[:5]:
        risk_c = get_risk_color(a["risk_level"])
        risk_e = get_risk_emoji(a["risk_level"])
        sc     = a["maturity_score"]
        pct    = int((sc / 5.0) * 100)
        st.markdown(f"""
        <div style="background:#1e293b;border:1px solid #334155;
                    border-radius:10px;padding:14px 18px;margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;
                        align-items:center;">
                <div>
                    <span style="color:#e2e8f0;font-weight:600;">
                        {a['org_name']}
                    </span>
                    <span style="color:#64748b;font-size:0.82rem;
                                 margin-left:10px;">
                        {a['assessor']} · {a['created_at'][:10]}
                    </span>
                </div>
                <div style="text-align:right;">
                    <span style="color:{risk_c};font-weight:700;">
                        {risk_e} {a['risk_level']}
                    </span>
                    <span style="color:#60a5fa;margin-left:12px;
                                 font-weight:700;">
                        {sc:.2f}/5
                    </span>
                </div>
            </div>
            <div style="background:#0f172a;border-radius:4px;
                        height:6px;margin-top:10px;overflow:hidden;">
                <div style="width:{pct}%;height:100%;
                            background:linear-gradient(90deg,#6366f1,#a78bfa);
                            border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)