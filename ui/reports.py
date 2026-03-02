"""Financial Reports section."""

import streamlit as st
import pandas as pd

from ui.components import fmt_milestone


def render_financial_reports(f_df, f_pess, f_opt, milestones_main, milestones_pess, milestones_opt):
    """Render all financial report tabs."""
    st.markdown("---")
    st.header("Financial Reports")

    rep_tab1, rep_tab2, rep_tab3, rep_tab4, rep_tab5 = st.tabs(
        ["P&L", "Cash Flow", "Balance Sheet", "Key Metrics", "Summary & Scenarios"])

    pnl_cols = ["Month", "Product Phase", "Total Gross Revenue", "Recognized Revenue", "COGS", "Gross Profit",
                "Marketing", "Salaries", "Misc Costs", "Total Commissions", "EBITDA",
                "Corporate Tax", "Net Profit"]
    pnl_rename = {
        "Month": "Месяц", "Product Phase": "Фаза",
        "Total Gross Revenue": "Валовая выручка (cash)",
        "Recognized Revenue": "Признанная выручка (MRR)",
        "COGS": "COGS (себест. на юзера)",
        "Gross Profit": "Валовая прибыль (выручка-COGS-комиссии)",
        "Marketing": "Маркетинг (реклама+органик)",
        "Salaries": "Зарплаты", "Misc Costs": "Прочие расходы",
        "Total Commissions": "Комиссии (Store+Web+банк)",
        "EBITDA": "EBITDA (до налогов)",
        "Corporate Tax": "Налог на прибыль",
        "Net Profit": "Чистая прибыль",
    }
    cf_cols = ["Month", "Product Phase", "Total Gross Revenue", "Total Commissions",
               "Total Expenses", "Corporate Tax", "Net Cash Flow", "Cash Balance"]
    cf_rename = {
        "Month": "Месяц", "Product Phase": "Фаза",
        "Total Gross Revenue": "Валовая выручка (cash)",
        "Total Commissions": "Комиссии (Store+Web+банк)",
        "Total Expenses": "Все расходы (COGS+маркетинг+зп+прочие)",
        "Corporate Tax": "Налог на прибыль",
        "Net Cash Flow": "Чистый ден. поток (приход-расход)",
        "Cash Balance": "Остаток на счёте",
    }

    with rep_tab1:
        st.subheader("Profit & Loss Statement")
        st.caption("Отчёт о прибылях и убытках. Валовая выручка — фактически полученные деньги. Признанная выручка (MRR) — помесячная. Чистая прибыль = EBITDA - налоги.")
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
        st.subheader("Balance Sheet (Simplified)")
        st.caption("Упрощённый баланс.")
        bs_cols = ["Month", "Product Phase", "Cash Balance", "Deferred Revenue", "Cumulative Net Profit"]
        bs_rename = {
            "Month": "Месяц", "Product Phase": "Фаза",
            "Cash Balance": "Остаток на счёте",
            "Deferred Revenue": "Отложенная выручка (авансы annual)",
            "Cumulative Net Profit": "Кумулятивная прибыль",
        }
        st.dataframe(f_df[bs_cols].rename(columns=bs_rename), use_container_width=True)

    with rep_tab4:
        st.subheader("Key Metrics")
        st.caption("Полная таблица ключевых SaaS-метрик по месяцам.")
        metrics_cols = ["Month", "Product Phase", "Total Active Users", "ARPU", "Blended Churn", "CRR %",
                        "LTV", "Paid CAC", "Organic CAC", "Blended CAC", "LTV/CAC", "MER", "ROAS",
                        "Payback Period (Months)", "ROI %", "NRR %", "Quick Ratio",
                        "Burn Rate", "Runway (Months)", "CAE", "Revenue per Install"]
        km_rename = {
            "Month": "Месяц", "Product Phase": "Фаза",
            "Total Active Users": "Активные юзеры",
            "ARPU": "ARPU (доход/юзер/мес)",
            "Blended Churn": "Отток (средневзвеш.)",
            "CRR %": "CRR % (удержание)",
            "LTV": "LTV (ценность клиента)",
            "Paid CAC": "Paid CAC (стоимость из рекламы)",
            "Organic CAC": "Organic CAC (стоимость из органики)",
            "Blended CAC": "Blended CAC (общая стоимость)",
            "LTV/CAC": "LTV/CAC (>3x хорошо)",
            "MER": "MER (выручка/маркетинг)",
            "ROAS": "ROAS (выручка/реклама)",
            "Payback Period (Months)": "Payback (мес. окупаемости)",
            "ROI %": "ROI % (возврат инвестиций)",
            "NRR %": "NRR % (удержание выручки)",
            "Quick Ratio": "Quick Ratio (рост/потери MRR)",
            "Burn Rate": "Burn Rate (расход/мес при убытке)",
            "Runway (Months)": "Runway (мес. до конца денег)",
            "CAE": "CAE (эффект. привлечения)",
            "Revenue per Install": "Доход на установку",
        }
        km_sc1, km_sc2, km_sc3 = st.tabs(["Base", "Pessimistic", "Optimistic"])
        with km_sc1:
            st.dataframe(f_df[metrics_cols].rename(columns=km_rename), use_container_width=True)
        with km_sc2:
            st.dataframe(f_pess[metrics_cols].rename(columns=km_rename), use_container_width=True)
        with km_sc3:
            st.dataframe(f_opt[metrics_cols].rename(columns=km_rename), use_container_width=True)

    with rep_tab5:
        _render_summary_tab(f_df, f_pess, f_opt, milestones_main, milestones_pess, milestones_opt)


