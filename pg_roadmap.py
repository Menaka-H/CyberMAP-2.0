# pg_roadmap.py — 90-Day Remediation Roadmap Generator
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.database import get_all_assessments, get_assessment_by_id, get_questions
from utils.scoring import compute_domain_scores, identify_gaps, get_maturity_label

EFFORT = {
    "Critical": {"days": 7,  "effort": "High",   "cost": "₹₹₹"},
    "High":     {"days": 30, "effort": "Medium",  "cost": "₹₹"},
    "Medium":   {"days": 90, "effort": "Low",     "cost": "₹"},
}

QUICK_WINS = [
    "Enable MFA on all admin accounts",
    "Apply all pending critical patches",
    "Review and revoke unused user accounts",
    "Enable centralized logging",
    "Back up all critical data and test restoration",
]

def build_roadmap(gaps):
    phases = {
        "Phase 1 — Immediate (Days 1–7)":   [],
        "Phase 2 — Short-term (Days 8–30)":  [],
        "Phase 3 — Medium-term (Days 31–90)": [],
    }
    for g in gaps:
        sev = g.get("severity", "Medium")
        task = {
            "control":    g["subdomain"],
            "domain":     g["domain"],
            "action":     g["recommendation"],
            "nist":       g["nist_ref"],
            "iso":        g["iso_ref"],
            "score":      g["score"],
            "severity":   sev,
            "effort":     EFFORT[sev]["effort"],
            "cost":       EFFORT[sev]["cost"],
        }
        if sev == "Critical":
            phases["Phase 1 — Immediate (Days 1–7)"].append(task)
        elif sev == "High":
            phases["Phase 2 — Short-term (Days 8–30)"].append(task)
        else:
            phases["Phase 3 — Medium-term (Days 31–90)"].append(task)
    return phases


def gantt_chart(phases):
    colors = {
        "Phase 1 — Immediate (Days 1–7)":    "#ef4444",
        "Phase 2 — Short-term (Days 8–30)":  "#f97316",
        "Phase 3 — Medium-term (Days 31–90)":"#eab308",
    }
    ranges = {
        "Phase 1 — Immediate (Days 1–7)":    (1,  7),
        "Phase 2 — Short-term (Days 8–30)":  (8,  30),
        "Phase 3 — Medium-term (Days 31–90)":(31, 90),
    }
    fig = go.Figure()
    for phase, tasks in phases.items():
        if tasks:
            start, end = ranges[phase]
            for task in tasks[:5]:
                fig.add_trace(go.Bar(
                    x=[end - start],
                    y=[f"{task['domain']}: {task['control'][:25]}"],
                    base=[start],
                    orientation="h",
                    marker_color=colors[phase],
                    name=phase,
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{task['control']}</b><br>"
                        f"Domain: {task['domain']}<br>"
                        f"Days {start}–{end}<br>"
                        f"Severity: {task['severity']}<extra></extra>"
                    ),
                ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        xaxis=dict(title="Day", range=[0, 95], gridcolor="#1e293b"),
        yaxis=dict(gridcolor="#1e293b", tickfont=dict(size=10)),
        barmode="overlay",
        height=max(300, len([t for p in phases.values() for t in p[:5]]) * 35),
        margin=dict(l=0, r=0, t=20, b=0),
    )
    return fig


