"""Scenarios management page — CRUD for scenarios within a project."""

import streamlit as st

st.set_page_config(page_title="Scenarios — Awesome Dashboard", layout="wide")

from db.client import is_supabase_configured
from db.auth import get_current_user, require_auth, logout
from db.models import list_scenarios, save_scenario, load_scenario_config, delete_scenario
from core.model_config import ModelConfig

if is_supabase_configured():
    require_auth()

user = get_current_user()
if not user:
    if is_supabase_configured():
        st.switch_page("pages/0_Login.py")
    else:
        st.info("Supabase not configured. Scenarios require authentication.")
        st.page_link("pages/1_Dashboard.py", label="Go to Dashboard →")
        st.stop()

# Sidebar
st.sidebar.markdown(f"**{user['display_name']}** ({user['email']})")
if st.sidebar.button("Logout"):
    logout()
    st.switch_page("pages/0_Login.py")

# Check current project
project = st.session_state.get("current_project")
if not project:
    st.warning("No project selected. Please select a project first.")
    st.page_link("pages/2_Projects.py", label="Go to Projects →")
    st.stop()

st.title(f"Scenarios — {project['name']}")
st.caption("Сохраняйте и загружайте конфигурации финансовой модели как сценарии.")

# --- Save current config as scenario ---
with st.expander("Save New Scenario", expanded=False):
    with st.form("save_scenario_form"):
        sc_name = st.text_input("Scenario Name")
        sc_notes = st.text_area("Notes (optional)")
        save_btn = st.form_submit_button("Save Current Config")
        if save_btn:
            if sc_name.strip():
                # Build config from defaults (user can also load from sidebar first)
                config = ModelConfig.from_defaults()
                result = save_scenario(user["id"], project["id"], sc_name.strip(), config, sc_notes.strip())
                if result:
                    st.success(f"Scenario '{sc_name.strip()}' saved!")
                    st.rerun()
                else:
                    st.error("Failed to save scenario.")
            else:
                st.warning("Enter a scenario name.")

# --- List scenarios ---
scenarios = list_scenarios(user["id"], project["id"])

if not scenarios:
    st.info("No scenarios yet. Save your first scenario above.")
else:
    for sc in scenarios:
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.markdown(f"**{sc['name']}**")
            if sc.get("notes"):
                st.caption(sc["notes"])
        with col2:
            st.caption(f"Created: {sc['created_at'][:10]}")
        with col3:
            if st.button("Load", key=f"load_{sc['id']}"):
                loaded_config = load_scenario_config(sc["id"])
                if loaded_config:
                    st.session_state["loaded_config"] = loaded_config
                    st.success(f"Loaded '{sc['name']}'. Go to Dashboard to use it.")
                else:
                    st.error("Failed to load scenario config.")
        with col4:
            if st.button("Delete", key=f"del_{sc['id']}", type="secondary"):
                delete_scenario(sc["id"])
                st.success(f"Deleted '{sc['name']}'")
                st.rerun()

        st.markdown("---")

# Navigation
st.page_link("pages/1_Dashboard.py", label="Go to Dashboard →")
st.page_link("pages/2_Projects.py", label="← Back to Projects")
