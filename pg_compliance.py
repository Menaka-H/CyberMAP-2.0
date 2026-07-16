# pg_compliance.py — Security Compliance Checker
import streamlit as st
from utils.database import get_all_assessments, get_assessment_by_id, get_questions
from utils.scoring import compute_domain_scores

# Compliance framework requirements mapped to NIST/ISO controls
FRAMEWORKS = {
    "🇮🇳 DPDP Act 2023": {
        "description": "India's Digital Personal Data Protection Act 2023",
        "requirements": [
            {"name": "Data Classification Policy",      "domain": "Identify", "min_score": 3, "ref": "ID.AM-05"},
            {"name": "Data Encryption at Rest",         "domain": "Protect",  "min_score": 3, "ref": "PR.DS-01"},
            {"name": "Data Encryption in Transit",      "domain": "Protect",  "min_score": 3, "ref": "PR.DS-02"},
            {"name": "Access Control & Least Privilege","domain": "Protect",  "min_score": 3, "ref": "PR.AA-05"},
            {"name": "Breach Notification Procedure",   "domain": "Respond",  "min_score": 3, "ref": "RS.CO-02"},
            {"name": "Data Retention Policy",           "domain": "Protect",  "min_score": 3, "ref": "PR.DS-03"},
            {"name": "Vendor/Processor Agreements",     "domain": "Govern",   "min_score": 3, "ref": "GV.SC-03"},
            {"name": "Incident Response Plan",          "domain": "Respond",  "min_score": 3, "ref": "RS.MA-01"},
        ],
    },
    "🇪🇺 GDPR": {
        "description": "EU General Data Protection Regulation",
        "requirements": [
            {"name": "Data Protection Policy",          "domain": "Govern",   "min_score": 3, "ref": "GV.PO-01"},
            {"name": "Data Classification",             "domain": "Identify", "min_score": 3, "ref": "ID.AM-05"},
            {"name": "Encryption at Rest & Transit",    "domain": "Protect",  "min_score": 4, "ref": "PR.DS-01"},
            {"name": "Access Control",                  "domain": "Protect",  "min_score": 3, "ref": "PR.AA-03"},
            {"name": "Breach Notification (72hr)",      "domain": "Respond",  "min_score": 4, "ref": "RS.CO-02"},
            {"name": "Data Retention Policy",           "domain": "Protect",  "min_score": 3, "ref": "PR.DS-03"},
            {"name": "Third-party Risk Management",     "domain": "Govern",   "min_score": 3, "ref": "GV.SC-01"},
            {"name": "Security Monitoring",             "domain": "Detect",   "min_score": 3, "ref": "DE.CM-01"},
            {"name": "DPA/Vendor Contracts",            "domain": "Govern",   "min_score": 3, "ref": "GV.SC-03"},
        ],
    },
    "💳 PCI-DSS v4.0": {
        "description": "Payment Card Industry Data Security Standard",
        "requirements": [
            {"name": "Network Segmentation & Firewall", "domain": "Protect",  "min_score": 4, "ref": "PR.PS-05"},
            {"name": "Strong Access Controls",          "domain": "Protect",  "min_score": 4, "ref": "PR.AA-03"},
            {"name": "Data Encryption",                 "domain": "Protect",  "min_score": 4, "ref": "PR.DS-01"},
            {"name": "Vulnerability Management",        "domain": "Identify", "min_score": 4, "ref": "ID.RA-01"},
            {"name": "Security Monitoring & Logging",   "domain": "Detect",   "min_score": 4, "ref": "DE.CM-03"},
            {"name": "Penetration Testing",             "domain": "Detect",   "min_score": 3, "ref": "DE.AE-06"},
            {"name": "Patch Management",                "domain": "Protect",  "min_score": 4, "ref": "PR.PS-02"},
            {"name": "Incident Response Plan",          "domain": "Respond",  "min_score": 4, "ref": "RS.MA-01"},
            {"name": "Physical Security Controls",      "domain": "Protect",  "min_score": 3, "ref": "PR.PS-05"},
            {"name": "Security Awareness Training",     "domain": "Govern",   "min_score": 3, "ref": "GV.AT-01"},
        ],
    },
    "🏥 HIPAA": {
        "description": "Health Insurance Portability and Accountability Act",
        "requirements": [
            {"name": "Access Control Policy",           "domain": "Protect",  "min_score": 4, "ref": "PR.AA-05"},
            {"name": "Audit Logging & Monitoring",      "domain": "Detect",   "min_score": 3, "ref": "DE.CM-03"},
            {"name": "Encryption of PHI",               "domain": "Protect",  "min_score": 4, "ref": "PR.DS-01"},
            {"name": "Risk Assessment",                 "domain": "Identify", "min_score": 3, "ref": "ID.RA-01"},
            {"name": "Incident Response",               "domain": "Respond",  "min_score": 3, "ref": "RS.MA-01"},
            {"name": "Backup & Recovery",               "domain": "Recover",  "min_score": 3, "ref": "RC.RP-01"},
            {"name": "Security Training",               "domain": "Govern",   "min_score": 3, "ref": "GV.AT-01"},
            {"name": "Business Associate Agreements",   "domain": "Govern",   "min_score": 3, "ref": "GV.SC-03"},
            {"name": "Workforce Security Policy",       "domain": "Govern",   "min_score": 3, "ref": "GV.PO-01"},
        ],
    },
    "🔒 ISO 27001:2022": {
        "description": "International Information Security Management Standard",
        "requirements": [
            {"name": "ISMS Policy",                     "domain": "Govern",   "min_score": 3, "ref": "GV.PO-01"},
            {"name": "Risk Assessment Process",         "domain": "Identify", "min_score": 3, "ref": "ID.RA-01"},
            {"name": "Asset Management",                "domain": "Identify", "min_score": 3, "ref": "ID.AM-01"},
            {"name": "Access Control",                  "domain": "Protect",  "min_score": 3, "ref": "PR.AA-05"},
            {"name": "Cryptography Controls",           "domain": "Protect",  "min_score": 3, "ref": "PR.DS-01"},
            {"name": "Incident Management",             "domain": "Respond",  "min_score": 3, "ref": "RS.MA-01"},
            {"name": "Business Continuity",             "domain": "Recover",  "min_score": 3, "ref": "RC.RP-01"},
            {"name": "Supplier Security",               "domain": "Govern",   "min_score": 3, "ref": "GV.SC-01"},
            {"name": "Security Monitoring",             "domain": "Detect",   "min_score": 3, "ref": "DE.CM-01"},
            {"name": "Awareness & Training",            "domain": "Govern",   "min_score": 3, "ref": "GV.AT-01"},
            {"name": "Vulnerability Management",        "domain": "Identify", "min_score": 3, "ref": "ID.RA-01"},
        ],
    },
}


