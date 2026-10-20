from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import Config
from .intervals import format_segments, parse_segments, subtract_intervals, total_minutes
from .parser import Activity, StoreHours, load_activity, load_business_hours


def _event(activity: Activity, hours: StoreHours, cfg: Config, gaps: list[tuple[int, int]]) -> dict[str, Any]:
    minutes = total_minutes(gaps)
    estimated = round(hours.expected_hourly_sales * (minutes / 60.0) * float(cfg.rules["impact_factor"]), 2)
    return {
        "date": activity.date.isoformat(),
        "weekday": activity.date.strftime("%A"),
        "channel": activity.channel,
        "store_id": hours.store_id,
        "store_name": hours.store_name,
        "region": hours.region,
        "city": hours.city,
        "supervisor": hours.supervisor,
        "planned_segments": format_segments(parse_segments(f"{hours.open_start}-{hours.open_end}")),
        "actual_segments": format_segments(parse_segments(activity.online_segments)),
        "abnormal_segments": format_segments(gaps),
        "abnormal_minutes": minutes,
        "expected_hourly_sales": round(hours.expected_hourly_sales, 2),
        "estimated_impacted_sales": estimated,
        "orders": activity.orders,
        "gmv": round(activity.gmv, 2),
    }


def compute(cfg: Config) -> dict[str, Any]:
    hours = load_business_hours(cfg.path(cfg.app["business_hours_path"]))
    activities = load_activity(cfg.path(cfg.app["activity_path"]))
    threshold = int(cfg.rules["min_abnormal_minutes"])
    tolerance = int(cfg.rules.get("gap_merge_tolerance_minutes", 0))
    anomalies = []
    validation = {"activity_rows": len(activities), "matched_rows": 0, "missing_business_hours": [], "below_threshold": 0}
    for activity in activities:
        key = (activity.store_id, activity.date.weekday())
        store_hours = hours.get(key)
        if store_hours is None:
            validation["missing_business_hours"].append(activity.store_id)
            continue
        validation["matched_rows"] += 1
        planned = parse_segments(f"{store_hours.open_start}-{store_hours.open_end}")
        actual = parse_segments(activity.online_segments)
        gaps = subtract_intervals(planned, actual, tolerance=tolerance)
        minutes = total_minutes(gaps)
        if minutes < threshold:
            validation["below_threshold"] += 1
            continue
        anomalies.append(_event(activity, store_hours, cfg, gaps))

    region_summary = _summary(anomalies, "region")
    supervisor_summary = _summary(anomalies, ("region", "supervisor"))
    channel_summary = _summary(anomalies, "channel")
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_mode": cfg.app["source_mode"],
        "simulation": True,
        "notice": "All stores, schedules, sales and impact estimates are synthetic. This is not a real business result.",
        "rules": {
            "min_abnormal_minutes": threshold,
            "impact_factor": float(cfg.rules["impact_factor"]),
            "gap_merge_tolerance_minutes": tolerance,
            "impact_formula": "expected_hourly_sales × abnormal_minutes ÷ 60 × impact_factor",
        },
        "validation": validation,
        "totals": {
            "anomalies": len(anomalies),
            "stores": len({row["store_id"] for row in anomalies}),
            "abnormal_minutes": sum(row["abnormal_minutes"] for row in anomalies),
            "estimated_impacted_sales": round(sum(row["estimated_impacted_sales"] for row in anomalies), 2),
        },
        "anomalies": sorted(anomalies, key=lambda row: (row["date"], row["region"], row["supervisor"], row["store_id"], row["channel"])),
        "region_summary": region_summary,
        "supervisor_summary": supervisor_summary,
        "channel_summary": channel_summary,
    }


def _summary(rows: list[dict], group_key: str | tuple[str, ...]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    keys = (group_key,) if isinstance(group_key, str) else group_key
    for row in rows:
        groups[tuple(row[key] for key in keys)].append(row)
    output = []
    for values, items in sorted(groups.items()):
        output.append({
            **dict(zip(keys, values)),
            "anomalies": len(items),
            "stores": len({item["store_id"] for item in items}),
            "abnormal_minutes": sum(item["abnormal_minutes"] for item in items),
            "estimated_impacted_sales": round(sum(item["estimated_impacted_sales"] for item in items), 2),
        })
    return output
