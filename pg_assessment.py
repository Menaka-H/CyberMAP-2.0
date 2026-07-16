# pg_assessment.py — Fixed with proper progress tracking
import streamlit as st
from utils.database import get_questions, save_assessment
from utils.scoring import compute_domain_scores, identify_gaps, build_feature_vector
from utils.ml_model import predict_risk
from utils.questions_data import DOMAINS

SCORE_OPTIONS = {
    0: "0 — Not Implemented",
    1: "1 — Initial",
    2: "2 — Developing",
    3: "3 — Defined",
    4: "4 — Managed",
    5: "5 — Optimising",
}

DOMAIN_COLORS = {
    "Govern":   "#6366f1",
    "Identify": "#3b82f6",
    "Protect":  "#10b981",
    "Detect":   "#f59e0b",
    "Respond":  "#ef4444",
    "Recover":  "#8b5cf6",
}

def render():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e3a5f,#0f172a);
                border-radius:14px;padding:24px 28px;margin-bottom:20px;
                border:1px solid #2563eb44;">
        <h2 style="color:white;margin:0;">📋 New Assessment</h2>
        <p style="color:#93c5fd;margin:6px 0 0 0;">
            Answer all 194 questions across 6 NIST CSF 2.0 domains.
            Move each slider to record your answer — untouched sliders
            are not counted as answered.
        </p>
    </div>
    """, unsafe_allow_html=True)

    questions = get_questions()
    if not questions:
        st.error("No questions found. Please restart the app.")
        return

    # ── Organisation Details ──────────────────────────────────────────
    st.markdown("### 🏢 Organisation Details")
    c1, c2 = st.columns(2)
    with c1:
        org_name = st.text_input(
            "Organisation Name *",
            placeholder="e.g. REVA University",
            key="asm_org",
        )
        industry = st.selectbox(
            "Industry",
            ["Technology","Finance & Banking","Healthcare",
             "Manufacturing","Retail & E-commerce","Government",
             "Education","Logistics","Energy & Utilities","Other"],
            key="asm_industry",
        )
    with c2:
        assessor = st.text_input(
            "Assessor Name *",
            placeholder="e.g. Menaka H",
            key="asm_assessor",
        )
        emp_size = st.selectbox(
            "Employee Size",
            ["1–50","51–200","201–500",
             "500–1000","1000–5000","5000+"],
            key="asm_emp",
        )

    st.markdown("---")

    # ── Group questions by domain ─────────────────────────────────────
    domain_questions = {}
    for q in questions:
        d = q["domain"]
        if d not in domain_questions:
            domain_questions[d] = []
        domain_questions[d].append(q)

    # ── Initialise TWO stores ─────────────────────────────────────────
    # answers     — actual slider values (default 0)
    # touched     — set of question IDs the user has actually moved
    if "asm_answers" not in st.session_state:
        st.session_state["asm_answers"] = {}
    if "asm_touched" not in st.session_state:
        st.session_state["asm_touched"] = set()

    answers = st.session_state["asm_answers"]
    touched = st.session_state["asm_touched"]

    # ── Domain Overview Cards ─────────────────────────────────────────
    st.markdown("### 📊 Domain Overview")
    cols = st.columns(6)
    for i, domain in enumerate(DOMAINS):
        dqs   = domain_questions.get(domain, [])
        color = DOMAIN_COLORS.get(domain, "#6366f1")
        dom_touched = sum(
            1 for q in dqs if str(q["id"]) in touched
        )
        with cols[i]:
            st.markdown(f"""
            <div style="background:#1e293b;border:2px solid {color};
                        border-radius:10px;padding:12px;text-align:center;">
                <div style="color:{color};font-weight:700;
                            font-size:0.85rem;">{domain}</div>
                <div style="color:#e2e8f0;font-size:1.2rem;
                            font-weight:700;">{len(dqs)}Q</div>
                <div style="color:#64748b;font-size:0.72rem;">
                    {dom_touched} answered
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📝 Assessment Questions")
    st.info("💡 Move each slider to record your answer. The progress bar only counts questions you have actively answered.")

    # ── Questions per domain ──────────────────────────────────────────
    for domain in DOMAINS:
        dqs   = domain_questions.get(domain, [])
        color = DOMAIN_COLORS.get(domain, "#6366f1")
        dom_touched = sum(
            1 for q in dqs if str(q["id"]) in touched
        )

        with st.expander(
            f"{domain} — {len(dqs)} questions "
            f"({dom_touched} answered)",
            expanded=False,
        ):
            for q in dqs:
                qid     = str(q["id"])
                cur_val = answers.get(qid, 0)

                # Question card
                st.markdown(f"""
                <div style="background:#0f172a;
                            border-left:3px solid {color};
                            border-radius:6px;
                            padding:10px 14px;
                            margin-bottom:4px;">
                    <div style="color:#e2e8f0;font-size:0.9rem;
                                font-weight:500;">
                        {q['question']}
                    </div>
                    <div style="margin-top:4px;">
                        <span style="background:#1e293b;color:#60a5fa;
                                     border-radius:4px;padding:2px 8px;
                                     font-size:0.72rem;">
                            {q.get('nist_ref','—')}
                        </span>
                        <span style="background:#1e293b;color:#34d399;
                                     border-radius:4px;padding:2px 8px;
                                     font-size:0.72rem;margin-left:4px;">
                            {q.get('iso_ref','—')}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                slider_key = f"asm_slider_{qid}"

                # on_change callback — marks question as touched
                def on_change(qid=qid, sk=slider_key):
                    val = st.session_state.get(sk, 0)
                    st.session_state["asm_answers"][qid] = val
                    st.session_state["asm_touched"].add(qid)

                st.select_slider(
                    label=f"Q{qid}",
                    options=[0, 1, 2, 3, 4, 5],
                    value=cur_val,
                    format_func=lambda x: SCORE_OPTIONS[x],
                    key=slider_key,
                    on_change=on_change,
                    label_visibility="collapsed",
                )

                # Always sync current value
                answers[qid] = st.session_state.get(slider_key, cur_val)

    # ── Progress ──────────────────────────────────────────────────────
    st.markdown("---")
    total_q      = len(questions)
    total_touched = len(touched)
    pct = int((total_touched / total_q) * 100) if total_q > 0 else 0

    col_p, col_s = st.columns([3, 1])
    with col_p:
        st.progress(pct / 100)
        st.caption(
            f"Progress: {total_touched} / {total_q} "
            f"questions answered ({pct}%)"
        )
    with col_s:
        if pct == 100:
            st.success("✅ 100% done")
        elif pct >= 50:
            st.warning(f"⚠️ {pct}% done")
        else:
            st.error(f"🔴 {pct}% done")

    # ── Submit ────────────────────────────────────────────────────────
    st.markdown("---")

    # Show warning if not all answered
    if total_touched < total_q:
        st.warning(
            f"⚠️ {total_q - total_touched} questions not yet answered. "
            f"Unanswered questions will be scored as 0 (Not Implemented)."
        )

    if st.button(
        "🔍 Analyse & Generate Results",
        type="primary",
        use_container_width=True,
    ):
        # Validation
        if not org_name.strip():
            st.error("❌ Please enter the organisation name.")
            return
        if not assessor.strip():
            st.error("❌ Please enter the assessor name.")
            return

        # Build final answers — 0 for any untouched questions
        final_answers = {}
        for q in questions:
            qid = str(q["id"])
            final_answers[qid] = answers.get(qid, 0)

        with st.spinner(
            "Computing maturity scores and running AI analysis..."
        ):
            domain_scores = compute_domain_scores(
                final_answers, questions
            )
            overall_score = sum(
                v["score"] for v in domain_scores.values()
            ) / len(domain_scores)

            gaps        = identify_gaps(
                final_answers, questions, threshold=3
            )
            feature_vec = build_feature_vector(domain_scores)
            ml_result   = predict_risk(feature_vec)
            risk_level  = ml_result.get("risk_level", "Unknown")

            aid = save_assessment(
                org_name      = org_name.strip(),
                assessor      = assessor.strip(),
                industry      = industry,
                emp_size      = emp_size,
                answers       = final_answers,
                domain_scores = domain_scores,
                overall_score = overall_score,
                gaps          = gaps,
                risk_level    = risk_level,
            )

        # Store in session
        st.session_state["last_assessment_id"] = aid
        st.session_state["last_domain_scores"] = domain_scores
        st.session_state["last_overall_score"] = overall_score
        st.session_state["last_gaps"]          = gaps
        st.session_state["last_ml_result"]     = ml_result
        st.session_state["last_org_name"]      = org_name.strip()
        st.session_state["last_assessor"]      = assessor.strip()

        # Clear for next assessment
        st.session_state["asm_answers"] = {}
        st.session_state["asm_touched"] = set()

        st.success(
            f"✅ Assessment complete! "
            f"Score: {overall_score:.2f}/5.00 — "
            f"Risk: {risk_level}"
        )
        st.info(
            "👉 Click **Results & Analysis** in the sidebar "
            "to view your full report and download PDF."
        )