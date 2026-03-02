"""Projects management page."""

import streamlit as st

st.set_page_config(page_title="Projects — Awesome Dashboard", layout="wide")

from db.client import is_supabase_configured
from db.auth import get_current_user, require_auth, logout
from db.models import list_projects, create_project, delete_project

if is_supabase_configured():
    require_auth()

user = get_current_user()
if not user:
    if is_supabase_configured():
        st.switch_page("pages/0_Login.py")
    else:
        st.info("Supabase not configured. Projects require authentication.")
        st.page_link("pages/1_Dashboard.py", label="Go to Dashboard →")
        st.stop()

# Sidebar user info
st.sidebar.markdown(f"**{user['display_name']}** ({user['email']})")
if st.sidebar.button("Logout"):
    logout()
    st.switch_page("pages/0_Login.py")

st.title("My Projects")
st.caption("Управление проектами. Каждый проект содержит собственные сценарии финансовой модели.")

# --- Create new project ---
with st.expander("Create New Project", expanded=False):
    with st.form("new_project_form"):
        proj_name = st.text_input("Project Name")
        proj_desc = st.text_area("Description (optional)")
        create_btn = st.form_submit_button("Create Project")
        if create_btn:
            if proj_name.strip():
                result = create_project(user["id"], proj_name.strip(), proj_desc.strip())
                if result:
                    st.success(f"Project '{proj_name.strip()}' created!")
                    st.rerun()
                else:
                    st.error("Failed to create project.")
            else:
                st.warning("Enter a project name.")

# --- List projects ---
projects = list_projects(user["id"])

if not projects:
    st.info("No projects yet. Create your first project above.")
else:
    for proj in projects:
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.markdown(f"### {proj['name']}")
            if proj.get("description"):
                st.caption(proj["description"])
        with col2:
            st.caption(f"Created: {proj['created_at'][:10]}")
        with col3:
            if st.button("Delete", key=f"del_{proj['id']}", type="secondary"):
                delete_project(proj["id"])
                # Clear current project if it was deleted
                if st.session_state.get("current_project", {}).get("id") == proj["id"]:
                    st.session_state.pop("current_project", None)
                st.success(f"Deleted '{proj['name']}'")
                st.rerun()

        # Select as active project
        if st.button(f"Open '{proj['name']}'", key=f"open_{proj['id']}"):
            st.session_state["current_project"] = proj
            st.switch_page("pages/3_Scenarios.py")

        st.markdown("---")
