import numpy as np
import pandas as pd


def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame with pct_segment and pct_rest columns (values 0-1),
    compute all 5 metrics and return the enriched DataFrame.
    """
    p1 = df["pct_segment"]
    p2 = df["pct_rest"]
    p_avg = (p1 + p2) / 2

    # Lift: p1 / p2 (undefined when p2 = 0)
    df["lift"] = np.where(p2 == 0, np.nan, p1 / p2)

    # Difference: bounded -1 to +1
    df["difference"] = p1 - p2

    # Standardized difference
    denom = np.sqrt(p_avg * (1 - p_avg))
    df["std_diff"] = np.where(denom == 0, np.nan, (p1 - p2) / denom)

    # Log odds ratio: clip to avoid log(0) or log(inf)
    p1c = p1.clip(0.001, 0.999)
    p2c = p2.clip(0.001, 0.999)
    df["log_odds"] = np.log((p1c / (1 - p1c)) / (p2c / (1 - p2c)))

    # Contribution: driver analysis weighted by population share
    df["contribution"] = (p1 - p2) * p_avg

    # Population share (used for bubble sizing)
    df["pop_share"] = p_avg

    return df
