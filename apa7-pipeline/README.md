# Pipeline APA 7 — Artigo científico automatizado

Automação mensal para gerar manuscritos no padrão **APA 7ª edição**, validar referências (CrossRef/DOI), checar consistência citação↔referência, coerência metodológica, originalidade heurística e exportar pacote de submissão.

## Estrutura

```
apa7-pipeline/
├── data/
│   ├── estudo_input.yaml          # Entrada do estudo (editar aqui)
│   └── references_validated.json  # Metadados CrossRef (gerado)
├── prompts/
│   └── modular_prompts.md         # Prompts seção-a-seção
├── templates/
│   └── checklist_exportacao.md
├── scripts/
│   ├── run_pipeline.py            # Orquestrador
│   ├── crossref_validate.py
│   ├── generate_manuscript.py
│   ├── verify_article.py
│   └── export_formats.py
└── output/                        # Artefatos gerados
```

## Como executar

```bash
cd apa7-pipeline
# 1) Edite data/estudo_input.yaml
# 2) Rode o pipeline
python3 scripts/run_pipeline.py
```

Dependências: `python-docx`, `requests`, `pyyaml`. PDF opcional via LibreOffice (`libreoffice --headless --convert-to pdf …docx`).

## Saídas esperadas (`output/`)

| Arquivo | Descrição |
|---|---|
| `artigo_apa7_*.md` | Manuscrito Markdown |
| `artigo_apa7_*.docx` | Manuscrito formatado (Times, espaço duplo, margens 1") |
| `artigo_apa7_*.pdf` | PDF (se LibreOffice/pandoc+TeX disponível) |
| `references.bib` / `references.ris` | Bibliografia exportável |
| `verification_report.json` | Plágio heurístico, DOIs, citações, APA, método |
| `revision_log.json` | Histórico de versões |
| `cover_letter.md` | Carta de apresentação |
| `export_checklist.json` | Checklist pré-exportação |

## Regras automáticas

- Citações autor–ano; 3+ autores → `et al.` desde a primeira citação (APA 7)
- DOI obrigatório quando disponível (validado na CrossRef)
- Similaridade heurística > 15% → sinaliza revisão humana
- Participantes humanos/animais → exige declaração ética
- Exportação só marcada `export_ready: true` se todas as checagens críticas passarem
- A verificação de similaridade é **heurística local** e **não substitui** Turnitin/iThenticate

## Execução 2026-09-01

Artigo gerado: *Motivação, retenção e fidelização de doadores de sangue: implicações para a enfermagem em serviços de hemoterapia*

Autor: Antonio Augusto Dornelas de Andrade (ORCID [0009-0001-3556-483X](https://orcid.org/0009-0001-3556-483X)).

Tema distinto da demonstração de 2026-08-01 (reações adversas / vasovagal) e do manuscrito de esquizofrenia.

## Execução de demonstração (2026-08-01)

Artigo: *Reações adversas na doação de sangue e o papel da enfermagem: revisão narrativa da evidência recente* (branch `cursor/artigo-cient-fico-apa-7-42c4`).
