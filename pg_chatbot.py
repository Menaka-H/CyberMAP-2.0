# pg_chatbot.py — AI Security Advisor with assessment context
import streamlit as st
from utils.database import get_all_assessments, get_questions
from utils.scoring import compute_domain_scores, identify_gaps

def get_assessment_context():
    """Load latest assessment data and build context string."""
    assessments = get_all_assessments()
    if not assessments:
        return None, None

    latest = assessments[0]
    questions = get_questions()

    # Get domain scores and gaps
    try:
        import json
        answers = json.loads(latest.get("answers_json", "{}"))
        domain_scores = compute_domain_scores(answers, questions)
        gaps = identify_gaps(answers, questions, threshold=3)
    except Exception:
        domain_scores = {}
        gaps = []

    # Build context
    org      = latest.get("org_name", "Unknown")
    assessor = latest.get("assessor", "Unknown")
    score    = latest.get("maturity_score", 0)
    risk     = latest.get("risk_level", "Unknown")

    # Domain scores text
    domain_text = ""
    for d, v in domain_scores.items():
        s = v.get("score", 0) if isinstance(v, dict) else 0
        domain_text += f"  - {d}: {s:.2f}/5.00\n"

    # Gap summary
    crit = [g for g in gaps if g.get("severity") == "Critical"]
    high = [g for g in gaps if g.get("severity") == "High"]
    med  = [g for g in gaps if g.get("severity") == "Medium"]

    # Top critical gaps text
    crit_text = ""
    for g in crit[:5]:
        crit_text += f"  - {g.get('question','')[:80]} [{g.get('nist_ref','')}]\n"

    high_text = ""
    for g in high[:5]:
        high_text += f"  - {g.get('question','')[:80]} [{g.get('nist_ref','')}]\n"

    context = f"""
ASSESSMENT CONTEXT FOR {org}:
- Assessor: {assessor}
- Overall Maturity Score: {score:.2f}/5.00
- AI/ML Risk Level: {risk}
- Total Gaps Found: {len(gaps)} ({len(crit)} Critical, {len(high)} High, {len(med)} Medium)

DOMAIN SCORES:
{domain_text}

TOP CRITICAL GAPS (Score 0-1):
{crit_text if crit_text else "  None"}

TOP HIGH GAPS (Score 1-2):
{high_text if high_text else "  None"}

SCORE INTERPRETATION:
- 0.0-1.0 = Initial (no formal controls)
- 1.0-2.0 = Developing (basic reactive controls)
- 2.0-3.0 = Defined (documented processes)
- 3.0-4.0 = Managed (monitored controls)
- 4.0-5.0 = Optimising (continuously improving)
"""
    return context, latest

