import math

import pandas as pd


def calculate_roi(inputs: dict) -> dict:
    months_per_year = 12

    monthly_hours_saved = inputs["team_size"] * inputs["hours_saved_per_week"] * 4.33
    monthly_labor_savings = monthly_hours_saved * inputs["loaded_hourly_cost"]
    annual_labor_savings = monthly_labor_savings * months_per_year

    annual_revenue_uplift = inputs["monthly_revenue"] * (inputs["revenue_uplift_pct"] / 100) * months_per_year
    annual_compliance_savings = inputs["monthly_manual_cost"] * (inputs["manual_cost_reduction_pct"] / 100) * months_per_year

    annual_benefits = annual_labor_savings + annual_revenue_uplift + annual_compliance_savings
    annual_subscription_cost = inputs["monthly_ai_cost"] * months_per_year
    first_year_cost = inputs["implementation_cost"] + inputs["training_cost"] + annual_subscription_cost
    net_annual_value = annual_benefits - first_year_cost

    roi_pct = (net_annual_value / first_year_cost * 100) if first_year_cost else math.inf
    monthly_net_benefit = (annual_benefits / months_per_year) - inputs["monthly_ai_cost"]
    payback_months = (
        (inputs["implementation_cost"] + inputs["training_cost"]) / monthly_net_benefit
        if monthly_net_benefit > 0
        else math.inf
    )

    breakeven_month = None
    cumulative = -(inputs["implementation_cost"] + inputs["training_cost"])
    for month in range(1, 37):
        cumulative += monthly_net_benefit
        if cumulative >= 0:
            breakeven_month = month
            break

    monthly_cashflow = []
    running_total = -(inputs["implementation_cost"] + inputs["training_cost"])
    for month in range(1, 13):
        running_total += monthly_net_benefit
        monthly_cashflow.append(
            {
                "Month": month,
                "Benefit": annual_benefits / months_per_year,
                "Cost": inputs["monthly_ai_cost"],
                "Net": monthly_net_benefit,
                "Cumulative": running_total,
            }
        )

    return {
        "monthly_hours_saved": monthly_hours_saved,
        "monthly_labor_savings": monthly_labor_savings,
        "annual_labor_savings": annual_labor_savings,
        "annual_revenue_uplift": annual_revenue_uplift,
        "annual_compliance_savings": annual_compliance_savings,
        "annual_benefits": annual_benefits,
        "annual_subscription_cost": annual_subscription_cost,
        "first_year_cost": first_year_cost,
        "net_annual_value": net_annual_value,
        "roi_pct": roi_pct,
        "monthly_net_benefit": monthly_net_benefit,
        "payback_months": payback_months,
        "breakeven_month": breakeven_month,
        "cashflow": pd.DataFrame(monthly_cashflow),
    }
