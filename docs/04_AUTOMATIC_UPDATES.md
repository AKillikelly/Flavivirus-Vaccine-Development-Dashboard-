# 04 — Automatic updates

## Where the automation lives

The automation file is:

```text
.github/workflows/pages.yml
```

## When it runs

The workflow runs in three situations:

1. When you push changes to the `main` branch.
2. When you manually click **Run workflow** in the Actions tab.
3. Every Monday at 06:17 in the `America/Montreal` time zone.

The schedule is defined here:

```yaml
schedule:
  - cron: "17 6 * * 1"
    timezone: "America/Montreal"
```

## What the workflow does

```text
Check out repository
  ↓
Set up Python 3.12
  ↓
Install requirements
  ↓
Run scripts/fetch_pipeline.py
  ↓
Run scripts/build_dashboard.py
  ↓
Upload public/ as the GitHub Pages artifact
  ↓
Deploy to GitHub Pages
```

## Optional: commit generated data back to the repository

By default, GitHub Pages receives the generated output, but scheduled generated files are not necessarily committed back to your repository history.

To make the workflow commit generated snapshots, create this repository variable:

```text
Settings → Secrets and variables → Actions → Variables → New repository variable
Name:  COMMIT_GENERATED_DATA
Value: true
```

When this variable is set to `true`, the workflow commits updated versions of:

```text
data/pipeline.csv
data/raw/
reports/automation_summary.md
public/flavivirus_vaccine_development_pipeline_data.csv
public/automation_summary.md
public/index.html
```

## When not to enable COMMIT_GENERATED_DATA

Leave it off if you want a cleaner repository and only care about the published dashboard.

Enable it if you want a visible data/audit history in GitHub commits.
