#!/usr/bin/env python3
"""
Pipeline APA 7 — orquestrador.

Etapas:
1) Padronizar metadados (YAML)
2) Validar referências (CrossRef)
3) Gerar manuscrito
4) Checagens (citações, DOI, APA, método, originalidade)
5) Exportar MD/DOCX/BibTeX/RIS + relatórios JSON
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from crossref_validate import save_refs, validate_dois  # noqa: E402
from export_formats import markdown_to_docx, to_bibtex, to_ris  # noqa: E402
from generate_manuscript import build_cover_letter, build_manuscript  # noqa: E402
from verify_article import build_report, write_report  # noqa: E402


def load_input(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def slugify(text: str, fallback: str = "artigo") -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_text.lower()).strip("_")
    return (slug[:72] or fallback)


def check_orcid(orcid_url: str) -> dict:
    orcid = orcid_url.rstrip("/").split("/")[-1]
    url = f"https://pub.orcid.org/v3.0/{orcid}/person"
    try:
        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "APA7-Pipeline/1.1 (mailto:antonioandradepy@gmail.com)",
            },
            timeout=20,
        )
        if response.status_code != 200:
            return {"orcid": orcid, "ok": False, "error": f"HTTP {response.status_code}"}
        person = response.json()
        name = person.get("name") or {}
        given = ((name.get("given-names") or {}).get("value")) or ""
        family = ((name.get("family-name") or {}).get("value")) or ""
        return {
            "orcid": orcid,
            "ok": True,
            "display_name": f"{given} {family}".strip(),
            "url": f"https://orcid.org/{orcid}",
        }
    except Exception as exc:  # noqa: BLE001
        return {"orcid": orcid, "ok": False, "error": str(exc)}


def try_pdf(docx_path: Path, pdf_path: Path, md_path: Path, out_dir: Path) -> str:
    try:
        soffice = shutil.which("libreoffice") or shutil.which("soffice")
        if soffice:
            subprocess.run(
                [
                    soffice,
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(out_dir),
                    str(docx_path),
                ],
                check=True,
                capture_output=True,
            )
            return pdf_path.name if pdf_path.exists() else "conversão sem arquivo"
        if shutil.which("pandoc"):
            subprocess.run(
                ["pandoc", str(md_path), "-o", str(pdf_path)],
                check=True,
                capture_output=True,
            )
            return pdf_path.name
        return "libreoffice/pandoc ausentes"
    except Exception as exc:  # noqa: BLE001
        return f"falha: {exc}"


def main() -> int:
    input_path = ROOT / "data" / "estudo_input.yaml"
    out_dir = ROOT / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    data = load_input(input_path)
    estudo = data["estudo"]
    meta = data["metadados"]
    limits = data.get("limites_verificacao") or {}
    similarity_max = float(limits.get("similaridade_max_percent", 15))
    slug = data.get("slug") or slugify(meta.get("titulo_provisorio") or "artigo")

    # 1) Validação CrossRef
    dois = list(estudo.get("bibliografia_inicial") or [])
    refs = validate_dois(dois)
    refs_path = ROOT / "data" / "references_validated.json"
    save_refs(refs, refs_path)

    unlocated = [r for r in refs if not r.get("located")]
    print(f"[CrossRef] {len(refs) - len(unlocated)}/{len(refs)} DOIs localizados")
    for item in unlocated:
        print(f"  NÃO LOCALIZADO: {item.get('doi')} ({item.get('error')})")

    # 1b) ORCID do correspondente
    autor = meta["autores"][0]
    orcid_info = check_orcid(autor.get("orcid") or "")
    print(f"[ORCID] {orcid_info}")

    # 2) Manuscrito
    manuscript = build_manuscript(data, refs)
    md_path = out_dir / f"artigo_apa7_{slug}.md"
    md_path.write_text(manuscript, encoding="utf-8")

    cover = build_cover_letter(data)
    cover_path = out_dir / "cover_letter.md"
    cover_path.write_text(cover, encoding="utf-8")

    # 3) Verificações
    report = build_report(
        body_text=manuscript,
        refs=refs,
        estudo=estudo,
        etica=meta.get("etica") or {},
        similarity_max=similarity_max,
    )
    report["orcid"] = orcid_info
    report["run"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": str(input_path.relative_to(ROOT)),
        "idioma": data.get("idioma"),
        "estilo": data.get("estilo_citacao"),
        "titulo": meta.get("titulo_provisorio"),
        "slug": slug,
        "versao": data.get("versao_rascunho"),
    }
    report_path = out_dir / "verification_report.json"
    write_report(report, report_path)

    # 4) Exportações
    bib_path = out_dir / "references.bib"
    ris_path = out_dir / "references.ris"
    bib_path.write_text(to_bibtex(refs), encoding="utf-8")
    ris_path.write_text(to_ris(refs), encoding="utf-8")

    docx_path = out_dir / f"artigo_apa7_{slug}.docx"
    title = " ".join(meta["titulo_provisorio"].split())
    markdown_to_docx(manuscript, docx_path, title=title)

    # 5) Registro de revisão
    revision = {
        "versions": [
            {
                "id": "v1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "label": "rascunho_inicial_pipeline",
                "changes_accepted": [
                    "Geração completa das seções APA 7",
                    "Validação CrossRef das referências iniciais",
                    "Consulta ORCID do autor correspondente",
                    "Exportação MD/DOCX/BibTeX/RIS",
                ],
                "changes_rejected": [],
                "export_ready": report["export_ready"],
                "notes": report["summary"],
            }
        ]
    }
    revision_path = out_dir / "revision_log.json"
    revision_path.write_text(json.dumps(revision, indent=2, ensure_ascii=False), encoding="utf-8")

    pdf_path = out_dir / f"artigo_apa7_{slug}.pdf"
    pdf_status = try_pdf(docx_path, pdf_path, md_path, out_dir)

    checklist = {
        "capa_completa": True,
        "resumo_palavras_chave": True,
        "secoes_obrigatorias": report["formatacao_apa"]["ok"],
        "citacoes_consistentes": report["citacoes_vs_referencias"]["ok"],
        "dois_validos": report["dois"]["ok"],
        "plagio_abaixo_limite": report["plagio"]["ok"],
        "etica_declarada": report["coerencia_metodologica"]["ok"],
        "orcid_autor": orcid_info.get("ok"),
        "exports": {
            "md": md_path.name,
            "docx": docx_path.name,
            "bib": bib_path.name,
            "ris": ris_path.name,
            "pdf": pdf_status,
            "verification_report": report_path.name,
            "revision_log": revision_path.name,
            "cover_letter": cover_path.name,
        },
        "export_ready": report["export_ready"],
    }
    (out_dir / "export_checklist.json").write_text(
        json.dumps(checklist, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "export_ready": report["export_ready"],
                "summary": report["summary"],
                "checklist": checklist,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0 if report["export_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
