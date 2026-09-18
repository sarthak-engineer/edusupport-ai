from __future__ import annotations

import pandas as pd

from app.anomalies.rules import (
    detect_customer_experience_anomalies,
    detect_resolution_outliers,
    detect_stale_high_priority,
)
from app.data.repository import get_support_tickets


class AnomalyDetector:
    """Deterministic and explainable anomaly detector."""

    def __init__(self, df: pd.DataFrame | None = None):
        self.df = (
            df.copy()
            if df is not None
            else get_support_tickets().copy()
        )

    def detect(self) -> list[dict]:
        anomalies = []

        stale = detect_stale_high_priority(self.df)

        for _, row in stale.iterrows():
            value_hrs = round(
                float((self.df["created_at"].max() - row["created_at"]).total_seconds() / 3600), 2
            )
            anomalies.append(
                {
                    "ticket_id": str(row["ticket_id"]),
                    "anomaly_type": "stale_high_priority",
                    "severity": (
                        "critical" if row["priority"] == "Critical" else "high"
                    ),
                    "reason": (
                        f"Priority = {row['priority']}, status = {row['status']}, "
                        f"ticket age = {value_hrs} hours, exceeding the 24-hour threshold."
                    ),
                    "value": value_hrs,
                }
            )

        outliers = detect_resolution_outliers(self.df)

        q1 = self.df["resolution_time_hrs"].quantile(0.25)
        q3 = self.df["resolution_time_hrs"].quantile(0.75)
        upper_bound = q3 + (1.5 * (q3 - q1))

        for _, row in outliers.iterrows():
            value_hrs = round(float(row["resolution_time_hrs"]), 2)
            anomalies.append(
                {
                    "ticket_id": str(row["ticket_id"]),
                    "anomaly_type": "resolution_time_outlier",
                    "severity": "medium",
                    "reason": (
                        f"Resolution time = {value_hrs} hours, above the calculated "
                        f"IQR upper bound of {upper_bound:.1f} hours."
                    ),
                    "value": value_hrs,
                }
            )

        experience = detect_customer_experience_anomalies(self.df)

        for _, row in experience.iterrows():
            rating = round(float(row["customer_rating"]), 2)
            res_time = round(float(row["resolution_time_hrs"]), 2)
            anomalies.append(
                {
                    "ticket_id": str(row["ticket_id"]),
                    "anomaly_type": "customer_experience",
                    "severity": "medium",
                    "reason": (
                        f"Customer rating = {rating} and resolution time = {res_time} hours, "
                        "which is above the dataset median."
                    ),
                    "value": rating,
                }
            )

        return anomalies

    def summary(self) -> dict:
        anomalies = self.detect()

        return {
            "total_anomalies": len(anomalies),
            "by_type": {
                "stale_high_priority": sum(
                    a["anomaly_type"]
                    == "stale_high_priority"
                    for a in anomalies
                ),
                "resolution_time_outlier": sum(
                    a["anomaly_type"]
                    == "resolution_time_outlier"
                    for a in anomalies
                ),
                "customer_experience": sum(
                    a["anomaly_type"]
                    == "customer_experience"
                    for a in anomalies
                ),
            },
        }
