"""Authentication helpers using Supabase Auth with session persistence."""

import time
import streamlit as st
from db.client import get_supabase, is_supabase_configured
from db.session import save_session_to_cookie, load_session_from_cookie, clear_session_cookie

# Refresh access token proactively every 45 minutes
_TOKEN_REFRESH_INTERVAL = 45 * 60


def get_current_user():
    """Return current user dict from session state, or None."""
    return st.session_state.get("user")


def _store_user(res) -> dict:
    """Extract user dict from Supabase auth response and store in session."""
    user = {
        "id": res.user.id,
        "email": res.user.email,
        "display_name": res.user.user_metadata.get("display_name", res.user.email.split("@")[0]),
        "access_token": res.session.access_token,
    }
    st.session_state["user"] = user
    st.session_state["_token_ts"] = time.time()
    save_session_to_cookie(user, res.session.refresh_token)
    return user


def login_with_email(email: str, password: str) -> dict | None:
    """Sign in with email/password. Returns user dict or None on failure."""
    sb = get_supabase()
    if not sb:
        return None
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        return _store_user(res)
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None


def register_with_email(email: str, password: str, display_name: str = "") -> dict | None:
    """Register a new user. Returns user dict or None.

    If Supabase requires email confirmation, session will be None —
    caller should check for that and show a verification message.
    """
    sb = get_supabase()
    if not sb:
        return None
    try:
        res = sb.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"display_name": display_name or email.split("@")[0]}},
        })
        if res.user and res.session:
            return _store_user(res)
        if res.user and not res.session:
            # Email confirmation required — return user stub without session
            return {
                "id": res.user.id,
                "email": res.user.email,
                "display_name": display_name or email.split("@")[0],
                "access_token": None,
                "needs_verification": True,
            }
        return None
    except Exception as e:
        st.error(f"Registration failed: {e}")
        return None


def refresh_access_token(refresh_token: str) -> dict | None:
    """Exchange a refresh_token for a new access_token. Returns user dict or None."""
    sb = get_supabase()
    if not sb:
        return None
    try:
        res = sb.auth.refresh_session(refresh_token)
        if res.user and res.session:
            return _store_user(res)
        return None
    except Exception:
        return None


def try_restore_session() -> dict | None:
    """Try to restore session from cookie when session_state is empty."""
    if get_current_user():
        return get_current_user()
    cookie_data = load_session_from_cookie()
    if not cookie_data or not cookie_data.get("refresh_token"):
        return None
    return refresh_access_token(cookie_data["refresh_token"])


def ensure_valid_token():
    """Proactively refresh the access token if it's older than 45 minutes."""
    user = get_current_user()
    if not user:
        return
    token_ts = st.session_state.get("_token_ts", 0)
    if time.time() - token_ts < _TOKEN_REFRESH_INTERVAL:
        return
    # Token might be stale — try to refresh from cookie
    cookie_data = load_session_from_cookie()
    if cookie_data and cookie_data.get("refresh_token"):
        refresh_access_token(cookie_data["refresh_token"])


def require_auth():
    """Guard: if no authenticated user, try to restore session, then redirect to login."""
    if not is_supabase_configured():
        return
    if get_current_user():
        ensure_valid_token()
        return
    # Try cookie-based restore before redirecting
    if try_restore_session():
        return
    st.switch_page("pages/0_Login.py")


def send_password_reset(email: str) -> bool:
    """Send a password reset email. Returns True on success."""
    sb = get_supabase()
    if not sb:
        return False
    try:
        sb.auth.reset_password_email(email)
        return True
    except Exception as e:
        st.error(f"Failed to send reset email: {e}")
        return False


def logout():
    """Sign out the current user and clear cookie."""
    sb = get_supabase()
    if sb:
        try:
            sb.auth.sign_out()
        except Exception:
            pass
    st.session_state.pop("user", None)
    st.session_state.pop("current_project", None)
    st.session_state.pop("_token_ts", None)
    clear_session_cookie()
