"""Basic tests for data generation, cleaning, and analysis."""

import pandas as pd
import pytest

from src.generate_data import generate_appointments
from src.clean_data import clean_appointments, validate_cleaned_data
from src.analyze_data import calculate_kpis, department_summary


def test_generator_is_reproducible():
    first = generate_appointments(100, seed=7)
    second = generate_appointments(100, seed=7)
    pd.testing.assert_frame_equal(first, second)


def test_cleaning_removes_exact_duplicates_and_validates():
    raw = generate_appointments(200, seed=11)
    cleaned, audit = clean_appointments(raw)
    checks = validate_cleaned_data(cleaned)

    assert audit["exact_duplicate_rows_removed"] > 0
    assert cleaned["appointment_id"].is_unique
    assert all(checks.values())
    assert cleaned["wait_time_minutes"].ge(0).all()


def test_kpis_reconcile_to_total():
    raw = generate_appointments(200, seed=15)
    cleaned, _ = clean_appointments(raw)
    kpis = calculate_kpis(cleaned)

    assert kpis["total_appointments"] == len(cleaned)
    assert (
        kpis["completed_appointments"]
        + kpis["cancelled_appointments"]
        + kpis["no_show_appointments"]
        == len(cleaned)
    )


def test_cleaner_rejects_missing_required_columns():
    with pytest.raises(ValueError):
        clean_appointments(pd.DataFrame({"appointment_id": ["A1"]}))


def test_department_summary_has_departments():
    cleaned, _ = clean_appointments(generate_appointments(100, seed=19))
    summary = department_summary(cleaned)
    assert not summary.empty
    assert "average_wait_minutes" in summary.columns
