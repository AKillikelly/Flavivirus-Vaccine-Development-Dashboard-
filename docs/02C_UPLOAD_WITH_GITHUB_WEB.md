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
