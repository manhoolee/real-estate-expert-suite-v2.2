#!/usr/bin/env python3
"""Deterministic area, unit, revenue, and optional gross-profit calculator."""

import argparse
import csv
import json
from pathlib import Path


SCENARIOS = ("conservative", "base", "optimistic")


def calculate(data: dict) -> dict:
    gfa = float(data["residential_gfa_sqm"])
    ratio = float(data["saleable_ratio"])
    if gfa <= 0 or not 0 < ratio <= 1:
        raise ValueError("residential_gfa_sqm must be positive and saleable_ratio in (0, 1]")
    segments = data.get("segments", [])
    if not segments:
        raise ValueError("segments cannot be empty")
    share_total = sum(float(item["share"]) for item in segments)
    if abs(share_total - 1.0) > 1e-6:
        raise ValueError(f"segment shares must total 1.0, got {share_total}")

    saleable = gfa * ratio
    rows = []
    revenues = {scenario: 0.0 for scenario in SCENARIOS}
    for item in segments:
        share = float(item["share"])
        avg_unit = float(item["avg_unit_gfa"])
        if share < 0 or avg_unit <= 0:
            raise ValueError("shares must be non-negative and avg_unit_gfa positive")
        area = saleable * share
        prices = {scenario: float(item["prices"][scenario]) for scenario in SCENARIOS}
        revenue = {scenario: area * prices[scenario] for scenario in SCENARIOS}
        for scenario in SCENARIOS:
            revenues[scenario] += revenue[scenario]
        rows.append({
            "name": item["name"],
            "share": share,
            "saleable_area_sqm": area,
            "avg_unit_gfa_sqm": avg_unit,
            "approx_units": round(area / avg_unit),
            "prices_yuan_per_sqm": prices,
            "revenue_yuan": revenue,
        })

    weighted_prices = {scenario: revenues[scenario] / saleable for scenario in SCENARIOS}
    result = {
        "model_version": "2.1.0",
        "project": data.get("project", ""),
        "scope_id": data["scope_id"],
        "residential_gfa_sqm": gfa,
        "saleable_ratio": ratio,
        "saleable_area_sqm": saleable,
        "segments": rows,
        "weighted_price_yuan_per_sqm": weighted_prices,
        "revenue_yuan": revenues,
        "evidence_note": "Arithmetic output only; assumptions require market and financial validation.",
    }
    if data.get("total_cost_yuan") is not None:
        cost = float(data["total_cost_yuan"])
        result["total_cost_yuan"] = cost
        result["gross_profit_yuan"] = {s: revenues[s] - cost for s in SCENARIOS}
        result["gross_margin"] = {
            s: (revenues[s] - cost) / revenues[s] if revenues[s] else None for s in SCENARIOS
        }
    return result


def write_csv(result: dict, destination: Path) -> None:
    fields = [
        "name", "share", "saleable_area_sqm", "avg_unit_gfa_sqm", "approx_units",
        "price_conservative", "price_base", "price_optimistic",
        "revenue_conservative", "revenue_base", "revenue_optimistic",
    ]
    with destination.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in result["segments"]:
            writer.writerow({
                "name": row["name"], "share": row["share"],
                "saleable_area_sqm": row["saleable_area_sqm"],
                "avg_unit_gfa_sqm": row["avg_unit_gfa_sqm"],
                "approx_units": row["approx_units"],
                **{f"price_{s}": row["prices_yuan_per_sqm"][s] for s in SCENARIOS},
                **{f"revenue_{s}": row["revenue_yuan"][s] for s in SCENARIOS},
            })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json")
    parser.add_argument("--out-json")
    parser.add_argument("--out-csv")
    args = parser.parse_args()
    data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    try:
        result = calculate(data)
    except (KeyError, TypeError, ValueError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out_json:
        Path(args.out_json).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if args.out_csv:
        write_csv(result, Path(args.out_csv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
