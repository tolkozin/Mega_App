"""CRUD operations for projects and scenarios using Supabase."""

import streamlit as st
from db.client import get_supabase
from core.model_config import ModelConfig


# ===================== PROJECTS =====================

def list_projects(user_id: str) -> list[dict]:
    """List all projects for a user."""
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
    """List all scenarios for a project."""
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
