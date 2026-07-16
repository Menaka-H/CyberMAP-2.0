# pg_security_builder.py — Complete Security Program Builder
# Helps any company build cybersecurity from scratch
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.database import get_all_assessments, get_assessment_by_id, get_questions
from utils.scoring import compute_domain_scores, get_maturity_label
from utils.questions_data import DOMAINS

# ── DATA ──────────────────────────────────────────────────────────────────────

INDUSTRIES = [
    "Technology", "Finance & Banking", "Healthcare",
    "Manufacturing", "Retail & E-commerce", "Government",
    "Education", "Logistics", "Energy & Utilities", "Other"
]

COMPANY_STAGES = {
    "🔴 No security at all (starting from zero)": {
        "level": 0, "score_range": "0.0 – 1.0",
        "desc": "No formal security controls exist."
    },
    "🟠 Basic security only (antivirus, firewall)": {
        "level": 1, "score_range": "1.0 – 2.0",
        "desc": "Minimal reactive controls in place."
    },
    "🟡 Some security but no formal program": {
        "level": 2, "score_range": "2.0 – 3.0",
        "desc": "Partial controls, no governance."
    },
    "🟢 Security tools but no governance/policies": {
        "level": 3, "score_range": "3.0 – 4.0",
        "desc": "Tools deployed but not managed."
    },
}

