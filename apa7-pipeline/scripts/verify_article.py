#!/usr/bin/env python3
"""Checagens automáticas: citações, DOI, APA e originalidade heurística."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


SECOND_AUTHOR = r"(?:\s+et\s+al\.|\s*&\s*[A-ZÀ-Ÿ][A-Za-zÀ-ÿ'\-]+|\s+(?:and|e)\s+[A-ZÀ-Ÿ][A-Za-zÀ-ÿ'\-]+)"
PARENTHETICAL_UNIT = re.compile(
    r"([A-ZÀ-Ÿ][A-Za-zÀ-ÿ'\-]+)"
    + SECOND_AUTHOR
    + r"?,\s*(\d{4}[a-z]?)"
)
NARRATIVE_CITATION = re.compile(
    r"\b([A-ZÀ-Ÿ][A-Za-zÀ-ÿ'\-]+)(?:\s+et\s+al\.)?(?:"
    + SECOND_AUTHOR
    + r")?\s+\((\d{4}[a-z]?)\)"
)


def extract_parenthetical_keys(text: str) -> list[str]:
    keys: list[str] = []
    for match in re.finditer(r"\(([^)]+)\)", text):
        blob = match.group(1)
        if not re.search(r"\d{4}", blob):
            continue
        for part in blob.split(";"):
            m = PARENTHETICAL_UNIT.search(part.strip())
            if m:
                keys.append(f"{m.group(1).lower()}{m.group(2)}")
    return keys


def extract_narrative_keys(text: str) -> list[str]:
    keys: list[str] = []
    for match in NARRATIVE_CITATION.finditer(text):
        keys.append(f"{match.group(1).lower()}{match.group(2)}")
    return keys


def citation_consistency(body_text: str, refs: list[dict[str, Any]]) -> dict[str, Any]:
    ref_keys = {r["cite_key"] for r in refs if r.get("located")}
    # also allow first-author family from APA authors
    alias: dict[str, str] = {}
    for ref in refs:
        if not ref.get("located"):
            continue
        key = ref["cite_key"]
        if ref.get("authors"):
            family = re.sub(r"^de\s+", "", ref["authors"][0].split(",")[0], flags=re.I)
            family = re.sub(r"[^A-Za-zÀ-ÿ]", "", family).lower()
            year = str(ref.get("year") or "nd")
            # letter suffix if present in cite_key
            suffix = key[len(family) + len(re.sub(r"[a-z]$", "", key.split(year)[0]) if False else "" ) :]
            # simpler: map family+year and family+year+letter
            base = f"{family}{ref.get('year')}"
            alias[base] = key
            alias[key] = key
            m = re.search(r"(\d{4})([a-z])?$", key)
            if m and m.group(2):
                alias[f"{family}{m.group(1)}{m.group(2)}"] = key

    cited = extract_parenthetical_keys(body_text) + extract_narrative_keys(body_text)
    normalized = []
    missing_in_refs = []
    for c in cited:
        if c in ref_keys:
            normalized.append(c)
        elif c in alias:
            normalized.append(alias[c])
        else:
            # try strip letter
            missing_in_refs.append(c)

    cited_set = set(normalized)
    unused_refs = sorted(ref_keys - cited_set)
    return {
        "citations_in_text": sorted(set(cited)),
        "citations_resolved": sorted(cited_set),
        "missing_in_reference_list": sorted(set(missing_in_refs)),
        "unused_in_text": unused_refs,
        "ok": len(missing_in_refs) == 0 and len(unused_refs) == 0,
    }


def doi_report(refs: list[dict[str, Any]]) -> dict[str, Any]:
    located = [r for r in refs if r.get("located")]
    invalid = [r.get("doi") for r in refs if not r.get("doi_valid")]
    without_doi = [r.get("cite_key") for r in located if not r.get("doi")]
    return {
        "total": len(refs),
        "located": len(located),
        "invalid_or_unlocated": invalid,
        "without_doi": without_doi,
        "ok": len(invalid) == 0 and len(without_doi) == 0,
    }


def apa_format_checks(text: str) -> dict[str, Any]:
    issues: list[str] = []
    recommendations: list[str] = []

    required = [
        "Resumo",
        "Palavras-chave",
        "Introdução",
        "Método",
        "Resultados",
        "Discussão",
        "Conclusão",
        "Referências",
    ]
    for heading in required:
        if heading.lower() not in text.lower():
            issues.append(f"Seção obrigatória ausente ou não rotulada: {heading}")

    # long quoted passages (>40 words) should be block quotes (heuristic: quotes with many words)
    for match in re.finditer(r"[\"“]([^\"”]{200,})[\"”]", text):
        words = len(match.group(1).split())
        if words > 40:
            issues.append(
                f"Citação direta com ~{words} palavras parece estar entre aspas; em APA 7 use bloco (sem aspas)."
            )

    if "Conflito" not in text and "conflitos de interesse" not in text.lower():
        issues.append("Declaração de conflito de interesse não encontrada.")
    if "Financiamento" not in text and "financiamento" not in text.lower():
        recommendations.append("Incluir seção explícita de Financiamento.")

    if re.search(r"\b[A-Z][a-z]+,\s+[A-Z][a-z]+,\s+[A-Z][a-z]+,\s+\d{4}\b", text):
        recommendations.append(
            "Em APA 7, obras com 3+ autores usam et al. desde a primeira citação no texto."
        )

    return {
        "issues": issues,
        "recommendations": recommendations,
        "ok": len(issues) == 0,
    }


def methodology_checklist(estudo: dict[str, Any], etica: dict[str, Any]) -> dict[str, Any]:
    items = []
    def add(name: str, ok: bool, detail: str):
        items.append({"item": name, "ok": ok, "detail": detail})

    add("tipo_estudo_definido", bool(estudo.get("tipo_estudo")), str(estudo.get("tipo_estudo")))
    add("objetivo_definido", bool(estudo.get("objetivo")), "objetivo presente" if estudo.get("objetivo") else "ausente")
    add("amostra_ou_corpus", bool(estudo.get("amostra")), str(estudo.get("amostra"))[:160])
    add("instrumentos", bool(estudo.get("instrumentos")), f"{len(estudo.get('instrumentos') or [])} itens")
    add("procedimentos", bool(estudo.get("procedimentos")), "procedimentos descritos")
    add("analises", bool(estudo.get("analises")), "estratégia analítica descrita")

    humans = bool(etica.get("envolvidos_humanos_animais"))
    ethics_text = (etica.get("declaracao") or "").strip()
    if humans:
        add("etica_aprovacao", bool(ethics_text), ethics_text or "aprovação ética obrigatória ausente")
    else:
        add("etica_declaracao_revisao", bool(ethics_text), ethics_text or "declarar N/A para revisão")

    ok = all(i["ok"] for i in items)
    return {"items": items, "ok": ok}


def originality_heuristic(text: str, threshold: float = 15.0) -> dict[str, Any]:
    """
    Estimativa local (não substitui Turnitin/iThenticate).
    Combina: densidade de frases genéricas acadêmicas + repetição interna de n-gramas.
    """
    boilerplate = [
        "de acordo com a literatura",
        "neste sentido",
        "pode-se concluir que",
        "é importante destacar",
        "no que tange",
        "diante do exposto",
        "torna-se evidente",
        "vale ressaltar",
        "nesse contexto",
        "à luz dos resultados",
    ]
    lower = text.lower()
    words = re.findall(r"[a-zà-ÿ]{3,}", lower)
    if not words:
        return {"similarity_percent": 0.0, "flag_human_review": False, "method": "heuristic-local", "ok": True}

    hits = sum(lower.count(p) for p in boilerplate)
    boilerplate_score = min(40.0, hits * 2.5)

    # repeated 7-grams
    n = 7
    grams = [" ".join(words[i : i + n]) for i in range(max(0, len(words) - n + 1))]
    counts = Counter(grams)
    repeated = sum(c - 1 for c in counts.values() if c > 1)
    repeat_score = min(40.0, (repeated / max(len(grams), 1)) * 100)

    # very short paragraphs ratio (possible padding)
    paras = [p.strip() for p in text.split("\n") if p.strip() and not p.startswith("#")]
    short = sum(1 for p in paras if 0 < len(p.split()) < 12)
    short_score = min(20.0, (short / max(len(paras), 1)) * 40)

    similarity = round(min(100.0, 0.45 * boilerplate_score + 0.40 * repeat_score + 0.15 * short_score), 2)
    return {
        "similarity_percent": similarity,
        "threshold_percent": threshold,
        "flag_human_review": similarity > threshold,
        "method": "heuristic-local (não é Turnitin/iThenticate)",
        "components": {
            "boilerplate_score": round(boilerplate_score, 2),
            "repeat_score": round(repeat_score, 2),
            "short_paragraph_score": round(short_score, 2),
        },
        "ok": similarity <= threshold,
        "note": "Para submissão formal, rodar verificação comercial de similaridade.",
    }


def build_report(
    body_text: str,
    refs: list[dict[str, Any]],
    estudo: dict[str, Any],
    etica: dict[str, Any],
    similarity_max: float = 15.0,
) -> dict[str, Any]:
    cit = citation_consistency(body_text, refs)
    dois = doi_report(refs)
    apa = apa_format_checks(body_text)
    method = methodology_checklist(estudo, etica)
    orig = originality_heuristic(body_text, threshold=similarity_max)

    export_ready = all([cit["ok"], dois["ok"], apa["ok"], method["ok"], orig["ok"]])
    return {
        "plagio": orig,
        "citacoes_vs_referencias": cit,
        "dois": dois,
        "formatacao_apa": apa,
        "coerencia_metodologica": method,
        "export_ready": export_ready,
        "summary": {
            "similaridade_percent": orig["similarity_percent"],
            "citacoes_faltantes": cit["missing_in_reference_list"],
            "referencias_nao_citadas": cit["unused_in_text"],
            "referencias_sem_doi_ou_invalidas": dois["invalid_or_unlocated"] + dois["without_doi"],
            "erros_formatacao_apa": apa["issues"],
        },
    }


def write_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
