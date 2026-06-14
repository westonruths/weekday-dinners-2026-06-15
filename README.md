# Ruths Weekly Meal Plans

Static GitHub Pages site for reusable weekly dinner planning.

Live page: https://westonruths.github.io/weekday-dinners-2026-06-15/

## What changed from the first one-off page

The site is now data-driven:

- `index.html` is the reusable app shell.
- `assets/styles.css` controls presentation.
- `assets/app.js` renders a selected weekly plan from JSON.
- `data/weeks/index.json` lists available weeks, newest first.
- `data/weeks/YYYY-MM-DD.json` stores one week of recipes.
- `templates/week-template.json` is the copy/paste starting point for future weeks.

## Add a new weekly meal plan

1. Copy the template:

   ```bash
   cp templates/week-template.json data/weeks/2026-06-22.json
   ```

2. Fill in the new week’s recipes in `data/weeks/2026-06-22.json`.

3. Add the week to the top of `data/weeks/index.json`:

   ```json
   {
     "slug": "2026-06-22",
     "label": "June 22–26, 2026",
     "path": "data/weeks/2026-06-22.json"
   }
   ```

4. Validate before publishing:

   ```bash
   python3 scripts/validate.py
   ```

5. Commit and push:

   ```bash
   git add -A
   git commit -m "feat: add June 22 meal plan"
   git push
   ```

## URL pattern

- Latest week: `https://westonruths.github.io/weekday-dinners-2026-06-15/`
- Specific week: `https://westonruths.github.io/weekday-dinners-2026-06-15/?week=2026-06-15`

## Data rules

Each weekly JSON file should include:

- `title`, `description`, use-up priorities, time target, and grocery notes.
- Exactly five weekday `days` for normal weekly dinner planning.
- For each day: `protein`, `carb`, `veg`, `time`, `ingredients`, `steps`, and `ariaServing`.
- Optional `notes`, `tags`, and recipe source links inside note/body text.
