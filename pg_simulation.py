# pages/pg_simulation.py — Attack Impact Simulation
import streamlit as st
import plotly.graph_objects as go
from utils.database import get_all_assessments, get_assessment_by_id, get_questions
from utils.scoring import compute_domain_scores

ATTACKS = {
    "🔒 Ransomware": {
        "desc": "Encrypts files and demands payment. Exploits weak endpoints, backups and patching.",
        "domains": {"Protect": 0.35, "Detect": 0.25, "Recover": 0.30, "Respond": 0.10},
        "mitigations": [
            "Deploy EDR on all endpoints (Protect — PR.PS-04)",
            "Maintain tested offline backups (Recover — RC.RP-01)",
            "Apply patches within 30 days (Protect — PR.PS-02)",
            "Test incident response plan (Respond — RS.MA-02)",
            "Enable email filtering (Detect — DE.CM-04)",
        ],
    },
    "🎣 Phishing / BEC": {
        "desc": "Tricks users into revealing credentials or transferring funds via deceptive emails.",
        "domains": {"Govern": 0.30, "Protect": 0.40, "Detect": 0.30},
        "mitigations": [
            "Conduct phishing simulation training (Govern — GV.AT-01)",
            "Enable MFA on all email accounts (Protect — PR.AA-03)",
            "Deploy email security gateway (Detect — DE.CM-04)",
            "Implement DMARC/DKIM/SPF (Protect — PR.PS-05)",
            "Train staff to verify unusual requests (Govern — GV.AT-02)",
        ],
    },
    "👤 Insider Threat": {
        "desc": "Malicious or accidental data theft/sabotage by employees or contractors.",
        "domains": {"Govern": 0.20, "Identify": 0.20, "Protect": 0.30, "Detect": 0.30},
        "mitigations": [
            "Enforce least privilege access (Protect — PR.AA-05)",
            "Enable user behaviour analytics (Detect — DE.CM-03)",
            "Review access rights every 6 months (Protect — PR.AA-05)",
            "Deploy DLP to monitor data transfers (Protect — PR.DS-05)",
            "Log and monitor privileged user activity (Detect — DE.CM-03)",
        ],
    },
    "🌐 Supply Chain Attack": {
        "desc": "Compromises a vendor or software supplier to gain access to your systems.",
        "domains": {"Govern": 0.40, "Identify": 0.30, "Detect": 0.30},
        "mitigations": [
            "Assess vendor security before onboarding (Govern — GV.SC-02)",
            "Include security clauses in all contracts (Govern — GV.SC-03)",
            "Monitor third-party access continuously (Detect — DE.CM-01)",
            "Maintain software bill of materials (Identify — ID.AM-02)",
            "Audit supplier access quarterly (Govern — GV.SC-04)",
        ],
    },
    "💉 SQL Injection / Web Attack": {
        "desc": "Exploits vulnerable web applications to steal data or gain system access.",
        "domains": {"Identify": 0.20, "Protect": 0.50, "Detect": 0.30},
        "mitigations": [
            "Deploy WAF on all web applications (Protect — PR.PS-05)",
            "Train developers in secure coding (Protect — PR.PS-03)",
            "Conduct quarterly web vulnerability scans (Detect — DE.AE-04)",
            "Perform annual penetration testing (Detect — DE.AE-06)",
            "Run code reviews before deployment (Protect — PR.PS-03)",
        ],
    },
}

def compute_attack_risk(domain_scores, attack_weights):
    """
    Calculate attack success probability.
    Lower domain scores = higher attack probability.
    """
    weighted_vulnerability = 0.0
    for domain, weight in attack_weights.items():
        score = domain_scores.get(domain, {}).get("score", 0)
        vulnerability = (5.0 - score) / 5.0
        weighted_vulnerability += vulnerability * weight
    return round(weighted_vulnerability * 100, 1)

