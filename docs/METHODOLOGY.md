# Methodology and Simulation Boundaries

## Inputs

1. `demo_business_hours.csv` defines a synthetic planned operating window and expected hourly sales for each store/weekday.
2. `demo_activity.csv` defines synthetic observed online segments for each store/date/channel.

## Detection

Planned and observed segments are converted to minute ranges. Intervals are merged, then the observed range is subtracted from the planned range. Each remaining gap is an abnormal closure interval.

Only rows whose total gap is at least `min_abnormal_minutes` are included in the report.

## Impact estimate

```text
estimated impacted sales = expected_hourly_sales × abnormal_minutes ÷ 60 × impact_factor
```

The estimate is deliberately labelled as synthetic. It does not reconstruct lost demand, customer behavior, promotions or channel substitution. It exists to demonstrate rule implementation and reporting structure.

## Outputs

- `Daily_Summary`: headline counts and simulated impact.
- `Anomaly_Details`: store/date/channel gaps and estimated values.
- `Region_Summary`, `Supervisor_Summary`, `Channel_Summary`: grouped views.
- `Methodology`: formula, assumptions and data classification.
- `Input_Validation`: row counts and master-data coverage.

## Safety constraints

- `source_mode` must be `demo`.
- `notify.channel` must be `file`.
- No network request, browser automation, credential or recipient configuration exists in the public implementation.
