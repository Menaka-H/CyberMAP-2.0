# pg_assessment.py — With optional evidence upload (CyberMAP 2.0)
# FIX: all st.markdown HTML is flush-left (no leading indentation) so
# Streamlit's Markdown parser does not turn indented </div> lines into
# literal code blocks. Logic is unchanged.
import streamlit as st
import os
from datetime import datetime
from utils.database import (
    get_questions, save_assessment, save_evidence,
    get_evidence_for_question, link_evidence_to_assessment,
)
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

# ── Domains where evidence can realistically be attached ──────────
# These are the technical, verifiable domains (firewall, encryption,
# monitoring, etc). Governance domains (Govern, Identify's policy
# side, Respond, Recover) stay slider-only, same as CyberMAP 1.0.
EVIDENCE_ELIGIBLE_DOMAINS = {"Protect", "Detect"}

EVIDENCE_FOLDER = os.path.join(
    os.path.dirname(__file__), "data", "evidence_files"
)


def is_evidence_eligible(question):
    return question.get("domain") in EVIDENCE_ELIGIBLE_DOMAINS


def render():
    # NOTE: HTML below is intentionally flush-left. Do not indent the
    # lines inside these triple-quoted strings or Streamlit will render
    # the closing tags as literal code.
    st.markdown("""
<div style="background:linear-gradient(135deg,#1e3a5f,#0f172a);border-radius:14px;padding:20px 28px;margin-bottom:16px;border:1px solid #2563eb44;">
<h2 style="color:white;margin:0;">📋 New Assessment</h2>
<p style="color:#93c5fd;margin:6px 0 0 0;">Answer all 194 questions across 6 NIST CSF 2.0 domains. Technical questions support optional evidence upload.</p>
</div>
""", unsafe_allow_html=True)

    questions = get_questions()
    if not questions:
        st.error("No questions found. Please restart the app.")
        return

    # ── Organisation Details ──────────────────────────────────
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

    # ── Group questions by domain ─────────────────────────────
    domain_questions = {}
    for q in questions:
        d = q["domain"]
        if d not in domain_questions:
            domain_questions[d] = []
        domain_questions[d].append(q)

    # ── Initialise session state ──────────────────────────────
    if "asm_answers" not in st.session_state:
        st.session_state["asm_answers"] = {}
    if "asm_touched" not in st.session_state:
        st.session_state["asm_touched"] = set()
    if "asm_evidence_ids" not in st.session_state:
        # tracks evidence uploaded THIS session, before assessment
        # has an ID — gets linked to the assessment on submit
        st.session_state["asm_evidence_ids"] = []

    st.markdown("""
<style>
.stSlider { margin-bottom: 4px !important; }
[data-testid="stExpander"] { scroll-behavior: auto !important; }
</style>
""", unsafe_allow_html=True)

    st.markdown("### 📝 Assessment Questions")
    st.info(
        "💡 Select each domain tab and move the sliders to record your "
        "answers. Questions in **Protect** and **Detect** support an "
        "optional evidence upload — screenshot, config export, or PDF."
    )

    tabs = st.tabs([
        f"{d} ({len(domain_questions.get(d, []))}Q)"
        for d in DOMAINS
    ])

    for tab, domain in zip(tabs, DOMAINS):
        with tab:
            dqs   = domain_questions.get(domain, [])
            color = DOMAIN_COLORS.get(domain, "#6366f1")
            dom_touched = sum(
                1 for q in dqs
                if str(q["id"]) in st.session_state["asm_touched"]
            )

            st.markdown(
                f'<div style="background:#1e293b;border-left:4px solid {color};'
                f'border-radius:6px;padding:8px 14px;margin-bottom:12px;">'
                f'<span style="color:{color};font-weight:700;">{domain}</span>'
                f'<span style="color:#64748b;margin-left:12px;font-size:0.85rem;">'
                f'{dom_touched} of {len(dqs)} answered</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            for q in dqs:
                qid     = str(q["id"])
                cur_val = st.session_state["asm_answers"].get(qid, 0)
                eligible = is_evidence_eligible(q)

                # Evidence badge (only for eligible questions that already
                # have evidence attached)
                evidence_badge = ""
                if eligible:
                    existing = get_evidence_for_question(qid)
                    if existing:
                        evidence_badge = (
                            f'<span style="background:#065f46;color:#6ee7b7;'
                            f'border-radius:4px;padding:1px 7px;'
                            f'font-size:0.7rem;margin-left:4px;">'
                            f'📎 {len(existing)} evidence attached</span>'
                        )

                # Question card — built as ONE flush-left HTML string
                # (implicit concatenation, no newlines/indentation) so the
                # Markdown parser never sees an indented </div>.
                st.markdown(
                    f'<div style="background:#0f172a;border-left:3px solid {color};'
                    f'border-radius:6px;padding:8px 12px;margin-bottom:2px;">'
                    f'<div style="color:#e2e8f0;font-size:0.88rem;font-weight:500;">'
                    f'{q["question"]}</div>'
                    f'<div style="margin-top:4px;">'
                    f'<span style="background:#1e293b;color:#60a5fa;'
                    f'border-radius:4px;padding:1px 7px;font-size:0.7rem;">'
                    f'{q.get("nist_ref","—")}</span> '
                    f'<span style="background:#1e293b;color:#34d399;'
                    f'border-radius:4px;padding:1px 7px;font-size:0.7rem;'
                    f'margin-left:4px;">{q.get("iso_ref","—")}</span>'
                    f'{evidence_badge}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                slider_key = f"asm_slider_{qid}"

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

                st.session_state["asm_answers"][qid] = \
                    st.session_state.get(slider_key, cur_val)

                # ── Optional evidence upload (Protect + Detect only) ──
                if eligible:
                    with st.expander(f"📎 Attach evidence for Q{qid} (optional)"):
                        uploaded_file = st.file_uploader(
                            "Upload screenshot, config export, or PDF",
                            type=["png", "jpg", "jpeg", "pdf", "txt", "json"],
                            key=f"evidence_upload_{qid}",
                        )
                        if uploaded_file is not None:
                            if st.button(
                                "Save this evidence",
                                key=f"save_evidence_{qid}",
                            ):
                                os.makedirs(EVIDENCE_FOLDER, exist_ok=True)
                                file_bytes = uploaded_file.getvalue()
                                safe_name = (
                                    f"{qid}_"
                                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                                    f"{uploaded_file.name}"
                                )
                                save_path = os.path.join(EVIDENCE_FOLDER, safe_name)
                                with open(save_path, "wb") as f:
                                    f.write(file_bytes)

                                evidence_id, file_hash, chain_hash = save_evidence(
                                    assessment_id = None,  # linked after submit
                                    question_id   = qid,
                                    filename      = uploaded_file.name,
                                    file_path     = save_path,
                                    file_type     = uploaded_file.type,
                                    file_bytes    = file_bytes,
                                    uploaded_by   = assessor.strip() or "Unknown",
                                    source        = "Manual",
                                )
                                st.session_state["asm_evidence_ids"].append(evidence_id)
                                st.success(
                                    f"✅ Evidence saved and hashed. "
                                    f"SHA-256: {file_hash[:16]}..."
                                )
                                st.rerun()

                        existing = get_evidence_for_question(qid)
                        if existing:
                            st.markdown("**Attached evidence:**")
                            for ev in existing:
                                st.caption(
                                    f"📄 {ev['filename']} — "
                                    f"uploaded {ev['uploaded_at']} — "
                                    f"status: {ev['verification_status']}"
                                )

                st.markdown(
                    "<hr style='margin:4px 0;border-color:#1e293b;'>",
                    unsafe_allow_html=True,
                )

    # ── Progress ──────────────────────────────────────────────
    st.markdown("---")
    total_q       = len(questions)
    total_touched = len(st.session_state["asm_touched"])
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

    evidence_count = len(st.session_state["asm_evidence_ids"])
    if evidence_count > 0:
        st.info(f"📎 {evidence_count} evidence file(s) attached so far this session.")

    # ── Submit ────────────────────────────────────────────────
    st.markdown("---")
    if total_touched < total_q:
        st.warning(
            f"⚠️ {total_q - total_touched} questions not yet answered. "
            f"Unanswered questions will be scored as 0."
        )

    if st.button(
        "🔍 Analyse & Generate Results",
        type="primary",
        use_container_width=True,
    ):
        if not org_name.strip():
            st.error("❌ Please enter the organisation name.")
            return
        if not assessor.strip():
            st.error("❌ Please enter the assessor name.")
            return

        final_answers = {}
        for q in questions:
            qid = str(q["id"])
            final_answers[qid] = \
                st.session_state["asm_answers"].get(qid, 0)

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
                answers       = final_answers,
                scores        = {d: v["score"] for d, v in domain_scores.items()},
                maturity_score= overall_score,
                risk_level    = risk_level,
                gaps          = gaps,
            )

            # Link all evidence uploaded this session to this assessment
            link_evidence_to_assessment(
                st.session_state["asm_evidence_ids"], aid
            )

        st.session_state["last_assessment_id"] = aid
        st.session_state["last_domain_scores"] = domain_scores
        st.session_state["last_overall_score"] = overall_score
        st.session_state["last_gaps"]          = gaps
        st.session_state["last_ml_result"]     = ml_result
        st.session_state["last_org_name"]      = org_name.strip()
        st.session_state["last_assessor"]      = assessor.strip()

        st.session_state["asm_answers"]      = {}
        st.session_state["asm_touched"]      = set()
        st.session_state["asm_evidence_ids"] = []

        st.success(
            f"✅ Assessment complete! "
            f"Score: {overall_score:.2f}/5.00 — "
            f"Risk: {risk_level}"
        )
        st.info(
            "👉 Click **Results & Analysis** in the sidebar "
            "to view your full report and download PDF."
        )