-- Healthcare Operations Analytics: SQLite interview practice
-- Run against data/healthcare_analytics.sqlite after running the pipeline.

-- 1. Basic aggregation: average waiting time by department.
SELECT department,
       COUNT(*) AS appointment_count,
       ROUND(AVG(wait_time_minutes), 2) AS average_wait_minutes
FROM appointments
GROUP BY department
ORDER BY average_wait_minutes DESC;

-- 2. CASE expression: classify waiting time.
SELECT appointment_id, wait_time_minutes,
       CASE
           WHEN wait_time_minutes < 20 THEN 'Short'
           WHEN wait_time_minutes < 45 THEN 'Moderate'
           ELSE 'Long'
       END AS wait_category
FROM appointments
LIMIT 20;

-- 3. CTE: departments with above-overall-average waiting times.
WITH overall AS (
    SELECT AVG(wait_time_minutes) AS overall_average
    FROM appointments
),
department_wait AS (
    SELECT department, AVG(wait_time_minutes) AS average_wait
    FROM appointments
    GROUP BY department
)
SELECT d.department,
       ROUND(d.average_wait, 2) AS average_wait,
       ROUND(o.overall_average, 2) AS overall_average
FROM department_wait d
CROSS JOIN overall o
WHERE d.average_wait > o.overall_average
ORDER BY d.average_wait DESC;

-- 4. Window function: rank departments by average waiting time.
WITH department_wait AS (
    SELECT department, AVG(wait_time_minutes) AS average_wait
    FROM appointments
    GROUP BY department
)
SELECT department,
       ROUND(average_wait, 2) AS average_wait,
       RANK() OVER (ORDER BY average_wait DESC) AS wait_rank
FROM department_wait;

-- 5. Monthly cancellation rate.
SELECT strftime('%Y-%m', appointment_date) AS month,
       COUNT(*) AS appointments,
       SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
       ROUND(
           100.0 * SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END)
           / COUNT(*), 2
       ) AS cancellation_rate_pct
FROM appointments
GROUP BY strftime('%Y-%m', appointment_date)
ORDER BY month;

-- 6. LAG: compare each month's cancellation rate with the previous month.
WITH monthly AS (
    SELECT strftime('%Y-%m', appointment_date) AS month,
           100.0 * SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END)
           / COUNT(*) AS cancellation_rate_pct
    FROM appointments
    GROUP BY strftime('%Y-%m', appointment_date)
)
SELECT month,
       ROUND(cancellation_rate_pct, 2) AS cancellation_rate_pct,
       ROUND(
           cancellation_rate_pct - LAG(cancellation_rate_pct)
           OVER (ORDER BY month), 2
       ) AS change_vs_previous_month_pp
FROM monthly
ORDER BY month;

-- 7. Data quality: duplicate appointment IDs (expected result: zero rows).
SELECT appointment_id, COUNT(*) AS occurrences
FROM appointments
GROUP BY appointment_id
HAVING COUNT(*) > 1;

-- 8. Status breakdown.
SELECT status, COUNT(*) AS appointment_count,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM appointments), 2) AS pct
FROM appointments
GROUP BY status
ORDER BY appointment_count DESC;
