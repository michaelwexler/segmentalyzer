import io
import re

import pandas as pd
import requests


def load_csv(file) -> pd.DataFrame:
    """Load a CSV from a file-like object (e.g. st.file_uploader result)."""
    return pd.read_csv(file)


def load_google_sheet(url: str) -> pd.DataFrame:
    """
    Load a public Google Sheet as a DataFrame.
    Accepts any standard Google Sheets URL and converts it to a CSV export URL.
    """
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError("Could not find a spreadsheet ID in the URL.")
    sheet_id = match.group(1)

    gid_match = re.search(r"gid=(\d+)", url)
    gid = gid_match.group(1) if gid_match else "0"

    export_url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        f"/export?format=csv&gid={gid}"
    )
    response = requests.get(export_url, timeout=15)
    response.raise_for_status()
    return pd.read_csv(io.StringIO(response.text))


def detect_and_normalize(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """
    Detect the CSV format and return a normalized DataFrame with
    pct_segment and pct_rest columns (values 0-1), plus a description
    of which format was detected.

    Returns (normalized_df, format_description)
    Raises ValueError if the format cannot be determined.
    """
    cols = {c.strip().lower() for c in df.columns}

    # Format A: pre-aggregated percentages
    if "pct_segment" in cols and "pct_rest" in cols:
        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]
        # Auto-detect if values are 0-100 scale
        if df["pct_segment"].max() > 1.5 or df["pct_rest"].max() > 1.5:
            df["pct_segment"] = df["pct_segment"] / 100
            df["pct_rest"] = df["pct_rest"] / 100
        return df, "Format A (pre-aggregated percentages)"

    # Format B: raw counts
    if all(c in cols for c in ("count_segment", "total_segment", "count_rest", "total_rest")):
        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]
        df["pct_segment"] = df["count_segment"] / df["total_segment"]
        df["pct_rest"] = df["count_rest"] / df["total_rest"]
        return df, "Format B (raw counts)"

    raise ValueError(
        "Could not detect CSV format. Expected columns:\n"
        "  Format A: attribute, pct_segment, pct_rest\n"
        "  Format B: attribute, count_segment, total_segment, count_rest, total_rest"
    )
