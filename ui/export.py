"""CSV export buttons."""

import streamlit as st
import pandas as pd

from ui.components import fmt_milestone


def render_export_section(df_main, df_pessimistic, df_optimistic, milestones_main, milestones_pess, milestones_opt):
    """Render export buttons for CSV downloads."""
    st.markdown("---")
    st.header("Export Data")

    csv_base = df_main.to_csv(index=False).encode("utf-8")
    csv_pess = df_pessimistic.to_csv(index=False).encode("utf-8")
    csv_opt = df_optimistic.to_csv(index=False).encode("utf-8")

    # Combined all-scenarios CSV
    df_base_tagged = df_main.copy()
    df_base_tagged.insert(0, "Scenario", "Base")
    df_pess_tagged = df_pessimistic.copy()
    df_pess_tagged.insert(0, "Scenario", "Pessimistic")
    df_opt_tagged = df_optimistic.copy()
    df_opt_tagged.insert(0, "Scenario", "Optimistic")
    df_all = pd.concat([df_base_tagged, df_pess_tagged, df_opt_tagged], ignore_index=True)

    # Milestones summary
    ms_rows = []
    for scenario, ms in [("Base", milestones_main), ("Pessimistic", milestones_pess), ("Optimistic", milestones_opt)]:
        row = {"Scenario": scenario}
        for key, label in [
            ("break_even_month", "Break-Even Month"), ("cumulative_break_even", "Cumulative Break-Even"),
            ("cf_positive_month", "CF Positive Month"), ("investment_payback_month", "Investment Payback"),
            ("runway_out_month", "Runway Out"), ("users_1000", "1K Users Month"),
            ("users_10000", "10K Users Month"), ("users_100000", "100K Users Month"),
            ("mrr_10000", "MRR $10K Month"), ("mrr_50000", "MRR $50K Month"),
            ("mrr_100000", "MRR $100K Month"), ("mrr_1000000", "MRR $1M Month"),
        ]:
            row[label] = ms.get(key, None)
        ms_rows.append(row)
    df_milestones = pd.DataFrame(ms_rows)

    csv_all = df_all.to_csv(index=False).encode("utf-8")
    csv_milestones = df_milestones.to_csv(index=False).encode("utf-8")

    exp_c1, exp_c2, exp_c3, exp_c4, exp_c5 = st.columns(5)
    exp_c1.download_button("Base (CSV)", csv_base, "base_scenario.csv", "text/csv")
    exp_c2.download_button("Pessimistic (CSV)", csv_pess, "pessimistic_scenario.csv", "text/csv")
    exp_c3.download_button("Optimistic (CSV)", csv_opt, "optimistic_scenario.csv", "text/csv")
    exp_c4.download_button("All Scenarios (CSV)", csv_all, "all_scenarios.csv", "text/csv")
    exp_c5.download_button("Milestones (CSV)", csv_milestones, "milestones.csv", "text/csv")
