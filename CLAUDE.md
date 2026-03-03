# Mega App — SaaS Financial Dashboard

## Project Overview
- **Origin**: Forked from Awesome_dashboard_main (subscription app financial model)
- **Goal**: Multi-user SaaS financial modeling tool
- **Stack**: Python, Streamlit, Pandas, NumPy, Plotly, Supabase (Auth + PostgreSQL)

## Architecture (Modularized)

```
Mega_App/
├── app.py                  # Entry point (redirect to Login or Dashboard)
├── core/
│   ├── model_config.py     # ModelConfig + PhaseConfig dataclasses (all 67+ params)
│   ├── engine.py           # run_model(config, sens_params) — pure function, no Streamlit
│   └── scenarios.py        # build_scenario_params(config) → base/pess/opt dicts
├── ui/
│   ├── sidebar.py          # render_sidebar() → ModelConfig (all expanders)
│   ├── charts.py           # 4-tab chart layout + Monte Carlo
│   ├── executive.py        # Milestones, Key Metrics, Cost Breakdown, Executive Dashboard
│   ├── reports.py          # Financial Reports (P&L, Cash Flow, Balance Sheet, Metrics, Summary)
│   ├── export.py           # CSV export buttons
│   └── components.py       # add_phase_lines, add_milestone_markers, health_indicator, fmt_milestone
├── db/
│   ├── client.py           # Supabase client singleton (graceful fallback if not configured)
│   ├── auth.py             # Auth: login, register, require_auth, logout, password reset, token refresh
│   ├── session.py          # Cookie-based session persistence (extra-streamlit-components)
│   ├── models.py           # CRUD: projects, scenarios, sharing (Supabase)
│   └── schema.sql          # SQL: profiles, projects, scenarios, project_shares + RLS + triggers
└── pages/
    ├── 0_Login.py          # Login / Register / Password Reset (skipped in local mode)
    ├── 1_Dashboard.py      # Main dashboard (sidebar → engine → charts + reports)
    ├── 2_Projects.py       # Project management + sharing UI
    └── 3_Scenarios.py      # Scenario management (role-aware: owner/editor/viewer)
```

## Key Design Decisions
- **ModelConfig dataclass**: All 67+ parameters serializable as JSONB for Supabase storage
- **Pure engine**: `run_model(config, sens_params)` has zero Streamlit dependencies
- **Graceful degradation**: Without `.env` Supabase credentials, runs in local mode (no auth, JSON scenarios)
- **Local scenarios**: Still supported via `saved_scenarios/` JSON files in sidebar

## Authentication & Sessions
- **Supabase Auth**: Email/password with JWT tokens
- **Session persistence**: Refresh tokens stored in browser cookies (`extra-streamlit-components`)
- **Token refresh**: Proactive refresh every 45 min; cookie-based restore on page reload
- **Password reset**: Via `sb.auth.reset_password_email()`, tab on Login page
- **Email verification**: If Supabase requires confirmation, registration shows verification message

## Project Sharing
- **Roles**: owner (full control), editor (CRUD scenarios), viewer (read-only)
- **Table**: `project_shares` with UNIQUE(project_id, shared_with_id)
- **RLS**: Projects/scenarios visible to owners + shared users; editors can modify scenarios
- **UI**: Owner manages shares via expander on Projects page (add/change role/revoke)
- **Functions**: `share_project()`, `revoke_share()`, `update_share_role()`, `list_project_shares()`, `list_shared_with_me()`, `get_user_role_for_project()`, `list_all_user_projects()`

## db/auth.py Functions
- `login_with_email(email, password)` — sign in + store cookie
- `register_with_email(email, password, display_name)` — register, handle email verification
- `refresh_access_token(refresh_token)` — exchange refresh for new access token
- `try_restore_session()` — restore from cookie when session_state empty
- `ensure_valid_token()` — proactive 45-min refresh
- `require_auth()` — guard with cookie restore before redirect
- `send_password_reset(email)` — send reset link
- `logout()` — sign out + clear cookie

## db/session.py Functions
- `save_session_to_cookie(user, refresh_token)` — persist to browser cookie
- `load_session_from_cookie()` — read cookie data
- `clear_session_cookie()` — remove on logout

## Running
- **Local mode**: `streamlit run app.py` (no `.env` needed)
- **SaaS mode**: Create `.env` from `.env.example`, run `db/schema.sql` in Supabase SQL Editor

## User Preferences
- Language: Russian (UI descriptions in Russian, labels in English)
- Prefers comprehensive financial modeling with SaaS metrics
- Values milestone tracking and investor-ready outputs
