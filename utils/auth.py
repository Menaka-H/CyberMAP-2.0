# utils/auth.py — Multi-user role system (clean login, no account display)
import streamlit as st
import hashlib

USERS = {
    "admin":  {"password": hashlib.sha256("admin123".encode()).hexdigest(),
               "role": "admin",    "name": "Administrator",
               "email": "admin@cybermap.com"},
    "menaka": {"password": hashlib.sha256("cyber2024".encode()).hexdigest(),
               "role": "assessor", "name": "Menaka H",
               "email": "menaka@reva.edu.in"},
    "darsh":  {"password": hashlib.sha256("darsh123".encode()).hexdigest(),
               "role": "assessor", "name": "Darsh",
               "email": "darsh@cybermap.com"},
    "viewer": {"password": hashlib.sha256("view123".encode()).hexdigest(),
               "role": "viewer",   "name": "Board Viewer",
               "email": "viewer@cybermap.com"},
    "ciso":   {"password": hashlib.sha256("ciso2024".encode()).hexdigest(),
               "role": "admin",    "name": "CISO",
               "email": "ciso@cybermap.com"},
}

ROLE_PERMISSIONS = {
    "admin": {
        "can_assess":  True,
        "can_view":    True,
        "can_export":  True,
        "can_manage":  True,
        "can_email":   True,
        "label":       "Administrator",
        "color":       "#ef4444",
        "badge":       "🔴",
    },
    "assessor": {
        "can_assess":  True,
        "can_view":    True,
        "can_export":  True,
        "can_manage":  False,
        "can_email":   True,
        "label":       "Assessor",
        "color":       "#3b82f6",
        "badge":       "🔵",
    },
    "viewer": {
        "can_assess":  False,
        "can_view":    True,
        "can_export":  False,
        "can_manage":  False,
        "can_email":   False,
        "label":       "Viewer",
        "color":       "#22c55e",
        "badge":       "🟢",
    },
}


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_login(username, password):
    user = USERS.get(username.lower())
    if user and user["password"] == hash_password(password):
        return True, user
    return False, None


def get_current_role():
    return st.session_state.get("role", "viewer")


def has_permission(permission):
    role = get_current_role()
    return ROLE_PERMISSIONS.get(role, {}).get(permission, False)


def require_permission(permission):
    if not has_permission(permission):
        role      = get_current_role()
        role_info = ROLE_PERMISSIONS.get(role, {})
        st.error(
            f"❌ Access denied. Your role "
            f"**{role_info.get('label', role)}** "
            f"does not have permission for this action."
        )
        st.stop()


def show_login():
    st.markdown("""
    <style>
    [data-testid="stSidebarNavItems"]     { display:none !important; }
    [data-testid="stSidebarNavSeparator"] { display:none !important; }
    [data-testid="stSidebarNav"]          { display:none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:

        # Logo and title
        st.markdown("""
        <div style="text-align:center; margin-bottom:32px;">
            <div style="font-size:4rem;">🛡️</div>
            <h1 style="color:white; margin:12px 0 6px 0;
                       font-size:2.2rem; font-weight:700;">
                CyberMAP
            </h1>
            <p style="color:#64748b; margin:0; font-size:0.95rem;">
                Cybersecurity Maturity Assessment Platform
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Login box
        st.markdown("""
        <div style="background:#1e293b; border:1px solid #334155;
                    border-radius:16px; padding:32px;">
        """, unsafe_allow_html=True)

        st.markdown("#### 🔐 Sign In")
        st.markdown("<br>", unsafe_allow_html=True)

        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_user",
            label_visibility="visible"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_pass",
            label_visibility="visible"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Sign In →", use_container_width=True, type="primary"):
            if not username.strip():
                st.error("Please enter your username.")
            elif not password.strip():
                st.error("Please enter your password.")
            else:
                success, user = check_login(username.strip(), password)
                if success:
                    st.session_state["logged_in"] = True
                    st.session_state["username"]  = username.lower().strip()
                    st.session_state["role"]      = user["role"]
                    st.session_state["name"]      = user["name"]
                    st.session_state["email"]     = user["email"]
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")

        st.markdown("</div>", unsafe_allow_html=True)

        # Simple footer caption only
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;">
            <p style="color:#334155; font-size:0.78rem; margin:0;">
                Contact your administrator if you need access.
            </p>
            <p style="color:#1e293b; font-size:0.72rem; margin:4px 0 0 0;">
                CyberMAP v3.0 | M.Tech Capstone | NIST CSF 2.0 | ISO 27001
            </p>
        </div>
        """, unsafe_allow_html=True)


def require_login():
    if not st.session_state.get("logged_in"):
        show_login()
        st.stop()