def get_ai_response(user_question, context):
    """Generate intelligent response based on assessment context."""

    q = user_question.lower()

    # Load full data for detailed responses
    assessments = get_all_assessments()
    if not assessments:
        return "No assessment data found. Please complete an assessment first."

    latest    = assessments[0]
    questions = get_questions()

    try:
        import json
        answers      = json.loads(latest.get("answers_json", "{}"))
        domain_scores= compute_domain_scores(answers, questions)
        gaps         = identify_gaps(answers, questions, threshold=3)
    except Exception:
        domain_scores = {}
        gaps          = []

    score  = latest.get("maturity_score", 0)
    risk   = latest.get("risk_level", "Unknown")
    org    = latest.get("org_name", "Organisation")

    crit   = [g for g in gaps if g.get("severity") == "Critical"]
    high   = [g for g in gaps if g.get("severity") == "High"]
    med    = [g for g in gaps if g.get("severity") == "Medium"]

    # ── TOP 3 / IMMEDIATE FIXES ───────────────────────────────
    if any(x in q for x in ["top 3", "fix immediately", "fix first",
                              "most important", "priority", "urgent",
                              "immediately", "critical"]):
        top_gaps = (crit + high)[:3]
        if not top_gaps:
            top_gaps = gaps[:3]

        resp = f"## 🚨 Top 3 Immediate Actions for {org}\n\n"
        resp += f"Based on your **{risk} Risk** assessment "
        resp += f"(score: **{score:.2f}/5.00**), "
        resp += f"here are your 3 highest priority fixes:\n\n"

        for i, g in enumerate(top_gaps, 1):
            sev   = g.get("severity", "")
            emoji = "🔴" if sev == "Critical" else "🟠" if sev == "High" else "🟡"
            resp += f"### {i}. {emoji} {g.get('question', '')}\n"
            resp += f"**Severity:** {sev} | "
            resp += f"**NIST:** `{g.get('nist_ref','')}` | "
            resp += f"**ISO:** `{g.get('iso_ref','')}`\n\n"
            resp += f"**Why it matters:** This control scored below the "
            resp += f"Defined threshold (3.0), meaning it is either not "
            resp += f"implemented or inconsistently applied — leaving your "
            resp += f"organisation exposed.\n\n"
            resp += f"**What to do:** {g.get('recommendation', 'Implement this control as a priority.')}\n\n"
            resp += "---\n"

        resp += f"\n💡 You have **{len(crit)} Critical** and "
        resp += f"**{len(high)} High** gaps in total. "
        resp += f"Go to the **Remediation Roadmap** page for the full 90-day plan."
        return resp

    # ── OVERALL SCORE ─────────────────────────────────────────
    elif any(x in q for x in ["overall score", "maturity score",
                                "my score", "total score", "what is my score"]):
        levels = {
            (0,1): ("Initial","No formal controls. Immediate action required."),
            (1,2): ("Developing","Basic reactive controls only. Needs structure."),
            (2,3): ("Defined","Documented processes but inconsistently applied."),
            (3,4): ("Managed","Monitored and measured controls. Good posture."),
            (4,5): ("Optimising","Continuously improving. Excellent posture."),
        }
        level_name, level_desc = "Unknown", ""
        for (lo, hi), (name, desc) in levels.items():
            if lo <= score < hi:
                level_name, level_desc = name, desc
                break

        resp  = f"## 📊 Overall Maturity Score for {org}\n\n"
        resp += f"**Score: {score:.2f} / 5.00**\n\n"
        resp += f"**Maturity Level: {level_name}**\n\n"
        resp += f"{level_desc}\n\n"
        resp += f"**AI/ML Risk Classification: {risk}**\n\n"
        resp += f"### Domain Breakdown:\n"
        for d, v in domain_scores.items():
            s = v.get("score", 0) if isinstance(v, dict) else 0
            bar = "█" * int(s) + "░" * (5 - int(s))
            resp += f"- **{d}:** {s:.2f}/5.00  `{bar}`\n"
        resp += f"\n**Total Gaps:** {len(gaps)} "
        resp += f"({len(crit)} Critical, {len(high)} High, {len(med)} Medium)"
        return resp

    # ── RISK LEVEL ────────────────────────────────────────────
    elif any(x in q for x in ["risk level", "risk", "danger",
                                "how safe", "how vulnerable"]):
        resp  = f"## 🤖 AI/ML Risk Classification for {org}\n\n"
        resp += f"**Risk Level: {risk}**\n\n"

        risk_explain = {
            "Critical": "Your organisation has severe cybersecurity gaps. "
                        "You are highly vulnerable to attacks. "
                        "Immediate action is required across multiple domains.",
            "High":     "Your organisation has significant gaps that increase "
                        "your exposure to cyber attacks. "
                        "Priority remediation is needed within 30 days.",
            "Medium":   "Your organisation has moderate gaps. "
                        "Controls exist but are inconsistently applied. "
                        "Improvement is needed within 90 days.",
            "Low":      "Your organisation has a good security posture. "
                        "Most controls are implemented. "
                        "Focus on continuous improvement.",
        }
        resp += risk_explain.get(risk, "Risk level determined by AI/ML model.") + "\n\n"
        resp += f"**Score: {score:.2f}/5.00** | "
        resp += f"**Gaps: {len(gaps)}** "
        resp += f"({len(crit)} Critical, {len(high)} High)\n\n"

        if crit:
            resp += "### 🔴 Your Most Critical Vulnerabilities:\n"
            for g in crit[:3]:
                resp += f"- {g.get('question','')[:80]}\n"
        return resp

    # ── WEAKEST DOMAIN ────────────────────────────────────────
    elif any(x in q for x in ["weakest", "lowest", "worst domain",
                                "worst area", "biggest gap"]):
        if domain_scores:
            sorted_d = sorted(
                domain_scores.items(),
                key=lambda x: x[1].get("score", 0) if isinstance(x[1], dict) else 0
            )
            weakest  = sorted_d[0]
            d_name   = weakest[0]
            d_score  = weakest[1].get("score", 0) if isinstance(weakest[1], dict) else 0
            d_gaps   = [g for g in gaps if g.get("domain") == d_name]

            resp  = f"## 📉 Weakest Domain: {d_name}\n\n"
            resp += f"**Score: {d_score:.2f}/5.00** — "
            resp += f"This is your lowest scoring domain.\n\n"
            resp += f"**{len(d_gaps)} gaps found** in {d_name}.\n\n"
            resp += f"### Top Issues in {d_name}:\n"
            for g in d_gaps[:4]:
                resp += f"- {g.get('question','')[:80]}\n"
                resp += f"  → {g.get('recommendation','')[:80]}\n\n"
            return resp

    # ── SPECIFIC DOMAIN ───────────────────────────────────────
    elif any(d.lower() in q for d in ["govern","identify","protect",
                                        "detect","respond","recover"]):
        target = None
        for d in ["Govern","Identify","Protect","Detect","Respond","Recover"]:
            if d.lower() in q:
                target = d
                break

        if target:
            d_info  = domain_scores.get(target, {})
            d_score = d_info.get("score", 0) if isinstance(d_info, dict) else 0
            d_gaps  = [g for g in gaps if g.get("domain") == target]

            resp  = f"## 🔍 {target} Domain Analysis\n\n"
            resp += f"**Score: {d_score:.2f}/5.00**\n\n"
            resp += f"**Gaps found: {len(d_gaps)}**\n\n"

            if d_gaps:
                resp += f"### Control Gaps in {target}:\n"
                for g in d_gaps[:6]:
                    sev   = g.get("severity","")
                    emoji = "🔴" if sev=="Critical" else "🟠" if sev=="High" else "🟡"
                    resp += f"\n{emoji} **{g.get('question','')[:70]}**\n"
                    resp += f"- NIST: `{g.get('nist_ref','')}` | "
                    resp += f"ISO: `{g.get('iso_ref','')}`\n"
                    resp += f"- Fix: {g.get('recommendation','')[:80]}\n"
            else:
                resp += f"✅ No significant gaps in {target}. Well done!\n"
            return resp

    # ── COMPLIANCE ────────────────────────────────────────────
    elif any(x in q for x in ["gdpr","dpdp","pci","hipaa","iso 27001",
                                "complian","regulation"]):
        resp  = f"## ✅ Compliance Status for {org}\n\n"
        resp += f"Based on your score of **{score:.2f}/5.00**, "
        resp += f"here is your likely compliance posture:\n\n"

        frameworks = {
            "DPDP Act 2023":  (score >= 3.0, "data protection, breach notification, vendor management"),
            "GDPR":           (score >= 3.5, "data encryption, breach notification within 72hrs, DPO"),
            "PCI-DSS v4.0":   (score >= 3.0, "encryption, access control, vulnerability scanning"),
            "HIPAA":          (score >= 3.0, "access control, audit logs, data encryption"),
            "ISO 27001:2022": (score >= 3.5, "ISMS, risk assessment, all Annex A controls"),
        }
        for fw, (ok, reqs) in frameworks.items():
            status = "✅ Likely Compliant" if ok else "❌ Gaps Detected"
            resp  += f"**{fw}:** {status}\n"
            resp  += f"Key requirements: {reqs}\n\n"

        resp += f"\n💡 Go to the **Compliance Checker** page for "
        resp += f"detailed requirement-by-requirement results."
        return resp

    # ── ENCRYPTION / MFA / SIEM / IRP specific ───────────────
    elif any(x in q for x in ["mfa","multi-factor","authentication"]):
        mfa_gaps = [g for g in gaps if "authentication" in g.get("question","").lower()
                    or "mfa" in g.get("question","").lower()
                    or "PR.AA-03" in g.get("nist_ref","")]
        resp = f"## 🔐 MFA Status for {org}\n\n"
        if mfa_gaps:
            resp += "❌ **MFA gaps detected:**\n\n"
            for g in mfa_gaps:
                resp += f"- {g.get('question','')}\n"
                resp += f"  Fix: Enable MFA on all privileged accounts, "
                resp += f"email and VPN immediately.\n\n"
        else:
            resp += "✅ No MFA gaps detected. MFA appears to be implemented.\n"
        return resp

    elif any(x in q for x in ["siem","logging","log","monitor"]):
        siem_gaps = [g for g in gaps if "siem" in g.get("question","").lower()
                     or "log" in g.get("question","").lower()
                     or "monitor" in g.get("question","").lower()]
        resp = f"## 📡 SIEM and Monitoring Status for {org}\n\n"
        if siem_gaps:
            resp += "❌ **Monitoring gaps detected:**\n\n"
            for g in siem_gaps[:4]:
                resp += f"- {g.get('question','')}\n"
                resp += f"  Fix: {g.get('recommendation','Deploy SIEM solution.')}\n\n"
            resp += "\n💡 Recommended tools: Wazuh (free), Splunk, Microsoft Sentinel."
        else:
            resp += "✅ Monitoring controls appear to be in place.\n"
        return resp

    elif any(x in q for x in ["incident response","irp","incident plan"]):
        irp_gaps = [g for g in gaps if "incident" in g.get("question","").lower()]
        resp = f"## 🚨 Incident Response Status for {org}\n\n"
        if irp_gaps:
            resp += "❌ **Incident response gaps:**\n\n"
            for g in irp_gaps[:3]:
                resp += f"- {g.get('question','')}\n"
                resp += f"  Fix: {g.get('recommendation','Create an IRP.')}\n\n"
        else:
            resp += "✅ Incident response controls appear to be in place.\n"
        return resp

    elif any(x in q for x in ["encrypt","tls","aes","data protection"]):
        enc_gaps = [g for g in gaps if "encrypt" in g.get("question","").lower()
                    or "tls" in g.get("question","").lower()]
        resp = f"## 🔒 Encryption Status for {org}\n\n"
        if enc_gaps:
            resp += "❌ **Encryption gaps detected:**\n\n"
            for g in enc_gaps[:4]:
                resp += f"- {g.get('question','')}\n"
                resp += f"  Fix: {g.get('recommendation','Implement AES-256 and TLS 1.2+.')}\n\n"
        else:
            resp += "✅ Encryption controls appear to be in place.\n"
        return resp

    # ── GAP SUMMARY ───────────────────────────────────────────
    elif any(x in q for x in ["gap","gaps","weakness","weaknesses",
                                "failing","failed","missing"]):
        resp  = f"## 🔍 Gap Analysis for {org}\n\n"
        resp += f"**Total Gaps: {len(gaps)}**\n"
        resp += f"- 🔴 Critical: {len(crit)}\n"
        resp += f"- 🟠 High: {len(high)}\n"
        resp += f"- 🟡 Medium: {len(med)}\n\n"

        if crit:
            resp += "### 🔴 Critical Gaps (Fix Immediately):\n"
            for g in crit[:4]:
                resp += f"- **{g.get('question','')[:70]}**\n"
                resp += f"  `{g.get('nist_ref','')}` → "
                resp += f"{g.get('recommendation','')[:60]}\n\n"

        if high:
            resp += "### 🟠 High Gaps (Fix Within 30 Days):\n"
            for g in high[:4]:
                resp += f"- {g.get('question','')[:70]}\n"
                resp += f"  → {g.get('recommendation','')[:60]}\n\n"

        return resp

    # ── RANSOMWARE / ATTACK ───────────────────────────────────
    elif any(x in q for x in ["ransomware","attack","vulnerable",
                                "hacked","breach"]):
        detect_score  = domain_scores.get("Detect",  {}).get("score", 0)
        respond_score = domain_scores.get("Respond", {}).get("score", 0)
        recover_score = domain_scores.get("Recover", {}).get("score", 0)

        avg    = (detect_score + respond_score + recover_score) / 3
        vuln   = "HIGH" if avg < 2 else "MEDIUM" if avg < 3 else "LOW"

        resp  = f"## 💥 Ransomware Vulnerability for {org}\n\n"
        resp += f"**Vulnerability Level: {vuln}**\n\n"
        resp += f"Key domain scores for ransomware resistance:\n"
        resp += f"- Detect: {detect_score:.2f}/5.00\n"
        resp += f"- Respond: {respond_score:.2f}/5.00\n"
        resp += f"- Recover: {recover_score:.2f}/5.00\n\n"
        resp += "**To reduce ransomware risk:**\n"
        resp += "- Deploy EDR on all endpoints\n"
        resp += "- Enable SIEM for early detection\n"
        resp += "- Test backups monthly\n"
        resp += "- Run tabletop ransomware simulation exercise\n"
        resp += "- Define and test your incident response plan\n"
        return resp

    # ── DEFAULT — still gives useful answer ───────────────────
    else:
        resp  = f"## 💡 Security Advisor — {org}\n\n"
        resp += f"**Current Status:** Score {score:.2f}/5.00 | "
        resp += f"Risk: {risk} | Gaps: {len(gaps)}\n\n"
        resp += "I can help you with:\n\n"
        resp += "- **Top 3 things to fix** — ask: *What are my top 3 priorities?*\n"
        resp += "- **Domain analysis** — ask: *What are my Protect domain gaps?*\n"
        resp += "- **Risk explanation** — ask: *Why is my risk level high?*\n"
        resp += "- **Compliance** — ask: *Am I GDPR compliant?*\n"
        resp += "- **Specific controls** — ask: *Is MFA implemented?*\n"
        resp += "- **Attack risk** — ask: *How vulnerable am I to ransomware?*\n\n"
        resp += f"You have **{len(crit)} Critical** and **{len(high)} High** "
        resp += f"gaps to address. What would you like to know?"
        return resp


