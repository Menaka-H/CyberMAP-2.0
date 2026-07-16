# pages/pg_chatbot.py — AI Security Advisor Chatbot
import streamlit as st
from utils.database import get_all_assessments, get_assessment_by_id, get_questions
from utils.scoring import compute_domain_scores, get_maturity_label
from utils.questions_data import RECOMMENDATIONS, DOMAINS

def get_context(assessment_id=None):
    """Build context string from latest or selected assessment."""
    assessments = get_all_assessments()
    if not assessments:
        return None, None

    if not assessment_id:
        assessment_id = assessments[0]["id"]

    row = get_assessment_by_id(assessment_id)
    if not row:
        return None, None

    qs = get_questions()
    domain_scores = compute_domain_scores(row["answers"], qs)
    gaps = row["gaps"]

    context = f"""
You are CyberMAP AI Advisor — an expert cybersecurity analyst assistant.
You have access to the following assessment results:

ORGANISATION: {row['org_name']}
ASSESSOR: {row['assessor']}
OVERALL MATURITY SCORE: {row['maturity_score']:.2f} / 5.00
RISK LEVEL: {row['risk_level']}

DOMAIN SCORES:
{chr(10).join([f"- {d}: {v['score']:.2f}/5.00 ({get_maturity_label(v['score'])[0]})"
               for d, v in domain_scores.items()])}

TOP GAPS (Critical/High severity):
{chr(10).join([f"- [{g['severity']}] {g['domain']}: {g['question'][:80]}..."
               for g in gaps[:10] if g.get('severity') in ['Critical','High']])}

FRAMEWORKS: NIST CSF 2.0, ISO/IEC 27001:2022

Your role:
- Answer cybersecurity questions based on these results
- Provide specific, actionable recommendations
- Explain NIST and ISO controls in simple terms
- Suggest remediation priorities based on severity
- Be concise, professional, and practical
- If asked about topics unrelated to cybersecurity, politely redirect
"""
    return context, row

def get_ai_response(context, user_message, history):
    """Generate AI response using rule-based logic + templates."""
    msg = user_message.lower().strip()

    # Score-related questions
    if any(w in msg for w in ["score", "maturity", "level", "rating"]):
        return (
            "Based on your assessment results, I can see your organisation's "
            "maturity profile across the 6 NIST CSF 2.0 domains. "
            "Your weakest domains need immediate attention — I recommend focusing "
            "on controls scoring below 2.0 first, as these represent the highest risk. "
            "Would you like me to explain what each maturity level means?"
        )

    if any(w in msg for w in ["risk", "critical", "danger", "threat"]):
        return (
            "Your AI-predicted risk level indicates the likelihood of a successful "
            "cyber attack based on your current control gaps. Critical and High severity "
            "gaps should be remediated within 30 days. Key immediate actions:\n\n"
            "1. Enable MFA on all privileged accounts\n"
            "2. Deploy or verify EDR on all endpoints\n"
            "3. Ensure critical patches are applied within 30 days\n"
            "4. Test your incident response plan\n\n"
            "Which of these would you like me to explain further?"
        )

    if any(w in msg for w in ["nist", "framework", "csf"]):
        return (
            "NIST CSF 2.0 (released February 2024) organises cybersecurity into "
            "6 functions: **Govern** (new in 2.0), Identify, Protect, Detect, "
            "Respond, and Recover. Each function contains specific outcomes called "
            "subcategories. Your assessment maps your controls to these subcategories "
            "so you can see exactly which NIST requirements you are meeting and which "
            "you are missing. Which NIST domain would you like to explore?"
        )

    if any(w in msg for w in ["iso", "27001", "isms"]):
        return (
            "ISO/IEC 27001:2022 is the international standard for Information "
            "Security Management Systems (ISMS). It requires organisations to "
            "establish, implement, maintain and continually improve security controls. "
            "Your CyberMAP assessment maps each question to specific ISO clauses "
            "(Clause 5 through 10 and Annex A controls). "
            "The most critical ISO controls for your gaps are in Annex A.8 "
            "(Technological controls). Shall I explain the certification process?"
        )

    if any(w in msg for w in ["gap", "missing", "weak", "improve"]):
        return (
            "Your gap analysis has identified controls that score below 3 (Defined). "
            "These are prioritised by severity:\n\n"
            "🔴 **Critical** (score 0-1): Must fix immediately — these represent "
            "fundamental security failures\n"
            "🟠 **High** (score 2): Fix within 30 days — significant risk exposure\n"
            "🟡 **Medium** (score 2-3): Fix within 90 days — notable weaknesses\n\n"
            "I recommend creating a remediation roadmap with owners and deadlines "
            "for each gap. Would you like a suggested timeline?"
        )

    if any(w in msg for w in ["recommend", "advice", "suggest", "next step", "what should"]):
        return (
            "Based on your assessment, here are my top 5 recommendations:\n\n"
            "1. **Enable MFA** on all admin and remote access accounts immediately\n"
            "2. **Deploy EDR** on any endpoints that lack endpoint protection\n"
            "3. **Create/update your Incident Response Plan** and test it quarterly\n"
            "4. **Conduct a formal risk assessment** if you haven't in the last year\n"
            "5. **Enable centralised logging** (SIEM) to improve detection capability\n\n"
            "These five actions will have the highest impact on reducing your risk level. "
            "Which one shall we start with?"
        )

    if any(w in msg for w in ["mfa", "multi-factor", "authentication", "password"]):
        return (
            "Multi-Factor Authentication (MFA) is one of the most impactful security "
            "controls you can implement. It maps to **NIST PR.AA-03** and **ISO 8.5**. "
            "Implementation steps:\n\n"
            "1. Start with admin/privileged accounts (highest priority)\n"
            "2. Then email and VPN access\n"
            "3. Use authenticator apps (TOTP) rather than SMS where possible\n"
            "4. Options: Microsoft Authenticator, Google Authenticator, Duo, Okta\n\n"
            "MFA alone can prevent 99.9% of account compromise attacks. "
            "Would you like guidance on choosing an MFA solution?"
        )

    if any(w in msg for w in ["ransomware", "attack", "breach", "incident"]):
        return (
            "Ransomware is the most common devastating attack organisations face today. "
            "Your CyberMAP controls most relevant to ransomware protection are:\n\n"
            "**Prevention:** Patch management (PR.PS-02), EDR (PR.PS-04), "
            "email filtering (DE.CM-04)\n"
            "**Detection:** SIEM/log monitoring (DE.CM-03), anomaly detection (DE.AE-03)\n"
            "**Recovery:** Tested backups (PR.DS-11), Incident Response Plan (RS.MA-01), "
            "Business Continuity Plan (RC.RP-01)\n\n"
            "The most important control is **immutable, offline backups** — "
            "ransomware cannot encrypt what it cannot reach."
        )

    if any(w in msg for w in ["report", "pdf", "download", "export"]):
        return (
            "Your full PDF report is available in the **Results & Analysis** page. "
            "Click the 'Generate PDF Report' button to download it. "
            "The report includes:\n"
            "• Executive summary with overall score and risk level\n"
            "• Domain-by-domain score breakdown\n"
            "• Full gap analysis table with NIST and ISO references\n"
            "• Prioritised recommendations for each domain\n\n"
            "The report is suitable for presenting to senior management or auditors."
        )

    if any(w in msg for w in ["hello", "hi", "help", "start", "what can you"]):
        return (
            "Hello! I'm your CyberMAP AI Security Advisor. I have access to your "
            "latest assessment results and can help you with:\n\n"
            "• 📊 **Understanding your scores** — what they mean and how to improve\n"
            "• 🔍 **Gap analysis** — explaining specific control weaknesses\n"
            "• 🛡️ **NIST CSF 2.0** — framework guidance and control explanations\n"
            "• 📋 **ISO 27001** — standard requirements and compliance advice\n"
            "• 🚨 **Risk reduction** — prioritised action plans\n"
            "• 💡 **Recommendations** — specific technical remediation steps\n\n"
            "What would you like to explore first?"
        )

    # Default intelligent response
    return (
        f"That's a great cybersecurity question. Based on your assessment results, "
        f"I'd recommend looking at your lowest-scoring domains first and focusing on "
        f"the Critical and High severity gaps identified in your gap analysis. "
        f"These represent the areas where your organisation is most exposed to risk.\n\n"
        f"Could you be more specific about what aspect of your security posture "
        f"you'd like me to help with? For example: specific controls, framework "
        f"requirements, remediation steps, or risk explanations?"
    )

