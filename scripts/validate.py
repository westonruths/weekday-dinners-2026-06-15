#!/usr/bin/env python3
"""Validate Ruths Weekly Meal Plans JSON data."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "weeks" / "index.json"
REQUIRED_PLAN_FIELDS = [
    "title",
    "description",
    "useFirst",
    "useLater",
    "timeTarget",
    "buyIfNeeded",
    "days",
    "groceryList",
]
REQUIRED_DAY_FIELDS = [
    "id",
    "dateLabel",
    "title",
    "protein",
    "carb",
    "veg",
    "time",
    "ingredients",
    "steps",
    "ariaServing",
]


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def validate_day(path: Path, day: dict, idx: int) -> None:
    for field in REQUIRED_DAY_FIELDS:
        require(field in day, f"{path.relative_to(ROOT)} day {idx}: missing {field}")
    for field in ["id", "dateLabel", "title", "protein", "carb", "veg", "time", "ariaServing"]:
        require(isinstance(day[field], str) and day[field].strip(), f"{path.relative_to(ROOT)} day {idx}: {field} must be a non-empty string")
    for field in ["ingredients", "steps"]:
        require(isinstance(day[field], list) and day[field], f"{path.relative_to(ROOT)} day {idx}: {field} must be a non-empty list")
        require(all(isinstance(item, str) and item.strip() for item in day[field]), f"{path.relative_to(ROOT)} day {idx}: {field} items must be non-empty strings")
    if "tags" in day:
        require(isinstance(day["tags"], list), f"{path.relative_to(ROOT)} day {idx}: tags must be a list")


def validate_plan(path: Path) -> None:
    plan = load_json(path)
    for field in REQUIRED_PLAN_FIELDS:
        require(field in plan, f"{path.relative_to(ROOT)}: missing {field}")
    require(isinstance(plan["days"], list), f"{path.relative_to(ROOT)}: days must be a list")
    require(len(plan["days"]) == 5, f"{path.relative_to(ROOT)}: expected exactly 5 weekday dinners, found {len(plan['days'])}")
    require(isinstance(plan["groceryList"], list), f"{path.relative_to(ROOT)}: groceryList must be a list")
    ids = []
    for idx, day in enumerate(plan["days"], start=1):
        validate_day(path, day, idx)
        ids.append(day["id"])
    require(len(ids) == len(set(ids)), f"{path.relative_to(ROOT)}: day ids must be unique")


def main() -> None:
    index = load_json(INDEX)
    weeks_value = index.get("weeks")
    require(isinstance(weeks_value, list), "data/weeks/index.json: weeks must be a list")
    if not isinstance(weeks_value, list):
        raise AssertionError("unreachable")
    weeks: list[dict] = weeks_value
    require(len(weeks) > 0, "data/weeks/index.json: weeks must be non-empty")
    slugs = []
    for week in weeks:
        for field in ["slug", "label", "path"]:
            require(field in week and isinstance(week[field], str) and week[field].strip() != "", f"data/weeks/index.json: each week needs {field}")
        slugs.append(week["slug"])
        path = ROOT / week["path"]
        require(path.exists(), f"data/weeks/index.json: missing plan file {week['path']}")
        validate_plan(path)
        page = ROOT / "weeks" / week["slug"] / "index.html"
        require(page.exists(), f"data/weeks/index.json: missing generated page weeks/{week['slug']}/index.html")
        page_text = page.read_text(encoding="utf-8")
        require("window.MEAL_PLAN_BASE = '../../'" in page_text, f"weeks/{week['slug']}/index.html: missing subpage base path")
    require(len(slugs) == len(set(slugs)), "data/weeks/index.json: week slugs must be unique")
    print(f"OK: validated {len(weeks)} week(s) and subpage(s)")


if __name__ == "__main__":
    main()
