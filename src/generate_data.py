"""Generate a reproducible synthetic healthcare appointments dataset."""

from pathlib import Path
import numpy as np
import pandas as pd


def generate_appointments(n_records: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Create synthetic appointment records with intentional quality issues."""
    if n_records < 20:
        raise ValueError("n_records must be at least 20 to introduce quality issues.")

    rng = np.random.default_rng(seed)
    departments = ["Cardiology", "Dental", "Orthopedics", "Neurology", "General Medicine"]
    statuses = ["Completed", "Cancelled", "No-show"]
    dates = pd.date_range("2026-01-01", "2026-06-30", freq="D")

    df = pd.DataFrame({
        "appointment_id": [f"A{i:05d}" for i in range(1, n_records + 1)],
        "appointment_date": rng.choice(dates, size=n_records),
        "department": rng.choice(
            departments, size=n_records,
            p=[0.20, 0.18, 0.17, 0.15, 0.30]
        ),
        "patient_age": rng.integers(18, 86, size=n_records),
        "wait_time_minutes": np.maximum(
            0, rng.normal(loc=35, scale=18, size=n_records)
        ).round().astype(float),
        "status": rng.choice(statuses, size=n_records, p=[0.75, 0.15, 0.10]),
        "satisfaction_score": rng.integers(1, 6, size=n_records).astype(float),
    })

    # Inject realistic data-quality issues for cleaning practice.
    missing_wait = rng.choice(df.index, size=max(1, int(n_records * 0.035)), replace=False)
    df.loc[missing_wait, "wait_time_minutes"] = np.nan

    missing_satisfaction = rng.choice(
        df.index, size=max(1, int(n_records * 0.045)), replace=False
    )
    df.loc[missing_satisfaction, "satisfaction_score"] = np.nan

    invalid_wait = rng.choice(df.index, size=max(1, int(n_records * 0.005)), replace=False)
    df.loc[invalid_wait, "wait_time_minutes"] = -10

    missing_department = rng.choice(
        df.index, size=max(1, int(n_records * 0.01)), replace=False
    )
    df.loc[missing_department, "department"] = np.nan

    # Inconsistent capitalization and whitespace.
    for original, inconsistent in {
        "Completed": "completed",
        "Cancelled": " CANCELLED ",
        "No-show": "NO-SHOW",
    }.items():
        candidates = df.index[df["status"] == original]
        if len(candidates):
            count = max(1, int(len(candidates) * 0.05))
            selected = rng.choice(candidates, size=min(count, len(candidates)), replace=False)
            df.loc[selected, "status"] = inconsistent

    # Append exact duplicate rows; cleaning should remove them.
    duplicate_count = max(1, int(n_records * 0.01))
    df = pd.concat(
        [df, df.sample(n=duplicate_count, random_state=seed)],
        ignore_index=True
    )
    df["appointment_date"] = pd.to_datetime(df["appointment_date"])
    return df


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "raw" / "appointments.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_appointments()
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df):,} rows with {len(df.columns)} columns.")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
