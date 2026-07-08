"""AI ROI calculator Streamlit application."""

import math
import altair as alt
import pandas as pd
import streamlit as st


from roi_model import calculate_roi
from roi_db import fetch_scenarios, init_db, save_scenario


st.set_page_config(
    page_title="AI ROI Calculator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def money(monetaryvalue: float) -> str:
    """Format a number as currency without decimal places."""
    return f"${monetaryvalue:,.0f}"


def money1(amount: float) -> str:
    """Format a number as currency with one decimal place."""
    return f"${amount:,.1f}"


def pct(percentage: float) -> str:
    """Format a number as a percentage with one decimal place."""
    return f"{percentage:.1f}%"


init_db()


st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .hero {
            padding: 1.5rem 1.75rem;
            border-radius: 1.5rem;
            background: linear-gradient(135deg, rgba(11,18,32,1) 0%, rgba(25,47,83,1) 45%, rgba(16,94,89,1) 100%);
            color: white;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.2);
            margin-bottom: 1.25rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2.4rem;
            line-height: 1.1;
        }
        .hero p {
            margin: 0.65rem 0 0 0;
            font-size: 1.02rem;
            opacity: 0.92;
        }
        .metric-card {
            background: white;
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 1rem;
            padding: 1rem 1.1rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        }
        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0 0 0.4rem 0;
        }
        .note {
            color: #475569;
            font-size: 0.92rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="hero">
        <h1>AI ROI Calculator</h1>
        <p>Estimate the business value of an AI initiative across 
        labor savings, revenue uplift, and payback time.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("Inputs")
    st.caption("Adjust the assumptions to match your team and use case.")
    scenario_name = st.text_input("Scenario name", value="My ROI scenario")

    team_size = st.number_input("Team size impacted", min_value=1, value=10, step=1)
    hours_saved_per_week = st.number_input("Hours saved per person per week", min_value=0.0, value=3.0, step=0.5)
    loaded_hourly_cost = st.number_input("Fully loaded hourly cost", min_value=0.0, value=45.0, step=1.0)

    st.divider()
    monthly_ai_cost = st.number_input("Monthly AI software cost", min_value=0.0, value=1200.0, step=50.0)
    implementation_cost = st.number_input("One-time implementation cost", min_value=0.0, value=5000.0, step=250.0)
    training_cost = st.number_input("Training / change management cost", min_value=0.0, value=2500.0, step=250.0)

    st.divider()
    monthly_revenue = st.number_input("Current monthly revenue influenced", min_value=0.0, value=50000.0, step=1000.0)
    revenue_uplift_pct = st.slider("Expected revenue uplift from AI", min_value=0.0, max_value=50.0, value=5.0, step=0.5)
    monthly_manual_cost = st.number_input("Monthly manual process cost", min_value=0.0, value=8000.0, step=500.0)
    manual_cost_reduction_pct = st.slider("Manual cost reduction from AI", min_value=0.0, max_value=100.0, value=20.0, step=1.0)


inputs = {
    "team_size": float(team_size),
    "hours_saved_per_week": float(hours_saved_per_week),
    "loaded_hourly_cost": float(loaded_hourly_cost),
    "monthly_ai_cost": float(monthly_ai_cost),
    "implementation_cost": float(implementation_cost),
    "training_cost": float(training_cost),
    "monthly_revenue": float(monthly_revenue),
    "revenue_uplift_pct": float(revenue_uplift_pct),
    "monthly_manual_cost": float(monthly_manual_cost),
    "manual_cost_reduction_pct": float(manual_cost_reduction_pct),
}

result = calculate_roi(inputs)

col1, col2, col3, col4 = st.columns(4)
metrics = [
    ("Annual ROI", pct(result["roi_pct"]) if math.isfinite(result["roi_pct"]) else "N/A"),
    ("Payback", f"{result['payback_months']:.1f} months" if math.isfinite(result["payback_months"]) else "N/A"),
    ("Annual Net Value", money(result["net_annual_value"])),
    ("Annual Benefits", money(result["annual_benefits"])),
]
for col, (label, value) in zip((col1, col2, col3, col4), metrics):
    with col:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label, value)
        st.markdown("</div>", unsafe_allow_html=True)


