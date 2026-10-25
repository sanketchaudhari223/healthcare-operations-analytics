# Healthcare Operations Analytics

An end-to-end data analytics portfolio project aligned with common Data Analyst responsibilities: data profiling, preprocessing, NumPy/Pandas analysis, SQL, statistical summaries, visualization, validation, and reproducible reporting.

> **Data disclaimer:** This project uses synthetic appointment records for educational purposes. It is not affiliated with Cigna and does not use real patient data.

## Business problem

A fictional healthcare operations team wants to understand appointment waiting times, cancellations, no-shows, and differences between departments. The project turns deliberately imperfect raw data into validated analytics outputs.

## Tech stack

- Python
- NumPy
- Pandas
- SQLite
- Matplotlib
- Seaborn
- pytest (tests)

## Project structure

```text
healthcare-operations-analytics/
├── data/
│   ├── raw/appointments.csv
│   └── processed/                  # generated
├── outputs/                        # generated reports and charts
├── sql/queries.sql
├── src/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── analyze_data.py
│   ├── database.py
│   ├── visualize.py
│   └── main.py
├── tests/test_project.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Quick start

Python 3.10+ is recommended.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python src/generate_data.py
python -m src.main
```

If PowerShell blocks virtual-environment activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

On macOS/Linux, activate with `source .venv/bin/activate`.

The pipeline generates `data/raw/appointments.csv` if it is missing, cleans the data, validates quality rules, loads a SQLite database, writes summary CSV/JSON files, and saves charts.

## Outputs

After `python -m src.main`, look in `outputs/` for:

- `summary_report.json` — data-quality audit, validation results, headline KPIs
- `department_summary.csv` — department performance metrics
- `monthly_summary.csv` — monthly volume and cancellation/no-show rates
- `weekday_summary.csv` — appointment volumes by weekday
- `sql_department_summary.csv` — example SQL-generated report
- `average_wait_by_department.png`
- `monthly_cancellation_rate.png`
- `waiting_time_distribution.png`

The cleaned dataset is written to `data/processed/appointments_cleaned.csv`; the SQLite database is `data/healthcare_analytics.sqlite`.

## Data-quality decisions

- Exact duplicate rows are removed.
- Text fields are normalized; status values are mapped to a controlled set.
- Invalid negative or implausibly large waiting times are treated as missing.
- Missing waiting times are imputed with the department median, falling back to the overall median.
- Missing satisfaction scores are retained because imputing subjective feedback could distort analysis.
- Missing departments are labeled `Unknown`.
- Invalid core identifiers, dates, and statuses are excluded.
- Duplicate appointment IDs are reduced to one record after exact-duplicate removal.

These are demonstration choices, not universal rules. In real work, agree on business definitions and document decisions with stakeholders.

## SQL practice

Open `sql/queries.sql` for examples of:

- Aggregations, `GROUP BY`, `CASE`, and `HAVING`
- CTEs and subqueries
- Window functions (`RANK`, `LAG`)
- Monthly cancellation rates
- Data-quality checks

SQLite supports the SQL features used in this project.

## Tests

Install test tooling and run:

```powershell
python -m pip install pytest
python -m pytest -q
```

## Suggested interview walkthrough

1. Explain the business problem and why the data is synthetic.
2. Describe the injected data-quality issues and cleaning rules.
3. Explain vectorized operations and why Pandas/NumPy are useful.
4. Walk through one SQL CTE and one window-function query.
5. Explain the KPI definitions and how you validated the totals.
6. Present the charts and discuss what further investigation a real team would need.

## Limitations and next steps

- The dataset is synthetic and cannot establish real-world healthcare conclusions.
- Waiting time is simulated rather than calculated from scheduled and actual timestamps.
- A production system would need source-system lineage, access controls, logging, monitoring, and privacy review.
- Further extensions: unit-test more edge cases, add Excel/Power BI reporting, and schedule the pipeline.

## Resume bullet (use after running and reviewing the project)

**Healthcare Operations Analytics | Python, NumPy, Pandas, SQLite, Matplotlib, Seaborn**
- Built a reproducible analytics pipeline on synthetic appointment data, implementing data cleaning, missing-value treatment, validation checks, SQL-based KPI reporting, and visualizations of department waiting times and monthly cancellation trends.
