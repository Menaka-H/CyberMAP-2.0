# pages/pg_benchmarking.py — Industry Benchmarking
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.database import get_all_assessments, get_assessment_by_id, get_questions
from utils.scoring import compute_domain_scores, get_maturity_label
from utils.questions_data import DOMAINS

BENCHMARKS = {
    "Technology":         {"Govern":3.8,"Identify":3.5,"Protect":3.7,"Detect":3.6,"Respond":3.4,"Recover":3.3,"overall":3.55},
    "Finance & Banking":  {"Govern":4.2,"Identify":4.0,"Protect":4.1,"Detect":3.9,"Respond":4.0,"Recover":3.8,"overall":4.00},
    "Healthcare":         {"Govern":3.2,"Identify":3.0,"Protect":3.4,"Detect":2.9,"Respond":3.1,"Recover":3.0,"overall":3.10},
    "Government":         {"Govern":3.5,"Identify":3.3,"Protect":3.4,"Detect":3.2,"Respond":3.3,"Recover":3.2,"overall":3.32},
    "Education":          {"Govern":2.8,"Identify":2.6,"Protect":2.9,"Detect":2.5,"Respond":2.7,"Recover":2.6,"overall":2.68},
    "Manufacturing":      {"Govern":2.9,"Identify":2.7,"Protect":3.0,"Detect":2.6,"Respond":2.8,"Recover":2.7,"overall":2.78},
    "Retail & E-commerce":{"Govern":3.0,"Identify":2.8,"Protect":3.1,"Detect":2.9,"Respond":2.9,"Recover":2.8,"overall":2.92},
    "Global Average":     {"Govern":3.2,"Identify":3.0,"Protect":3.2,"Detect":3.0,"Respond":3.1,"Recover":3.0,"overall":3.08},
}

