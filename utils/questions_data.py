# utils/questions_data.py
# 210 security questions mapped to NIST CSF 2.0 and ISO 27001

DOMAINS = ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]

DOMAIN_DESCRIPTIONS = {
    "Govern":   "Policies, roles, risk strategy and leadership oversight",
    "Identify": "Asset management, risk assessment and business environment",
    "Protect":  "Access control, data security and system resilience",
    "Detect":   "Continuous monitoring, anomaly detection and log analysis",
    "Respond":  "Incident response planning, communications and mitigation",
    "Recover":  "Recovery planning, improvements and stakeholder communication",
}

QUESTIONS = [

    # ── GOVERN (35 questions) ────────────────────────────────────────────
    {
        "domain": "Govern", "subdomain": "Policy",
        "question": "Does your organization have a formally documented and approved cybersecurity policy?",
        "nist_ref": "GV.PO-01", "iso_ref": "ISO 5.1", "weight": 1.2,
    },
    {
        "domain": "Govern", "subdomain": "Policy",
        "question": "Is the cybersecurity policy reviewed and updated at least once a year?",
        "nist_ref": "GV.PO-01", "iso_ref": "ISO 5.1", "weight": 1.1,
    },
    {
        "domain": "Govern", "subdomain": "Policy",
        "question": "Is the cybersecurity policy communicated to all employees and contractors?",
        "nist_ref": "GV.PO-02", "iso_ref": "ISO 5.1", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Policy",
        "question": "Are specific policies in place for acceptable use of IT systems and internet?",
        "nist_ref": "GV.PO-01", "iso_ref": "ISO 5.10", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Policy",
        "question": "Is there a dedicated information security policy separate from the general IT policy?",
        "nist_ref": "GV.PO-01", "iso_ref": "ISO 5.1", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Policy",
        "question": "Are policy exceptions formally documented, approved and time-limited?",
        "nist_ref": "GV.PO-02", "iso_ref": "ISO 5.1", "weight": 0.9,
    },
    {
        "domain": "Govern", "subdomain": "Policy",
        "question": "Is there a mobile device and remote working security policy in place?",
        "nist_ref": "GV.PO-01", "iso_ref": "ISO 8.1", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Roles and Responsibilities",
        "question": "Are cybersecurity roles and responsibilities clearly defined and assigned?",
        "nist_ref": "GV.RR-01", "iso_ref": "ISO 5.2", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Roles and Responsibilities",
        "question": "Is there a designated CISO or cybersecurity officer with formal authority?",
        "nist_ref": "GV.RR-02", "iso_ref": "ISO 5.2", "weight": 1.2,
    },
    {
        "domain": "Govern", "subdomain": "Roles and Responsibilities",
        "question": "Are cybersecurity responsibilities included in employee job descriptions?",
        "nist_ref": "GV.RR-01", "iso_ref": "ISO 6.2", "weight": 0.9,
    },
    {
        "domain": "Govern", "subdomain": "Roles and Responsibilities",
        "question": "Is there a security steering committee or governance body that meets regularly?",
        "nist_ref": "GV.RR-03", "iso_ref": "ISO 5.4", "weight": 1.1,
    },
    {
        "domain": "Govern", "subdomain": "Roles and Responsibilities",
        "question": "Are third-party security responsibilities clearly defined in contracts?",
        "nist_ref": "GV.RR-04", "iso_ref": "ISO 5.20", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Risk Strategy",
        "question": "Has leadership established and communicated a risk tolerance for cybersecurity?",
        "nist_ref": "GV.RM-01", "iso_ref": "ISO 6.1", "weight": 1.1,
    },
    {
        "domain": "Govern", "subdomain": "Risk Strategy",
        "question": "Is there a formal risk management strategy aligned with business objectives?",
        "nist_ref": "GV.RM-02", "iso_ref": "ISO 6.1", "weight": 1.1,
    },
    {
        "domain": "Govern", "subdomain": "Risk Strategy",
        "question": "Are cybersecurity risks integrated into the enterprise risk management framework?",
        "nist_ref": "GV.RM-03", "iso_ref": "ISO 6.1", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Risk Strategy",
        "question": "Is risk appetite reviewed and updated by senior leadership at least annually?",
        "nist_ref": "GV.RM-01", "iso_ref": "ISO 6.1", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Risk Strategy",
        "question": "Are strategic cybersecurity objectives defined and measurable?",
        "nist_ref": "GV.RM-04", "iso_ref": "ISO 6.2", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Compliance",
        "question": "Are legal, regulatory and contractual cybersecurity obligations tracked and met?",
        "nist_ref": "GV.OC-03", "iso_ref": "ISO 5.31", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Compliance",
        "question": "Is there a process to monitor changes in relevant laws and regulations?",
        "nist_ref": "GV.OC-03", "iso_ref": "ISO 5.31", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Compliance",
        "question": "Are internal cybersecurity audits conducted at least once a year?",
        "nist_ref": "GV.OC-03", "iso_ref": "ISO 9.2", "weight": 1.1,
    },
    {
        "domain": "Govern", "subdomain": "Compliance",
        "question": "Are audit findings tracked and remediated within defined timelines?",
        "nist_ref": "GV.OC-03", "iso_ref": "ISO 10.1", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Compliance",
        "question": "Is there a process to ensure software licences are legally compliant?",
        "nist_ref": "GV.OC-04", "iso_ref": "ISO 5.32", "weight": 0.9,
    },
    {
        "domain": "Govern", "subdomain": "Supply Chain",
        "question": "Does your organization assess cybersecurity risks from third-party vendors?",
        "nist_ref": "GV.SC-01", "iso_ref": "ISO 5.19", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Supply Chain",
        "question": "Are supplier security assessments conducted before onboarding new vendors?",
        "nist_ref": "GV.SC-02", "iso_ref": "ISO 5.19", "weight": 1.1,
    },
    {
        "domain": "Govern", "subdomain": "Supply Chain",
        "question": "Are supplier contracts reviewed for cybersecurity requirements at least annually?",
        "nist_ref": "GV.SC-03", "iso_ref": "ISO 5.20", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Supply Chain",
        "question": "Is there a process to offboard vendors securely when contracts end?",
        "nist_ref": "GV.SC-04", "iso_ref": "ISO 5.19", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Awareness and Training",
        "question": "Is cybersecurity training mandatory for all employees at least annually?",
        "nist_ref": "GV.AT-01", "iso_ref": "ISO 6.3", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Awareness and Training",
        "question": "Is role-based security training provided for IT and security staff?",
        "nist_ref": "GV.AT-02", "iso_ref": "ISO 6.3", "weight": 1.1,
    },
    {
        "domain": "Govern", "subdomain": "Awareness and Training",
        "question": "Are phishing simulation exercises conducted regularly?",
        "nist_ref": "GV.AT-01", "iso_ref": "ISO 6.3", "weight": 1.1,
    },
    {
        "domain": "Govern", "subdomain": "Awareness and Training",
        "question": "Is security awareness training completion tracked and reported to management?",
        "nist_ref": "GV.AT-03", "iso_ref": "ISO 6.3", "weight": 0.9,
    },
    {
        "domain": "Govern", "subdomain": "Awareness and Training",
        "question": "Are new employees required to complete security training before accessing systems?",
        "nist_ref": "GV.AT-01", "iso_ref": "ISO 6.2", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Oversight",
        "question": "Does senior management receive regular cybersecurity performance reports?",
        "nist_ref": "GV.OV-01", "iso_ref": "ISO 5.4", "weight": 0.9,
    },
    {
        "domain": "Govern", "subdomain": "Oversight",
        "question": "Are cybersecurity KPIs and metrics defined and tracked at the executive level?",
        "nist_ref": "GV.OV-02", "iso_ref": "ISO 9.1", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Oversight",
        "question": "Is there a formal process for management to review the ISMS at least annually?",
        "nist_ref": "GV.OV-03", "iso_ref": "ISO 9.3", "weight": 1.0,
    },
    {
        "domain": "Govern", "subdomain": "Oversight",
        "question": "Are cybersecurity budgets reviewed and approved by senior leadership?",
        "nist_ref": "GV.OV-01", "iso_ref": "ISO 5.4", "weight": 1.0,
    },

    # ── IDENTIFY (35 questions) ──────────────────────────────────────────
    {
        "domain": "Identify", "subdomain": "Asset Management",
        "question": "Is there an up-to-date inventory of all hardware assets including servers and laptops?",
        "nist_ref": "ID.AM-01", "iso_ref": "ISO 8.1", "weight": 1.2,
    },
    {
        "domain": "Identify", "subdomain": "Asset Management",
        "question": "Is a current inventory of all software applications and licences maintained?",
        "nist_ref": "ID.AM-02", "iso_ref": "ISO 8.1", "weight": 1.1,
    },
    {
        "domain": "Identify", "subdomain": "Asset Management",
        "question": "Are data assets classified by sensitivity level such as Public, Confidential or Restricted?",
        "nist_ref": "ID.AM-05", "iso_ref": "ISO 8.2", "weight": 1.2,
    },
    {
        "domain": "Identify", "subdomain": "Asset Management",
        "question": "Are all assets assigned an owner who is responsible for their security?",
        "nist_ref": "ID.AM-01", "iso_ref": "ISO 8.1", "weight": 1.1,
    },
    {
        "domain": "Identify", "subdomain": "Asset Management",
        "question": "Are cloud assets and services included in the asset inventory?",
        "nist_ref": "ID.AM-02", "iso_ref": "ISO 8.1", "weight": 1.1,
    },
    {
        "domain": "Identify", "subdomain": "Asset Management",
        "question": "Are IoT and OT devices tracked separately in the asset inventory?",
        "nist_ref": "ID.AM-03", "iso_ref": "ISO 8.1", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Asset Management",
        "question": "Is the asset inventory reviewed and updated at least quarterly?",
        "nist_ref": "ID.AM-01", "iso_ref": "ISO 8.1", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Asset Management",
        "question": "Are removable media devices tracked and controlled in the asset inventory?",
        "nist_ref": "ID.AM-04", "iso_ref": "ISO 8.1", "weight": 0.9,
    },
    {
        "domain": "Identify", "subdomain": "Asset Management",
        "question": "Is there an automated tool used to discover and maintain the asset inventory?",
        "nist_ref": "ID.AM-01", "iso_ref": "ISO 8.1", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Risk Assessment",
        "question": "Are formal risk assessments conducted and documented at least once a year?",
        "nist_ref": "ID.RA-01", "iso_ref": "ISO 8.2", "weight": 1.3,
    },
    {
        "domain": "Identify", "subdomain": "Risk Assessment",
        "question": "Are identified risks prioritised and tracked using a risk register?",
        "nist_ref": "ID.RA-06", "iso_ref": "ISO 6.1.2", "weight": 1.1,
    },
    {
        "domain": "Identify", "subdomain": "Risk Assessment",
        "question": "Are threat intelligence feeds used to inform risk assessments?",
        "nist_ref": "ID.RA-02", "iso_ref": "ISO 8.2", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Risk Assessment",
        "question": "Are risk assessments conducted after major changes to systems or infrastructure?",
        "nist_ref": "ID.RA-03", "iso_ref": "ISO 8.2", "weight": 1.1,
    },
    {
        "domain": "Identify", "subdomain": "Risk Assessment",
        "question": "Are residual risks formally accepted by risk owners after treatment?",
        "nist_ref": "ID.RA-06", "iso_ref": "ISO 6.1.3", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Risk Assessment",
        "question": "Are risk treatment plans documented with owners and deadlines?",
        "nist_ref": "ID.RA-06", "iso_ref": "ISO 6.1.3", "weight": 1.1,
    },
    {
        "domain": "Identify", "subdomain": "Risk Assessment",
        "question": "Is a risk scoring methodology such as likelihood times impact used consistently?",
        "nist_ref": "ID.RA-04", "iso_ref": "ISO 8.2", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Risk Assessment",
        "question": "Are third-party risks included in the organizational risk assessment?",
        "nist_ref": "ID.RA-05", "iso_ref": "ISO 5.19", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Business Environment",
        "question": "Are critical business processes and their cybersecurity dependencies identified?",
        "nist_ref": "ID.BE-04", "iso_ref": "ISO 5.30", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Business Environment",
        "question": "Are critical systems and data assets identified and documented?",
        "nist_ref": "ID.BE-05", "iso_ref": "ISO 5.30", "weight": 1.1,
    },
    {
        "domain": "Identify", "subdomain": "Business Environment",
        "question": "Is the organization's role in the supply chain understood from a security perspective?",
        "nist_ref": "ID.BE-01", "iso_ref": "ISO 5.19", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Business Environment",
        "question": "Are business impact analyses conducted for critical systems?",
        "nist_ref": "ID.BE-04", "iso_ref": "ISO 5.30", "weight": 1.1,
    },
    {
        "domain": "Identify", "subdomain": "Business Environment",
        "question": "Are dependencies on external services such as cloud providers documented?",
        "nist_ref": "ID.BE-02", "iso_ref": "ISO 5.19", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Vulnerability Management",
        "question": "Are systems regularly scanned for known vulnerabilities?",
        "nist_ref": "ID.RA-01", "iso_ref": "ISO 8.8", "weight": 1.2,
    },
    {
        "domain": "Identify", "subdomain": "Vulnerability Management",
        "question": "Are vulnerability scan results reviewed and acted upon promptly?",
        "nist_ref": "ID.RA-01", "iso_ref": "ISO 8.8", "weight": 1.2,
    },
    {
        "domain": "Identify", "subdomain": "Vulnerability Management",
        "question": "Is there a process to track known vulnerabilities from discovery to remediation?",
        "nist_ref": "ID.RA-01", "iso_ref": "ISO 8.8", "weight": 1.1,
    },
    {
        "domain": "Identify", "subdomain": "Vulnerability Management",
        "question": "Are vulnerability disclosures from software vendors monitored and acted upon?",
        "nist_ref": "ID.RA-02", "iso_ref": "ISO 8.8", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Improvement",
        "question": "Are lessons learned from past incidents used to update risk assessments?",
        "nist_ref": "ID.IM-01", "iso_ref": "ISO 10.2", "weight": 0.9,
    },
    {
        "domain": "Identify", "subdomain": "Improvement",
        "question": "Are cybersecurity improvements tracked and reported to management?",
        "nist_ref": "ID.IM-02", "iso_ref": "ISO 10.1", "weight": 0.9,
    },
    {
        "domain": "Identify", "subdomain": "Improvement",
        "question": "Are industry threat intelligence reports reviewed regularly?",
        "nist_ref": "ID.IM-03", "iso_ref": "ISO 5.7", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Improvement",
        "question": "Is there a process to incorporate new threats into existing controls?",
        "nist_ref": "ID.IM-01", "iso_ref": "ISO 10.2", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Improvement",
        "question": "Are security metrics used to identify areas needing improvement?",
        "nist_ref": "ID.IM-02", "iso_ref": "ISO 9.1", "weight": 1.0,
    },
    {
        "domain": "Identify", "subdomain": "Improvement",
        "question": "Are penetration test findings used to drive security improvements?",
        "nist_ref": "ID.IM-01", "iso_ref": "ISO 10.1", "weight": 1.1,
    },

    # ── PROTECT (50 questions) ───────────────────────────────────────────
    {
        "domain": "Protect", "subdomain": "Identity Management",
        "question": "Is multi-factor authentication enforced for all privileged and remote access accounts?",
        "nist_ref": "PR.AA-03", "iso_ref": "ISO 8.5", "weight": 1.5,
    },
    {
        "domain": "Protect", "subdomain": "Identity Management",
        "question": "Is the principle of least privilege enforced for all user accounts?",
        "nist_ref": "PR.AA-05", "iso_ref": "ISO 8.2", "weight": 1.3,
    },
    {
        "domain": "Protect", "subdomain": "Identity Management",
        "question": "Are user access rights reviewed and updated at least every six months?",
        "nist_ref": "PR.AA-05", "iso_ref": "ISO 8.2", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Identity Management",
        "question": "Is MFA enforced for all cloud service access?",
        "nist_ref": "PR.AA-03", "iso_ref": "ISO 8.5", "weight": 1.4,
    },
    {
        "domain": "Protect", "subdomain": "Identity Management",
        "question": "Are shared or generic accounts prohibited across all systems?",
        "nist_ref": "PR.AA-01", "iso_ref": "ISO 8.2", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Identity Management",
        "question": "Is there a formal process to provision and deprovision user accounts?",
        "nist_ref": "PR.AA-02", "iso_ref": "ISO 8.2", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Identity Management",
        "question": "Are privileged accounts separate from standard user accounts?",
        "nist_ref": "PR.AA-05", "iso_ref": "ISO 8.2", "weight": 1.3,
    },
    {
        "domain": "Protect", "subdomain": "Identity Management",
        "question": "Is a privileged access management solution deployed?",
        "nist_ref": "PR.AA-05", "iso_ref": "ISO 8.2", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Identity Management",
        "question": "Are inactive accounts automatically disabled after a defined period?",
        "nist_ref": "PR.AA-02", "iso_ref": "ISO 8.2", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Identity Management",
        "question": "Is single sign-on implemented with strong authentication?",
        "nist_ref": "PR.AA-03", "iso_ref": "ISO 8.5", "weight": 1.0,
    },
    {
        "domain": "Protect", "subdomain": "Data Security",
        "question": "Is sensitive data encrypted at rest using AES-256 or equivalent?",
        "nist_ref": "PR.DS-01", "iso_ref": "ISO 8.24", "weight": 1.4,
    },
    {
        "domain": "Protect", "subdomain": "Data Security",
        "question": "Is sensitive data encrypted in transit using TLS 1.2 or higher?",
        "nist_ref": "PR.DS-02", "iso_ref": "ISO 8.24", "weight": 1.4,
    },
    {
        "domain": "Protect", "subdomain": "Data Security",
        "question": "Are regular automated backups performed and tested for restorability?",
        "nist_ref": "PR.DS-11", "iso_ref": "ISO 8.13", "weight": 1.3,
    },
    {
        "domain": "Protect", "subdomain": "Data Security",
        "question": "Is data loss prevention software deployed to prevent unauthorized data transfers?",
        "nist_ref": "PR.DS-05", "iso_ref": "ISO 8.12", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Data Security",
        "question": "Is there a formal data retention and deletion policy that is enforced?",
        "nist_ref": "PR.DS-03", "iso_ref": "ISO 8.10", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Data Security",
        "question": "Are database access logs reviewed regularly for unauthorized queries?",
        "nist_ref": "PR.DS-07", "iso_ref": "ISO 8.15", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Data Security",
        "question": "Is sensitive data masked or tokenized in non-production environments?",
        "nist_ref": "PR.DS-07", "iso_ref": "ISO 8.11", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Data Security",
        "question": "Are backup copies stored securely offsite or in a separate cloud region?",
        "nist_ref": "PR.DS-11", "iso_ref": "ISO 8.13", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Data Security",
        "question": "Is there a process to securely dispose of hardware containing sensitive data?",
        "nist_ref": "PR.DS-03", "iso_ref": "ISO 8.10", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Data Security",
        "question": "Are encryption keys managed using a dedicated key management system?",
        "nist_ref": "PR.DS-01", "iso_ref": "ISO 8.24", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Platform Security",
        "question": "Are security configuration baselines applied to all systems?",
        "nist_ref": "PR.PS-01", "iso_ref": "ISO 8.9", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Platform Security",
        "question": "Is a patch management process in place with critical patches applied within 30 days?",
        "nist_ref": "PR.PS-02", "iso_ref": "ISO 8.8", "weight": 1.3,
    },
    {
        "domain": "Protect", "subdomain": "Platform Security",
        "question": "Are firewalls and network segmentation controls deployed and reviewed regularly?",
        "nist_ref": "PR.PS-05", "iso_ref": "ISO 8.22", "weight": 1.3,
    },
    {
        "domain": "Protect", "subdomain": "Platform Security",
        "question": "Is unnecessary software and services removed from all systems?",
        "nist_ref": "PR.PS-01", "iso_ref": "ISO 8.9", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Platform Security",
        "question": "Are operating systems and applications updated to supported versions only?",
        "nist_ref": "PR.PS-02", "iso_ref": "ISO 8.8", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Platform Security",
        "question": "Are web application firewalls deployed for all public-facing applications?",
        "nist_ref": "PR.PS-05", "iso_ref": "ISO 8.22", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Platform Security",
        "question": "Is secure coding training provided to all developers?",
        "nist_ref": "PR.PS-03", "iso_ref": "ISO 8.28", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Platform Security",
        "question": "Are code reviews or static analysis tools used before software deployment?",
        "nist_ref": "PR.PS-03", "iso_ref": "ISO 8.28", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Platform Security",
        "question": "Is there a change management process for all system and application changes?",
        "nist_ref": "PR.PS-04", "iso_ref": "ISO 8.32", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Platform Security",
        "question": "Are test and production environments separated with different access controls?",
        "nist_ref": "PR.PS-04", "iso_ref": "ISO 8.31", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Endpoint Security",
        "question": "Is endpoint protection such as EDR or antivirus deployed on all devices?",
        "nist_ref": "PR.PS-04", "iso_ref": "ISO 8.7", "weight": 1.3,
    },
    {
        "domain": "Protect", "subdomain": "Endpoint Security",
        "question": "Are endpoint security solutions centrally managed and monitored?",
        "nist_ref": "PR.PS-04", "iso_ref": "ISO 8.7", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Endpoint Security",
        "question": "Is disk encryption enabled on all laptops and portable devices?",
        "nist_ref": "PR.DS-01", "iso_ref": "ISO 8.24", "weight": 1.3,
    },
    {
        "domain": "Protect", "subdomain": "Endpoint Security",
        "question": "Is there a mobile device management solution for all corporate mobile devices?",
        "nist_ref": "PR.PS-04", "iso_ref": "ISO 8.1", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Endpoint Security",
        "question": "Are USB and removable media ports disabled or controlled on endpoints?",
        "nist_ref": "PR.DS-05", "iso_ref": "ISO 8.12", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Network Security",
        "question": "Is network traffic filtered between internal segments using access control lists?",
        "nist_ref": "PR.PS-05", "iso_ref": "ISO 8.22", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Network Security",
        "question": "Are wireless networks separated from the corporate network?",
        "nist_ref": "PR.PS-05", "iso_ref": "ISO 8.20", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Network Security",
        "question": "Is VPN with strong authentication required for all remote access?",
        "nist_ref": "PR.AA-03", "iso_ref": "ISO 8.20", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Network Security",
        "question": "Are DNS filtering or web proxy solutions used to block malicious sites?",
        "nist_ref": "PR.PS-05", "iso_ref": "ISO 8.23", "weight": 1.1,
    },
    {
        "domain": "Protect", "subdomain": "Network Security",
        "question": "Are network diagrams maintained and updated when changes are made?",
        "nist_ref": "PR.PS-05", "iso_ref": "ISO 8.20", "weight": 1.0,
    },
    {
        "domain": "Protect", "subdomain": "Physical Security",
        "question": "Is physical access to server rooms and data centres restricted and logged?",
        "nist_ref": "PR.PS-05", "iso_ref": "ISO 7.2", "weight": 1.2,
    },
    {
        "domain": "Protect", "subdomain": "Physical Security",
        "question": "Are clean desk and clear screen policies enforced across the organisation?",
        "nist_ref": "PR.PS-05", "iso_ref": "ISO 7.7", "weight": 0.9,
    },
    {
        "domain": "Protect", "subdomain": "Physical Security",
        "question": "Are visitors to secure areas escorted and their access logged?",
        "nist_ref": "PR.PS-05", "iso_ref": "ISO 7.2", "weight": 1.0,
    },
    {
        "domain": "Protect", "subdomain": "Physical Security",
        "question": "Is CCTV used to monitor access to critical infrastructure areas?",
        "nist_ref": "PR.PS-05", "iso_ref": "ISO 7.4", "weight": 1.0,
    },
    {
        "domain": "Protect", "subdomain": "Physical Security",
        "question": "Are environmental controls such as fire suppression and cooling in place for server rooms?",
        "nist_ref": "PR.PS-05", "iso_ref": "ISO 7.5", "weight": 1.0,
    },

    # ── DETECT (40 questions) ────────────────────────────────────────────
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Are networks and systems continuously monitored for unauthorized activity?",
        "nist_ref": "DE.CM-01", "iso_ref": "ISO 8.16", "weight": 1.4,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Is a SIEM or centralised log management solution in place and actively used?",
        "nist_ref": "DE.CM-03", "iso_ref": "ISO 8.15", "weight": 1.3,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Are security logs retained for at least 90 days and reviewed regularly?",
        "nist_ref": "DE.CM-09", "iso_ref": "ISO 8.15", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Are privileged user activities logged and monitored separately?",
        "nist_ref": "DE.CM-03", "iso_ref": "ISO 8.15", "weight": 1.2,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Are failed login attempts monitored and alerted upon?",
        "nist_ref": "DE.CM-01", "iso_ref": "ISO 8.16", "weight": 1.2,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Is network traffic monitored for unusual patterns or volumes?",
        "nist_ref": "DE.CM-01", "iso_ref": "ISO 8.16", "weight": 1.2,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Are file integrity monitoring tools used on critical systems?",
        "nist_ref": "DE.CM-01", "iso_ref": "ISO 8.16", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Are cloud environment audit logs enabled and monitored?",
        "nist_ref": "DE.CM-06", "iso_ref": "ISO 8.15", "weight": 1.2,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Is user behaviour analytics used to detect insider threats?",
        "nist_ref": "DE.CM-03", "iso_ref": "ISO 8.16", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Are alerts reviewed and triaged by security personnel within defined SLAs?",
        "nist_ref": "DE.CM-09", "iso_ref": "ISO 8.16", "weight": 1.2,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Is there 24 by 7 security monitoring coverage either internally or via an MSSP?",
        "nist_ref": "DE.CM-01", "iso_ref": "ISO 8.16", "weight": 1.3,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Are email security gateways used to detect phishing and malicious attachments?",
        "nist_ref": "DE.CM-04", "iso_ref": "ISO 8.23", "weight": 1.2,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Is DNS query logging enabled and monitored for suspicious activity?",
        "nist_ref": "DE.CM-01", "iso_ref": "ISO 8.15", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Are data egress points monitored for unauthorized data transfers?",
        "nist_ref": "DE.CM-05", "iso_ref": "ISO 8.12", "weight": 1.2,
    },
    {
        "domain": "Detect", "subdomain": "Continuous Monitoring",
        "question": "Are configuration changes to critical systems monitored and alerted upon?",
        "nist_ref": "DE.CM-09", "iso_ref": "ISO 8.15", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Are security alerts triaged and correlated to reduce false positives?",
        "nist_ref": "DE.AE-03", "iso_ref": "ISO 8.16", "weight": 1.2,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Are vulnerability scans conducted at least quarterly on internet-facing assets?",
        "nist_ref": "DE.AE-04", "iso_ref": "ISO 8.8", "weight": 1.3,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Are penetration tests or red team exercises conducted at least annually?",
        "nist_ref": "DE.AE-06", "iso_ref": "ISO 8.8", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Are detection rules and signatures updated regularly in the SIEM?",
        "nist_ref": "DE.AE-03", "iso_ref": "ISO 8.16", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Are threat hunting exercises conducted proactively to find hidden threats?",
        "nist_ref": "DE.AE-06", "iso_ref": "ISO 8.16", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Is there a documented process for escalating security events to incidents?",
        "nist_ref": "DE.AE-05", "iso_ref": "ISO 5.25", "weight": 1.2,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Are indicators of compromise from threat intelligence shared and used in detection?",
        "nist_ref": "DE.AE-02", "iso_ref": "ISO 5.7", "weight": 1.0,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Are security events correlated across multiple sources for better detection?",
        "nist_ref": "DE.AE-03", "iso_ref": "ISO 8.16", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Is the mean time to detect security incidents tracked and reported?",
        "nist_ref": "DE.AE-05", "iso_ref": "ISO 9.1", "weight": 1.0,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Are anomaly-based detection methods used alongside signature-based ones?",
        "nist_ref": "DE.AE-01", "iso_ref": "ISO 8.16", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Are detection capabilities tested regularly through red team or purple team exercises?",
        "nist_ref": "DE.AE-06", "iso_ref": "ISO 8.8", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Are security baselines defined so deviations can be detected automatically?",
        "nist_ref": "DE.AE-01", "iso_ref": "ISO 8.9", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Is there a process to detect and alert on new devices connecting to the network?",
        "nist_ref": "DE.CM-07", "iso_ref": "ISO 8.16", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Are application logs monitored for signs of injection attacks or abuse?",
        "nist_ref": "DE.AE-03", "iso_ref": "ISO 8.15", "weight": 1.1,
    },
    {
        "domain": "Detect", "subdomain": "Event Analysis",
        "question": "Are dark web monitoring services used to detect leaked credentials?",
        "nist_ref": "DE.AE-02", "iso_ref": "ISO 5.7", "weight": 1.0,
    },

    # ── RESPOND (25 questions) ───────────────────────────────────────────
    {
        "domain": "Respond", "subdomain": "Incident Management",
        "question": "Is a documented incident response plan in place and accessible to the team?",
        "nist_ref": "RS.MA-01", "iso_ref": "ISO 5.26", "weight": 1.4,
    },
    {
        "domain": "Respond", "subdomain": "Incident Management",
        "question": "Is the incident response plan tested through tabletop or live exercises annually?",
        "nist_ref": "RS.MA-02", "iso_ref": "ISO 5.26", "weight": 1.2,
    },
    {
        "domain": "Respond", "subdomain": "Incident Management",
        "question": "Are security incidents classified by severity with defined escalation thresholds?",
        "nist_ref": "RS.MA-03", "iso_ref": "ISO 5.25", "weight": 1.1,
    },
    {
        "domain": "Respond", "subdomain": "Incident Management",
        "question": "Is there a dedicated incident response team with defined roles?",
        "nist_ref": "RS.MA-01", "iso_ref": "ISO 5.26", "weight": 1.2,
    },
    {
        "domain": "Respond", "subdomain": "Incident Management",
        "question": "Are incident response retainers in place with external security firms?",
        "nist_ref": "RS.MA-04", "iso_ref": "ISO 5.26", "weight": 1.0,
    },
    {
        "domain": "Respond", "subdomain": "Incident Management",
        "question": "Are mean time to respond metrics tracked and reported?",
        "nist_ref": "RS.MA-05", "iso_ref": "ISO 9.1", "weight": 1.0,
    },
    {
        "domain": "Respond", "subdomain": "Incident Management",
        "question": "Is there a war room or dedicated space for managing major incidents?",
        "nist_ref": "RS.MA-01", "iso_ref": "ISO 5.26", "weight": 0.9,
    },
    {
        "domain": "Respond", "subdomain": "Incident Management",
        "question": "Are legal and HR teams involved in the incident response process where required?",
        "nist_ref": "RS.MA-01", "iso_ref": "ISO 5.26", "weight": 1.0,
    },
    {
        "domain": "Respond", "subdomain": "Incident Analysis",
        "question": "Are root cause analyses performed after significant security incidents?",
        "nist_ref": "RS.AN-03", "iso_ref": "ISO 5.27", "weight": 1.2,
    },
    {
        "domain": "Respond", "subdomain": "Incident Analysis",
        "question": "Is forensic evidence preserved correctly during incident investigations?",
        "nist_ref": "RS.AN-04", "iso_ref": "ISO 5.28", "weight": 1.2,
    },
    {
        "domain": "Respond", "subdomain": "Incident Analysis",
        "question": "Are incident timelines documented from detection through to resolution?",
        "nist_ref": "RS.AN-03", "iso_ref": "ISO 5.27", "weight": 1.1,
    },
    {
        "domain": "Respond", "subdomain": "Incident Analysis",
        "question": "Are incident reports shared with relevant stakeholders after resolution?",
        "nist_ref": "RS.AN-05", "iso_ref": "ISO 5.27", "weight": 1.0,
    },
    {
        "domain": "Respond", "subdomain": "Incident Analysis",
        "question": "Are security incidents categorised and tracked in a ticketing or case management system?",
        "nist_ref": "RS.AN-03", "iso_ref": "ISO 5.27", "weight": 1.1,
    },
    {
        "domain": "Respond", "subdomain": "Communications",
        "question": "Are breach notification procedures defined and aligned with regulatory requirements?",
        "nist_ref": "RS.CO-02", "iso_ref": "ISO 5.29", "weight": 1.1,
    },
    {
        "domain": "Respond", "subdomain": "Communications",
        "question": "Is there a communication plan for notifying customers in case of a breach?",
        "nist_ref": "RS.CO-03", "iso_ref": "ISO 5.29", "weight": 1.1,
    },
    {
        "domain": "Respond", "subdomain": "Communications",
        "question": "Are regulators notified within legally required timeframes after a breach?",
        "nist_ref": "RS.CO-04", "iso_ref": "ISO 5.29", "weight": 1.2,
    },
    {
        "domain": "Respond", "subdomain": "Communications",
        "question": "Is there a media and PR response plan for publicly disclosed incidents?",
        "nist_ref": "RS.CO-05", "iso_ref": "ISO 5.29", "weight": 1.0,
    },
    {
        "domain": "Respond", "subdomain": "Mitigation",
        "question": "Can the security team contain and isolate a compromised system within 4 hours?",
        "nist_ref": "RS.MI-01", "iso_ref": "ISO 5.26", "weight": 1.2,
    },
    {
        "domain": "Respond", "subdomain": "Mitigation",
        "question": "Are compromised credentials revoked immediately upon detection?",
        "nist_ref": "RS.MI-02", "iso_ref": "ISO 5.26", "weight": 1.3,
    },
    {
        "domain": "Respond", "subdomain": "Mitigation",
        "question": "Is there a process to block malicious IPs and domains discovered during incidents?",
        "nist_ref": "RS.MI-03", "iso_ref": "ISO 5.26", "weight": 1.1,
    },
    {
        "domain": "Respond", "subdomain": "Mitigation",
        "question": "Are emergency patches applied outside normal change windows during active incidents?",
        "nist_ref": "RS.MI-02", "iso_ref": "ISO 5.26", "weight": 1.1,
    },
    {
        "domain": "Respond", "subdomain": "Mitigation",
        "question": "Is there a process to eradicate malware and verify systems are clean before restoration?",
        "nist_ref": "RS.MI-02", "iso_ref": "ISO 5.26", "weight": 1.2,
    },
    {
        "domain": "Respond", "subdomain": "Improvements",
        "question": "Are lessons learned from incidents used to improve security controls?",
        "nist_ref": "RS.IM-01", "iso_ref": "ISO 10.1", "weight": 1.1,
    },
    {
        "domain": "Respond", "subdomain": "Improvements",
        "question": "Are incident response procedures updated after each major incident?",
        "nist_ref": "RS.IM-02", "iso_ref": "ISO 10.1", "weight": 1.0,
    },
    {
        "domain": "Respond", "subdomain": "Improvements",
        "question": "Are post-incident reviews conducted within two weeks of resolution?",
        "nist_ref": "RS.IM-01", "iso_ref": "ISO 10.1", "weight": 1.0,
    },
    {
        "domain": "Respond", "subdomain": "Improvements",
        "question": "Are improvement actions from post-incident reviews tracked to completion?",
        "nist_ref": "RS.IM-02", "iso_ref": "ISO 10.1", "weight": 1.0,
    },

    # ── RECOVER (25 questions) ───────────────────────────────────────────
    {
        "domain": "Recover", "subdomain": "Incident Recovery",
        "question": "Is a documented business continuity or disaster recovery plan in place?",
        "nist_ref": "RC.RP-01", "iso_ref": "ISO 5.30", "weight": 1.3,
    },
    {
        "domain": "Recover", "subdomain": "Incident Recovery",
        "question": "Are recovery time objectives and recovery point objectives defined for critical systems?",
        "nist_ref": "RC.RP-02", "iso_ref": "ISO 5.30", "weight": 1.2,
    },
    {
        "domain": "Recover", "subdomain": "Incident Recovery",
        "question": "Are BCP and DRP plans tested through full exercises at least annually?",
        "nist_ref": "RC.RP-03", "iso_ref": "ISO 5.30", "weight": 1.1,
    },
    {
        "domain": "Recover", "subdomain": "Incident Recovery",
        "question": "Are recovery procedures documented step by step for each critical system?",
        "nist_ref": "RC.RP-04", "iso_ref": "ISO 5.30", "weight": 1.1,
    },
    {
        "domain": "Recover", "subdomain": "Incident Recovery",
        "question": "Are backups tested for successful restoration at least quarterly?",
        "nist_ref": "RC.RP-01", "iso_ref": "ISO 8.13", "weight": 1.2,
    },
    {
        "domain": "Recover", "subdomain": "Incident Recovery",
        "question": "Are recovery priorities defined so the most critical systems are restored first?",
        "nist_ref": "RC.RP-02", "iso_ref": "ISO 5.30", "weight": 1.1,
    },
    {
        "domain": "Recover", "subdomain": "Incident Recovery",
        "question": "Is there an alternate processing site or cloud failover for critical systems?",
        "nist_ref": "RC.RP-01", "iso_ref": "ISO 5.30", "weight": 1.2,
    },
    {
        "domain": "Recover", "subdomain": "Incident Recovery",
        "question": "Are recovery procedures accessible offline in case primary systems are unavailable?",
        "nist_ref": "RC.RP-04", "iso_ref": "ISO 5.30", "weight": 1.1,
    },
    {
        "domain": "Recover", "subdomain": "Incident Recovery",
        "question": "Are systems verified to be clean and fully functional before being restored to production?",
        "nist_ref": "RC.RP-05", "iso_ref": "ISO 5.30", "weight": 1.2,
    },
    {
        "domain": "Recover", "subdomain": "Incident Recovery",
        "question": "Is there a process to restore data integrity after a ransomware or corruption event?",
        "nist_ref": "RC.RP-01", "iso_ref": "ISO 8.13", "weight": 1.3,
    },
    {
        "domain": "Recover", "subdomain": "Incident Recovery",
        "question": "Are RTOs and RPOs validated through actual recovery tests rather than estimates?",
        "nist_ref": "RC.RP-03", "iso_ref": "ISO 5.30", "weight": 1.2,
    },
    {
        "domain": "Recover", "subdomain": "Incident Recovery",
        "question": "Are critical system dependencies documented to ensure correct recovery order?",
        "nist_ref": "RC.RP-02", "iso_ref": "ISO 5.30", "weight": 1.1,
    },
    {
        "domain": "Recover", "subdomain": "Improvements",
        "question": "Are post-incident reviews used to update and improve recovery plans?",
        "nist_ref": "RC.IM-01", "iso_ref": "ISO 10.1", "weight": 1.1,
    },
    {
        "domain": "Recover", "subdomain": "Improvements",
        "question": "Are recovery test results documented and used to close gaps?",
        "nist_ref": "RC.IM-02", "iso_ref": "ISO 10.1", "weight": 1.0,
    },
    {
        "domain": "Recover", "subdomain": "Improvements",
        "question": "Are recovery plan improvements tracked with owners and deadlines?",
        "nist_ref": "RC.IM-01", "iso_ref": "ISO 10.1", "weight": 1.0,
    },
    {
        "domain": "Recover", "subdomain": "Improvements",
        "question": "Are lessons from industry incidents used to improve your own recovery capabilities?",
        "nist_ref": "RC.IM-02", "iso_ref": "ISO 10.2", "weight": 1.0,
    },
    {
        "domain": "Recover", "subdomain": "Communications",
        "question": "Is there a defined communication plan for notifying stakeholders during recovery?",
        "nist_ref": "RC.CO-03", "iso_ref": "ISO 5.29", "weight": 1.0,
    },
    {
        "domain": "Recover", "subdomain": "Communications",
        "question": "Are customers and partners notified of service restoration timelines during incidents?",
        "nist_ref": "RC.CO-04", "iso_ref": "ISO 5.29", "weight": 1.0,
    },
    {
        "domain": "Recover", "subdomain": "Communications",
        "question": "Is there a status page or communication channel for service availability updates?",
        "nist_ref": "RC.CO-03", "iso_ref": "ISO 5.29", "weight": 0.9,
    },
    {
        "domain": "Recover", "subdomain": "Communications",
        "question": "Are regulators notified of extended outages as required by applicable regulations?",
        "nist_ref": "RC.CO-04", "iso_ref": "ISO 5.29", "weight": 1.1,
    },
    {
        "domain": "Recover", "subdomain": "Communications",
        "question": "Is there a post-recovery report issued to leadership after major incidents?",
        "nist_ref": "RC.CO-05", "iso_ref": "ISO 5.29", "weight": 1.0,
    },
    {
        "domain": "Recover", "subdomain": "Resilience",
        "question": "Are critical services designed with redundancy to avoid single points of failure?",
        "nist_ref": "RC.RP-01", "iso_ref": "ISO 5.30", "weight": 1.2,
    },
    {
        "domain": "Recover", "subdomain": "Resilience",
        "question": "Is there an uninterruptible power supply and generator backup for critical systems?",
        "nist_ref": "RC.RP-01", "iso_ref": "ISO 7.11", "weight": 1.1,
    },
    {
        "domain": "Recover", "subdomain": "Resilience",
        "question": "Are internet and WAN connections redundant with automatic failover?",
        "nist_ref": "RC.RP-01", "iso_ref": "ISO 5.30", "weight": 1.1,
    },
    {
        "domain": "Recover", "subdomain": "Resilience",
        "question": "Are cloud workloads distributed across multiple availability zones?",
        "nist_ref": "RC.RP-01", "iso_ref": "ISO 5.30", "weight": 1.1,
    },
    {
        "domain": "Recover", "subdomain": "Resilience",
        "question": "Is chaos engineering or resilience testing used to validate system reliability?",
        "nist_ref": "RC.RP-03", "iso_ref": "ISO 5.30", "weight": 1.0,
    },
]

