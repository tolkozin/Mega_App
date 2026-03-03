"""E-commerce sidebar rendering — all expanders, returns EcomConfig.

Widget-conflict-free pattern: defaults are seeded into st.session_state
BEFORE widgets render; widgets use only key= (no value=).
Scenario management is DB-backed via db.models.
"""

import streamlit as st

from ecommerce.model_config import EcomConfig, EcomPhaseConfig
from db.client import is_supabase_configured
from db.auth import get_current_user
from db.models import (
    list_scenarios, list_all_user_projects, save_scenario,
    load_scenario_config, delete_scenario,
)


# ===================== DEFAULTS =====================

ECOM_CONFIG_DEFAULTS = {
    "ecom_total_months": 36, "ecom_phase1_dur": 3, "ecom_phase2_dur": 6,
    # Phase 1
    "ecom_p1_aov": 45.0, "ecom_p1_repeat": 10.0, "ecom_p1_ordret": 1.2,
    "ecom_p1_cogs": 45.0, "ecom_p1_returns": 5.0, "ecom_p1_ad": 3000.0,
    "ecom_p1_cpc": 2.00, "ecom_p1_conv": 2.0, "ecom_p1_organic": 10.0, "ecom_p1_discount": 10.0,
    # Phase 2
    "ecom_p2_aov": 50.0, "ecom_p2_repeat": 20.0, "ecom_p2_ordret": 1.5,
    "ecom_p2_cogs": 40.0, "ecom_p2_returns": 5.0, "ecom_p2_ad": 8000.0,
    "ecom_p2_cpc": 1.50, "ecom_p2_conv": 3.0, "ecom_p2_organic": 20.0, "ecom_p2_discount": 5.0,
    # Phase 3
    "ecom_p3_aov": 55.0, "ecom_p3_repeat": 30.0, "ecom_p3_ordret": 2.0,
    "ecom_p3_cogs": 35.0, "ecom_p3_returns": 4.0, "ecom_p3_ad": 20000.0,
    "ecom_p3_cpc": 1.20, "ecom_p3_conv": 4.0, "ecom_p3_organic": 30.0, "ecom_p3_discount": 3.0,
    # Salaries & Costs
    "ecom_sal_base": 5000.0, "ecom_sal_growth": 3.0, "ecom_misc": 2000.0, "ecom_corp_tax": 1.0,
    # Sensitivity
    "ecom_sens_conv": 0, "ecom_sens_cpc": 0, "ecom_sens_aov": 0, "ecom_sens_organic": 0,
    "ecom_scenario_bound": 20, "ecom_mc_enabled": False, "ecom_mc_iter": 200, "ecom_mc_var": 20.0,
}


def _seed_ecom_session_state():
    """Seed session_state with ecom defaults for keys that don't exist yet."""
    for key, default in ECOM_CONFIG_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default


def ecom_config_to_session_state(config: EcomConfig):
    """Map all EcomConfig fields back into widget keys in session_state."""
    st.session_state["ecom_total_months"] = config.total_months
    st.session_state["ecom_phase1_dur"] = config.phase1_dur
    st.session_state["ecom_phase2_dur"] = config.phase2_dur

    # Per-phase configs
    for prefix, phase in [("ecom_p1", config.phase1), ("ecom_p2", config.phase2), ("ecom_p3", config.phase3)]:
        st.session_state[f"{prefix}_aov"] = phase.avg_order_value
        st.session_state[f"{prefix}_repeat"] = phase.repeat_purchase_rate
        st.session_state[f"{prefix}_ordret"] = phase.orders_per_returning
        st.session_state[f"{prefix}_cogs"] = phase.cogs_pct
        st.session_state[f"{prefix}_returns"] = phase.return_rate
        st.session_state[f"{prefix}_ad"] = phase.ad_budget
        st.session_state[f"{prefix}_cpc"] = phase.cpc
        st.session_state[f"{prefix}_conv"] = phase.click_to_purchase
        st.session_state[f"{prefix}_organic"] = phase.organic_pct
        st.session_state[f"{prefix}_discount"] = phase.discount_rate

    # Salaries & Costs
    st.session_state["ecom_sal_base"] = config.salaries_base
    st.session_state["ecom_sal_growth"] = config.salaries_growth
    st.session_state["ecom_misc"] = config.misc_costs
    st.session_state["ecom_corp_tax"] = config.corporate_tax

    # Sensitivity
    st.session_state["ecom_sens_conv"] = int(config.sens_conv)
    st.session_state["ecom_sens_cpc"] = int(config.sens_cpc)
    st.session_state["ecom_sens_aov"] = int(config.sens_aov)
    st.session_state["ecom_sens_organic"] = int(config.sens_organic)
    st.session_state["ecom_scenario_bound"] = int(config.scenario_bound)
    st.session_state["ecom_mc_enabled"] = config.mc_enabled
    st.session_state["ecom_mc_iter"] = config.mc_iterations
    st.session_state["ecom_mc_var"] = config.mc_variance


