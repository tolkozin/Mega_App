"""E-commerce Financial Reports section."""

import streamlit as st
import pandas as pd

from ui.components import fmt_milestone


def render_ecom_reports(f_df, f_pess, f_opt, milestones_main, milestones_pess, milestones_opt):
    """Render all e-commerce financial report tabs."""
    st.markdown("---")
    st.header("Financial Reports")

    rep_tab1, rep_tab2, rep_tab3, rep_tab4 = st.tabs(
        ["P&L", "Cash Flow", "Key Metrics", "Summary & Scenarios"])

    pnl_cols = ["Month", "Product Phase", "Gross Revenue", "Returns", "Discounts", "Net Revenue",
                "COGS", "Gross Profit", "Marketing", "Salaries", "Misc Costs",
                "EBITDA", "Corporate Tax", "Net Profit"]
    pnl_rename = {
        "Month": "Месяц", "Product Phase": "Фаза",
        "Gross Revenue": "Валовая выручка",
        "Returns": "Возвраты",
        "Discounts": "Скидки",
        "Net Revenue": "Чистая выручка",
        "COGS": "Себестоимость (COGS)",
        "Gross Profit": "Валовая прибыль",
        "Marketing": "Маркетинг (реклама)",
        "Salaries": "Зарплаты",
        "Misc Costs": "Прочие расходы",
        "EBITDA": "EBITDA",
        "Corporate Tax": "Налог на прибыль",
        "Net Profit": "Чистая прибыль",
    }

    cf_cols = ["Month", "Product Phase", "Net Revenue", "COGS", "Marketing",
               "Salaries", "Misc Costs", "Corporate Tax", "Net Cash Flow", "Cash Balance"]
    cf_rename = {
        "Month": "Месяц", "Product Phase": "Фаза",
        "Net Revenue": "Чистая выручка",
        "COGS": "Себестоимость",
        "Marketing": "Маркетинг",
        "Salaries": "Зарплаты",
        "Misc Costs": "Прочие расходы",
        "Corporate Tax": "Налог на прибыль",
        "Net Cash Flow": "Чистый ден. поток",
        "Cash Balance": "Остаток на счёте",
    }

    with rep_tab1:
        st.subheader("Profit & Loss Statement")
        st.caption("Отчёт о прибылях и убытках для e-commerce бизнеса.")
        pnl_sc1, pnl_sc2, pnl_sc3 = st.tabs(["Base", "Pessimistic", "Optimistic"])
        with pnl_sc1:
            st.dataframe(f_df[pnl_cols].rename(columns=pnl_rename), use_container_width=True)
        with pnl_sc2:
            st.dataframe(f_pess[pnl_cols].rename(columns=pnl_rename), use_container_width=True)
        with pnl_sc3:
            st.dataframe(f_opt[pnl_cols].rename(columns=pnl_rename), use_container_width=True)

    with rep_tab2:
        st.subheader("Cash Flow Statement")
        st.caption("Отчёт о движении денежных средств.")
        cf_sc1, cf_sc2, cf_sc3 = st.tabs(["Base", "Pessimistic", "Optimistic"])
        with cf_sc1:
            st.dataframe(f_df[cf_cols].rename(columns=cf_rename), use_container_width=True)
        with cf_sc2:
            st.dataframe(f_pess[cf_cols].rename(columns=cf_rename), use_container_width=True)
        with cf_sc3:
            st.dataframe(f_opt[cf_cols].rename(columns=cf_rename), use_container_width=True)

    with rep_tab3:
        st.subheader("Key Metrics")
        st.caption("Полная таблица ключевых e-commerce метрик по месяцам.")
        metrics_cols = ["Month", "Product Phase", "Total Orders", "New Customers", "Cumulative Customers",
                        "AOV", "Gross Margin %", "CAC", "LTV", "LTV/CAC", "ROAS",
                        "CAC Payback", "ROI %", "Burn Rate", "Runway (Months)"]
        km_rename = {
            "Month": "Месяц", "Product Phase": "Фаза",
            "Total Orders": "Заказов",
            "New Customers": "Новые клиенты",
            "Cumulative Customers": "Кумул. клиенты",
            "AOV": "Средний чек",
            "Gross Margin %": "Валовая маржа %",
            "CAC": "CAC (стоимость привлечения)",
            "LTV": "LTV (ценность клиента)",
            "LTV/CAC": "LTV/CAC",
            "ROAS": "ROAS (доход/реклама)",
            "CAC Payback": "CAC Payback (заказов)",
            "ROI %": "ROI %",
            "Burn Rate": "Burn Rate",
            "Runway (Months)": "Runway (мес.)",
        }
        km_sc1, km_sc2, km_sc3 = st.tabs(["Base", "Pessimistic", "Optimistic"])
        with km_sc1:
            st.dataframe(f_df[metrics_cols].rename(columns=km_rename), use_container_width=True)
        with km_sc2:
            st.dataframe(f_pess[metrics_cols].rename(columns=km_rename), use_container_width=True)
        with km_sc3:
            st.dataframe(f_opt[metrics_cols].rename(columns=km_rename), use_container_width=True)

    with rep_tab4:
        _render_ecom_summary_tab(f_df, f_pess, f_opt, milestones_main, milestones_pess, milestones_opt)


