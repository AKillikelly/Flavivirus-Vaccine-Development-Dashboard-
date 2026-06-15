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
