#!/usr/bin/env python3
"""Generate static subpages for each weekly meal plan."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "weeks" / "index.json"

SHELL = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{title}</title>
  <meta name=\"description\" content=\"Reusable weekly dinner plan for the Ruths family.\" />
  <link rel=\"stylesheet\" href=\"{base}assets/styles.css\" />
</head>
<body>
  <header class=\"site-header\">
    <div class=\"eyebrow\">Ruths family dinners</div>
    <h1>Weekly Meal Plans</h1>
    <p class=\"lede\">A reusable meal-planning site for weeknight dinners: each week is stored as structured data, and the page renders full recipes, grocery notes, use-up priorities, and toddler-serving notes.</p>
    <nav class=\"top-actions\" aria-label=\"Site actions\">
      <a class=\"button\" href=\"#week-list\">Choose a week</a>
      <a class=\"button button-secondary\" href=\"{base}templates/week-template.json\">JSON template</a>
      <a class=\"button button-secondary\" href=\"{base}README.md\">How to add a week</a>
    </nav>
  </header>

  <main id=\"app\" class=\"app\" aria-live=\"polite\">
    <section class=\"loading-card\">
      <h2>Loading meal plan…</h2>
      <p>If this stays visible, check that the weekly JSON files are valid and listed in <code>data/weeks/index.json</code>.</p>
    </section>
  </main>

  <footer class=\"site-footer\">
    <p>Static GitHub Pages app. Meal plans are practical household planning, not medical advice; food-safety notes are included where relevant.</p>
  </footer>

  <script>window.MEAL_PLAN_BASE = '{base}';</script>
  <script src=\"{base}assets/app.js\"></script>
</body>
</html>
"""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_shell(path: Path, *, title: str, base: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(SHELL.format(title=title, base=base), encoding="utf-8")


def main() -> None:
    index = load_json(INDEX)
    weeks = index.get("weeks", [])
    if not isinstance(weeks, list) or not weeks:
        raise SystemExit("data/weeks/index.json must contain a non-empty weeks list")

    # Root page renders the newest/listed-first week but links to week subpages.
    write_shell(ROOT / "index.html", title="Ruths Weekly Meal Plans", base="")

    for week in weeks:
        slug = week["slug"]
        label = week.get("label", slug)
        write_shell(
            ROOT / "weeks" / slug / "index.html",
            title=f"{label} — Ruths Weekly Meal Plans",
            base="../../",
        )
        print(f"generated weeks/{slug}/index.html")


if __name__ == "__main__":
    main()
