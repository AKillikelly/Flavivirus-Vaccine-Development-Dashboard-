# All-in-one beginner guide

This combines the beginner setup and maintenance documents into one file. The separate numbered documents remain in `docs/`.


---


# Start here: flavivirus dashboard GitHub beginner kit

This folder is a complete GitHub repository for an automatically updating flavivirus vaccine-development dashboard.

You do **not** need to write code to publish it. The Python scripts, starter data, static dashboard, and GitHub Actions workflow are already included.

## What you will build

A GitHub Pages website that:

- displays an interactive flavivirus vaccine-development dashboard;
- refreshes public-source data automatically;
- can be refreshed manually from GitHub's **Actions** tab;
- publishes a downloadable CSV and automation report;
- can be maintained with either GitHub Desktop or terminal commands.

## Fastest path

1. Unzip this folder on your computer.
2. Create a new GitHub repository.
3. Upload or publish **the contents** of this folder to that repository. Do not upload only the ZIP file.
4. In GitHub, go to **Settings → Pages**.
5. Under **Build and deployment → Source**, choose **GitHub Actions**.
6. Go to **Actions**.
7. Open **Automated refresh and deploy flavivirus dashboard**.
8. Click **Run workflow**.
9. When the workflow succeeds, open the deployment URL shown by GitHub Pages.

## Read these files in order

1. `docs/00_QUICK_CHECKLIST.md`
2. `docs/01_BEGINNER_OVERVIEW.md`
3. `docs/02_UPLOAD_WITH_GITHUB_DESKTOP.md`
4. `docs/03_ENABLE_GITHUB_PAGES_AND_RUN.md`
5. `docs/04_AUTOMATIC_UPDATES.md`
6. `docs/05_TROUBLESHOOTING.md`

Use `docs/02B_UPLOAD_WITH_TERMINAL.md` only if you prefer command-line Git.

## Important files not to delete

```text
.github/workflows/pages.yml          automatic GitHub build/deploy workflow
scripts/fetch_pipeline.py            public-source data refresh script
scripts/build_dashboard.py           dashboard builder
scripts/dashboard_template.html      dashboard page template
data/pipeline.csv                    generated data table
public/index.html                    dashboard page published by GitHub Pages
requirements.txt                     Python dependency file
```

## Important publication note

Do not add private data, passwords, API keys, unpublished results, or confidential documents to this repository. GitHub Pages sites are public when published, and public repositories are visible to everyone.


---


# 00 — Quick checklist

Use this checklist as you deploy the dashboard.

## Before GitHub

- [ ] Unzipped the project folder.
- [ ] Confirmed the folder contains `START_HERE.md`.
- [ ] Confirmed the folder contains `.github/workflows/pages.yml`.
- [ ] Confirmed the folder contains `scripts/`, `data/`, `public/`, and `docs/`.

## Upload

- [ ] Created a new GitHub repository.
- [ ] Uploaded or published the contents of the project folder.
- [ ] Confirmed `.github/workflows/pages.yml` exists in GitHub.
- [ ] Confirmed the default branch is `main`.

## Pages setup

- [ ] Opened **Settings → Pages**.
- [ ] Set **Build and deployment → Source** to **GitHub Actions**.

## First build

- [ ] Opened the **Actions** tab.
- [ ] Selected **Automated refresh and deploy flavivirus dashboard**.
- [ ] Clicked **Run workflow**.
- [ ] Confirmed the `build` job passed.
- [ ] Confirmed the `deploy` job passed.

## Final check

- [ ] Opened the GitHub Pages URL.
- [ ] Confirmed the dashboard loads.
- [ ] Confirmed filters and table work.
- [ ] Confirmed CSV download works.
- [ ] Confirmed automation report download works.


---


# 01 — Beginner overview

## What is GitHub?

GitHub is where the project files live. Your dashboard will be stored in a GitHub repository, which is a project folder that GitHub can track and publish.

## What is GitHub Pages?

GitHub Pages is GitHub's static website hosting feature. In this project, GitHub Pages publishes the files inside the `public/` folder after the automated workflow finishes.

## What is GitHub Actions?

GitHub Actions is the automation system. This project uses it to run Python, refresh the data, rebuild the dashboard, and deploy the result to GitHub Pages.

## What is already done for you?

The project already includes:

- dashboard HTML template;
- generated starter data;
- Python data-refresh script;
- Python dashboard-build script;
- GitHub Actions workflow;
- beginner documentation;
- troubleshooting checklist.

## Recommended beginner method

Use GitHub Desktop:

- It avoids most command-line setup problems.
- It handles hidden folders like `.github` more reliably than manual web uploads.
- It lets you publish updates later with simple buttons.

## Method choices

| Method | Best for | Read |
|---|---|---|
| GitHub Desktop | Beginners | `docs/02_UPLOAD_WITH_GITHUB_DESKTOP.md` |
| Terminal / Git command line | Users already comfortable with commands | `docs/02B_UPLOAD_WITH_TERMINAL.md` |
| GitHub web upload | Small quick tests; less ideal for hidden folders | `docs/02C_UPLOAD_WITH_GITHUB_WEB.md` |

After uploading, everyone should read:

```text
docs/03_ENABLE_GITHUB_PAGES_AND_RUN.md
```


---


# 02 — Upload with GitHub Desktop

This is the easiest path for a beginner.

## Before you start

Install GitHub Desktop and sign in with your GitHub account.

## Step 1: Unzip the project

Unzip the project folder. Inside it you should see files and folders such as:

```text
.github
scripts
public
data
reports
docs
README.md
START_HERE.md
requirements.txt
```

The `.github` folder may be hidden by your computer. That is normal. Do not delete it.

## Step 2: Add the folder in GitHub Desktop

1. Open GitHub Desktop.
2. Choose **File → Add Local Repository**.
3. Select the unzipped project folder.
4. If GitHub Desktop says it is not a repository yet, choose the option to create one from the folder.
5. Name the repository, for example:

```text
flavivirus-vaccine-dashboard
```

## Step 3: Make the first commit

1. Review the changed files.
2. In the summary box, type:

```text
Initial flavivirus dashboard
```

3. Click **Commit to main**.

## Step 4: Publish to GitHub

1. Click **Publish repository**.
2. Choose public unless you know your plan supports Pages for private repositories.
3. Click **Publish repository**.

## Step 5: Continue to Pages setup

Read:

```text
docs/03_ENABLE_GITHUB_PAGES_AND_RUN.md
```


---


# 02B — Upload with terminal commands

Use this route only if you are comfortable with the command line.

## Step 1: Create an empty GitHub repository

Create a repository on GitHub. Do not initialize it with a README, license, or `.gitignore` because this folder already includes the files it needs.

## Step 2: Open a terminal in the unzipped folder

Use `cd` to enter the project folder.

Example:

```bash
cd path/to/flavivirus-dashboard-github-beginner-complete-kit
```

## Step 3: Initialize Git and push

Replace `YOUR-USERNAME` and `YOUR-REPO-NAME` with your actual GitHub username and repository name.

```bash
git init
git add .
git commit -m "Initial flavivirus dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main
```

## Step 4: Check that the workflow file is present

In GitHub, confirm this file exists:

```text
.github/workflows/pages.yml
```

## Step 5: Continue to Pages setup

Read:

```text
docs/03_ENABLE_GITHUB_PAGES_AND_RUN.md
```

## Common terminal issue: authentication

GitHub does not accept account passwords for Git over HTTPS. Use GitHub Desktop, GitHub CLI, or a personal access token if Git asks for credentials.


---


# 02C — Upload with the GitHub website

This method can work, but GitHub Desktop is usually easier because this project contains a hidden `.github` folder.

## Step 1: Create a new repository

1. Go to GitHub.
2. Click **New repository**.
3. Name it, for example:

```text
flavivirus-vaccine-dashboard
```

4. Choose **Public** unless you know your plan supports Pages for private repositories.
5. Do not add a README, `.gitignore`, or license from GitHub because this project already includes the files it needs.
6. Click **Create repository**.

## Step 2: Upload the files

1. Unzip this project on your computer.
2. Open the unzipped folder.
3. Upload the **contents** of the folder to GitHub.
4. Make sure these folders appear in the repository after upload:

```text
.github/workflows/pages.yml
scripts/
public/
data/
reports/
docs/
```

## Step 3: Check the hidden workflow folder

The most important check is this file:

```text
.github/workflows/pages.yml
```

If that file is missing, the automatic update workflow will not appear in the Actions tab.

On macOS, press `Command + Shift + .` in Finder to show hidden folders. On Windows, turn on **View → Show → Hidden items** in File Explorer.

## Step 4: Commit the upload

GitHub will ask for a commit message. Use:

```text
Initial flavivirus dashboard
```

Then click **Commit changes**.

## Step 5: Continue to Pages setup

Read:

```text
docs/03_ENABLE_GITHUB_PAGES_AND_RUN.md
```


---


# 03 — Enable GitHub Pages and run the dashboard

After the files are in GitHub, tell GitHub Pages to deploy from GitHub Actions.

## Step 1: Open repository settings

