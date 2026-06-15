# Flavivirus vaccine dashboard automation summary

Generated: `2026-06-15T14:00:44Z`
Output CSV: `data/pipeline.csv`
Network mode: `disabled / seed-only snapshot`

## Pipeline totals

- Rows written: **20**
- Target viruses represented: **13**
- ClinicalTrials.gov records returned before dedupe: **0**
- ClinicalTrials.gov records after NCT dedupe: **0**

## Rows by stage

- Stage 0 — No dedicated human-vaccine pathway / gap lane: **5**
- Stage 1 — Discovery / translational: **0**
- Stage 2 — Preclinical or manufacturing-enabling: **2**
- Stage 3 — Phase 1: **2**
- Stage 4 — Phase 2: **2**
- Stage 5 — Efficacy / Phase 3: **1**
- Stage 6 — Regulatory authorization / WHO prequalification: **0**
- Stage 7 — Programmatic use / stockpile / post-licensure: **8**

## Highest mapped stage by target

- **AHFV** (Alkhurma hemorrhagic fever virus): stage 0
- **DENV** (Dengue virus): stage 7
- **JEV** (Japanese encephalitis virus): stage 7
- **KFDV** (Kyasanur Forest disease virus): stage 7
- **MVEV** (Murray Valley encephalitis virus): stage 0
- **OHFV** (Omsk hemorrhagic fever virus): stage 0
- **POWV** (Powassan virus): stage 2
- **SLEV** (St. Louis encephalitis virus): stage 0
- **TBEV** (Tick-borne encephalitis virus): stage 7
- **USUV** (Usutu virus): stage 0
- **WNV** (West Nile virus): stage 3
- **YFV** (Yellow fever virus): stage 7
- **ZIKV** (Zika virus): stage 4

## ClinicalTrials.gov query audit

- No ClinicalTrials.gov query results recorded for this run.

## Watch-page audit

- No watch pages fetched for this run.

## Classification rules

- Clinical trial records are deduplicated by NCT ID.
- Target virus and candidate labels are assigned with deterministic alias and candidate-pattern rules in `scripts/fetch_pipeline.py`.
- ClinicalTrials.gov phase fields map to stages 3–5; curated official-source rows are required for stage 6 or 7 authorization/programme claims.
- Gap rows are generated only when no target-specific seed or clinical signal is available.
- News or arbitrary webpage text is not used to upstage candidates automatically.

## Warnings

- Network disabled; ClinicalTrials.gov refresh skipped and curated seed rows were used.
- Network disabled; configured watch-page audit skipped.
