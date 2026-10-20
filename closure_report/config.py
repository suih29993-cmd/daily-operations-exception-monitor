from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULTS: dict[str, Any] = {
    "app": {
        "source_mode": "demo",
        "archive_dir": "outputs",
        "business_hours_path": "data/demo_business_hours.csv",
        "activity_path": "data/demo_activity.csv",
        "log_dir": "outputs/logs",
    },
    "rules": {
        "min_abnormal_minutes": 15,
        "impact_factor": 0.70,
        "gap_merge_tolerance_minutes": 0,
    },
    "notify": {"channel": "file", "output": "outputs/daily_summary.md"},
}


def _merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


@dataclass
class Config:
    root: Path
    data: dict[str, Any]

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        root = (path.parent if path else ROOT).resolve()
        candidate = Path(path) if path else ROOT / "config.yaml"
        raw = yaml.safe_load(candidate.read_text(encoding="utf-8")) if candidate.exists() else {}
        data = _merge(DEFAULTS, raw or {})
        data["app"]["source_mode"] = os.getenv("CLOSURE_SOURCE_MODE", data["app"]["source_mode"])
        data["app"]["archive_dir"] = os.getenv("CLOSURE_ARCHIVE_DIR", data["app"]["archive_dir"])
        return cls(root=root, data=data)

    @property
    def app(self) -> dict[str, Any]:
        return self.data["app"]

    @property
    def rules(self) -> dict[str, Any]:
        return self.data["rules"]

    @property
    def notify(self) -> dict[str, Any]:
        return self.data["notify"]

    def path(self, value: str | Path) -> Path:
        path = Path(value)
        return path if path.is_absolute() else (self.root / path).resolve()

    def validate(self) -> None:
        if self.app.get("source_mode") != "demo":
            raise ValueError("This public demo only supports app.source_mode=demo")
        if self.notify.get("channel") != "file":
            raise ValueError("This public demo only writes local files")
        if not 0 <= float(self.rules.get("impact_factor", 0)) <= 1:
            raise ValueError("rules.impact_factor must be between 0 and 1")
        self.path(self.app["archive_dir"]).mkdir(parents=True, exist_ok=True)
        self.path(self.app["log_dir"]).mkdir(parents=True, exist_ok=True)
