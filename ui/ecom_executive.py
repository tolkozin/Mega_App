"""E-commerce Executive Dashboard, Key Metrics, Milestones, Cost Breakdown."""

import streamlit as st
import pandas as pd
import numpy as np

from ui.components import health_indicator, fmt_milestone


def render_ecom_milestones(milestones_main):
    """Render Key Milestones section for e-commerce."""
    st.header("Key Milestones")
    ms_cols = st.columns(4)

    ms_cols[0].metric("Break-Even (Monthly P&L)", fmt_milestone(milestones_main.get("break_even_month")),
        help="Месяц, когда Net Profit впервые > 0.")
    ms_cols[1].metric("Cumulative Break-Even", fmt_milestone(milestones_main.get("cumulative_break_even")),
        help="Месяц, когда кумулятивная прибыль вышла в плюс.")
    ms_cols[2].metric("Cash Flow Positive", fmt_milestone(milestones_main.get("cf_positive_month")),
        help="Месяц, когда денежный поток впервые > 0.")
    ms_cols[3].metric("Runway Out", fmt_milestone(milestones_main.get("runway_out_month")),
        help="Месяц, когда деньги закончатся. '—' = денег хватает.")

    ms_cols2 = st.columns(4)
    ms_cols2[0].metric("1K Customers", fmt_milestone(milestones_main.get("customers_1000")),
        help="Месяц достижения 1,000 уникальных клиентов.")
    ms_cols2[1].metric("10K Customers", fmt_milestone(milestones_main.get("customers_10000")),
        help="Месяц достижения 10,000 уникальных клиентов.")
    ms_cols2[2].metric("Revenue $10K/mo", fmt_milestone(milestones_main.get("revenue_10000")),
        help="Месяц достижения чистой выручки $10K/мес.")
    ms_cols2[3].metric("Revenue $100K/mo", fmt_milestone(milestones_main.get("revenue_100000")),
        help="Месяц достижения чистой выручки $100K/мес.")


def render_ecom_key_metrics(f_df, config):
    """Render Key Metrics section for e-commerce."""
    st.markdown("---")
    st.header("Key Metrics")

    row1 = st.columns(4)
    row1[0].metric("Total Revenue", f"${f_df['Net Revenue'].sum():,.0f}",
        help="Сумма чистой выручки за период.")
    row1[1].metric("Net Profit", f"${f_df['Net Profit'].sum():,.0f}",
        help="Чистая прибыль за период.")
    row1[2].metric("End Monthly Orders", f"{f_df['Total Orders'].iloc[-1]:,.0f}",
        help="Заказов в последний месяц.")
    row1[3].metric("Avg LTV/CAC", f"{f_df['LTV/CAC'].dropna().mean():.2f}x" if not f_df['LTV/CAC'].dropna().empty else "—",
        help="Среднее LTV/CAC. >3x = отлично.")

    row2 = st.columns(6)
    roi_val = f_df["ROI %"].iloc[-1] if not f_df["ROI %"].isna().all() else 0
    roas_val = f_df["Cumulative ROAS"].iloc[-1] if not f_df["Cumulative ROAS"].isna().all() else 0
    aov_val = f_df["AOV"].iloc[-1] if f_df["AOV"].iloc[-1] > 0 else 0
    gm_val = f_df["Gross Margin %"].iloc[-1] if f_df["Gross Margin %"].iloc[-1] > 0 else 0
    burn_vals = f_df[f_df["Burn Rate"] > 0]["Burn Rate"]
    burn_val = burn_vals.iloc[-1] if not burn_vals.empty else 0
    runway_vals = f_df["Runway (Months)"].dropna()
    runway_val = runway_vals.iloc[-1] if not runway_vals.empty else None

    row2[0].metric("ROI", f"{roi_val:,.0f}%",
        help="Return on Investment (кумулятивный).")
    row2[1].metric("ROAS", f"{roas_val:,.1f}x",
        help="Return on Ad Spend (кумулятивный).")
    row2[2].metric("AOV", f"${aov_val:,.2f}",
        help="Average Order Value (последний месяц).")
    row2[3].metric("Gross Margin", f"{gm_val:.1f}%",
        help="Валовая маржа (последний месяц).")
    row2[4].metric("Burn Rate", f"${burn_val:,.0f}/mo",
        help="Скорость сжигания денег (если CF < 0).")
    row2[5].metric("Runway", f"{runway_val:,.0f} мес." if runway_val else "∞",
        help="Месяцев до конца денег при текущем Burn Rate.")


def render_ecom_cost_breakdown(f_df):
    """Render Revenue → Net Profit Breakdown for e-commerce."""
    st.markdown("---")
    st.subheader("Revenue → Net Profit Breakdown")

    _total_rev = f_df["Net Revenue"].sum()
    _total_cogs = f_df["COGS"].sum()
    _total_marketing = f_df["Marketing"].sum()
    _total_sal = f_df["Salaries"].sum()
    _total_misc = f_df["Misc Costs"].sum()
    _total_tax = f_df["Corporate Tax"].sum()
    _total_net = f_df["Net Profit"].sum()

    _breakdown_cols = st.columns(7)
    _breakdown_cols[0].metric("Net Revenue", f"${_total_rev:,.0f}")
    _breakdown_cols[1].metric("- COGS", f"${_total_cogs:,.0f}")
    _breakdown_cols[2].metric("- Marketing", f"${_total_marketing:,.0f}")
    _breakdown_cols[3].metric("- Salaries", f"${_total_sal:,.0f}")
    _breakdown_cols[4].metric("- Misc", f"${_total_misc:,.0f}")
    _breakdown_cols[5].metric("- Tax", f"${_total_tax:,.0f}")
    _breakdown_cols[6].metric("= Net Profit", f"${_total_net:,.0f}")