def render_ecom_sidebar() -> EcomConfig:
    """Render all e-commerce sidebar widgets and return an EcomConfig."""

    # Seed defaults — prevents widget key conflicts on load
    _seed_ecom_session_state()

    # --- DB-backed Scenario Management ---
    user = get_current_user()
    project = st.session_state.get("current_project")

    if user and is_supabase_configured():
        with st.sidebar.expander("Scenario Management", expanded=False):
            # Project selector — only ecommerce projects
            all_projects = list_all_user_projects(user["id"])
            ecom_projects = [p for p in all_projects if p.get("product_type") == "ecommerce"]
            if not ecom_projects:
                st.info("No e-commerce projects found.")
            else:
                proj_names = [p["name"] for p in ecom_projects]
                default_idx = 0
                if project:
                    for i, p in enumerate(ecom_projects):
                        if p["id"] == project.get("id"):
                            default_idx = i
                            break
                selected_proj_idx = st.selectbox(
                    "Project", range(len(proj_names)),
                    format_func=lambda i: proj_names[i],
                    index=default_idx, key="_escn_proj",
                )
                sel_project = ecom_projects[selected_proj_idx]

                # Save
                st.markdown("**Save Current**")
                save_name = st.text_input("Scenario Name", value="", key="_escn_save_name")
                save_notes = st.text_input("Notes (optional)", value="", key="_escn_save_notes")
                if st.button("Save", key="_escn_btn_save"):
                    last_cfg = st.session_state.get("_last_ecom_config")
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
                        key="_escn_load_sel",
                    )
                    sel_sc = scenarios[load_idx]
                    lc1, lc2 = st.columns(2)
                    if lc1.button("Load", key="_escn_btn_load"):
                        loaded = load_scenario_config(sel_sc["id"], "ecommerce")
                        if loaded:
                            ecom_config_to_session_state(loaded)
                            st.success(f"Loaded: {sel_sc['name']}")
                            st.rerun()
                        else:
                            st.error("Failed to load scenario.")
                    if lc2.button("Delete", key="_escn_btn_del"):
                        delete_scenario(sel_sc["id"])
                        st.success(f"Deleted: {sel_sc['name']}")
                        st.rerun()

                    st.caption(f"Created: {sel_sc.get('created_at', '?')[:10]} | "
                               f"Notes: {sel_sc.get('notes') or '—'}")
                else:
                    st.info("No saved scenarios yet.")

    # --- General Settings ---
    with st.sidebar.expander("General Settings", expanded=True):
        total_months = st.number_input("Projection Horizon (months)", min_value=6, max_value=120, key="ecom_total_months",
            help="Горизонт моделирования. По умолчанию 36 месяцев (3 года).")
        phase1_dur = st.number_input("Phase 1 Duration (months)", min_value=1, max_value=48, key="ecom_phase1_dur",
            help="Длительность фазы запуска — тестирование продукта и каналов.")
        phase2_dur = st.number_input("Phase 2 Duration (months)", min_value=1, max_value=48, key="ecom_phase2_dur",
            help="Длительность фазы роста — масштабирование рекламы и ассортимента.")
        phase3_dur = total_months - phase1_dur - phase2_dur
        if phase3_dur < 1:
            st.error(f"Phase 1 + Phase 2 должны быть < {total_months} месяцев!")
            st.stop()
        st.caption(f"Phase 3 (Scaling): {phase3_dur} мес.")

    # --- Phase 1: Launch ---
    with st.sidebar.expander("Phase 1: Launch"):
        p1_aov = st.number_input("P1 Avg Order Value ($)", min_value=1.0, key="ecom_p1_aov",
            help="Средний чек заказа.")
        p1_repeat = st.number_input("P1 Repeat Purchase Rate %", min_value=0.0, max_value=100.0, key="ecom_p1_repeat",
            help="Процент клиентов, совершающих повторные покупки.")
        p1_orders_ret = st.number_input("P1 Orders/Returning Customer", min_value=0.1, max_value=10.0, key="ecom_p1_ordret",
            help="Среднее кол-во заказов в мес. у вернувшегося клиента.")
        p1_cogs = st.number_input("P1 COGS %", min_value=0.0, max_value=100.0, key="ecom_p1_cogs",
            help="Себестоимость как % от выручки.")
        p1_returns = st.number_input("P1 Return Rate %", min_value=0.0, max_value=50.0, key="ecom_p1_returns",
            help="Процент возвратов.")
        p1_ad = st.number_input("P1 Monthly Ad Budget ($)", min_value=0.0, key="ecom_p1_ad",
            help="Рекламный бюджет в месяц.")
        p1_cpc = st.number_input("P1 CPC ($)", min_value=0.01, key="ecom_p1_cpc",
            help="Стоимость клика.")
        p1_conv = st.number_input("P1 Click-to-Purchase %", min_value=0.0, max_value=100.0, key="ecom_p1_conv",
            help="Конверсия из клика в покупку.")
        p1_organic = st.number_input("P1 Organic %", min_value=0.0, max_value=99.0, key="ecom_p1_organic",
            help="Процент органического трафика от общего.")
        p1_discount = st.number_input("P1 Avg Discount %", min_value=0.0, max_value=100.0, key="ecom_p1_discount",
            help="Средняя скидка на заказы.")

    # --- Phase 2: Growth ---
    with st.sidebar.expander("Phase 2: Growth"):
        p2_aov = st.number_input("P2 Avg Order Value ($)", min_value=1.0, key="ecom_p2_aov",
            help="Средний чек заказа.")
        p2_repeat = st.number_input("P2 Repeat Purchase Rate %", min_value=0.0, max_value=100.0, key="ecom_p2_repeat",
            help="Процент клиентов, совершающих повторные покупки.")
        p2_orders_ret = st.number_input("P2 Orders/Returning Customer", min_value=0.1, max_value=10.0, key="ecom_p2_ordret",
            help="Среднее кол-во заказов в мес. у вернувшегося клиента.")
        p2_cogs = st.number_input("P2 COGS %", min_value=0.0, max_value=100.0, key="ecom_p2_cogs",
            help="Себестоимость как % от выручки.")
        p2_returns = st.number_input("P2 Return Rate %", min_value=0.0, max_value=50.0, key="ecom_p2_returns",
            help="Процент возвратов.")
        p2_ad = st.number_input("P2 Monthly Ad Budget ($)", min_value=0.0, key="ecom_p2_ad",
            help="Рекламный бюджет в месяц.")
        p2_cpc = st.number_input("P2 CPC ($)", min_value=0.01, key="ecom_p2_cpc",
            help="Стоимость клика.")
        p2_conv = st.number_input("P2 Click-to-Purchase %", min_value=0.0, max_value=100.0, key="ecom_p2_conv",
            help="Конверсия из клика в покупку.")
        p2_organic = st.number_input("P2 Organic %", min_value=0.0, max_value=99.0, key="ecom_p2_organic",
            help="Процент органического трафика от общего.")
        p2_discount = st.number_input("P2 Avg Discount %", min_value=0.0, max_value=100.0, key="ecom_p2_discount",
            help="Средняя скидка на заказы.")

    # --- Phase 3: Scaling ---
    with st.sidebar.expander("Phase 3: Scaling"):
        p3_aov = st.number_input("P3 Avg Order Value ($)", min_value=1.0, key="ecom_p3_aov",
            help="Средний чек заказа.")
        p3_repeat = st.number_input("P3 Repeat Purchase Rate %", min_value=0.0, max_value=100.0, key="ecom_p3_repeat",
            help="Процент клиентов, совершающих повторные покупки.")
        p3_orders_ret = st.number_input("P3 Orders/Returning Customer", min_value=0.1, max_value=10.0, key="ecom_p3_ordret",
            help="Среднее кол-во заказов в мес. у вернувшегося клиента.")
        p3_cogs = st.number_input("P3 COGS %", min_value=0.0, max_value=100.0, key="ecom_p3_cogs",
            help="Себестоимость как % от выручки.")
        p3_returns = st.number_input("P3 Return Rate %", min_value=0.0, max_value=50.0, key="ecom_p3_returns",
            help="Процент возвратов.")
        p3_ad = st.number_input("P3 Monthly Ad Budget ($)", min_value=0.0, key="ecom_p3_ad",
            help="Рекламный бюджет в месяц.")
        p3_cpc = st.number_input("P3 CPC ($)", min_value=0.01, key="ecom_p3_cpc",
            help="Стоимость клика.")
        p3_conv = st.number_input("P3 Click-to-Purchase %", min_value=0.0, max_value=100.0, key="ecom_p3_conv",
            help="Конверсия из клика в покупку.")
        p3_organic = st.number_input("P3 Organic %", min_value=0.0, max_value=99.0, key="ecom_p3_organic",
            help="Процент органического трафика от общего.")
        p3_discount = st.number_input("P3 Avg Discount %", min_value=0.0, max_value=100.0, key="ecom_p3_discount",
            help="Средняя скидка на заказы.")

    # --- Salaries & Costs ---
    with st.sidebar.expander("Salaries & Costs"):
        salaries_base = st.number_input("Base Monthly Salaries ($)", min_value=0.0, key="ecom_sal_base",
            help="Начальные зарплаты в месяц.")
        salaries_growth = st.number_input("Salary Growth %/mo", min_value=0.0, max_value=50.0, key="ecom_sal_growth",
            help="Ежемесячный рост зарплат (%).")
        misc_costs = st.number_input("Monthly Misc Costs ($)", min_value=0.0, key="ecom_misc",
            help="Прочие постоянные расходы в месяц (аренда, софт, логистика).")
        corporate_tax = st.number_input("Corporate Tax %", min_value=0.0, max_value=50.0, key="ecom_corp_tax",
            help="Налог на прибыль.")

    # --- Sensitivity ---
    with st.sidebar.expander("Scenario Sensitivity"):
        sens_conv = st.slider("Conversion Sensitivity %", -50, 50, key="ecom_sens_conv",
            help="Корректировка конверсий. + = лучше, - = хуже.")
        sens_cpc = st.slider("CPC Sensitivity %", -50, 50, key="ecom_sens_cpc",
            help="Корректировка CPC. + = дороже клики, - = дешевле.")
        sens_aov = st.slider("AOV Sensitivity %", -50, 50, key="ecom_sens_aov",
            help="Корректировка среднего чека. + = выше, - = ниже.")
        sens_organic = st.slider("Organic Sensitivity %", -50, 50, key="ecom_sens_organic",
            help="Корректировка органического трафика.")
        scenario_bound = st.slider("Scenario Bound %", 5, 50, key="ecom_scenario_bound",
            help="Границы пессимистичного/оптимистичного сценариев.")
        st.markdown("---")
        mc_enabled = st.checkbox("Monte Carlo Simulation", key="ecom_mc_enabled",
            help="Запустить N итераций с рандомизацией параметров.")
        if mc_enabled:
            mc_iterations = st.number_input("MC Iterations", min_value=50, max_value=1000, key="ecom_mc_iter")
            mc_variance = st.number_input("MC Max Variance %", min_value=5.0, max_value=50.0, key="ecom_mc_var")
        else:
            mc_iterations = st.session_state.get("ecom_mc_iter", 200)
            mc_variance = st.session_state.get("ecom_mc_var", 20.0)

    # ===================== BUILD EcomConfig =====================
    config = EcomConfig(
        total_months=total_months,
        phase1_dur=phase1_dur,
        phase2_dur=phase2_dur,
        phase1=EcomPhaseConfig(
            avg_order_value=p1_aov, repeat_purchase_rate=p1_repeat, orders_per_returning=p1_orders_ret,
            cogs_pct=p1_cogs, return_rate=p1_returns, ad_budget=p1_ad, cpc=p1_cpc,
            click_to_purchase=p1_conv, organic_pct=p1_organic, discount_rate=p1_discount,
        ),
        phase2=EcomPhaseConfig(
            avg_order_value=p2_aov, repeat_purchase_rate=p2_repeat, orders_per_returning=p2_orders_ret,
            cogs_pct=p2_cogs, return_rate=p2_returns, ad_budget=p2_ad, cpc=p2_cpc,
            click_to_purchase=p2_conv, organic_pct=p2_organic, discount_rate=p2_discount,
        ),
        phase3=EcomPhaseConfig(
            avg_order_value=p3_aov, repeat_purchase_rate=p3_repeat, orders_per_returning=p3_orders_ret,
            cogs_pct=p3_cogs, return_rate=p3_returns, ad_budget=p3_ad, cpc=p3_cpc,
            click_to_purchase=p3_conv, organic_pct=p3_organic, discount_rate=p3_discount,
        ),
        salaries_base=salaries_base,
        salaries_growth=salaries_growth,
        misc_costs=misc_costs,
        corporate_tax=corporate_tax,
        sens_conv=sens_conv,
        sens_cpc=sens_cpc,
        sens_aov=sens_aov,
        sens_organic=sens_organic,
        scenario_bound=scenario_bound,
        mc_enabled=mc_enabled,
        mc_iterations=mc_iterations,
        mc_variance=mc_variance,
    )

    # Stash config for scenario save
    st.session_state["_last_ecom_config"] = config

    return config
