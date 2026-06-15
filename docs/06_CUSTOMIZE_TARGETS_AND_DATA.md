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
