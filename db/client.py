"""Supabase client singleton."""

import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def get_supabase():
    """Return a cached Supabase client. Falls back gracefully if not configured."""
    if not _SUPABASE_URL or not _SUPABASE_KEY:
        return None

    if "supabase_client" not in st.session_state:
        from supabase import create_client
        st.session_state["supabase_client"] = create_client(_SUPABASE_URL, _SUPABASE_KEY)

    return st.session_state["supabase_client"]


def is_supabase_configured() -> bool:
    """Check if Supabase credentials are set."""
    return bool(_SUPABASE_URL and _SUPABASE_KEY)