def render():
    st.markdown("""
    <style>
    .road-header {
        background:linear-gradient(135deg,#1c1917,#0f172a);
        border-radius:14px; padding:24px 28px; margin-bottom:20px;
        border:1px solid #f97316aa;
    }
    .phase-card {
        border-radius:10px; padding:14px 16px; margin-bottom:8px;
    }
    .task-row {
        background:#0f172a; border-radius:8px;
        padding:10px 14px; margin-bottom:6px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="road-header">
        <h2 style="color:white;margin:0;">🗺️ 90-Day Remediation Roadmap</h2>
        <p style="color:#fed7aa;margin:6px 0 0 0;">
            Auto-generated priority-based security improvement plan
            based on your assessment gaps.
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
    chosen = st.selectbox("Select assessment:", list(options.keys()))
    row = get_assessment_by_id(options[chosen])
    qs  = get_questions()
    domain_scores = compute_domain_scores(row["answers"], qs)
    gaps = identify_gaps(row["answers"], qs, threshold=3)

    if not gaps:
        st.success("✅ No gaps found! Your organisation is well-secured.")
        return

    phases = build_roadmap(gaps)

    # Summary stats
    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, color in [
        (c1, str(len(gaps)),
         "Total Gaps",    "#60a5fa"),
        (c2, str(len(phases["Phase 1 — Immediate (Days 1–7)"])),
         "Immediate Actions", "#ef4444"),
        (c3, str(len(phases["Phase 2 — Short-term (Days 8–30)"])),
         "Short-term",    "#f97316"),
        (c4, str(len(phases["Phase 3 — Medium-term (Days 31–90)"])),
         "Medium-term",   "#eab308"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#1e293b;border:1px solid #334155;
                        border-radius:10px;padding:14px;text-align:center;">
                <div style="font-size:1.8rem;font-weight:700;
                            color:{color};">{val}</div>
                <div style="font-size:0.75rem;color:#64748b;
                            text-transform:uppercase;letter-spacing:1px;">
                    {label}
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Quick wins
    st.markdown("### ⚡ Quick Wins — Do These First")
    qw_cols = st.columns(len(QUICK_WINS))
    for i, qw in enumerate(QUICK_WINS):
        with qw_cols[i]:
            st.markdown(f"""
            <div style="background:#1e293b;border:1px solid #22c55e33;
                        border-radius:10px;padding:12px;text-align:center;
                        height:100px;display:flex;align-items:center;
                        justify-content:center;">
                <div style="color:#86efac;font-size:0.82rem;">{qw}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Gantt chart
    st.markdown("### 📅 90-Day Gantt Chart")
    st.plotly_chart(gantt_chart(phases), use_container_width=True)

    st.markdown("---")

    # Phase details
    phase_colors = {
        "Phase 1 — Immediate (Days 1–7)":    ("#ef4444", "#1e0505"),
        "Phase 2 — Short-term (Days 8–30)":  ("#f97316", "#1c1005"),
        "Phase 3 — Medium-term (Days 31–90)":("#eab308", "#1c1a05"),
    }

    for phase_name, tasks in phases.items():
        if not tasks:
            continue
        color, bg = phase_colors[phase_name]
        with st.expander(
            f"{phase_name} — {len(tasks)} actions",
            expanded=(phase_name == "Phase 1 — Immediate (Days 1–7)")
        ):
            for i, task in enumerate(tasks, 1):
                st.markdown(f"""
                <div class="task-row">
                    <div style="display:flex;justify-content:space-between;
                                align-items:flex-start;">
                        <div style="flex:1;">
                            <span style="color:{color};font-weight:700;">
                                #{i}
                            </span>
                            <span style="color:#e2e8f0;font-weight:600;
                                         margin-left:8px;">
                                {task['domain']} — {task['control']}
                            </span>
                            <p style="color:#94a3b8;margin:6px 0 4px 0;
                                      font-size:0.88rem;">
                                💡 {task['action']}
                            </p>
                            <span style="background:#1e293b;color:#60a5fa;
                                         border-radius:4px;padding:2px 8px;
                                         font-size:0.75rem;">
                                {task['nist']}
                            </span>
                            <span style="background:#1e293b;color:#34d399;
                                         border-radius:4px;padding:2px 8px;
                                         font-size:0.75rem;margin-left:4px;">
                                {task['iso']}
                            </span>
                        </div>
                        <div style="text-align:right;min-width:80px;">
                            <div style="color:{color};font-weight:700;">
                                {task['severity']}
                            </div>
                            <div style="color:#64748b;font-size:0.78rem;">
                                Effort: {task['effort']}
                            </div>
                            <div style="color:#64748b;font-size:0.78rem;">
                                {task['cost']}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)