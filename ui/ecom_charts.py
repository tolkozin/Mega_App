"""E-commerce Plotly chart tabs."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from ui.components import add_phase_lines, add_milestone_markers


MS_FINANCIAL = [("break_even_month", "BE"), ("cumulative_break_even", "Cum.BE"), ("runway_out_month", "Runway Out")]
MS_ORDERS = [("orders_1000", "1K"), ("orders_10000", "10K"), ("orders_100000", "100K")]
MS_REVENUE = [("revenue_10000", "$10K"), ("revenue_50000", "$50K"), ("revenue_100000", "$100K")]
MS_CUSTOMERS = [("customers_1000", "1K"), ("customers_10000", "10K"), ("customers_100000", "100K")]


def render_ecom_charts(f_df, f_pess, f_opt, milestones_main, p1_end, p2_end, config):
    """Render all 4 e-commerce chart tabs."""
    tab1, tab2, tab3, tab4 = st.tabs(["Revenue & Orders", "Customers", "Unit Economics", "Profitability"])

    with tab1:
        _render_revenue_orders_tab(f_df, f_pess, f_opt, milestones_main, p1_end, p2_end)

    with tab2:
        _render_customers_tab(f_df, f_pess, f_opt, milestones_main, p1_end, p2_end)

    with tab3:
        _render_unit_economics_tab(f_df, f_pess, f_opt, milestones_main, p1_end, p2_end)

    with tab4:
        _render_profitability_tab(f_df, f_pess, f_opt, milestones_main, p1_end, p2_end)


def _render_revenue_orders_tab(f_df, f_pess, f_opt, ms, p1_end, p2_end):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Net Revenue")
        st.caption("Чистая выручка = Валовая выручка - Возвраты - Скидки. Показывает фактически заработанные деньги по трём сценариям.")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Net Revenue"], mode="lines", name="Base", fill="tozeroy"))
        fig.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["Net Revenue"], mode="lines", line=dict(dash="dot", color="red"), name="Pessimistic"))
        fig.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["Net Revenue"], mode="lines", line=dict(dash="dash", color="green"), name="Optimistic"))
        fig.update_layout(title="Net Revenue (3 Scenarios)")
        add_phase_lines(fig, p1_end, p2_end)
        add_milestone_markers(fig, ms, MS_REVENUE, color="purple")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Total Orders")
        st.caption("Общее количество заказов в месяц: новые покупки + повторные заказы от существующих клиентов.")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=f_df["Month"], y=f_df["Total Orders"], name="Total Orders (Base)"))
        fig2.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["Total Orders"], mode="lines", line=dict(dash="dot", color="red"), name="Pessimistic"))
        fig2.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["Total Orders"], mode="lines", line=dict(dash="dash", color="green"), name="Optimistic"))
        fig2.update_layout(title="Total Orders (3 Scenarios)")
        add_phase_lines(fig2, p1_end, p2_end)
        add_milestone_markers(fig2, ms, MS_ORDERS, color="blue")
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Revenue Breakdown")
        st.caption("Декомпозиция валовой выручки: сколько теряется на возвратах и скидках.")
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=f_df["Month"], y=f_df["Gross Revenue"], name="Gross Revenue"))
        fig3.add_trace(go.Bar(x=f_df["Month"], y=-f_df["Returns"], name="Returns", marker_color="red"))
        fig3.add_trace(go.Bar(x=f_df["Month"], y=-f_df["Discounts"], name="Discounts", marker_color="orange"))
        fig3.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Net Revenue"], mode="lines+markers", name="Net Revenue", line=dict(color="black", width=2)))
        fig3.update_layout(barmode="relative", title="Revenue Waterfall")
        add_phase_lines(fig3, p1_end, p2_end)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("Cash Balance")
        st.caption("Остаток денег на счёте. Красная линия на нуле — если ниже, деньги закончились.")
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=f_df["Month"], y=f_df["Cash Balance"], name="Base"))
        fig4.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["Cash Balance"], mode="lines", line=dict(dash="dot", color="red"), name="Pessimistic"))
        fig4.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["Cash Balance"], mode="lines", line=dict(dash="dash", color="green"), name="Optimistic"))
        fig4.add_hline(y=0, line_dash="dash", line_color="red")
        add_phase_lines(fig4, p1_end, p2_end)
        add_milestone_markers(fig4, ms, MS_FINANCIAL, color="orange")
        fig4.update_layout(title="Cash Balance (3 Scenarios)")
        st.plotly_chart(fig4, use_container_width=True)


def _render_customers_tab(f_df, f_pess, f_opt, ms, p1_end, p2_end):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("New vs Returning Customers")
        st.caption("Новые клиенты (из рекламы + органика) vs повторные заказы от существующей базы.")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=f_df["Month"], y=f_df["New Customers"], name="New Customers", marker_color="steelblue"))
        fig.add_trace(go.Bar(x=f_df["Month"], y=f_df["Returning Orders"], name="Returning Orders", marker_color="lightgreen"))
        fig.update_layout(barmode="stack", title="Customer Acquisition Mix")
        add_phase_lines(fig, p1_end, p2_end)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Cumulative Customers")
        st.caption("Накопленная база уникальных клиентов. Маркеры показывают достижение ключевых отметок.")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Cumulative Customers"], mode="lines", name="Base"))
        fig2.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["Cumulative Customers"], mode="lines", line=dict(dash="dot", color="red"), name="Pessimistic"))
        fig2.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["Cumulative Customers"], mode="lines", line=dict(dash="dash", color="green"), name="Optimistic"))
        fig2.update_layout(title="Cumulative Customers (3 Scenarios)")
        add_phase_lines(fig2, p1_end, p2_end)
        add_milestone_markers(fig2, ms, MS_CUSTOMERS, color="blue")
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Paid vs Organic Purchases")
        st.caption("Разбивка новых покупок по источникам: платная реклама vs органический трафик.")
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=f_df["Month"], y=f_df["Paid Purchases"], name="Paid Purchases"))
        fig3.add_trace(go.Bar(x=f_df["Month"], y=f_df["Organic Purchases"], name="Organic Purchases"))
        fig3.update_layout(barmode="stack", title="Traffic Source Mix")
        add_phase_lines(fig3, p1_end, p2_end)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("AOV Trend")
        st.caption("Динамика среднего чека (Average Order Value) по месяцам и трём сценариям.")
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=f_df["Month"], y=f_df["AOV"], mode="lines+markers", name="Base"))
        fig4.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["AOV"], mode="lines", line=dict(dash="dot", color="red"), name="Pessimistic"))
        fig4.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["AOV"], mode="lines", line=dict(dash="dash", color="green"), name="Optimistic"))
        fig4.update_layout(title="Average Order Value (3 Scenarios)")
        add_phase_lines(fig4, p1_end, p2_end)
        st.plotly_chart(fig4, use_container_width=True)


def _render_unit_economics_tab(f_df, f_pess, f_opt, ms, p1_end, p2_end):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("LTV vs CAC")
        st.caption("Пожизненная ценность клиента (LTV) vs стоимость привлечения (CAC). LTV > CAC = юнит-экономика положительная.")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=f_df["Month"], y=f_df["LTV"], mode="lines", name="LTV (Base)"))
        fig.add_trace(go.Scatter(x=f_df["Month"], y=f_df["CAC"], mode="lines", name="CAC (Base)"))
        fig.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["LTV"], mode="lines", line=dict(dash="dot"), name="LTV (Pess)", visible="legendonly"))
        fig.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["CAC"], mode="lines", line=dict(dash="dot"), name="CAC (Pess)", visible="legendonly"))
        fig.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["LTV"], mode="lines", line=dict(dash="dash"), name="LTV (Opt)", visible="legendonly"))
        fig.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["CAC"], mode="lines", line=dict(dash="dash"), name="CAC (Opt)", visible="legendonly"))
        fig.update_layout(title="LTV vs CAC (3 Scenarios)")
        add_phase_lines(fig, p1_end, p2_end)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("ROAS")
        st.caption("Return on Ad Spend — сколько выручки приносит каждый доллар рекламы. ROAS > 1 = реклама окупается.")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=f_df["Month"], y=f_df["ROAS"], mode="lines", name="ROAS (Base)"))
        fig2.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["ROAS"], mode="lines", line=dict(dash="dot", color="red"), name="Pessimistic"))
        fig2.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["ROAS"], mode="lines", line=dict(dash="dash", color="green"), name="Optimistic"))
        fig2.add_hline(y=1.0, line_dash="dash", line_color="gray", annotation_text="Break-even")
        fig2.update_layout(title="ROAS (3 Scenarios)")
        add_phase_lines(fig2, p1_end, p2_end)
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Gross Margin %")
        st.caption("Валовая маржа — процент прибыли после вычета себестоимости от чистой выручки.")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Gross Margin %"], mode="lines", name="Base"))
        fig3.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["Gross Margin %"], mode="lines", line=dict(dash="dot", color="red"), name="Pessimistic"))
        fig3.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["Gross Margin %"], mode="lines", line=dict(dash="dash", color="green"), name="Optimistic"))
        fig3.update_layout(title="Gross Margin % (3 Scenarios)")
        add_phase_lines(fig3, p1_end, p2_end)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("CAC Payback")
        st.caption("Через сколько заказов окупается привлечение одного клиента.")
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=f_df["Month"], y=f_df["CAC Payback"], mode="lines", name="Base"))
        fig4.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["CAC Payback"], mode="lines", line=dict(dash="dot", color="red"), name="Pessimistic"))
        fig4.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["CAC Payback"], mode="lines", line=dict(dash="dash", color="green"), name="Optimistic"))
        fig4.update_layout(title="CAC Payback (orders to break even)")
        add_phase_lines(fig4, p1_end, p2_end)
        st.plotly_chart(fig4, use_container_width=True)


def _render_profitability_tab(f_df, f_pess, f_opt, ms, p1_end, p2_end):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("P&L Waterfall")
        st.caption("Каскадная диаграмма: выручка минус все расходы = чистая прибыль.")
        fig = go.Figure(go.Waterfall(
            name="P&L", orientation="v",
            measure=["relative", "relative", "relative", "relative", "relative", "relative", "total"],
            x=["Net Revenue", "COGS", "Marketing", "Salaries", "Misc", "Tax", "Net Profit"],
            y=[f_df["Net Revenue"].sum(), -f_df["COGS"].sum(), -f_df["Marketing"].sum(),
               -f_df["Salaries"].sum(), -f_df["Misc Costs"].sum(),
               -f_df["Corporate Tax"].sum(), f_df["Net Profit"].sum()],
            connector={"line": {"color": "rgb(63, 63, 63)"}}
        ))
        fig.update_layout(title="P&L Waterfall (Period Total)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Scenario Comparison")
        st.caption("Сравнение итоговых показателей по трём сценариям.")
        metrics_names = ["Net Profit", "Total Revenue", "End Orders"]
        scenario_data = []
        for label, sdf in [("Pessimistic", f_pess), ("Base", f_df), ("Optimistic", f_opt)]:
            scenario_data.append({
                "Scenario": label,
                "Net Profit": sdf["Net Profit"].sum(),
                "Total Revenue": sdf["Net Revenue"].sum(),
                "End Orders": sdf["Total Orders"].iloc[-1],
            })
        sc_df = pd.DataFrame(scenario_data)
        fig2 = go.Figure()
        for metric in metrics_names:
            fig2.add_trace(go.Bar(
                x=sc_df["Scenario"], y=sc_df[metric], name=metric,
                visible=True if metric == "Net Profit" else "legendonly"
            ))
        fig2.update_layout(title="Scenario Comparison", barmode="group")
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Cumulative Net Profit")
        st.caption("Накопленная чистая прибыль. Пересечение нуля — кумулятивная безубыточность.")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Cumulative Net Profit"], mode="lines", name="Base"))
        fig3.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["Cumulative Net Profit"], mode="lines", line=dict(dash="dot", color="red"), name="Pessimistic"))
        fig3.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["Cumulative Net Profit"], mode="lines", line=dict(dash="dash", color="green"), name="Optimistic"))
        fig3.add_hline(y=0, line_dash="dash", line_color="red")
        fig3.update_layout(title="Cumulative Net Profit (3 Scenarios)")
        add_phase_lines(fig3, p1_end, p2_end)
        add_milestone_markers(fig3, ms, [("cumulative_break_even", "Cum.BE")], color="green")
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("ROI %")
        st.caption("Кумулятивный ROI — возврат на маркетинговые инвестиции.")
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=f_df["Month"], y=f_df["ROI %"], mode="lines", name="Base"))
        fig4.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["ROI %"], mode="lines", line=dict(dash="dot", color="red"), name="Pessimistic"))
        fig4.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["ROI %"], mode="lines", line=dict(dash="dash", color="green"), name="Optimistic"))
        fig4.add_hline(y=0, line_dash="dash", line_color="gray")
        fig4.update_layout(title="Cumulative ROI % (3 Scenarios)")
        add_phase_lines(fig4, p1_end, p2_end)
        st.plotly_chart(fig4, use_container_width=True)


def render_ecom_monte_carlo(config, base_sens, start_m, end_m):
    """Render Monte Carlo simulation for e-commerce model."""
    from ecommerce.engine import run_ecom_model

    st.markdown("---")
    st.header("Monte Carlo Simulation")
    st.caption("Моделирование случайных отклонений параметров для оценки диапазона возможных результатов.")
    import numpy as np
    np.random.seed(42)
    mc_results = []
    mc_var = config.mc_variance / 100.0
    progress = st.progress(0, text="Running Monte Carlo...")
    for iteration in range(config.mc_iterations):
        rand_sens = {
            "conv": base_sens["conv"] + np.random.uniform(-mc_var, mc_var),
            "cpc": base_sens["cpc"] + np.random.uniform(-mc_var, mc_var),
            "aov": base_sens["aov"] + np.random.uniform(-mc_var, mc_var),
            "organic": base_sens["organic"] + np.random.uniform(-mc_var, mc_var),
        }
        mc_df, _ = run_ecom_model(config, rand_sens)
        mc_filtered = mc_df[(mc_df["Month"] >= start_m) & (mc_df["Month"] <= end_m)]
        mc_results.append({
            "Net Profit": mc_filtered["Net Profit"].sum(),
            "Total Revenue": mc_filtered["Net Revenue"].sum(),
            "End Orders": mc_filtered["Total Orders"].iloc[-1],
        })
        if (iteration + 1) % max(1, config.mc_iterations // 20) == 0:
            progress.progress((iteration + 1) / config.mc_iterations, text=f"Monte Carlo: {iteration + 1}/{config.mc_iterations}")
    progress.empty()

    mc_df_results = pd.DataFrame(mc_results)
    mc_c1, mc_c2, mc_c3 = st.columns(3)
    with mc_c1:
        fig_mc1 = px.histogram(mc_df_results, x="Net Profit", nbins=30, title="Net Profit Distribution")
        fig_mc1.add_vline(x=mc_df_results["Net Profit"].median(), line_dash="dash", line_color="red", annotation_text="Median")
        st.plotly_chart(fig_mc1, use_container_width=True)
    with mc_c2:
        fig_mc2 = px.histogram(mc_df_results, x="Total Revenue", nbins=30, title="Revenue Distribution")
        fig_mc2.add_vline(x=mc_df_results["Total Revenue"].median(), line_dash="dash", line_color="red", annotation_text="Median")
        st.plotly_chart(fig_mc2, use_container_width=True)
    with mc_c3:
        fig_mc3 = px.histogram(mc_df_results, x="End Orders", nbins=30, title="End Monthly Orders Distribution")
        fig_mc3.add_vline(x=mc_df_results["End Orders"].median(), line_dash="dash", line_color="red", annotation_text="Median")
        st.plotly_chart(fig_mc3, use_container_width=True)

    st.markdown("**Monte Carlo Summary**")
    mc_summary = mc_df_results.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
    mc_summary.columns = ["Count", "Mean", "Std", "Min", "P5", "P25", "Median", "P75", "P95", "Max"]
    st.dataframe(mc_summary[["Mean", "Median", "Std", "P5", "P25", "P75", "P95", "Min", "Max"]], use_container_width=True)
