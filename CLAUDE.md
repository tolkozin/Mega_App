# Mega App — SaaS Financial Dashboard

## Project Overview
- **Origin**: Forked from Awesome_dashboard_main (subscription app financial model)
- **Goal**: Multi-user SaaS financial modeling tool with support for **subscription** and **e-commerce** product types
- **Stack**: Python, Streamlit, Pandas, NumPy, Plotly, Supabase (Auth + PostgreSQL)

## Architecture (Modularized)

```
Mega_App/
├── app.py                  # Entry point (redirect to Login or Dashboard)
├── core/                   # Subscription financial model (НЕ ТРОГАТЬ)
│   ├── model_config.py     # ModelConfig + PhaseConfig dataclasses (all 67+ params)
│   ├── engine.py           # run_model(config, sens_params) — pure function, no Streamlit
│   └── scenarios.py        # build_scenario_params(config) → base/pess/opt dicts
├── ecommerce/              # E-commerce financial model (parallel to core/)
│   ├── model_config.py     # EcomConfig + EcomPhaseConfig dataclasses
│   ├── engine.py           # run_ecom_model(config, sens_params) → (df, milestones)
│   ├── scenarios.py        # build_ecom_scenario_params(config) → base/pess/opt dicts
│   └── sidebar.py          # render_ecom_sidebar() → EcomConfig
├── ui/
│   ├── sidebar.py          # render_sidebar() → ModelConfig (subscription, all expanders)
│   ├── charts.py           # 4-tab chart layout + Monte Carlo (subscription)
│   ├── executive.py        # Milestones, Key Metrics, Cost Breakdown (subscription)
│   ├── reports.py          # Financial Reports (subscription)
│   ├── ecom_charts.py      # 4-tab charts + Monte Carlo (e-commerce)
│   ├── ecom_executive.py   # KPI cards, milestones, scenario comparison (e-commerce)
│   ├── ecom_reports.py     # P&L, Cash Flow, Key Metrics tables (e-commerce)
│   ├── export.py           # CSV export buttons (shared)
│   └── components.py       # add_phase_lines, add_milestone_markers, health_indicator, fmt_milestone (shared)
├── db/
│   ├── client.py           # Supabase client singleton (graceful fallback if not configured)
│   ├── auth.py             # Auth: login, register, require_auth, logout, password reset, token refresh
│   ├── session.py          # Cookie-based session persistence (extra-streamlit-components)
│   ├── models.py           # CRUD: projects, scenarios, sharing (Supabase) — supports both config types
│   └── schema.sql          # SQL: profiles, projects (product_type column), scenarios, project_shares + RLS + triggers
└── pages/
    ├── 0_Login.py          # Login / Register / Password Reset (skipped in local mode)
    ├── 1_Dashboard.py      # Routes by product_type: subscription → core modules, ecommerce → ecom modules
    ├── 2_Projects.py       # Project management + sharing UI (product_type selectbox on create)
    └── 3_Scenarios.py      # Scenario management (role-aware: owner/editor/viewer)
```

## Product Types
- **subscription** (default): SaaS subscription model with MRR, churn, cohorts, 67+ params
- **ecommerce**: E-commerce model with AOV, CPC, repeat purchases, COGS%, unit economics
- Product type is stored in `projects.product_type` column in DB
- Dashboard routes to the correct engine/UI based on current project's type
- Each type has its own: config dataclass, engine, sidebar, charts, reports, executive dashboard

## E-commerce Model (ecommerce/)
- **EcomConfig**: 3-phase config with per-phase: AOV, CPC, click_to_purchase, repeat_rate, COGS%, return_rate, discount_rate, organic_pct
- **Engine**: Monthly model: Traffic → Cohorts → Revenue → Unit Economics → OpEx → P&L → Metrics
- **Metrics**: CAC, LTV, LTV/CAC, ROAS, Gross Margin, AOV trend, CAC Payback, ROI, Burn Rate, Runway
- **Milestones**: break_even, cumulative_break_even, cf_positive, runway_out, customer thresholds, revenue thresholds
- **Sensitivity**: conv, cpc, aov, organic — same 3-scenario (base/pess/opt) + Monte Carlo pattern

## Key Design Decisions
- **ModelConfig dataclass**: All 67+ parameters serializable as JSONB for Supabase storage
- **EcomConfig dataclass**: Parallel structure for e-commerce, also serializable as JSONB
- **Pure engine**: Both `run_model()` and `run_ecom_model()` have zero Streamlit dependencies
- **Graceful degradation**: Without `.env` Supabase credentials, runs in local mode (no auth, JSON scenarios)
- **Local scenarios**: Still supported via `saved_scenarios/` JSON files in sidebar
- **Parallel modules**: Subscription code (core/) is never modified by e-commerce changes

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

## DB Migration for E-commerce
Run in Supabase SQL Editor:
```sql
ALTER TABLE public.projects ADD COLUMN product_type TEXT NOT NULL DEFAULT 'subscription' CHECK (product_type IN ('subscription', 'ecommerce'));
```

## Running
- **Local mode**: `streamlit run app.py` (no `.env` needed)
- **SaaS mode**: Create `.env` from `.env.example`, run `db/schema.sql` in Supabase SQL Editor

## User Preferences
- Language: Russian (UI descriptions in Russian, labels in English)
- Prefers comprehensive financial modeling with SaaS metrics
- Values milestone tracking and investor-ready outputs