def render():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#052e16,#0f172a);
                border-radius:14px;padding:24px 28px;margin-bottom:20px;
                border:1px solid #16a34a44">
        <h2 style="color:white;margin:0">📈 Industry Benchmarking</h2>
        <p style="color:#86efac;margin:6px 0 0 0">
            Compare your cybersecurity maturity against industry averages
            and global benchmarks.
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
    col1, col2 = st.columns(2)
    chosen   = col1.selectbox("Your assessment:", list(options.keys()))
    industry = col2.selectbox("Compare against:", list(BENCHMARKS.keys()))

    row = get_assessment_by_id(options[chosen])
    qs  = get_questions()
    domain_scores = compute_domain_scores(row["answers"], qs)
    benchmark     = BENCHMARKS[industry]
    overall       = row["maturity_score"]
    bench_overall = benchmark["overall"]
    diff          = round(overall - bench_overall, 2)

    st.markdown("---")

    # KPI cards
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        (c1, f"{overall:.2f}",       "Your score",           "#60a5fa"),
        (c2, f"{bench_overall:.2f}", f"{industry} avg",      "#34d399"),
        (c3, f"{diff:+.2f}",         "vs benchmark",
         "#22c55e" if diff >= 0 else "#ef4444"),
        (c4, ("Above" if diff >= 0 else "Below"),
         "benchmark status",
         "#22c55e" if diff >= 0 else "#ef4444"),
    ]
    for col, val, label, color in kpis:
        with col:
            st.markdown(f"""
            <div style="background:#1e293b;border:1px solid #334155;
                        border-radius:10px;padding:14px;text-align:center">
                <div style="font-size:1.5rem;font-weight:700;color:{color}">{val}</div>
                <div style="font-size:0.75rem;color:#64748b;
                            text-transform:uppercase;margin-top:4px">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Side-by-side radar comparison
    col_radar, col_bar = st.columns(2)

    with col_radar:
        st.markdown("#### 🕸️ Radar Comparison")
        labels = DOMAINS
        your_vals = [domain_scores.get(d, {}).get("score", 0) for d in labels]
        bench_vals = [benchmark.get(d, 3.0) for d in labels]
        y_closed = your_vals  + [your_vals[0]]
        b_closed = bench_vals + [bench_vals[0]]
        l_closed = labels     + [labels[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=y_closed, theta=l_closed, name="Your Score",
            fill="toself", fillcolor="rgba(59,130,246,0.15)",
            line=dict(color="#3b82f6", width=2),
        ))
        fig.add_trace(go.Scatterpolar(
            r=b_closed, theta=l_closed, name=industry,
            fill="toself", fillcolor="rgba(34,197,94,0.10)",
            line=dict(color="#22c55e", width=2, dash="dot"),
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0,5],
                                gridcolor="#1e293b", linecolor="#334155"),
                angularaxis=dict(gridcolor="#1e293b"),
                bgcolor="#0f172a",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            height=320, margin=dict(l=30,r=30,t=20,b=60),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_bar:
        st.markdown("#### 📊 Domain Gap vs Benchmark")
        gaps_vs = [
            round(domain_scores.get(d, {}).get("score", 0) - benchmark.get(d, 3.0), 2)
            for d in DOMAINS
        ]
        colors = ["#22c55e" if g >= 0 else "#ef4444" for g in gaps_vs]
        fig2 = go.Figure(go.Bar(
            x=DOMAINS, y=gaps_vs,
            marker_color=colors,
            text=[f"{g:+.2f}" for g in gaps_vs],
            textposition="outside",
            textfont=dict(color="#e2e8f0"),
        ))
        fig2.add_shape(type="line",
            x0=-0.5, x1=len(DOMAINS)-0.5, y0=0, y1=0,
            line=dict(color="#475569", width=1))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            yaxis=dict(gridcolor="#1e293b", title="Gap vs benchmark"),
            xaxis=dict(gridcolor="#1e293b"),
            showlegend=False,
            height=320, margin=dict(l=0,r=0,t=20,b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Detailed domain table
    st.markdown("#### 📋 Domain-by-Domain Comparison")
    rows = []
    for d in DOMAINS:
        your = domain_scores.get(d, {}).get("score", 0)
        bench = benchmark.get(d, 3.0)
        gap   = round(your - bench, 2)
        lbl, em, _ = get_maturity_label(your)
        rows.append({
            "Domain":        d,
            "Your Score":    f"{your:.2f}",
            "Industry Avg":  f"{bench:.2f}",
            "Gap":           f"{gap:+.2f}",
            "Your Level":    f"{em} {lbl}",
            "Status":        "✅ Above" if gap >= 0 else "❌ Below",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("---")

    # All industries comparison
    st.markdown("#### 🌍 Your Score vs All Industries")
    all_industries = list(BENCHMARKS.keys())
    all_scores     = [BENCHMARKS[i]["overall"] for i in all_industries]
    bar_colors     = ["#3b82f6" if i == industry
                      else "#22c55e" if BENCHMARKS[i]["overall"] <= overall
                      else "#ef4444" for i in all_industries]

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=all_industries, y=all_scores,
        marker_color=bar_colors,
        text=[f"{s:.2f}" for s in all_scores],
        textposition="outside",
        textfont=dict(color="#e2e8f0"),
        name="Industry avg",
    ))
    fig3.add_shape(type="line",
        x0=-0.5, x1=len(all_industries)-0.5, y0=overall, y1=overall,
        line=dict(color="#60a5fa", width=2, dash="dash"))
    fig3.add_annotation(
        x=len(all_industries)-1, y=overall+0.1,
        text=f"Your score: {overall:.2f}",
        showarrow=False, font=dict(color="#60a5fa", size=11))
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        yaxis=dict(range=[0,5], gridcolor="#1e293b"),
        xaxis=dict(tickangle=-20),
        showlegend=False,
        height=300, margin=dict(l=0,r=0,t=20,b=60),
    )
    st.plotly_chart(fig3, use_container_width=True)