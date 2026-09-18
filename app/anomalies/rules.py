from __future__ import annotations

import pandas as pd


def detect_stale_high_priority(df: pd.DataFrame) -> pd.DataFrame:
    """Find unresolved High/Critical tickets older than 24 hours."""

    reference_time = df["created_at"].max()

    result = df[
        df["priority"].isin(["High", "Critical"])
        & df["status"].isin(["Open", "Escalated"])
        & (
            (reference_time - df["created_at"])
            >= pd.Timedelta(hours=24)
        )
    ].copy()

    return result


def detect_resolution_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Detect unusually long resolution times using IQR."""

    resolved = df[
        df["resolution_time_hrs"].notna()
    ].copy()

    if resolved.empty:
        return resolved

    q1 = resolved["resolution_time_hrs"].quantile(0.25)
    q3 = resolved["resolution_time_hrs"].quantile(0.75)

    iqr = q3 - q1
    upper_bound = q3 + (1.5 * iqr)

    return resolved[
        resolved["resolution_time_hrs"] > upper_bound
    ].copy()


def detect_customer_experience_anomalies(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Find low-rated tickets with above-median resolution time."""

    resolved = df[
        df["customer_rating"].notna()
        & df["resolution_time_hrs"].notna()
    ].copy()

    if resolved.empty:
        return resolved

    median_resolution = resolved[
        "resolution_time_hrs"
    ].median()

    return resolved[
        (resolved["customer_rating"] <= 2)
        & (
            resolved["resolution_time_hrs"]
            > median_resolution
        )
    ].copy()