def check_compliance(domain_scores, framework_reqs):
    results = []
    for req in framework_reqs:
        domain = req["domain"]
        score  = domain_scores.get(domain, {}).get("score", 0)
        passed = score >= req["min_score"]
        gap    = max(0, req["min_score"] - score)
        results.append({
            **req,
            "actual_score": round(score, 2),
            "passed":       passed,
            "gap":          round(gap, 2),
        })
    total    = len(results)
    passed   = sum(1 for r in results if r["passed"])
    pct      = round((passed / total) * 100) if total > 0 else 0
    status   = ("✅ Compliant" if pct >= 90 else
                "⚠️ Partially Compliant" if pct >= 60 else
                "❌ Non-Compliant")
    return results, passed, total, pct, status


def render():
    st.markdown("""
    <style>
    .comp-header {
        background:linear-gradient(135deg,#052e16,#0f172a);
        border-radius:14px; padding:24px 28px; margin-bottom:20px;
        border:1px solid #16a34a44;
    }
    .req-row {
        background:#1e293b; border-radius:8px;
        padding:10px 14px; margin-bottom:6px;
        display:flex; justify-content:space-between; align-items:center;
    }
    .framework-card {
        background:#1e293b; border:1px solid #334155;
        border-radius:12px; padding:16px; margin-bottom:10px;
        cursor:pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="comp-header">
        <h2 style="color:white;margin:0;">✅ Security Compliance Checker</h2>
        <p style="color:#86efac;margin:6px 0 0 0;">
            Check if your organisation meets DPDP, GDPR, PCI-DSS,
            HIPAA and ISO 27001 requirements based on assessment results.
        </p>
    </div>
    """, unsafe_allow_html=True)

    assessments = get_all_assessments()
    if not assessments:
        st.warning("No assessments found. Complete a New Assessment first.")
        return

    # Select assessment
    options = {
        f"ID {a['id']} — {a['org_name']} ({a['created_at'][:10]})": a["id"]
        for a in assessments
    }
    chosen = st.selectbox("Select assessment:", list(options.keys()))
    row = get_assessment_by_id(options[chosen])
    qs  = get_questions()
    domain_scores = compute_domain_scores(row["answers"], qs)

    st.markdown("---")

    # Overall compliance summary
    st.markdown("### 📊 Compliance Summary — All Frameworks")

    fw_cols = st.columns(len(FRAMEWORKS))
    for i, (fw_name, fw_data) in enumerate(FRAMEWORKS.items()):
        results, passed, total, pct, status = check_compliance(
            domain_scores, fw_data["requirements"]
        )
        color = "#22c55e" if pct >= 90 else "#f59e0b" if pct >= 60 else "#ef4444"
        with fw_cols[i]:
            st.markdown(f"""
            <div style="background:#1e293b; border:2px solid {color};
                        border-radius:12px; padding:16px; text-align:center;">
                <div style="font-size:1.5rem;">{fw_name[:2]}</div>
                <div style="color:#e2e8f0; font-size:0.8rem; font-weight:600;
                            margin:4px 0;">{fw_name[2:].strip()}</div>
                <div style="color:{color}; font-size:1.8rem;
                            font-weight:700;">{pct}%</div>
                <div style="color:{color}; font-size:0.75rem;">
                    {passed}/{total} passed
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Detailed check per framework
    st.markdown("### 🔍 Detailed Compliance Check")
    selected_fw = st.selectbox("Select framework to inspect:",
                                list(FRAMEWORKS.keys()))
    fw_data = FRAMEWORKS[selected_fw]
    results, passed, total, pct, status = check_compliance(
        domain_scores, fw_data["requirements"]
    )

    color = "#22c55e" if pct >= 90 else "#f59e0b" if pct >= 60 else "#ef4444"

    col_stat, col_info = st.columns([1, 3])
    with col_stat:
        st.markdown(f"""
        <div style="background:#1e293b; border:2px solid {color};
                    border-radius:14px; padding:24px; text-align:center;">
            <div style="font-size:2.5rem; font-weight:700;
                        color:{color};">{pct}%</div>
            <div style="color:{color}; font-weight:600;
                        margin:8px 0;">{status}</div>
            <div style="color:#64748b; font-size:0.85rem;">
                {passed} of {total} requirements met
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_info:
        st.markdown(f"**{selected_fw}** — {fw_data['description']}")
        st.progress(pct / 100)
        if pct >= 90:
            st.success("✅ Your organisation meets the requirements for this framework.")
        elif pct >= 60:
            st.warning("⚠️ Partial compliance. Address failing requirements to achieve full compliance.")
        else:
            st.error("❌ Significant gaps exist. Immediate remediation required.")

    st.markdown("---")

    # Requirement details
    st.markdown("**Requirement Checklist:**")
    for req in results:
        icon  = "✅" if req["passed"] else "❌"
        color = "#22c55e" if req["passed"] else "#ef4444"
        gap_text = f" (gap: +{req['gap']:.1f} needed)" if not req["passed"] else ""

        st.markdown(f"""
        <div class="req-row">
            <div>
                <span style="font-size:1.1rem;">{icon}</span>
                <span style="color:#e2e8f0; margin-left:8px;
                             font-weight:500;">{req['name']}</span>
                <span style="color:#64748b; font-size:0.8rem; margin-left:8px;">
                    {req['domain']} · {req['ref']}
                </span>
            </div>
            <div style="text-align:right;">
                <span style="color:{color}; font-weight:700;">
                    {req['actual_score']:.1f}/{req['min_score']:.0f}
                </span>
                <span style="color:#64748b; font-size:0.78rem;">
                    {gap_text}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)