"""All Plotly chart tabs."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from ui.components import add_phase_lines, add_milestone_markers


# Milestone marker sets
MS_FINANCIAL = [("break_even_month", "BE"), ("cumulative_break_even", "Cum.BE"), ("runway_out_month", "Runway Out")]
MS_USERS = [("users_1000", "1K"), ("users_10000", "10K"), ("users_100000", "100K")]
MS_MRR = [("mrr_10000", "$10K"), ("mrr_50000", "$50K"), ("mrr_100000", "$100K")]


def render_charts(f_df, f_pess, f_opt, milestones_main, p1_end, p2_end, config):
    """Render all 4 chart tabs."""
    tab1, tab2, tab3, tab4 = st.tabs(["Growth & Revenue", "Unit Economics & Efficiency", "P&L & Scenarios", "Cohorts & Deep Dive"])

    with tab1:
        _render_growth_revenue_tab(f_df, f_pess, f_opt, milestones_main, p1_end, p2_end)

    with tab2:
        _render_unit_economics_tab(f_df, f_pess, f_opt, milestones_main, p1_end, p2_end)

    with tab3:
        _render_pnl_scenarios_tab(f_df, f_pess, f_opt, milestones_main, p1_end, p2_end)

    with tab4:
        _render_cohorts_deep_dive_tab(f_df, f_pess, f_opt, milestones_main, p1_end, p2_end, config)


def _render_growth_revenue_tab(f_df, f_pess, f_opt, ms, p1_end, p2_end):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("MRR by Subscription Plan")
        st.caption("Ежемесячная повторяющаяся выручка (MRR) в разбивке по типам подписок. Показывает вклад каждого плана в общий MRR и помогает понять зависимость от конкретного типа подписки.")
        fig1 = go.Figure()
        for col, name in [("MRR Weekly", "Weekly"), ("MRR Monthly", "Monthly"), ("MRR Annual", "Annual")]:
            fig1.add_trace(go.Scatter(x=f_df["Month"], y=f_df[col], mode="lines", stackgroup="one", name=f"{name} (Base)"))
            fig1.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess[col], mode="lines", line=dict(dash="dot"), name=f"{name} (Pess)", visible="legendonly"))
            fig1.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt[col], mode="lines", line=dict(dash="dash"), name=f"{name} (Opt)", visible="legendonly"))
        fig1.update_layout(title="MRR Breakdown")
        add_phase_lines(fig1, p1_end, p2_end)
        add_milestone_markers(fig1, ms, MS_MRR, color="purple")
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("Cash Balance")
        st.caption("Остаток денег на счёте с учётом инвестиций, доходов и всех расходов. Красная линия на нуле — если столбцы опускаются ниже, значит деньги закончились.")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=f_df["Month"], y=f_df["Cash Balance"], name="Base"))
        fig2.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["Cash Balance"], mode="lines", line=dict(dash="dot", color="red"), name="Pessimistic"))
        fig2.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["Cash Balance"], mode="lines", line=dict(dash="dash", color="green"), name="Optimistic"))
        fig2.add_hline(y=0, line_dash="dash", line_color="red")
        add_phase_lines(fig2, p1_end, p2_end)
        add_milestone_markers(fig2, ms, MS_FINANCIAL, color="orange")
        fig2.update_layout(title="Cash Balance (3 Scenarios)")
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Gross vs Net Revenue")
        st.caption("Сравнение валовой выручки (до вычета комиссий) и чистой выручки (после вычета комиссий App Store, Web, банков). Разница между ними — это комиссии платёжных систем.")
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=f_df["Month"], y=f_df["Gross Revenue Web"], name="Gross Web"))
        fig4.add_trace(go.Bar(x=f_df["Month"], y=f_df["Gross Revenue Store"], name="Gross Store"))
        fig4.add_trace(go.Bar(x=f_df["Month"], y=f_df["Net Revenue"], name="Net Revenue"))
        fig4.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["Net Revenue"], mode="lines", line=dict(dash="dot", color="red"), name="Net Rev (Pess)", visible="legendonly"))
        fig4.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["Net Revenue"], mode="lines", line=dict(dash="dash", color="green"), name="Net Rev (Opt)", visible="legendonly"))
        fig4.update_layout(barmode="group", title="Revenue Comparison (3 Scenarios)")
        add_phase_lines(fig4, p1_end, p2_end)
        st.plotly_chart(fig4, use_container_width=True)

    with c4:
        st.subheader("Churn Rates by Subscription Type")
        st.caption("Процент оттока подписчиков по каждому типу плана. Weekly и Monthly — ежемесячный отток, Annual — годовая доля неперподписок. Учитывает множитель фазы.")
        fig6 = go.Figure()
        for col in ["Weekly Churn %", "Monthly Churn %", "Annual Non-Renewal %"]:
            fig6.add_trace(go.Scatter(x=f_df["Month"], y=f_df[col], mode="lines", name=f"{col} (Base)"))
            fig6.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess[col], mode="lines", line=dict(dash="dot"), name=f"{col} (Pess)", visible="legendonly"))
            fig6.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt[col], mode="lines", line=dict(dash="dash"), name=f"{col} (Opt)", visible="legendonly"))
        fig6.update_layout(title="Churn Rates (3 Scenarios)")
        add_phase_lines(fig6, p1_end, p2_end)
        st.plotly_chart(fig6, use_container_width=True)

    # Deferred Revenue & Active Users
    c3b, c4b = st.columns(2)
    with c3b:
        st.subheader("Deferred Revenue")
        st.caption("Отложенная выручка — деньги, полученные от annual-подписчиков авансом, но ещё не признанные как выручка. Растёт при увеличении доли годовых подписок.")
        fig_def = go.Figure()
        fig_def.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Deferred Revenue"], mode="lines+markers", name="Deferred Revenue (Base)", fill="tozeroy"))
        fig_def.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["Deferred Revenue"], mode="lines", line=dict(dash="dot"), name="Pess", visible="legendonly"))
        fig_def.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["Deferred Revenue"], mode="lines", line=dict(dash="dash"), name="Opt", visible="legendonly"))
        fig_def.update_layout(title="Deferred Revenue (Collected but Unrecognized)")
        add_phase_lines(fig_def, p1_end, p2_end)
        st.plotly_chart(fig_def, use_container_width=True)

    with c4b:
        st.subheader("Active Users")
        st.caption("Общее количество активных подписчиков (все планы). Маркеры показывают достижение ключевых отметок (1K, 10K, 100K пользователей).")
        fig_users = go.Figure()
        fig_users.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Total Active Users"], mode="lines", name="Users (Base)"))
        fig_users.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["Total Active Users"], mode="lines", line=dict(dash="dot", color="red"), name="Users (Pess)"))
        fig_users.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["Total Active Users"], mode="lines", line=dict(dash="dash", color="green"), name="Users (Opt)"))
        fig_users.update_layout(title="Total Active Users (3 Scenarios)")
        add_phase_lines(fig_users, p1_end, p2_end)
        add_milestone_markers(fig_users, ms, MS_USERS, color="blue")
        st.plotly_chart(fig_users, use_container_width=True)


def _render_unit_economics_tab(f_df, f_pess, f_opt, ms, p1_end, p2_end):
    c5, c6 = st.columns(2)
    with c5:
        st.subheader("LTV vs CAC")
        st.caption("Пожизненная ценность клиента (LTV) vs стоимость привлечения (CAC). Когда LTV выше CAC — юнит-экономика положительная. Формула LTV = ARPU × Gross Margin / Churn.")
        fig3 = go.Figure()
        for col in ["LTV", "Paid CAC", "Organic CAC", "Blended CAC"]:
            fig3.add_trace(go.Scatter(x=f_df["Month"], y=f_df[col], mode="lines", name=f"{col} (Base)"))
            fig3.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess[col], mode="lines", line=dict(dash="dot"), name=f"{col} (Pess)", visible="legendonly"))
            fig3.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt[col], mode="lines", line=dict(dash="dash"), name=f"{col} (Opt)", visible="legendonly"))
        fig3.update_layout(title="LTV vs CAC (3 Scenarios)")
        add_phase_lines(fig3, p1_end, p2_end)
        st.plotly_chart(fig3, use_container_width=True)

    with c6:
        st.subheader("Payback Period")
        st.caption("Срок окупаемости одного пользователя в месяцах. Показывает через сколько месяцев выручка от подписчика покроет затраты на его привлечение. Формула: CAC / (ARPU × Gross Margin).")
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Payback Period (Months)"], mode="lines", name="Base"))
        fig5.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["Payback Period (Months)"], mode="lines", line=dict(dash="dot"), name="Pessimistic"))
        fig5.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["Payback Period (Months)"], mode="lines", line=dict(dash="dash"), name="Optimistic"))
        fig5.update_layout(title="Payback Period (3 Scenarios)")
        add_phase_lines(fig5, p1_end, p2_end)
        st.plotly_chart(fig5, use_container_width=True)

    c7, c8 = st.columns(2)
    with c7:
        st.subheader("MER & ROAS")
        st.caption("Эффективность маркетинга. MER = Выручка / Весь маркетинг (включая органик). ROAS = Выручка / Рекламный бюджет (только платная реклама). Значение >1 означает, что реклама приносит больше, чем стоит.")
        fig8 = go.Figure()
        fig8.add_trace(go.Scatter(x=f_df["Month"], y=f_df["MER"], mode="lines", name="MER (Base)"))
        fig8.add_trace(go.Scatter(x=f_df["Month"], y=f_df["ROAS"], mode="lines", name="ROAS (Base)"))
        fig8.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["MER"], mode="lines", line=dict(dash="dot"), name="MER (Pess)", visible="legendonly"))
        fig8.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["ROAS"], mode="lines", line=dict(dash="dot"), name="ROAS (Pess)", visible="legendonly"))
        fig8.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["MER"], mode="lines", line=dict(dash="dash"), name="MER (Opt)", visible="legendonly"))
        fig8.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["ROAS"], mode="lines", line=dict(dash="dash"), name="ROAS (Opt)", visible="legendonly"))
        fig8.update_layout(title="Marketing Efficiency (3 Scenarios)")
        add_phase_lines(fig8, p1_end, p2_end)
        st.plotly_chart(fig8, use_container_width=True)

    with c8:
        st.subheader("MRR Movement Waterfall")
        st.caption("Из чего складывается изменение MRR за весь период. New MRR — от новых подписчиков, Expansion — апгрейды, Contraction — даунгрейды, Churned — ушедшие. Итог — Net New MRR.")
        fig_mrr_w = go.Figure(go.Waterfall(
            name="MRR Movement", orientation="v",
            measure=["relative", "relative", "relative", "relative", "total"],
            x=["New MRR", "Expansion", "Contraction", "Churned", "Net New MRR"],
            y=[f_df["New MRR"].sum(), f_df["Expansion MRR"].sum(),
               -f_df["Contraction MRR"].sum(), -f_df["Churned MRR"].sum(),
               f_df["Net New MRR"].sum()],
            connector={"line": {"color": "rgb(63, 63, 63)"}}
        ))
        fig_mrr_w.update_layout(title="MRR Movement (Period Total)")
        st.plotly_chart(fig_mrr_w, use_container_width=True)

    # Unit Economics Over Time
    st.subheader("Unit Economics Over Time")
    st.caption("Ключевые юнит-метрики на одном графике: ARPU (доход с пользователя), CAC (стоимость привлечения), LTV (пожизненная ценность) и Payback (срок окупаемости, правая ось).")
    fig_ue = go.Figure()
    fig_ue.add_trace(go.Scatter(x=f_df["Month"], y=f_df["ARPU"], mode="lines", name="ARPU"))
    fig_ue.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Blended CAC"], mode="lines", name="Blended CAC"))
    fig_ue.add_trace(go.Scatter(x=f_df["Month"], y=f_df["LTV"], mode="lines", name="LTV"))
    fig_ue.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Payback Period (Months)"], mode="lines", name="Payback (months)", yaxis="y2"))
    fig_ue.update_layout(
        title="ARPU / CAC / LTV / Payback",
        yaxis=dict(title="$ Value"),
        yaxis2=dict(title="Payback (months)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    add_phase_lines(fig_ue, p1_end, p2_end)
    add_milestone_markers(fig_ue, ms, MS_FINANCIAL, color="orange")
    st.plotly_chart(fig_ue, use_container_width=True)


def _render_pnl_scenarios_tab(f_df, f_pess, f_opt, ms, p1_end, p2_end):
    c9, c10 = st.columns(2)
    with c9:
        st.subheader("P&L Waterfall")
        st.caption("Каскадная диаграмма отчёта о прибылях и убытках. Показывает как из выручки последовательно вычитаются расходы.")
        fig7 = go.Figure(go.Waterfall(
            name="P&L", orientation="v",
            measure=["relative", "relative", "relative", "relative", "relative", "total"],
            x=["Revenue", "COGS", "Marketing", "Salaries & Misc", "Commissions & Tax", "Net Profit"],
            y=[f_df["Total Gross Revenue"].sum(), -f_df["COGS"].sum(), -f_df["Marketing"].sum(),
               -(f_df["Salaries"].sum() + f_df["Misc Costs"].sum()),
               -(f_df["Total Commissions"].sum() + f_df["Corporate Tax"].sum()),
               f_df["Net Profit"].sum()],
            connector={"line": {"color": "rgb(63, 63, 63)"}}
        ))
        fig7.update_layout(title="P&L Waterfall")
        st.plotly_chart(fig7, use_container_width=True)

    with c10:
        st.subheader("Scenario Comparison")
        st.caption("Сравнение итоговых показателей по трём сценариям. Переключайте метрики через легенду.")
        metrics_names = ["Net Profit", "Total Revenue", "End MRR", "End Users"]
        scenario_data = []
        for label, sdf in [("Pessimistic", f_pess), ("Base", f_df), ("Optimistic", f_opt)]:
            scenario_data.append({
                "Scenario": label,
                "Net Profit": sdf["Net Profit"].sum(),
                "Total Revenue": sdf["Total Gross Revenue"].sum(),
                "End MRR": sdf["Total MRR"].iloc[-1],
                "End Users": sdf["Total Active Users"].iloc[-1],
            })
        sc_df = pd.DataFrame(scenario_data)

        fig9 = go.Figure()
        for metric in metrics_names:
            fig9.add_trace(go.Bar(
                x=sc_df["Scenario"], y=sc_df[metric], name=metric,
                visible=True if metric == "Net Profit" else "legendonly"
            ))
        fig9.update_layout(title="Scenario Comparison", barmode="group")
        st.plotly_chart(fig9, use_container_width=True)

    c11, c12 = st.columns(2)
    with c11:
        st.subheader("Cumulative Net Profit")
        st.caption("Накопленная чистая прибыль нарастающим итогом. Момент пересечения нуля — точка кумулятивной безубыточности.")
        fig_roi = go.Figure()
        fig_roi.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Cumulative Net Profit"], mode="lines", name="Base"))
        fig_roi.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["Cumulative Net Profit"], mode="lines", line=dict(dash="dot", color="red"), name="Pessimistic"))
        fig_roi.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["Cumulative Net Profit"], mode="lines", line=dict(dash="dash", color="green"), name="Optimistic"))
        fig_roi.add_hline(y=0, line_dash="dash", line_color="red")
        add_phase_lines(fig_roi, p1_end, p2_end)
        add_milestone_markers(fig_roi, ms, [("cumulative_break_even", "Cum.BE"), ("investment_payback_month", "Payback")], color="green")
        fig_roi.update_layout(title="Cumulative Net Profit (3 Scenarios)")
        st.plotly_chart(fig_roi, use_container_width=True)

    with c12:
        st.subheader("NRR & Quick Ratio")
        st.caption("NRR (левая ось) — сколько % выручки удерживается от существующих пользователей. Quick Ratio (правая ось) — отношение роста MRR к потерям.")
        fig_nrr = go.Figure()
        fig_nrr.add_trace(go.Scatter(x=f_df["Month"], y=f_df["NRR %"], mode="lines", name="NRR % (Base)"))
        fig_nrr.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["NRR %"], mode="lines", line=dict(dash="dot"), name="NRR % (Pess)", visible="legendonly"))
        fig_nrr.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["NRR %"], mode="lines", line=dict(dash="dash"), name="NRR % (Opt)", visible="legendonly"))
        fig_nrr.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Quick Ratio"], mode="lines", name="Quick Ratio", yaxis="y2"))
        fig_nrr.add_hline(y=100, line_dash="dash", line_color="gray")
        fig_nrr.update_layout(
            title="NRR & Quick Ratio",
            yaxis=dict(title="NRR %"),
            yaxis2=dict(title="Quick Ratio", overlaying="y", side="right"),
        )
        add_phase_lines(fig_nrr, p1_end, p2_end)
        st.plotly_chart(fig_nrr, use_container_width=True)


def _render_cohorts_deep_dive_tab(f_df, f_pess, f_opt, ms, p1_end, p2_end, config):
    total_months = config.total_months

    # Cohort Retention Heatmap — needs retention_matrix from session state
    retention_main = st.session_state.get("retention_main")
    if retention_main is not None:
        st.subheader("Cohort Retention Heatmap")
        st.caption("Тепловая карта удержания когорт. Строки — когорты по месяцу привлечения, столбцы — текущий месяц. Цвет показывает % пользователей, оставшихся от начального размера когорты.")
        max_cohorts = min(total_months, 30)
        step = max(1, total_months // max_cohorts)
        cohort_indices = list(range(0, total_months, step))
        retention_display = retention_main[np.ix_(cohort_indices, range(total_months))]
        heatmap_data = []
        heatmap_y = []
        for idx, ci in enumerate(cohort_indices):
            row = []
            for j in range(total_months):
                if j >= ci and retention_display[idx, j] > 0:
                    row.append(round(retention_display[idx, j], 1))
                else:
                    row.append(None)
            heatmap_data.append(row)
            heatmap_y.append(f"M{ci + 1}")

        fig_hm = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=[f"M{m}" for m in range(1, total_months + 1)],
            y=heatmap_y,
            colorscale="RdYlGn",
            zmin=0, zmax=100,
            text=[[f"{v:.0f}%" if v is not None else "" for v in row] for row in heatmap_data],
            texttemplate="%{text}",
            colorbar=dict(title="Retention %"),
            hoverongaps=False,
        ))
        fig_hm.update_layout(
            title="Cohort Retention (% of initial cohort remaining)",
            xaxis_title="Month",
            yaxis_title="Cohort Start",
            height=500,
        )
        st.plotly_chart(fig_hm, use_container_width=True)
        st.caption("Строки — когорты (месяц привлечения). Столбцы — текущий месяц. Значение — % оставшихся пользователей от начального размера когорты.")

    # MRR Movement Over Time & ROI
    c_dd1, c_dd2 = st.columns(2)
    with c_dd1:
        st.subheader("MRR Movement Over Time")
        st.caption("Помесячная динамика изменений MRR. Зелёные столбцы — новый MRR и апгрейды. Красные — отток и даунгрейды. Чёрная линия — чистый прирост MRR.")
        fig_mrr_t = go.Figure()
        fig_mrr_t.add_trace(go.Bar(x=f_df["Month"], y=f_df["New MRR"], name="New MRR", marker_color="green"))
        fig_mrr_t.add_trace(go.Bar(x=f_df["Month"], y=f_df["Expansion MRR"], name="Expansion MRR", marker_color="lightgreen"))
        fig_mrr_t.add_trace(go.Bar(x=f_df["Month"], y=-f_df["Contraction MRR"], name="Contraction MRR", marker_color="orange"))
        fig_mrr_t.add_trace(go.Bar(x=f_df["Month"], y=-f_df["Churned MRR"], name="Churned MRR", marker_color="red"))
        fig_mrr_t.add_trace(go.Scatter(x=f_df["Month"], y=f_df["Net New MRR"], mode="lines+markers", name="Net New MRR", line=dict(color="black", width=2)))
        fig_mrr_t.update_layout(barmode="relative", title="MRR Movement by Month")
        add_phase_lines(fig_mrr_t, p1_end, p2_end)
        st.plotly_chart(fig_mrr_t, use_container_width=True)

    with c_dd2:
        st.subheader("ROI % Over Time")
        st.caption("Кумулятивный ROI — возврат на инвестиции нарастающим итогом. Когда линия пересекает 0% — инвестиции начинают окупаться.")
        fig_roi_t = go.Figure()
        fig_roi_t.add_trace(go.Scatter(x=f_df["Month"], y=f_df["ROI %"], mode="lines", name="ROI % (Base)"))
        fig_roi_t.add_trace(go.Scatter(x=f_pess["Month"], y=f_pess["ROI %"], mode="lines", line=dict(dash="dot", color="red"), name="ROI % (Pess)"))
        fig_roi_t.add_trace(go.Scatter(x=f_opt["Month"], y=f_opt["ROI %"], mode="lines", line=dict(dash="dash", color="green"), name="ROI % (Opt)"))
        fig_roi_t.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_roi_t.update_layout(title="Cumulative ROI % (3 Scenarios)")
        add_phase_lines(fig_roi_t, p1_end, p2_end)
        st.plotly_chart(fig_roi_t, use_container_width=True)


def render_monte_carlo(config, base_sens, start_m, end_m):
    """Render Monte Carlo simulation section."""
    from core.engine import run_model

    st.markdown("---")
    st.header("Monte Carlo Simulation")
    st.caption("Моделирование случайных отклонений параметров для оценки диапазона возможных результатов.")
    np.random.seed(42)
    mc_results = []
    mc_var = config.mc_variance / 100.0
    progress = st.progress(0, text="Running Monte Carlo...")
    for iteration in range(config.mc_iterations):
        rand_sens = {
            "conv": base_sens["conv"] + np.random.uniform(-mc_var, mc_var),
            "churn": base_sens["churn"] + np.random.uniform(-mc_var, mc_var),
            "cpi": base_sens["cpi"] + np.random.uniform(-mc_var, mc_var),
            "organic": base_sens["organic"] + np.random.uniform(-mc_var, mc_var),
        }
        mc_df, _, _ = run_model(config, rand_sens)
        mc_filtered = mc_df[(mc_df["Month"] >= start_m) & (mc_df["Month"] <= end_m)]
        mc_results.append({
            "Net Profit": mc_filtered["Net Profit"].sum(),
            "Total Revenue": mc_filtered["Total Gross Revenue"].sum(),
            "End MRR": mc_filtered["Total MRR"].iloc[-1],
        })
        if (iteration + 1) % max(1, config.mc_iterations // 20) == 0:
            progress.progress((iteration + 1) / config.mc_iterations, text=f"Monte Carlo: {iteration + 1}/{config.mc_iterations}")
    progress.empty()

    mc_df_results = pd.DataFrame(mc_results)
    mc_c1, mc_c2, mc_c3 = st.columns(3)
    with mc_c1:
        fig_mc1 = px.histogram(mc_df_results, x="Net Profit", nbins=30, title="Net Profit Distribution")
        fig_mc1.add_vline(x=mc_df_results["Net Profit"].median(), line_dash="dash", line_color="red",
                          annotation_text="Median")
        st.plotly_chart(fig_mc1, use_container_width=True)
    with mc_c2:
        fig_mc2 = px.histogram(mc_df_results, x="Total Revenue", nbins=30, title="Revenue Distribution")
        fig_mc2.add_vline(x=mc_df_results["Total Revenue"].median(), line_dash="dash", line_color="red",
                          annotation_text="Median")
        st.plotly_chart(fig_mc2, use_container_width=True)
    with mc_c3:
        fig_mc3 = px.histogram(mc_df_results, x="End MRR", nbins=30, title="End MRR Distribution")
        fig_mc3.add_vline(x=mc_df_results["End MRR"].median(), line_dash="dash", line_color="red",
                          annotation_text="Median")
        st.plotly_chart(fig_mc3, use_container_width=True)

    st.markdown("**Monte Carlo Summary**")
    mc_summary = mc_df_results.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
    mc_summary.columns = ["Count", "Mean", "Std", "Min", "P5", "P25", "Median", "P75", "P95", "Max"]
    st.dataframe(mc_summary[["Mean", "Median", "Std", "P5", "P25", "P75", "P95", "Min", "Max"]], use_container_width=True)