1. Go to your repository on GitHub.
2. Click **Settings**.
3. In the left sidebar, click **Pages**.

## Step 2: Select GitHub Actions as the publishing source

Under **Build and deployment**:

1. Find **Source**.
2. Choose **GitHub Actions**.

Do not choose **Deploy from a branch** for this project. The included workflow builds the dashboard and publishes the `public/` folder.

## Step 3: Run the workflow manually once

1. Click the **Actions** tab in your repository.
2. In the left sidebar, click **Automated refresh and deploy flavivirus dashboard**.
3. Click **Run workflow**.
4. Keep the branch as `main`.
5. Click the green **Run workflow** button.

## Step 4: Watch the workflow

The workflow has two jobs:

1. `build` — refreshes data and builds `public/index.html`.
2. `deploy` — publishes the built dashboard to GitHub Pages.

When both jobs have green check marks, the dashboard is deployed.

## Step 5: Open the dashboard URL

After deployment, GitHub will show a Pages URL. It usually looks like:

```text
https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/
```

## Step 6: Confirm the dashboard works

Check that:

- the page loads;
- filters work;
- the candidate table appears;
- download links work;
- `public/flavivirus_vaccine_development_pipeline_data.csv` is available;
- `public/automation_summary.md` is available.


---


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


---


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


---


# 06 — Customize targets and data

Most beginners do not need to edit the scripts. The dashboard works as packaged.

Use this file when you want to add a flavivirus target, change wording, or add a curated candidate row.

## Main file to edit

```text
scripts/fetch_pipeline.py
```

## Important sections

### `TARGETS`

Defines each target virus and default text.

### `TARGET_ALIASES`

Helps the script classify ClinicalTrials.gov records.

### `CLINICALTRIALS_QUERIES`

Search terms sent to ClinicalTrials.gov.

### `WATCH_PAGES`

Official or high-confidence pages saved for audit. Watch pages are not automatically interpreted into higher stages.

### `make_seed_rows()`

Curated source-backed rows for stable facts such as licensed products, WHO prequalification, regulatory authorization, programmatic use, explicit no-vaccine gaps, or preclinical candidates.

## Conservative staging rule

Do not label a row as stage 6 or 7 unless an official or high-confidence source supports it.

| Stage | Use when |
|---:|---|
| 0 | No dedicated human-vaccine pathway identified |
| 1 | Discovery / translational signal |
| 2 | Preclinical or manufacturing-enabling candidate |
| 3 | Phase 1 human trial |
| 4 | Phase 2 human trial |
| 5 | Efficacy / Phase 3 |
| 6 | Regulatory authorization or WHO prequalification |
| 7 | Programmatic use, stockpile, or post-licensure deployment |

## Data quality checklist before committing a curated row

- target virus is correct;
- candidate name is specific;
- stage is conservative;
- regulatory wording is precise;
- source URL is public and stable;
- evidence summary does not overclaim;
- notes explain uncertainty;
- no private or unpublished information is included.


---


# 07 — File map

## Root files

| File | Purpose |
|---|---|
| `START_HERE.md` | First file a beginner should open |
| `BEGINNER_START_HERE.txt` | Plain-text quick start |
| `README.md` | Main repository description shown by GitHub |
| `PACKAGE_MANIFEST.md` | File inventory |
| `requirements.txt` | Python dependency file; currently no third-party packages required |
| `.gitignore` | Prevents local clutter from being committed |

## Automation

| File | Purpose |
|---|---|
| `.github/workflows/pages.yml` | GitHub Actions workflow that refreshes, builds, and deploys the dashboard |

## Scripts

| File | Purpose |
|---|---|
| `scripts/fetch_pipeline.py` | Collects public data signals, classifies records, writes `data/pipeline.csv`, and writes the automation report |
| `scripts/build_dashboard.py` | Converts `data/pipeline.csv` into `public/index.html` |
| `scripts/dashboard_template.html` | HTML, CSS, and JavaScript template for the dashboard |

## Data and reports

| File/folder | Purpose |
|---|---|
| `data/pipeline.csv` | Main generated data table |
| `data/raw/` | Optional raw source/audit files from automated fetches |
| `reports/automation_summary.md` | Data-refresh report generated by the fetch script |

## Published website files

| File | Purpose |
|---|---|
| `public/index.html` | Main dashboard page published by GitHub Pages |
| `public/flavivirus_vaccine_development_pipeline_data.csv` | Downloadable CSV used by the dashboard |
| `public/automation_summary.md` | Downloadable automation report |
| `public/.nojekyll` | Tells GitHub Pages not to process the site with Jekyll |