SECURITY_PROGRAM_STEPS = {
    0: [
        {
            "phase": "Week 1–2",
            "title": "Appoint Security Leadership",
            "actions": [
                "Designate a CISO or Security Officer",
                "Form a security steering committee",
                "Get executive sponsorship and budget approval",
                "Define cybersecurity objectives aligned to business goals",
            ],
            "nist": "GV.RR-01", "iso": "ISO 5.2",
            "priority": "Critical",
        },
        {
            "phase": "Week 2–4",
            "title": "Asset Discovery",
            "actions": [
                "Run network scan to discover all devices (use Nmap)",
                "Create hardware asset inventory spreadsheet",
                "List all software applications in use",
                "Identify and classify all sensitive data",
            ],
            "nist": "ID.AM-01", "iso": "ISO 8.1",
            "priority": "Critical",
        },
        {
            "phase": "Month 1",
            "title": "Basic Access Controls",
            "actions": [
                "Create unique accounts for every user — no sharing",
                "Enable MFA on all admin accounts immediately",
                "Remove all default passwords on every device",
                "Create an offboarding checklist to revoke access",
            ],
            "nist": "PR.AA-03", "iso": "ISO 8.5",
            "priority": "Critical",
        },
        {
            "phase": "Month 1–2",
            "title": "Endpoint Protection",
            "actions": [
                "Deploy EDR/antivirus on all endpoints",
                "Enable automatic OS and software updates",
                "Enable full-disk encryption on all laptops",
                "Set up centralised endpoint management console",
            ],
            "nist": "PR.PS-04", "iso": "ISO 8.7",
            "priority": "Critical",
        },
        {
            "phase": "Month 2",
            "title": "Data Backup",
            "actions": [
                "Identify all critical data that must be backed up",
                "Set up automated daily backups",
                "Store one backup copy offsite or in cloud",
                "Test restoration from backup immediately",
            ],
            "nist": "PR.DS-11", "iso": "ISO 8.13",
            "priority": "Critical",
        },
        {
            "phase": "Month 2–3",
            "title": "Write Core Policies",
            "actions": [
                "Draft Acceptable Use Policy",
                "Draft Password Policy (min 12 chars, MFA required)",
                "Draft Data Classification Policy",
                "Get policies approved and signed by leadership",
            ],
            "nist": "GV.PO-01", "iso": "ISO 5.1",
            "priority": "High",
        },
    ],
    1: [
        {
            "phase": "Month 1",
            "title": "Formalise Governance",
            "actions": [
                "Document and approve cybersecurity policy",
                "Assign security roles and responsibilities",
                "Establish security risk tolerance with leadership",
                "Schedule quarterly security review meetings",
            ],
            "nist": "GV.PO-01", "iso": "ISO 5.1",
            "priority": "Critical",
        },
        {
            "phase": "Month 1–2",
            "title": "Enable MFA Everywhere",
            "actions": [
                "Enable MFA on all email accounts",
                "Enable MFA on VPN and remote access",
                "Enable MFA on cloud services (AWS, Azure, GCP)",
                "Enforce MFA for all SaaS applications",
            ],
            "nist": "PR.AA-03", "iso": "ISO 8.5",
            "priority": "Critical",
        },
        {
            "phase": "Month 2",
            "title": "Patch Management",
            "actions": [
                "Audit all systems for missing patches",
                "Apply all critical patches within 7 days",
                "Set up automated patching where possible",
                "Define 30-day SLA for all security patches",
            ],
            "nist": "PR.PS-02", "iso": "ISO 8.8",
            "priority": "High",
        },
        {
            "phase": "Month 2–3",
            "title": "Network Segmentation",
            "actions": [
                "Separate production from development networks",
                "Isolate IoT devices on separate VLAN",
                "Configure firewall rules between segments",
                "Restrict lateral movement between zones",
            ],
            "nist": "PR.PS-05", "iso": "ISO 8.22",
            "priority": "High",
        },
        {
            "phase": "Month 3",
            "title": "Security Awareness Training",
            "actions": [
                "Run mandatory security awareness training for all staff",
                "Conduct first phishing simulation exercise",
                "Create security awareness newsletter",
                "Train IT staff on incident response basics",
            ],
            "nist": "GV.AT-01", "iso": "ISO 6.3",
            "priority": "High",
        },
        {
            "phase": "Month 3–4",
            "title": "Basic Monitoring",
            "actions": [
                "Enable logging on all critical systems",
                "Set up centralised log collection (Wazuh/Splunk)",
                "Configure alerts for failed logins and privilege escalation",
                "Assign someone to review alerts daily",
            ],
            "nist": "DE.CM-01", "iso": "ISO 8.16",
            "priority": "High",
        },
    ],
    2: [
        {
            "phase": "Month 1",
            "title": "Formal Risk Assessment",
            "actions": [
                "Conduct full risk assessment using ISO 27005",
                "Create and maintain a risk register",
                "Assign risk owners and treatment plans",
                "Present risk register to leadership quarterly",
            ],
            "nist": "ID.RA-01", "iso": "ISO 8.2",
            "priority": "Critical",
        },
        {
            "phase": "Month 1–2",
            "title": "Incident Response Plan",
            "actions": [
                "Write formal Incident Response Plan (IRP)",
                "Define incident severity levels and escalation paths",
                "Assign incident response team roles",
                "Run first tabletop exercise to test the plan",
            ],
            "nist": "RS.MA-01", "iso": "ISO 5.26",
            "priority": "Critical",
        },
        {
            "phase": "Month 2",
            "title": "Vulnerability Management",
            "actions": [
                "Deploy vulnerability scanning tool (Nessus/Qualys)",
                "Run baseline scan across all systems",
                "Prioritise and remediate critical findings",
                "Schedule quarterly scans going forward",
            ],
            "nist": "ID.RA-01", "iso": "ISO 8.8",
            "priority": "High",
        },
        {
            "phase": "Month 2–3",
            "title": "Third-Party Risk Management",
            "actions": [
                "List all vendors with access to your systems/data",
                "Send security questionnaires to critical vendors",
                "Add security clauses to all new vendor contracts",
                "Create vendor offboarding process",
            ],
            "nist": "GV.SC-01", "iso": "ISO 5.19",
            "priority": "High",
        },
        {
            "phase": "Month 3",
            "title": "Business Continuity",
            "actions": [
                "Define Recovery Time Objectives for critical systems",
                "Write Business Continuity Plan (BCP)",
                "Test backup restoration for all critical systems",
                "Document recovery procedures step by step",
            ],
            "nist": "RC.RP-01", "iso": "ISO 5.30",
            "priority": "High",
        },
    ],
    3: [
        {
            "phase": "Month 1",
            "title": "SIEM & SOC Setup",
            "actions": [
                "Deploy or upgrade SIEM solution",
                "Define detection use cases and alert rules",
                "Establish SOC workflows and escalation procedures",
                "Set up 24/7 monitoring coverage",
            ],
            "nist": "DE.CM-03", "iso": "ISO 8.15",
            "priority": "Critical",
        },
        {
            "phase": "Month 1–2",
            "title": "Zero Trust Architecture",
            "actions": [
                "Implement identity-based access controls",
                "Deploy privileged access management (PAM)",
                "Enable conditional access policies",
                "Micro-segment the network further",
            ],
            "nist": "PR.AA-05", "iso": "ISO 8.2",
            "priority": "Critical",
        },
        {
            "phase": "Month 2",
            "title": "Annual Penetration Testing",
            "actions": [
                "Engage qualified penetration testing firm",
                "Test external perimeter and web applications",
                "Test internal network and Active Directory",
                "Remediate all critical and high findings",
            ],
            "nist": "DE.AE-06", "iso": "ISO 8.8",
            "priority": "High",
        },
        {
            "phase": "Month 2–3",
            "title": "Security Metrics & Reporting",
            "actions": [
                "Define 10 key cybersecurity KPIs",
                "Build security dashboard for leadership",
                "Report maturity scores monthly to CISO",
                "Benchmark against industry peers annually",
            ],
            "nist": "GV.OV-02", "iso": "ISO 9.1",
            "priority": "High",
        },
    ],
}

