#!/usr/bin/env python3
"""Fetch and classify flavivirus vaccine-development signals.

The script is intentionally conservative:
- structured ClinicalTrials.gov records can add or update clinical-stage rows;
- curated seed rows preserve stable regulatory/programmatic signals from official sources;
- configured watch pages are captured for audit, but arbitrary webpages do not upstage a row.

It has no third-party dependency and will still build a source-backed snapshot when external
network access is unavailable.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

STAGE_LABELS: Dict[int, str] = {
    0: "No dedicated human-vaccine pathway / gap lane",
    1: "Discovery / translational",
    2: "Preclinical or manufacturing-enabling",
    3: "Phase 1",
    4: "Phase 2",
    5: "Efficacy / Phase 3",
    6: "Regulatory authorization / WHO prequalification",
    7: "Programmatic use / stockpile / post-licensure",
}

FIELDNAMES = [
    "id",
    "target_virus",
    "target_abbrev",
    "virus_group",
    "vector_or_route",
    "candidate",
    "platform",
    "developer_sponsor",
    "stage_order",
    "stage",
    "status_type",
    "active_status",
    "regulatory_status",
    "target_use",
    "evidence_summary",
    "next_milestone",
    "development_geography",
    "source_1",
    "source_url_1",
    "source_2",
    "source_url_2",
    "source_3",
    "source_url_3",
    "notes",
    "automation_method",
    "last_checked_utc",
    "supporting_record_count",
]

TARGETS: Dict[str, Dict[str, str]] = {
    "DENV": {
        "name": "Dengue virus",
        "group": "Mosquito-borne flavivirus",
        "vector_or_route": "Aedes mosquitoes",
        "default_use": "Endemic pediatric/adolescent programmes, outbreak-prone settings, and travellers where authorized",
    },
    "YFV": {
        "name": "Yellow fever virus",
        "group": "Mosquito-borne flavivirus",
        "vector_or_route": "Aedes/Hemagogus mosquitoes",
        "default_use": "Routine immunization, outbreak response, travel, laboratory-risk protection, and emergency stockpile",
    },
    "JEV": {
        "name": "Japanese encephalitis virus",
        "group": "Mosquito-borne flavivirus",
        "vector_or_route": "Culex mosquitoes; enzootic pig/bird cycle",
        "default_use": "Routine immunization in endemic countries and vaccination of travellers/laboratory workers at risk",
    },
    "WNV": {
        "name": "West Nile virus",
        "group": "Mosquito-borne flavivirus",
        "vector_or_route": "Culex mosquitoes; bird reservoir",
        "default_use": "No licensed human vaccine; candidate development for older adults and other severe-disease risk groups",
    },
    "ZIKV": {
        "name": "Zika virus",
        "group": "Mosquito-borne / congenital-risk flavivirus",
        "vector_or_route": "Aedes mosquitoes; sexual and congenital transmission also relevant",
        "default_use": "No licensed vaccine; development focused on reproductive-age populations and outbreak-prone areas",
    },
    "SLEV": {
        "name": "St. Louis encephalitis virus",
        "group": "Mosquito-borne flavivirus",
        "vector_or_route": "Culex mosquitoes; bird reservoir",
        "default_use": "No dedicated human vaccine pathway identified; mosquito-bite prevention remains primary",
    },
    "MVEV": {
        "name": "Murray Valley encephalitis virus",
        "group": "Mosquito-borne flavivirus",
        "vector_or_route": "Culex mosquitoes; enzootic waterbird cycle",
        "default_use": "No licensed human vaccine; prevention relies on mosquito avoidance and surveillance",
    },
    "USUV": {
        "name": "Usutu virus",
        "group": "Mosquito-borne flavivirus",
        "vector_or_route": "Culex mosquitoes; bird reservoir",
        "default_use": "No licensed human vaccine; prevention relies on mosquito avoidance and surveillance",
    },
    "TBEV": {
        "name": "Tick-borne encephalitis virus",
        "group": "Tick-borne flavivirus",
        "vector_or_route": "Ixodes ticks; occasional unpasteurized dairy exposure",
        "default_use": "Routine/risk-based use in endemic countries, travellers, and laboratory-risk groups",
    },
    "KFDV": {
        "name": "Kyasanur Forest disease virus",
        "group": "Tick-borne hemorrhagic flavivirus",
        "vector_or_route": "Haemaphysalis ticks; forest exposure in India",
        "default_use": "Regional risk-based programmes in India; improved vaccine candidates under development",
    },
    "POWV": {
        "name": "Powassan virus",
        "group": "Tick-borne flavivirus",
        "vector_or_route": "Ixodes ticks",
        "default_use": "No licensed human vaccine; preclinical work is exploratory",
    },
    "OHFV": {
        "name": "Omsk hemorrhagic fever virus",
        "group": "Tick-borne hemorrhagic flavivirus",
        "vector_or_route": "Ticks and contact with infected muskrats/other animals",
        "default_use": "No dedicated human vaccine pathway identified; TBE vaccines may be considered for some high-risk groups where appropriate",
    },
    "AHFV": {
        "name": "Alkhurma hemorrhagic fever virus",
        "group": "Tick-borne hemorrhagic flavivirus",
        "vector_or_route": "Ticks and contact with infected animals/animal products",
        "default_use": "No dedicated human vaccine pathway identified",
    },
}

# Order matters. More specific aliases are checked before generic words.
TARGET_ALIASES: Sequence[Tuple[str, Sequence[str]]] = [
    ("AHFV", ["alkhurma", "al khurma", "alkurma", "ahfv"]),
    ("OHFV", ["omsk hemorrhagic", "omsk haemorrhagic", "ohfv"]),
    ("KFDV", ["kyasanur", "kfdv", "kfd vaccine", "kyasanur forest", "monkey fever"]),
    ("POWV", ["powassan", "powv"]),
    ("MVEV", ["murray valley", "mvev"]),
    ("SLEV", ["st. louis encephalitis", "st louis encephalitis", "saint louis encephalitis", "slev"]),
    ("USUV", ["usutu", "usuv"]),
    ("TBEV", ["tick-borne encephalitis", "tick borne encephalitis", "tbe vaccine", "tbe-vaccine", "ticovac", "fsme", "fsmE", "encepur"]),
    ("WNV", ["west nile", "wnv", "hydrovax"]),
    ("ZIKV", ["zika", "zikv", "vrc5283", "vrc 5283", "vrc705", "vrc 705", "mrna-1893", "zpiv"]),
    ("JEV", ["japanese encephalitis", "ixiaro", "ic51", "sa14", "jev vaccine"]),
    ("YFV", ["yellow fever", "yf-vax", "yfvax", "stamaril", "17d vaccine", "yfv vaccine"]),
    ("DENV", ["dengue", "denv", "dengvaxia", "cyd-tdv", "cyd tdv", "tak-003", "tak003", "qdenga", "tv003", "tv005", "butantan-dv"]),
]

CLINICALTRIALS_QUERIES = [
    "Dengue vaccine",
    "Dengvaxia OR CYD-TDV",
    "Qdenga OR TAK-003",
    "TV003 OR TV005 OR Butantan-DV dengue vaccine",
    "Yellow fever vaccine OR YF-VAX OR Stamaril OR 17D",
    "Japanese encephalitis vaccine OR IXIARO OR IC51 OR SA14-14-2",
    "Tick-borne encephalitis vaccine OR TICOVAC OR FSME OR Encepur",
    "Zika vaccine OR VRC5283 OR mRNA-1893 OR ZPIV",
    "West Nile virus vaccine OR HydroVax-001B",
    "Powassan vaccine",
    "Kyasanur Forest disease vaccine OR KFD vaccine",
    "Omsk hemorrhagic fever vaccine",
    "St. Louis encephalitis vaccine",
    "Murray Valley encephalitis vaccine",
    "Usutu vaccine",
    "Alkhurma hemorrhagic fever vaccine",
]

WATCH_PAGES: Sequence[Tuple[str, str]] = [
    ("ClinicalTrials.gov Data API", "https://clinicaltrials.gov/data-api/api"),
    ("WHO dengue vaccine prequalification notice", "https://www.who.int/news/item/15-05-2024-who-prequalifies-new-dengue-vaccine"),
    ("WHO yellow fever fact sheet", "https://www.who.int/news-room/fact-sheets/detail/yellow-fever"),
    ("FDA YF-VAX product page", "https://www.fda.gov/vaccines-blood-biologics/vaccines/yf-vax"),
    ("FDA IXIARO product page", "https://www.fda.gov/vaccines-blood-biologics/vaccines/ixiaro"),
    ("CDC West Nile treatment/prevention", "https://www.cdc.gov/west-nile-virus/hcp/treatment-prevention/index.html"),
    ("WHO Zika fact sheet", "https://www.who.int/news-room/fact-sheets/detail/zika-virus"),
]

SOURCELESS = ("", "")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def clean(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def slugify(value: str, max_len: int = 96) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value[:max_len].strip("-") or "row"


def stable_id(target: str, candidate: str) -> str:
    base = slugify(f"{target}-{candidate}", 80)
    digest = hashlib.sha1(f"{target}|{candidate}".encode("utf-8")).hexdigest()[:8]
    return f"{base}-{digest}"


def source_pairs(row: Dict[str, Any]) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for i in range(1, 4):
        label = clean(row.get(f"source_{i}", ""))
        url = clean(row.get(f"source_url_{i}", ""))
        if label or url:
            out.append((label, url))
    return out


def assign_sources(row: Dict[str, Any], pairs: Iterable[Tuple[str, str]]) -> None:
    unique: List[Tuple[str, str]] = []
    seen = set()
    for label, url in pairs:
        label = clean(label)
        url = clean(url)
        key = (label.lower(), url.lower())
        if (label or url) and key not in seen:
            seen.add(key)
            unique.append((label, url))
    for idx in range(1, 4):
        label, url = unique[idx - 1] if idx <= len(unique) else SOURCELESS
        row[f"source_{idx}"] = label
        row[f"source_url_{idx}"] = url


def seed_row(
    *,
    target: str,
    candidate: str,
    platform: str,
    developer_sponsor: str,
    stage_order: int,
    status_type: str,
    active_status: str,
    regulatory_status: str,
    target_use: str,
    evidence_summary: str,
    next_milestone: str,
    development_geography: str,
    sources: Sequence[Tuple[str, str]],
    notes: str = "",
    supporting_record_count: int = 1,
    now: str,
) -> Dict[str, Any]:
    target_info = TARGETS[target]
    row: Dict[str, Any] = {
        "id": stable_id(target, candidate),
        "target_virus": target_info["name"],
        "target_abbrev": target,
        "virus_group": target_info["group"],
        "vector_or_route": target_info["vector_or_route"],
        "candidate": candidate,
        "platform": platform,
        "developer_sponsor": developer_sponsor,
        "stage_order": stage_order,
        "stage": STAGE_LABELS[stage_order],
        "status_type": status_type,
        "active_status": active_status,
        "regulatory_status": regulatory_status,
        "target_use": target_use or target_info["default_use"],
        "evidence_summary": evidence_summary,
        "next_milestone": next_milestone,
        "development_geography": development_geography,
        "notes": notes,
        "automation_method": "Curated official-source seed row; refreshed alongside automated ClinicalTrials.gov scan",
        "last_checked_utc": now,
        "supporting_record_count": supporting_record_count,
    }
    assign_sources(row, sources)
    return row


def make_seed_rows(now: str) -> List[Dict[str, Any]]:
    return [
        seed_row(
            target="YFV",
            candidate="17D yellow fever vaccines (YF-VAX / Stamaril / WHO-PQ producers)",
            platform="Live attenuated 17D-lineage vaccines",
            developer_sponsor="Sanofi, Bio-Manguinhos/Fiocruz, Institut Pasteur de Dakar, and other WHO-prequalified/public-sector manufacturers",
            stage_order=7,
            status_type="Licensed / deployed",
            active_status="Programmatic and travel use",
            regulatory_status="Licensed in multiple jurisdictions; WHO-recommended prevention measure; emergency stockpile use",
            target_use="Routine immunization in endemic areas, outbreak response, travel requirements, laboratory-risk protection, and emergency stockpile",
            evidence_summary="Long-established 17D-lineage vaccines anchor global yellow fever prevention; a single dose is considered to provide long-term/lifelong protection in standard recommendations.",
            next_milestone="Maintain supply resilience, outbreak stockpile readiness, and risk-based vaccination coverage.",
            development_geography="Global; endemic areas in Africa and South America plus travel clinics",
            sources=[
                ("FDA YF-VAX product page", "https://www.fda.gov/vaccines-blood-biologics/vaccines/yf-vax"),
                ("WHO yellow fever fact sheet", "https://www.who.int/news-room/fact-sheets/detail/yellow-fever"),
                ("CDC Yellow Book yellow fever chapter", "https://www.cdc.gov/yellow-book/hcp/travel-associated-infections-diseases/yellow-fever.html"),
            ],
            notes="Dashboard stage reflects vaccine-development maturity, not current outbreak risk or country-entry requirements.",
            now=now,
        ),
        seed_row(
            target="DENV",
            candidate="Dengvaxia / CYD-TDV",
            platform="Live attenuated chimeric tetravalent dengue vaccine",
            developer_sponsor="Sanofi Pasteur",
            stage_order=7,
            status_type="Licensed / restricted programmatic use",
            active_status="Use limited to seropositive populations where recommended/authorized",
            regulatory_status="FDA-approved for laboratory-confirmed previous dengue infection in specified endemic-area pediatric/adolescent populations; other country policies vary",
            target_use="Seropositive people in defined age/geography groups; not a universal dengue vaccine lane",
            evidence_summary="Dengvaxia is a licensed tetravalent dengue vaccine but requires strict prior-infection targeting because of safety/benefit considerations.",
            next_milestone="Maintain serostatus-linked policy safeguards and monitor country-specific use recommendations.",
            development_geography="Selected endemic jurisdictions; U.S. endemic territories under ACIP/FDA constraints",
            sources=[
                ("FDA Dengvaxia package insert", "https://www.fda.gov/media/124379/download"),
                ("CDC dengue vaccine guidance", "https://www.cdc.gov/dengue/hcp/vaccine/index.html"),
                ("WHO prequalified vaccines list", "https://extranet.who.int/prequal/vaccines/prequalified-vaccines"),
            ],
            notes="Counted as post-licensure but flagged as restricted-use rather than broad deployment.",
            now=now,
        ),
        seed_row(
            target="DENV",
            candidate="Qdenga / TAK-003",
            platform="Live attenuated tetravalent dengue vaccine",
            developer_sponsor="Takeda",
            stage_order=7,
            status_type="Authorized / WHO-prequalified",
            active_status="Authorized in several jurisdictions; WHO prequalified",
            regulatory_status="WHO prequalified in 2024; EMA-authorized; national recommendations differ",
            target_use="Children/adolescents in high-transmission settings where recommended and travellers where authorized by national policy",
            evidence_summary="TAK-003/Qdenga became the second dengue vaccine prequalified by WHO, adding a major programmatic dengue-vaccine option.",
            next_milestone="Track national policy adoption, risk-group guidance, supply scale-up, and post-authorization safety/effectiveness data.",
            development_geography="WHO prequalification; EU and multiple endemic-country regulatory pathways",
            sources=[
                ("WHO prequalifies new dengue vaccine", "https://www.who.int/news/item/15-05-2024-who-prequalifies-new-dengue-vaccine"),
                ("EMA Qdenga EPAR", "https://www.ema.europa.eu/en/medicines/human/EPAR/qdenga"),
                ("WHO prequalified vaccines list", "https://extranet.who.int/prequal/vaccines/prequalified-vaccines"),
            ],
            notes="National recommendations can be more restrictive than the marketing authorization.",
            now=now,
        ),
        seed_row(
            target="DENV",
            candidate="TV003 / TV005 / Butantan-DV lineage",
            platform="Single-dose live attenuated tetravalent dengue vaccine candidate",
            developer_sponsor="U.S. NIH/NIAID lineage; Instituto Butantan and partners",
            stage_order=5,
            status_type="Efficacy-stage clinical development",
            active_status="Phase 3 / efficacy-stage evidence signal",
            regulatory_status="Investigational; no dashboard-seeded WHO/FDA/EMA authorization signal",
            target_use="Potential broad endemic-area dengue vaccination if efficacy, safety, and regulatory endpoints are met",
            evidence_summary="The TV003/TV005 lineage is represented as an efficacy-stage dengue vaccine candidate; automated ClinicalTrials.gov refresh can update linked trial status.",
            next_milestone="Regulatory review, implementation policy, and post-trial safety/effectiveness assessment if filings proceed.",
            development_geography="Brazil and other dengue-endemic research settings",
            sources=[
                ("ClinicalTrials.gov NCT02406729", "https://clinicaltrials.gov/study/NCT02406729"),
                ("NIAID dengue vaccine research", "https://www.niaid.nih.gov/diseases-conditions/dengue-vaccines"),
            ],
            notes="Seeded as Phase 3/efficacy-stage rather than authorized; confirm country-specific regulatory status before use.",
            now=now,
        ),
        seed_row(
            target="JEV",
            candidate="IXIARO / IC51",
            platform="Purified inactivated, Vero-cell-derived Japanese encephalitis vaccine",
            developer_sponsor="Valneva Austria GmbH",
            stage_order=7,
            status_type="Licensed / deployed",
            active_status="Travel and risk-based use",
            regulatory_status="FDA and EMA-authorized for prevention of disease caused by Japanese encephalitis virus in age-defined populations",
            target_use="Travellers to endemic areas, laboratory workers, and other risk groups according to national guidance",
            evidence_summary="IXIARO is an authorized inactivated Japanese encephalitis vaccine and is used for risk-based protection outside routine endemic-country programmes.",
            next_milestone="Continue risk-based travel/laboratory recommendations and supply monitoring.",
            development_geography="United States, European Union, travel-medicine markets, and other jurisdictions",
            sources=[
                ("FDA IXIARO product page", "https://www.fda.gov/vaccines-blood-biologics/vaccines/ixiaro"),
                ("CDC Japanese encephalitis vaccine guidance", "https://www.cdc.gov/japanese-encephalitis/hcp/vaccine/index.html"),
                ("EMA IXIARO product information", "https://www.ema.europa.eu/en/medicines/human/EPAR/ixiaro"),
            ],
            now=now,
        ),
        seed_row(
            target="JEV",
            candidate="Live attenuated SA14-14-2 Japanese encephalitis vaccines",
            platform="Live attenuated SA14-14-2",
            developer_sponsor="Chengdu Institute of Biological Products and other regional programme partners",
            stage_order=7,
            status_type="WHO-prequalified / programmatic use",
            active_status="Routine use in endemic-country immunization programmes",
            regulatory_status="WHO-prequalified product lineage and widely used endemic-country programme vaccine",
            target_use="Pediatric routine immunization and campaigns in endemic countries",
            evidence_summary="SA14-14-2 is a mature JE vaccine platform used programmatically in endemic settings, including WHO-prequalified supply pathways.",
            next_milestone="Maintain endemic-country coverage, supply quality, and surveillance for programme impact.",
            development_geography="Asia-Pacific endemic countries; global procurement channels where applicable",
            sources=[
                ("WHO Japanese encephalitis vaccine standardization", "https://www.who.int/teams/health-product-policy-and-standards/standards-and-specifications/vaccine-standardization/japanese-encephalitis"),
                ("WHO prequalified vaccines list", "https://extranet.who.int/prequal/vaccines/prequalified-vaccines"),
                ("PATH Japanese encephalitis vaccine overview", "https://www.path.org/our-impact/resources/japanese-encephalitis-vaccine/"),
            ],
            notes="Row groups multiple programme products/platform instances at the target-virus level.",
            now=now,
        ),
        seed_row(
            target="TBEV",
            candidate="TicoVac / FSME-IMMUN",
            platform="Inactivated whole-virus tick-borne encephalitis vaccine",
            developer_sponsor="Pfizer",
            stage_order=7,
            status_type="Licensed / deployed",
            active_status="Risk-based use in endemic-area travellers and other exposed groups",
            regulatory_status="FDA-approved for individuals aged 1 year and older; related FSME-IMMUN product lineage used in Europe",
            target_use="Travellers/residents with TBE exposure risk and laboratory-risk groups according to national guidance",
            evidence_summary="TicoVac is an authorized inactivated TBE vaccine and part of a broader mature TBE vaccine ecosystem.",
            next_milestone="Maintain risk-based recommendations and monitor traveler/endemic-country programme needs.",
            development_geography="United States, Europe, and other TBE-endemic regions",
            sources=[
                ("FDA TICOVAC package insert", "https://www.fda.gov/media/151502/download"),
                ("CDC TBE vaccine guidance", "https://www.cdc.gov/tick-borne-encephalitis/hcp/vaccine/index.html"),
                ("WHO TBE vaccine standardization", "https://www.who.int/teams/health-product-policy-and-standards/standards-and-specifications/vaccine-standardization/tick-borne-encephalitis"),
            ],
            now=now,
        ),
        seed_row(
            target="TBEV",
            candidate="Encepur and other established TBE vaccines",
            platform="Inactivated whole-virus tick-borne encephalitis vaccines",
            developer_sponsor="Bavarian Nordic / GSK legacy and regional manufacturers",
            stage_order=7,
            status_type="Licensed / deployed",
            active_status="Endemic-country and travel-risk use",
            regulatory_status="Authorized in multiple non-U.S. jurisdictions; WHO describes several widely used assured-quality TBE vaccines",
            target_use="Risk-based and routine use in TBE-endemic countries according to national recommendations",
            evidence_summary="Multiple TBE vaccines beyond TicoVac/FSME-IMMUN are mature products in endemic-region vaccination practice.",
            next_milestone="Track jurisdiction-specific product availability, recommendations, and effectiveness data.",
            development_geography="Europe and Eurasian endemic regions",
            sources=[
                ("WHO TBE vaccine standardization", "https://www.who.int/teams/health-product-policy-and-standards/standards-and-specifications/vaccine-standardization/tick-borne-encephalitis"),
                ("CDC TBE vaccine guidance", "https://www.cdc.gov/tick-borne-encephalitis/hcp/vaccine/index.html"),
            ],
            notes="Grouped row captures mature non-U.S. TBE products; product-level availability varies by country.",
            now=now,
        ),
        seed_row(
            target="KFDV",
            candidate="Local formalin-inactivated KFD vaccine",
            platform="Formalin-inactivated tissue-culture KFD vaccine",
            developer_sponsor="Indian state/public-health programme supply lineage",
            stage_order=7,
            status_type="Regional programme use",
            active_status="Available for people at risk in affected Indian regions, with effectiveness/supply caveats",
            regulatory_status="Regional/local risk-based vaccine availability; not a globally licensed product lane",
            target_use="People at occupational/geographic risk in Kyasanur Forest disease endemic districts",
            evidence_summary="KFD has had a regional inactivated vaccine option for at-risk populations, although improved vaccines are being developed because durability/effectiveness and programme logistics remain concerns.",
            next_milestone="Clarify current supply, coverage, effectiveness, and transition strategy to improved vaccine candidates.",
            development_geography="Western Ghats region, India",
            sources=[
                ("CDC Kyasanur Forest disease overview", "https://www.cdc.gov/kyasanur/about/index.html"),
                ("ICMR/PIB improved KFD vaccine notice", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2224977&lang=1&reg=3"),
            ],
            notes="Stage 7 reflects regional programme availability, not broad international licensure.",
            now=now,
        ),
        seed_row(
            target="KFDV",
            candidate="ICMR-NIV / Indian Immunologicals improved inactivated KFD candidate",
            platform="Adjuvanted inactivated whole-virion candidate",
            developer_sponsor="ICMR-National Institute of Virology and Indian Immunologicals Limited",
            stage_order=2,
            status_type="Preclinical / manufacturing-enabling",
            active_status="Improved candidate in development",
            regulatory_status="Investigational",
            target_use="Improved two-dose risk-based vaccine option for KFD endemic regions if clinical/regulatory milestones are met",
            evidence_summary="Indian public-sector and manufacturer partners report progress on an improved inactivated KFD vaccine candidate, with preclinical and manufacturing-development signals.",
            next_milestone="Human clinical trial confirmation, immunogenicity/safety readouts, and regulatory review.",
            development_geography="India",
            sources=[
                ("Government of India PIB KFD vaccine notice", "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2224977&lang=1&reg=3"),
                ("Frontiers in Immunology KFD vaccine candidate article", "https://www.frontiersin.org/journals/immunology/articles/10.3389/fimmu.2026.1786057/full"),
            ],
            notes="Script will upstage only if structured clinical-trial records or configured official sources provide a clear milestone.",
            now=now,
        ),
        seed_row(
            target="ZIKV",
            candidate="VRC5283 / VRC 705 DNA Zika vaccine",
            platform="DNA vaccine encoding Zika virus prM/E antigens",
            developer_sponsor="NIH Vaccine Research Center / NIAID and collaborators",
            stage_order=4,
            status_type="Phase 2 clinical development",
            active_status="Completed/closed trial signal; no licensed vaccine",
            regulatory_status="Investigational; no authorized Zika vaccine seeded",
            target_use="Potential outbreak/congenital-risk protection for reproductive-age populations if efficacy pathway resumes",
            evidence_summary="VRC5283 advanced into a Phase 2/2B Zika vaccine study, but Zika vaccine development remains without a licensed product.",
            next_milestone="Determine feasible efficacy/immunobridging pathway under lower or episodic transmission conditions.",
            development_geography="Americas and U.S. clinical research sites",
            sources=[
                ("ClinicalTrials.gov NCT03110770", "https://clinicaltrials.gov/study/NCT03110770"),
                ("NIAID Zika vaccine trial announcement", "https://www.niaid.nih.gov/news-events/phase-2-zika-vaccine-trial-begins-us-central-and-south-america"),
                ("WHO Zika fact sheet", "https://www.who.int/news-room/fact-sheets/detail/zika-virus"),
            ],
            notes="Highest seeded Zika stage is clinical, but not licensure.",
            now=now,
        ),
        seed_row(
            target="ZIKV",
            candidate="mRNA-1893 Zika vaccine",
            platform="mRNA vaccine encoding Zika virus antigens",
            developer_sponsor="Moderna",
            stage_order=4,
            status_type="Phase 2 clinical development",
            active_status="Phase 2 dose-confirmation clinical signal",
            regulatory_status="Investigational; no authorized Zika vaccine seeded",
            target_use="Potential outbreak/congenital-risk protection if development pathway succeeds",
            evidence_summary="mRNA-1893 has Phase 1 and Phase 2 ClinicalTrials.gov records and is tracked as a clinical-stage Zika candidate.",
            next_milestone="Safety, immunogenicity, durability, and viable efficacy/immunobridging strategy.",
            development_geography="United States and trial-network sites",
            sources=[
                ("ClinicalTrials.gov NCT04917861", "https://clinicaltrials.gov/study/NCT04917861"),
                ("ClinicalTrials.gov NCT04064905", "https://clinicaltrials.gov/study/NCT04064905"),
                ("WHO Zika fact sheet", "https://www.who.int/news-room/fact-sheets/detail/zika-virus"),
            ],
            now=now,
        ),
        seed_row(
            target="ZIKV",
            candidate="ZPIV purified inactivated Zika vaccine lineage",
            platform="Purified inactivated whole-virus Zika vaccine",
            developer_sponsor="Walter Reed Army Institute of Research / NIAID / BARDA partners",
            stage_order=3,
            status_type="Phase 1 clinical development",
            active_status="Early clinical signal",
            regulatory_status="Investigational; no authorized Zika vaccine seeded",
            target_use="Potential outbreak/congenital-risk protection if development pathway resumes",
            evidence_summary="ZPIV and related inactivated Zika vaccine candidates entered Phase 1 studies but are not licensed products.",
            next_milestone="Define development sponsor, immune correlate, and efficacy/immunobridging pathway.",
            development_geography="United States and other early clinical-trial settings",
            sources=[
                ("ClinicalTrials.gov NCT02937233", "https://clinicaltrials.gov/study/NCT02937233"),
                ("WHO Zika fact sheet", "https://www.who.int/news-room/fact-sheets/detail/zika-virus"),
            ],
            now=now,
        ),
        seed_row(
            target="WNV",
            candidate="HydroVax-001B West Nile virus vaccine",
            platform="Hydrogen peroxide-inactivated whole-virus vaccine candidate",
            developer_sponsor="Oregon Health & Science University / IDCRC / NIAID-supported network",
            stage_order=3,
            status_type="Phase 1 clinical development",
            active_status="Phase 1 safety/immunogenicity trial signal",
            regulatory_status="Investigational; no licensed human WNV vaccine",
            target_use="Potential severe-disease prevention for older adults and other high-risk groups if clinical pathway succeeds",
            evidence_summary="HydroVax-001B is in Phase 1 human evaluation, while public-health guidance still notes no licensed human WNV vaccine.",
            next_milestone="Phase 1 safety/immunogenicity readout and decision on age/risk-group development strategy.",
            development_geography="United States",
            sources=[
                ("ClinicalTrials.gov NCT06745921", "https://clinicaltrials.gov/study/NCT06745921"),
                ("IDCRC WNV vaccine trial launch", "https://idcrc.org/about/news-archive/west-nile.html"),
                ("CDC WNV treatment/prevention", "https://www.cdc.gov/west-nile-virus/hcp/treatment-prevention/index.html"),
            ],
            notes="No licensed human vaccine row is not a separate gap because a dedicated human clinical pathway is now represented.",
            now=now,
        ),
        seed_row(
            target="POWV",
            candidate="POW-VLP and other preclinical Powassan vaccine candidates",
            platform="Virus-like particle / live-attenuated / experimental platform candidates",
            developer_sponsor="Academic and preclinical developers including ATCC-linked POW-VLP work",
            stage_order=2,
            status_type="Preclinical",
            active_status="Preclinical proof-of-concept; no human vaccine",
            regulatory_status="No licensed human Powassan vaccine",
            target_use="Exploratory prevention for tick-exposed populations in endemic areas if candidate matures",
            evidence_summary="Preclinical Powassan vaccine candidates have shown immunogenicity/protection signals in animal models, but public-health guidance reports no human vaccine is available.",
            next_milestone="Candidate selection, GLP toxicology/CMC package, and first-in-human trial readiness.",
            development_geography="Preclinical research; North America focus",
            sources=[
                ("ATCC POW-VLP vaccine candidate webinar", "https://www.atcc.org/resources/webinars/2021-webinars/creating-a-vaccine-for-the-tick-borne-powassan-virus"),
                ("Pathogens POW-VLP preclinical article", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8229747/"),
                ("CDC Powassan treatment/prevention", "https://www.cdc.gov/powassan/hcp/treatment-prevention/index.html"),
            ],
            notes="Not upstaged above preclinical without a structured human-trial signal.",
            now=now,
        ),
        seed_row(
            target="OHFV",
            candidate="No dedicated Omsk hemorrhagic fever human-vaccine pathway identified",
            platform="Gap lane",
            developer_sponsor="None identified by automated scan/seed sources",
            stage_order=0,
            status_type="Gap / no dedicated pathway",
            active_status="No dedicated vaccine identified",
            regulatory_status="No Omsk hemorrhagic fever vaccine currently available in seeded public-health guidance",
            target_use=TARGETS["OHFV"]["default_use"],
            evidence_summary="Public-health guidance reports no dedicated Omsk hemorrhagic fever vaccine; TBE vaccines may offer partial/cross-protection considerations for selected high-risk groups but are not target-specific OHF vaccines.",
            next_milestone="Assess whether target-specific candidate development is warranted for exposed occupational groups.",
            development_geography="Western Siberia / high-risk occupational settings",
            sources=[
                ("CDC Omsk hemorrhagic fever overview", "https://www.cdc.gov/omsk-fever/about/index.html"),
            ],
            notes="Cross-protection by TBE vaccine is not counted as a dedicated OHFV vaccine lane.",
            now=now,
        ),
        seed_row(
            target="AHFV",
            candidate="No dedicated Alkhurma hemorrhagic fever human-vaccine pathway identified",
            platform="Gap lane",
            developer_sponsor="None identified by automated scan/seed sources",
            stage_order=0,
            status_type="Gap / no dedicated pathway",
            active_status="No dedicated vaccine identified",
            regulatory_status="No vaccine identified in seeded public disease-profile guidance",
            target_use=TARGETS["AHFV"]["default_use"],
            evidence_summary="Configured public sources identify no current vaccine for Alkhurma hemorrhagic fever virus.",
            next_milestone="Define epidemiologic target-product rationale and preclinical candidate strategy if prioritised.",
            development_geography="Arabian Peninsula / regional exposure settings",
            sources=[
                ("EFSA Alkhurma haemorrhagic fever disease profile", "https://animal-diseases.efsa.europa.eu/AHFV"),
                ("CDC Alkhurma hemorrhagic fever basics", "https://www.cdc.gov/alkhurma/about/index.html"),
            ],
            now=now,
        ),
        seed_row(
            target="SLEV",
            candidate="No St. Louis encephalitis human-vaccine pathway identified",
            platform="Gap lane",
            developer_sponsor="None identified by automated scan/seed sources",
            stage_order=0,
            status_type="Gap / no dedicated pathway",
            active_status="No human vaccine identified",
            regulatory_status="No St. Louis encephalitis vaccines available for humans in seeded CDC guidance",
            target_use=TARGETS["SLEV"]["default_use"],
            evidence_summary="CDC guidance states that no St. Louis encephalitis vaccines are available for use in humans.",
            next_milestone="Prioritization decision, candidate discovery, and potential integration with broader JE-serocomplex vaccine strategy.",
            development_geography="Americas",
            sources=[
                ("CDC SLE treatment/prevention", "https://www.cdc.gov/sle/hcp/treatment-prevention/index.html"),
                ("CDC SLE overview", "https://www.cdc.gov/sle/about/index.html"),
            ],
            now=now,
        ),
        seed_row(
            target="MVEV",
            candidate="No Murray Valley encephalitis human-vaccine pathway identified",
            platform="Gap lane",
            developer_sponsor="None identified by automated scan/seed sources",
            stage_order=0,
            status_type="Gap / no dedicated pathway",
            active_status="No human vaccine identified",
            regulatory_status="No vaccine or specific treatment in seeded Australian CDC guidance",
            target_use=TARGETS["MVEV"]["default_use"],
            evidence_summary="Australian public-health guidance identifies no vaccine or specific treatment for Murray Valley encephalitis virus infection.",
            next_milestone="Assess cross-protection science, One Health surveillance triggers, and feasibility of a dedicated candidate pathway.",
            development_geography="Australia and Papua New Guinea region",
            sources=[
                ("Australian CDC MVE overview", "https://www.cdc.gov.au/diseases/murray-valley-encephalitis-mve-virus-infection"),
                ("PHAC pathogen safety data sheet for MVEV", "https://www.canada.ca/en/public-health/services/laboratory-biosafety-biosecurity/pathogen-safety-data-sheets-risk-assessment/murray-valley-encephalitis.html"),
            ],
            now=now,
        ),
        seed_row(
            target="USUV",
            candidate="No Usutu human-vaccine pathway identified",
            platform="Gap lane",
            developer_sponsor="None identified by automated scan/seed sources",
            stage_order=0,
            status_type="Gap / no dedicated pathway",
            active_status="No human vaccine identified",
            regulatory_status="No Usutu vaccine available for humans in seeded CDC guidance",
            target_use=TARGETS["USUV"]["default_use"],
            evidence_summary="CDC guidance states that no Usutu virus vaccines are available for use in humans.",
            next_milestone="Clarify burden, risk groups, and whether WNV/JE-serocomplex vaccine technologies provide a development shortcut.",
            development_geography="Europe and other Culex-borne flavivirus surveillance settings",
            sources=[
                ("CDC Usutu clinical prevention", "https://www.cdc.gov/usutu/hcp/clinical-diagnosis-treatment/index.html"),
                ("CDC Usutu overview", "https://www.cdc.gov/usutu/about/index.html"),
            ],
            now=now,
        ),
    ]


def lower(text: str) -> str:
    return text.lower()


def classify_target(text: str) -> Optional[str]:
    t = lower(text)
    for code, aliases in TARGET_ALIASES:
        for alias in aliases:
            if alias.lower() in t:
                return code
    return None


def looks_like_vaccine_record(text: str) -> bool:
    t = lower(text)
    vaccine_terms = ["vaccine", "vaccination", "immunization", "immunisation", "vrc", "mrna", "hydrovax", "tak-003", "cyd-tdv", "zpiv"]
    return any(term in t for term in vaccine_terms)


def candidate_from_text(target: str, text: str) -> str:
    t = lower(text)
    patterns = [
        (r"\b(dengvaxia|cyd[-\s]?tdv)\b", "Dengvaxia / CYD-TDV"),
        (r"\b(qdenga|tak[-\s]?003|tak003)\b", "Qdenga / TAK-003"),
        (r"\b(tv003|tv005|butantan[-\s]?dv|butantan dengue)\b", "TV003 / TV005 / Butantan-DV lineage"),
        (r"\b(yf[-\s]?vax|stamaril|17d)\b", "17D yellow fever vaccines (YF-VAX / Stamaril / WHO-PQ producers)"),
        (r"\b(ixiaro|ic51)\b", "IXIARO / IC51"),
        (r"\b(sa14[-\s]?14[-\s]?2|cd\.jevax|cd jevax)\b", "Live attenuated SA14-14-2 Japanese encephalitis vaccines"),
        (r"\b(ticovac|fsme[-\s]?immun|fsmE[-\s]?immun)\b", "TicoVac / FSME-IMMUN"),
        (r"\b(encepur)\b", "Encepur and other established TBE vaccines"),
        (r"\b(vrc[-\s]?5283|vrc[-\s]?705)\b", "VRC5283 / VRC 705 DNA Zika vaccine"),
        (r"\b(mrna[-\s]?1893|mrna 1893)\b", "mRNA-1893 Zika vaccine"),
        (r"\b(zpiv|purified inactivated zika)\b", "ZPIV purified inactivated Zika vaccine lineage"),
        (r"\b(hydrovax[-\s]?001b|hydrovax[-\s]?001)\b", "HydroVax-001B West Nile virus vaccine"),
        (r"\b(pow[-\s]?vlp|virus[-\s]?like particle.*powassan)\b", "POW-VLP and other preclinical Powassan vaccine candidates"),
        (r"\b(kyasanur|kfd).*\b(inactivated|adjuvanted|candidate)\b", "ICMR-NIV / Indian Immunologicals improved inactivated KFD candidate"),
    ]
    for pattern, label in patterns:
        if re.search(pattern, t):
            return label
    return f"{TARGETS[target]['name']} vaccine candidate (unclassified clinical signal)"


def platform_from_candidate(candidate: str, text: str) -> str:
    t = lower(candidate + " " + text)
    if "dna" in t or "vrc5283" in t or "vrc 705" in t:
        return "DNA vaccine"
    if "mrna" in t:
        return "mRNA vaccine"
    if "inactivated" in t or "zpiv" in t or "hydrovax" in t or "ixiaro" in t or "ticovac" in t or "encepur" in t or "fsme" in t:
        return "Inactivated vaccine"
    if "vlp" in t or "virus-like" in t:
        return "Virus-like particle vaccine candidate"
    if "live" in t or "attenuated" in t or "dengvaxia" in t or "qdenga" in t or "tv003" in t or "tv005" in t or "17d" in t or "sa14" in t:
        return "Live attenuated vaccine"
    return "Vaccine candidate; platform requires manual review"


def stage_from_phases(phases: Sequence[str]) -> int:
    joined = " ".join(phases).upper().replace("_", " ")
    if "PHASE3" in joined or "PHASE 3" in joined:
        return 5
    if "PHASE2" in joined or "PHASE 2" in joined:
        return 4
    if "PHASE1" in joined or "PHASE 1" in joined or "EARLY" in joined:
        return 3
    return 1


def format_status(status: str) -> str:
    return clean(status).replace("_", " ").title() if status else "Status not reported"


def unique_join(values: Iterable[str], limit: int = 8) -> str:
    out: List[str] = []
    seen = set()
    for value in values:
        v = clean(value)
        if not v:
            continue
        key = v.lower()
        if key not in seen:
            seen.add(key)
            out.append(v)
        if len(out) >= limit:
            break
    return "; ".join(out)


def collect_strings(obj: Any, keys: Sequence[str]) -> List[str]:
    out: List[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in keys and isinstance(value, str):
                out.append(value)
            out.extend(collect_strings(value, keys))
    elif isinstance(obj, list):
        for item in obj:
            out.extend(collect_strings(item, keys))
    return out


def extract_study(study: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    protocol = study.get("protocolSection", {})
    ident = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    conditions = protocol.get("conditionsModule", {})
    interventions = protocol.get("armsInterventionsModule", {})
    sponsors = protocol.get("sponsorCollaboratorsModule", {})
    locations = protocol.get("contactsLocationsModule", {})

    nct_id = clean(ident.get("nctId"))
    if not nct_id:
        return None

    titles = [ident.get("briefTitle"), ident.get("officialTitle"), ident.get("acronym")]
    condition_text = " ".join(conditions.get("conditions", []) or [])
    intervention_names = []
    for item in interventions.get("interventions", []) or []:
        intervention_names.append(item.get("name", ""))
        intervention_names.extend(item.get("otherNames", []) or [])
        intervention_names.append(item.get("description", ""))
    text = clean(" | ".join([*(clean(x) for x in titles), condition_text, *intervention_names]))
    return {
        "nct_id": nct_id,
        "title": clean(ident.get("briefTitle") or ident.get("officialTitle")),
        "text": text,
        "phases": [clean(p) for p in design.get("phases", []) or []],
        "status": clean(status.get("overallStatus")),
        "start_date": clean((status.get("startDateStruct") or {}).get("date")),
        "completion_date": clean((status.get("completionDateStruct") or {}).get("date")),
        "lead_sponsor": clean((sponsors.get("leadSponsor") or {}).get("name")),
        "collaborators": [clean(c.get("name")) for c in sponsors.get("collaborators", []) or [] if isinstance(c, dict)],
        "countries": [clean(l.get("country")) for l in locations.get("locations", []) or [] if isinstance(l, dict)],
        "url": f"https://clinicaltrials.gov/study/{nct_id}",
    }


def http_get_json(url: str, timeout: int = 45) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "flavivirus-vaccine-dashboard/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
    return json.loads(body)


def http_get_text(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "flavivirus-vaccine-dashboard/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read(250_000)
    return raw.decode("utf-8", errors="replace")


def fetch_clinicaltrials(raw_dir: Path, max_pages: int, page_size: int, no_network: bool) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Any]]:
    warnings: List[str] = []
    audit = {"queries": [], "study_count": 0, "deduplicated_study_count": 0}
    if no_network:
        warnings.append("Network disabled; ClinicalTrials.gov refresh skipped and curated seed rows were used.")
        return [], warnings, audit

    raw_dir.mkdir(parents=True, exist_ok=True)
    studies_by_nct: Dict[str, Dict[str, Any]] = {}
    endpoint = "https://clinicaltrials.gov/api/v2/studies"
    for query in CLINICALTRIALS_QUERIES:
        query_slug = slugify(query, 64)
        page_token: Optional[str] = None
        query_total = 0
        raw_pages: List[Dict[str, Any]] = []
        for page in range(max_pages):
            params = {
                "format": "json",
                "pageSize": str(page_size),
                "query.term": query,
            }
            if page_token:
                params["pageToken"] = page_token
            url = f"{endpoint}?{urllib.parse.urlencode(params)}"
            try:
                payload = http_get_json(url)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
                warnings.append(f"ClinicalTrials.gov query failed for {query!r}: {exc}")
                break
            raw_pages.append(payload)
            for study in payload.get("studies", []) or []:
                extracted = extract_study(study)
                if not extracted:
                    continue
                studies_by_nct[extracted["nct_id"]] = extracted
                query_total += 1
            page_token = payload.get("nextPageToken")
            if not page_token:
                break
            time.sleep(0.15)
        (raw_dir / f"clinicaltrials_{query_slug}.json").write_text(json.dumps(raw_pages, indent=2, ensure_ascii=False), encoding="utf-8")
        audit["queries"].append({"query": query, "records_returned_before_dedupe": query_total})
    audit["study_count"] = sum(q["records_returned_before_dedupe"] for q in audit["queries"])
    audit["deduplicated_study_count"] = len(studies_by_nct)
    return list(studies_by_nct.values()), warnings, audit


def clinical_rows(studies: Sequence[Dict[str, Any]], now: str) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    grouped: Dict[Tuple[str, str], Dict[str, Any]] = {}
    record_counts: Dict[str, int] = defaultdict(int)
    for study in studies:
        text = clean(" | ".join([study.get("title", ""), study.get("text", "")]))
        target = classify_target(text)
        if not target or not looks_like_vaccine_record(text):
            continue
        candidate = candidate_from_text(target, text)
        key = (target, candidate.lower())
        stage_order = stage_from_phases(study.get("phases", []) or [])
        record_counts[target] += 1
        if key not in grouped:
            target_info = TARGETS[target]
            row = {
                "id": stable_id(target, candidate),
                "target_virus": target_info["name"],
                "target_abbrev": target,
                "virus_group": target_info["group"],
                "vector_or_route": target_info["vector_or_route"],
                "candidate": candidate,
                "platform": platform_from_candidate(candidate, text),
                "developer_sponsor": "",
                "stage_order": stage_order,
                "stage": STAGE_LABELS[stage_order],
                "status_type": "ClinicalTrials.gov signal",
                "active_status": "",
                "regulatory_status": "Investigational clinical-trial signal unless a curated official-source row also documents authorization",
                "target_use": target_info["default_use"],
                "evidence_summary": "",
                "next_milestone": "Manual review of trial protocol, results posting, and sponsor/regulatory source pages.",
                "development_geography": "",
                "notes": "Automatically classified from ClinicalTrials.gov title, conditions, interventions, phase, sponsor, and location fields.",
                "automation_method": "ClinicalTrials.gov v2 API deterministic classifier",
                "last_checked_utc": now,
                "supporting_record_count": 0,
                "_sources": [],
                "_statuses": [],
                "_sponsors": [],
                "_countries": [],
                "_titles": [],
            }
            grouped[key] = row
        row = grouped[key]
        if stage_order > int(row["stage_order"]):
            row["stage_order"] = stage_order
            row["stage"] = STAGE_LABELS[stage_order]
        row["supporting_record_count"] = int(row["supporting_record_count"]) + 1
        row["_sources"].append((study.get("nct_id", "ClinicalTrials.gov"), study.get("url", "")))
        row["_statuses"].append(format_status(study.get("status", "")))
        sponsors = [study.get("lead_sponsor", ""), *(study.get("collaborators", []) or [])]
        row["_sponsors"].extend(sponsors)
        row["_countries"].extend(study.get("countries", []) or [])
        row["_titles"].append(study.get("title", ""))

    out: List[Dict[str, Any]] = []
    for row in grouped.values():
        row["developer_sponsor"] = unique_join(row.pop("_sponsors"), limit=6) or "Sponsor not parsed"
        row["active_status"] = unique_join(row.pop("_statuses"), limit=5)
        row["development_geography"] = unique_join(row.pop("_countries"), limit=6) or "Not reported in parsed locations"
        titles = unique_join(row.pop("_titles"), limit=3)
        row["evidence_summary"] = f"{row['supporting_record_count']} ClinicalTrials.gov record(s) mapped to {row['candidate']}. Representative record titles: {titles}" if titles else f"{row['supporting_record_count']} ClinicalTrials.gov record(s) mapped to {row['candidate']}."
        sources = row.pop("_sources")
        assign_sources(row, sources)
        out.append(row)
    return out, dict(record_counts)


def normalize_key(row: Dict[str, Any]) -> Tuple[str, str]:
    return (clean(row.get("target_abbrev", "")), slugify(clean(row.get("candidate", "")), 100))


def combine_semicolon(a: str, b: str, limit: int = 7) -> str:
    return unique_join([*(a.split("; ") if a else []), *(b.split("; ") if b else [])], limit=limit)


def merge_rows(existing: Dict[str, Any], incoming: Dict[str, Any], now: str) -> Dict[str, Any]:
    existing_stage = int(existing.get("stage_order") or 0)
    incoming_stage = int(incoming.get("stage_order") or 0)
    if incoming_stage > existing_stage:
        # Preserve identity/source richness from existing, but adopt incoming development stage and clinical status.
        existing["stage_order"] = incoming_stage
        existing["stage"] = STAGE_LABELS[incoming_stage]
        existing["status_type"] = combine_semicolon(existing.get("status_type", ""), incoming.get("status_type", ""), limit=4)
        existing["active_status"] = combine_semicolon(incoming.get("active_status", ""), existing.get("active_status", ""), limit=5)
        existing["next_milestone"] = incoming.get("next_milestone") or existing.get("next_milestone", "")
    else:
        existing["status_type"] = combine_semicolon(existing.get("status_type", ""), incoming.get("status_type", ""), limit=4)
        existing["active_status"] = combine_semicolon(existing.get("active_status", ""), incoming.get("active_status", ""), limit=5)

    if incoming.get("developer_sponsor"):
        existing["developer_sponsor"] = combine_semicolon(existing.get("developer_sponsor", ""), incoming.get("developer_sponsor", ""), limit=7)
    if incoming.get("development_geography"):
        existing["development_geography"] = combine_semicolon(existing.get("development_geography", ""), incoming.get("development_geography", ""), limit=7)

    clinical_phrase = incoming.get("evidence_summary", "")
    if clinical_phrase and clinical_phrase not in existing.get("evidence_summary", ""):
        existing["evidence_summary"] = clean(existing.get("evidence_summary", "") + " " + clinical_phrase)
    existing["automation_method"] = combine_semicolon(existing.get("automation_method", ""), incoming.get("automation_method", ""), limit=5)
    existing["last_checked_utc"] = now
    existing["supporting_record_count"] = int(existing.get("supporting_record_count") or 0) + int(incoming.get("supporting_record_count") or 0)
    assign_sources(existing, [*source_pairs(existing), *source_pairs(incoming)])
    return existing


def add_missing_gap_rows(rows: List[Dict[str, Any]], now: str) -> List[Dict[str, Any]]:
    targets_present = {clean(row.get("target_abbrev")) for row in rows}
    for target in TARGETS:
        if target not in targets_present:
            target_info = TARGETS[target]
            rows.append(seed_row(
                target=target,
                candidate=f"No dedicated {target_info['name']} human-vaccine pathway identified",
                platform="Gap lane",
                developer_sponsor="None identified by automated scan/seed sources",
                stage_order=0,
                status_type="Gap / no dedicated pathway",
                active_status="No human vaccine pathway identified",
                regulatory_status="No dedicated human vaccine authorization or clinical pathway identified by this automated build",
                target_use=target_info["default_use"],
                evidence_summary="Automatically generated because no configured seed or ClinicalTrials.gov record mapped to this target.",
                next_milestone="Manual prioritization review and candidate-discovery surveillance.",
                development_geography="Not applicable",
                sources=[("ClinicalTrials.gov automated search", "https://clinicaltrials.gov/")],
                notes="Generated fallback gap row.",
                supporting_record_count=0,
                now=now,
            ))
    return rows


def fetch_watch_pages(raw_dir: Path, no_network: bool) -> Tuple[List[Dict[str, Any]], List[str]]:
    warnings: List[str] = []
    audit_rows: List[Dict[str, Any]] = []
    if no_network:
        warnings.append("Network disabled; configured watch-page audit skipped.")
        return audit_rows, warnings
    raw_dir.mkdir(parents=True, exist_ok=True)
    for label, url in WATCH_PAGES:
        try:
            text = http_get_text(url)
            slug = slugify(label, 60)
            (raw_dir / f"watch_{slug}.txt").write_text(text, encoding="utf-8")
            audit_rows.append({"label": label, "url": url, "status": "fetched", "bytes": len(text.encode("utf-8"))})
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            warnings.append(f"Watch page failed for {label}: {exc}")
            audit_rows.append({"label": label, "url": url, "status": f"failed: {exc}", "bytes": 0})
    return audit_rows, warnings


def build_report(
    *,
    now: str,
    rows: Sequence[Dict[str, Any]],
    output_csv: Path,
    clinical_audit: Dict[str, Any],
    clinical_counts: Dict[str, int],
    watch_audit: Sequence[Dict[str, Any]],
    warnings: Sequence[str],
    no_network: bool,
) -> str:
    stage_counts = defaultdict(int)
    target_highest = {}
    for row in rows:
        stage = int(row.get("stage_order") or 0)
        stage_counts[stage] += 1
        target = clean(row.get("target_abbrev", ""))
        target_highest[target] = max(target_highest.get(target, 0), stage)

    lines = [
        "# Flavivirus vaccine dashboard automation summary",
        "",
        f"Generated: `{now}`",
        f"Output CSV: `{output_csv.as_posix()}`",
        f"Network mode: `{'disabled / seed-only snapshot' if no_network else 'enabled'}`",
        "",
        "## Pipeline totals",
        "",
        f"- Rows written: **{len(rows)}**",
        f"- Target viruses represented: **{len(target_highest)}**",
        f"- ClinicalTrials.gov records returned before dedupe: **{clinical_audit.get('study_count', 0)}**",
        f"- ClinicalTrials.gov records after NCT dedupe: **{clinical_audit.get('deduplicated_study_count', 0)}**",
        "",
        "## Rows by stage",
        "",
    ]
    for stage in sorted(STAGE_LABELS):
        lines.append(f"- Stage {stage} — {STAGE_LABELS[stage]}: **{stage_counts.get(stage, 0)}**")
    lines.extend(["", "## Highest mapped stage by target", ""])
    for target in sorted(TARGETS):
        lines.append(f"- **{target}** ({TARGETS[target]['name']}): stage {target_highest.get(target, 0)}")

    lines.extend(["", "## ClinicalTrials.gov query audit", ""])
    if clinical_audit.get("queries"):
        for item in clinical_audit["queries"]:
            lines.append(f"- `{item['query']}` → {item['records_returned_before_dedupe']} record(s) before dedupe")
    else:
        lines.append("- No ClinicalTrials.gov query results recorded for this run.")

    if clinical_counts:
        lines.extend(["", "### Classified ClinicalTrials.gov records by target", ""])
        for target, count in sorted(clinical_counts.items()):
            lines.append(f"- **{target}**: {count}")

    lines.extend(["", "## Watch-page audit", ""])
    if watch_audit:
        for item in watch_audit:
            lines.append(f"- {item['label']}: {item['status']} ({item.get('bytes', 0)} bytes) — {item['url']}")
    else:
        lines.append("- No watch pages fetched for this run.")

    lines.extend([
        "",
        "## Classification rules",
        "",
        "- Clinical trial records are deduplicated by NCT ID.",
        "- Target virus and candidate labels are assigned with deterministic alias and candidate-pattern rules in `scripts/fetch_pipeline.py`.",
        "- ClinicalTrials.gov phase fields map to stages 3–5; curated official-source rows are required for stage 6 or 7 authorization/programme claims.",
        "- Gap rows are generated only when no target-specific seed or clinical signal is available.",
        "- News or arbitrary webpage text is not used to upstage candidates automatically.",
        "",
        "## Warnings",
        "",
    ])
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def write_csv(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = {field: clean(row.get(field, "")) for field in FIELDNAMES}
            writer.writerow(out)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build the flavivirus vaccine-development pipeline CSV.")
    parser.add_argument("--data", default="data/pipeline.csv", help="Output CSV path")
    parser.add_argument("--report", default="reports/automation_summary.md", help="Output automation report path")
    parser.add_argument("--raw-dir", default="data/raw", help="Directory for raw API/watch artifacts")
    parser.add_argument("--max-pages", type=int, default=4, help="Maximum ClinicalTrials.gov pages per query")
    parser.add_argument("--page-size", type=int, default=100, help="ClinicalTrials.gov page size")
    parser.add_argument("--no-network", action="store_true", help="Skip network calls and build from curated seeds only")
    args = parser.parse_args(argv)

    env_no_network = os.getenv("FLAVIVIRUS_DASHBOARD_NO_NETWORK", "").lower() in {"1", "true", "yes"}
    no_network = args.no_network or env_no_network
    now = utc_now()
    raw_dir = Path(args.raw_dir)
    warnings: List[str] = []

    rows_by_key: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for row in make_seed_rows(now):
        rows_by_key[normalize_key(row)] = row

    studies, clinical_warnings, clinical_audit = fetch_clinicaltrials(raw_dir, args.max_pages, args.page_size, no_network)
    warnings.extend(clinical_warnings)
    ct_rows, clinical_counts = clinical_rows(studies, now)
    for row in ct_rows:
        key = normalize_key(row)
        if key in rows_by_key:
            rows_by_key[key] = merge_rows(rows_by_key[key], row, now)
        else:
            rows_by_key[key] = row

    watch_audit, watch_warnings = fetch_watch_pages(raw_dir, no_network)
    warnings.extend(watch_warnings)

    rows = list(rows_by_key.values())
    rows = add_missing_gap_rows(rows, now)
    rows.sort(key=lambda r: (clean(r.get("virus_group")), clean(r.get("target_abbrev")), -int(r.get("stage_order") or 0), clean(r.get("candidate"))))

    output_csv = Path(args.data)
    write_csv(output_csv, rows)

    report = build_report(
        now=now,
        rows=rows,
        output_csv=output_csv,
        clinical_audit=clinical_audit,
        clinical_counts=clinical_counts,
        watch_audit=watch_audit,
        warnings=warnings,
        no_network=no_network,
    )
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"Wrote {output_csv} with {len(rows)} rows")
    print(f"Wrote {report_path}")
    if warnings:
        print("Warnings:", file=sys.stderr)
        for warning in warnings:
            print(f"- {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
