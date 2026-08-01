#!/usr/bin/env python3
"""Valida e completa metadados bibliográficos via CrossRef / DOI.org."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

USER_AGENT = "APA7-Pipeline/1.0 (mailto:antonioandradepy@gmail.com)"
CROSSREF = "https://api.crossref.org/works"


def clean(text: str | None) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def initials(given: str) -> str:
    parts = [p for p in given.replace("-", " ").split() if p]
    return " ".join(f"{p[0].upper()}." for p in parts)


def format_authors_apa(authors: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for author in authors:
        family = clean(author.get("family", ""))
        given = clean(author.get("given", ""))
        if not family:
            continue
        ini = initials(given)
        out.append(f"{family}, {ini}".strip() if ini else family)
    return out


def author_string(authors: list[str]) -> str:
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]}, & {authors[1]}"
    return ", ".join(authors[:-1]) + f", & {authors[-1]}"


def extract_year(item: dict[str, Any]) -> int | None:
    for key in ("published-print", "published-online", "issued"):
        parts = (item.get(key) or {}).get("date-parts", [[None]])[0]
        if parts and parts[0]:
            return int(parts[0])
    return None


def cite_key(authors: list[str], year: int | None) -> str:
    if authors:
        family = authors[0].split(",")[0]
        family = re.sub(r"^de\s+", "", family, flags=re.I)
        family = re.sub(r"[^A-Za-zÀ-ÿ]", "", family)
    else:
        family = "Anonymous"
    return f"{family.lower()}{year or 'nd'}"


def apa_journal_reference(meta: dict[str, Any]) -> str:
    authors = meta["authors"]
    year = meta["year"] or "n.d."
    title = meta["title"]
    journal = meta["journal"]
    volume = meta.get("volume")
    issue = meta.get("issue")
    page = meta.get("page")
    doi = meta["doi"]

    ref = f"{author_string(authors)} ({year}). {title}."
    if journal:
        ref += f" *{journal}*"
        if volume:
            ref += f", *{volume}*"
            if issue and str(issue) not in {"0", "null", "None"}:
                ref += f"({issue})"
        if page:
            ref += f", {page}"
        ref += "."
    ref += f" https://doi.org/{doi}"
    return ref


def fetch_doi(doi: str) -> dict[str, Any]:
    doi = doi.strip().removeprefix("https://doi.org/").removeprefix("http://doi.org/")
    url = f"{CROSSREF}/{quote(doi, safe='/')}"
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    if response.status_code != 200:
        return {
            "doi": doi,
            "doi_valid": False,
            "error": f"HTTP {response.status_code}",
            "located": False,
        }
    item = response.json()["message"]
    authors = format_authors_apa(item.get("author") or [])
    year = extract_year(item)
    meta = {
        "doi": doi,
        "doi_valid": True,
        "located": True,
        "title": clean(" ".join(item.get("title") or [])),
        "authors": authors,
        "journal": clean(" ".join(item.get("container-title") or [])),
        "year": year,
        "volume": item.get("volume"),
        "issue": item.get("issue"),
        "page": item.get("page"),
        "type": item.get("type"),
        "url": f"https://doi.org/{doi}",
        "cite_key": cite_key(authors, year),
    }
    meta["apa"] = apa_journal_reference(meta)
    return meta


def validate_dois(dois: list[str]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    key_counts: dict[str, int] = {}
    for doi in dois:
        meta = fetch_doi(doi)
        if meta.get("located"):
            base = meta["cite_key"]
            key_counts[base] = key_counts.get(base, 0) + 1
            if key_counts[base] > 1:
                meta["cite_key"] = f"{base}{chr(96 + key_counts[base])}"
            # first duplicate becomes ...a / ...b — fix first occurrence too
        refs.append(meta)

    # normalize duplicate keys: thijsen2021, thijsen2021b → thijsen2021a, thijsen2021b
    groups: dict[str, list[int]] = {}
    for idx, ref in enumerate(refs):
        if not ref.get("located"):
            continue
        base = re.sub(r"[a-z]$", "", ref["cite_key"]) if re.search(r"\d{4}[a-z]$", ref["cite_key"]) else ref["cite_key"]
        # recompute clean base
        base = cite_key(ref.get("authors") or [], ref.get("year"))
        groups.setdefault(base, []).append(idx)
    for base, idxs in groups.items():
        if len(idxs) == 1:
            refs[idxs[0]]["cite_key"] = base
        else:
            for n, idx in enumerate(idxs):
                refs[idx]["cite_key"] = f"{base}{chr(97 + n)}"
                refs[idx]["apa"] = apa_journal_reference(refs[idx])
    return refs


def save_refs(refs: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(refs, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    import sys

    dois = sys.argv[1:]
    if not dois:
        print("Uso: crossref_validate.py DOI [DOI ...]")
        raise SystemExit(1)
    out = validate_dois(dois)
    print(json.dumps(out, indent=2, ensure_ascii=False))
