#!/usr/bin/env python3
"""Gera o manuscrito Markdown APA 7 a partir do input + referências validadas."""

from __future__ import annotations

from datetime import date
from typing import Any

DOI = {
    "bagot": "10.1016/j.tmrv.2016.02.002",
    "bednall2011": "10.1016/j.tmrv.2011.04.005",
    "bednall2013": "10.1016/j.socscimed.2013.07.022",
    "hashemi": "10.1111/trf.15404",
    "wevers": "10.1111/vox.12189",
    "asamoah": "10.1111/vox.13026",
    "swanevelder": "10.1111/trf.15436",
    "ferguson": "10.1111/j.1537-2995.2007.01423.x",
    "masser": "10.1111/j.1537-2995.2008.01981.x",
    "dongen2012": "10.1111/j.1537-2995.2012.03810.x",
    "giacomini": "10.1590/s0103-21002010000100011",
    "germain": "10.1111/j.1537-2995.2007.01409.x",
    "dongen2015": "10.1111/tme.12249",
    "zago": "10.1590/s0034-89102010000100012",
    "gemelli": "10.1111/trf.13874",
    "godin": "10.1111/j.1537-2995.2007.01331.x",
    "conceicao": "10.1016/j.bjhh.2016.05.006",
}


def _norm_doi(doi: str) -> str:
    return doi.strip().removeprefix("https://doi.org/").removeprefix("http://doi.org/").lower()


