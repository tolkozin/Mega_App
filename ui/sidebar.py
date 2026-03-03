"""Sidebar rendering — all expanders, returns ModelConfig.

Widget-conflict-free pattern: defaults are seeded into st.session_state
BEFORE widgets render; widgets use only key= (no value=).
Scenario management is DB-backed via db.models.
"""

import streamlit as st

from core.model_config import ModelConfig, PhaseConfig
from db.client import is_supabase_configured
from db.auth import get_current_user
from db.models import (
    list_scenarios, list_all_user_projects, save_scenario,
    load_scenario_config, delete_scenario,
)


# ===================== DEFAULTS =====================

CONFIG_DEFAULTS = {
    "cfg_total_months": 60, "cfg_phase1_dur": 3, "cfg_phase2_dur": 3,
    "cfg_sens_conv": 0, "cfg_sens_churn": 0, "cfg_sens_cpi": 0, "cfg_sens_organic": 0,
    "cfg_scenario_bound": 20, "cfg_mc_enabled": False, "mc_iter": 200, "mc_var": 20.0,
    "cfg_corp_tax": 1.0, "cfg_store_split": 50, "cfg_app_store_comm": 15.0,
    "cfg_web_comm_pct": 3.5, "cfg_web_comm_fixed": 0.50, "cfg_bank_fee": 1.0,
    "cfg_p1_inv": 100000.0, "cfg_p1_sal": 17475.0, "cfg_p1_misc": 8419.0,
    "cfg_p1_ad": 0.0, "cfg_p1_cpi": 7.50, "cfg_p1_ct": 0.0, "cfg_p1_cp": 0.0,
    "cfg_p2_inv": 0.0, "cfg_p2_sal": 3600.0, "cfg_p2_misc": 750.0,
    "cfg_p2_ad": 5000.0, "cfg_p2_cpi": 7.50, "cfg_p2_ct": 20.0, "cfg_p2_cp": 20.0,
    "cfg_p3_inv": 0.0, "cfg_p3_sal": 64800.0, "cfg_p3_misc": 13500.0,
    "cfg_p3_ad": 150000.0, "cfg_p3_cpi": 7.50, "cfg_p3_ct": 25.0, "cfg_p3_cp": 25.0,
    "p2_adg_mode": "Percentage (%)", "p2_adg_pct": 5.0, "p2_adg_abs": 5000.0, "p2_cpid": 1.0,
    "p3_adg_mode": "Percentage (%)", "p3_adg_pct": 5.0, "p3_adg_abs": 5000.0, "p3_cpid": 1.0,
    "cfg_org_start": 0.0,
    "p1_ogm": "Percentage (%)", "p1_ogp": 0.0, "p1_oga": 0.0, "p1_oct": 0.0, "p1_ocp": 0.0, "p1_osp": 0.0,
    "p2_ogm": "Percentage (%)", "p2_ogp": 10.0, "p2_oga": 50.0, "p2_oct": 25.0, "p2_ocp": 25.0, "p2_osp": 500.0,
    "p3_ogm": "Percentage (%)", "p3_ogp": 15.0, "p3_oga": 500.0, "p3_oct": 35.0, "p3_ocp": 35.0, "p3_osp": 2000.0,
    "pr_w": 4.99, "pr_m": 7.99, "pr_a": 49.99, "pp_pr": False,
    "p2_pw": 4.99, "p2_pm": 7.99, "p2_pa": 49.99,
    "p3_pw": 4.99, "p3_pm": 7.99, "p3_pa": 49.99,
    "mx_w": 0.0, "mx_m": 48.0, "mx_a": 52.0, "pp_mx": False,
    "p2_mw": 0.0, "p2_mm": 48.0, "p2_ma": 52.0,
    "p3_mw": 0.0, "p3_mm": 48.0, "p3_ma": 52.0,
    "cfg_wk_cancel": 15.0, "cfg_mo_churn": 10.0, "cfg_yr_nonrenew": 30.0,
    "cfg_p2_churn_mult": 1.5, "cfg_p3_churn_mult": 1.0,
    "cfg_trial_days": 7, "cfg_refund_rate": 2.0, "cfg_cogs_global": 0.10,
    "pp_cogs": False, "p1_cogs": 0.05, "p2_cogs": 0.15, "p3_cogs": 0.08,
    "cfg_upgrade_rate": 2.0, "cfg_downgrade_rate": 5.0,
}


def _seed_session_state():
    """Seed session_state with defaults for keys that don't exist yet."""
    for key, default in CONFIG_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default