def _render_summary_tab(f_df, f_pess, f_opt, milestones_main, milestones_pess, milestones_opt):
    def build_phase_summary(sdf):
        ps = sdf.groupby("Product Phase").agg(
            Months=("Month", "count"),
            Total_Revenue=("Total Gross Revenue", "sum"),
            Total_Marketing=("Marketing", "sum"),
            Total_Salaries=("Salaries", "sum"),
            Total_Misc=("Misc Costs", "sum"),
            Total_COGS=("COGS", "sum"),
            Total_Commissions=("Total Commissions", "sum"),
            Net_Profit=("Net Profit", "sum"),
            End_Users=("Total Active Users", "last"),
            New_Users=("New Paid Users", "sum"),
            End_MRR=("Total MRR", "last"),
            Avg_ARPU=("ARPU", "mean"),
            Avg_LTV_CAC=("LTV/CAC", "mean"),
        ).reset_index()
        ps.columns = [
            "Фаза", "Месяцев", "Выручка (cash)", "Маркетинг", "Зарплаты",
            "Прочие", "COGS (себест.)", "Комиссии (Store+Web+банк)",
            "Чистая прибыль", "Юзеры на конец", "Новые юзеры", "MRR на конец",
            "Сред. ARPU", "Сред. LTV/CAC",
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

    # Scenario comparison table
    st.subheader("Scenario Comparison Table")
    st.caption("Сводная таблица итогов по трём сценариям.")
    sc_table = pd.DataFrame({
        "Metric": ["Total Revenue", "Net Profit", "End MRR", "End Users", "Cumulative ROI %",
                    "Break-Even Month", "Cumulative BE", "Runway Out"],
        "Pessimistic": [
            f"${f_pess['Total Gross Revenue'].sum():,.0f}",
            f"${f_pess['Net Profit'].sum():,.0f}",
            f"${f_pess['Total MRR'].iloc[-1]:,.0f}",
            f"{f_pess['Total Active Users'].iloc[-1]:,.0f}",
            f"{f_pess['ROI %'].iloc[-1]:,.0f}%",
            fmt_milestone(milestones_pess.get("break_even_month")),
            fmt_milestone(milestones_pess.get("cumulative_break_even")),
            fmt_milestone(milestones_pess.get("runway_out_month")),
        ],
        "Base": [
            f"${f_df['Total Gross Revenue'].sum():,.0f}",
            f"${f_df['Net Profit'].sum():,.0f}",
            f"${f_df['Total MRR'].iloc[-1]:,.0f}",
            f"{f_df['Total Active Users'].iloc[-1]:,.0f}",
            f"{f_df['ROI %'].iloc[-1]:,.0f}%",
            fmt_milestone(milestones_main.get("break_even_month")),
            fmt_milestone(milestones_main.get("cumulative_break_even")),
            fmt_milestone(milestones_main.get("runway_out_month")),
        ],
        "Optimistic": [
            f"${f_opt['Total Gross Revenue'].sum():,.0f}",
            f"${f_opt['Net Profit'].sum():,.0f}",
            f"${f_opt['Total MRR'].iloc[-1]:,.0f}",
            f"{f_opt['Total Active Users'].iloc[-1]:,.0f}",
            f"{f_opt['ROI %'].iloc[-1]:,.0f}%",
            fmt_milestone(milestones_opt.get("break_even_month")),
            fmt_milestone(milestones_opt.get("cumulative_break_even")),
            fmt_milestone(milestones_opt.get("runway_out_month")),
        ],
    })
    st.dataframe(sc_table, use_container_width=True, hide_index=True)

    # Milestone comparison
    st.subheader("Milestone Comparison")
    st.caption("Сравнение ключевых вех по трём сценариям.")
    ms_compare = pd.DataFrame({
        "Milestone": ["Break-Even (P&L)", "Cumulative Break-Even", "Cash Flow Positive",
                       "Investment Payback", "1K Users", "10K Users", "MRR $10K", "MRR $100K", "Runway Out"],
        "Pessimistic": [
            fmt_milestone(milestones_pess.get(k)) for k in
            ["break_even_month", "cumulative_break_even", "cf_positive_month",
             "investment_payback_month", "users_1000", "users_10000", "mrr_10000", "mrr_100000", "runway_out_month"]
        ],
        "Base": [
            fmt_milestone(milestones_main.get(k)) for k in
            ["break_even_month", "cumulative_break_even", "cf_positive_month",
             "investment_payback_month", "users_1000", "users_10000", "mrr_10000", "mrr_100000", "runway_out_month"]
        ],
        "Optimistic": [
            fmt_milestone(milestones_opt.get(k)) for k in
            ["break_even_month", "cumulative_break_even", "cf_positive_month",
             "investment_payback_month", "users_1000", "users_10000", "mrr_10000", "mrr_100000", "runway_out_month"]
        ],
    })
    st.dataframe(ms_compare, use_container_width=True, hide_index=True)
