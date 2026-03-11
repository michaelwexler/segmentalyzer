import streamlit as st

from seg_source.loader import load_csv, load_google_sheet, detect_and_normalize
from seg_source.calculations import compute_metrics
from seg_source.charts import (
    chart_lift_vs_difference,
    chart_std_diff_vs_pop_share,
    chart_log_odds_vs_pop_share,
)

st.set_page_config(page_title="Segmentalyzer", layout="wide")
st.title("Segmentalyzer")
st.caption(
    "Compare two segments and discover which attribute differences actually matter."
)

# ── Data Input ────────────────────────────────────────────────────────────────

if "raw_df" not in st.session_state:
    st.header("1. Load Data")
    tab_csv, tab_sheets = st.tabs(["Upload CSV", "Google Sheet URL"])

    with tab_csv:
        uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
        if uploaded:
            st.session_state["raw_df"] = load_csv(uploaded)
            st.rerun()

    with tab_sheets:
        col_url, col_go = st.columns([5, 1])
        with col_url:
            sheet_url = st.text_input("Paste a public Google Sheets URL", label_visibility="collapsed")
        with col_go:
            go_clicked = st.button("Go", use_container_width=True)
        if go_clicked and sheet_url:
            try:
                st.session_state["raw_df"] = load_google_sheet(sheet_url)
                st.rerun()
            except Exception as e:
                st.error(f"Could not load sheet: {e}")
        elif go_clicked and not sheet_url:
            st.warning("Please enter a Google Sheets URL first.")

    st.info(
        "Expected CSV formats:\n\n"
        "**Format A** (pre-aggregated): `attribute, pct_segment, pct_rest`\n\n"
        "**Format B** (raw counts): `attribute, count_segment, total_segment, count_rest, total_rest`"
    )
    st.stop()

raw_df = st.session_state["raw_df"]

col_status, col_reset = st.columns([6, 1])
with col_status:
    st.success(f"Loaded {len(raw_df):,} rows.")
with col_reset:
    if st.button("Reset", use_container_width=True):
        del st.session_state["raw_df"]
        st.rerun()

# ── Normalize & Compute ───────────────────────────────────────────────────────

try:
    df, fmt = detect_and_normalize(raw_df)
except ValueError as e:
    st.error(str(e))
    st.stop()

st.caption(f"Detected: {fmt}")
df = compute_metrics(df)

# ── Results Table ─────────────────────────────────────────────────────────────

st.header("2. Results")

max_diff = float(df["difference"].abs().max())
threshold = st.slider(
    "Minimum |Difference| to show",
    min_value=0.0,
    max_value=max(max_diff, 0.01),
    value=0.0,
    step=0.01,
    format="%.2f",
)

display_df = df[df["difference"].abs() >= threshold].copy()

# Find attribute column
metric_cols = {
    "pct_segment", "pct_rest", "lift", "difference", "std_diff",
    "log_odds", "contribution", "pop_share",
    "count_segment", "total_segment", "count_rest", "total_rest",
}
attr_col = next(
    (c for c in display_df.columns if c.lower() not in metric_cols),
    display_df.columns[0],
)

# Column order: attribute → raw scores → metrics (pop_share excluded from table)
ordered_cols = [attr_col, "pct_segment", "pct_rest", "difference", "lift",
                "std_diff", "log_odds", "contribution"]
show_cols = [c for c in ordered_cols if c in display_df.columns]

rename_map = {
    "pct_segment": "% Segment",
    "pct_rest": "% Rest",
    "difference": "Difference (pct pts)",
    "lift": "Lift",
    "std_diff": "Std Diff",
    "log_odds": "Log Odds",
    "contribution": "Contribution",
}

# Scale percentage columns to 0–100 for display
table_df = display_df[show_cols].copy()
for col in ["pct_segment", "pct_rest", "difference"]:
    if col in table_df.columns:
        table_df[col] = table_df[col] * 100

table_df = (
    table_df
    .rename(columns=rename_map)
    .sort_values("Difference (pct pts)", ascending=False, key=abs)
    .reset_index(drop=True)
)

st.dataframe(
    table_df,
    column_config={
        "% Segment":  st.column_config.NumberColumn(format="%.1f%%"),
        "% Rest":     st.column_config.NumberColumn(format="%.1f%%"),
        "Difference (pct pts)": st.column_config.NumberColumn(format="%+.1f"),
        "Lift":       st.column_config.NumberColumn(format="%.2f\u00d7"),
        "Std Diff":   st.column_config.NumberColumn(format="%.2f"),
        "Log Odds":   st.column_config.NumberColumn(format="%.2f"),
        "Contribution": st.column_config.NumberColumn(format="%.4f"),
    },
    width="stretch",
)

st.caption(
    f"Showing {len(display_df):,} of {len(df):,} attributes. "
    "**Pop Share** (used in charts) = average of % Segment and % Rest — "
    "a proxy for how common the attribute is overall."
)

# ── Charts ────────────────────────────────────────────────────────────────────

st.header("3. Visualizations")
chart1, chart2, chart3 = st.tabs(
    ["Lift vs. Difference", "Std Diff vs. Pop Share", "Log Odds vs. Pop Share"]
)

with chart1:
    st.plotly_chart(chart_lift_vs_difference(display_df), width="stretch")

with chart2:
    st.plotly_chart(chart_std_diff_vs_pop_share(display_df), width="stretch")

with chart3:
    st.plotly_chart(chart_log_odds_vs_pop_share(display_df), width="stretch")
