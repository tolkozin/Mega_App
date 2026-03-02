"""Authentication helpers using Supabase Auth."""

import streamlit as st
from db.client import get_supabase, is_supabase_configured


def get_current_user():
    """Return current user dict from session state, or None."""
    return st.session_state.get("user")


def require_auth():
    """Guard: if no authenticated user, redirect to login page."""
    if not is_supabase_configured():
        return  # No auth when Supabase not configured (local dev mode)
    if not get_current_user():
        st.switch_page("pages/0_Login.py")


def login_with_email(email: str, password: str) -> dict | None:
    """Sign in with email/password. Returns user dict or None on failure."""
    sb = get_supabase()
    if not sb:
        return None
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        user = {
            "id": res.user.id,
            "email": res.user.email,
            "display_name": res.user.user_metadata.get("display_name", email.split("@")[0]),
            "access_token": res.session.access_token,
        }
        st.session_state["user"] = user
        return user
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None


def register_with_email(email: str, password: str, display_name: str = "") -> dict | None:
    """Register a new user. Returns user dict or None on failure."""
    sb = get_supabase()
    if not sb:
        return None
    try:
        res = sb.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"display_name": display_name or email.split("@")[0]}},
        })
        if res.user:
            user = {
                "id": res.user.id,
                "email": res.user.email,
                "display_name": display_name or email.split("@")[0],
                "access_token": res.session.access_token if res.session else None,
            }
            st.session_state["user"] = user
            return user
        return None
    except Exception as e:
        st.error(f"Registration failed: {e}")
        return None


def logout():
    """Sign out the current user."""
    sb = get_supabase()
    if sb:
        try:
            sb.auth.sign_out()
        except Exception:
            pass
    st.session_state.pop("user", None)
    st.session_state.pop("current_project", None)
