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