def render_ecom_executive_dashboard(f_df, f_pess, f_opt, milestones_main, milestones_pess, milestones_opt):
    """Render Executive Dashboard section with health indicators and scenario summary."""
    st.markdown("---")
    st.header("Executive Dashboard")

    latest_ltv_cac = f_df["LTV/CAC"].dropna().iloc[-1] if not f_df["LTV/CAC"].dropna().empty else 0
    latest_gm = f_df["Gross Margin %"].dropna().iloc[-1] if not f_df["Gross Margin %"].dropna().empty else 0
    latest_roas = f_df["ROAS"].dropna().iloc[-1] if not f_df["ROAS"].dropna().empty else 0
    latest_cac = f_df["CAC"].dropna().iloc[-1] if not f_df["CAC"].dropna().empty else None
    latest_aov = f_df["AOV"].iloc[-1] if f_df["AOV"].iloc[-1] > 0 else 0
    total_net_profit = f_df["Net Profit"].sum()
    end_cash = f_df["Cash Balance"].iloc[-1]

    exec_data = {
        "Metric": [
            "LTV/CAC", "Gross Margin %", "ROAS", "CAC ($)",
            "AOV ($)", "Net Profit (total)", "End Cash Balance",
        ],
        "Value": [
            f"{latest_ltv_cac:.2f}x", f"{latest_gm:.1f}%", f"{latest_roas:.2f}x",
            f"${latest_cac:.2f}" if latest_cac else "—",
            f"${latest_aov:.2f}", f"${total_net_profit:,.0f}", f"${end_cash:,.0f}",
        ],
        "Status": [
            health_indicator(latest_ltv_cac, 3.0, 1.0),
            health_indicator(latest_gm, 50, 30),
            health_indicator(latest_roas, 3, 1),
            health_indicator(latest_cac, 20, 50, higher_is_better=False) if latest_cac else "⚪ N/A",
            health_indicator(latest_aov, 40, 20),
            health_indicator(total_net_profit, 0, -50000),
            health_indicator(end_cash, 0, -10000),
        ],
        "Benchmark": [
            ">3x отлично, <1x плохо",
            ">50% отлично, <30% плохо",
            ">3x эффективно, <1x убыточно",
            "<$20 отлично, >$50 плохо",
            ">$40 хорошо, <$20 плохо",
            ">0 прибыль, <0 убыток",
            ">0 есть деньги, <0 дефицит",
        ],
    }

    ex_c1, ex_c2 = st.columns([2, 3])
    with ex_c1:
        st.dataframe(pd.DataFrame(exec_data), use_container_width=True, hide_index=True)

    with ex_c2:
        st.markdown("**Scenario Summary (Period Total)**")
        sc_mini = pd.DataFrame({
            "": ["Revenue", "Net Profit", "End Orders", "Customers", "ROI %", "Break-Even"],
            "🔴 Pessimistic": [
                f"${f_pess['Net Revenue'].sum():,.0f}",
                f"${f_pess['Net Profit'].sum():,.0f}",
                f"{f_pess['Total Orders'].iloc[-1]:,.0f}",
                f"{f_pess['Cumulative Customers'].iloc[-1]:,.0f}",
                f"{f_pess['ROI %'].iloc[-1]:,.0f}%",
                fmt_milestone(milestones_pess.get("break_even_month")),
            ],
            "🔵 Base": [
                f"${f_df['Net Revenue'].sum():,.0f}",
                f"${f_df['Net Profit'].sum():,.0f}",
                f"{f_df['Total Orders'].iloc[-1]:,.0f}",
                f"{f_df['Cumulative Customers'].iloc[-1]:,.0f}",
                f"{f_df['ROI %'].iloc[-1]:,.0f}%",
                fmt_milestone(milestones_main.get("break_even_month")),
            ],
            "🟢 Optimistic": [
                f"${f_opt['Net Revenue'].sum():,.0f}",
                f"${f_opt['Net Profit'].sum():,.0f}",
                f"{f_opt['Total Orders'].iloc[-1]:,.0f}",
                f"{f_opt['Cumulative Customers'].iloc[-1]:,.0f}",
                f"{f_opt['ROI %'].iloc[-1]:,.0f}%",
                fmt_milestone(milestones_opt.get("break_even_month")),
            ],
        })
        st.dataframe(sc_mini, use_container_width=True, hide_index=True)

        ms_inline = []
        for key, label in [("break_even_month", "Break-Even"), ("cumulative_break_even", "Cum. Break-Even"),
                            ("cf_positive_month", "CF Positive"), ("runway_out_month", "Runway Out")]:
            val = milestones_main.get(key)
            ms_inline.append(f"**{label}:** {val} мес." if val else f"**{label}:** —")
        st.markdown(" | ".join(ms_inline))
