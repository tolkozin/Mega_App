"""Scenarios management page — CRUD for scenarios within a project, role-aware."""

import streamlit as st

st.set_page_config(page_title="Scenarios — Awesome Dashboard", layout="wide")

from db.client import is_supabase_configured
from db.auth import get_current_user, require_auth, logout
from db.models import (
    list_scenarios_for_project, save_scenario, load_scenario_config,
    delete_scenario, get_user_role_for_project,
)
from ui.sidebar import config_to_session_state
from ecommerce.sidebar import ecom_config_to_session_state

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

# Determine user role
role = get_user_role_for_project(user["id"], project["id"]) if is_supabase_configured() else "owner"
can_edit = role in ("owner", "editor")

role_colors = {"owner": "green", "editor": "blue", "viewer": "orange"}
product_type = project.get("product_type", "subscription")
ptype_label = "E-commerce" if product_type == "ecommerce" else "Subscription"

st.title(f"Scenarios — {project['name']}")
st.caption(f"Сохраняйте и загружайте конфигурации финансовой модели как сценарии. "
           f"Тип: **{ptype_label}** | "
           f"Ваша роль: :{role_colors.get(role, 'gray')}[{role.capitalize() if role else 'N/A'}]")

# --- Save current config as scenario (editors/owners only) ---
if can_edit:
    with st.expander("Save New Scenario", expanded=False):
        # Determine which config to save
        if product_type == "ecommerce":
            last_config = st.session_state.get("_last_ecom_config")
        else:
            last_config = st.session_state.get("_last_config")

        if not last_config:
            st.warning("No config available yet. Visit the Dashboard first to generate a config, then come back to save it.")
        else:
            with st.form("save_scenario_form"):
                sc_name = st.text_input("Scenario Name")
                sc_notes = st.text_area("Notes (optional)")
                save_btn = st.form_submit_button("Save Current Config")
                if save_btn:
                    if sc_name.strip():
                        result = save_scenario(user["id"], project["id"], sc_name.strip(), last_config, sc_notes.strip())
                        if result:
                            st.success(f"Scenario '{sc_name.strip()}' saved!")
                            st.rerun()
                        else:
                            st.error("Failed to save scenario.")
                    else:
                        st.warning("Enter a scenario name.")

# --- List scenarios (all scenarios visible via RLS) ---
scenarios = list_scenarios_for_project(project["id"])

if not scenarios:
    st.info("No scenarios yet." + (" Save your first scenario above." if can_edit else ""))
else:
    for sc in scenarios:
        cols = [3, 2, 1] if not can_edit else [3, 2, 1, 1]
        columns = st.columns(cols)
        with columns[0]:
            st.markdown(f"**{sc['name']}**")
            if sc.get("notes"):
                st.caption(sc["notes"])
        with columns[1]:
            st.caption(f"Created: {sc['created_at'][:10]}")
        with columns[2]:
            if st.button("Load", key=f"load_{sc['id']}"):
                loaded_config = load_scenario_config(sc["id"], product_type)
                if loaded_config:
                    # Push loaded config into widget keys so sidebar picks it up
                    if product_type == "ecommerce":
                        ecom_config_to_session_state(loaded_config)
                    else:
                        config_to_session_state(loaded_config)
                    st.success(f"Loaded '{sc['name']}'. Go to Dashboard to use it.")
                else:
                    st.error("Failed to load scenario config.")
        if can_edit and len(columns) > 3:
            with columns[3]:
                if st.button("Delete", key=f"del_{sc['id']}", type="secondary"):
                    delete_scenario(sc["id"])
                    st.success(f"Deleted '{sc['name']}'")
                    st.rerun()

        st.markdown("---")

# Navigation
st.page_link("pages/1_Dashboard.py", label="Go to Dashboard →")
st.page_link("pages/2_Projects.py", label="← Back to Projects")
