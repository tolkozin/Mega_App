"""Projects management page with sharing support."""

import streamlit as st

st.set_page_config(page_title="Projects — Awesome Dashboard", layout="wide")

from db.client import is_supabase_configured
from db.auth import get_current_user, require_auth, logout
from db.models import (
    list_all_user_projects, create_project, delete_project,
    lookup_user_by_email, share_project, list_project_shares,
    revoke_share, update_share_role,
)
from ui.sidebar import CONFIG_DEFAULTS
from ecommerce.sidebar import ECOM_CONFIG_DEFAULTS

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
        product_type = st.selectbox("Product Type", ["subscription", "ecommerce"],
            format_func=lambda x: "Subscription App" if x == "subscription" else "E-commerce",
            help="Тип продукта определяет финансовую модель: подписочный SaaS или e-commerce.")
        create_btn = st.form_submit_button("Create Project")
        if create_btn:
            if proj_name.strip():
                result = create_project(user["id"], proj_name.strip(), proj_desc.strip(), product_type)
                if result:
                    st.success(f"Project '{proj_name.strip()}' created!")
                    st.rerun()
                else:
                    st.error("Failed to create project.")
            else:
                st.warning("Enter a project name.")

# --- List projects ---
projects = list_all_user_projects(user["id"])

if not projects:
    st.info("No projects yet. Create your first project above.")
else:
    for proj in projects:
        role = proj.get("_role", "owner")
        owner_name = proj.get("_owner_name")

        # Role badge + product type badge
        role_colors = {"owner": "green", "editor": "blue", "viewer": "orange"}
        role_label = role.capitalize()
        ptype = proj.get("product_type", "subscription")
        ptype_label = "E-commerce" if ptype == "ecommerce" else "Subscription"
        ptype_color = "violet" if ptype == "ecommerce" else "blue"

        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.markdown(f"### {proj['name']}  :{role_colors.get(role, 'gray')}[{role_label}]  :{ptype_color}[{ptype_label}]")
            if owner_name:
                st.caption(f"Owner: {owner_name}")
            if proj.get("description"):
                st.caption(proj["description"])
        with col2:
            st.caption(f"Created: {proj['created_at'][:10]}")
        with col3:
            # Only owners can delete
            if role == "owner":
                if st.button("Delete", key=f"del_{proj['id']}", type="secondary"):
                    delete_project(proj["id"])
                    if st.session_state.get("current_project", {}).get("id") == proj["id"]:
                        st.session_state.pop("current_project", None)
                    st.success(f"Deleted '{proj['name']}'")
                    st.rerun()

        # Select as active project
        if st.button(f"Open '{proj['name']}'", key=f"open_{proj['id']}"):
            # Clear old config keys so stale values don't leak between projects
            for k in list(CONFIG_DEFAULTS.keys()):
                st.session_state.pop(k, None)
            for k in list(ECOM_CONFIG_DEFAULTS.keys()):
                st.session_state.pop(k, None)
            st.session_state.pop("_last_config", None)
            st.session_state.pop("_last_ecom_config", None)
            st.session_state["current_project"] = proj
            st.switch_page("pages/3_Scenarios.py")

        # Sharing management (owners only)
        if role == "owner":
            with st.expander("Manage Sharing", expanded=False):
                # Share with a new user
                with st.form(f"share_form_{proj['id']}"):
                    share_cols = st.columns([3, 1, 1])
                    with share_cols[0]:
                        share_email = st.text_input("User email", key=f"share_email_{proj['id']}")
                    with share_cols[1]:
                        share_role = st.selectbox("Role", ["viewer", "editor"], key=f"share_role_{proj['id']}")
                    with share_cols[2]:
                        share_btn = st.form_submit_button("Share")
                    if share_btn and share_email:
                        target = lookup_user_by_email(share_email.strip())
                        if not target:
                            st.error("User not found.")
                        elif target["id"] == user["id"]:
                            st.warning("You can't share with yourself.")
                        else:
                            result = share_project(proj["id"], user["id"], target["id"], share_role)
                            if result:
                                st.success(f"Shared with {share_email.strip()} as {share_role}.")
                                st.rerun()

                # Current shares
                shares = list_project_shares(proj["id"])
                if shares:
                    st.markdown("**Current shares:**")
                    for s in shares:
                        profile = s.get("profiles", {})
                        s_email = profile.get("email", "?")
                        s_name = profile.get("display_name", "")
                        s_label = f"{s_name} ({s_email})" if s_name else s_email

                        sc1, sc2, sc3 = st.columns([3, 1, 1])
                        with sc1:
                            st.write(f"{s_label} — **{s['role']}**")
                        with sc2:
                            new_role = "editor" if s["role"] == "viewer" else "viewer"
                            if st.button(f"→ {new_role}", key=f"chrole_{s['id']}"):
                                update_share_role(s["id"], new_role)
                                st.rerun()
                        with sc3:
                            if st.button("Revoke", key=f"revoke_{s['id']}", type="secondary"):
                                revoke_share(s["id"])
                                st.rerun()
                else:
                    st.caption("Not shared with anyone.")

        st.markdown("---")
