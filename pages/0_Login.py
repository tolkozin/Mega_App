"""Login / Registration / Password Reset page."""

import streamlit as st

st.set_page_config(page_title="Login — Awesome Dashboard", layout="centered")

from db.client import is_supabase_configured
from db.auth import get_current_user, login_with_email, register_with_email, send_password_reset

# If already logged in, go to dashboard
if get_current_user():
    st.switch_page("pages/1_Dashboard.py")

# If Supabase not configured, skip auth
if not is_supabase_configured():
    st.info("Supabase not configured. Running in local mode.")
    st.page_link("pages/1_Dashboard.py", label="Go to Dashboard →")
    st.stop()

st.title("Awesome Dashboard")
st.markdown("Financial model for subscription apps")

tab_login, tab_register, tab_reset = st.tabs(["Login", "Register", "Reset Password"])

with tab_login:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if email and password:
                user = login_with_email(email, password)
                if user:
                    st.success(f"Welcome, {user['display_name']}!")
                    st.switch_page("pages/1_Dashboard.py")
            else:
                st.warning("Please enter email and password.")

with tab_register:
    with st.form("register_form"):
        reg_email = st.text_input("Email", key="reg_email")
        reg_name = st.text_input("Display Name", key="reg_name")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_password2 = st.text_input("Confirm Password", type="password", key="reg_pass2")
        reg_submitted = st.form_submit_button("Register")
        if reg_submitted:
            if not reg_email or not reg_password:
                st.warning("Please fill in all fields.")
            elif reg_password != reg_password2:
                st.error("Passwords do not match.")
            elif len(reg_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                user = register_with_email(reg_email, reg_password, reg_name)
                if user and user.get("needs_verification"):
                    st.info("Проверьте почту — мы отправили ссылку для подтверждения email.")
                elif user:
                    st.success("Account created! Redirecting...")
                    st.switch_page("pages/1_Dashboard.py")

with tab_reset:
    with st.form("reset_form"):
        reset_email = st.text_input("Email", key="reset_email")
        reset_submitted = st.form_submit_button("Send Reset Link")
        if reset_submitted:
            if reset_email:
                if send_password_reset(reset_email):
                    st.success("Ссылка для сброса пароля отправлена на вашу почту.")
            else:
                st.warning("Please enter your email.")
