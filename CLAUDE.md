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
│   ├── auth.py             # login, register, require_auth, logout
│   ├── models.py           # CRUD: projects, scenarios (Supabase)
│   └── schema.sql          # SQL for Supabase: profiles, projects, scenarios + RLS + triggers
└── pages/
    ├── 0_Login.py          # Login / Register (skipped in local mode)
    ├── 1_Dashboard.py      # Main dashboard (sidebar → engine → charts + reports)
    ├── 2_Projects.py       # Project management
    └── 3_Scenarios.py      # Scenario management within a project
```

## Key Design Decisions
- **ModelConfig dataclass**: All 67+ parameters serializable as JSONB for Supabase storage
- **Pure engine**: `run_model(config, sens_params)` has zero Streamlit dependencies
- **Graceful degradation**: Without `.env` Supabase credentials, runs in local mode (no auth, JSON scenarios)
- **Local scenarios**: Still supported via `saved_scenarios/` JSON files in sidebar

## Running
- **Local mode**: `streamlit run app.py` (no `.env` needed)
- **SaaS mode**: Create `.env` from `.env.example`, run `db/schema.sql` in Supabase SQL Editor

## User Preferences
- Language: Russian (UI descriptions in Russian, labels in English)
- Prefers comprehensive financial modeling with SaaS metrics
- Values milestone tracking and investor-ready outputs
