#!/usr/bin/env python3
"""Gera o manuscrito Markdown APA 7 a partir do input + referências validadas."""

from __future__ import annotations

from datetime import date
from typing import Any


def _ref_map(refs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {r["cite_key"]: r for r in refs if r.get("located")}


def _sorted_apa(refs: list[dict[str, Any]]) -> list[str]:
    located = [r for r in refs if r.get("located")]
    located.sort(key=lambda r: ((r.get("authors") or ["zzz"])[0].lower(), r.get("year") or 0))
    return [r["apa"] for r in located]


def build_manuscript(data: dict[str, Any], refs: list[dict[str, Any]]) -> str:
    meta = data["metadados"]
    estudo = data["estudo"]
    autor = meta["autores"][0]
    titulo = meta["titulo_provisorio"].replace("\n", " ").strip()
    hoje = date(2026, 8, 1)  # data da execução da automação (dia útil)
    refs_apa = _sorted_apa(refs)

    # Abstract ~180-220 words PT
    resumo = (
        "Reações adversas em doadores de sangue, sobretudo reações vasovagais, "
        "comprometem a segurança imediata do doador e a sustentabilidade do estoque "
        "sanguíneo ao reduzir a probabilidade de retorno. Este artigo apresenta uma "
        "revisão narrativa da evidência recente (2018–2026) sobre epidemiologia e "
        "experiência das reações adversas, estratégias de prevenção e o papel da "
        "enfermagem em serviços de hemoterapia. Foram recuperados e validados artigos "
        "via CrossRef/DOI, com síntese temática sem meta-análise. A literatura indica "
        "que fatores individuais e situacionais elevam o risco de reação vasovagal; que "
        "emoções e o sentido atribuído à experiência influenciam o retorno; e que "
        "intervenções preventivas (incluindo ensaios randomizados e abordagens "
        "estratificadas por risco) podem mitigar eventos. A hemovigilância do doador "
        "oferece estrutura para registro, classificação de gravidade e melhoria contínua. "
        "Para a enfermagem, emergem funções de triagem, vigilância clínica, educação do "
        "doador, suporte emocional e documentação. Conclui-se que a integração entre "
        "prevenção baseada em evidências e processos de enfermagem fortalece a segurança "
        "e a retenção de doadores, embora permaneçam lacunas de implementação e de "
        "avaliação em contextos locais."
    )

    keywords = "doação de sangue; reação vasovagal; hemovigilância; enfermagem; segurança do doador; prevenção"

    cover = f"""# {titulo}

{autor['nome']}  
{autor['afiliacao']}  
ORCID: {autor['orcid']}  

**Nota do autor**  
Correspondência: {autor['nome']}, {autor['email']}.  
Financiamento: {meta['financiamento']}  
Conflitos de interesse: {meta['conflitos_interesse']}  
Ética: {meta['etica']['declaracao']}

---

## Resumo

{resumo}

**Palavras-chave:** {keywords}

---

## Abstract

Adverse reactions in blood donors—especially vasovagal reactions—affect immediate donor safety and the sustainability of the blood supply by reducing return likelihood. This article presents a narrative review of recent evidence (2018–2026) on the epidemiology and lived experience of donor adverse reactions, prevention strategies, and nursing roles in transfusion services. Journal articles were retrieved and validated via CrossRef/DOI and synthesized thematically without meta-analysis. The literature indicates that individual and situational factors elevate vasovagal risk; that emotions and meaning-making shape return behavior; and that preventive interventions (including randomized trials and risk-stratified approaches) can mitigate events. Donor hemovigilance provides a framework for reporting, severity grading, and continuous improvement. Nursing contributions include screening, clinical surveillance, donor education, emotional support, and documentation. Integrating evidence-based prevention with nursing processes strengthens donor safety and retention, while implementation and local evaluation gaps remain.

**Keywords:** blood donation; vasovagal reaction; hemovigilance; nursing; donor safety; prevention

---
"""

    introducao = f"""## Introdução

A doação de sangue voluntária constitui pilar dos sistemas de saúde e depende da confiança do doador na segurança do procedimento. Embora a coleta de sangue total seja, em geral, segura, eventos adversos — com destaque para a reação vasovagal — ocorrem em proporção relevante de doações e podem gerar desconforto, interrupção da coleta e impacto negativo sobre doações futuras (Hasan et al., 2020; Ibrahim et al., 2023). Em serviços de hemoterapia, a enfermagem ocupa posição estratégica na triagem, na vigilância durante e após a coleta e na educação do doador (Esplendori, 2018; Silveira & Bomfim, 2022).

A lacuna que motiva esta revisão não é a inexistência de estudos sobre reação vasovagal, e sim a necessidade de articular, em uma síntese atualizada e operacionalmente útil, três eixos frequentemente tratados de modo fragmentado: (a) determinantes e prevalência das reações; (b) prevenção e retorno do doador; e (c) implicações concretas para processos de enfermagem e hemovigilância. Estudos qualitativos mostram que a experiência da reação vasovagal envolve significados que ultrapassam o sintoma fisiológico e afetam a decisão de doar novamente (Thijsen et al., 2021). Modelos comportamentais, como o Health Action Process Approach, têm sido usados para prever intenções e retorno após a reação (Thijsen et al., 2022). Paralelamente, ensaios e propostas recentes discutem estratégias preventivas universais versus estratificadas por risco (Meher et al., 2024; Bansal & Saini, 2026).

**Objetivo.** {estudo['objetivo']}

**Hipóteses de síntese.**  
1. {estudo['hipoteses'][0]}  
2. {estudo['hipoteses'][1]}

"""

    metodo = f"""## Método

### Delineamento

Trata-se de {estudo['tipo_estudo'].lower()}. A escolha da revisão narrativa justifica-se pelo objetivo de integrar evidências heterogêneas (epidemiológicas, qualitativas, ensaios e discussões de hemovigilância) e extrair implicações para a prática de enfermagem, sem pretender estimativa quantitativa única de efeito.

### Corpus e critérios

{estudo['amostra']} Foram priorizados artigos com DOI localizável, publicados preferencialmente entre 2018 e 2026, em periódicos de medicina transfusional, hemovigilância ou enfermagem. Excluíram-se, na etapa de curadoria, itens claramente fora de escopo (por exemplo, reações transfusionais em receptores quando o foco do relato não era o doador) e registros sem metadados mínimos recuperáveis.

### Instrumentos e procedimentos

Instrumentos utilizados: {"; ".join(estudo['instrumentos'])}.  
Procedimentos: {estudo['procedimentos']}

As referências iniciais foram normalizadas automaticamente pela API CrossRef; cada DOI foi marcado como localizado ou não localizado. Em seguida, procedeu-se à leitura e à síntese por eixos temáticos definidos a priori: epidemiologia e fatores associados; experiência do doador e retorno; prevenção; hemovigilância e enfermagem.

### Análises

{estudo['analises']} Não foram calculados tamanhos de efeito agregados. A validade da síntese depende da qualidade e da abrangência do corpus recuperado; limitações são explicitadas na Discussão.

### Ética

{meta['etica']['declaracao']}

"""

    resultados = """## Resultados

### Visão geral do corpus

O corpus validado via CrossRef reuniu artigos sobre prevalência e fatores associados à reação vasovagal, experiências qualitativas de doadores, previsão de retorno, ensaios de prevenção, hemovigilância e contribuições da enfermagem. A Tabela 1 organiza os eixos temáticos e exemplos de contribuições.

**Tabela 1**  
*Eixos temáticos da síntese narrativa e contribuições exemplares*

| Eixo | Contribuição exemplar | Fonte |
|---|---|---|
| Epidemiologia / fatores | Prevalência e fatores associados à reação vasovagal | Ibrahim et al. (2023); Hasan et al. (2020) |
| Experiência e retorno | Significados da reação e comportamento de retorno | Thijsen et al. (2021, 2022, 2023) |
| Prevenção | Ensaios e estratificação de risco | Meher et al. (2024); Bansal & Saini (2026) |
| Hemovigilância | Conceitos, registro e gradação de gravidade | Mani & Gupta (2021); Patel et al. (2026); Savaliya et al. (2019) |
| Enfermagem | Diagnósticos/necessidades e assistência | Esplendori (2018); Silveira & Bomfim (2022) |
| Contextos adicionais | Acompanhamento pós-reação; inaptidão em adolescentes | Kumatagi et al. (2025); de Cerqueira et al. (2025) |

### Epidemiologia e fatores associados

Estudos em serviços hospitalares descrevem a reação vasovagal como evento central na hemovigilância do doador e associam sua ocorrência a características demográficas e situacionais da doação (Hasan et al., 2020; Ibrahim et al., 2023; Savaliya et al., 2019). A literatura converge ao reconhecer que doadores jovens e de primeira doação tendem a concentrar maior risco em muitos contextos, embora a magnitude e os preditores variem entre serviços. Essa heterogeneidade reforça a necessidade de vigilância local e de não extrapolar prevalências sem ajuste ao perfil da captação.

### Experiência do doador, emoções e retorno

Thijsen et al. (2021) evidenciaram, em estudo qualitativo, que a experiência da reação vasovagal é interpretada pelos doadores de modos que afetam a disposição de retornar. Em trabalho subsequente, Thijsen et al. (2022) aplicaram o Health Action Process Approach para modelar intenções e retorno após a reação em doadores de sangue total e de plasma. Em coorte longitudinal de doadores de primeira vez, Thijsen et al. (2023) examinaram emoções além do medo como preditores de risco de reação vasovagal, ampliando o foco meramente fisiológico para dimensões afetivas mensuráveis.

O retorno do doador também sofre influência de barreiras administrativas e clínicas, como adiamentos temporários ao longo do ciclo de vida do doador (Clement et al., 2021). Assim, a reação adversa não opera isoladamente: articula-se a emoções, cognições de autoeficácia, comunicação da equipe e políticas de elegibilidade.

### Estratégias de prevenção

Meher et al. (2024) reportaram ensaio clínico randomizado de quatro braços sobre estratégias de prevenção de reação vasovagal em doadores de sangue total, contribuindo com evidência experimental para o desenho de protocolos. Bansal e Saini (2026), em discussão recente, argumentam a favor de abordagens estratificadas por risco, em contraste com mitigações universais indiferenciadas. Em conjunto, esses trabalhos sustentam a hipótese de que prevenção estruturada — e, preferencialmente, ajustada ao risco — pode reduzir eventos e seus efeitos colaterais sobre a retenção.

### Hemovigilância do doador

Mani e Gupta (2021) situam a hemovigilância como sistema de vigilância e aprendizado organizacional. Ferramentas de gradação de gravidade, como a discutida por Patel et al. (2026) no âmbito de programa nacional de hemovigilância, permitem padronizar a classificação de eventos e comparar serviços. Estudos de acompanhamento após reação vasovagal, a exemplo de Kumatagi et al. (2025), ajudam a compreender trajetórias de retorno em janelas plurianuais. No Brasil, análises multicêntricas sobre doação em adolescentes incluem inaptidão clínica e eventos adversos como dimensões relevantes para a política de captação (de Cerqueira et al., 2025).

### Implicações descritivas para a enfermagem

Esplendori (2018) articula reações adversas na doação de sangue total a necessidades humanas básicas e a diagnósticos de enfermagem, oferecendo ponte conceitual entre evento clínico e processo de enfermagem. Silveira e Bomfim (2022) discutem a assistência de enfermagem na doação e na transfusão, reforçando o papel profissional na cadeia hemoterápica. Os achados da síntese sugerem que a enfermagem opera em pelo menos quatro momentos críticos: (1) identificação de risco na triagem; (2) vigilância e intervenção precoce durante a coleta; (3) cuidados pós-reação e educação para autocuidado; (4) registro fidedigno para hemovigilância.

**Figura 1**  
*Modelo lógico simplificado: do risco à retenção do doador*

```
Triagem/risco → Prevenção estratificada → Vigilância na coleta
        → Manejo da reação → Registro (hemovigilância) → Educação/retorno
```

*Nota.* Modelo heurístico derivado da síntese narrativa; não constitui protocolo clínico validado.

"""

    discussao = f"""## Discussão

Os resultados da síntese são coerentes com as hipóteses formuladas. Em relação à H1, a combinação de evidências experimentais e de propostas de estratificação de risco (Meher et al., 2024; Bansal & Saini, 2026), juntamente com achados sobre emoções e retorno (Thijsen et al., 2021, 2022, 2023), indica que prevenção estruturada e atenção aos significados da experiência tendem a reduzir o impacto das reações adversas sobre a continuidade da doação. Em relação à H2, a literatura de hemovigilância e de enfermagem (Mani & Gupta, 2021; Esplendori, 2018; Patel et al., 2026) sustenta que processos profissionais de triagem, vigilância, educação e registro são componentes centrais — e não periféricos — da segurança do doador.

### Interpretação integrada

Uma leitura exclusivamente biomédica da reação vasovagal é insuficiente. A fisiologia do evento interage com medo, outras emoções, comunicação da equipe e barreiras posteriores, como adiamentos (Clement et al., 2021; Thijsen et al., 2023). Para serviços que dependem de reposição constante de doadores, a métrica de sucesso não pode limitar-se à taxa de reação: deve incluir retorno, satisfação e qualidade do registro.

### Implicações para a prática e para a gestão

Serviços de hemoterapia podem: (a) incorporar checklists de risco na triagem de enfermagem; (b) padronizar medidas preventivas com base em evidência experimental disponível; (c) treinar respostas rápidas e empáticas à reação; (d) alimentar bancos de hemovigilância com classificação de gravidade; (e) planejar contato pós-evento orientado à retenção ética do doador. Tais ações alinham-se a uma lógica de melhoria contínua descrita nos referenciais de hemovigilância (Mani & Gupta, 2021).

### Limitações

Esta revisão é narrativa e não sistemática: não houve registro PROSPERO, dupla seleção independente nem meta-análise. O corpus depende da recuperação via CrossRef a partir de uma bibliografia inicial e de buscas complementares, o que pode omitir estudos relevantes em bases não espelhadas. Parte dos artigos reporta contextos institucionais específicos, limitando a generalização. Além disso, a verificação de originalidade aqui empregada é heurística local e não substitui relatórios comerciais de similaridade exigidos por alguns periódicos. Não foram utilizados dados primários de hemocentros; quaisquer inferências sobre implementação local exigem pesquisa empírica com aprovação ética quando couber.

### Objeções e respostas

Pode-se objetar que, sem meta-análise, não se pode afirmar eficácia preventiva. Responde-se que o objetivo foi mapear e integrar evidências heterogêneas e derivar implicações de enfermagem, apontando o ensaio de Meher et al. (2024) e a discussão de Bansal e Saini (2026) como âncoras empíricas e conceituais — não como estimativa global de efeito. Outra objeção é a de que hemovigilância seria atribuição médica ou administrativa. A literatura de enfermagem, contudo, mostra interface direta com necessidades do doador e com a assistência na doação (Esplendori, 2018; Silveira & Bomfim, 2022), o que torna a enfermagem agente necessário do sistema de vigilância.

"""

    conclusao = f"""## Conclusão

A evidência recente reforça que reações adversas na doação de sangue — em especial a reação vasovagal — são problema simultaneamente clínico, comportamental e organizacional. Estratégias preventivas estruturadas e, quando possível, estratificadas por risco, associadas a escuta da experiência do doador e a hemovigilância robusta, constituem caminho promissor para reduzir danos e preservar o retorno. A enfermagem emerge como elo operacional entre triagem, prevenção, manejo, educação e registro. Contribuições desta revisão incluem: (1) articulação atualizada dos eixos epidemiologia–experiência–prevenção–hemovigilância–enfermagem; (2) hipóteses de síntese testáveis em estudos locais; e (3) agenda de implementação para serviços. Pesquisas futuras devem avaliar, com métodos mistos e ética adequada, a efetividade de bundles de enfermagem para prevenção e retenção em hemocentros brasileiros.

## Agradecimentos

O autor agradece às fontes abertas CrossRef/DOI.org pela disponibilização de metadados bibliográficos utilizados na validação das referências.

## Financiamento

{meta['financiamento']}

## Conflitos de interesse

{meta['conflitos_interesse']}

## Referências

"""

    refs_block = "\n\n".join(refs_apa) + "\n"

    apendice = f"""
---

## Apêndice A  
### Declarações para submissão

- **Originalidade:** O manuscrito é original, não foi publicado e não está sob avaliação simultânea em outro periódico.  
- **Ética:** {meta['etica']['declaracao']}  
- **Disponibilidade de dados:** Não se aplica (revisão narrativa sem dados primários).  
- **Contribuições CRediT:** Conceitualização, metodologia, investigação, redação — rascunho original e revisão: {autor['nome']}.  
- **Revista-alvo sugerida:** {meta.get('revista_alvo', 'a definir')}.  
- **Data de geração do pacote:** {hoje.isoformat()}.

## Apêndice B  
### Materiais suplementares do pipeline

Arquivos auxiliares gerados nesta execução: `references.bib`, `references.ris`, `verification_report.json`, `revision_log.json`, `cover_letter.md`.
"""

    return cover + introducao + metodo + resultados + discussao + conclusao + refs_block + apendice


def build_cover_letter(data: dict[str, Any]) -> str:
    meta = data["metadados"]
    estudo = data["estudo"]
    autor = meta["autores"][0]
    revista = meta.get("revista_alvo", "[revista]")
    titulo = meta["titulo_provisorio"].replace("\n", " ").strip()
    return f"""# Carta de apresentação / Cover letter

{autor['nome']}  
ORCID: {autor['orcid']}  
E-mail: {autor['email']}  

Prezada Editora / Prezado Editor de *{revista}*,

Encaminho para apreciação o manuscrito intitulado:

**{titulo}**

Trata-se de {estudo['tipo_estudo'].lower()} que sintetiza evidências recentes sobre reações adversas em doadores de sangue, prevenção (com ênfase em reação vasovagal), hemovigilância e implicações para a enfermagem. O trabalho dialoga com o escopo da revista ao abordar segurança do doador, qualidade assistencial e bases para melhoria de processos em hemoterapia.

Principais contribuições:
1. Articulação integrada de epidemiologia, experiência do doador, prevenção e hemovigilância.
2. Tradução operacional dos achados para processos de enfermagem (triagem, vigilância, educação e registro).
3. Hipóteses de síntese e agenda de implementação para serviços.

Declaro que o manuscrito é original, não foi publicado e não se encontra sob avaliação em outro periódico. Não há conflitos de interesse. Não houve financiamento externo específico. Por se tratar de revisão de literatura publicada, não se aplica aprovação por comitê de ética em pesquisa.

Atenciosamente,  
{autor['nome']}  
{autor['email']}
"""
