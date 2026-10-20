from __future__ import annotations

from datetime import time


def parse_time(value: str) -> int:
    text = str(value).strip()
    if not text:
        raise ValueError("empty time")
    parts = text.split(":")
    if len(parts) not in (2, 3):
        raise ValueError(f"invalid time: {value}")
    hour, minute = int(parts[0]), int(parts[1])
    return hour * 60 + minute


def parse_segments(value: str) -> list[tuple[int, int]]:
    segments = []
    for item in str(value or "").split(";"):
        item = item.strip()
        if not item:
            continue
        if "-" not in item:
            raise ValueError(f"invalid segment: {item}")
        start, end = (part.strip() for part in item.split("-", 1))
        start_min, end_min = parse_time(start), parse_time(end)
        if end_min <= start_min:
            raise ValueError(f"segment end must be after start: {item}")
        segments.append((start_min, end_min))
    return merge_intervals(segments)


def merge_intervals(segments: list[tuple[int, int]], tolerance: int = 0) -> list[tuple[int, int]]:
    if not segments:
        return []
    ordered = sorted(segments)
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        previous_start, previous_end = merged[-1]
        if start <= previous_end + max(0, tolerance):
            merged[-1] = (previous_start, max(previous_end, end))
        else:
            merged.append((start, end))
    return merged


def subtract_intervals(planned: list[tuple[int, int]], actual: list[tuple[int, int]], tolerance: int = 0) -> list[tuple[int, int]]:
    gaps = []
    actual = merge_intervals(actual, tolerance)
    for plan_start, plan_end in merge_intervals(planned, tolerance):
        cursor = plan_start
        for actual_start, actual_end in actual:
            if actual_end <= cursor or actual_start >= plan_end:
                continue
            if actual_start > cursor:
                gaps.append((cursor, min(actual_start, plan_end)))
            cursor = max(cursor, actual_end)
            if cursor >= plan_end:
                break
        if cursor < plan_end:
            gaps.append((cursor, plan_end))
    return [(start, end) for start, end in gaps if end - start > tolerance]


def total_minutes(segments: list[tuple[int, int]]) -> int:
    return sum(end - start for start, end in segments)


def format_segments(segments: list[tuple[int, int]]) -> str:
    def fmt(value: int) -> str:
        return f"{value // 60:02d}:{value % 60:02d}"
    return "; ".join(f"{fmt(start)}-{fmt(end)}" for start, end in segments) if segments else "none"
