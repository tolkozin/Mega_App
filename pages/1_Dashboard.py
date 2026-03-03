"""Main Dashboard page — routes between subscription and e-commerce models."""

import streamlit as st

st.set_page_config(page_title="Awesome Dashboard", layout="wide")

from db.client import is_supabase_configured
from db.auth import get_current_user, require_auth, logout

# Auth guard (skipped if Supabase not configured)
if is_supabase_configured():
    require_auth()

# User info in sidebar
user = get_current_user()
if user:
    st.sidebar.markdown(f"**{user['display_name']}** ({user['email']})")
    if st.sidebar.button("Logout"):
        logout()
        st.switch_page("pages/0_Login.py")
    st.sidebar.markdown("---")

# Determine product type from current project (default: subscription)
current_project = st.session_state.get("current_project")
product_type = "subscription"
if current_project:
    product_type = current_project.get("product_type", "subscription")

# ===================== E-COMMERCE DASHBOARD =====================
if product_type == "ecommerce":
    st.title("E-commerce Dashboard")
    if current_project:
        st.caption(f"Project: {current_project.get('name', '')}")

    # --- Sidebar: collect parameters into EcomConfig ---
    from ecommerce.sidebar import render_ecom_sidebar
    config = render_ecom_sidebar()

    # --- Run model for 3 scenarios ---
    from ecommerce.engine import run_ecom_model
    from ecommerce.scenarios import build_ecom_scenario_params

    scenarios = build_ecom_scenario_params(config)
    df_main, milestones_main = run_ecom_model(config, scenarios["base"])
    df_pessimistic, milestones_pess = run_ecom_model(config, scenarios["pessimistic"])
    df_optimistic, milestones_opt = run_ecom_model(config, scenarios["optimistic"])

    p1_end = config.phase1_dur
    p2_end = config.phase1_dur + config.phase2_dur

    # --- Global month filter ---
    st.header("Global Dashboard Filters")
    month_range = st.slider("Select Month Range", 1, config.total_months, (1, config.total_months),
        help="Фильтр по месяцам — влияет на все графики и отчёты.")
    start_m, end_m = month_range
    f_df = df_main[(df_main["Month"] >= start_m) & (df_main["Month"] <= end_m)]
    f_pess = df_pessimistic[(df_pessimistic["Month"] >= start_m) & (df_pessimistic["Month"] <= end_m)]
    f_opt = df_optimistic[(df_optimistic["Month"] >= start_m) & (df_optimistic["Month"] <= end_m)]

    # --- Milestones ---
    from ui.ecom_executive import render_ecom_milestones, render_ecom_key_metrics, render_ecom_cost_breakdown, render_ecom_executive_dashboard
    render_ecom_milestones(milestones_main)

    # --- Key Metrics ---
    render_ecom_key_metrics(f_df, config)

    # --- Cost Breakdown ---
    render_ecom_cost_breakdown(f_df)

    # --- Executive Dashboard ---
    render_ecom_executive_dashboard(f_df, f_pess, f_opt, milestones_main, milestones_pess, milestones_opt)

    # --- Charts ---
    st.markdown("---")
    from ui.ecom_charts import render_ecom_charts, render_ecom_monte_carlo
    render_ecom_charts(f_df, f_pess, f_opt, milestones_main, p1_end, p2_end, config)

    # --- Monte Carlo ---
    if config.mc_enabled:
        render_ecom_monte_carlo(config, scenarios["base"], start_m, end_m)

    # --- Financial Reports ---
    from ui.ecom_reports import render_ecom_reports
    render_ecom_reports(f_df, f_pess, f_opt, milestones_main, milestones_pess, milestones_opt)

    # --- Export ---
    from ui.export import render_export_section
    render_export_section(df_main, df_pessimistic, df_optimistic, milestones_main, milestones_pess, milestones_opt)

# ===================== SUBSCRIPTION DASHBOARD (original) =====================
else:
    st.title("Awesome Dashboard")
    if current_project:
        st.caption(f"Project: {current_project.get('name', '')}")

    # --- Sidebar: collect all parameters into ModelConfig ---
    from ui.sidebar import render_sidebar
    config = render_sidebar()

    # --- Run model for 3 scenarios ---
    from core.engine import run_model
    from core.scenarios import build_scenario_params

    scenarios = build_scenario_params(config)
    df_main, milestones_main, retention_main = run_model(config, scenarios["base"])
    df_pessimistic, milestones_pess, _ = run_model(config, scenarios["pessimistic"])
    df_optimistic, milestones_opt, _ = run_model(config, scenarios["optimistic"])

    # Store retention matrix for heatmap
    st.session_state["retention_main"] = retention_main

    p1_end = config.phase1_dur
    p2_end = config.phase1_dur + config.phase2_dur

    # --- Global month filter ---
    st.header("Global Dashboard Filters")
    month_range = st.slider("Select Month Range", 1, config.total_months, (1, config.total_months),
        help="Фильтр по месяцам — влияет на все графики и отчёты.")
    start_m, end_m = month_range
    f_df = df_main[(df_main["Month"] >= start_m) & (df_main["Month"] <= end_m)]
    f_pess = df_pessimistic[(df_pessimistic["Month"] >= start_m) & (df_pessimistic["Month"] <= end_m)]
    f_opt = df_optimistic[(df_optimistic["Month"] >= start_m) & (df_optimistic["Month"] <= end_m)]

    # --- Milestones ---
    from ui.executive import render_milestones, render_key_metrics, render_cost_breakdown, render_executive_dashboard
    render_milestones(milestones_main)

    # --- Key Metrics ---
    render_key_metrics(f_df, config)

    # --- Cost Breakdown ---
    render_cost_breakdown(f_df)

    # --- Executive Dashboard ---
    render_executive_dashboard(f_df, f_pess, f_opt, milestones_main, milestones_pess, milestones_opt)

    # --- Charts ---
    st.markdown("---")
    from ui.charts import render_charts, render_monte_carlo
    render_charts(f_df, f_pess, f_opt, milestones_main, p1_end, p2_end, config)

    # --- Monte Carlo ---
    if config.mc_enabled:
        render_monte_carlo(config, scenarios["base"], start_m, end_m)

    # --- Financial Reports ---
    from ui.reports import render_financial_reports
    render_financial_reports(f_df, f_pess, f_opt, milestones_main, milestones_pess, milestones_opt)

    # --- Export ---
    from ui.export import render_export_section
    render_export_section(df_main, df_pessimistic, df_optimistic, milestones_main, milestones_pess, milestones_opt)