TOOL_RECOMMENDATIONS = {
    "Identity & Access": [
        {"name": "Microsoft Entra ID", "type": "IAM/MFA",
         "cost": "₹₹", "tier": "Enterprise",
         "desc": "Identity platform with MFA, SSO and conditional access"},
        {"name": "CyberArk",           "type": "PAM",
         "cost": "₹₹₹", "tier": "Enterprise",
         "desc": "Privileged access management for admin accounts"},
        {"name": "Okta",               "type": "SSO/MFA",
         "cost": "₹₹", "tier": "Mid/Enterprise",
         "desc": "Cloud-based identity and SSO platform"},
    ],
    "Endpoint Security": [
        {"name": "CrowdStrike Falcon",  "type": "EDR",
         "cost": "₹₹₹", "tier": "Enterprise",
         "desc": "AI-powered endpoint detection and response"},
        {"name": "SentinelOne",         "type": "EDR",
         "cost": "₹₹₹", "tier": "Enterprise",
         "desc": "Autonomous EDR with behavioural AI"},
        {"name": "Microsoft Defender",  "type": "EDR",
         "cost": "₹₹", "tier": "All sizes",
         "desc": "Built-in EDR for Windows environments"},
    ],
    "Network Security": [
        {"name": "Palo Alto NGFW",      "type": "Firewall",
         "cost": "₹₹₹", "tier": "Enterprise",
         "desc": "Next-gen firewall with app-layer inspection"},
        {"name": "Cisco Umbrella",      "type": "DNS Security",
         "cost": "₹₹", "tier": "Enterprise",
         "desc": "Cloud-delivered DNS security and web filtering"},
        {"name": "Zscaler",             "type": "ZTNA",
         "cost": "₹₹₹", "tier": "Enterprise",
         "desc": "Zero trust network access platform"},
    ],
    "SIEM & Monitoring": [
        {"name": "Splunk",              "type": "SIEM",
         "cost": "₹₹₹", "tier": "Enterprise",
         "desc": "Industry-leading SIEM with advanced analytics"},
        {"name": "Microsoft Sentinel",  "type": "SIEM",
         "cost": "₹₹", "tier": "Enterprise",
         "desc": "Cloud-native SIEM with AI-driven detection"},
        {"name": "Wazuh",               "type": "SIEM (Open Source)",
         "cost": "Free", "tier": "All sizes",
         "desc": "Open-source SIEM, XDR and SOAR platform"},
    ],
    "Vulnerability Management": [
        {"name": "Tenable Nessus",      "type": "Vuln Scanner",
         "cost": "₹₹", "tier": "Enterprise",
         "desc": "Industry standard vulnerability assessment tool"},
        {"name": "Qualys VMDR",         "type": "Vuln Management",
         "cost": "₹₹₹", "tier": "Enterprise",
         "desc": "Cloud-based vulnerability management platform"},
        {"name": "OpenVAS",             "type": "Vuln Scanner (Free)",
         "cost": "Free", "tier": "All sizes",
         "desc": "Open-source vulnerability scanning solution"},
    ],
    "Data Security": [
        {"name": "Varonis",             "type": "DLP/DSPM",
         "cost": "₹₹₹", "tier": "Enterprise",
         "desc": "Data security and insider threat protection"},
        {"name": "Microsoft Purview",   "type": "DLP",
         "cost": "₹₹", "tier": "Enterprise",
         "desc": "Data classification and loss prevention"},
        {"name": "Symantec DLP",        "type": "DLP",
         "cost": "₹₹₹", "tier": "Enterprise",
         "desc": "Enterprise data loss prevention platform"},
    ],
}

BUDGET_ESTIMATES = {
    "500–1000 employees": {
        "Identity & Access":        {"min": 800000,  "max": 2000000},
        "Endpoint Security":        {"min": 1500000, "max": 3500000},
        "Network Security":         {"min": 1200000, "max": 3000000},
        "SIEM & Monitoring":        {"min": 1000000, "max": 2500000},
        "Vulnerability Management": {"min": 500000,  "max": 1200000},
        "Data Security":            {"min": 800000,  "max": 2000000},
        "Training & Awareness":     {"min": 300000,  "max": 800000},
        "Compliance & Audit":       {"min": 500000,  "max": 1500000},
        "Incident Response Retainer":{"min": 400000, "max": 1000000},
        "Penetration Testing":      {"min": 300000,  "max": 800000},
    },
    "1000–5000 employees": {
        "Identity & Access":        {"min": 2000000,  "max": 5000000},
        "Endpoint Security":        {"min": 3500000,  "max": 8000000},
        "Network Security":         {"min": 3000000,  "max": 7000000},
        "SIEM & Monitoring":        {"min": 2500000,  "max": 6000000},
        "Vulnerability Management": {"min": 1200000,  "max": 3000000},
        "Data Security":            {"min": 2000000,  "max": 5000000},
        "Training & Awareness":     {"min": 800000,   "max": 2000000},
        "Compliance & Audit":       {"min": 1500000,  "max": 4000000},
        "Incident Response Retainer":{"min": 1000000, "max": 3000000},
        "Penetration Testing":      {"min": 800000,   "max": 2000000},
    },
    "5000+ employees": {
        "Identity & Access":        {"min": 5000000,  "max": 15000000},
        "Endpoint Security":        {"min": 8000000,  "max": 20000000},
        "Network Security":         {"min": 7000000,  "max": 18000000},
        "SIEM & Monitoring":        {"min": 6000000,  "max": 15000000},
        "Vulnerability Management": {"min": 3000000,  "max": 8000000},
        "Data Security":            {"min": 5000000,  "max": 12000000},
        "Training & Awareness":     {"min": 2000000,  "max": 5000000},
        "Compliance & Audit":       {"min": 4000000,  "max": 10000000},
        "Incident Response Retainer":{"min": 3000000, "max": 8000000},
        "Penetration Testing":      {"min": 2000000,  "max": 5000000},
    },
}

