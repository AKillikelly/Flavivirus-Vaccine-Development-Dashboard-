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
