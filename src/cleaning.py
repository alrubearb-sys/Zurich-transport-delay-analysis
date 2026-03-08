from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

RAW_DEFAULT = Path("data/raw/vbz_delays_original.csv")
CLEAN_DEFAULT = Path("data/processed/vbz_delays_clean.csv")
DB_DEFAULT = Path("data/processed/vbz_delays.db")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean VBZ delay dataset and load to SQLite.")
    parser.add_argument("--input", type=Path, default=RAW_DEFAULT, help="Path to raw CSV file.")
    parser.add_argument("--output", type=Path, default=CLEAN_DEFAULT, help="Path to cleaned CSV file.")
    parser.add_argument("--db", type=Path, default=DB_DEFAULT, help="Path to SQLite database file.")
    return parser.parse_args()


def safe_time_diff(end_seconds: pd.Series, start_seconds: pd.Series) -> pd.Series:
    """Compute time difference in seconds with midnight rollover handling."""
    diff = end_seconds - start_seconds
    diff = np.where(diff < -43200, diff + 86400, diff)
    diff = np.where(diff > 43200, diff - 86400, diff)
    return pd.Series(diff, index=end_seconds.index)


def clean_data(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path, low_memory=False)
    df = df.rename(
        columns={
            "halt_kurz_von1": "halt_kurz_von",
            "halt_kurz_nach1": "halt_kurz_nach",
            "ist_an_nach1": "ist_an_nach",
        }
    )

    required_cols = [
        "linie",
        "betriebsdatum",
        "halt_kurz_von",
        "halt_kurz_nach",
        "soll_ab_von",
        "ist_ab_von",
        "soll_an_nach",
        "ist_an_nach",
    ]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    df["betriebsdatum"] = pd.to_datetime(df["betriebsdatum"], format="%d.%m.%y", errors="coerce")
    time_cols = ["soll_ab_von", "ist_ab_von", "soll_an_nach", "ist_an_nach"]
    for col in time_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["betriebsdatum"] + time_cols)
    df["linie"] = df["linie"].astype(str)
    df["halt_kurz_von"] = df["halt_kurz_von"].astype(str)
    df["halt_kurz_nach"] = df["halt_kurz_nach"].astype(str)

    df["departure_delay_sec"] = df["ist_ab_von"] - df["soll_ab_von"]
    df["arrival_delay_sec"] = df["ist_an_nach"] - df["soll_an_nach"]
    df["scheduled_travel_sec"] = safe_time_diff(df["soll_an_nach"], df["soll_ab_von"])
    df["actual_travel_sec"] = safe_time_diff(df["ist_an_nach"], df["ist_ab_von"])
    df["travel_time_diff_sec"] = df["actual_travel_sec"] - df["scheduled_travel_sec"]
    df["departure_hour"] = (df["soll_ab_von"] // 3600).astype(int) % 24
    df["is_delayed_departure"] = (df["departure_delay_sec"] > 0).astype(int)

    cols_to_keep = [
        "linie",
        "betriebsdatum",
        "halt_kurz_von",
        "halt_kurz_nach",
        "soll_ab_von",
        "ist_ab_von",
        "soll_an_nach",
        "ist_an_nach",
        "departure_hour",
        "departure_delay_sec",
        "arrival_delay_sec",
        "scheduled_travel_sec",
        "actual_travel_sec",
        "travel_time_diff_sec",
        "is_delayed_departure",
    ]
    return df[cols_to_keep].copy()


def save_outputs(df: pd.DataFrame, output_csv: Path, output_db: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_db.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_csv, index=False)

    with sqlite3.connect(output_db) as conn:
        df.to_sql("delays_clean", conn, if_exists="replace", index=False)
        conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_delays_line ON delays_clean(linie);
            CREATE INDEX IF NOT EXISTS idx_delays_date ON delays_clean(betriebsdatum);
            CREATE INDEX IF NOT EXISTS idx_delays_hour ON delays_clean(departure_hour);
            CREATE INDEX IF NOT EXISTS idx_delays_stop_from ON delays_clean(halt_kurz_von);
            """
        )


def main() -> None:
    args = parse_args()
    df = clean_data(args.input)
    save_outputs(df, args.output, args.db)
    print(f"Rows cleaned: {len(df):,}")
    print(f"Clean CSV: {args.output}")
    print(f"SQLite DB: {args.db}")


if __name__ == "__main__":
    main()
