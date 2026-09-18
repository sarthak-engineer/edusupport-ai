from __future__ import annotations

import pandas as pd


def filter_by_date_range(
    df: pd.DataFrame,
    *,
    start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Filter tickets by created_at date range."""

    result = df.copy()

    if start is not None:
        result = result[result["created_at"] >= start]

    if end is not None:
        result = result[result["created_at"] <= end]

    return result
