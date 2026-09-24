from __future__ import annotations

from typing import Any

import pandas as pd

from app.data.repository import get_support_tickets


class AnalyticsService:
    """Deterministic analytics engine for support ticket data."""

    def __init__(self, df: pd.DataFrame | None = None):
        self.df = df.copy() if df is not None else get_support_tickets().copy()

    def get_kpi_summary(self) -> dict[str, Any]:
        """Return high-level support ticket KPIs."""

        total_tickets = len(self.df)

        resolved = int(
            (self.df["status"] == "Resolved").sum()
        )

        open_tickets = int(
            (self.df["status"] == "Open").sum()
        )

        escalated = int(
            (self.df["status"] == "Escalated").sum()
        )

        critical_tickets = int(
            (self.df["priority"] == "Critical").sum()
        )


        resolution_rate = (
            round((resolved / total_tickets) * 100, 2)
            if total_tickets
            else 0.0
        )

        return {
            "total_tickets": total_tickets,
            "resolved_tickets": resolved,
            "open_tickets": open_tickets,
            "escalated_tickets": escalated,
            "critical_tickets": critical_tickets,
            "resolution_rate_percent": resolution_rate,
        }

    def filter_tickets(
        self,
        *,
        category: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        agent_id: str | None = None,
    ) -> pd.DataFrame:
        """Filter tickets using supported dimensions."""

        result = self.df.copy()

        if category is not None:
            result = result[
                result["category"].str.lower() == category.lower()
            ]

        if priority is not None:
            result = result[
                result["priority"].str.lower() == priority.lower()
            ]

        if status is not None:
            result = result[
                result["status"].str.lower() == status.lower()
            ]

        if agent_id is not None:
            result = result[
                result["agent_id"].str.lower() == agent_id.lower()
            ]

        return result

    def get_agent_performance(self) -> pd.DataFrame:
        """Return deterministic performance metrics by agent."""

        grouped = (
            self.df.groupby("agent_id")
            .agg(
                total_tickets=("ticket_id", "count"),
                resolved_tickets=(
                    "status",
                    lambda x: (x == "Resolved").sum(),
                ),
                average_rating=(
                    "customer_rating",
                    "mean",
                ),
                average_resolution_time=(
                    "resolution_time_hrs",
                    "mean",
                ),
            )
            .reset_index()
        )

        grouped["resolution_rate_percent"] = (
            grouped["resolved_tickets"]
            / grouped["total_tickets"]
            * 100
        ).round(2)

        grouped["average_rating"] = grouped[
            "average_rating"
        ].round(2)

        grouped["average_resolution_time"] = grouped[
            "average_resolution_time"
        ].round(2)

        return grouped

    def get_category_performance(self) -> pd.DataFrame:
        """Return performance metrics grouped by category."""

        grouped = (
            self.df.groupby("category")
            .agg(
                count=("ticket_id", "count"),
                resolved_tickets=(
                    "status",
                    lambda x: (x == "Resolved").sum(),
                ),
                average_rating=(
                    "customer_rating",
                    "mean",
                ),
                average_resolution_time=(
                    "resolution_time_hrs",
                    "mean",
                ),
            )
            .reset_index()
        )

        grouped["resolution_rate_percent"] = (
            grouped["resolved_tickets"]
            / grouped["count"]
            * 100
        ).round(2)

        grouped["average_rating"] = grouped[
            "average_rating"
        ].round(2)

        grouped["average_resolution_time"] = grouped[
            "average_resolution_time"
        ].round(2)

        return grouped

    def get_priority_distribution(self) -> pd.DataFrame:
        """Return ticket counts grouped by priority."""

        return (
            self.df["priority"]
            .value_counts()
            .rename_axis("priority")
            .reset_index(name="count")
        )

    def get_status_distribution(self) -> pd.DataFrame:
        """Return ticket counts grouped by status."""

        return (
            self.df["status"]
            .value_counts()
            .rename_axis("status")
            .reset_index(name="ticket_count")
        )

    def get_resolution_statistics(self) -> dict[str, float | int]:
        """Return statistics for resolved-ticket resolution times."""

        values = self.df["resolution_time_hrs"].dropna()

        if values.empty:
            return {
                "count": 0,
                "mean": 0.0,
                "median": 0.0,
                "min": 0.0,
                "max": 0.0,
            }

        return {
            "count": int(values.count()),
            "mean": round(float(values.mean()), 2),
            "median": round(float(values.median()), 2),
            "min": round(float(values.min()), 2),
            "max": round(float(values.max()), 2),
        }

    def rank_agents(
        self,
        *,
        metric: str,
        ascending: bool = False,
        limit: int = 5,
    ) -> pd.DataFrame:
        """Rank agents using supported performance metrics."""

        performance = self.get_agent_performance()

        allowed_metrics = {
            "resolved_tickets": "resolved_tickets",
            "average_rating": "average_rating",
            "average_resolution_time": "average_resolution_time",
            "resolution_rate_percent": "resolution_rate_percent",
        }

        if metric not in allowed_metrics:
            raise ValueError(
                f"Unsupported agent ranking metric: {metric}"
            )

        column = allowed_metrics[metric]

        return (
            performance
            .sort_values(
                by=column,
                ascending=ascending,
            )
            .head(limit)
            .reset_index(drop=True)
        )

    def get_ticket_count(
        self,
        *,
        category: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        agent_id: str | None = None,
        start_date: pd.Timestamp | None = None,
        end_date: pd.Timestamp | None = None,
    ) -> int:
        """Count tickets matching the supplied filters."""

        result = self.filter_tickets(
            category=category,
            priority=priority,
            status=status,
            agent_id=agent_id,
        )

        if start_date is not None:
            result = result[result["created_at"] >= start_date]

        if end_date is not None:
            result = result[result["created_at"] <= end_date]

        return int(len(result))
