from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

DB_DEFAULT = Path("data/processed/vbz_delays.db")
OUTPUT_DIR_DEFAULT = Path("visuals")
SUMMARY_DIR_DEFAULT = Path("data/processed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run delay analysis queries and save plots.")
    parser.add_argument("--db", type=Path, default=DB_DEFAULT, help="Path to SQLite database file.")
    parser.add_argument("--visuals", type=Path, default=OUTPUT_DIR_DEFAULT, help="Output folder for PNG charts.")
    parser.add_argument("--summaries", type=Path, default=SUMMARY_DIR_DEFAULT, help="Output folder for CSV summaries.")
    return parser.parse_args()


def load_query(conn: sqlite3.Connection, query: str) -> pd.DataFrame:
    return pd.read_sql_query(query, conn)


def save_summary(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> None:
    args = parse_args()
    args.visuals.mkdir(parents=True, exist_ok=True)
    args.summaries.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid")
    with sqlite3.connect(args.db) as conn:
        q1 = """
        SELECT
            linie,
            COUNT(*) AS total_trips,
            ROUND(AVG(departure_delay_sec), 2) AS avg_departure_delay_sec,
            ROUND(100.0 * AVG(is_delayed_departure), 2) AS pct_delayed_departures
        FROM delays_clean
        GROUP BY linie
        HAVING COUNT(*) >= 100
        ORDER BY avg_departure_delay_sec DESC
        """
        df_q1 = load_query(conn, q1)
        save_summary(df_q1, args.summaries / "q1_delay_by_line.csv")

        top_lines = df_q1.head(15).sort_values("avg_departure_delay_sec")
        plt.figure(figsize=(10, 7))
        plt.barh(top_lines["linie"], top_lines["avg_departure_delay_sec"], color="#1f77b4")
        plt.xlabel("Average departure delay (seconds)")
        plt.ylabel("Line")
        plt.title("Average Delay by Transport Line (Top 15)")
        plt.tight_layout()
        plt.savefig(args.visuals / "delay_by_line.png", dpi=150)
        plt.close()

        q2 = """
        SELECT
            departure_hour,
            COUNT(*) AS total_trips,
            ROUND(AVG(departure_delay_sec), 2) AS avg_departure_delay_sec,
            ROUND(100.0 * AVG(is_delayed_departure), 2) AS pct_delayed_departures
        FROM delays_clean
        GROUP BY departure_hour
        ORDER BY departure_hour
        """
        df_q2 = load_query(conn, q2)
        save_summary(df_q2, args.summaries / "q2_delay_by_hour.csv")

        plt.figure(figsize=(10, 5))
        plt.plot(df_q2["departure_hour"], df_q2["pct_delayed_departures"], marker="o", color="#d62728")
        plt.xlabel("Hour of day")
        plt.ylabel("% delayed departures")
        plt.title("Delayed Departures by Hour")
        plt.xticks(range(0, 24, 1))
        plt.tight_layout()
        plt.savefig(args.visuals / "delay_by_hour.png", dpi=150)
        plt.close()

        q3 = """
        SELECT
            halt_kurz_von AS stop_code,
            COUNT(*) AS total_departures,
            ROUND(AVG(departure_delay_sec), 2) AS avg_departure_delay_sec,
            ROUND(100.0 * AVG(is_delayed_departure), 2) AS pct_delayed_departures
        FROM delays_clean
        GROUP BY halt_kurz_von
        HAVING COUNT(*) >= 100
        ORDER BY pct_delayed_departures DESC
        """
        df_q3 = load_query(conn, q3)
        save_summary(df_q3, args.summaries / "q3_delay_by_stop.csv")

        q4 = """
        SELECT
            linie,
            COUNT(*) AS total_segments,
            ROUND(AVG(scheduled_travel_sec), 2) AS avg_scheduled_travel_sec,
            ROUND(AVG(actual_travel_sec), 2) AS avg_actual_travel_sec,
            ROUND(AVG(travel_time_diff_sec), 2) AS avg_travel_time_diff_sec
        FROM delays_clean
        GROUP BY linie
        HAVING COUNT(*) >= 100
        ORDER BY avg_travel_time_diff_sec DESC
        """
        df_q4 = load_query(conn, q4)
        save_summary(df_q4, args.summaries / "q4_travel_time_diff.csv")

        q5 = """
        SELECT
            DATE(betriebsdatum) AS service_date,
            COUNT(*) AS total_trips,
            ROUND(AVG(departure_delay_sec), 2) AS avg_departure_delay_sec,
            ROUND(100.0 * AVG(is_delayed_departure), 2) AS pct_delayed_departures
        FROM delays_clean
        GROUP BY DATE(betriebsdatum)
        ORDER BY DATE(betriebsdatum)
        """
        df_q5 = load_query(conn, q5)
        save_summary(df_q5, args.summaries / "q5_delay_trend.csv")

        q_heatmap = """
        SELECT
            CAST(strftime('%w', betriebsdatum) AS INTEGER) AS day_of_week,
            departure_hour,
            AVG(departure_delay_sec) AS avg_delay_sec
        FROM delays_clean
        GROUP BY day_of_week, departure_hour
        ORDER BY day_of_week, departure_hour
        """
        df_heat = load_query(conn, q_heatmap)

    day_map = {
        0: "Sun",
        1: "Mon",
        2: "Tue",
        3: "Wed",
        4: "Thu",
        5: "Fri",
        6: "Sat",
    }
    df_heat["day_of_week"] = df_heat["day_of_week"].map(day_map)
    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    heatmap_data = df_heat.pivot(index="day_of_week", columns="departure_hour", values="avg_delay_sec")
    heatmap_data = heatmap_data.reindex(day_order)

    plt.figure(figsize=(12, 5))
    sns.heatmap(heatmap_data, cmap="YlOrRd", cbar_kws={"label": "Avg delay (sec)"})
    plt.xlabel("Hour of day")
    plt.ylabel("Day of week")
    plt.title("Average Delay Heatmap")
    plt.tight_layout()
    plt.savefig(args.visuals / "delay_heatmap.png", dpi=150)
    plt.close()

    if len(df_q5) >= 2:
        x = np.arange(len(df_q5))
        y = df_q5["avg_departure_delay_sec"].to_numpy(dtype=float)
        slope, _ = np.polyfit(x, y, 1)
        trend_label = "increasing" if slope > 0 else "decreasing"
        print(f"Delay trend based on linear fit: {trend_label} ({slope:.4f} sec/day index)")
    else:
        print("Not enough daily points to estimate trend.")

    print(f"Saved visuals to: {args.visuals}")
    print(f"Saved summary CSVs to: {args.summaries}")


if __name__ == "__main__":
    main()
