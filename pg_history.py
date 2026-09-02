# pg_history.py — Professional History Page (CyberMAP)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.database import get_all_assessments
from utils.ml_model import get_risk_emoji, get_risk_color
from utils.predictive_analysis import get_score_history, predict_future_maturity


def render():
    st.markdown("""
<style>
.history-card { background:#1e293b; border:1px solid #334155; border-radius:12px; padding:18px 20px; margin-bottom:10px; }
.section-header { font-size:1.05rem; font-weight:600; color:#e2e8f0; border-left:4px solid #3b82f6; padding-left:12px; margin:20px 0 12px 0; }
</style>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="background:linear-gradient(135deg,#1e3a5f,#0f172a);border-radius:14px;padding:24px 28px;margin-bottom:20px;border:1px solid #2563eb44">
<h2 style="color:white;margin:0">📁 Assessment History</h2>
<p style="color:#93c5fd;margin:6px 0 0 0">All past assessments stored in the database</p>
</div>
""", unsafe_allow_html=True)

    assessments = get_all_assessments()

    if not assessments:
        st.info("No assessments yet. Complete your first assessment to see history.")
        return

    # ── Summary stats ─────────────────────────────────────────────────────
    total     = len(assessments)
    avg_score = sum((a["maturity_score"] or 0) for a in assessments) / total
    best      = max(assessments, key=lambda x: x["maturity_score"] or 0)

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, color in [
        (c1, str(total),                       "Total Assessments", "#60a5fa"),
        (c2, f"{avg_score:.2f}/5.00",          "Average Score",     "#34d399"),
        (c3, f"{best['maturity_score']:.2f}",  "Best Score",        "#a78bfa"),
        (c4, str(best["org_name"])[:16],       "Top Organisation",  "#fb923c"),
    ]:
        with col:
            st.markdown(
                f'<div style="background:#1e293b;border:1px solid #334155;'
                f'border-radius:10px;padding:14px;text-align:center">'
                f'<div style="font-size:1.3rem;font-weight:700;color:{color}">{val}</div>'
                f'<div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;'
                f'letter-spacing:1px;margin-top:4px">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Assessment cards ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 All Assessments</div>',
                unsafe_allow_html=True)

    for a in assessments:
        score = a.get("maturity_score", 0) or 0
        risk  = a.get("risk_level", "—")
        pct   = int((score / 5) * 100)
        clr   = get_risk_color(risk)
        emoji = get_risk_emoji(risk)

        col_info, col_score, col_btn = st.columns([4, 3, 2])

        with col_info:
            st.markdown(
                f'<div style="padding:8px 0">'
                f'<div style="font-weight:600;color:#e2e8f0;font-size:1rem">{a["org_name"]}</div>'
                f'<div style="color:#64748b;font-size:0.85rem;margin-top:2px">'
                f'👤 {a["assessor"]} &nbsp;·&nbsp; 📅 {str(a["created_at"])[:10]} &nbsp;·&nbsp; ID #{a["id"]}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with col_score:
            st.markdown(
                f'<div style="padding:8px 0">'
                f'<div style="display:flex;align-items:center;gap:8px">'
                f'<div style="flex:1;background:#0f172a;border-radius:6px;height:8px;overflow:hidden">'
                f'<div style="width:{pct}%;height:100%;background:{clr};border-radius:6px"></div>'
                f'</div>'
                f'<span style="color:{clr};font-weight:700;min-width:36px">{score:.2f}</span>'
                f'</div>'
                f'<div style="color:{clr};font-size:0.85rem;margin-top:4px">{emoji} {risk} Risk</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with col_btn:
            st.write("")
            if st.button("📊 View", key=f"view_{a['id']}", use_container_width=True):
                for k in ["last_domain_scores", "last_overall_score", "last_gaps",
                          "last_ml_result", "last_org_name", "last_assessor"]:
                    st.session_state.pop(k, None)

                aid = a["id"]
                st.session_state["last_assessment_id"] = aid
                st.session_state["last_aid"]           = aid
                st.session_state["_default_nav"] = "Results & Analysis"
                st.rerun()

        st.markdown("<hr style='border-color:#1e293b;margin:4px 0'>",
                    unsafe_allow_html=True)

    st.markdown("---")

    # ── Score Trend Over Time ─────────────────────────────────────────────
    if len(assessments) >= 2:
        st.markdown('<div class="section-header">📈 Score Trend Over Time</div>',
                    unsafe_allow_html=True)

        df = pd.DataFrame(assessments)
        sort_col = "id" if "id" in df.columns else "created_at"
        df = df.sort_values(sort_col).reset_index(drop=True)

        x_labels = [
            f"#{row['id']} · {str(row['created_at'])[:10]}"
            for _, row in df.iterrows()
        ]
        y_vals = [round(float(v or 0), 2) for v in df["maturity_score"]]
        hover  = [
            f"{row['org_name']}<br>{str(row['created_at'])[:10]}"
            f"<br>Score: {float(row['maturity_score'] or 0):.2f} / 5"
            for _, row in df.iterrows()
        ]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_labels,
            y=y_vals,
            mode="lines+markers+text",
            text=[f"{v:.2f}" for v in y_vals],
            textposition="top center",
            textfont=dict(color="#e2e8f0", size=12),
            line=dict(color="#3b82f6", width=3, shape="spline"),
            marker=dict(size=13, color="#60a5fa",
                        line=dict(color="#1e3a5f", width=2)),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.10)",
            hovertext=hover,
            hoverinfo="text",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            height=340,
            margin=dict(l=10, r=20, t=40, b=50),
            showlegend=False,
            yaxis=dict(
                range=[0, 5.5], dtick=1, gridcolor="#1e293b",
                zeroline=False, title="Maturity Score",
            ),
            xaxis=dict(
                type="category", gridcolor="#1e293b",
                tickangle=0, automargin=True, title="Assessment",
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("📈 Complete at least two assessments to see the score trend over time.")

    st.markdown("---")

    # ── Predictive Maturity Analysis (CyberMAP 2.0) ────────────────────────
    st.markdown('<div class="section-header">🔮 Predictive Maturity Analysis</div>',
                unsafe_allow_html=True)

    org_names = sorted(set(a["org_name"] for a in assessments))
    selected_org = st.selectbox(
        "Select organisation to forecast:",
        org_names,
        key="predictive_org_select",
    )

    dates, scores = get_score_history(selected_org, assessments)
    result = predict_future_maturity(dates, scores)

    if not result.get("has_enough_data"):
        st.info(
            f"'{selected_org}' has only {len(scores)} assessment(s) on record. "
            f"At least 2 assessments are needed to project a trend, and 3+ "
            f"give a more reliable estimate."
        )
    else:
        direction_icon = {
            "Improving": "📈",
            "Declining": "📉",
            "Stable": "➡️",
        }.get(result["trend_direction"], "➡️")
        direction_color = {
            "Improving": "#22c55e",
            "Declining": "#ef4444",
            "Stable": "#f59e0b",
        }.get(result["trend_direction"], "#94a3b8")

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Current Score", f"{result['current_score']:.2f} / 5.00")
        col_b.metric(
            "Trend",
            f"{direction_icon} {result['trend_direction']}",
        )
        col_c.metric("Confidence", result["confidence"])

        st.markdown(f"""
        <div style="background:#0f172a;border-left:4px solid {direction_color};
                    border-radius:8px;padding:14px 18px;margin:12px 0;">
            <p style="color:#e2e8f0;margin:0;font-size:0.95rem;">
                Based on {result['data_points_used']} assessments for
                <b>{selected_org}</b>, the maturity score is changing at
                approximately <b>{result['rate_per_month']:+.3f} points per
                month</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Projected Future Scores**")
        proj_cols = st.columns(3)
        for i, (months, projected) in enumerate(result["projections"].items()):
            with proj_cols[i]:
                st.markdown(f"""
                <div style="background:#1e293b;border:1px solid #334155;
                            border-radius:10px;padding:16px;text-align:center;">
                    <div style="color:#64748b;font-size:0.78rem;
                                text-transform:uppercase;">
                        In {months} month{'s' if months > 1 else ''}
                    </div>
                    <div style="color:{direction_color};font-size:1.6rem;
                                font-weight:700;margin-top:4px;">
                        {projected:.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if result["r_squared"] is not None:
            st.caption(
                f"Linear fit quality (R²): {result['r_squared']} — "
                f"closer to 1.0 indicates a more consistent trend across "
                f"assessments."
            )

        st.caption(
            "⚠️ This is a simple linear projection assuming the current "
            "rate of improvement continues unchanged. It does not account "
            "for new risks, organisational changes, or non-linear "
            "improvement patterns, and should be treated as an indicative "
            "planning estimate rather than a guarantee."
        )