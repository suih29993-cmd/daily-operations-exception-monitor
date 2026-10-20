from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class StoreHours:
    store_id: str
    store_name: str
    region: str
    city: str
    supervisor: str
    weekday: int
    open_start: str
    open_end: str
    expected_hourly_sales: float


@dataclass(frozen=True)
class Activity:
    date: date
    channel: str
    store_id: str
    online_segments: str
    orders: int
    gmv: float


def load_business_hours(path: Path) -> dict[tuple[str, int], StoreHours]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"store_id", "store_name", "region", "city", "supervisor", "weekday", "open_start", "open_end", "expected_hourly_sales"}
    missing = required - set(rows[0].keys() if rows else [])
    if missing:
        raise ValueError(f"business hours missing columns: {sorted(missing)}")
    result = {}
    for row in rows:
        item = StoreHours(
            store_id=row["store_id"].strip(), store_name=row["store_name"].strip(),
            region=row["region"].strip(), city=row["city"].strip(),
            supervisor=row["supervisor"].strip(), weekday=int(row["weekday"]),
            open_start=row["open_start"].strip(), open_end=row["open_end"].strip(),
            expected_hourly_sales=float(row["expected_hourly_sales"]),
        )
        key = (item.store_id, item.weekday)
        if key in result:
            raise ValueError(f"duplicate business-hours row: {key}")
        result[key] = item
    return result


def load_activity(path: Path) -> list[Activity]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"date", "channel", "store_id", "online_segments", "orders", "gmv"}
    missing = required - set(rows[0].keys() if rows else [])
    if missing:
        raise ValueError(f"activity missing columns: {sorted(missing)}")
    return [
        Activity(
            date=date.fromisoformat(row["date"].strip()),
            channel=row["channel"].strip(),
            store_id=row["store_id"].strip(),
            online_segments=row["online_segments"].strip(),
            orders=int(float(row["orders"])),
            gmv=float(row["gmv"]),
        )
        for row in rows
    ]
