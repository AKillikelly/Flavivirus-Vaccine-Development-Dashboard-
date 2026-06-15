# 05 — Troubleshooting

## Problem: I do not see the workflow in the Actions tab

Most likely cause: `.github/workflows/pages.yml` was not uploaded.

Fix:

1. Go to your repository file list.
2. Look for `.github`.
3. Open `.github/workflows/pages.yml`.
4. If it is missing, upload the `.github` folder from this package.

## Problem: GitHub Pages shows a 404 page

Possible causes:

- The workflow has not run yet.
- The workflow failed.
- Pages source is not set to GitHub Actions.
- Deployment is still processing.

Fix:

1. Go to **Actions**.
2. Open the latest workflow run.
3. Confirm both `build` and `deploy` are green.
4. Go to **Settings → Pages**.
5. Confirm **Source** is **GitHub Actions**.
6. Open the Pages URL shown after deployment.

## Problem: The build job fails during Python setup

Check that `.github/workflows/pages.yml` still contains:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.12"
```

Also check that `requirements.txt` exists at the repository root.

## Problem: The build job fails during data refresh

Open the failed step named **Fetch and classify pipeline data**.

Possible causes:

- a temporary external source/network issue;
- a changed ClinicalTrials.gov response;
- a malformed edit in `scripts/fetch_pipeline.py`.

Fix:

1. Re-run the workflow once.
2. If it fails again, compare your latest changes to `scripts/fetch_pipeline.py`.
3. Use the local smoke test from `docs/08_LOCAL_BUILD_OPTIONAL.md`.

## Problem: Optional generated-data commit fails

If you enabled `COMMIT_GENERATED_DATA=true`, the workflow needs permission to push commits.

Fix:

1. Go to **Settings → Actions → General**.
2. Check workflow permissions.
3. Use read/write permissions when you want Actions to commit generated files.
4. Re-run the workflow.

## Problem: I accidentally deleted a required file

Required files/folders:

```text
.github/workflows/pages.yml
scripts/fetch_pipeline.py
scripts/build_dashboard.py
scripts/dashboard_template.html
requirements.txt
data/pipeline.csv
public/index.html
```

Restore the missing file from this ZIP package and commit it again.