def config_to_session_state(config: ModelConfig):
    """Map all ModelConfig fields back into widget keys in session_state.

    Call this when loading a saved scenario so that sidebar widgets
    pick up the loaded values on the next rerun.
    """
    st.session_state["cfg_total_months"] = config.total_months
    st.session_state["cfg_phase1_dur"] = config.phase1_dur
    st.session_state["cfg_phase2_dur"] = config.phase2_dur

    # Sensitivity
    st.session_state["cfg_sens_conv"] = int(config.sens_conv)
    st.session_state["cfg_sens_churn"] = int(config.sens_churn)
    st.session_state["cfg_sens_cpi"] = int(config.sens_cpi)
    st.session_state["cfg_sens_organic"] = int(config.sens_organic)
    st.session_state["cfg_scenario_bound"] = int(config.scenario_bound)
    st.session_state["cfg_mc_enabled"] = config.mc_enabled
    st.session_state["mc_iter"] = config.mc_iterations
    st.session_state["mc_var"] = config.mc_variance

    # Taxes & Fees
    st.session_state["cfg_corp_tax"] = config.corporate_tax
    st.session_state["cfg_store_split"] = int(config.store_split)
    st.session_state["cfg_app_store_comm"] = config.app_store_comm
    st.session_state["cfg_web_comm_pct"] = config.web_comm_pct
    st.session_state["cfg_web_comm_fixed"] = config.web_comm_fixed
    st.session_state["cfg_bank_fee"] = config.bank_fee

    # Retention & Churn
    st.session_state["cfg_wk_cancel"] = config.weekly_cancel_rate
    st.session_state["cfg_mo_churn"] = config.monthly_churn_rate
    st.session_state["cfg_yr_nonrenew"] = config.annual_non_renewal
    st.session_state["cfg_p2_churn_mult"] = config.phase2.churn_mult
    st.session_state["cfg_p3_churn_mult"] = config.phase3.churn_mult

    # Trial, Refunds & COGS
    st.session_state["cfg_trial_days"] = config.trial_days
    st.session_state["cfg_refund_rate"] = config.refund_rate
    st.session_state["cfg_cogs_global"] = config.phase1.cogs  # fallback
    # Detect per-phase COGS
    cogs_values = [config.phase1.cogs, config.phase2.cogs, config.phase3.cogs]
    all_same = len(set(cogs_values)) == 1
    st.session_state["pp_cogs"] = not all_same
    st.session_state["p1_cogs"] = config.phase1.cogs
    st.session_state["p2_cogs"] = config.phase2.cogs
    st.session_state["p3_cogs"] = config.phase3.cogs

    # Expansion
    st.session_state["cfg_upgrade_rate"] = config.upgrade_rate
    st.session_state["cfg_downgrade_rate"] = config.downgrade_rate

    # Organic
    st.session_state["cfg_org_start"] = config.starting_organic

    # Per-phase configs
    for prefix, phase in [("p1", config.phase1), ("p2", config.phase2), ("p3", config.phase3)]:
        pfx = "cfg_" + prefix
        st.session_state[f"{pfx}_inv"] = phase.investment
        st.session_state[f"{pfx}_sal"] = phase.salaries_total
        st.session_state[f"{pfx}_misc"] = phase.misc_total
        st.session_state[f"{pfx}_ad"] = phase.ad_budget
        st.session_state[f"{pfx}_cpi"] = phase.cpi
        st.session_state[f"{pfx}_ct"] = phase.conv_trial
        st.session_state[f"{pfx}_cp"] = phase.conv_paid

    # Ad Budget Growth (phases 2 & 3 only)
    st.session_state["p2_adg_mode"] = config.phase2.ad_growth_mode
    st.session_state["p2_adg_pct"] = config.phase2.ad_growth_pct
    st.session_state["p2_adg_abs"] = config.phase2.ad_growth_abs
    st.session_state["p2_cpid"] = config.phase2.cpi_degradation
    st.session_state["p3_adg_mode"] = config.phase3.ad_growth_mode
    st.session_state["p3_adg_pct"] = config.phase3.ad_growth_pct
    st.session_state["p3_adg_abs"] = config.phase3.ad_growth_abs
    st.session_state["p3_cpid"] = config.phase3.cpi_degradation

    # Organic per-phase
    for prefix, phase in [("p1", config.phase1), ("p2", config.phase2), ("p3", config.phase3)]:
        st.session_state[f"{prefix}_ogm"] = phase.organic_growth_mode
        st.session_state[f"{prefix}_ogp"] = phase.organic_growth_pct
        st.session_state[f"{prefix}_oga"] = phase.organic_growth_abs
        st.session_state[f"{prefix}_oct"] = phase.organic_conv_trial
        st.session_state[f"{prefix}_ocp"] = phase.organic_conv_paid
        st.session_state[f"{prefix}_osp"] = phase.organic_spend

    # Pricing — default = phase1
    st.session_state["pr_w"] = config.phase1.price_weekly
    st.session_state["pr_m"] = config.phase1.price_monthly
    st.session_state["pr_a"] = config.phase1.price_annual

    # Detect per-phase pricing
    p1p = (config.phase1.price_weekly, config.phase1.price_monthly, config.phase1.price_annual)
    p2p = (config.phase2.price_weekly, config.phase2.price_monthly, config.phase2.price_annual)
    p3p = (config.phase3.price_weekly, config.phase3.price_monthly, config.phase3.price_annual)
    st.session_state["pp_pr"] = (p1p != p2p or p1p != p3p)
    st.session_state["p2_pw"] = config.phase2.price_weekly
    st.session_state["p2_pm"] = config.phase2.price_monthly
    st.session_state["p2_pa"] = config.phase2.price_annual
    st.session_state["p3_pw"] = config.phase3.price_weekly
    st.session_state["p3_pm"] = config.phase3.price_monthly
    st.session_state["p3_pa"] = config.phase3.price_annual

    # Mix — stored as fractions (0..1) in config, displayed as percentages (0..100) in widgets
    st.session_state["mx_w"] = config.phase1.mix_weekly * 100
    st.session_state["mx_m"] = config.phase1.mix_monthly * 100
    st.session_state["mx_a"] = config.phase1.mix_annual * 100

    # Detect per-phase mix
    p1m = (config.phase1.mix_weekly, config.phase1.mix_monthly, config.phase1.mix_annual)
    p2m = (config.phase2.mix_weekly, config.phase2.mix_monthly, config.phase2.mix_annual)
    p3m = (config.phase3.mix_weekly, config.phase3.mix_monthly, config.phase3.mix_annual)
    st.session_state["pp_mx"] = (p1m != p2m or p1m != p3m)
    st.session_state["p2_mw"] = config.phase2.mix_weekly * 100
    st.session_state["p2_mm"] = config.phase2.mix_monthly * 100
    st.session_state["p2_ma"] = config.phase2.mix_annual * 100
    st.session_state["p3_mw"] = config.phase3.mix_weekly * 100
    st.session_state["p3_mm"] = config.phase3.mix_monthly * 100
    st.session_state["p3_ma"] = config.phase3.mix_annual * 100


