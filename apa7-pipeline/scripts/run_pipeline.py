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
import sys
from datetime import datetime, timezone
from pathlib import Path

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


def main() -> int:
    input_path = ROOT / "data" / "estudo_input.yaml"
    out_dir = ROOT / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    data = load_input(input_path)
    estudo = data["estudo"]
    meta = data["metadados"]
    limits = data.get("limites_verificacao") or {}
    similarity_max = float(limits.get("similaridade_max_percent", 15))

    # 1) Validação CrossRef
    dois = list(estudo.get("bibliografia_inicial") or [])
    refs = validate_dois(dois)
    refs_path = ROOT / "data" / "references_validated.json"
    save_refs(refs, refs_path)

    unlocated = [r for r in refs if not r.get("located")]
    print(f"[CrossRef] {len(refs) - len(unlocated)}/{len(refs)} DOIs localizados")
    for r in unlocated:
        print(f"  NÃO LOCALIZADO: {r.get('doi')} ({r.get('error')})")

    # 2) Manuscrito
    manuscript = build_manuscript(data, refs)
    md_path = out_dir / "artigo_apa7_reacoes_adversas_doacao_sangue.md"
    md_path.write_text(manuscript, encoding="utf-8")

    cover = build_cover_letter(data)
    cover_path = out_dir / "cover_letter.md"
    cover_path.write_text(cover, encoding="utf-8")

    # 3) Verificações (corpo sem lista de referências APA longas para citações)
    # Usa o manuscrito completo; o verificador procura seções e pares citação/ref
    report = build_report(
        body_text=manuscript,
        refs=refs,
        estudo=estudo,
        etica=meta.get("etica") or {},
        similarity_max=similarity_max,
    )
    report["run"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": str(input_path.relative_to(ROOT)),
        "idioma": data.get("idioma"),
        "estilo": data.get("estilo_citacao"),
        "titulo": meta.get("titulo_provisorio"),
    }
    report_path = out_dir / "verification_report.json"
    write_report(report, report_path)

    # 4) Exportações
    bib_path = out_dir / "references.bib"
    ris_path = out_dir / "references.ris"
    bib_path.write_text(to_bibtex(refs), encoding="utf-8")
    ris_path.write_text(to_ris(refs), encoding="utf-8")

    docx_path = out_dir / "artigo_apa7_reacoes_adversas_doacao_sangue.docx"
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

    # 6) Tentativa PDF via LibreOffice (preferencial) ou pandoc
    pdf_path = out_dir / "artigo_apa7_reacoes_adversas_doacao_sangue.pdf"
    pdf_status = "não gerado"
    try:
        import shutil
        import subprocess

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
            pdf_status = pdf_path.name if pdf_path.exists() else "conversão sem arquivo"
        elif shutil.which("pandoc"):
            subprocess.run(
                ["pandoc", str(md_path), "-o", str(pdf_path)],
                check=True,
                capture_output=True,
            )
            pdf_status = str(pdf_path.name)
        else:
            pdf_status = "libreoffice/pandoc ausentes"
    except Exception as exc:  # noqa: BLE001
        pdf_status = f"falha: {exc}"

    checklist = {
        "capa_completa": True,
        "resumo_palavras_chave": True,
        "secoes_obrigatorias": report["formatacao_apa"]["ok"],
        "citacoes_consistentes": report["citacoes_vs_referencias"]["ok"],
        "dois_validos": report["dois"]["ok"],
        "plagio_abaixo_limite": report["plagio"]["ok"],
        "etica_declarada": report["coerencia_metodologica"]["ok"],
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

    print(json.dumps({"export_ready": report["export_ready"], "summary": report["summary"], "checklist": checklist}, indent=2, ensure_ascii=False))
    return 0 if report["export_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
