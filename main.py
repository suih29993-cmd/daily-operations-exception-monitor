# -*- coding: utf-8 -*-
"""CLI entry point for the synthetic abnormal-closure reporting demo."""
from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path

from closure_report.calculator import compute
from closure_report.config import Config
from closure_report.report import write_excel, write_json, write_markdown


def setup_logging(cfg: Config) -> None:
    path = cfg.path(cfg.app["log_dir"])
    path.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(path / "closure_report.log", encoding="utf-8"), logging.StreamHandler(sys.stdout)],
        force=True,
    )


def run(cfg: Config, examples: bool = False) -> dict:
    payload = compute(cfg)
    output_dir = cfg.path(cfg.app["archive_dir"])
    xlsx = write_excel(payload, output_dir / "demo_daily_abnormal_closure.xlsx")
    json_path = write_json(payload, output_dir / "demo_daily_abnormal_closure.json")
    md_path = write_markdown(payload, output_dir / "demo_daily_abnormal_closure.md")
    if examples:
        example_dir = cfg.root / "examples"
        example_dir.mkdir(parents=True, exist_ok=True)
        for source in (xlsx, json_path, md_path):
            shutil.copy2(source, example_dir / source.name)
    logging.getLogger(__name__).info("anomalies=%s stores=%s minutes=%s impact=%.2f", payload["totals"]["anomalies"], payload["totals"]["stores"], payload["totals"]["abnormal_minutes"], payload["totals"]["estimated_impacted_sales"])
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthetic daily abnormal-closure report")
    parser.add_argument("--config", help="optional path to config.yaml")
    sub = parser.add_subparsers(dest="command", required=True)
    run_cmd = sub.add_parser("run", help="generate JSON, Markdown and Excel outputs")
    run_cmd.add_argument("--examples", action="store_true", help="also refresh examples/")
    sub.add_parser("validate", help="run all checks without writing reports")
    args = parser.parse_args(argv)
    cfg = Config.load(Path(args.config) if args.config else None)
    cfg.validate()
    setup_logging(cfg)
    if args.command == "validate":
        payload = compute(cfg)
        if payload["validation"]["missing_business_hours"]:
            raise SystemExit("validation failed: missing business hours")
        if payload["totals"]["anomalies"] == 0:
            raise SystemExit("validation failed: no synthetic anomalies detected")
        print(f"validation passed: {payload['totals']}")
        return 0
    payload = run(cfg, examples=args.examples)
    print(f"generated {payload['totals']['anomalies']} anomalies; estimated synthetic impact CNY {payload['totals']['estimated_impacted_sales']:,.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