left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.subheader("Value Breakdown")
    breakdown = pd.DataFrame(
        {
            "Category": [
                "Labor savings",
                "Revenue uplift",
                "Manual cost reduction",
                "AI subscription cost",
                "Implementation + training",
            ],
            "Annual Value": [
                result["annual_labor_savings"],
                result["annual_revenue_uplift"],
                result["annual_compliance_savings"],
                -result["annual_subscription_cost"],
                -(inputs["implementation_cost"] + inputs["training_cost"]),
            ],
        }
    )

    breakdown["Direction"] = breakdown["Annual Value"].apply(lambda x: "Positive" if x >= 0 else "Cost")
    chart = (
        alt.Chart(breakdown)
        .mark_bar()
        .encode(
            x=alt.X("Category:N", sort=None, axis=alt.Axis(labelAngle=-20)),
            y=alt.Y("Annual Value:Q", title="Annual value ($)"),
            color=alt.Color(
                "Direction:N",
                scale=alt.Scale(domain=["Positive", "Cost"], range=["#0f766e", "#ef4444"]),
                legend=None,
            ),
            tooltip=["Category", alt.Tooltip("Annual Value:Q", format=",.0f")],
        )
        .properties(height=340)
    )
    st.altair_chart(chart, use_container_width=True)

with right:
    st.subheader("Key Figures")
    st.write(f"Monthly hours saved: **{result['monthly_hours_saved']:.1f}**")
    st.write(f"Monthly labor savings: **{money(result['monthly_labor_savings'])}**")
    st.write(f"Annual labor savings: **{money(result['annual_labor_savings'])}**")
    st.write(f"Annual revenue uplift: **{money(result['annual_revenue_uplift'])}**")
    st.write(f"Annual manual cost reduction: **{money(result['annual_compliance_savings'])}**")
    st.write(f"First-year cost: **{money(result['first_year_cost'])}**")
    st.write(f"Net annual value: **{money(result['net_annual_value'])}**")

    st.divider()
    if math.isfinite(result["payback_months"]):
        st.success(f"Estimated payback period: {result['payback_months']:.1f} months")
    else:
        st.warning("Payback period cannot be estimated with the current assumptions.")

    if result["breakeven_month"] is not None:
        st.info(f"Break-even arrives in month {result['breakeven_month']}.")
    else:
        st.info("Break-even does not occur within 36 months.")

    if st.button("Save this scenario", use_container_width=True):
        save_scenario(scenario_name, inputs, result)
        st.success(f"Saved '{scenario_name}' to the database.")


st.subheader("12-Month Cash Flow")
cashflow = result["cashflow"]
cashflow_long = cashflow.melt(
    id_vars=["Month"],
    value_vars=["Benefit", "Cost", "Net"],
    var_name="Series",
    value_name="Value",
)
cashflow_chart = (
    alt.Chart(cashflow_long)
    .mark_line(point=True)
    .encode(
        x=alt.X("Month:Q", title="Month"),
        y=alt.Y("Value:Q", title="Monthly value ($)"),
        color=alt.Color("Series:N", legend=alt.Legend(title=None)),
        tooltip=[
            alt.Tooltip("Month:Q", title="Month"),
            alt.Tooltip("Series:N", title="Series"),
            alt.Tooltip("Value:Q", title="Value", format=",.0f"),
        ],
    )
    .properties(height=340)
)
st.altair_chart(cashflow_chart, use_container_width=True)

with st.expander("Assumptions and formula notes", expanded=False):
    st.markdown(
        """
        - Monthly labor savings = `team size x hours saved per week x 4.33 x loaded hourly cost`
        - Annual benefits = labor savings + revenue uplift + manual cost reduction
        - First-year cost = implementation + training + 12 months of subscription
        - ROI = `(annual benefits - first-year cost) / first-year cost x 100`
        - Payback = `(implementation + training) / monthly net benefit`
        """
    )

with st.expander("Saved scenarios", expanded=False):
    scenarios = fetch_scenarios(limit=10)
    if scenarios.empty:
        st.info("No saved scenarios yet. Save one using the button above.")
    else:
        display = scenarios.copy()
        display["annual_benefits"] = display["annual_benefits"].map(money)
        display["net_annual_value"] = display["net_annual_value"].map(money)
        display["roi_pct"] = display["roi_pct"].map(lambda x: f"{x:.1f}%")
        display["payback_months"] = display["payback_months"].map(lambda x: "N/A" if pd.isna(x) else f"{x:.1f}")
        st.dataframe(
            display[
                [
                    "id",
                    "scenario_name",
                    "saved_at",
                    "team_size",
                    "hours_saved_per_week",
                    "annual_benefits",
                    "net_annual_value",
                    "roi_pct",
                    "payback_months",
                    "breakeven_month",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
