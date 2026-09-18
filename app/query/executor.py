from __future__ import annotations

from typing import Any

import pandas as pd

from app.analytics.service import AnalyticsService
from app.query.schema import QueryPlan
from app.query.validator import validate_query_plan


class QueryExecutor:
    """Execute validated query plans using deterministic analytics."""

    def __init__(self, analytics: AnalyticsService | None = None):
        self.analytics = analytics or AnalyticsService()

    def execute(self, plan: QueryPlan) -> dict[str, Any]:
        """Execute a validated query plan."""

        plan = validate_query_plan(plan)

        df = self.analytics.df.copy()

        # Apply filters
        for condition in plan.filters:
            df = self._apply_filter(
                df,
                condition.field,
                condition.operator,
                condition.value,
            )

        # Apply filter groups
        for group in plan.filter_groups:
            group_mask = None
            for condition in group.conditions:
                cond_df = self._apply_filter(
                    df,
                    condition.field,
                    condition.operator,
                    condition.value,
                )
                cond_mask = df.index.isin(cond_df.index)
                
                if group_mask is None:
                    group_mask = cond_mask
                else:
                    if group.logic == "OR":
                        group_mask = group_mask | cond_mask
                    elif group.logic == "AND":
                        group_mask = group_mask & cond_mask
            
            if group_mask is not None:
                df = df[group_mask]

        # Apply relative time filters
        if plan.relative_time:
            ref_time = df["created_at"].max()
            if plan.relative_time == "older_than_24_hours":
                df = df[df["created_at"] < (ref_time - pd.Timedelta(hours=24))]
            elif plan.relative_time == "last_24_hours":
                df = df[df["created_at"] >= (ref_time - pd.Timedelta(hours=24))]
            elif plan.relative_time == "today":
                df = df[df["created_at"] >= ref_time.floor("D")]
            elif plan.relative_time == "yesterday":
                yesterday = (ref_time - pd.Timedelta(days=1)).floor("D")
                df = df[(df["created_at"] >= yesterday) & (df["created_at"] < ref_time.floor("D"))]
            elif plan.relative_time == "this_week":
                df = df[df["created_at"] >= (ref_time - pd.Timedelta(days=ref_time.dayofweek)).floor("D")]
            elif plan.relative_time == "this_month":
                df = df[df["created_at"] >= ref_time.replace(day=1).floor("D")]

        # Apply absolute date filters
        if plan.start_date or plan.end_date:
            ref_time = df["created_at"].max()
            
            if plan.start_date:
                start = pd.to_datetime(plan.start_date)
                df = df[df["created_at"] >= start]

            if plan.end_date:
                end = pd.to_datetime(plan.end_date)
                df = df[df["created_at"] <= end]

        # Grouped query
        if plan.group_by:
            return self._execute_grouped(df, plan)

        # Anomaly query
        if plan.intent == "anomaly":
            from app.anomalies.detector import AnomalyDetector
            detector = AnomalyDetector(df)
            anomalies = detector.detect()
            
            return {
                "count": len(anomalies),
                "rows": anomalies
            }

        # Aggregation query
        if plan.aggregation:
            return self._execute_aggregation(df, plan)

        # Basic filtered query
        result = {
            "count": int(len(df)),
        }

        if plan.limit:
            result["rows"] = df.head(plan.limit).to_dict(
                orient="records"
            )

        return result

    @staticmethod
    def _apply_filter(
        df: pd.DataFrame,
        field: str,
        operator: str,
        value: Any,
    ) -> pd.DataFrame:

        series = df[field]

        if operator == "eq":
            return df[series.astype(str).str.lower() == str(value).lower()]

        if operator == "neq":
            return df[series.astype(str).str.lower() != str(value).lower()]

        if operator == "gt":
            return df[series > value]

        if operator == "gte":
            return df[series >= value]

        if operator == "lt":
            return df[series < value]

        if operator == "lte":
            return df[series <= value]

        if operator == "contains":
            return df[
                series.astype(str)
                .str.contains(str(value), case=False, na=False)
            ]

        raise ValueError(f"Unsupported operator: {operator}")

    @staticmethod
    def _execute_aggregation(
        df: pd.DataFrame,
        plan: QueryPlan,
    ) -> dict[str, Any]:

        aggregation = plan.aggregation

        if aggregation == "count":
            value = len(df)

        else:
            if not plan.aggregation_field:
                raise ValueError(
                    "aggregation_field is required for this aggregation"
                )

            series = pd.to_numeric(
                df[plan.aggregation_field],
                errors="coerce",
            )

            if aggregation == "sum":
                value = series.sum()

            elif aggregation == "avg":
                value = series.mean()

            elif aggregation == "min":
                value = series.min()

            elif aggregation == "max":
                value = series.max()

            else:
                raise ValueError(
                    f"Unsupported aggregation: {aggregation}"
                )

        if pd.isna(value):
            value = None
        elif isinstance(value, float):
            value = round(value, 2)
        else:
            value = int(value)

        actual_count = int(series.count()) if aggregation != "count" else int(len(df))

        return {
            "count": actual_count,
            "aggregation": aggregation,
            "aggregation_field": plan.aggregation_field,
            "value": value,
        }

    @staticmethod
    def _execute_grouped(
        df: pd.DataFrame,
        plan: QueryPlan,
    ) -> dict[str, Any]:

        group_by = plan.group_by

        if not group_by:
            raise ValueError("group_by is required")

        if plan.aggregation == "count":
            grouped = (
                df.groupby(group_by)
                .size()
                .reset_index(name="value")
            )

        elif plan.aggregation:
            if not plan.aggregation_field:
                raise ValueError(
                    "aggregation_field is required"
                )

            numeric = pd.to_numeric(
                df[plan.aggregation_field],
                errors="coerce",
            )

            working = df.copy()
            working["_aggregation_value"] = numeric

            grouped = (
                working.groupby(group_by)["_aggregation_value"]
                .agg(plan.aggregation)
                .reset_index(name="value")
            )

        else:
            grouped = (
                df.groupby(group_by)
                .size()
                .reset_index(name="value")
            )

        if plan.sort_by:
            if plan.sort_by in grouped.columns:
                grouped = grouped.sort_values(
                    by=plan.sort_by,
                    ascending=plan.sort_order == "asc",
                )
        else:
            grouped = grouped.sort_values(
                by="value",
                ascending=plan.sort_order == "asc",
            )

        if plan.limit:
            grouped = grouped.head(plan.limit)

        grouped["value"] = grouped["value"].round(2)

        actual_count = int(numeric.count()) if plan.aggregation and plan.aggregation_field else int(len(df))

        return {
            "count": actual_count,
            "group_by": group_by,
            "results": grouped.to_dict(
                orient="records"
            ),
        }
