# -*- coding: utf-8 -*-
"""Generate deterministic synthetic schedules and channel activity."""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

STORES = []
for region, letter in (("Region_A", "A"), ("Region_B", "B")):
    for index in range(1, 7):
        STORES.append({
            "store_id": f"Store_{letter}{index:03d}",
            "store_name": f"Demo Store {letter}{index:03d}",
            "region": region,
            "city": f"Demo City {letter}{(index + 1) // 2}",
            "supervisor": f"Supervisor_{letter}{(index + 1) // 3}",
            "hourly": 210 + index * 11 + (18 if region == "Region_B" else 0),
        })

DATES = [date(2026, 8, 3), date(2026, 8, 4), date(2026, 8, 5)]

OVERRIDES = {
    ("2026-08-03", "Store_A002", "channel_a"): "10:00-13:00;14:00-16:00;18:00-22:00",
    ("2026-08-03", "Store_A004", "channel_b"): "12:00-22:00",
    ("2026-08-03", "Store_B001", "channel_a"): "10:00-20:00",
    ("2026-08-04", "Store_A006", "channel_b"): "10:00-12:00;12:10-22:00",
    ("2026-08-04", "Store_B003", "channel_a"): "11:00-14:00;16:00-22:00",
    ("2026-08-05", "Store_A005", "channel_a"): "10:00-16:00;17:00-22:00",
    ("2026-08-05", "Store_B002", "channel_b"): "",
}


def hours_for(day: date) -> tuple[str, str]:
    return ("09:30", "22:30") if day.weekday() >= 5 else ("10:00", "22:00")


def minutes_between(start: str, end: str) -> int:
    sh, sm = map(int, start.split(":"))
    eh, em = map(int, end.split(":"))
    return (eh * 60 + em) - (sh * 60 + sm)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    hours_rows = []
    for store in STORES:
        for weekday in range(7):
            start, end = ("09:30", "22:30") if weekday >= 5 else ("10:00", "22:00")
            hours_rows.append({
                "store_id": store["store_id"], "store_name": store["store_name"],
                "region": store["region"], "city": store["city"],
                "supervisor": store["supervisor"], "weekday": weekday,
                "open_start": start, "open_end": end,
                "expected_hourly_sales": f"{store['hourly']:.2f}",
            })
    with (DATA / "demo_business_hours.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(hours_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(hours_rows)

    activity_rows = []
    for day in DATES:
        start, end = hours_for(day)
        for store in STORES:
            for channel in ("channel_a", "channel_b"):
                online = OVERRIDES.get((day.isoformat(), store["store_id"], channel), f"{start}-{end}")
                if online:
                    observed_minutes = sum(
                        minutes_between(*segment.split("-"))
                        for segment in online.split(";") if segment.strip()
                    )
                else:
                    observed_minutes = 0
                gmv = round(store["hourly"] * observed_minutes / 60 * 0.88, 2)
                orders = max(0, int(round(gmv / 34)))
                activity_rows.append({
                    "date": day.isoformat(), "channel": channel,
                    "store_id": store["store_id"], "online_segments": online,
                    "orders": orders, "gmv": f"{gmv:.2f}",
                })
    with (DATA / "demo_activity.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(activity_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(activity_rows)
    print(f"wrote {len(hours_rows)} schedule rows and {len(activity_rows)} activity rows")


if __name__ == "__main__":
    main()
