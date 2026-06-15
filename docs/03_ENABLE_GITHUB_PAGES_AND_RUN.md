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
