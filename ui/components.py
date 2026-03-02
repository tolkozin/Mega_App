"""Shared UI helper functions — phase lines, milestone markers, health indicators."""

import numpy as np


def add_phase_lines(fig, p1_end, p2_end):
    """Add phase boundary vertical lines to a Plotly figure."""
    fig.add_vline(x=p1_end + 0.5, line_dash="dot", line_color="gray",
                  annotation_text="Phase 2", annotation_position="top")
    fig.add_vline(x=p2_end + 0.5, line_dash="dot", line_color="gray",
                  annotation_text="Phase 3", annotation_position="top")
    return fig


def add_milestone_markers(fig, ms, keys_labels, color="orange"):
    """Add milestone vertical markers to a Plotly figure."""
    for key, label in keys_labels:
        val = ms.get(key)
        if val is not None:
            fig.add_vline(x=val, line_dash="dashdot", line_color=color, line_width=1,
                          annotation_text=label, annotation_position="bottom",
                          annotation_font_size=9, annotation_font_color=color)


def health_indicator(value, good_threshold, bad_threshold, higher_is_better=True):
    """Return colored status emoji based on thresholds."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "⚪ N/A"
    if higher_is_better:
        if value >= good_threshold:
            return f"🟢 {value:,.1f}" if isinstance(value, float) else f"🟢 {value:,}"
        elif value >= bad_threshold:
            return f"🟡 {value:,.1f}" if isinstance(value, float) else f"🟡 {value:,}"
        else:
            return f"🔴 {value:,.1f}" if isinstance(value, float) else f"🔴 {value:,}"
    else:
        if value <= good_threshold:
            return f"🟢 {value:,.1f}" if isinstance(value, float) else f"🟢 {value:,}"
        elif value <= bad_threshold:
            return f"🟡 {value:,.1f}" if isinstance(value, float) else f"🟡 {value:,}"
        else:
            return f"🔴 {value:,.1f}" if isinstance(value, float) else f"🔴 {value:,}"


def fmt_milestone(val, suffix="мес."):
    """Format a milestone value for display."""
    return f"{val} {suffix}" if val is not None else "—"
