# Zurich Transport Delay Analysis (VBZ)

End-to-end analytics project on Zurich public transport reliability using Python and SQLite.

- Scope: 1,402,968 trip-segment records
- Time window: 2022-12-25 to 2022-12-31
- Focus: delay hotspots by line, hour, stop, and daily trend

## Business Problem
Public transport operators need to know where and when delays are concentrated to prioritize operational interventions. This project builds a reproducible workflow to convert raw trip-segment logs into actionable reliability KPIs.

## Dataset
- Source: Zurich Open Data (VBZ delay records)
- Raw file expected at: `data/raw/vbz_delays_original.csv`
- Granularity: trip-segment operational records
- Main fields: line, stop codes, scheduled/actual departure and arrival times

## Methodology
1. Clean and validate raw timestamps.
2. Engineer delay and travel-time metrics.
3. Load analysis-ready data into SQLite with indexes.
4. Run SQL aggregations for line/hour/stop/date views.
5. Export summary tables (CSV) and visual outputs (PNG).

## Engineered KPIs
- `departure_delay_sec`
- `arrival_delay_sec`
- `scheduled_travel_sec`
- `actual_travel_sec`
- `travel_time_diff_sec`
- `is_delayed_departure`
- `departure_hour`

## Key Findings
- Strong year-end effect: average departure delay rose to **28.68s on 2022-12-31** vs **11.00s** average on 2022-12-25 to 2022-12-30.
- Several lines show materially higher average delay than the system baseline.
- Delay incidence varies by hour and stop, indicating location/time-specific operational pressure.

## Recommendations
- Prioritize monitoring and staffing for high-delay lines and high-delay stop clusters.
- Add time-window alerting around historically high-delay periods.
- Track year-end and event-period reliability separately from normal-week baselines.

## Tech Stack
- Python (pandas, NumPy, matplotlib, seaborn)
- SQLite
- Jupyter Notebooks

## Repository Structure
```text
Zurich-transport-delay-analysis/
|-- data/
|   |-- raw/
|   `-- processed/
|       |-- q1_delay_by_line.csv
|       |-- q2_delay_by_hour.csv
|       |-- q3_delay_by_stop.csv
|       |-- q4_travel_time_diff.csv
|       `-- q5_delay_trend.csv
|-- notebooks/
|   |-- 01_data_cleaning.ipynb
|   |-- 02_exploratory_analysis.ipynb
|   `-- 03_delay_analysis.ipynb
|-- src/
|   |-- cleaning.py
|   `-- analysis.py
|-- visuals/
|   |-- delay_by_line.png
|   |-- delay_by_hour.png
|   `-- delay_heatmap.png
|-- requirements.txt
`-- README.md
```

## How to Run
```bash
pip install -r requirements.txt
python src/cleaning.py
python src/analysis.py
```

Outputs are generated in:
- `data/processed/`
- `visuals/`

## Visuals
![Delay by Line](visuals/delay_by_line.png)
![Average Delay Heatmap](visuals/delay_heatmap.png)

## CV-Ready Impact
- Built a reproducible Python + SQLite pipeline on 1.4M+ transport records.
- Identified delay hotspots by line, stop, and hour using SQL-based KPI analysis.
- Quantified an end-of-year delay spike on 2022-12-31, supporting targeted operational monitoring.

## Limitations
- Analysis covers one week only (2022-12-25 to 2022-12-31).
- Night-hour delay percentages can be sensitive to lower service frequency.
- Results are descriptive analytics, not a predictive model.

## Next Steps
- Extend to multi-month data for seasonality and stability checks.
- Add route-level segmentation and service-type comparison.
- Build a lightweight dashboard for operational reporting.
