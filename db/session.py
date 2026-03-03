"""Session persistence via browser cookies using extra-streamlit-components."""

import streamlit as st
import extra_streamlit_components as stx
import json

_COOKIE_KEY = "mega_app_session"
_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


def _get_cookie_manager():
    """Return a cached cookie manager instance."""
    return stx.CookieManager(key="mega_app_cookies")


def save_session_to_cookie(user: dict, refresh_token: str):
    """Save user info and refresh_token to a browser cookie."""
    cm = _get_cookie_manager()
    payload = {
        "id": user["id"],
        "email": user["email"],
        "display_name": user.get("display_name", ""),
        "refresh_token": refresh_token,
    }
    cm.set(_COOKIE_KEY, json.dumps(payload), max_age=_COOKIE_MAX_AGE)


def load_session_from_cookie() -> dict | None:
    """Read session cookie. Returns dict with user info + refresh_token, or None."""
    cm = _get_cookie_manager()
    raw = cm.get(_COOKIE_KEY)
    if not raw:
        return None
    try:
        if isinstance(raw, str):
            return json.loads(raw)
        return raw
    except (json.JSONDecodeError, TypeError):
        return None


def clear_session_cookie():
    """Delete the session cookie on logout."""
    cm = _get_cookie_manager()
    cm.delete(_COOKIE_KEY)
