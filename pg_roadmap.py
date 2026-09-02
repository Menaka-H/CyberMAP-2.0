# pg_roadmap.py — 90-Day Remediation Roadmap Generator
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.database import get_all_assessments, get_assessment_by_id, get_questions
from utils.scoring import compute_domain_scores, identify_gaps, get_maturity_label
from utils.prioritization import prioritize_gaps, apply_cve_boost

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
            "control":        g["subdomain"],
            "domain":         g["domain"],
            "action":         g["recommendation"],
            "nist":           g["nist_ref"],
            "iso":            g["iso_ref"],
            "score":          g["score"],
            "severity":       sev,
            "effort":         EFFORT[sev]["effort"],
            "cost":           EFFORT[sev]["cost"],
            "priority_score": g.get("priority_score", 0),
            "cve_count":      g.get("cve_count", 0),
        }
        if sev == "Critical":
            phases["Phase 1 — Immediate (Days 1–7)"].append(task)
        elif sev == "High":
            phases["Phase 2 — Short-term (Days 8–30)"].append(task)
        else:
            phases["Phase 3 — Medium-term (Days 31–90)"].append(task)

    for phase_name in phases:
        phases[phase_name].sort(key=lambda t: t["priority_score"], reverse=True)

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
                        f"Severity: {task['severity']}<br>"
                        f"Priority Score: {task['priority_score']}<extra></extra>"
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
            based on your assessment gaps, ranked by severity, business
            impact, exploitability, remediation effort, and real known
            vulnerabilities where applicable.
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

    gaps = prioritize_gaps(gaps)

    with st.spinner("Checking top gaps against live vulnerability data..."):
        try:
            gaps = apply_cve_boost(gaps, max_checks=5)
        except Exception:
            pass

    phases = build_roadmap(gaps)

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
            st.markdown(
                f'<div style="background:#1e293b;border:1px solid #334155;'
                f'border-radius:10px;padding:14px;text-align:center;">'
                f'<div style="font-size:1.8rem;font-weight:700;color:{color};">{val}</div>'
                f'<div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    if gaps:
        top_gap = gaps[0]
        cve_badge = ""
        if top_gap.get("cve_count", 0) > 0:
            cve_badge = (
                f'<span style="background:#dc262633;color:#fca5a5;'
                f'border-radius:4px;padding:2px 8px;font-size:0.75rem;'
                f'margin-left:8px;">⚠️ {top_gap["cve_count"]} known CVEs found</span>'
            )

        st.markdown("### 🎯 Highest Priority Fix")
        st.markdown(
            f'<div style="background:#0f172a;border-left:4px solid #a855f7;'
            f'border-radius:8px;padding:14px 18px;margin-bottom:10px;">'
            f'<span style="color:#a855f7;font-weight:700;">Priority Score: {top_gap.get("priority_score", 0)}</span>'
            f'{cve_badge}'
            f'<p style="color:#e2e8f0;margin:6px 0 2px 0;font-weight:600;">{top_gap["domain"]} — {top_gap["subdomain"]}</p>'
            f'<p style="color:#94a3b8;margin:0;font-size:0.88rem;">{top_gap["question"]}</p>'
            f'<p style="color:#fbbf24;margin:6px 0 0 0;font-size:0.85rem;">💡 {top_gap["recommendation"]}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Ranked using Priority Score = (Severity × Business Impact × "
            "Exploitability) ÷ Remediation Effort, with a 1.5× boost "
            "applied to the top 5 gaps if real, currently known CVEs "
            "are found for that control area via a live NVD lookup."
        )

    st.markdown("---")

    st.markdown("### ⚡ Quick Wins — Do These First")
    qw_cols = st.columns(len(QUICK_WINS))
    for i, qw in enumerate(QUICK_WINS):
        with qw_cols[i]:
            st.markdown(
                f'<div style="background:#1e293b;border:1px solid #22c55e33;'
                f'border-radius:10px;padding:12px;text-align:center;'
                f'height:100px;display:flex;align-items:center;justify-content:center;">'
                f'<div style="color:#86efac;font-size:0.82rem;">{qw}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    st.markdown("### 📅 90-Day Gantt Chart")
    st.plotly_chart(gantt_chart(phases), use_container_width=True)

    st.markdown("---")

    phase_colors = {
        "Phase 1 — Immediate (Days 1–7)":    "#ef4444",
        "Phase 2 — Short-term (Days 8–30)":  "#f97316",
        "Phase 3 — Medium-term (Days 31–90)":"#eab308",
    }

    for phase_name, tasks in phases.items():
        if not tasks:
            continue
        color = phase_colors[phase_name]
        with st.expander(
            f"{phase_name} — {len(tasks)} actions",
            expanded=(phase_name == "Phase 1 — Immediate (Days 1–7)")
        ):
            for i, task in enumerate(tasks, 1):
                cve_tag = ""
                if task.get("cve_count", 0) > 0:
                    cve_tag = (
                        f'<span style="background:#dc262633;color:#fca5a5;'
                        f'border-radius:4px;padding:2px 8px;font-size:0.72rem;'
                        f'margin-left:8px;">⚠️ {task["cve_count"]} CVEs</span>'
                    )

                task_html = (
                    f'<div class="task-row">'
                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                    f'<div style="flex:1;">'
                    f'<span style="color:{color};font-weight:700;">#{i}</span>'
                    f'<span style="color:#e2e8f0;font-weight:600;margin-left:8px;">{task["domain"]} — {task["control"]}</span>'
                    f'<span style="background:#a855f733;color:#c084fc;border-radius:4px;padding:2px 8px;font-size:0.72rem;margin-left:8px;">Priority: {task["priority_score"]}</span>'
                    f'{cve_tag}'
                    f'<p style="color:#94a3b8;margin:6px 0 4px 0;font-size:0.88rem;">💡 {task["action"]}</p>'
                    f'<span style="background:#1e293b;color:#60a5fa;border-radius:4px;padding:2px 8px;font-size:0.75rem;">{task["nist"]}</span>'
                    f'<span style="background:#1e293b;color:#34d399;border-radius:4px;padding:2px 8px;font-size:0.75rem;margin-left:4px;">{task["iso"]}</span>'
                    f'</div>'
                    f'<div style="text-align:right;min-width:80px;">'
                    f'<div style="color:{color};font-weight:700;">{task["severity"]}</div>'
                    f'<div style="color:#64748b;font-size:0.78rem;">Effort: {task["effort"]}</div>'
                    f'<div style="color:#64748b;font-size:0.78rem;">{task["cost"]}</div>'
                    f'</div>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(task_html, unsafe_allow_html=True)