def render_sidebar() -> ModelConfig:
    """Render all sidebar widgets and return a ModelConfig built from their values."""

    # Seed defaults — prevents widget key conflicts on load
    _seed_session_state()

    # --- DB-backed Scenario Management ---
    user = get_current_user()
    project = st.session_state.get("current_project")

    if user and is_supabase_configured():
        with st.sidebar.expander("Scenario Management", expanded=False):
            # Project selector — only subscription projects
            all_projects = list_all_user_projects(user["id"])
            sub_projects = [p for p in all_projects if p.get("product_type", "subscription") == "subscription"]
            if not sub_projects:
                st.info("No subscription projects found.")
            else:
                proj_names = [p["name"] for p in sub_projects]
                # Pre-select current project if it exists
                default_idx = 0
                if project:
                    for i, p in enumerate(sub_projects):
                        if p["id"] == project.get("id"):
                            default_idx = i
                            break
                selected_proj_idx = st.selectbox(
                    "Project", range(len(proj_names)),
                    format_func=lambda i: proj_names[i],
                    index=default_idx, key="_scn_sub_proj",
                )
                sel_project = sub_projects[selected_proj_idx]

                # Save
                st.markdown("**Save Current**")
                save_name = st.text_input("Scenario Name", value="", key="_scn_save_name")
                save_notes = st.text_input("Notes (optional)", value="", key="_scn_save_notes")
                if st.button("Save", key="_scn_btn_save"):
                    last_cfg = st.session_state.get("_last_config")
                    if not last_cfg:
                        st.warning("Run the dashboard first to build a config.")
                    elif save_name.strip():
                        result = save_scenario(user["id"], sel_project["id"], save_name.strip(), last_cfg, save_notes.strip())
                        if result:
                            st.success(f"Saved: {save_name.strip()}")
                            st.rerun()
                        else:
                            st.error("Failed to save scenario.")
                    else:
                        st.warning("Enter a scenario name.")

                # Load / Delete
                st.markdown("---")
                st.markdown("**Load Saved**")
                scenarios = list_scenarios(user["id"], sel_project["id"])
                if scenarios:
                    sc_names = [s["name"] for s in scenarios]
                    load_idx = st.selectbox(
                        "Select Scenario", range(len(sc_names)),
                        format_func=lambda i: sc_names[i],
                        key="_scn_load_sel",
                    )
                    sel_sc = scenarios[load_idx]
                    lc1, lc2 = st.columns(2)
                    if lc1.button("Load", key="_scn_btn_load"):
                        loaded = load_scenario_config(sel_sc["id"], "subscription")
                        if loaded:
                            config_to_session_state(loaded)
                            st.success(f"Loaded: {sel_sc['name']}")
                            st.rerun()
                        else:
                            st.error("Failed to load scenario.")
                    if lc2.button("Delete", key="_scn_btn_del"):
                        delete_scenario(sel_sc["id"])
                        st.success(f"Deleted: {sel_sc['name']}")
                        st.rerun()

                    st.caption(f"Created: {sel_sc.get('created_at', '?')[:10]} | "
                               f"Notes: {sel_sc.get('notes') or '—'}")
                else:
                    st.info("No saved scenarios yet.")

    # --- General Settings ---
    with st.sidebar.expander("General Settings", expanded=True):
        total_months = st.number_input("Projection Horizon (months)", min_value=12, max_value=120, key="cfg_total_months",
            help="Горизонт моделирования. По умолчанию 60 месяцев (5 лет).")
        phase1_dur = st.number_input("Phase 1 Duration (months)", min_value=1, max_value=48, key="cfg_phase1_dur",
            help="Длительность фазы Pre-MVP — разработка, нет рекламы и пользователей.")
        phase2_dur = st.number_input("Phase 2 Duration (months)", min_value=1, max_value=48, key="cfg_phase2_dur",
            help="Длительность фазы MVP — мягкий запуск, первые пользователи.")
        phase3_dur = total_months - phase1_dur - phase2_dur
        if phase3_dur < 1:
            st.error(f"Phase 1 + Phase 2 должны быть < {total_months} месяцев!")
            st.stop()
        st.caption(f"Phase 3 (Scaling): {phase3_dur} мес.")

    # --- Scenario Sensitivity ---
    with st.sidebar.expander("Scenario Sensitivity"):
        st.markdown("**Per-Variable Sensitivity**")
        sens_conv = st.slider("Conversion Sensitivity %", -50, 50, key="cfg_sens_conv",
            help="Корректировка конверсий. + = лучше конверсии, - = хуже.")
        sens_churn = st.slider("Churn Sensitivity %", -50, 50, key="cfg_sens_churn",
            help="Корректировка оттока. + = больше отток (хуже), - = меньше (лучше).")
        sens_cpi = st.slider("CPI Sensitivity %", -50, 50, key="cfg_sens_cpi",
            help="Корректировка CPI. + = дороже установки, - = дешевле.")
        sens_organic = st.slider("Organic Sensitivity %", -50, 50, key="cfg_sens_organic",
            help="Корректировка органического роста. + = больше органики.")
        scenario_bound = st.slider("Scenario Bound %", 5, 50, key="cfg_scenario_bound",
            help="Границы пессимистичного/оптимистичного сценариев.")
        st.markdown("---")
        mc_enabled = st.checkbox("Monte Carlo Simulation", key="cfg_mc_enabled",
            help="Запустить N итераций с рандомизацией параметров.")
        if mc_enabled:
            mc_iterations = st.number_input("MC Iterations", min_value=50, max_value=1000, key="mc_iter")
            mc_variance = st.number_input("MC Max Variance %", min_value=5.0, max_value=50.0, key="mc_var")
        else:
            mc_iterations = st.session_state.get("mc_iter", 200)
            mc_variance = st.session_state.get("mc_var", 20.0)

    # --- Taxes & Payment Fees ---
    with st.sidebar.expander("Taxes & Payment Fees"):
        corporate_tax = st.number_input("Corporate Tax %", min_value=0.0, max_value=50.0, key="cfg_corp_tax",
            help="Налог на прибыль. 1% Грузия, 5% Армения, 3-10% Казахстан.")
        store_split = st.slider("Store vs Web % (Store)", 0, 100, key="cfg_store_split",
            help="Процент пользователей, покупающих через App Store.")
        app_store_comm = st.number_input("App Store Commission %", min_value=0.0, max_value=50.0, key="cfg_app_store_comm",
            help="Комиссия App Store. 15% по Small Business Program до $1M/год.")
        web_comm_pct = st.number_input("Web Commission %", min_value=0.0, max_value=20.0, key="cfg_web_comm_pct",
            help="Процентная комиссия Lemon Squeezy / Paddle.")
        web_comm_fixed = st.number_input("Web Fixed Fee per Txn ($)", min_value=0.0, max_value=5.0, key="cfg_web_comm_fixed",
            help="Фиксированная комиссия за каждую Web-транзакцию.")
        bank_fee = st.number_input("Banking Fee %", min_value=0.0, max_value=10.0, key="cfg_bank_fee",
            help="Комиссия банка за переводы и конвертации.")

    # --- Phase 1: Pre-MVP ---
    with st.sidebar.expander("Phase 1: Pre-MVP"):
        p1_investment = st.number_input("Phase 1 Investment ($)", min_value=0.0, key="cfg_p1_inv",
            help="Инвестиции в начале Phase 1.")
        p1_salaries_total = st.number_input("Phase 1 Total Salaries ($)", min_value=0.0, key="cfg_p1_sal",
            help="Общая сумма зарплат за всю фазу.")
        p1_misc_total = st.number_input("Phase 1 Total Misc Costs ($)", min_value=0.0, key="cfg_p1_misc",
            help="Прочие расходы за всю фазу.")
        p1_ad_budget = st.number_input("Phase 1 Monthly Ad Budget ($)", min_value=0.0, key="cfg_p1_ad",
            help="Рекламный бюджет в месяц. Обычно 0 на Pre-MVP.")
        p1_cpi = st.number_input("Phase 1 CPI ($)", min_value=0.01, key="cfg_p1_cpi",
            help="Стоимость одной установки.")
        p1_conv_trial = st.number_input("Phase 1 Conv. to Trial %", min_value=0.0, max_value=100.0, key="cfg_p1_ct",
            help="Конверсия установки в триал. На Pre-MVP обычно 0.")
        p1_conv_paid = st.number_input("Phase 1 Trial-to-Paid %", min_value=0.0, max_value=100.0, key="cfg_p1_cp",
            help="Конверсия триала в оплату. На Pre-MVP обычно 0.")

    # --- Phase 2: MVP ---
    with st.sidebar.expander("Phase 2: MVP"):
        p2_investment = st.number_input("Phase 2 Investment ($)", min_value=0.0, key="cfg_p2_inv",
            help="Дополнительные инвестиции в начале Phase 2.")
        p2_salaries_total = st.number_input("Phase 2 Total Salaries ($)", min_value=0.0, key="cfg_p2_sal",
            help="Общая сумма зарплат за фазу MVP.")
        p2_misc_total = st.number_input("Phase 2 Total Misc Costs ($)", min_value=0.0, key="cfg_p2_misc",
            help="Прочие расходы за фазу MVP.")
        p2_ad_budget = st.number_input("Phase 2 Monthly Ad Budget ($)", min_value=0.0, key="cfg_p2_ad",
            help="Стартовый рекламный бюджет на MVP.")
        p2_cpi = st.number_input("Phase 2 CPI ($)", min_value=0.01, key="cfg_p2_cpi",
            help="Стоимость установки на этапе MVP.")
        p2_conv_trial = st.number_input("Phase 2 Conv. to Trial %", min_value=0.0, max_value=100.0, key="cfg_p2_ct",
            help="Конверсия в триал на MVP.")
        p2_conv_paid = st.number_input("Phase 2 Trial-to-Paid %", min_value=0.0, max_value=100.0, key="cfg_p2_cp",
            help="Конверсия в оплату на MVP.")

    # --- Phase 3: Scaling ---
    with st.sidebar.expander("Phase 3: Scaling"):
        p3_investment = st.number_input("Phase 3 Investment ($)", min_value=0.0, key="cfg_p3_inv",
            help="Дополнительные инвестиции в начале Phase 3.")
        p3_salaries_total = st.number_input("Phase 3 Total Salaries ($)", min_value=0.0, key="cfg_p3_sal",
            help="Общая сумма зарплат за фазу масштабирования.")
        p3_misc_total = st.number_input("Phase 3 Total Misc Costs ($)", min_value=0.0, key="cfg_p3_misc",
            help="Прочие расходы за фазу масштабирования.")
        p3_ad_budget = st.number_input("Phase 3 Monthly Ad Budget ($)", min_value=0.0, key="cfg_p3_ad",
            help="Стартовый рекламный бюджет на этапе масштабирования.")
        p3_cpi = st.number_input("Phase 3 CPI ($)", min_value=0.01, key="cfg_p3_cpi",
            help="Стоимость установки на зрелом продукте.")
        p3_conv_trial = st.number_input("Phase 3 Conv. to Trial %", min_value=0.0, max_value=100.0, key="cfg_p3_ct",
            help="Конверсия в триал на зрелом продукте.")
        p3_conv_paid = st.number_input("Phase 3 Trial-to-Paid %", min_value=0.0, max_value=100.0, key="cfg_p3_cp",
            help="Конверсия в оплату на зрелом продукте.")

    # --- Ad Budget Growth ---
    with st.sidebar.expander("Ad Budget Growth"):
        st.markdown("**Phase 2: MVP**")
        p2_ad_growth_mode = st.radio("P2 Growth Mode", ["Percentage (%)", "Absolute ($)"], key="p2_adg_mode",
            help="Как растёт рекламный бюджет на MVP.")
        if p2_ad_growth_mode == "Percentage (%)":
            p2_ad_growth_pct = st.number_input("P2 MoM Growth %", min_value=0.0, max_value=100.0, key="p2_adg_pct")
            p2_ad_growth_abs = 0.0
        else:
            p2_ad_growth_abs = st.number_input("P2 MoM Growth ($)", min_value=0.0, key="p2_adg_abs")
            p2_ad_growth_pct = 0.0
        p2_cpi_deg = st.number_input("P2 CPI Degradation %", min_value=0.0, max_value=10.0, key="p2_cpid",
            help="Рост CPI за каждые +$1000 к бюджету на MVP.")

        st.markdown("**Phase 3: Scaling**")
        p3_ad_growth_mode = st.radio("P3 Growth Mode", ["Percentage (%)", "Absolute ($)"], key="p3_adg_mode",
            help="Как растёт рекламный бюджет на Scaling.")
        if p3_ad_growth_mode == "Percentage (%)":
            p3_ad_growth_pct = st.number_input("P3 MoM Growth %", min_value=0.0, max_value=100.0, key="p3_adg_pct")
            p3_ad_growth_abs = 0.0
        else:
            p3_ad_growth_abs = st.number_input("P3 MoM Growth ($)", min_value=0.0, key="p3_adg_abs")
            p3_ad_growth_pct = 0.0
        p3_cpi_deg = st.number_input("P3 CPI Degradation %", min_value=0.0, max_value=10.0, key="p3_cpid",
            help="Рост CPI за каждые +$1000 к бюджету на Scaling.")

    # --- Organic Acquisition ---
    with st.sidebar.expander("Organic Acquisition"):
        starting_organic = st.number_input("Starting Organic Traffic", min_value=0.0, key="cfg_org_start",
            help="Начальное количество органических посетителей в месяц.")

        st.markdown("**Phase 1: Pre-MVP**")
        p1_organic_growth_mode = st.radio("P1 Organic Growth", ["Percentage (%)", "Absolute (users)"], key="p1_ogm",
            help="Рост органики на Pre-MVP. Обычно 0.")
        if p1_organic_growth_mode == "Percentage (%)":
            p1_organic_growth_pct = st.number_input("P1 Organic MoM %", min_value=0.0, max_value=200.0, key="p1_ogp")
            p1_organic_growth_abs = 0.0
        else:
            p1_organic_growth_abs = st.number_input("P1 Organic MoM (users)", min_value=0.0, key="p1_oga")
            p1_organic_growth_pct = 0.0
        p1_organic_conv_trial = st.number_input("P1 Organic Conv Trial %", min_value=0.0, max_value=100.0, key="p1_oct")
        p1_organic_conv_paid = st.number_input("P1 Organic Conv Paid %", min_value=0.0, max_value=100.0, key="p1_ocp")
        p1_organic_spend = st.number_input("P1 Monthly Organic Spend ($)", min_value=0.0, key="p1_osp")

        st.markdown("**Phase 2: MVP**")
        p2_organic_growth_mode = st.radio("P2 Organic Growth", ["Percentage (%)", "Absolute (users)"], key="p2_ogm",
            help="Рост органики на MVP.")
        if p2_organic_growth_mode == "Percentage (%)":
            p2_organic_growth_pct = st.number_input("P2 Organic MoM %", min_value=0.0, max_value=200.0, key="p2_ogp")
            p2_organic_growth_abs = 0.0
        else:
            p2_organic_growth_abs = st.number_input("P2 Organic MoM (users)", min_value=0.0, key="p2_oga")
            p2_organic_growth_pct = 0.0
        p2_organic_conv_trial = st.number_input("P2 Organic Conv Trial %", min_value=0.0, max_value=100.0, key="p2_oct")
        p2_organic_conv_paid = st.number_input("P2 Organic Conv Paid %", min_value=0.0, max_value=100.0, key="p2_ocp")
        p2_organic_spend = st.number_input("P2 Monthly Organic Spend ($)", min_value=0.0, key="p2_osp")

        st.markdown("**Phase 3: Scaling**")
        p3_organic_growth_mode = st.radio("P3 Organic Growth", ["Percentage (%)", "Absolute (users)"], key="p3_ogm",
            help="Рост органики на Scaling.")
        if p3_organic_growth_mode == "Percentage (%)":
            p3_organic_growth_pct = st.number_input("P3 Organic MoM %", min_value=0.0, max_value=200.0, key="p3_ogp")
            p3_organic_growth_abs = 0.0
        else:
            p3_organic_growth_abs = st.number_input("P3 Organic MoM (users)", min_value=0.0, key="p3_oga")
            p3_organic_growth_pct = 0.0
        p3_organic_conv_trial = st.number_input("P3 Organic Conv Trial %", min_value=0.0, max_value=100.0, key="p3_oct")
        p3_organic_conv_paid = st.number_input("P3 Organic Conv Paid %", min_value=0.0, max_value=100.0, key="p3_ocp")
        p3_organic_spend = st.number_input("P3 Monthly Organic Spend ($)", min_value=0.0, key="p3_osp")

    # --- Subscription Mix & Pricing ---
    with st.sidebar.expander("Subscription Mix & Pricing"):
        st.markdown("**Default Pricing**")
        price_weekly = st.number_input("Price: Weekly ($)", min_value=0.0, key="pr_w")
        price_monthly = st.number_input("Price: Monthly ($)", min_value=0.0, key="pr_m")
        price_annual = st.number_input("Price: Annual ($)", min_value=0.0, key="pr_a")

        per_phase_pricing = st.checkbox("Customize pricing per phase", key="pp_pr")
        if per_phase_pricing:
            st.markdown("**Phase 2 Pricing**")
            p2_price_weekly = st.number_input("P2 Weekly ($)", min_value=0.0, key="p2_pw")
            p2_price_monthly = st.number_input("P2 Monthly ($)", min_value=0.0, key="p2_pm")
            p2_price_annual = st.number_input("P2 Annual ($)", min_value=0.0, key="p2_pa")
            st.markdown("**Phase 3 Pricing**")
            p3_price_weekly = st.number_input("P3 Weekly ($)", min_value=0.0, key="p3_pw")
            p3_price_monthly = st.number_input("P3 Monthly ($)", min_value=0.0, key="p3_pm")
            p3_price_annual = st.number_input("P3 Annual ($)", min_value=0.0, key="p3_pa")
        else:
            p2_price_weekly = p3_price_weekly = price_weekly
            p2_price_monthly = p3_price_monthly = price_monthly
            p2_price_annual = p3_price_annual = price_annual

        st.markdown("---")
        st.markdown("**Subscription Mix**")
        mix_weekly = st.number_input("Mix: Weekly %", min_value=0.0, max_value=100.0, key="mx_w")
        mix_monthly = st.number_input("Mix: Monthly %", min_value=0.0, max_value=100.0, key="mx_m")
        mix_annual = st.number_input("Mix: Annual %", min_value=0.0, max_value=100.0, key="mx_a")
        total_mix = mix_weekly + mix_monthly + mix_annual
        if total_mix > 0:
            mix_weekly /= total_mix
            mix_monthly /= total_mix
            mix_annual /= total_mix
        else:
            mix_monthly = 1.0

        per_phase_mix = st.checkbox("Customize mix per phase", key="pp_mx")
        if per_phase_mix:
            st.markdown("**Phase 2 Mix**")
            p2_mix_weekly = st.number_input("P2 Weekly %", min_value=0.0, max_value=100.0, key="p2_mw")
            p2_mix_monthly = st.number_input("P2 Monthly %", min_value=0.0, max_value=100.0, key="p2_mm")
            p2_mix_annual = st.number_input("P2 Annual %", min_value=0.0, max_value=100.0, key="p2_ma")
            p2_total = p2_mix_weekly + p2_mix_monthly + p2_mix_annual
            if p2_total > 0:
                p2_mix_weekly /= p2_total; p2_mix_monthly /= p2_total; p2_mix_annual /= p2_total
            else:
                p2_mix_monthly = 1.0

            st.markdown("**Phase 3 Mix**")
            p3_mix_weekly = st.number_input("P3 Weekly %", min_value=0.0, max_value=100.0, key="p3_mw")
            p3_mix_monthly = st.number_input("P3 Monthly %", min_value=0.0, max_value=100.0, key="p3_mm")
            p3_mix_annual = st.number_input("P3 Annual %", min_value=0.0, max_value=100.0, key="p3_ma")
            p3_total = p3_mix_weekly + p3_mix_monthly + p3_mix_annual
            if p3_total > 0:
                p3_mix_weekly /= p3_total; p3_mix_monthly /= p3_total; p3_mix_annual /= p3_total
            else:
                p3_mix_monthly = 1.0
        else:
            p2_mix_weekly = p3_mix_weekly = mix_weekly
            p2_mix_monthly = p3_mix_monthly = mix_monthly
            p2_mix_annual = p3_mix_annual = mix_annual

    # --- Retention & Churn ---
    with st.sidebar.expander("Retention & Churn"):
        weekly_cancel_rate = st.number_input("Weekly Cancellation Rate %", min_value=0.0, max_value=100.0, key="cfg_wk_cancel",
            help="Процент недельных подписчиков, отменяющих каждую неделю.")
        monthly_churn_rate = st.number_input("Monthly Churn Rate %", min_value=0.0, max_value=100.0, key="cfg_mo_churn",
            help="Процент месячных подписчиков, уходящих каждый месяц.")
        annual_non_renewal = st.number_input("Annual Non-Renewal Rate %", min_value=0.0, max_value=100.0, key="cfg_yr_nonrenew",
            help="Процент годовых подписчиков, НЕ продлевающих через 12 месяцев.")
        st.markdown("**Churn Multiplier by Phase**")
        p2_churn_mult = st.number_input("Phase 2 Churn Multiplier", min_value=0.1, max_value=5.0, key="cfg_p2_churn_mult",
            help="Множитель оттока на MVP. 1.5 = отток на 50% выше базового.")
        p3_churn_mult = st.number_input("Phase 3 Churn Multiplier", min_value=0.1, max_value=5.0, key="cfg_p3_churn_mult",
            help="Множитель оттока на Scaling. 1.0 = базовый.")

    # --- Trial, Refunds & COGS ---
    with st.sidebar.expander("Trial, Refunds & COGS"):
        trial_days = st.number_input("Trial Duration (days)", min_value=0, max_value=90, key="cfg_trial_days",
            help="Длительность бесплатного триала. 0 = оплата сразу.")
        refund_rate = st.number_input("Refund Rate %", min_value=0.0, max_value=30.0, key="cfg_refund_rate",
            help="Процент возвратов от валовой выручки.")
        cogs_global = st.number_input("COGS per Active User ($)", min_value=0.0, key="cfg_cogs_global",
            help="Затраты на серверы/хостинг на одного активного пользователя в месяц.")
        per_phase_cogs = st.checkbox("Customize COGS per phase", key="pp_cogs")
        if per_phase_cogs:
            p1_cogs = st.number_input("P1 COGS ($)", min_value=0.0, key="p1_cogs",
                help="COGS на Pre-MVP.")
            p2_cogs = st.number_input("P2 COGS ($)", min_value=0.0, key="p2_cogs",
                help="COGS на MVP.")
            p3_cogs = st.number_input("P3 COGS ($)", min_value=0.0, key="p3_cogs",
                help="COGS на Scaling.")
        else:
            p1_cogs = p2_cogs = p3_cogs = cogs_global

    # --- Expansion & Contraction ---
    with st.sidebar.expander("Expansion & Contraction"):
        upgrade_rate = st.number_input("Monthly->Annual Upgrade %/mo", min_value=0.0, max_value=20.0, key="cfg_upgrade_rate",
            help="Процент месячных подписчиков, переходящих на годовой план.")
        downgrade_rate = st.number_input("Annual->Monthly Downgrade %/yr", min_value=0.0, max_value=50.0, key="cfg_downgrade_rate",
            help="Процент годовых подписчиков, переходящих на месячный план при продлении.")

    # ===================== BUILD ModelConfig =====================
    config = ModelConfig(
        total_months=total_months,
        phase1_dur=phase1_dur,
        phase2_dur=phase2_dur,
        sens_conv=sens_conv,
        sens_churn=sens_churn,
        sens_cpi=sens_cpi,
        sens_organic=sens_organic,
        scenario_bound=scenario_bound,
        mc_enabled=mc_enabled,
        mc_iterations=mc_iterations,
        mc_variance=mc_variance,
        corporate_tax=corporate_tax,
        store_split=store_split,
        app_store_comm=app_store_comm,
        web_comm_pct=web_comm_pct,
        web_comm_fixed=web_comm_fixed,
        bank_fee=bank_fee,
        weekly_cancel_rate=weekly_cancel_rate,
        monthly_churn_rate=monthly_churn_rate,
        annual_non_renewal=annual_non_renewal,
        trial_days=trial_days,
        refund_rate=refund_rate,
        upgrade_rate=upgrade_rate,
        downgrade_rate=downgrade_rate,
        starting_organic=starting_organic,
        phase1=PhaseConfig(
            investment=p1_investment, salaries_total=p1_salaries_total, misc_total=p1_misc_total,
            ad_budget=p1_ad_budget, cpi=p1_cpi, conv_trial=p1_conv_trial, conv_paid=p1_conv_paid,
            churn_mult=1.0,
            ad_growth_mode="Percentage (%)", ad_growth_pct=0.0, ad_growth_abs=0.0,
            cpi_degradation=0.0,
            organic_growth_mode=p1_organic_growth_mode,
            organic_growth_pct=p1_organic_growth_pct, organic_growth_abs=p1_organic_growth_abs,
            organic_conv_trial=p1_organic_conv_trial, organic_conv_paid=p1_organic_conv_paid,
            organic_spend=p1_organic_spend,
            price_weekly=price_weekly, price_monthly=price_monthly, price_annual=price_annual,
            mix_weekly=mix_weekly, mix_monthly=mix_monthly, mix_annual=mix_annual,
            cogs=p1_cogs,
        ),
        phase2=PhaseConfig(
            investment=p2_investment, salaries_total=p2_salaries_total, misc_total=p2_misc_total,
            ad_budget=p2_ad_budget, cpi=p2_cpi, conv_trial=p2_conv_trial, conv_paid=p2_conv_paid,
            churn_mult=p2_churn_mult,
            ad_growth_mode=p2_ad_growth_mode, ad_growth_pct=p2_ad_growth_pct, ad_growth_abs=p2_ad_growth_abs,
            cpi_degradation=p2_cpi_deg,
            organic_growth_mode=p2_organic_growth_mode,
            organic_growth_pct=p2_organic_growth_pct, organic_growth_abs=p2_organic_growth_abs,
            organic_conv_trial=p2_organic_conv_trial, organic_conv_paid=p2_organic_conv_paid,
            organic_spend=p2_organic_spend,
            price_weekly=p2_price_weekly, price_monthly=p2_price_monthly, price_annual=p2_price_annual,
            mix_weekly=p2_mix_weekly, mix_monthly=p2_mix_monthly, mix_annual=p2_mix_annual,
            cogs=p2_cogs,
        ),
        phase3=PhaseConfig(
            investment=p3_investment, salaries_total=p3_salaries_total, misc_total=p3_misc_total,
            ad_budget=p3_ad_budget, cpi=p3_cpi, conv_trial=p3_conv_trial, conv_paid=p3_conv_paid,
            churn_mult=p3_churn_mult,
            ad_growth_mode=p3_ad_growth_mode, ad_growth_pct=p3_ad_growth_pct, ad_growth_abs=p3_ad_growth_abs,
            cpi_degradation=p3_cpi_deg,
            organic_growth_mode=p3_organic_growth_mode,
            organic_growth_pct=p3_organic_growth_pct, organic_growth_abs=p3_organic_growth_abs,
            organic_conv_trial=p3_organic_conv_trial, organic_conv_paid=p3_organic_conv_paid,
            organic_spend=p3_organic_spend,
            price_weekly=p3_price_weekly, price_monthly=p3_price_monthly, price_annual=p3_price_annual,
            mix_weekly=p3_mix_weekly, mix_monthly=p3_mix_monthly, mix_annual=p3_mix_annual,
            cogs=p3_cogs,
        ),
    )

    # Stash config for scenario save
    st.session_state["_last_config"] = config

    return config