POLICY_TEMPLATES = {
    "Information Security Policy": """
INFORMATION SECURITY POLICY
{company_name} | Version 1.0 | {date}

1. PURPOSE
This policy establishes {company_name}'s commitment to protecting
information assets against unauthorized access, disclosure, modification,
destruction or interference.

2. SCOPE
This policy applies to all employees, contractors, consultants, vendors
and any other persons with access to {company_name}'s information systems.

3. POLICY STATEMENTS
3.1 All information assets must be classified as Public, Internal,
    Confidential or Restricted.
3.2 Access to information must follow the principle of least privilege.
3.3 All users must complete annual security awareness training.
3.4 Security incidents must be reported within 1 hour of discovery.
3.5 All systems must be patched within 30 days of critical patch release.

4. COMPLIANCE
Violations of this policy may result in disciplinary action up to and
including termination and legal prosecution.

5. REVIEW
This policy will be reviewed annually and updated as required.

Approved by: ___________________ Date: ___________
""",
    "Acceptable Use Policy": """
ACCEPTABLE USE POLICY
{company_name} | Version 1.0 | {date}

1. PURPOSE
To define the acceptable use of {company_name}'s information technology
resources to protect employees, the company and its partners.

2. ACCEPTABLE USE
2.1 IT resources are provided for business purposes.
2.2 Incidental personal use is permitted if it does not interfere with work.
2.3 Users must not share credentials or allow others to use their accounts.
2.4 All data created on company systems remains company property.

3. PROHIBITED ACTIVITIES
Users must NOT:
- Access, download or distribute illegal content
- Attempt to bypass or disable security controls
- Install unauthorised software without IT approval
- Share confidential information outside approved channels
- Use company resources for personal financial gain

4. MONITORING
{company_name} reserves the right to monitor all activity on its systems.
Users have no expectation of privacy on company-owned devices.

5. VIOLATIONS
Violations will be reported to management and may result in disciplinary
action including termination.

Approved by: ___________________ Date: ___________
""",
    "Password Policy": """
PASSWORD POLICY
{company_name} | Version 1.0 | {date}

1. PURPOSE
To ensure strong authentication controls protect {company_name}'s systems
and data from unauthorized access.

2. PASSWORD REQUIREMENTS
2.1 Minimum length: 12 characters
2.2 Must contain: uppercase, lowercase, number and special character
2.3 Must not contain: username, company name or dictionary words
2.4 Must not reuse last 10 passwords
2.5 Maximum password age: 90 days for standard accounts

3. MULTI-FACTOR AUTHENTICATION
MFA is mandatory for:
- All administrator accounts
- Remote access and VPN
- Email and collaboration tools
- Cloud service consoles
- Financial and HR systems

4. PRIVILEGED ACCOUNTS
4.1 Admin passwords must be minimum 16 characters
4.2 Privileged sessions must be recorded via PAM solution
4.3 Admin accounts must not be used for daily tasks

5. PASSWORD STORAGE
Passwords must never be written down, stored in plain text or
sent via email. Use the approved password manager.

Approved by: ___________________ Date: ___________
""",
    "Incident Response Policy": """
INCIDENT RESPONSE POLICY
{company_name} | Version 1.0 | {date}

1. PURPOSE
To ensure {company_name} responds to cybersecurity incidents in a timely,
consistent and effective manner to minimise business impact.

2. INCIDENT CLASSIFICATION
Severity 1 (Critical): Active breach, ransomware, data exfiltration
  → Response time: 15 minutes | Escalate to CISO immediately
Severity 2 (High): Malware infection, account compromise
  → Response time: 1 hour | Escalate to Security Team
Severity 3 (Medium): Policy violation, phishing attempt
  → Response time: 4 hours | Handle within Security Team
Severity 4 (Low): Suspicious activity, minor policy breach
  → Response time: 24 hours | Log and monitor

3. RESPONSE PHASES
Phase 1 — Preparation: Maintain IRP, train team, test quarterly
Phase 2 — Detection: Monitor alerts, identify indicators of compromise
Phase 3 — Containment: Isolate affected systems within 1 hour
Phase 4 — Eradication: Remove malware, patch vulnerabilities
Phase 5 — Recovery: Restore from clean backups, verify integrity
Phase 6 — Lessons Learned: RCA within 2 weeks, update controls

4. REPORTING OBLIGATIONS
- Internal: Notify CISO within 1 hour of Sev 1/2 incidents
- Regulatory: Notify regulator within 72 hours if personal data affected
- Customers: Notify affected customers per contractual obligations

Approved by: ___________________ Date: ___________
""",
}

