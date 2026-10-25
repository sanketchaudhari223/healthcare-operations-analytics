"""Create charts using Matplotlib and Seaborn."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Works in terminals/CI without a display.
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def create_charts(
    df: pd.DataFrame,
    dept_summary: pd.DataFrame,
    month_summary: pd.DataFrame,
    output_dir: Path,
) -> list[Path]:
    """Save a small set of portfolio-ready charts and return their paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    outputs = []

    fig, ax = plt.subplots(figsize=(10, 6))
    plotted = dept_summary.sort_values("average_wait_minutes", ascending=True)
    ax.barh(plotted["department"], plotted["average_wait_minutes"])
    ax.set_title("Average Appointment Waiting Time by Department")
    ax.set_xlabel("Average wait (minutes)")
    ax.set_ylabel("Department")
    fig.tight_layout()
    path = output_dir / "average_wait_by_department.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    outputs.append(path)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(
        data=month_summary, x="month", y="cancellation_rate_pct",
        marker="o", ax=ax
    )
    ax.set_title("Monthly Appointment Cancellation Rate")
    ax.set_xlabel("Month")
    ax.set_ylabel("Cancellation rate (%)")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    path = output_dir / "monthly_cancellation_rate.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    outputs.append(path)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(df["wait_time_minutes"].dropna(), bins=25)
    ax.set_title("Distribution of Appointment Waiting Times")
    ax.set_xlabel("Wait (minutes)")
    ax.set_ylabel("Appointment count")
    fig.tight_layout()
    path = output_dir / "waiting_time_distribution.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    outputs.append(path)

    return outputs
