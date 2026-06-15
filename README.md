# Flavivirus vaccine development dashboard

This is a beginner-ready GitHub Pages project for an automatically updating flavivirus vaccine-development dashboard.

The repository includes:

- a static dashboard (`public/index.html`);
- a generated vaccine pipeline CSV (`data/pipeline.csv`);
- Python scripts that refresh and rebuild the dashboard;
- a GitHub Actions workflow that publishes the dashboard automatically;
- beginner documentation in the `docs/` folder.

## What the dashboard tracks

The dashboard maps vaccine-development maturity for medically important flaviviruses, including dengue virus, yellow fever virus, Japanese encephalitis virus, tick-borne encephalitis virus, Zika virus, West Nile virus, Kyasanur Forest disease virus, Powassan virus, St. Louis encephalitis virus, Murray Valley encephalitis virus, Usutu virus, Omsk hemorrhagic fever virus, and Alkhurma hemorrhagic fever virus.

It is a vaccine-development landscape dashboard. It is **not** a clinical recommendation, travel-health rulebook, case map, procurement recommendation, or substitute for official regulator/public-health guidance.

## Beginner start

Open:

```text
START_HERE.md
```

Then follow the numbered documents in `docs/`.

## How the automated build works

```text
Public sources
  ↓
scripts/fetch_pipeline.py
  ↓
data/pipeline.csv and reports/automation_summary.md
  ↓
scripts/build_dashboard.py
  ↓
public/index.html
  ↓
GitHub Pages
```

The workflow is in:

```text
.github/workflows/pages.yml
```

## Deployment summary

1. Create a GitHub repository.
2. Upload or publish all files from this folder.
3. Set **Settings → Pages → Build and deployment → Source** to **GitHub Actions**.
4. Run the workflow manually once from the **Actions** tab.
5. Open the GitHub Pages URL after deployment succeeds.

## Optional local build

Local testing is optional. GitHub Actions can build the project in the cloud.

```bash
python scripts/fetch_pipeline.py --no-network
python scripts/build_dashboard.py
python -m http.server 8000 --directory public
```

Then open:

```text
http://localhost:8000
```

## Repository structure

```text
.github/workflows/pages.yml          Automatic GitHub Actions workflow
scripts/fetch_pipeline.py            Data collector and classifier
scripts/build_dashboard.py           Static dashboard builder
scripts/dashboard_template.html      Dashboard HTML/CSS/JavaScript template
data/pipeline.csv                    Generated dashboard data
reports/automation_summary.md        Generated data-refresh report
public/index.html                    Published dashboard page
public/flavivirus_vaccine_development_pipeline_data.csv
public/automation_summary.md
docs/                                Beginner instructions
```

## Data-quality principle

Use official or high-confidence public sources when adding stage 6 or stage 7 claims. Stage 6 means authorization or WHO prequalification. Stage 7 means programmatic use, stockpile, or post-licensure deployment. When evidence is uncertain, keep the row at the lower stage and document the uncertainty in `notes`.