MATURITY_ROADMAP = {
    "6 Months": {
        "goal": "Achieve Initial → Developing (Score 1.0 → 2.5)",
        "color": "#ef4444",
        "milestones": [
            "Month 1: Appoint CISO, complete asset inventory",
            "Month 2: Enable MFA, deploy EDR, set up backups",
            "Month 3: Write and approve core security policies",
            "Month 4: Deploy firewall, enable basic logging",
            "Month 5: Conduct first security awareness training",
            "Month 6: Complete first formal risk assessment",
        ],
    },
    "1 Year": {
        "goal": "Achieve Developing → Defined (Score 2.5 → 3.5)",
        "color": "#f59e0b",
        "milestones": [
            "Q1: Establish governance, policies and risk management",
            "Q2: Deploy SIEM, formalise incident response",
            "Q3: Vendor risk management, vulnerability scanning",
            "Q4: First penetration test, compliance assessment",
        ],
    },
    "3 Years": {
        "goal": "Achieve Defined → Managed (Score 3.5 → 4.5)",
        "color": "#22c55e",
        "milestones": [
            "Year 1: Governance, controls and basic monitoring",
            "Year 2: Advanced detection, SOC, zero trust architecture",
            "Year 3: Continuous improvement, AI-driven security, certification",
        ],
    },
}


# ── RENDER FUNCTION ───────────────────────────────────────────────────────────

