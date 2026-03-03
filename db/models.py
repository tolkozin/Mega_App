"""CRUD operations for projects, scenarios, and sharing using Supabase."""

import streamlit as st
from db.client import get_supabase
from core.model_config import ModelConfig


# ===================== PROJECTS =====================

def list_projects(user_id: str) -> list[dict]:
    """List all projects owned by a user."""
    sb = get_supabase()
    if not sb:
        return []
    res = sb.table("projects").select("*").eq("user_id", user_id).order("created_at").execute()
    return res.data or []


def create_project(user_id: str, name: str, description: str = "") -> dict | None:
    """Create a new project. Returns the created project dict."""
    sb = get_supabase()
    if not sb:
        return None
    res = sb.table("projects").insert({
        "user_id": user_id,
        "name": name,
        "description": description,
    }).execute()
    return res.data[0] if res.data else None


def delete_project(project_id: str):
    """Delete a project (cascades to scenarios via DB FK)."""
    sb = get_supabase()
    if not sb:
        return
    sb.table("projects").delete().eq("id", project_id).execute()


def get_project(project_id: str) -> dict | None:
    """Get a single project by ID."""
    sb = get_supabase()
    if not sb:
        return None
    res = sb.table("projects").select("*").eq("id", project_id).single().execute()
    return res.data


# ===================== SCENARIOS =====================

def list_scenarios(user_id: str, project_id: str) -> list[dict]:
    """List all scenarios for a project (filtered by user_id)."""
    sb = get_supabase()
    if not sb:
        return []
    res = (sb.table("scenarios")
           .select("id, name, notes, created_at")
           .eq("user_id", user_id)
           .eq("project_id", project_id)
           .order("created_at")
           .execute())
    return res.data or []


def list_scenarios_for_project(project_id: str) -> list[dict]:
    """List all scenarios for a project (RLS controls visibility for shared users)."""
    sb = get_supabase()
    if not sb:
        return []
    res = (sb.table("scenarios")
           .select("id, name, notes, created_at, user_id")
           .eq("project_id", project_id)
           .order("created_at")
           .execute())
    return res.data or []


def save_scenario(user_id: str, project_id: str, name: str, config: ModelConfig, notes: str = "") -> dict | None:
    """Save a scenario config as JSONB. Returns the created scenario dict."""
    sb = get_supabase()
    if not sb:
        return None
    res = sb.table("scenarios").insert({
        "user_id": user_id,
        "project_id": project_id,
        "name": name,
        "notes": notes,
        "config": config.to_dict(),
    }).execute()
    return res.data[0] if res.data else None


def load_scenario_config(scenario_id: str) -> ModelConfig | None:
    """Load a scenario's config from DB. Returns ModelConfig or None."""
    sb = get_supabase()
    if not sb:
        return None
    res = sb.table("scenarios").select("config").eq("id", scenario_id).single().execute()
    if res.data and res.data.get("config"):
        return ModelConfig.from_dict(res.data["config"])
    return None


def delete_scenario(scenario_id: str):
    """Delete a single scenario."""
    sb = get_supabase()
    if not sb:
        return
    sb.table("scenarios").delete().eq("id", scenario_id).execute()


def update_scenario(scenario_id: str, name: str = None, notes: str = None, config: ModelConfig = None):
    """Update scenario fields."""
    sb = get_supabase()
    if not sb:
        return
    data = {}
    if name is not None:
        data["name"] = name
    if notes is not None:
        data["notes"] = notes
    if config is not None:
        data["config"] = config.to_dict()
    if data:
        sb.table("scenarios").update(data).eq("id", scenario_id).execute()


# ===================== SHARING =====================

def lookup_user_by_email(email: str) -> dict | None:
    """Find a user profile by email (for sharing)."""
    sb = get_supabase()
    if not sb:
        return None
    res = (sb.table("profiles")
           .select("id, email, display_name")
           .eq("email", email)
           .execute())
    return res.data[0] if res.data else None


def share_project(project_id: str, owner_id: str, shared_with_id: str, role: str = "viewer") -> dict | None:
    """Share a project with another user. Returns the share record or None."""
    sb = get_supabase()
    if not sb:
        return None
    try:
        res = sb.table("project_shares").insert({
            "project_id": project_id,
            "owner_id": owner_id,
            "shared_with_id": shared_with_id,
            "role": role,
        }).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        st.error(f"Failed to share project: {e}")
        return None


def revoke_share(share_id: str):
    """Remove a project share."""
    sb = get_supabase()
    if not sb:
        return
    sb.table("project_shares").delete().eq("id", share_id).execute()


def update_share_role(share_id: str, role: str):
    """Update the role of an existing share."""
    sb = get_supabase()
    if not sb:
        return
    sb.table("project_shares").update({"role": role}).eq("id", share_id).execute()


def list_project_shares(project_id: str) -> list[dict]:
    """List all shares for a project (for the owner's management UI)."""
    sb = get_supabase()
    if not sb:
        return []
    res = (sb.table("project_shares")
           .select("id, shared_with_id, role, created_at, profiles!project_shares_shared_with_id_fkey(email, display_name)")
           .eq("project_id", project_id)
           .order("created_at")
           .execute())
    return res.data or []


def list_shared_with_me(user_id: str) -> list[dict]:
    """List projects shared with a user (with role and owner info)."""
    sb = get_supabase()
    if not sb:
        return []
    res = (sb.table("project_shares")
           .select("id, role, project_id, projects(id, name, description, created_at, user_id), profiles!project_shares_owner_id_fkey(email, display_name)")
           .eq("shared_with_id", user_id)
           .order("created_at")
           .execute())
    return res.data or []


def get_user_role_for_project(user_id: str, project_id: str) -> str | None:
    """Determine the user's role for a project: 'owner', 'editor', 'viewer', or None."""
    sb = get_supabase()
    if not sb:
        return None
    # Check if owner
    proj = sb.table("projects").select("user_id").eq("id", project_id).single().execute()
    if proj.data and proj.data.get("user_id") == user_id:
        return "owner"
    # Check shares
    share = (sb.table("project_shares")
             .select("role")
             .eq("project_id", project_id)
             .eq("shared_with_id", user_id)
             .execute())
    if share.data:
        return share.data[0]["role"]
    return None


def list_all_user_projects(user_id: str) -> list[dict]:
    """List owned + shared projects for a user, each annotated with _role and _owner_name."""
    owned = list_projects(user_id)
    for p in owned:
        p["_role"] = "owner"
        p["_owner_name"] = None

    shared_records = list_shared_with_me(user_id)
    shared = []
    for rec in shared_records:
        proj_data = rec.get("projects")
        if not proj_data:
            continue
        proj = dict(proj_data)
        proj["_role"] = rec["role"]
        owner_profile = rec.get("profiles")
        proj["_owner_name"] = owner_profile.get("display_name") or owner_profile.get("email") if owner_profile else "Unknown"
        shared.append(proj)

    return owned + shared
