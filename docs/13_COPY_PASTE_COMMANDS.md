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