def render():
    st.markdown("""
    <style>
    .chat-msg-user {
        background:#1e3a5f; border-radius:12px 12px 4px 12px;
        padding:12px 16px; margin:8px 0; margin-left:20%;
        color:#e2e8f0;
    }
    .chat-msg-bot {
        background:#1e293b; border:1px solid #334155;
        border-radius:12px 12px 12px 4px;
        padding:12px 16px; margin:8px 0; margin-right:20%;
        color:#e2e8f0;
    }
    .chat-label-user { color:#60a5fa; font-size:0.8rem; text-align:right; margin-right:4px; }
    .chat-label-bot  { color:#34d399; font-size:0.8rem; margin-left:4px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e3a5f,#0f172a);
                border-radius:14px;padding:24px 28px;margin-bottom:20px;
                border:1px solid #2563eb44">
        <h2 style="color:white;margin:0">🤖 AI Security Advisor</h2>
        <p style="color:#93c5fd;margin:6px 0 0 0">
            Ask me anything about your cybersecurity assessment results,
            NIST CSF 2.0, ISO 27001, or how to improve your security posture.
        </p>
    </div>
    """, unsafe_allow_html=True)

    assessments = get_all_assessments()
    if not assessments:
        st.warning("No assessments found. Complete a New Assessment first, then come back here.")
        return

    # Assessment selector
    options = {
        f"ID {a['id']} — {a['org_name']} ({a['created_at'][:10]})": a["id"]
        for a in assessments
    }
    chosen = st.selectbox("Assessment context:", list(options.keys()))
    context, row = get_context(options[chosen])

    if not context:
        st.error("Could not load assessment data.")
        return

    # Context summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Organisation", row["org_name"])
    col2.metric("Overall Score", f"{row['maturity_score']:.2f}/5.00")
    col3.metric("Risk Level", row["risk_level"])

    st.markdown("---")

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        # Welcome message
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": (
                f"Hello! I've loaded the assessment for **{row['org_name']}**. "
                f"Your overall maturity score is **{row['maturity_score']:.2f}/5.00** "
                f"with a **{row['risk_level']}** risk level. "
                f"How can I help you understand and improve your cybersecurity posture?"
            )
        })

    # Quick question buttons
    st.markdown("**Quick questions:**")
    qcols = st.columns(4)
    quick = [
        "What are my biggest gaps?",
        "How do I improve my score?",
        "Explain my risk level",
        "What is NIST CSF 2.0?",
    ]
    for i, q in enumerate(quick):
        if qcols[i].button(q, key=f"quick_{i}", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": q})
            response = get_ai_response(context, q, st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

    st.markdown("---")

    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-label-user">You</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-msg-user">{msg["content"]}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-label-bot">🤖 AI Advisor</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="chat-msg-bot">{msg["content"]}</div>',
                        unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("Ask me about your security posture, gaps, NIST controls...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = get_ai_response(context, user_input, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=False):
        st.session_state.chat_history = []
        st.rerun()