def _index(refs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_doi = {_norm_doi(r["doi"]): r for r in refs if r.get("located") and r.get("doi")}
    out: dict[str, dict[str, Any]] = {}
    for key, doi in DOI.items():
        ref = by_doi.get(_norm_doi(doi))
        if ref is None:
            raise KeyError(f"DOI não localizado para a chave {key}: {doi}")
        out[key] = ref
    return out


def _family(author_apa: str) -> str:
    fam = author_apa.split(",")[0].strip()
    for dash in ("\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2212"):
        fam = fam.replace(dash, "-")
    if fam:
        return fam[0].upper() + fam[1:]
    return fam


def intext(ref: dict[str, Any], kind: str = "p") -> str:
    """Citação APA 7: p=parentética, n=narrativa, y=ano."""
    authors = ref.get("authors") or ["Anonymous"]
    year = ref.get("year") or "n.d."
    n = len(authors)
    f0 = _family(authors[0])
    if n == 1:
        name_p = name_n = f0
    elif n == 2:
        f1 = _family(authors[1])
        name_p = f"{f0} & {f1}"
        name_n = f"{f0} e {f1}"
    else:
        name_p = name_n = f"{f0} et al."
    if kind == "p":
        return f"({name_p}, {year})"
    if kind == "n":
        return f"{name_n} ({year})"
    if kind == "y":
        return str(year)
    raise ValueError(kind)


def join_p(*ref_list: dict[str, Any]) -> str:
    inner = "; ".join(intext(ref, "p")[1:-1] for ref in ref_list)
    return f"({inner})"


def _sorted_apa(refs: list[dict[str, Any]]) -> list[str]:
    located = [r for r in refs if r.get("located")]
    located.sort(key=lambda r: ((r.get("authors") or ["zzz"])[0].lower(), r.get("year") or 0))
    return [r["apa"] for r in located]


def build_manuscript(data: dict[str, Any], refs: list[dict[str, Any]]) -> str:
    meta = data["metadados"]
    estudo = data["estudo"]
    autor = meta["autores"][0]
    titulo = " ".join(meta["titulo_provisorio"].split())
    hoje = date(2026, 9, 1)
    r = _index(refs)
    refs_apa = _sorted_apa(refs)

    resumo = (
        "A sustentabilidade do estoque de sangue depende da conversão da primeira "
        "doação em uma sequência de retornos, e não apenas da captação de novatos. "
        "Este artigo apresenta revisão narrativa de evidências indexadas, com DOIs "
        "validados na CrossRef, sobre motivadores e barreiras da doação, preditores "
        "de retorno, intervenções de retenção e implicações para a enfermagem em "
        "serviços de hemoterapia. Revisões sistemáticas e meta-análises organizam "
        "motivadores pró-sociais, valores pessoais e conveniência, ao lado de "
        "barreiras como medo, baixa autoeficácia, inconveniência, experiência "
        "negativa de serviço e adiamentos. Modelos sociocognitivos, sobretudo a "
        "teoria do comportamento planejado, explicam intenção com mais consistência "
        "do que o comportamento observado. A janela da primeira doação é crítica: "
        "parcela substancial dos novatos não retorna. Estudos de campo e ensaios "
        "indicam ganhos de retorno com cartas emocionais ou educativas, lembretes e "
        "com a combinação de intenções de implementação e compromisso explícito, "
        "ao passo que incentivos materiais e reuniões motivacionais genéricas "
        "tendem a efeitos menores. No Brasil, dados de prevalência, percepções de "
        "doadores e estratégias de fidelização descritas pela enfermagem convergem "
        "para educação, desconstrução de medos e qualidade do acolhimento. A retenção "
        "é, portanto, problema simultaneamente comportamental e organizacional, no "
        "qual a enfermagem media o encontro que torna a doação repetível."
    )

    keywords = (
        "doação de sangue; retenção de doadores; motivação; fidelização; "
        "enfermagem; hemoterapia"
    )

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

Blood-supply sustainability depends on converting a first donation into repeated return, not merely on recruiting new donors. This article presents a narrative review of indexed evidence, with DOIs validated via CrossRef, on donation motivators and barriers, predictors of return, retention interventions, and implications for nursing in transfusion services. Systematic reviews and meta-analyses organize prosocial motives, personal values, and convenience alongside barriers such as fear, low self-efficacy, inconvenience, negative service experience, and deferral. Social-cognitive models, especially the theory of planned behavior, explain intention more consistently than observed behavior. The first-donation window is critical: a substantial share of novices never return. Field studies and trials show return gains from emotional or educational letters, reminders, and the combination of implementation intentions with explicit commitment, whereas material incentives and generic motivational meetings tend to smaller effects. In Brazil, prevalence data, donor perceptions, and nursing descriptions of loyalty-building converge on education, demystifying fear, and the quality of reception. Retention is therefore both a behavioral and an organizational problem, in which nursing mediates the encounter that makes donation repeatable.

**Keywords:** blood donation; donor retention; motivation; donor loyalty; nursing; transfusion medicine

---
"""

    introducao = f"""## Introdução

Sistemas de sangue baseados em doação voluntária não remunerada enfrentam um descompasso persistente entre a população elegível e o conjunto efetivo de doadores ativos. A revisão de {intext(r['bagot'], 'n')} observou que apenas cerca de 5% dos elegíveis doam e que aproximadamente metade daqueles que realizam a primeira doação não retornam. Esse padrão desloca o problema do abastecimento da mera captação para a retenção: sem carreira de doações repetidas, os serviços permanecem dependentes de fluxos instáveis de novatos e de campanhas emergenciais.

A psicologia da doação acumulou, nas duas últimas décadas, taxonomias de motivadores e barreiras {intext(r['bednall2011'], 'p')}, sínteses quantitativas de antecedentes da intenção e do comportamento {intext(r['bednall2013'], 'p')} e propostas de integração entre agendas da ciência social e da prática dos serviços {intext(r['ferguson'], 'p')}. Em paralelo, a teoria do comportamento planejado (TCP) foi testada em doadores australianos para prever intenção e comportamento {intext(r['masser'], 'p')}, e comparações entre doadores novos e experientes esclareceram determinantes da repetição {intext(r['godin'], 'p')}. O que permanece menos articulado, sobretudo em língua portuguesa e com vocabulário de processo de enfermagem, é o modo como essas evidências se traduzem em trabalho cotidiano de acolhimento, educação, experiência de serviço e seguimento.

A lacuna que orienta esta revisão não é a ausência de estudos sobre motivação. É a fragmentação entre (a) sínteses internacionais de preditores e intervenções, (b) evidência empírica sobre a janela da primeira doação e o lapso de doadores frequentes, e (c) a literatura brasileira de enfermagem e de saúde coletiva sobre fidelização e percepções da doação. Sem essa articulação, protocolos de captação tendem a tratar a enfermagem como suporte técnico da coleta, e não como mediadora do encontro que decide o retorno.

**Objetivo.** {estudo['objetivo']}

**Hipóteses de síntese.**
1. {estudo['hipoteses'][0]}
2. {estudo['hipoteses'][1]}

"""

    metodo = f"""## Método

### Delineamento

Trata-se de {estudo['tipo_estudo'].lower()}. A revisão narrativa foi escolhida porque o objeto reúne desenhos heterogêneos — meta-análises, ensaios de campo, inquéritos, coortes de retorno e estudos qualitativos de enfermagem — cujo valor para a prática não se reduz a um tamanho de efeito único.

### Corpus e critérios

{estudo['amostra']} Incluíram-se itens com DOI localizável cuja contribuição recaísse sobre motivação, intenção, retorno, lapso, intervenções de retenção, percepções da doação ou estratégias de fidelização descritas pela enfermagem. Excluíram-se, na curadoria, trabalhos centrados exclusivamente em reações transfusionais de receptores, em aspectos laboratoriais da unidade de sangue ou em temas clínicos sem nexo com o comportamento de doar.

A bibliografia inicial foi fixada a priori no arquivo de entrada do pipeline e validada na API CrossRef. Não se pretendeu exaustividade de bases (não houve estratégia PRISMA nem registro PROSPERO). O recorte privilegia periódicos de medicina transfusional, ciência social da saúde e enfermagem com metadados recuperáveis.

### Instrumentos e procedimentos

Instrumentos: {"; ".join(estudo['instrumentos'])}.
Procedimentos: {estudo['procedimentos']}

A síntese foi organizada em sete eixos definidos antes da redação: (1) magnitude do problema de retenção; (2) taxonomia de motivadores e barreiras; (3) modelos sociocognitivos; (4) janela da primeira doação; (5) evidência de intervenções; (6) lapso de doadores já inseridos no serviço; (7) contexto brasileiro e implicações de enfermagem.

### Análises

{estudo['analises']} A validade da síntese depende da abrangência do corpus e da fidelidade aos achados publicados; limitações são explicitadas na Discussão.

### Ética

{meta['etica']['declaracao']}

"""

    resultados = f"""## Resultados

### Magnitude do problema e lógica da carreira do doador

{intext(r['bagot'], 'n')} situaram a retenção do doador de primeira vez como problema de sistema: a baixa penetração da doação na população elegível combina-se a elevada perda após a estreia. {intext(r['dongen2015'], 'n')}, em ensaio de revisão intitulado de modo programático *Easy come, easy go*, argumentou que a facilidade relativa de recrutar não se traduz automaticamente em permanência, o que exige desenho deliberado de retenção. Esse diagnóstico reorienta indicadores: taxa de captação isolada superestima a saúde do painel se o retorno de novatos e a prevenção de lapso não forem medidos.

A comparação entre doadores atuais e doadores em lapso mostra que o abandono não é ruído residual. {intext(r['germain'], 'n')} examinaram determinantes do comportamento de retorno contrastando esses dois grupos, evidenciando que variáveis de experiência com o serviço e de percepção do ato de doar separam quem permanece de quem se afasta. Entre doadores já frequentes, {intext(r['gemelli'], 'n')} descreveram o subgrupo de alta frequência e identificaram preditores de lapso, o que desloca a agenda da captação para a manutenção de carreiras longas.

**Tabela 1**
*Eixos da síntese e âncoras empíricas do corpus*

| Eixo | Questão central | Âncoras |
|---|---|---|
| Magnitude e carreira | Por que retenção é problema de abastecimento? | Bagot et al. ({intext(r['bagot'], 'y')}); Van Dongen ({intext(r['dongen2015'], 'y')}) |
| Motivadores e barreiras | O que inicia, sustenta ou interrompe a doação? | Bednall e Bove ({intext(r['bednall2011'], 'y')}); Bednall et al. ({intext(r['bednall2013'], 'y')}) |
| Modelos sociocognitivos | Como intenção se liga (ou não) ao retorno? | Masser et al. ({intext(r['masser'], 'y')}); Godin et al. ({intext(r['godin'], 'y')}); Ferguson et al. ({intext(r['ferguson'], 'y')}) |
| Primeira doação | Quais fatores predizem o segundo ato? | Hashemi et al. ({intext(r['hashemi'], 'y')}); Wevers et al. ({intext(r['wevers'], 'y')}); Swanevelder et al. ({intext(r['swanevelder'], 'y')}); Asamoah-Akuoko et al. ({intext(r['asamoah'], 'y')}) |
| Lapso | O que afasta doadores já inseridos? | Germain et al. ({intext(r['germain'], 'y')}); Gemelli et al. ({intext(r['gemelli'], 'y')}); Van Dongen et al. ({intext(r['dongen2012'], 'y')}) |
| Brasil e enfermagem | Como o encontro assistencial organiza fidelização? | Zago et al. ({intext(r['zago'], 'y')}); Giacomini e Lunardi Filho ({intext(r['giacomini'], 'y')}); Conceição et al. ({intext(r['conceicao'], 'y')}) |

### Taxonomia de motivadores e barreiras

{intext(r['bednall2011'], 'n')} sintetizaram, em meta-análise de autorrelato, categorias de motivadores e de barreiras aplicáveis a doadores de primeira vez, repetidores, em lapso, de aférese e não doadores elegíveis. Entre motivadores, doadores iniciantes e repetidores citaram com frequência conveniência, motivação pró-social e valores pessoais; doadores em lapso enfatizaram reputação da agência coletora, necessidade percebida, comunicação de marketing e incentivos. Entre barreiras, doadores e não doadores recorreram a baixa autoeficácia, baixo envolvimento, inconveniência, ausência de comunicação, incentivos ineficazes, falta de conhecimento, experiências negativas de serviço e medo.

Essa taxonomia tem duas consequências analíticas. Primeira: o mesmo indivíduo atravessa estágios em que o peso relativo dos fatores muda; tratar “o doador” como tipo único distorce intervenção. Segunda: barreiras de serviço (fila, trato, informação) não são epifenômenos psicológicos — são atributos organizacionais mensuráveis. A meta-análise subsequente de {intext(r['bednall2013'], 'n')} consolidou antecedentes da intenção e do comportamento, reforçando que construtos sociocognitivos e condições situacionais devem ser lidos em conjunto, e não como listas rivais.

### Modelos sociocognitivos: intenção, controle percebido e repetição

{intext(r['ferguson'], 'n')} defenderam a integração de avanços teóricos das ciências sociais e comportamentais às agendas de recrutamento e retenção, contra o empirismo de campanhas isoladas. No teste de um modelo estendido da TCP, {intext(r['masser'], 'n')} mostraram que atitudes, norma subjetiva e controle comportamental percebido organizam a intenção de doar entre doadores australianos, com implicações para mensagens que visem crenças específicas em vez de apelos genéricos à solidariedade.

{intext(r['godin'], 'n')} compararam determinantes da doação repetida entre doadores novos e experientes, indicando que o peso dos preditores não é idêntico ao longo da carreira. Esse achado dialoga com a observação de {intext(r['bagot'], 'n')} de que intenção prediz retenção de novatos, sendo ela própria alimentada por atitudes e por senso de controle. A lacuna clássica intenção–comportamento permanece: intenção elevada não garante retorno se ansiedade, evento adverso, adiamento ou serviço ruim interromperem a cadeia.

Eventos adversos e angústia subjetiva entram aqui como perturbadores da carreira, não como tema clínico autônomo. {intext(r['dongen2012'], 'n')} demonstraram influência de reações adversas, sofrimento subjetivo e ansiedade sobre a retenção de doadores de primeira vez. O ponto para a presente síntese é organizacional: prevenção e acolhimento pós-evento são instrumentos de retenção, além de deveres de segurança.

### A janela da primeira doação: preditores de retorno real

Quatro estudos do corpus medem retorno ou intenção de retorno em novatos, em contextos nacionais distintos, o que impede média única, mas permite convergências.

{intext(r['hashemi'], 'n')} conduziram ensaio de campo com 1.356 doadores de primeira vez em quatro centros no Irã, alocados a carta emocional, carta educativa, lembrete telefônico, incentivo, reunião motivacional ou ausência de intervenção. O retorno em seis meses foi de 29% no conjunto (intervalo de confiança de 95%: 0,26–0,31). As taxas por braço foram 36% (carta emocional), 33,2% (carta educativa), 31,5% (telefone), 30% (incentivo), 22% (reunião motivacional) e 22,1% (controle). Cartas e telefone superaram o controle; a reunião motivacional não se distinguiu dele.

{intext(r['wevers'], 'n')} testaram, em 937 doadores recém-registrados, uma folha adicional no exame médico com intenções de implementação e/ou compromisso explícito. A condição que combinou as duas técnicas apresentou retorno 11,5 pontos percentuais acima do controle, com razão de chances de 1,65 (intervalo de confiança de 95%: 1,08–2,50). O achado importa porque a intervenção é breve, de baixo custo e inserível no fluxo já existente de triagem.

{intext(r['swanevelder'], 'n')} acompanharam 2.902 doadores de primeira vez de origem africana na África do Sul. Em um ano, 54% tentaram ao menos uma nova doação. Concordância forte com o enunciado de que doar é um modo fácil de fazer diferença (OR 2,0; IC 95%: 1,3–2,9) e ter doado em resposta a anúncios (OR 1,6; IC 95%: 1,2–2,1) associaram-se ao retorno; mau atendimento ao “cliente” associou-se a não retorno (OR 0,45; IC 95%: 0,28–0,71). O estudo liga motivador pró-social, comunicação de massa e qualidade do serviço a comportamento observado, não apenas a intenção.

{intext(r['asamoah'], 'n')} investigaram intenção de retorno em 505 doadores de primeira vez em Gana. Preditores positivos incluíram incentivos motivacionais (OR 1,67), facilidade de acesso ao local (OR 2,65), lembretes por SMS ou e-mail (OR 2,84) e anúncios em televisão, rádio ou jornal (OR 2,97). Preditores negativos incluíram acesso preferencial a transfusões (“créditos de sangue”), desejo de conhecer resultados de testes e desconhecimento ou desconfiança sobre o destino do sangue após a doação. Transparência sobre o uso do sangue e recusa de contraprestações ambíguas aparecem, assim, como temas éticos com efeito comportamental.

**Tabela 2**
*Intervenções e preditores de retorno na janela da primeira doação (achados reportados pelas fontes)*

| Estudo | Desenho e N | Desfecho | Resultado principal reportado |
|---|---|---|---|
| Hashemi et al. ({intext(r['hashemi'], 'y')}) | Ensaio de campo; 1.356 novatos | Retorno em 6 meses | Cartas emocional/educativa e telefone > controle; reunião motivacional ≈ controle |
| Wevers et al. ({intext(r['wevers'], 'y')}) | Experimento; 937 recém-registrados | Primeiro retorno | Intenção de implementação + compromisso: OR 1,65 vs. controle |
| Swanevelder et al. ({intext(r['swanevelder'], 'y')}) | Coorte; 2.902 novatos | Tentativa de retorno em 1 ano | 54% retornaram; pró-socialidade e anúncios predizem retorno; mau serviço prediz não retorno |
| Asamoah-Akuoko et al. ({intext(r['asamoah'], 'y')}) | Transversal; 505 novatos | Intenção de retorno em 4 meses | Acesso, lembretes e mídia elevam intenção; opacidade do destino do sangue a reduz |

A síntese da Tabela 2 sustenta H1 de modo convergente, não meta-analítico: comunicação personalizada, lembretes e técnicas de planejamento do comportamento superam, nos estudos disponíveis, tanto o nada fazer quanto formatos motivacionais genéricos. Incentivos materiais ocupam posição intermediária e contextualmente instável.

### Lapso após a inserção no serviço

Retenção não se esgota no segundo ato. {intext(r['germain'], 'n')} mostraram que doadores em lapso diferem de doadores atuais em determinantes do retorno, o que recomenda reconquista distinta da captação de nunca-doadores. {intext(r['gemelli'], 'n')} caracterizaram doadores frequentes de sangue total e preditores de lapso, lembrando que o painel “fiel” também se desgasta por adiamentos, mudança de vida, cansaço da rotina ou falha de convite no intervalo certo.

A revisão de {intext(r['dongen2015'], 'n')} reuniu essa trajetória sob a fórmula da entrada fácil e da saída igualmente fácil. Combinada a {intext(r['dongen2012'], 'p')}, a mensagem operacional é que o serviço deve gerir três rupturas: a que ocorre imediatamente após a estreia, a que se segue a um evento aversivo e a que se instala silenciosamente em carreiras longas.

### Contexto brasileiro: prevalência, percepções e enfermagem

{intext(r['zago'], 'n')} estimaram prevalência de doação de sangue e fatores associados em Pelotas, no Rio Grande do Sul, oferecendo âncora populacional brasileira: doar não é hábito majoritário, e associações sociodemográficas importam para o desenho de captação territorial. Sem pretender atualizar a prevalência daquele inquérito, o estudo permanece útil como evidência de que barreiras e diferenciais sociais se observam também em município brasileiro com tradição de pesquisa epidemiológica.

{intext(r['conceicao'], 'n')} examinaram percepções de doadores e de receptores sobre a doação, evidenciando que o significado do ato não é idêntico nos dois polos da cadeia e que esclarecer o destino e o valor do sangue pode reduzir opacidade — tema que reaparece, em outro país, nos preditores negativos de {intext(r['asamoah'], 'n')}.

{intext(r['giacomini'], 'n')} investigaram estratégias de fidelização na perspectiva da enfermagem. Os entrevistados atribuíram o baixo número de doadores voluntários sobretudo a medos e preconceitos (passar mal, contaminação), à falta de conhecimento sobre o processo e a uma cultura que pouco elabora o tema. As estratégias propostas concentram-se em educação, desconstrução de temores e construção de vínculo, o que alinha o discurso profissional brasileiro aos achados internacionais sobre serviço, informação e autoeficácia {join_p(r['bednall2011'], r['swanevelder'])}.

### Implicações descritivas para o processo de enfermagem

A leitura conjunta do corpus autoriza descrever quatro momentos em que a enfermagem incide sobre a probabilidade de retorno, sem transformar a síntese em protocolo clínico validado.

**Tabela 3**
*Momentos do processo de enfermagem com nexo de retenção derivado da síntese*

| Momento | Ação de enfermagem | Nexo com a evidência |
|---|---|---|
| Antes da coleta | Acolhimento, informação sobre o processo, redução de medo e de opacidade | Barreiras de conhecimento e medo {join_p(r['bednall2011'], r['giacomini'])}; desconfiança quanto ao destino do sangue {intext(r['asamoah'], 'p')} |
| Durante a triagem | Convite a um plano concreto de retorno (quando e como) | Intenção de implementação e compromisso {intext(r['wevers'], 'p')}; controle percebido {intext(r['masser'], 'p')} |
| Após a doação | Avaliação da experiência de serviço e contato breve educativo ou emocional | Cartas e telefone {intext(r['hashemi'], 'p')}; qualidade do atendimento {intext(r['swanevelder'], 'p')} |
| Ao longo da carreira | Lembretes, reconquista de lapsos e vigilância de preditores de abandono | Lembretes {intext(r['asamoah'], 'p')}; lapso {join_p(r['germain'], r['gemelli'])} |

**Figura 1**
*Modelo lógico da retenção: da estreia à carreira*

```
Elegibilidade → Primeira doação → Experiência de serviço/educação
        → Intenção e plano de retorno → Segunda doação
        → Manutenção (convite no intervalo; prevenção de lapso)
```

*Nota.* Esquema heurístico derivado da síntese narrativa; não constitui diretriz assistencial.

O modelo da Figura 1 torna visível H2: a enfermagem não aparece apenas no instante da punção, e sim nos nós em que informação, plano, experiência e seguimento se decidem.

"""

    discussao = f"""## Discussão

Os eixos da síntese são coerentes com as hipóteses. Quanto à H1, a evidência de campo de {intext(r['hashemi'], 'n')} e o experimento de {intext(r['wevers'], 'n')} mostram que intervenções estruturadas — comunicação escrita com conteúdo emocional ou educativo, lembrete telefônico e a dupla intenção de implementação plus compromisso — elevam o retorno de novatos acima do controle, ao passo que reunião motivacional genérica não o fez no ensaio iraniano. A revisão de {intext(r['bagot'], 'n')} já havia relativizado o efeito de lembretes e incentivos tradicionais e destacado o peso de suporte psicológico individualizado; o corpus posterior não anula essa cautela, mas especifica formatos de baixo custo que funcionam melhor do que o apelo indiferenciado.

Quanto à H2, {intext(r['swanevelder'], 'n')} associaram mau atendimento a não retorno, {intext(r['bednall2011'], 'n')} incluíram experiência negativa de serviço na taxonomia de barreiras, e {intext(r['giacomini'], 'n')} descreveram a enfermagem como agente de educação e de vínculo. Esses achados não “provam” mediação estatística no sentido de análise de caminhos; sustentam, como hipótese de síntese, que o encontro assistencial é mecanismo organizacional da retenção.

### Interpretação integrada

Três tensões organizam a leitura. A primeira é entre altruísmo declarado e arquitetura da ação. Motivação pró-social é onipresente no autorrelato {join_p(r['bednall2011'], r['swanevelder'])}, mas o retorno sobe quando o serviço reduz fricção (acesso, lembrete, plano concreto) {join_p(r['wevers'], r['asamoah'])}. Solidariedade sem desenho de implementação permanece intenção.

A segunda tensão é entre captação e carreira. Métricas de “novos doadores” podem mascarar rotatividade alta {join_p(r['bagot'], r['dongen2015'])}. Doadores frequentes também lapsam {intext(r['gemelli'], 'p')}, o que exige fila de trabalho específica de manutenção, distinta da campanha de rua.

A terceira tensão é ética e comunicacional. Em Gana, “créditos de sangue” e a busca de resultados de testes predisseram negativamente a intenção de retorno {intext(r['asamoah'], 'p')}. No Brasil, percepções de doadores e receptores nem sempre coincidem {intext(r['conceicao'], 'p')}, e medos de contaminação persistem no discurso de quem trabalha na captação {intext(r['giacomini'], 'p')}. Transparência sobre o uso do sangue e recusa de contraprestações que mercantilizem o ato não são adornos morais: interferem no retorno.

{intext(r['ferguson'], 'n')} e {intext(r['masser'], 'n')} oferecem a gramática para essas tensões: campanhas devem mirar crenças e controle percebido, não apenas o volume de exposição midiática. {intext(r['godin'], 'n')} acrescentam que novatos e experientes não respondem aos mesmos preditores, o que condena o panfleto único.

### Implicações para a prática e para a gestão

Serviços de hemoterapia podem, com base no corpus e sem extrapolação indevida de um país a outro: (a) registrar retorno em 6 e 12 meses como indicador de qualidade, não só unidades coletadas; (b) inserir na alta do novato um plano escrito de quando e onde retornar, nos moldes de intenção de implementação {intext(r['wevers'], 'p')}; (c) substituir reuniões motivacionais genéricas por contato breve educativo ou emocional {intext(r['hashemi'], 'p')}; (d) auditar a experiência de serviço na ótica de quem doa {intext(r['swanevelder'], 'p')}; (e) explicar o destino do sangue com linguagem compreensível {join_p(r['asamoah'], r['conceicao'])}; (f) criar fila de reconquista para lapsos {intext(r['germain'], 'p')}; (g) treinar enfermagem para os quatro momentos da Tabela 3 {intext(r['giacomini'], 'p')}.

Nenhuma dessas ações dispensa avaliação local. Prevalências e razões de chances citadas pertencem a contextos (Irã, Países Baixos, África do Sul, Gana, Austrália, Canadá, Brasil) cuja mistura de incentivos, confiança institucional e perfil etário difere da de cada hemocentro brasileiro.

### Limitações

A revisão é narrativa: não houve busca sistemática em múltiplas bases, dupla seleção independente, avaliação formal de risco de viés nem meta-análise própria. O corpus parte de uma lista inicial de DOIs, o que pode omitir estudos relevantes, especialmente em enfermagem publicada em periódicos não indexados na CrossRef. Números de retorno foram reproduzidos a partir dos relatos das fontes e não reanalisados. A generalização para o Brasil é interpretativa: o inquérito de Pelotas {intext(r['zago'], 'p')} e os estudos de {intext(r['giacomini'], 'p')} e de {intext(r['conceicao'], 'p')} não cobrem a heterogeneidade da rede hemoterápica nacional. A verificação de originalidade deste pacote é heurística local e não substitui relatórios comerciais de similaridade. Não foram usados dados primários de doadores; implementação local com coleta de dados exige projeto próprio e aprovação ética quando couber.

### Objeções e respostas

Objeção 1: sem meta-análise não se pode afirmar que “intervenções funcionam”. Resposta: H1 é hipótese de síntese, apoiada em convergência de ensaios e coortes nomeados, não em estimativa global de efeito. O ensaio de {intext(r['hashemi'], 'n')} e o experimento de {intext(r['wevers'], 'n')} são âncoras empíricas; a revisão de {intext(r['bagot'], 'n')} impede entusiasmo indiscriminado com incentivos.

Objeção 2: retenção seria função de marketing, não de enfermagem. Resposta: a taxonomia de barreiras inclui serviço e medo {intext(r['bednall2011'], 'p')}, o não retorno associa-se a mau atendimento {intext(r['swanevelder'], 'p')}, e a literatura brasileira de enfermagem já formula fidelização como trabalho educativo e relacional {intext(r['giacomini'], 'p')}. Marketing sem o encontro da coleta deixa intocado o mecanismo.

Objeção 3: enfatizar retorno de novatos negligenciaria doadores frequentes. Resposta: o corpus inclui lapso de atuais e de frequentes {join_p(r['germain'], r['gemelli'])}. A janela da primeira doação é crítica por volume de perda, não por exclusividade.

Objeção 4: modelos da TCP estariam datados. Resposta: mesmo que extensões posteriores existam fora deste corpus, os testes de {intext(r['masser'], 'n')} e de {intext(r['godin'], 'n')} continuam a oferecer variáveis manipuláveis (atitude, norma, controle, diferença novato/experiente) que campanhas genéricas ignoram.

"""

    conclusao = f"""## Conclusão

A evidência reunida indica que o estoque de sangue se sustenta quando a primeira doação se converte em carreira, e que essa conversão é sensível a desenho de intervenção e a qualidade do encontro assistencial. H1 recebe apoio convergente: comunicação estruturada, lembretes e técnicas de planejamento do comportamento associam-se a maior retorno de novatos do que a inação ou o apelo motivacional genérico. H2 recebe apoio conceitual e observacional: enfermagem, educação, transparência e experiência de serviço aparecem como mediadores organizacionais da retenção, não como acessórios da punção.

Contribuições desta revisão incluem (1) articulação, em um único argumento, de taxonomias motivacionais, modelos sociocognitivos, janela da primeira doação, lapso e literatura brasileira de enfermagem; (2) tradução dos achados em quatro momentos de processo passíveis de auditoria local; e (3) recusa de indicadores que contem apenas unidades coletadas. Pesquisas futuras, com ética adequada, devem testar bundles de enfermagem de retenção em hemocentros brasileiros, com desfechos de retorno real em 6 e 12 meses, estratificação entre novatos e frequentes, e avaliação da experiência de serviço relatada pelo doador.

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

- **Originalidade:** O manuscrito é original, não foi publicado e não está sob avaliação simultânea em outro periódico. Não reproduz o artigo de demonstração do pipeline (agosto de 2026) sobre reações adversas na doação, nem manuscritos prévios do autor sobre outros temas.
- **Ética:** {meta['etica']['declaracao']}
- **Disponibilidade de dados:** Não se aplica (revisão narrativa sem dados primários).
- **Contribuições CRediT:** Conceitualização, metodologia, investigação, redação — rascunho original e revisão: {autor['nome']}.
- **ORCID:** {autor['orcid']}
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
    titulo = " ".join(meta["titulo_provisorio"].split())
    return f"""# Carta de apresentação / Cover letter

{autor['nome']}
ORCID: {autor['orcid']}
E-mail: {autor['email']}

Prezada Editora / Prezado Editor de *{revista}*,

Encaminho para apreciação o manuscrito intitulado:

**{titulo}**

Trata-se de {estudo['tipo_estudo'].lower()} que sintetiza evidências sobre motivadores e barreiras da doação de sangue, preditores de retorno (com ênfase na janela da primeira doação), intervenções de retenção e implicações para a enfermagem em serviços de hemoterapia. O trabalho dialoga com o escopo da revista ao tratar comportamento do doador, qualidade do serviço de coleta e bases para melhoria de processos de retenção.

Principais contribuições:
1. Articulação de taxonomias motivacionais, modelos sociocognitivos e evidência de intervenções de retorno.
2. Tradução operacional dos achados para quatro momentos do processo de enfermagem.
3. Hipóteses de síntese testáveis em avaliação local de hemocentros, sem meta-análise indevida.

Declaro que o manuscrito é original, não foi publicado e não se encontra sob avaliação em outro periódico. Não há conflitos de interesse. Não houve financiamento externo específico. Por se tratar de revisão de literatura publicada, não se aplica aprovação por comitê de ética em pesquisa.

Atenciosamente,
{autor['nome']}
{autor['email']}
"""
