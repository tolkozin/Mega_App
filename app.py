"""Awesome Dashboard — entry point.

Redirects to Login (if Supabase configured) or Dashboard (local mode).
"""

import streamlit as st

st.set_page_config(page_title="Awesome Dashboard", layout="wide")

from db.client import is_supabase_configured
from db.auth import get_current_user

if is_supabase_configured():
    # SaaS mode: check auth
    if get_current_user():
        st.switch_page("pages/1_Dashboard.py")
    else:
        st.switch_page("pages/0_Login.py")
else:
    # Local mode: go straight to dashboard
    st.switch_page("pages/1_Dashboard.py")
