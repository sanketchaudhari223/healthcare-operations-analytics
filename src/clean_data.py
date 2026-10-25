"""Data cleaning and validation functions."""

import pandas as pd

REQUIRED_COLUMNS = {
    "appointment_id", "appointment_date", "department", "patient_age",
    "wait_time_minutes", "status", "satisfaction_score"
}
VALID_STATUSES = {"Completed", "Cancelled", "No-show"}


def clean_appointments(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean appointment data and return (cleaned_dataframe, audit_summary)."""
    missing_columns = REQUIRED_COLUMNS - set(raw.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    df = raw.copy()
    original_rows = len(df)

    # Remove only exact duplicate records; preserve non-identical records for review.
    exact_duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Normalize types and text fields.
    df["appointment_id"] = df["appointment_id"].astype("string").str.strip()
    df["appointment_date"] = pd.to_datetime(df["appointment_date"], errors="coerce")
    df["department"] = (
        df["department"].astype("string").str.strip().replace("", pd.NA)
    )
    df["department"] = df["department"].fillna("Unknown")

    df["status"] = (
        df["status"].astype("string").str.strip().str.lower()
        .replace({"no show": "no-show", "noshow": "no-show"})
        .map({
            "completed": "Completed",
            "cancelled": "Cancelled",
            "canceled": "Cancelled",
            "no-show": "No-show",
        })
    )

    # Invalid values are treated as missing, not silently accepted.
    df["patient_age"] = pd.to_numeric(df["patient_age"], errors="coerce")
    invalid_age = ~df["patient_age"].between(0, 120)
    invalid_age_count = int(invalid_age.fillna(False).sum())
    df.loc[invalid_age, "patient_age"] = pd.NA

    df["wait_time_minutes"] = pd.to_numeric(df["wait_time_minutes"], errors="coerce")
    invalid_wait = (df["wait_time_minutes"] < 0) | (df["wait_time_minutes"] > 24 * 60)
    invalid_wait_count = int(invalid_wait.fillna(False).sum())
    df.loc[invalid_wait, "wait_time_minutes"] = pd.NA

    df["satisfaction_score"] = pd.to_numeric(
        df["satisfaction_score"], errors="coerce"
    )
    invalid_satisfaction = ~df["satisfaction_score"].between(1, 5)
    invalid_satisfaction_count = int(invalid_satisfaction.fillna(False).sum())
    df.loc[invalid_satisfaction, "satisfaction_score"] = pd.NA

    # Impute wait time with department median, then global median as fallback.
    missing_wait_before = int(df["wait_time_minutes"].isna().sum())
    global_median = df["wait_time_minutes"].median()
    if pd.isna(global_median):
        global_median = 0.0
    dept_medians = df.groupby("department")["wait_time_minutes"].transform("median")
    df["wait_time_minutes"] = df["wait_time_minutes"].fillna(dept_medians).fillna(global_median)

    # Keep satisfaction missing: imputing subjective feedback can distort reporting.
    df["patient_age"] = df["patient_age"].round().astype("Int64")
    df["wait_time_minutes"] = df["wait_time_minutes"].round(0).astype("Int64")
    df["satisfaction_score"] = df["satisfaction_score"].astype("Float64")

    # Rows with unusable identifiers, dates, or statuses cannot be reliably analyzed.
    invalid_core = (
        df["appointment_id"].isna() | df["appointment_id"].eq("")
        | df["appointment_date"].isna() | df["status"].isna()
    )
    dropped_invalid_core = int(invalid_core.sum())
    df = df.loc[~invalid_core].copy()

    # Appointment IDs are expected to identify a single appointment.
    duplicate_ids = int(df["appointment_id"].duplicated(keep="first").sum())
    df = df.drop_duplicates(subset=["appointment_id"], keep="first").copy()

    df = df.sort_values(["appointment_date", "appointment_id"]).reset_index(drop=True)

    audit = {
        "input_rows": original_rows,
        "exact_duplicate_rows_removed": exact_duplicates,
        "invalid_wait_values_set_missing": invalid_wait_count,
        "missing_wait_values_before_imputation": missing_wait_before,
        "invalid_age_values_set_missing": invalid_age_count,
        "invalid_satisfaction_values_set_missing": invalid_satisfaction_count,
        "rows_dropped_for_invalid_core_fields": dropped_invalid_core,
        "duplicate_appointment_ids_removed": duplicate_ids,
        "output_rows": len(df),
        "missing_wait_values_after_cleaning": int(df["wait_time_minutes"].isna().sum()),
        "missing_satisfaction_values_retained": int(df["satisfaction_score"].isna().sum()),
    }
    return df, audit


def validate_cleaned_data(df: pd.DataFrame) -> dict:
    """Run post-cleaning checks and return a dictionary of pass/fail results."""
    checks = {
        "appointment_id_not_null": bool(df["appointment_id"].notna().all()),
        "appointment_id_unique": bool(df["appointment_id"].is_unique),
        "appointment_date_valid": bool(df["appointment_date"].notna().all()),
        "status_valid": bool(df["status"].isin(VALID_STATUSES).all()),
        "wait_time_non_negative": bool((df["wait_time_minutes"] >= 0).all()),
        "wait_time_not_missing": bool(df["wait_time_minutes"].notna().all()),
        "satisfaction_in_range_or_missing": bool(
            df["satisfaction_score"].dropna().between(1, 5).all()
        ),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"Data validation failed: {failed}")
    return checks