---


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


---


# 09 — Maintenance checklist

## Each month

- Open the live dashboard.
- Confirm the latest workflow run succeeded.
- Download the CSV from the dashboard and spot-check a few rows.
- Open `public/automation_summary.md` and check for warnings.
- Review high-stage rows for source drift or broken links.

## Each quarter

- Review all stage 6 and stage 7 rows.
- Confirm regulator/WHO/public-health source links still support the wording.
- Search for major vaccine-development updates that should be added as curated seed rows.
- Check whether any target virus should be added or retired.
- Check whether ClinicalTrials.gov aliases should be expanded.

## Before sharing externally

- Make sure the dashboard date is recent.
- Make sure the limitations statement is visible.
- Make sure no private or unpublished data has been added.
- Confirm the CSV and automation report downloads work.

## Keep this principle

The dashboard should be conservative. A lower stage with clear evidence is better than a higher stage with weak evidence.


---


# 10 — Glossary

## Repository

A project folder stored on GitHub.

## Commit

A saved change in Git. Think of it as a snapshot of the project at one point in time.

## Branch

A version line in Git. This project uses the `main` branch.

## GitHub Pages

GitHub's static website hosting feature.

## GitHub Actions

GitHub's automation feature. It runs the workflow file in `.github/workflows/pages.yml`.

## Workflow

A YAML file that tells GitHub Actions what to do.

## Artifact

A packaged set of files created by a workflow. This project uploads the `public/` folder as the Pages artifact.

## Static site

A website made of files such as HTML, CSS, JavaScript, CSV, and images. It does not require a live database or backend server.

## CSV

Comma-separated values. A spreadsheet-like data file.

## ClinicalTrials.gov

A public registry of clinical studies. This project uses it as one automated source for clinical-stage vaccine-development records.

## Curated seed row

A row added directly in the script because it represents a stable, source-backed signal such as authorization, WHO prequalification, programmatic use, or an explicit no-vaccine gap.

## Stage

The dashboard's simplified vaccine-development maturity level from 0 to 7.


---


# 11 — Data limits and review rules

## Purpose

This dashboard is designed as a vaccine-development landscape view. It is not a clinical, regulatory, travel, procurement, or investment recommendation.

## What automation can do well

Automation can:

- search structured clinical-trial records;
- deduplicate trial IDs;
- classify target viruses using defined aliases;
- map clinical phases into simplified stages;
- rebuild the dashboard consistently;
- produce an audit report.

## What automation should not do alone

Automation should not automatically infer:

- regulatory authorization from news headlines;
- programmatic use from vague public statements;
- vaccine availability from product mentions without an official source;
- safety or efficacy conclusions beyond source wording;
- national policy recommendations without checking current official guidance.

## Conservative review rule

When a row is uncertain, keep it at the lower stage and document the uncertainty in `notes`.

## Recommended source hierarchy

For high-stage claims, prefer:

1. regulator product pages or package inserts;
2. WHO prequalification or WHO policy documents;
3. national immunization/public-health guidance;
4. clinical-trial registry records;
5. peer-reviewed literature;
6. sponsor announcements, clearly labeled as sponsor announcements.


---


# 12 — Official GitHub references

Use these official GitHub documentation pages when GitHub's interface changes or you need more detail.

## GitHub Pages publishing source

https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

Useful for selecting **GitHub Actions** as the publishing source.

## Custom workflows with GitHub Pages

https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

Useful for understanding `actions/configure-pages`, `actions/upload-pages-artifact`, and `actions/deploy-pages`.

## Events that trigger workflows

https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

Useful for scheduled workflow syntax, manual runs, default-branch behavior, and schedule timing.

## Manually running a workflow

https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow

Useful for using the **Run workflow** button.

## Building and testing Python with GitHub Actions

https://docs.github.com/en/actions/tutorials/build-and-test-code/python

Useful for understanding `actions/setup-python`.


---


# 13 — Copy/paste command sheet

## Create and push a new repository

Replace `YOUR-USERNAME` and `YOUR-REPO-NAME` first.

```bash
git init
git add .
git commit -m "Initial flavivirus dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main
```

## Local syntax check

```bash
python -m py_compile scripts/fetch_pipeline.py scripts/build_dashboard.py
```

## Local offline build

```bash
python scripts/fetch_pipeline.py --no-network
python scripts/build_dashboard.py
```

## Local online build

```bash
python scripts/fetch_pipeline.py
python scripts/build_dashboard.py
```

## Local web preview

```bash
python -m http.server 8000 --directory public
```

Open:

```text
http://localhost:8000
```


---


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
