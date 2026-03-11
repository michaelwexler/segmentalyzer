import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _attr_col(df: pd.DataFrame) -> str:
    """Find the attribute column name (first non-metric column)."""
    metric_cols = {
        "pct_segment", "pct_rest", "lift", "difference", "std_diff",
        "log_odds", "contribution", "pop_share",
        "count_segment", "total_segment", "count_rest", "total_rest",
    }
    for col in df.columns:
        if col.lower() not in metric_cols:
            return col
    return df.columns[0]


def _add_axes(fig: go.Figure, x0: bool = True, y1: bool = False) -> go.Figure:
    """Add solid zero-crossing axis lines to a figure."""
    if x0:
        fig.add_vline(x=0, line_dash="solid", line_color="black", line_width=1.5)
    if y1:
        fig.add_hline(y=1, line_dash="solid", line_color="black", line_width=1.5)
    return fig


def chart_lift_vs_difference(df: pd.DataFrame) -> go.Figure:
    attr = _attr_col(df)
    fig = px.scatter(
        df,
        x="difference",
        y="lift",
        hover_name=attr,
        labels={"difference": "Difference (% Segment − % Rest)", "lift": "Lift (×)"},
        title="Lift vs. Difference",
    )
    _add_axes(fig, x0=True, y1=True)
    return fig


def chart_std_diff_vs_pop_share(df: pd.DataFrame) -> go.Figure:
    attr = _attr_col(df)
    plot_df = df.dropna(subset=["std_diff", "pop_share"]).copy()
    plot_df["bubble_size"] = (plot_df["pop_share"] * 100).clip(lower=1)
    fig = px.scatter(
        plot_df,
        x="std_diff",
        y="pop_share",
        size="bubble_size",
        hover_name=attr,
        labels={
            "std_diff": "Std Diff",
            "pop_share": "Pop Share",
        },
        title="Std Diff vs. Pop Share",
    )
    _add_axes(fig, x0=True)
    return fig


def chart_log_odds_vs_pop_share(df: pd.DataFrame) -> go.Figure:
    attr = _attr_col(df)
    plot_df = df.dropna(subset=["log_odds", "pop_share"]).copy()
    plot_df["bubble_size"] = (plot_df["log_odds"].abs() * 50).clip(lower=1)
    fig = px.scatter(
        plot_df,
        x="log_odds",
        y="pop_share",
        size="bubble_size",
        hover_name=attr,
        labels={
            "log_odds": "Log Odds",
            "pop_share": "Pop Share",
        },
        title="Log Odds vs. Pop Share",
    )
    _add_axes(fig, x0=True)
    return fig
