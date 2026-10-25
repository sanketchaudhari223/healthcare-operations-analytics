"""Run the end-to-end healthcare operations analytics pipeline."""

from pathlib import Path
import json
import pandas as pd

from src.generate_data import generate_appointments
from src.clean_data import clean_appointments, validate_cleaned_data
from src.analyze_data import calculate_kpis, department_summary, monthly_summary, weekday_summary
from src.database import load_to_sqlite, run_sql_query
from src.visualize import create_charts


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    raw_path = root / "data" / "raw" / "appointments.csv"
    processed_dir = root / "data" / "processed"
    output_dir = root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    database_path = root / "data" / "healthcare_analytics.sqlite"

    # Generate raw data only if it doesn't already exist.
    if not raw_path.exists():
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        generate_appointments().to_csv(raw_path, index=False)

    raw = pd.read_csv(raw_path)
    cleaned, audit = clean_appointments(raw)
    checks = validate_cleaned_data(cleaned)

    processed_dir.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(processed_dir / "appointments_cleaned.csv", index=False)

    kpis = calculate_kpis(cleaned)
    departments = department_summary(cleaned)
    monthly = monthly_summary(cleaned)
    weekdays = weekday_summary(cleaned)

    departments.to_csv(output_dir / "department_summary.csv", index=False)
    monthly.to_csv(output_dir / "monthly_summary.csv", index=False)
    weekdays.to_csv(output_dir / "weekday_summary.csv", index=False)

    load_to_sqlite(cleaned, database_path)
    sql_query = """
        SELECT department,
               COUNT(*) AS appointments,
               ROUND(AVG(wait_time_minutes), 2) AS average_wait_minutes,
               ROUND(100.0 * SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END)
                     / COUNT(*), 2) AS cancellation_rate_pct
        FROM appointments
        GROUP BY department
        ORDER BY average_wait_minutes DESC;
    """
    sql_department_summary = run_sql_query(database_path, sql_query)
    sql_department_summary.to_csv(output_dir / "sql_department_summary.csv", index=False)

    charts = create_charts(cleaned, departments, monthly, output_dir)

    report = {
        "project": "Healthcare Operations Analytics",
        "data_note": "Synthetic data for educational use; not real healthcare data.",
        "data_quality_audit": audit,
        "validation_checks": checks,
        "kpis": kpis,
        "highest_average_wait_department": (
            str(departments.iloc[0]["department"]) if not departments.empty else None
        ),
        "generated_charts": [str(p.relative_to(root)) for p in charts],
    }
    (output_dir / "summary_report.json").write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )

    print("\n=== PIPELINE COMPLETED ===")
    print(f"Raw rows: {len(raw):,} | Clean rows: {len(cleaned):,}")
    print("\nKPI summary:")
    for key, value in kpis.items():
        print(f"  {key}: {value}")
    print("\nDepartment summary:")
    print(departments.to_string(index=False))
    print("\nValidation checks:")
    for key, value in checks.items():
        print(f"  {key}: {'PASS' if value else 'FAIL'}")
    print(f"\nDatabase: {database_path}")
    print(f"Reports and charts: {output_dir}")


if __name__ == "__main__":
    main()