def render():
    st.markdown("""
    <style>
    .builder-hero {
        background: linear-gradient(135deg,#0f172a,#1e3a5f,#1e1b4b);
        border-radius:16px; padding:28px 32px; margin-bottom:24px;
        border:1px solid #6366f144;
    }
    .step-card {
        background:#1e293b; border:1px solid #334155;
        border-radius:12px; padding:18px; margin-bottom:12px;
    }
    .tool-card {
        background:#1e293b; border:1px solid #334155;
        border-radius:10px; padding:14px; margin-bottom:8px;
        display:flex; justify-content:space-between; align-items:flex-start;
    }
    .budget-bar {
        background:#0f172a; border-radius:6px; height:10px;
        overflow:hidden; margin:6px 0;
    }
    .sec-title {
        font-size:0.95rem; font-weight:600; color:#e2e8f0;
        border-left:4px solid #6366f1; padding-left:12px;
        margin:24px 0 14px 0;
    }
    .milestone {
        background:#0f172a; border-left:3px solid #6366f1;
        border-radius:6px; padding:10px 14px; margin-bottom:6px;
        color:#94a3b8; font-size:0.88rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── HERO ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="builder-hero">
        <h2 style="color:white;margin:0;font-size:1.8rem;">
            🏗️ Security Program Builder
        </h2>
        <p style="color:#a5b4fc;margin:8px 0 0 0;font-size:1rem;">
            Complete toolkit for building enterprise cybersecurity from scratch.
            Step-by-step guidance, policy templates, tool recommendations,
            budget estimates and a 3-year maturity roadmap.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── COMPANY PROFILE ───────────────────────────────────────────────────
    st.markdown('<div class="sec-title">🏢 Company Profile</div>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    company_name = col1.text_input("Company Name",
                                    placeholder="e.g. Acme Enterprises")
    industry     = col2.selectbox("Industry", INDUSTRIES)
    emp_size     = col3.selectbox("Employee Count",
                                   ["500–1000 employees",
                                    "1000–5000 employees",
                                    "5000+ employees"])

    col4, col5 = st.columns(2)
    current_stage = col4.selectbox("Current Security Stage",
                                    list(COMPANY_STAGES.keys()))
    target_stage  = col5.selectbox("Target Maturity Level", [
        "🟡 Developing (Score 2.0–2.5) — 6 months",
        "🟢 Defined    (Score 3.0–3.5) — 1 year",
        "🔵 Managed    (Score 4.0–4.5) — 2–3 years",
    ])

    stage_level = COMPANY_STAGES[current_stage]["level"]
    st.markdown("---")

    # ── TABS ──────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Step-by-Step Guide",
        "🛠️ Tool Recommendations",
        "💰 Budget Estimator",
        "📄 Policy Templates",
        "🗓️ Maturity Roadmap",
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — STEP BY STEP GUIDE
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown(f"""
        <div style="background:#1e293b;border:1px solid #334155;
                    border-radius:10px;padding:16px;margin-bottom:20px;">
            <div style="color:#a5b4fc;font-size:0.85rem;
                        text-transform:uppercase;letter-spacing:1px;">
                Current Stage
            </div>
            <div style="color:#e2e8f0;font-size:1.1rem;font-weight:600;
                        margin:4px 0;">
                {current_stage}
            </div>
            <div style="color:#64748b;font-size:0.85rem;">
                {COMPANY_STAGES[current_stage]['desc']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        steps = SECURITY_PROGRAM_STEPS.get(stage_level, [])

        priority_colors = {
            "Critical": "#ef4444",
            "High":     "#f97316",
            "Medium":   "#eab308",
        }

        for i, step in enumerate(steps, 1):
            color = priority_colors.get(step["priority"], "#60a5fa")
            with st.expander(
                f"Step {i} — {step['title']} ({step['phase']})",
                expanded=(i == 1)
            ):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"""
                    <div style="margin-bottom:12px;">
                        <span style="background:{color}22;color:{color};
                                     border-radius:6px;padding:3px 10px;
                                     font-size:0.78rem;font-weight:700;">
                            {step['priority']}
                        </span>
                        <span style="background:#1e293b;color:#60a5fa;
                                     border-radius:6px;padding:3px 10px;
                                     font-size:0.78rem;margin-left:6px;">
                            NIST: {step['nist']}
                        </span>
                        <span style="background:#1e293b;color:#34d399;
                                     border-radius:6px;padding:3px 10px;
                                     font-size:0.78rem;margin-left:6px;">
                            {step['iso']}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                    for action in step["actions"]:
                        st.markdown(f"""
                        <div style="background:#0f172a;border-left:3px solid {color};
                                    border-radius:6px;padding:10px 14px;
                                    margin-bottom:6px;color:#e2e8f0;
                                    font-size:0.9rem;">
                            ▸ {action}
                        </div>
                        """, unsafe_allow_html=True)

                with col_b:
                    st.markdown(f"""
                    <div style="background:{color}11;border:1px solid {color};
                                border-radius:10px;padding:14px;text-align:center;
                                margin-top:20px;">
                        <div style="color:{color};font-size:0.8rem;
                                    font-weight:700;">TIMELINE</div>
                        <div style="color:#e2e8f0;font-size:0.9rem;
                                    margin-top:6px;">{step['phase']}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — TOOL RECOMMENDATIONS
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown(f"""
        <div style="background:#1e293b;border-radius:10px;padding:14px 18px;
                    margin-bottom:16px;">
            <p style="color:#94a3b8;margin:0;font-size:0.9rem;">
                Recommended enterprise security tools for
                <strong style="color:#e2e8f0;">{industry}</strong> organisations
                with <strong style="color:#e2e8f0;">{emp_size}</strong>.
                Sorted by category and priority.
            </p>
        </div>
        """, unsafe_allow_html=True)

        for category, tools in TOOL_RECOMMENDATIONS.items():
            st.markdown(f'<div class="sec-title">🔧 {category}</div>',
                        unsafe_allow_html=True)

            for tool in tools:
                cost_color = ("#22c55e" if tool["cost"] == "Free"
                              else "#f59e0b" if tool["cost"] == "₹₹"
                              else "#ef4444")
                st.markdown(f"""
                <div class="tool-card">
                    <div style="flex:1;">
                        <div style="display:flex;align-items:center;gap:10px;
                                    margin-bottom:4px;">
                            <span style="color:#e2e8f0;font-weight:700;
                                         font-size:1rem;">{tool['name']}</span>
                            <span style="background:#1e3a5f;color:#93c5fd;
                                         border-radius:12px;padding:2px 10px;
                                         font-size:0.75rem;">{tool['type']}</span>
                            <span style="background:#0f172a;color:#64748b;
                                         border-radius:12px;padding:2px 10px;
                                         font-size:0.75rem;">{tool['tier']}</span>
                        </div>
                        <div style="color:#64748b;font-size:0.85rem;">
                            {tool['desc']}
                        </div>
                    </div>
                    <div style="text-align:right;min-width:70px;
                                padding-left:16px;">
                        <div style="color:{cost_color};font-weight:700;
                                    font-size:1.1rem;">{tool['cost']}</div>
                        <div style="color:#64748b;font-size:0.72rem;">
                            per year
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — BUDGET ESTIMATOR
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown(f"""
        <div style="background:#1e293b;border-radius:10px;padding:14px 18px;
                    margin-bottom:20px;">
            <p style="color:#94a3b8;margin:0;font-size:0.9rem;">
                Annual cybersecurity budget estimate for
                <strong style="color:#e2e8f0;">
                    {company_name or 'your organisation'}
                </strong>
                ({emp_size}). All figures in Indian Rupees (₹).
            </p>
        </div>
        """, unsafe_allow_html=True)

        budget = BUDGET_ESTIMATES.get(emp_size, {})
        total_min = sum(v["min"] for v in budget.values())
        total_max = sum(v["max"] for v in budget.values())

        # Total budget card
        col_t1, col_t2, col_t3 = st.columns(3)
        col_t1.markdown(f"""
        <div style="background:#1e293b;border:1px solid #334155;
                    border-radius:12px;padding:18px;text-align:center;">
            <div style="color:#60a5fa;font-size:0.75rem;text-transform:uppercase;
                        letter-spacing:1px;">Minimum Budget</div>
            <div style="color:#60a5fa;font-size:1.6rem;font-weight:700;
                        margin-top:6px;">
                ₹{total_min/100000:.1f}L
            </div>
            <div style="color:#64748b;font-size:0.8rem;">per year</div>
        </div>""", unsafe_allow_html=True)

        col_t2.markdown(f"""
        <div style="background:#1e293b;border:1px solid #6366f1;
                    border-radius:12px;padding:18px;text-align:center;">
            <div style="color:#a5b4fc;font-size:0.75rem;text-transform:uppercase;
                        letter-spacing:1px;">Recommended Budget</div>
            <div style="color:#a5b4fc;font-size:1.6rem;font-weight:700;
                        margin-top:6px;">
                ₹{((total_min+total_max)/2)/100000:.1f}L
            </div>
            <div style="color:#64748b;font-size:0.8rem;">per year</div>
        </div>""", unsafe_allow_html=True)

        col_t3.markdown(f"""
        <div style="background:#1e293b;border:1px solid #334155;
                    border-radius:12px;padding:18px;text-align:center;">
            <div style="color:#34d399;font-size:0.75rem;text-transform:uppercase;
                        letter-spacing:1px;">Maximum Budget</div>
            <div style="color:#34d399;font-size:1.6rem;font-weight:700;
                        margin-top:6px;">
                ₹{total_max/100000:.1f}L
            </div>
            <div style="color:#64748b;font-size:0.8rem;">per year</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Budget Breakdown by Category:**")

        max_val = max(v["max"] for v in budget.values())
        for category, vals in budget.items():
            mid = (vals["min"] + vals["max"]) / 2
            pct = int((vals["max"] / max_val) * 100)
            st.markdown(f"""
            <div style="background:#1e293b;border-radius:8px;
                        padding:12px 16px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;
                            margin-bottom:6px;">
                    <span style="color:#e2e8f0;font-weight:500;
                                 font-size:0.9rem;">{category}</span>
                    <span style="color:#a5b4fc;font-weight:600;font-size:0.9rem;">
                        ₹{vals['min']//100000}L – ₹{vals['max']//100000}L
                    </span>
                </div>
                <div class="budget-bar">
                    <div style="width:{pct}%;height:100%;
                                background:linear-gradient(90deg,#6366f1,#8b5cf6);
                                border-radius:6px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Budget donut chart
        st.markdown("---")
        st.markdown("**Budget Allocation Chart:**")
        categories = list(budget.keys())
        mid_vals   = [(v["min"]+v["max"])/2 for v in budget.values()]
        colors_pie = ["#6366f1","#3b82f6","#06b6d4","#10b981",
                      "#f59e0b","#ef4444","#8b5cf6","#ec4899",
                      "#14b8a6","#f97316"]

        fig = go.Figure(go.Pie(
            labels=categories, values=mid_vals,
            hole=0.5,
            marker=dict(colors=colors_pie[:len(categories)],
                        line=dict(color="#0f172a", width=2)),
            textinfo="label+percent",
            textfont=dict(color="#e2e8f0", size=11),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            showlegend=False,
            height=360,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — POLICY TEMPLATES
    # ════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("""
        <div style="background:#1e293b;border-radius:10px;padding:14px 18px;
                    margin-bottom:16px;">
            <p style="color:#94a3b8;margin:0;font-size:0.9rem;">
                Auto-generated cybersecurity policy templates customised
                with your company name. Copy, edit and get approved by
                your legal and leadership teams.
            </p>
        </div>
        """, unsafe_allow_html=True)

        from datetime import datetime
        today = datetime.now().strftime("%d %B %Y")
        cname = company_name.strip() if company_name.strip() else "Your Organisation"

        selected_policy = st.selectbox(
            "Select policy template:",
            list(POLICY_TEMPLATES.keys())
        )

        policy_text = POLICY_TEMPLATES[selected_policy].format(
            company_name=cname,
            date=today,
        )

        st.markdown(f"""
        <div style="background:#0f172a;border:1px solid #334155;
                    border-radius:10px;padding:20px;font-family:monospace;
                    font-size:0.82rem;color:#e2e8f0;white-space:pre-wrap;
                    line-height:1.6;max-height:500px;overflow-y:auto;">
{policy_text}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label=f"⬇️ Download {selected_policy}",
            data=policy_text,
            file_name=f"{cname.replace(' ','_')}_{selected_policy.replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

        st.info("💡 These templates are starting points. Have your legal and "
                "compliance team review before official approval.")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 5 — MATURITY ROADMAP
    # ════════════════════════════════════════════════════════════════════════
    with tab5:
        st.markdown(f"""
        <div style="background:#1e293b;border-radius:10px;padding:14px 18px;
                    margin-bottom:20px;">
            <p style="color:#94a3b8;margin:0;font-size:0.9rem;">
                3-year cybersecurity maturity improvement roadmap for
                <strong style="color:#e2e8f0;">
                    {company_name or 'your organisation'}
                </strong>.
                Starting from: <strong style="color:#e2e8f0;">
                    {current_stage[:30]}
                </strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Timeline visual
        tl_cols = st.columns(3)
        for i, (period, data) in enumerate(MATURITY_ROADMAP.items()):
            with tl_cols[i]:
                st.markdown(f"""
                <div style="background:#1e293b;border:2px solid {data['color']};
                            border-radius:14px;padding:20px;text-align:center;
                            margin-bottom:16px;">
                    <div style="font-size:1.4rem;font-weight:700;
                                color:{data['color']};">{period}</div>
                    <div style="color:#94a3b8;font-size:0.8rem;
                                margin:8px 0;">{data['goal']}</div>
                </div>
                """, unsafe_allow_html=True)

                for milestone in data["milestones"]:
                    st.markdown(f"""
                    <div style="background:#0f172a;
                                border-left:3px solid {data['color']};
                                border-radius:6px;padding:8px 12px;
                                margin-bottom:6px;color:#94a3b8;
                                font-size:0.82rem;">{milestone}</div>
                    """, unsafe_allow_html=True)

        st.markdown("---")

        # Maturity progression chart
        st.markdown("**Expected Maturity Score Progression:**")
        periods    = ["Now", "6 Months", "1 Year", "2 Years", "3 Years"]
        base_score = stage_level * 0.8
        expected   = [
            round(base_score, 1),
            round(min(base_score + 1.0, 2.5), 1),
            round(min(base_score + 1.8, 3.5), 1),
            round(min(base_score + 2.4, 4.2), 1),
            round(min(base_score + 3.0, 4.8), 1),
        ]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=periods, y=expected,
            mode="lines+markers+text",
            text=[f"{s}" for s in expected],
            textposition="top center",
            textfont=dict(color="#e2e8f0", size=12),
            line=dict(color="#6366f1", width=3),
            marker=dict(size=12, color="#a5b4fc",
                        line=dict(color="#0f172a", width=2)),
            fill="tozeroy",
            fillcolor="rgba(99,102,241,0.08)",
        ))
        # Target line at 3.0
        fig2.add_shape(type="line",
            x0=0, x1=1, xref="paper", y0=3, y1=3,
            line=dict(color="#22c55e", width=1.5, dash="dash"))
        fig2.add_annotation(x=0.02, y=3.2, xref="paper",
            text="Target: Defined (3.0)",
            showarrow=False,
            font=dict(color="#22c55e", size=10))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            yaxis=dict(range=[0, 5.5], gridcolor="#1e293b",
                       title="Maturity Score"),
            xaxis=dict(gridcolor="#1e293b"),
            showlegend=False,
            height=280,
            margin=dict(l=0, r=0, t=20, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Key success factors
        st.markdown("---")
        st.markdown("**🔑 Key Success Factors for Large Enterprises:**")
        factors = [
            ("👔", "Executive Sponsorship",
             "CISO must report directly to CEO/Board"),
            ("💰", "Dedicated Budget",
             "Allocate 8–12% of IT budget to security"),
            ("👥", "Security Team",
             "Hire dedicated SOC analysts and security engineers"),
            ("📋", "Governance",
             "Quarterly board-level security reviews"),
            ("🔄", "Continuous Improvement",
             "Reassess maturity every 6 months"),
            ("🤝", "Culture",
             "Security is everyone's responsibility"),
        ]
        f_cols = st.columns(3)
        for i, (icon, title, desc) in enumerate(factors):
            with f_cols[i % 3]:
                st.markdown(f"""
                <div style="background:#1e293b;border:1px solid #334155;
                            border-radius:10px;padding:14px;margin-bottom:10px;">
                    <div style="font-size:1.4rem;">{icon}</div>
                    <div style="color:#e2e8f0;font-weight:600;
                                margin:6px 0 4px 0;font-size:0.9rem;">
                        {title}
                    </div>
                    <div style="color:#64748b;font-size:0.82rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)