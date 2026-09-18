from typing import Any
from app.query.schema import QueryPlan

def explain_plan(plan: QueryPlan, result: dict[str, Any]) -> str:
    parts = []
    
    op_map = {
        "eq": "=",
        "neq": "is not",
        "gt": ">",
        "gte": ">=",
        "lt": "<",
        "lte": "<="
    }
    
    # 1. Filters
    filter_strs = []
    for f in plan.filters:
        op = op_map.get(f.operator, f.operator)
        filter_strs.append(f"{f.field} {op} {f.value}")
        
    for g in plan.filter_groups:
        group_conds = []
        for f in g.conditions:
            op = op_map.get(f.operator, f.operator)
            group_conds.append(f"{f.field} {op} {f.value}")
        
        if group_conds:
            join_str = f" {g.logic.upper()} "
            filter_strs.append(f"({join_str.join(group_conds)})")
            
    if filter_strs:
        filters_combined = " AND ".join(filter_strs)
        parts.append(f"Filtered tickets where {filters_combined}")
        
    # 2. Group By
    if plan.group_by:
        parts.append(f"Grouped tickets by {plan.group_by}")

    # 3. Action / Aggregation
    if plan.aggregation:
        if plan.aggregation == "count":
            if plan.group_by:
                parts.append("counted the records in each group")
            else:
                parts.append("counted the matching records")
        else:
            agg_name = {
                "avg": "mean",
                "sum": "sum",
                "min": "minimum",
                "max": "maximum"
            }.get(plan.aggregation, plan.aggregation)
            
            if plan.aggregation_field:
                clean_field = plan.aggregation_field.replace('_hrs', '').replace('_', ' ')
                parts.append(f"kept records with a recorded {clean_field}")
                parts.append(f"calculated the {agg_name} of {plan.aggregation_field}")
    else:
        if not parts:
            parts.append("Selected tickets")

    # 4. Dates
    if plan.relative_time:
        if plan.relative_time == "older_than_24_hours":
            parts.append("applied the dataset-relative age > 24 hours condition")
        else:
            clean_time = plan.relative_time.replace('_', ' ')
            parts.append(f"identified tickets from {clean_time}")
            
    if plan.start_date and plan.end_date:
        parts.append(f"identified tickets between {plan.start_date} and {plan.end_date}")
    elif plan.start_date:
        parts.append(f"identified tickets from {plan.start_date}")
    elif plan.end_date:
        parts.append(f"identified tickets up to {plan.end_date}")
        
    # 5. Limit and Sort
    if plan.limit and plan.sort_order:
        dir_str = "highest" if plan.sort_order == "desc" else "lowest"
        if plan.aggregation == "count":
            parts.append(f"selected the {dir_str} count")
        else:
            sort_field = plan.sort_by if plan.sort_by else "value"
            parts.append(f"selected the {dir_str} {sort_field}")
    elif plan.limit:
        parts.append(f"returned the top {plan.limit}")

    # Combine parts cleanly
    if not parts:
        return "No explanation available."
        
    parts[0] = parts[0][0].upper() + parts[0][1:]
    
    if len(parts) == 1:
        explanation = parts[0]
    elif len(parts) == 2:
        explanation = f"{parts[0]} and {parts[1]}"
    else:
        explanation = ", ".join(parts[:-1]) + f", and {parts[-1]}"
        
    if not explanation.endswith("."):
        explanation += "."
        
    return explanation
