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
