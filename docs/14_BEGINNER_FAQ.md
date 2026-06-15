# 14 — Beginner FAQ

## Do I upload the ZIP file to GitHub?

No. Unzip it first, then upload or publish the contents of the folder.

## Do I need to know Python?

No. GitHub Actions runs the Python scripts for you. You only need Python locally if you want to test edits on your computer.

## Why is the `.github` folder important?

It contains the workflow file. Without `.github/workflows/pages.yml`, GitHub will not know how to refresh and deploy the dashboard automatically.

## Can I rename the repository?

Yes. The dashboard should still work. Your Pages URL will use the repository name.

## Can I make the repository private?

Maybe. GitHub Pages support for private repositories depends on your account, organization, and plan. Public is simplest for beginners.

## Can I edit the dashboard text?

Yes. Most visible dashboard design and text are in `scripts/dashboard_template.html`. Data row wording is mostly in `scripts/fetch_pipeline.py` and `data/pipeline.csv`.

## What happens if an external data source is temporarily down?

The workflow report will record warnings. The script includes curated seed rows so the dashboard can still produce a conservative snapshot.

## How often does the dashboard update?

Every Monday at 06:17 America/Montreal time, plus whenever you push to `main` or manually run the workflow.