def _render_ecom_summary_tab(f_df, f_pess, f_opt, milestones_main, milestones_pess, milestones_opt):
    def build_phase_summary(sdf):
        ps = sdf.groupby("Product Phase").agg(
            Months=("Month", "count"),
            Total_Revenue=("Net Revenue", "sum"),
            Total_Marketing=("Marketing", "sum"),
            Total_Salaries=("Salaries", "sum"),
            Total_Misc=("Misc Costs", "sum"),
            Total_COGS=("COGS", "sum"),
            Net_Profit=("Net Profit", "sum"),
            Total_Orders=("Total Orders", "sum"),
            New_Customers=("New Customers", "sum"),
            Avg_AOV=("AOV", "mean"),
            Avg_LTV_CAC=("LTV/CAC", "mean"),
        ).reset_index()
        ps.columns = [
            "Фаза", "Месяцев", "Чистая выручка", "Маркетинг", "Зарплаты",
            "Прочие", "Себестоимость",
            "Чистая прибыль", "Заказов", "Новых клиентов",
            "Сред. AOV", "Сред. LTV/CAC",
        ]
        return ps

    st.subheader("Summary by Phase")
    st.caption("Итоги по каждой фазе продукта.")
    ps_sc1, ps_sc2, ps_sc3 = st.tabs(["Base", "Pessimistic", "Optimistic"])
    with ps_sc1:
        st.dataframe(build_phase_summary(f_df), use_container_width=True)
    with ps_sc2:
        st.dataframe(build_phase_summary(f_pess), use_container_width=True)
    with ps_sc3:
        st.dataframe(build_phase_summary(f_opt), use_container_width=True)

    st.subheader("Scenario Comparison Table")
    st.caption("Сводная таблица итогов по трём сценариям.")
    sc_table = pd.DataFrame({
        "Metric": ["Total Revenue", "Net Profit", "End Monthly Orders", "Total Customers",
                    "ROI %", "Break-Even Month", "Cumulative BE"],
        "Pessimistic": [
            f"${f_pess['Net Revenue'].sum():,.0f}",
            f"${f_pess['Net Profit'].sum():,.0f}",
            f"{f_pess['Total Orders'].iloc[-1]:,.0f}",
            f"{f_pess['Cumulative Customers'].iloc[-1]:,.0f}",
            f"{f_pess['ROI %'].iloc[-1]:,.0f}%",
            fmt_milestone(milestones_pess.get("break_even_month")),
            fmt_milestone(milestones_pess.get("cumulative_break_even")),
        ],
        "Base": [
            f"${f_df['Net Revenue'].sum():,.0f}",
            f"${f_df['Net Profit'].sum():,.0f}",
            f"{f_df['Total Orders'].iloc[-1]:,.0f}",
            f"{f_df['Cumulative Customers'].iloc[-1]:,.0f}",
            f"{f_df['ROI %'].iloc[-1]:,.0f}%",
            fmt_milestone(milestones_main.get("break_even_month")),
            fmt_milestone(milestones_main.get("cumulative_break_even")),
        ],
        "Optimistic": [
            f"${f_opt['Net Revenue'].sum():,.0f}",
            f"${f_opt['Net Profit'].sum():,.0f}",
            f"{f_opt['Total Orders'].iloc[-1]:,.0f}",
            f"{f_opt['Cumulative Customers'].iloc[-1]:,.0f}",
            f"{f_opt['ROI %'].iloc[-1]:,.0f}%",
            fmt_milestone(milestones_opt.get("break_even_month")),
            fmt_milestone(milestones_opt.get("cumulative_break_even")),
        ],
    })
    st.dataframe(sc_table, use_container_width=True, hide_index=True)

    st.subheader("Milestone Comparison")
    st.caption("Сравнение ключевых вех по трём сценариям.")
    milestone_keys = [
        ("break_even_month", "Break-Even (P&L)"),
        ("cumulative_break_even", "Cumulative Break-Even"),
        ("cf_positive_month", "Cash Flow Positive"),
        ("runway_out_month", "Runway Out"),
        ("customers_1000", "1K Customers"),
        ("customers_10000", "10K Customers"),
        ("revenue_10000", "Revenue $10K/mo"),
        ("revenue_100000", "Revenue $100K/mo"),
    ]
    ms_compare = pd.DataFrame({
        "Milestone": [label for _, label in milestone_keys],
        "Pessimistic": [fmt_milestone(milestones_pess.get(k)) for k, _ in milestone_keys],
        "Base": [fmt_milestone(milestones_main.get(k)) for k, _ in milestone_keys],
        "Optimistic": [fmt_milestone(milestones_opt.get(k)) for k, _ in milestone_keys],
    })
    st.dataframe(ms_compare, use_container_width=True, hide_index=True)