def render():
    st.title("🤖 AI Security Advisor")
    st.markdown(
        "Ask me anything about your cybersecurity assessment results, "
        "gaps, risks and recommendations."
    )

    # Load context
    context, latest = get_assessment_context()

    if not context:
        st.warning(
            "⚠️ No assessment data found. "
            "Please complete an assessment first."
        )
        return

    # Show quick stats
    if latest:
        score = latest.get("maturity_score", 0)
        risk  = latest.get("risk_level", "Unknown")
        org   = latest.get("org_name", "Organisation")
        c1, c2, c3 = st.columns(3)
        c1.metric("Organisation", org)
        c2.metric("Overall Score", f"{score:.2f}/5.00")
        c3.metric("Risk Level", risk)
        st.markdown("---")

    # Quick question buttons
    st.markdown("**💬 Quick Questions — click to ask:**")
    qcols = st.columns(3)
    quick_questions = [
        "What are my top 3 priorities?",
        "What is my overall score?",
        "What are my critical gaps?",
        "Am I GDPR compliant?",
        "Which domain is weakest?",
        "How vulnerable am I to ransomware?",
    ]
    for i, qq in enumerate(quick_questions):
        with qcols[i % 3]:
            if st.button(qq, key=f"qq_{i}", use_container_width=True):
                st.session_state["chatbot_input"] = qq

    st.markdown("---")

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display chat history
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="background:#1e3a5f;border-radius:10px;
                        padding:10px 14px;margin:8px 0;text-align:right;">
                <span style="color:#93c5fd;">👤 {msg['content']}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#1e293b;border-radius:10px;
                        padding:10px 14px;margin:8px 0;">
                <span style="color:#e2e8f0;">{msg['content']}</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(msg["content"])

    # Input box
    default_val = st.session_state.pop("chatbot_input", "")
    user_input  = st.text_input(
        "Ask a security question:",
        value=default_val,
        placeholder="e.g. What are my top 3 priorities?",
        key="chat_input_box",
    )

    col_send, col_clear = st.columns([1, 4])
    with col_send:
        send = st.button("Send ➤", type="primary",
                         use_container_width=True)
    with col_clear:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()

    if send and user_input.strip():
        # Add user message
        st.session_state["chat_history"].append({
            "role": "user",
            "content": user_input.strip(),
        })

        # Generate response
        with st.spinner("Analysing your assessment data..."):
            response = get_ai_response(user_input.strip(), context)

        # Add assistant response
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": response,
        })

        st.rerun()