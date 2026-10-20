# Synthetic Daily Abnormal Closure Report

A reproducible Python workflow for detecting abnormal closure intervals from planned versus observed online segments, estimating the affected duration and generating region, supervisor and channel summaries.

> **Data notice:** all schedules, stores, channel activity, orders and monetary values are synthetic. The estimated impacted sales column is a **simulation** and must not be presented as actual business performance.

## What it demonstrates

- CSV ingestion with schema and master-data validation.
- Interval parsing, merging and subtraction for time-segment gaps.
- Minimum-duration filtering and configurable example impact assumptions.
- Region, supervisor and channel aggregation.
- Excel report generation with detail, summary, methodology and validation sheets.
- Local Markdown/JSON output and structured logging.
- Guardrails that refuse live modes and external notification channels.

## Workflow

```text
business hours ─┐
                ├─ interval comparison ─ gap minutes ─ impact estimate ─ grouped report
activity rows ──┘
```

The impact formula is intentionally simple and transparent:

```text
estimated impacted sales = expected hourly sales × abnormal minutes ÷ 60 × impact factor
```

`impact_factor` is an illustrative assumption in this portfolio version. It is not a production rule.

## Quick start

```powershell
python -m pip install -r requirements.txt
python scripts/generate_demo_inputs.py
python main.py run --examples
python main.py validate
```

Generated files:

- `outputs/demo_daily_abnormal_closure.xlsx`
- `outputs/demo_daily_abnormal_closure.md`
- `outputs/demo_daily_abnormal_closure.json`
- copies under `examples/` when `--examples` is used

## Project structure

```text
main.py                         CLI
closure_report/config.py        configuration and safety guard
closure_report/parser.py        CSV/master-data loaders
closure_report/intervals.py     time interval operations
closure_report/calculator.py    anomaly detection and grouping
closure_report/report.py        Excel, Markdown and JSON writers
data/                           deterministic synthetic inputs
tests/                          unit and integration tests
docs/METHODOLOGY.md             calculation and simulation boundaries
```

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Scope

This is a public portfolio implementation, not a deployed enterprise service. It does not log into vendor portals, download reports, read browser profiles, send group messages or use internal master data. A production deployment would require separate authorization, secret management, data retention controls and validation against approved operational rules.

## Isolation and safety

- Bundled defaults and relative paths resolve from this project directory. The demo reads only `data/demo_business_hours.csv` and `data/demo_activity.csv`.
- Reports and logs stay under `outputs/`; refreshed preview copies stay under `examples/`. No shared output directory or original project file is used.
- `Config.validate()` accepts only `source_mode: demo` and `notify.channel: file`. Live modes and external notification channels fail before report generation.
- The code contains no HTTP, webhook, browser-automation, credential or recipient integration. It cannot contact a merchant portal, internal service or group chat.
- Dependencies are Python, openpyxl and the standard library. All monetary values are synthetic and explicitly labelled as simulations.
