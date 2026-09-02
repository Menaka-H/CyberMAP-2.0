# app.py - CyberMAP v3.0 with all advanced features + CyberMAP 2.0 extensions
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.database import init_db, seed_questions
from utils.ml_model import train_model
from utils.questions_data import QUESTIONS
from utils.auth import require_login, has_permission, get_current_role, ROLE_PERMISSIONS

st.set_page_config(
    page_title="CyberMAP",
    page_icon=":shield:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stSidebarNavItems"]     { display:none !important; }
[data-testid="stSidebarNavSeparator"] { display:none !important; }
[data-testid="stSidebarNav"]          { display:none !important; }
section[data-testid="stSidebar"]      { background:#0f172a !important; }
section[data-testid="stSidebar"] *    { color:#f0f4ff !important; }
[data-testid="stMetric"] {
    background:#1e293b; border:1px solid #334155;
    border-radius:10px; padding:14px 18px;
}
.stButton button {
    border-radius:8px; font-weight:600;
    background:#2563eb; color:white; border:none;
}
.stButton button:hover { background:#1d4ed8; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource(show_spinner="Initializing CyberMAP...")
def bootstrap():
    init_db()
    seed_questions(QUESTIONS)
    train_model()
    return True

bootstrap()
require_login()

if st.session_state.get("go_to_assessment"):
    del st.session_state["go_to_assessment"]
    st.session_state["_default_nav"] = "New Assessment"

default_nav = st.session_state.pop("_default_nav", None)

role      = get_current_role()
role_info = ROLE_PERMISSIONS.get(role, {})

with st.sidebar:
    st.markdown("## CyberMAP")
    st.markdown(f"""
    <div style="margin-bottom:8px;">
        <div style="color:#e2e8f0;font-size:0.95rem;font-weight:600;">
            {st.session_state.get('name', 'User')}
        </div>
        <span style="background:{role_info.get('color','#6b7280')}22;
                     color:{role_info.get('color','#6b7280')};
                     border:1px solid {role_info.get('color','#6b7280')};
                     border-radius:12px;padding:2px 10px;font-size:0.75rem;">
            {role_info.get('badge','')} {role_info.get('label','').upper()}
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    menu_items = ["Dashboard"]

    if has_permission("can_assess"):
        menu_items.append("New Assessment")

    menu_items += ["Results & Analysis", "History"]

    if has_permission("can_view"):
        menu_items += [
            "AI Advisor",
            "Attack Simulation",
            "Benchmarking",
            "Compliance Checker",
            "Remediation Roadmap",
            "Executive Scorecard",
            "Security Builder",
            "Fleet Import",
            "Continuous Monitoring",
            "Policy Gap Analyzer",
        ]

    nav_index = 0
    if default_nav and default_nav in menu_items:
        nav_index = menu_items.index(default_nav)

    page = st.radio("Navigate", menu_items, index=nav_index, key="nav")

    st.markdown("---")
    st.markdown("**Frameworks**")
    st.markdown("- NIST CSF 2.0")
    st.markdown("- ISO/IEC 27001:2022")
    st.markdown("---")

    if st.button("Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.caption("CyberMAP v3.0 | M.Tech Capstone")

if page == "Dashboard":
    from pg_dashboard import render; render()
elif page == "New Assessment":
    from pg_assessment import render; render()
elif page == "Results & Analysis":
    from pg_results import render; render()
elif page == "History":
    from pg_history import render; render()
elif page == "AI Advisor":
    from pg_chatbot import render; render()
elif page == "Attack Simulation":
    from pg_simulation import render; render()
elif page == "Benchmarking":
    from pg_benchmarking import render; render()
elif page == "Compliance Checker":
    from pg_compliance import render; render()
elif page == "Remediation Roadmap":
    from pg_roadmap import render; render()
elif page == "Executive Scorecard":
    from pg_scorecard import render; render()
elif page == "Security Builder":
    from pg_security_builder import render; render()
elif page == "Fleet Import":
    from pg_fleet_import import render; render()
elif page == "Continuous Monitoring":
    from pg_monitoring import render; render()
elif page == "Policy Gap Analyzer":
    from pg_policy_analyzer import render; render()