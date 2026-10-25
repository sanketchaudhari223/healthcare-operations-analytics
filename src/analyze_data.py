"""Exploratory analysis and KPI calculations."""

import pandas as pd


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate headline operational KPIs from cleaned appointment data."""
    total = len(df)
    completed = int(df["status"].eq("Completed").sum())
    cancelled = int(df["status"].eq("Cancelled").sum())
    no_show = int(df["status"].eq("No-show").sum())
    return {
        "total_appointments": total,
        "completed_appointments": completed,
        "cancelled_appointments": cancelled,
        "no_show_appointments": no_show,
        "cancellation_rate_pct": round(cancelled / total * 100, 2) if total else 0.0,
        "no_show_rate_pct": round(no_show / total * 100, 2) if total else 0.0,
        "average_wait_minutes": round(float(df["wait_time_minutes"].mean()), 2) if total else 0.0,
        "median_wait_minutes": round(float(df["wait_time_minutes"].median()), 2) if total else 0.0,
        "average_satisfaction": round(float(df["satisfaction_score"].mean()), 2)
        if df["satisfaction_score"].notna().any() else None,
    }


def department_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize volume, waiting time, cancellation and no-show rates by department."""
    grouped = df.groupby("department", dropna=False)
    summary = grouped.agg(
        appointments=("appointment_id", "count"),
        average_wait_minutes=("wait_time_minutes", "mean"),
        median_wait_minutes=("wait_time_minutes", "median"),
        average_satisfaction=("satisfaction_score", "mean"),
    )
    status_counts = (
        df.assign(
            cancelled=df["status"].eq("Cancelled").astype(int),
            no_show=df["status"].eq("No-show").astype(int),
        )
        .groupby("department")
        .agg(cancelled_count=("cancelled", "sum"), no_show_count=("no_show", "sum"))
    )
    summary = summary.join(status_counts)
    summary["cancellation_rate_pct"] = (
        summary["cancelled_count"] / summary["appointments"] * 100
    )
    summary["no_show_rate_pct"] = (
        summary["no_show_count"] / summary["appointments"] * 100
    )
    return summary.reset_index().round(2).sort_values(
        "average_wait_minutes", ascending=False
    )


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly appointment volume and operational rates."""
    work = df.copy()
    work["month"] = work["appointment_date"].dt.to_period("M").astype(str)
    summary = work.groupby("month").agg(
        appointments=("appointment_id", "count"),
        average_wait_minutes=("wait_time_minutes", "mean"),
        cancelled_count=("status", lambda s: int(s.eq("Cancelled").sum())),
        no_show_count=("status", lambda s: int(s.eq("No-show").sum())),
    )
    summary["cancellation_rate_pct"] = (
        summary["cancelled_count"] / summary["appointments"] * 100
    )
    summary["no_show_rate_pct"] = (
        summary["no_show_count"] / summary["appointments"] * 100
    )
    return summary.reset_index().round(2)


def weekday_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize appointment volumes by day of week."""
    work = df.copy()
    work["day_of_week"] = work["appointment_date"].dt.day_name()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    result = work.groupby("day_of_week").size().reindex(order, fill_value=0)
    return result.rename_axis("day_of_week").reset_index(name="appointments")
