# Zurich Transport Delay Analysis

End-to-end data analytics project focused on operational delay patterns in Zurich public transport (VBZ).

## Project Objective
Identify where and when delays happen most often, quantify travel-time gaps, and evaluate short-term delay trend behavior.

## Business Questions
1. Which transport lines experience the most delays?
2. At what times of the day are delays most frequent?
3. Which stops have the highest delay rates?
4. How does actual travel time differ from scheduled time?
5. Are delays increasing or decreasing over time?

## Dataset
- Source file: `data/raw/vbz_delays_original.csv`
- Coverage: 7 days of operations (`2022-12-25` to `2022-12-31`)
- Grain: trip segment-level operational records (scheduled vs actual timings)
- Volume analyzed: `1,402,968` trip segments

## Methodology
1. Data cleaning and feature engineering in Python (`src/cleaning.py`)
2. Structured storage in SQLite (`data/processed/vbz_delays.db`)
3. SQL-based aggregation for each business question (`src/analysis.py`)
4. Visual reporting in PNG + summary CSV exports

## Key Engineered Metrics
- `departure_delay_sec`: actual departure minus scheduled departure
- `arrival_delay_sec`: actual arrival minus scheduled arrival
- `scheduled_travel_sec`: planned segment travel time
- `actual_travel_sec`: observed segment travel time
- `travel_time_diff_sec`: actual minus scheduled travel time
- `departure_hour`: hour-of-day feature for peak-time analysis

## Key Findings 
- **Most delay-prone lines (by average departure delay):** line `91` (64.74 sec), line `163` (46.85 sec), line `309` (42.52 sec).
- **High-volume lines with relevant delay burden:** line `31` handled `64,488` segments with `29.34 sec` average departure delay; line `32` handled `49,212` segments with `23.47 sec`.
- **Most delay-prone hours (by delay rate):** `02:00` (75.36% delayed departures) and `01:00` (69.09%). Among high-volume daytime windows, `14:00-15:00` showed elevated delay rates (60.34% to 61.18%).
- **Stops with highest delay rates (minimum 500 departures):** `BWEI` (92.19%), `BDIE` (90.47%), `ITFA` (89.04%).
- **Travel-time gap:** lines `307`, `309`, and `91` showed the largest positive actual-vs-scheduled segment gaps (11.82 sec, 11.33 sec, and 11.21 sec).
- **Trend over the week:** average delay rose sharply on `2022-12-31` (`28.68 sec`) compared with the first six-day average (`11.00 sec`), indicating end-of-year operational pressure.

## Tech Stack
- Python: `pandas`, `numpy`, `matplotlib`, `seaborn`
- SQL: SQLite (table creation, indexing, grouped analytics)
- Jupyter Notebooks for analysis narrative

## Repository Structure
```text
zurich-transport-delay-analysis/
|
|-- data/
|   |-- raw/
|   |   `-- vbz_delays_original.csv
|   `-- processed/
|       |-- vbz_delays_clean.csv
|       |-- vbz_delays.db
|       |-- q1_delay_by_line.csv
|       |-- q2_delay_by_hour.csv
|       |-- q3_delay_by_stop.csv
|       |-- q4_travel_time_diff.csv
|       `-- q5_delay_trend.csv
|
|-- notebooks/
|   |-- 01_data_cleaning.ipynb
|   |-- 02_exploratory_analysis.ipynb
|   `-- 03_delay_analysis.ipynb
|
|-- visuals/
|   |-- delay_by_line.png
|   |-- delay_by_hour.png
|   `-- delay_heatmap.png
|
|-- src/
|   |-- cleaning.py
|   `-- analysis.py
|
|-- README.md
|-- requirements.txt
`-- .gitignore
```

## How To Reproduce
```bash
pip install -r requirements.txt
python src/cleaning.py
python src/analysis.py
```

## Output Artifacts
- Clean dataset: `data/processed/vbz_delays_clean.csv`
- SQLite database: `data/processed/vbz_delays.db`
- Question-level summaries: `data/processed/q1_...q5_*.csv`
- Visuals: `visuals/delay_by_line.png`, `visuals/delay_by_hour.png`, `visuals/delay_heatmap.png`

## Portfolio Value
This project demonstrates:
- Data cleaning at scale on raw operational transport data
- Practical SQL analytics in SQLite for business-focused questions
- End-to-end reproducibility from raw data to stakeholder-ready outputs
- Clear communication of findings through notebook narrative and visual reporting

## CV-Ready Bullet Points
- Built an end-to-end transport delay analytics pipeline (Python + SQLite) on 1.4M+ VBZ trip-segment records, transforming raw operational data into reusable SQL analytics assets.
- Developed SQL-driven analyses to identify delay hotspots by line, hour, and stop, and quantified actual-vs-scheduled travel-time gaps for operations monitoring.
- Produced stakeholder-ready outputs (clean datasets, indexed SQLite tables, summary CSVs, and visual reports) and highlighted a strong delay spike on 31-Dec-2022 versus the prior six-day baseline.

## GitHub Note on Data Files
To keep the repository lightweight and compatible with GitHub file-size limits, large artifacts are excluded from version control:
- `data/raw/vbz_delays_original.csv`
- `data/processed/vbz_delays_clean.csv`
- `data/processed/vbz_delays.db`

Included in the repo:
- reproducible pipeline (`src/`)
- notebooks (`notebooks/`)
- summary outputs (`data/processed/q1...q5*.csv`)
- visuals (`visuals/`)

If you want to fully reproduce results, place the raw dataset in `data/raw/` and run:
```bash
python src/cleaning.py
python src/analysis.py
```