# ── SCORE REFERENCE TABLES ────────────────────────────────────────────────────
SCORE_LABELS = {
    0: "Not Implemented",
    1: "Initial / Ad-hoc",
    2: "Developing",
    3: "Defined",
    4: "Managed and Measurable",
    5: "Optimising",
}

SCORE_DESCRIPTIONS = {
    0: "This control does not exist or has not been considered.",
    1: "Some awareness exists but no formal process. Purely reactive.",
    2: "A process exists but it is inconsistent or incomplete.",
    3: "Process is documented, approved and consistently applied.",
    4: "Process is measured, monitored and controlled proactively.",
    5: "Best-in-class. Continuously improved and automated where possible.",
}

RECOMMENDATIONS = {
    "Govern": [
        "Develop and formally approve a cybersecurity policy signed by leadership.",
        "Assign a dedicated security officer with clear accountability.",
        "Establish a risk committee that meets at least quarterly.",
        "Make cybersecurity awareness training mandatory for all staff annually.",
        "Conduct internal audits at least once a year and track all findings.",
    ],
    "Identify": [
        "Deploy an automated asset discovery tool such as Nmap or Qualys.",
        "Implement data classification labels and handling procedures.",
        "Conduct a formal risk assessment using ISO 27005 or NIST SP 800-30.",
        "Maintain a live risk register with owners and remediation timelines.",
        "Subscribe to threat intelligence feeds relevant to your industry.",
    ],
    "Protect": [
        "Enable MFA on all privileged accounts, email and VPN immediately.",
        "Implement a privileged access management solution.",
        "Apply AES-256 encryption for all data at rest and TLS 1.2 in transit.",
        "Establish a 30-day SLA for applying critical vulnerability patches.",
        "Deploy EDR software on all endpoints and enable centralised management.",
        "Implement network segmentation to limit lateral movement.",
    ],
    "Detect": [
        "Deploy a SIEM solution such as Wazuh, Splunk or Microsoft Sentinel.",
        "Enable centralised logging with a minimum 90-day retention policy.",
        "Schedule quarterly vulnerability scans on all internet-facing assets.",
        "Conduct an annual penetration test by a qualified third party.",
        "Implement user behaviour analytics to detect insider threats.",
    ],
    "Respond": [
        "Create and approve a formal Incident Response Plan.",
        "Run tabletop exercises simulating ransomware or data breach scenarios.",
        "Define severity tiers and response time SLAs for each incident type.",
        "Align breach notification procedures with DPDP Act or GDPR requirements.",
        "Retain an external incident response firm for major incident support.",
    ],
    "Recover": [
        "Document and approve a Business Continuity and Disaster Recovery Plan.",
        "Define and validate RTOs and RPOs for all critical systems.",
        "Test backup restoration at least quarterly and verify data integrity.",
        "Create a stakeholder communication template for recovery events.",
        "Design critical services with redundancy to eliminate single points of failure.",
    ],
}
# ── SUBDOMAIN-LEVEL RECOMMENDATIONS (CyberMAP 2.0) ────────────────────────────
# Keyed by (domain, subdomain) so every distinct subdomain gets a
# genuinely relevant recommendation instead of falling back to one
# generic domain-level text.
SUBDOMAIN_RECOMMENDATIONS = {
    ("Govern", "Policy"):
        "Develop, approve and communicate a documented cybersecurity policy — "
        "including mobile device and remote work provisions — reviewed at least annually.",
    ("Govern", "Roles and Responsibilities"):
        "Formally assign a CISO or security lead, document RACI-style responsibilities, "
        "and include security duties in employee job descriptions.",
    ("Govern", "Risk Strategy"):
        "Establish a leadership-approved risk tolerance statement and integrate "
        "cybersecurity risk into the enterprise risk management framework.",
    ("Govern", "Compliance"):
        "Maintain a compliance register tracking legal, regulatory and licensing "
        "obligations, with internal cybersecurity audits conducted annually.",
    ("Govern", "Supply Chain"):
        "Implement a vendor risk assessment and secure offboarding process covering "
        "onboarding, annual contract review and clean contract termination.",
    ("Govern", "Awareness and Training"):
        "Make security awareness training and phishing simulations mandatory for "
        "all staff annually, with completion tracked and reported to management.",
    ("Govern", "Oversight"):
        "Establish a formal management review cadence (at least annually) with "
        "cybersecurity KPIs and budget reported to senior leadership.",

    ("Identify", "Asset Management"):
        "Deploy an automated asset discovery tool and maintain a classified, "
        "owner-assigned inventory reviewed at least quarterly.",
    ("Identify", "Risk Assessment"):
        "Conduct formal risk assessments annually using ISO 27005 or NIST SP 800-30, "
        "maintaining a live risk register with treatment plans and owners.",
    ("Identify", "Business Environment"):
        "Document critical business processes and their dependencies, and conduct "
        "business impact analyses for all critical systems.",
    ("Identify", "Vulnerability Management"):
        "Implement continuous vulnerability scanning with a tracked remediation "
        "workflow from discovery through to closure.",
    ("Identify", "Improvement"):
        "Use security metrics, penetration test findings and lessons from past "
        "incidents to drive a formal continuous improvement process.",

    ("Protect", "Identity Management"):
        "Enforce MFA and least privilege for all accounts, with a formal "
        "provisioning/deprovisioning process and a privileged access management solution.",
    ("Protect", "Data Security"):
        "Encrypt sensitive data at rest (AES-256) and in transit (TLS 1.2+), with "
        "managed encryption keys and regularly tested backups.",
    ("Protect", "Platform Security"):
        "Apply hardened security configuration baselines, patch critical "
        "vulnerabilities within 30 days, and enforce secure software development practices.",
    ("Protect", "Endpoint Security"):
        "Deploy centrally managed EDR or antivirus and disk encryption on all "
        "endpoints, with MDM enforced for corporate mobile devices.",
    ("Protect", "Network Security"):
        "Segment networks, isolate wireless from the corporate network, and require "
        "VPN with strong authentication for all remote access.",
    ("Protect", "Physical Security"):
        "Restrict and log physical access to server rooms, enforce clean desk "
        "practices, and maintain environmental controls such as fire suppression.",

    ("Detect", "Continuous Monitoring"):
        "Deploy a SIEM with centralised logging (minimum 90-day retention) and "
        "continuous, ideally 24x7, security monitoring coverage.",
    ("Detect", "Event Analysis"):
        "Correlate and triage security alerts, conduct regular vulnerability scans "
        "and penetration tests, and incorporate threat intelligence into detection.",

    ("Respond", "Incident Management"):
        "Establish a documented, tested Incident Response Plan with a dedicated "
        "team, defined severity tiers and clear escalation thresholds.",
    ("Respond", "Incident Analysis"):
        "Perform root cause analysis and preserve forensic evidence for every "
        "significant incident, tracked in a case management system.",
    ("Respond", "Communications"):
        "Define breach notification procedures aligned with DPDP/GDPR requirements, "
        "including customer, regulator and PR communication plans.",
    ("Respond", "Mitigation"):
        "Build playbooks to contain compromised systems, revoke credentials and "
        "eradicate threats within defined response time targets.",
    ("Respond", "Improvements"):
        "Conduct post-incident reviews within two weeks of resolution and track "
        "resulting improvement actions to completion.",

    ("Recover", "Incident Recovery"):
        "Document and test a Business Continuity and Disaster Recovery Plan with "
        "validated RTOs/RPOs and quarterly backup restoration tests.",
    ("Recover", "Improvements"):
        "Use recovery test results and post-incident reviews to close gaps, "
        "tracked with clear owners and deadlines.",
    ("Recover", "Communications"):
        "Maintain a stakeholder communication plan for recovery events, including "
        "regulator notification procedures for extended outages.",
    ("Recover", "Resilience"):
        "Design redundancy into critical services — failover connectivity, UPS or "
        "generator backup, multi-availability-zone deployment — and validate with resilience testing.",
}