def risk_gauge(probability, attack_name):
    color = ("#ef4444" if probability >= 70 else
             "#f97316" if probability >= 50 else
             "#eab308" if probability >= 30 else "#22c55e")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability,
        number={"suffix": "%", "font": {"size": 32, "color": "#e2e8f0"}},
        title={"text": attack_name, "font": {"size": 13, "color": "#94a3b8"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#475569"},
            "bar":  {"color": color, "thickness": 0.3},
            "bgcolor": "#0f172a",
            "steps": [
                {"range": [0,  30], "color": "#052e16"},
                {"range": [30, 50], "color": "#1c1a05"},
                {"range": [50, 70], "color": "#1c1005"},
                {"range": [70,100], "color": "#1e0505"},
            ],
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        height=220, margin=dict(l=20,r=20,t=40,b=10),
    )
    return fig

def render():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#450a0a,#0f172a);
                border-radius:14px;padding:24px 28px;margin-bottom:20px;
                border:1px solid #ef444444">
        <h2 style="color:white;margin:0">💥 Attack Impact Simulation</h2>
        <p style="color:#fca5a5;margin:6px 0 0 0">
            Simulate real-world cyber attacks against your security posture
            to understand where you are most vulnerable.
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
    chosen = st.selectbox("Select assessment to simulate against:", list(options.keys()))
    row    = get_assessment_by_id(options[chosen])
    qs     = get_questions()
    domain_scores = compute_domain_scores(row["answers"], qs)

    st.markdown("---")
    st.markdown("### 🎯 Attack Success Probability by Threat Type")
    st.caption(
        "Probability = how likely this attack would succeed given your "
        "current security controls. Higher score = better protection = lower probability."
    )

    # Compute all attack risks
    results = {}
    for attack_name, attack_data in ATTACKS.items():
        prob = compute_attack_risk(domain_scores, attack_data["domains"])
        results[attack_name] = prob

    # Show gauges in a grid
    cols = st.columns(3)
    for i, (attack, prob) in enumerate(results.items()):
        with cols[i % 3]:
            st.plotly_chart(risk_gauge(prob, attack),
                            use_container_width=True)

    st.markdown("---")

    # Detailed simulation for selected attack
    st.markdown("### 🔬 Detailed Attack Simulation")
    selected = st.selectbox("Choose attack to simulate in detail:", list(ATTACKS.keys()))
    attack_data = ATTACKS[selected]
    prob = results[selected]

    col_desc, col_risk = st.columns([2, 1])

    with col_desc:
        st.markdown(f"**About this attack:**")
        st.markdown(f"_{attack_data['desc']}_")

        st.markdown("**Domains affecting this attack vector:**")
        for domain, weight in attack_data["domains"].items():
            sc  = domain_scores.get(domain, {}).get("score", 0)
            vuln = round(((5 - sc) / 5) * 100)
            clr  = "#ef4444" if vuln > 60 else "#f97316" if vuln > 40 else "#22c55e"
            st.markdown(f"""
            <div style="background:#1e293b;border-radius:8px;
                        padding:10px 14px;margin-bottom:6px">
                <div style="display:flex;justify-content:space-between">
                    <span style="color:#e2e8f0;font-weight:600">{domain}</span>
                    <span style="color:{clr};font-weight:700">{vuln}% vulnerable</span>
                </div>
                <div style="background:#0f172a;border-radius:4px;
                            height:6px;margin-top:6px;overflow:hidden">
                    <div style="width:{vuln}%;height:100%;background:{clr};
                                border-radius:4px"></div>
                </div>
                <span style="color:#64748b;font-size:0.8rem">
                    Current score: {sc:.1f}/5 | Weight in this attack: {int(weight*100)}%
                </span>
            </div>""", unsafe_allow_html=True)

    with col_risk:
        risk_label = ("CRITICAL" if prob >= 70 else "HIGH" if prob >= 50
                      else "MEDIUM" if prob >= 30 else "LOW")
        risk_color = {"CRITICAL":"#ef4444","HIGH":"#f97316",
                      "MEDIUM":"#eab308","LOW":"#22c55e"}[risk_label]

        st.markdown(f"""
        <div style="background:{risk_color}18;border:2px solid {risk_color};
                    border-radius:12px;padding:24px;text-align:center">
            <div style="font-size:2.5rem;font-weight:700;color:{risk_color}">{prob}%</div>
            <div style="color:{risk_color};font-weight:600;font-size:1.1rem">
                {risk_label} RISK
            </div>
            <div style="color:#64748b;font-size:0.85rem;margin-top:8px">
                Attack success probability
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if prob >= 70:
            st.error("⚠️ Your organisation is highly vulnerable to this attack. Immediate action required.")
        elif prob >= 50:
            st.warning("⚠️ Significant vulnerability. Prioritise mitigation within 30 days.")
        elif prob >= 30:
            st.info("ℹ️ Moderate risk. Include in your security roadmap.")
        else:
            st.success("✅ Good protection against this attack vector.")

    st.markdown("---")
    st.markdown("### 🛡️ Recommended Mitigations")
    for i, mit in enumerate(attack_data["mitigations"], 1):
        st.markdown(f"""
        <div style="background:#1e293b;border-left:3px solid #3b82f6;
                    border-radius:8px;padding:10px 14px;margin-bottom:6px">
            <span style="color:#60a5fa;font-weight:700">{i}.</span>
            <span style="color:#e2e8f0;margin-left:8px">{mit}</span>
        </div>""", unsafe_allow_html=True)