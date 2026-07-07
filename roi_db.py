import json
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


DB_PATH = Path(__file__).with_name("roi_scenarios.sqlite3")


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS roi_scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_name TEXT NOT NULL,
                saved_at TEXT NOT NULL,
                inputs_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                team_size INTEGER NOT NULL,
                hours_saved_per_week REAL NOT NULL,
                loaded_hourly_cost REAL NOT NULL,
                monthly_ai_cost REAL NOT NULL,
                implementation_cost REAL NOT NULL,
                training_cost REAL NOT NULL,
                monthly_revenue REAL NOT NULL,
                revenue_uplift_pct REAL NOT NULL,
                monthly_manual_cost REAL NOT NULL,
                manual_cost_reduction_pct REAL NOT NULL,
                monthly_hours_saved REAL NOT NULL,
                annual_benefits REAL NOT NULL,
                first_year_cost REAL NOT NULL,
                net_annual_value REAL NOT NULL,
                roi_pct REAL NOT NULL,
                payback_months REAL,
                breakeven_month INTEGER
            )
            """
        )
        conn.commit()


def save_scenario(scenario_name: str, inputs: dict[str, Any], result: dict[str, Any]) -> None:
    payload_inputs = json.dumps(inputs)
    payload_result = json.dumps(
        {key: _json_safe(value) for key, value in result.items()},
        default=_json_safe,
    )

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO roi_scenarios (
                scenario_name, saved_at, inputs_json, result_json,
                team_size, hours_saved_per_week, loaded_hourly_cost, monthly_ai_cost,
                implementation_cost, training_cost, monthly_revenue, revenue_uplift_pct,
                monthly_manual_cost, manual_cost_reduction_pct, monthly_hours_saved,
                annual_benefits, first_year_cost, net_annual_value, roi_pct,
                payback_months, breakeven_month
            )
            VALUES (
                :scenario_name, datetime('now'), :inputs_json, :result_json,
                :team_size, :hours_saved_per_week, :loaded_hourly_cost, :monthly_ai_cost,
                :implementation_cost, :training_cost, :monthly_revenue, :revenue_uplift_pct,
                :monthly_manual_cost, :manual_cost_reduction_pct, :monthly_hours_saved,
                :annual_benefits, :first_year_cost, :net_annual_value, :roi_pct,
                :payback_months, :breakeven_month
            )
            """,
            {
                "scenario_name": scenario_name,
                "inputs_json": payload_inputs,
                "result_json": payload_result,
                "team_size": int(inputs["team_size"]),
                "hours_saved_per_week": float(inputs["hours_saved_per_week"]),
                "loaded_hourly_cost": float(inputs["loaded_hourly_cost"]),
                "monthly_ai_cost": float(inputs["monthly_ai_cost"]),
                "implementation_cost": float(inputs["implementation_cost"]),
                "training_cost": float(inputs["training_cost"]),
                "monthly_revenue": float(inputs["monthly_revenue"]),
                "revenue_uplift_pct": float(inputs["revenue_uplift_pct"]),
                "monthly_manual_cost": float(inputs["monthly_manual_cost"]),
                "manual_cost_reduction_pct": float(inputs["manual_cost_reduction_pct"]),
                "monthly_hours_saved": float(result["monthly_hours_saved"]),
                "annual_benefits": float(result["annual_benefits"]),
                "first_year_cost": float(result["first_year_cost"]),
                "net_annual_value": float(result["net_annual_value"]),
                "roi_pct": float(result["roi_pct"]),
                "payback_months": None if result["payback_months"] is None else float(result["payback_months"]),
                "breakeven_month": result["breakeven_month"],
            },
        )
        conn.commit()


def fetch_scenarios(limit: int = 10) -> pd.DataFrame:
    with _connect() as conn:
        return pd.read_sql_query(
            """
            SELECT
                id,
                scenario_name,
                saved_at,
                team_size,
                hours_saved_per_week,
                loaded_hourly_cost,
                annual_benefits,
                net_annual_value,
                roi_pct,
                payback_months,
                breakeven_month
            FROM roi_scenarios
            ORDER BY id DESC
            LIMIT ?
            """,
            conn,
            params=(limit,),
        )


def _json_safe(value: Any) -> Any:
    if isinstance(value, pd.DataFrame):
        return value.to_dict(orient="records")
    if isinstance(value, pd.Series):
        return value.to_dict()
    if hasattr(value, "item"):
        return value.item()
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value
