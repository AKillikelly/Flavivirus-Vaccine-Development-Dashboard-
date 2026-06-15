# 08 — Optional local build

You do not need to build locally to publish the dashboard. GitHub Actions can do everything in the cloud.

Local testing is useful when you want to edit scripts, data, or dashboard design before pushing changes.

## Requirements

- Python 3.12 or newer is recommended.
- No third-party Python packages are required by this project.

## Smoke test without network

From the project folder, run:

```bash
python scripts/fetch_pipeline.py --no-network
python scripts/build_dashboard.py
```

Expected result:

```text
Wrote data/pipeline.csv with ... rows
Wrote reports/automation_summary.md
Wrote public/index.html with ... rows
```

## View the dashboard locally

Run:

```bash
python -m http.server 8000 --directory public
```

Open:

```text
http://localhost:8000
```

Stop the server with `Ctrl + C` in the terminal.

## Validate Python syntax

Run:

```bash
python -m py_compile scripts/fetch_pipeline.py scripts/build_dashboard.py
```

No output usually means the syntax check passed.
