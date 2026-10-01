#!/usr/bin/env python3
"""Gera o manuscrito Markdown APA 7 a partir do input + referências validadas.

Execução de outubro de 2026: deficiência de ferro e inaptidão por hemoglobina.
Não reutiliza os manuscritos de esquizofrenia, de reações adversas (agosto/2026)
nem de retenção de doadores (setembro/2026).
"""

from __future__ import annotations

from datetime import date
from typing import Any

DOI = {
    "cable2010": "10.1111/j.1537-2995.2010.02865.x",
    "cable2011": "10.1111/j.1537-2995.2011.03401.x",
    "kiss": "10.1001/jama.2015.119",
    "cable2016": "10.1111/trf.13659",
    "mast": "10.1016/j.tmrv.2013.11.001",
    "smith": "10.1002/14651858.cd009532.pub2",
    "pasricha": "10.1111/j.1537-2995.2011.03173.x",
    "spencer": "10.1111/trf.15448",
    "rigas": "10.1111/tme.12477",
    "magnussen": "10.1111/trf.13152",
    "cancado2001": "10.1590/s1516-31802001000400003",
    "cancado2012": "10.5581/1516-8484.20120086",
    "backman": "10.1111/trf.13578",
    "interval": "10.1016/s0140-6736(17)31928-1",
    "padilha": "10.1590/s0034-71672011000200003",
    "waldvogel": "10.1111/vox.12348",
    "drexler": "10.1016/j.clnu.2019.03.025",
    "silva": "10.5581/1516-8484.20120092",
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
    hoje = date(2026, 10, 1)
    r = _index(refs)
    refs_apa = _sorted_apa(refs)

    resumo = (
        "A cada doação de sangue total o organismo perde ferro em quantidade que a "
        "hemoglobina, isoladamente, não caracteriza. Este artigo revisa de modo "
        "narrativo estudos com DOI validado na CrossRef sobre depleção de ferro, "
        "inaptidão por hemoglobina baixa e reposição, e examina o lugar da enfermagem "
        "na triagem clínica. Coortes de grandes serviços mostram estoques ausentes e "
        "eritropoese ferropriva em parcela ampla de doadores frequentes, com gradiente "
        "por sexo, idade e intensidade de doação. Ensaios e uma revisão Cochrane "
        "indicam que ferro oral em dose baixa acelera a recuperação da hemoglobina e "
        "dos estoques e reduz inaptidão, ao custo de mais eventos adversos, o que "
        "desaconselha suplementação universal não monitorada. Encurtar o intervalo "
        "entre doações aumenta o volume coletado, porém eleva sintomas, inaptidões e "
        "deficiência de ferro. Evidência brasileira, local e anterior à difusão da "
        "ferritina de rotina, já descrevia deficiência sobretudo em mulheres "
        "multidoadoras e erro de classificação quando a hemoglobina não é confirmada. "
        "A triagem clínica, competência descrita para a enfermeira, é o momento de "
        "explicar a causa provável da inaptidão, confirmar a medida e encaminhar "
        "reposição ou alongamento de intervalo. Proteger o doador exige política de "
        "ferro acoplada ao ato da triagem, e não apenas um ponto de corte de hemoglobina."
    )

    keywords = (
        "doação de sangue; deficiência de ferro; ferritina; "
        "inaptidão por hemoglobina; suplementação de ferro; enfermagem"
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

Each whole-blood donation removes an amount of iron that hemoglobin alone does not characterize. This narrative review synthesizes CrossRef-validated studies on iron depletion, low-hemoglobin deferral, and iron replacement, and examines where nursing sits in clinical donor screening. Large-service cohorts show absent iron stores and iron-deficient erythropoiesis in a substantial share of frequent donors, graded by sex, age, and donation intensity. Trials and a Cochrane review indicate that low-dose oral iron speeds recovery of hemoglobin and stores and reduces deferral, at the cost of more adverse events, which argues against unmonitored universal supplementation. Shorter interdonation intervals increase the volume collected but also increase symptoms, deferrals, and iron deficiency. Brazilian evidence, local and gathered before routine ferritin testing spread, already described deficiency especially among repeat female donors and misclassification when hemoglobin is not confirmed. Clinical screening, a competency described for the nurse, is the moment to explain the likely cause of deferral, confirm the measurement, and refer for replacement or a longer interval. Protecting the donor therefore requires an iron policy tied to the screening encounter, not only a hemoglobin cutoff.

**Keywords:** blood donation; iron deficiency; ferritin; hemoglobin deferral; iron supplementation; nursing

---
"""

    introducao = f"""## Introdução

A doação de sangue total retira, em um único procedimento de cerca de 425 a 475 mL, algo entre 200 e 250 mg de ferro, mobilizando em seguida as reservas corporais {intext(r['cancado2001'], 'p')}. Essa perda é pequena diante do estoque de um adulto com reservas folgadas e é grande diante do estoque de quem já doa com frequência, menstrua ou chega à coleta com ferritina baixa. A hemoglobina usada na porta do serviço é um marcador tardio: pode estar acima do ponto de corte quando os estoques já se esgotaram. {intext(r['mast'], 'n')} revisa a inaptidão por hemoglobina baixa e lembra que ela ocorre em cerca de 10% das tentativas de doação de sangue total, com causas que vão da deficiência de ferro à faixa de 12,0 a 12,4 g/dL em mulheres — dentro da referência populacional, porém abaixo dos 12,5 g/dL exigidos para doar nos Estados Unidos — e, no extremo, a anemia de doença ainda não reconhecida.

O estudo RISE, na inscrição, encontrou estoques de ferro ausentes (ferritina inferior a 12 ng/mL) em 15,0% e eritropoese ferropriva em 41,7% de 2.425 doadores de hemácias {intext(r['cable2010'], 'p')}. Entre doadores frequentes, as proporções de estoques ausentes e de eritropoese ferropriva foram de 16,4% e 48,7% em homens e de 27,1% e 66,1% em mulheres. A intensidade de doação foi o preditor mais fortemente associado, com razões de chances, conforme o estrato de intensidade e em comparação com doadores de primeira vez, entre 5,3 e 52,2. Sexo feminino, idade mais jovem, menstruação e menor peso aumentaram a chance; o uso de suplemento de ferro tendeu a protegê-la. Dieta e raça ou etnia, naquele modelo, em geral não se associaram aos desfechos.

A mesma coorte, seguida enquanto os participantes continuavam a doar, confirmou que o problema não é um artefato da visita de entrada {intext(r['cable2011'], 'p')}. Entre mulheres de primeira vez ou reativadas que retornaram, 20% tinham estoques ausentes e 51% eritropoese ferropriva na visita final; entre homens, 8% e 20%. Entre doadores frequentes que retornaram, as cifras foram 27% e 62% nas mulheres e 18% e 47% nos homens. Intervalo mais curto e maior número de doações nos dois anos anteriores predisseram depleção; suplemento de ferro reduziu o risco. A inaptidão por hemoglobina, por sua vez, associou-se a sexo feminino, raça negra e intervalo curto. O intervalo mínimo de 56 dias praticado nos Estados Unidos não repõe, para muitos doadores, nem a hemoglobina nem o ferro {intext(r['mast'], 'p')}.

Há, ao lado da biologia, um problema de medida. Em 1.396.645 registros de um serviço nacional, a hemoglobina capilar foi mais baixa no verão e no fim da tarde do que no inverno e pela manhã {intext(r['backman'], 'p')}. Em julho, as médias foram 154,1 g/L em homens e 139,6 g/L em mulheres; em janeiro, 156,9 g/L e 141,8 g/L. Às 19 h, 153,8 g/L e 138,9 g/L; às 11 h, 157,2 g/L e 142,8 g/L. Fatores que não descrevem a saúde do doador alteram a taxa de inaptidão. No Brasil, {intext(r['silva'], 'n')} compararam a triagem manual da hemoglobina com método automatizado em candidatos inaptos por anemia: a taxa de inaptidão por anemia foi de 4,2%; entre os excluídos, deficiência de ferro explicou 37,5% e talassemia beta 9,3%; e 38,1% dos inicialmente inaptos tinham hemoglobina normal na dosagem automatizada. Os autores recomendam confirmar hemoglobina ou hematócrito antes de inaptar.

O outro lado da política de coleta é o intervalo. O ensaio INTERVAL comparou, na Inglaterra, a prática padrão com intervalos mais curtos usados em outros países: homens aleatorizados para 12, 10 ou 8 semanas e mulheres para 16, 14 ou 12 semanas {intext(r['interval'], 'p')}. Foram recrutados 45.263 doadores e analisados 45.042. Entre homens, o grupo de 8 semanas coletou, em dois anos, 1,69 unidades a mais por doador do que o de 12 semanas (intervalo de confiança de 95% [IC 95%] 1,59 a 1,80; cerca de 795 mL), e o de 10 semanas coletou 0,79 unidades a mais (IC 95% 0,69 a 0,88; cerca de 370 mL). A interpretação dos autores é direta: doar com mais frequência do que o padrão britânico rendeu mais sangue sem efeito maior sobre qualidade de vida, atividade física ou função cognitiva, mas produziu mais sintomas ligados à doação, mais inaptidões e mais deficiência de ferro.

{intext(r['cancado2012'], 'n')} situam esse dilema na história recente dos serviços: desde os anos 1980 a hemoterapia concentrou-se na segurança do produto e na suficiência do estoque, e o preço dessa ênfase, argumentam, foi a depleção de ferro do doador de repetição. A capacidade de doar sem desenvolver deficiência ou anemia varia com ingestão, perdas menstruais, frequência de doação e uso de suplemento. O editorial não substitui uma coorte nacional; recoloca a saúde de quem doa como objeto, e não como externalidade da meta de bolsas.

A literatura de enfermagem descreve outro recorte do mesmo balcão. {intext(r['padilha'], 'n')} observaram 25 entrevistas de triagem feitas por cinco enfermeiras em banco de sangue de hospital universitário em Porto Alegre e mapearam competências do Conselho Internacional de Enfermagem: seis na área de prática profissional, ética e legal, e onze na provisão e no gerenciamento do cuidado. O estudo não mede ferritina. Mostra que a decisão de aptidão é trabalho de enfermagem, com dever de informação e de cuidado, não um gesto acessório da coleta.

A lacuna que esta revisão enfrenta é a separação entre esses três corpos: a epidemiologia do ferro do doador, os ensaios de intervalo e de reposição, e a descrição da triagem como competência de enfermagem. Sem articulação, o serviço ou encurta o intervalo para ganhar bolsas e descobre a inaptidão tarde, ou distribui ferro a todos e esbarra em eventos adversos e adesão incerta, ou explica a hemoglobina baixa como “anemia” sem dizer se há estoque, talassemia ou erro de medida. O objetivo é reunir o que as fontes permitem afirmar, e só isso.

**Objetivo.** {estudo['objetivo']}

**Hipóteses de síntese.**
1. {estudo['hipoteses'][0]}
2. {estudo['hipoteses'][1]}
3. {estudo['hipoteses'][2]}

"""

    metodo = f"""## Método

### Delineamento

Trata-se de {estudo['tipo_estudo'].lower()}. O desenho narrativo foi escolhido porque o objeto mistura coortes laboratoriais, ensaio pragmático de intervalo, ensaios de ferro oral e venoso, revisão de ensaios, série operacional de um serviço e estudo qualitativo de competências. Esses desenhos não compartilham um único desfecho que autorize, neste manuscrito, uma nova meta-análise.

### Corpus e critérios

{estudo['amostra']} Incluíram-se artigos de periódico cujo DOI a CrossRef localizou e cuja contribuição incidisse sobre estoques de ferro em doadores, inaptidão por hemoglobina, intervalo entre doações, suplementação ou triagem clínica de enfermagem. Ficaram de fora, na curadoria, trabalhos centrados em reação vasovagal, motivação para o retorno ou fidelização — temas de revisões distintas —, bem como preprints, resumos de congresso e dissertações sem artigo correspondente.

A lista de DOIs foi fixada no arquivo de entrada e validada na API CrossRef antes da redação. Não houve busca sistemática em múltiplas bases, registro de protocolo, seleção em duplicata nem ferramenta formal de risco de viés. A ausência desses passos é limite do desenho, não detalhe a ser corrigido na leitura dos resultados. O recorte privilegia periódicos de medicina transfusional, uma revisão Cochrane e dois núcleos brasileiros: hemoterapia (Santa Casa de São Paulo e candidatos inaptos por anemia) e enfermagem (triagem em Porto Alegre).

### Instrumentos e procedimentos

Instrumentos: {"; ".join(estudo['instrumentos'])}.
Procedimentos: {estudo['procedimentos']}

A síntese seguiu seis eixos definidos antes da redação: (1) prevalência e preditores de depleção; (2) hemoglobina como critério, incluindo erro de medida; (3) intervalo entre doações; (4) ensaios e revisão de suplementação; (5) algoritmos de serviço com ferritina; (6) triagem de enfermagem e a tarefa de informar a inaptidão.

### Análises

{estudo['analises']} Quando o resumo disponível truncava um intervalo de confiança ou um valor de p, o número incompleto não foi completado por estimativa. A validade da síntese depende da fidelidade a essas fontes e da cobertura deliberadamente estreita do corpus.

### Ética

{meta['etica']['declaracao']}

"""

    resultados = f"""## Resultados

### Prevalência e preditores

Os dois relatos do RISE separam inscrição e seguimento, e por isso não devem ser lidos como uma única porcentagem {join_p(r['cable2010'], r['cable2011'])}. Na entrada, a depleção já era comum em doadores frequentes de ambos os sexos. No fim do seguimento, mulheres jovens e quem doava com intervalo curto concentravam estoques ausentes e eritropoese ferropriva, enquanto o uso de ferro suplementar apontava na direção oposta. A mensagem operacional é que “apto pela hemoglobina” não equivale a “com reserva”.

Um inquérito posterior, com mais de 12.600 doações de sangue total bem-sucedidas em quatro centros dos Estados Unidos e amostra enriquecida para minorias (1.605 doadores afro-americanos, 1.616 asiáticos e 1.023 hispânicos), encontrou estoques ausentes em 19% e ferritina baixa em 42% {intext(r['spencer'], 'p')}. Controlados os demais fatores, doadores afro-americanos e asiáticos tiveram risco 20% a 25% menor de estoques ausentes do que brancos não hispânicos, e doadores hispânicos tiveram risco 25% maior. Suplemento diário de ferro reduziu o risco de ferritina baixa e de estoques ausentes em 30% a 40%; o uso menos frequente protegeu menos (7% a 19%). Antiácidos regulares acrescentaram ao menos 20% de risco. Em mulheres, contraceptivo oral ou estrogênio reduziu o risco em 16% a 22%; em homens, testosterona suplementar elevou o risco de ferritina baixa e de estoques ausentes em 50% a 125%. Idade, sexo e frequência de doação permaneceram os preditores principais; os demais refinam a quem oferecer o quê.

No Danish Blood Donor Study, sexo, número de doações prévias, tempo desde a última doação e status menopausal foram os preditores mais fortes de deficiência de ferro {intext(r['rigas'], 'p')}. O mesmo relato nota que a evidência sobre efeitos dessa deficiência na saúde de quem doa ainda é escassa: há indício de queda transitória de desempenho físico em mulheres após uma doação padrão, e não há, nos dados ali resumidos, reflexo da deficiência em piora autopercebida da saúde mental ou física. A consequência prática que os autores extraem é dupla: alongar intervalos ou suplementar com guia laboratorial.

Em São Paulo, {intext(r['cancado2001'], 'n')} estudaram 300 doadores da Santa Casa entre 20 de setembro e 5 de outubro de 1999, com ferro sérico, capacidade total de ligação, saturação de transferrina, ferritina e índices eritrocitários. A frequência de deficiência de ferro foi de 11,0%: 5,5% nos homens (13/237) e 31,7% nas mulheres (20/63). Em homens, a deficiência foi mais frequente em multidoadores do que em doadores de primeira vez (7,6% versus 0,0%). A conclusão dos autores é que hemoglobina ou hematócrito, sozinhos, não detectam nem excluem deficiência sem anemia. O estudo é local e anterior às coortes internacionais citadas acima; ainda assim, a direção — mulher e repetição — coincide com elas.

**Tabela 1**

*Definições operacionais de depleção de ferro reproduzidas das fontes (não harmonizadas entre si)*

| Fonte | Limiar citado | O que o limiar designa |
| --- | --- | --- |
| {intext(r['cable2010'], 'p')} | Ferritina < 12 ng/mL | Estoques de ferro ausentes |
| {intext(r['cable2010'], 'p')} | log(receptor solúvel de transferrina/ferritina) ≥ 2,07 | Eritropoese ferropriva |
| {intext(r['spencer'], 'p')} | Ferritina baixa e estoques ausentes, nos termos do estudo | Desfechos separados; prevalências de 42% e 19% |
| {intext(r['waldvogel'], 'p')} | Ferritina < 30 ng/mL, sem anemia | Critério de entrada do ensaio em mulheres |
| {intext(r['drexler'], 'p')} | Ferritina ≤ 30 ng/mL | Critério de entrada do ensaio IronWoMan |
| {intext(r['pasricha'], 'p')} | Depleção em 59 de 261 doadoras (22,6%) | Doadoras pré-menopáusicas não anêmicas; o ponto numérico exato da ferritina não foi completado porque o resumo recuperado o trunca |

A Tabela 1 existe para impedir que “deficiência de ferro” seja tratada como uma única porcentagem. Estoques ausentes, eritropoese ferropriva e ferritina abaixo de 30 ng/mL não são sinônimos. Comparar 15% do RISE com 11% da Santa Casa sem dizer o ensaio laboratorial é um erro de leitura, não um achado.

### Hemoglobina, inaptidão e erro de classificação

{intext(r['mast'], 'n')} organiza as causas da inaptidão por hemoglobina baixa em pelo menos três grupos que a frase “está anêmico” mistura: deficiência por menstruação ou gestação, já na primeira tentativa; deficiência adquirida pela repetição da doação, porque o intervalo de 56 dias não repõe o ferro retirado; e causas não relacionadas ao hábito de doar, inclusive doença ainda não diagnosticada. Dessa heterogeneidade decorre a dificuldade, reconhecida na revisão, de o serviço dizer ao doador por que ele foi inapto e de desenhar um programa único de prevenção.

A predição é possível antes da queda da hemoglobina abaixo do corte. {intext(r['pasricha'], 'n')} acompanharam doadoras pré-menopáusicas aptas, portanto não anêmicas no momento da medida. De 261, 59 (22,6%) estavam com depleção de ferro. Hemoglobina e índices de ferro, colhidos antes da doação, permitiram identificar quem tinha maior chance de inaptidão ulterior por anemia. O resumo recuperado não traz o coeficiente completo do modelo; o que se pode afirmar sem completá-lo é a proporção de depleção em aptas e a tese de que a triagem só com hemoglobina chega tarde para parte das doadoras.

O erro de medida empurra pessoas para os dois lados do corte. {intext(r['backman'], 'n')} mostram variação sazonal e circadiana da hemoglobina capilar em escala nacional. {intext(r['silva'], 'n')} mostram, em candidatos brasileiros já inaptos pela técnica manual, que mais de um terço teria hemoglobina normal no método automatizado, e que a deficiência de ferro, embora fosse a causa mais frequente entre os excluídos (37,5%), não era a única: talassemia beta respondeu por 9,3%. Confirmar a medida antes de inaptar, como propõem, é ao mesmo tempo cuidado com o doador e cuidado com o estoque.

### Intervalo entre doações

O INTERVAL responde à pergunta que o RISE deixa em aberto: o que acontece, em desfecho de coleta e em desfecho de ferro, quando o intervalo encurta de propósito {join_p(r['cable2011'], r['interval'])}. No braço masculino, intervalos de 8 e de 10 semanas renderam mais unidades em dois anos do que o intervalo de 12 semanas, nas magnitudes já citadas. O preço, na conclusão do ensaio, foi mais sintomas relacionados à doação, mais inaptidão e mais deficiência de ferro, sem grande abalo de qualidade de vida, atividade física ou cognição. {intext(r['cable2011'], 'n')} já haviam indicado, na coorte observacional, que alongar o intervalo reduziria depleção e inaptidão por hemoglobina, e que a alternativa seria repor ferro para sustentar a frequência. O ensaio randomizado não contradiz essa bifurcação; quantifica o lado da oferta.

Não se transcreve aqui o incremento de unidades no braço feminino porque o trecho correspondente do resumo recuperado não foi usado para inventar a estimativa. A conclusão dos autores cobre o desenho inteiro — homens e mulheres — quanto à direção: mais sangue, mais deficiência de ferro. Generalizar o número masculino para mulheres seria outro artigo, não este.

### Reposição de ferro

O ensaio de {intext(r['kiss'], 'n')} randomizou 215 doadores, com hemoglobina de partida compatível com a doação, para gluconato ferroso (37,5 mg de ferro elementar ao dia) ou nenhum ferro, por 24 semanas, estratificados por ferritina, sexo e idade. Depois da doação de 500 mL, a hemoglobina média caiu de 13,4 g/dL (desvio-padrão 1,1) para 12,0 g/dL (1,2) no grupo de ferritina baixa (≤ 26 ng/mL) e de 14,2 g/dL (1,1) para 12,9 g/dL (1,2) no grupo de ferritina mais alta. O tempo até recuperar 80% da hemoglobina removida foi, com ferro, em média 32 dias (intervalo interquartil [IIQ] 30 a 34) no grupo de ferritina baixa e 31 dias (IIQ 29 a 33) no de ferritina mais alta. Sem ferro, esses tempos foram 158 dias (IIQ 126 a mais de 168) e 78 dias (IIQ 66 a 95). A ferritina voltou ao basal em mediana de 21 dias (IIQ 12 a 84) nos depletos que tomaram ferro, e em mais de 168 dias nos que não tomaram. No conjunto de quem recebeu suplemento, a mediana até o basal da ferritina foi 76 dias (IIQ 20 a 126), contra mais de 168 dias sem ferro.

O relato complementar de balanço de ferro, no mesmo esquema de 37,5 mg ou nenhum ferro por 24 semanas e com os mesmos 215 doadores, estimou o ferro corporal total pela soma dos estoques e do ferro da hemoglobina {intext(r['cable2016'], 'p')}. Aos 24 semanas, o ferro corporal total de quem suplementou subiu 281,0 mg em relação ao período anterior à doação (IC 95% 223,4 a 338,6), e o de quem não suplementou caiu 74,1 mg (IC 95% −112,3 a −35,9). Oito semanas de ferro responderam por quase todo o ganho medido. Doadores com ferro repuseram o que a bolsa retirou; doadores sem ferro não repuseram.

A hepcidina ajuda a ler por que a reposição oral não é um interruptor instantâneo. {intext(r['waldvogel'], 'n')} mediram hepcidina por espectrometria de massa em mulheres pré-menopáusicas com deficiência sem anemia (ferritina inicial inferior a 30 ng/mL), dentro de um ensaio de 80 mg de ferro ao dia por quatro semanas (n = 145). Em quatro semanas, a hepcidina plasmática subiu no braço de ferro em relação ao placebo (diferença 0,29 nM; IC 95% 0,18 a 0,40). Houve correlação com a ferritina na linha de base e correlação mais forte depois do tratamento. A hepcidina não previu quem responderia, mas marcou a repleção necessária à eritropoese. Ou seja: o ferro oral move o eixo regulatório, e o movimento é mensurável em semanas, não em horas de pós-doação.

Ferro venoso acelera ainda mais, com outro custo e outra logística. O IronWoMan randomizou 176 doadores com ferritina igual ou inferior a 30 ng/mL para uma dose de carboximaltose férrica intravenosa de 1.000 mg (n = 86) ou fumarato ferroso oral, 100 comprimidos de 100 mg, dez por semana (n = 90) {intext(r['drexler'], 'p')}. Completaram 172 pessoas, 137 mulheres; quatro do braço oral não retornaram. No seguimento, a saturação da transferrina foi mais alta no braço intravenoso (mediana 27%, IIQ 23 a 35) do que no oral (21%, IIQ 16 a 32), e a ferritina também foi significativamente mais alta no intravenoso. Os autores concluem que a dose única intravenosa é muito eficaz contra a deficiência iatrogênica e que o ferro oral permanece alternativa aceitável. A avaliação dos estoques, e não a hemoglobina isolada, é o que sustentaria a decisão.

A síntese dos ensaios cabe à revisão Cochrane de {intext(r['smith'], 'n')}, que reuniu 30 ensaios (4.704 participantes) até a busca de 18 de novembro de 2013: 19 comparações de ferro contra placebo ou controle, uma de via oral contra parenteral, quatro de doses, uma de durações e 12 de apresentações. Muitos ensaios tinham qualidade metodológica baixa ou incerta; os autores classificaram a evidência como moderada. Houve redução estatisticamente significativa da inaptidão por hemoglobina baixa na primeira doação depois de iniciado o ferro (risco relativo 0,34; IC 95% 0,21 a 0,55; quatro estudos; 1.194 participantes). Doadores suplementados também apresentaram hemoglobina e estoques mais altos. O benefício convive com mais eventos adversos, o que limita aceitação e adesão. Efeitos de longo prazo da suplementação sem medida de estoques são desconhecidos. A conclusão prática da revisão é restritiva: o uso disseminado de comprimidos fica prejudicado; serviços podem considerar suplementação dirigida a quem tem maior risco, intervalos personalizados e orientação dietética.

### Algoritmo de serviço

A experiência de dois anos na Região da Capital da Dinamarca traduz parte dessa conclusão em rotina {intext(r['magnussen'], 'p')}. Centralizou-se a medida de hemoglobina, introduziu-se ferritina e criou-se um centro de hemoglobina e ferro do doador. Um algoritmo baseado em hemoglobina e ferritina decidia o contato, a oferta de ferro intermitente ou, raramente, o encaminhamento ao clínico geral. No período, 62.663 doadores realizaram 193.288 unidades, e 318 doadores forneceram 754 hemogramas. A hemoglobina de doadores de repetição subiu de 15,39 para 15,60 g/dL em homens e de 13,85 para 14,06 g/dL em mulheres. A proporção com hemoglobina baixa caiu de 0,9% para 0,3% nos homens e de 3,9% para 2,7% nas mulheres. {intext(r['rigas'], 'n')} descrevem o mesmo arranjo de Copenhague como viável: ferritina de rotina e suplementação reduziram a parcela de doadores com hemoglobina baixa. Não se trata de dois experimentos independentes; são a coorte de pesquisa e a série operacional do mesmo sistema. O que a série acrescenta é a ordem de grandeza do serviço e a escolha de suplementar quem se beneficia, não a fila inteira.

### Triagem de enfermagem

Nenhum dos ensaios acima foi desenhado como estudo de enfermagem. O nexo está no ato em que a hemoglobina é medida e a frase sobre aptidão é dita. {intext(r['padilha'], 'n')} mostraram que esse ato, no serviço observado, é da enfermeira, e que as competências exigidas incluem prática ética e legal e gerenciamento do cuidado. {intext(r['mast'], 'n')} mostra que a causa da inaptidão por hemoglobina baixa é heterogênea e que informar mal é um risco próprio do programa. {intext(r['silva'], 'n')} e {intext(r['backman'], 'n')} mostram que a medida pode inaptar quem a dosagem confirmada ou outro horário não inaptaria. {intext(r['smith'], 'n')} e {intext(r['magnussen'], 'n')} mostram que a conduta seguinte, quando há depleção, não é um comprimido para todos nem um “volte quando puder”: é suplementação dirigida ou intervalo ajustado, com estoque medido.

A Figura 1 ordena esses passos como síntese conceitual. Não é protocolo testado. A Tabela 2 reúne as estimativas que a síntese usa, para que o leitor confira a fonte de cada número. A Tabela 3 distingue o que a enfermeira pode fazer na triagem com base no corpus do que exigiria estudo novo.

**Figura 1**

*Percurso conceitual da triagem quando a hemoglobina é limítrofe ou baixa. Síntese dos eixos do corpus; não é algoritmo validado em ensaio.*

1. Medir a hemoglobina com método declarado e, se o valor for limítrofe ou discrepante com a clínica, confirmar antes de inaptar {join_p(r['silva'], r['backman'])}.
2. Não tratar a hemoglobina isolada como prova de estoque suficiente nem como diagnóstico etiológico {join_p(r['cancado2001'], r['mast'], r['pasricha'])}.
3. Quando houver ferritina ou índice equivalente, separar estoque ausente, depleção sem anemia e anemia, e registrar o limiar usado {join_p(r['cable2010'], r['spencer'])}.
4. Oferecer reposição àqueles com maior chance de benefício, informando eventos adversos e tempo de recuperação, ou alongar o intervalo {join_p(r['kiss'], r['smith'], r['magnussen'], r['interval'])}.
5. Explicar a causa provável em linguagem compreensível e combinar o retorno, como parte da competência de triagem {intext(r['padilha'], 'p')}.

**Tabela 2**

*Estimativas reproduzidas das fontes e usadas na síntese*

| Eixo | Estimativa | Fonte |
| --- | --- | --- |
| Inscrição RISE | 15,0% estoques ausentes; 41,7% eritropoese ferropriva (n = 2.425) | {intext(r['cable2010'], 'p')} |
| Frequentes, inscrição | Homens 16,4% e 48,7%; mulheres 27,1% e 66,1% (estoques ausentes e eritropoese ferropriva) | {intext(r['cable2010'], 'p')} |
| Visita final, frequentes | Mulheres 27% e 62%; homens 18% e 47% | {intext(r['cable2011'], 'p')} |
| Quatro centros, Estados Unidos | 19% estoques ausentes; 42% ferritina baixa (> 12.600 doações) | {intext(r['spencer'], 'p')} |
| Santa Casa, 1999 | Deficiência em 11,0% (homens 5,5%; mulheres 31,7%; n = 300) | {intext(r['cancado2001'], 'p')} |
| Inaptidão por anemia, Brasil | 4,2% dos candidatos; 37,5% por deficiência de ferro entre excluídos; 38,1% com hemoglobina normal no método automatizado | {intext(r['silva'], 'p')} |
| INTERVAL, homens, 2 anos | +1,69 unidades (8 versus 12 semanas); +0,79 (10 versus 12 semanas) | {intext(r['interval'], 'p')} |
| Ferro oral, recuperação de 80% da hemoglobina | Cerca de 32 e 31 dias com ferro; 158 e 78 dias sem ferro | {intext(r['kiss'], 'p')} |
| Ferro corporal total em 24 semanas | +281,0 mg com ferro; −74,1 mg sem ferro | {intext(r['cable2016'], 'p')} |
| Inaptidão na 1ª doação após ferro | Risco relativo 0,34 (IC 95% 0,21 a 0,55) | {intext(r['smith'], 'p')} |
| Copenhague, 2 anos | Hemoglobina de repetição: homens 15,39 para 15,60 g/dL; mulheres 13,85 para 14,06 g/dL | {intext(r['magnussen'], 'p')} |

**Tabela 3**

*O que a triagem de enfermagem pode sustentar com este corpus, e o que não pode*

| Conduta na triagem | Apoio no corpus | O que este corpus não autoriza |
| --- | --- | --- |
| Confirmar hemoglobina limítrofe antes de inaptar | Discrepância manual versus automatizada; variação por hora e estação {join_p(r['silva'], r['backman'])} | Fixar, daqui, o método obrigatório de um hemocentro |
| Dizer que hemoglobina normal não garante estoque | Prevalência de depleção em aptos {join_p(r['cable2010'], r['pasricha'], r['cancado2001'])} | Dispensar ferritina em todo doador sem avaliação de custo local |
| Encaminhar reposição dirigida ou intervalo maior | Ensaios, Cochrane e série dinamarquesa {join_p(r['kiss'], r['smith'], r['magnussen'], r['cable2011'])} | Prescrever dose única nacional ou ferro venoso de rotina |
| Informar tempo de recuperação | Semanas com ferro em dose baixa; muitos meses sem ferro {join_p(r['kiss'], r['cable2016'])} | Prometer a mesma mediana a todos os biótipos |
| Registrar a conversa como cuidado | Competências de triagem {intext(r['padilha'], 'p')} | Afirmar que o mapeamento de Porto Alegre mediu desfecho de ferro |

"""

    discussao = f"""## Discussão

### Leitura das hipóteses

H1 encontra apoio convergente. Intensidade de doação e intervalo curto predizem estoques ausentes, eritropoese ferropriva e inaptidão por hemoglobina em coorte {join_p(r['cable2010'], r['cable2011'])}, reaparecem como frequência e tempo desde a última doação na experiência dinamarquesa {intext(r['rigas'], 'p')} e, quando o intervalo é encurtado por randomização, a deficiência de ferro aumenta junto com a coleta {intext(r['interval'], 'p')}. Sexo e idade não desaparecem — mulheres jovens e pré-menopáusicas carregam risco maior em quase todas as fontes —, mas não esgotam o efeito da exposição à doação. A H1 é hipótese de síntese: não há, neste manuscrito, uma razão de chances única que valha para todos os serviços.

H2 também encontra apoio, com a ressalva que a própria Cochrane formula. Ferro oral em dose baixa encurta a recuperação da hemoglobina e dos estoques {join_p(r['kiss'], r['cable2016'])}, move a hepcidina em mulheres com ferritina inicial abaixo de 30 ng/mL {intext(r['waldvogel'], 'p')} e, na meta-análise, reduz a inaptidão na doação seguinte com risco relativo de 0,34 {intext(r['smith'], 'p')}. Ferro venoso em dose única eleva saturação e ferritina mais do que o esquema oral estudado, e ainda assim os autores mantêm o oral como alternativa {intext(r['drexler'], 'p')}. O algoritmo que suplementa quem a ferritina indica, e não a fila inteira, coincidiu com hemoglobina mais alta e menos inaptidão em dois anos de serviço {intext(r['magnussen'], 'p')}. A mesma revisão que demonstra eficácia registra mais eventos adversos, adesão limitada e ignorância sobre o uso prolongado sem medir estoque {intext(r['smith'], 'p')}. H2, portanto, não diz “dê ferro a todo doador”. Diz que a reposição dirigida funciona e que a reposição cega tropeça na aceitabilidade.

H3 é conceitual e deve permanecer rotulada assim. {intext(r['padilha'], 'n')} não dosaram ferritina; {intext(r['kiss'], 'n')} não observaram competências de enfermagem. O argumento é de encaixe: a decisão de aptidão ocorre na triagem, a causa da hemoglobina baixa é heterogênea {intext(r['mast'], 'p')}, a medida erra {join_p(r['silva'], r['backman'])} e a conduta que o corpus sustenta — confirmar, distinguir estoque de hemoglobina, repor ou espaçar, informar o prazo — cabe a quem conduz essa conversa. Tratar H3 como resultado de ensaio seria falso. Recusar o encaixe deixaria a política de ferro numa diretoria e a frase dita ao doador noutra, sem responsável pelo intervalo entre as duas.

### Interpretação

Três distinções evitam leituras frouxas. A primeira é entre oferta de bolsas e saúde de quem doa. O INTERVAL mostra que as duas se movem juntas e em sentidos que a gestão precisa nomear: mais unidades, mais deficiência {intext(r['interval'], 'p')}. {intext(r['cancado2012'], 'n')} já pediam que a hemoterapia devolvesse atenção à saúde do doador de repetição depois de décadas centradas no produto e no estoque. Esta revisão especifica o conteúdo dessa atenção: estoque de ferro, não só fila de captação.

A segunda distinção é entre hemoglobina e ferro. Serviços que só olham o ponto de corte classificam como apto quem está depleto {join_p(r['cable2010'], r['pasricha'], r['cancado2001'])} e, no sentido inverso, inaptam por variação de método, de hora ou de estação {join_p(r['silva'], r['backman'])}. A Tabela 1 é o antídoto contra o hábito de citar “porcentagem de anêmicos” como se os limiares fossem intercambiáveis.

A terceira é entre suplemento disponível e suplemento aceitável. Eficácia em 24 semanas {intext(r['kiss'], 'p')} não responde quem engole o comprimido no mês seguinte. A Cochrane é explícita nesse limite {intext(r['smith'], 'p')}. Antiácido, contraceptivo e testosterona modificam o risco {intext(r['spencer'], 'p')} e são perguntas de triagem, não notas de rodapé farmacológico: alteram a quem a reposição dirigida deveria chegar primeiro.

### Implicações para a prática

Com o corpus em mãos, um serviço de hemoterapia pode examinar, sem copiar cegamente o intervalo britânico nem a ferritina dinamarquesa: (a) se a hemoglobina limítrofe é confirmada antes da inaptidão {intext(r['silva'], 'p')}; (b) se doadores frequentes, mulheres em idade fértil e quem retorna em intervalo mínimo têm alguma medida de estoque, nem que seja em amostra {join_p(r['cable2011'], r['rigas'])}; (c) se a frase da inaptidão distingue deficiência, possível erro de medida e necessidade de investigação clínica {intext(r['mast'], 'p')}; (d) se há via para ferro oral dirigido, com aviso de eventos adversos, em vez de comprimido universal ou de silêncio {join_p(r['smith'], r['magnussen'])}; (e) se o prazo informado ao doador se aproxima de semanas com reposição e não de “doze quando quiser” {intext(r['kiss'], 'p')}; (f) se a enfermeira da triagem participa do desenho desse roteiro, dado que o ato é dela {intext(r['padilha'], 'p')}.

Nada disso fixa dose, marca ou periodicidade de ferritina para o Brasil. A série de Copenhague e os ensaios norte-americanos e austríacos operam sob regras de intervalo, financiamento e laboratorio diferentes das de um hemocentro brasileiro. O que se transfere é a lógica — medir estoque em quem a repetição coloca em risco, repor em quem se beneficia, não inaptar por um único capilar duvidoso —, não o protocolo fotocopiado.

### Limitações

A revisão é narrativa. Não houve estratégia PRISMA, seleção independente, avaliação formal de risco de viés nem meta-análise própria. O risco relativo de 0,34 é o da Cochrane, não um cálculo deste autor {intext(r['smith'], 'p')}. Vários resumos chegaram truncados nas bases consultadas; estimativas incompletas foram omitidas em vez de completadas. O corpus começa numa lista fechada de DOIs e pode omitir ensaios relevantes, em especial literatura de enfermagem sem DOI na CrossRef ou publicada depois de 2020. Os estudos brasileiros têm mais de uma década e amostras locais {join_p(r['cancado2001'], r['silva'], r['padilha'])}; não descrevem a rede nacional de hoje. O relato dinamarquês de preditores e a série de hemoglobina são o mesmo sistema visto de dois ângulos {join_p(r['rigas'], r['magnussen'])}, e o ensaio de recuperação de hemoglobina e o de ferro corporal total compartilham o mesmo esquema de suplementação {join_p(r['kiss'], r['cable2016'])}: contá-los como replicações independentes seria inflar a evidência. A checagem de originalidade deste pacote é heurística e não substitui verificação comercial de similaridade. Não houve dados primários de doadores.

### Objeções e respostas

Objeção 1: sem meta-análise nova não se poderia dizer que o ferro “funciona”. Resposta: H2 apoia-se em ensaios nomeados e numa revisão Cochrane de 30 ensaios, com qualidade moderada e com o efeito adverso explícito {join_p(r['smith'], r['kiss'], r['drexler'])}. Este texto não produz estimativa global adicional.

Objeção 2: o INTERVAL teria mostrado que doar mais vezes é seguro, porque qualidade de vida, atividade e cognição pouco mudaram. Resposta: o mesmo parágrafo da conclusão registra mais sintomas, mais inaptidões e mais deficiência de ferro {intext(r['interval'], 'p')}. Segurança, nesse ensaio, não é sinônimo de estoque de ferro preservado.

Objeção 3: ferritina para doadores frequentes seria cara demais para entrar numa revisão de enfermagem. Resposta: a objeção é de custeio, e este corpus não calcula custo. Mostra o preço clínico de não medir — depleção em aptos e inaptidão evitável — e um serviço que suplementou de modo seletivo {join_p(r['pasricha'], r['magnussen'])}. A decisão orçamentária permanece local; a omissão do dado, não.

Objeção 4: triagem de enfermagem e metabolismo do ferro seriam assuntos de profissões diferentes. Resposta: a hemoglobina que dispara a inaptidão é lida na triagem, e as competências desse momento incluem informação e cuidado {intext(r['padilha'], 'p')}. Separar o comprimido da conversa reproduz o desencontro que {intext(r['mast'], 'n')} descreve quando o serviço não sabe explicar a causa da inaptidão.

"""

    conclusao = f"""## Conclusão

A hemoglobina da porta do hemocentro não resume o ferro de quem doa. H1 recebe apoio de coortes e de um ensaio de intervalo: doar mais vezes e com menos espaçamento associa-se a estoques ausentes, eritropoese ferropriva e inaptidão, ainda que também se associe a mais bolsas. H2 recebe apoio de ensaios e da Cochrane, com limite explícito: ferro dirigido acelera a recuperação e reduz inaptidão; ferro universal não monitorado esbarra em eventos adversos, adesão e ausência de dados de longo prazo. H3 organiza a consequência prática sem fingir um experimento de enfermagem: confirmar a medida, não confundir hemoglobina com estoque, encaminhar reposição ou intervalo e explicar o prazo são atos da triagem.

As contribuições deste texto são três. Primeira, recusar uma porcentagem única de “anemia do doador”, porque os limiares do corpus não coincidem. Segunda, colocar no mesmo argumento a oferta de sangue e a depleção, em vez de tratar a segunda como nota de segurança. Terceira, devolver à enfermeira da triagem a frase etiológica que a revisão de inaptidão mostra faltar. Pesquisa seguinte, com ética própria, pode testar em hemocentro brasileiro um roteiro breve de triagem — confirmação da hemoglobina limítrofe, ferritina em frequentes e em mulheres em idade fértil, e ferro oral dirigido — com desfechos de inaptidão, estoque e compreensão do doador sobre o motivo da conduta. Até lá, o mínimo defensável é não informar “anemia” quando o que se mediu foi um capilar, e não prometer retorno rápido a quem saiu sem ferro de reposição.

## Agradecimentos

O autor agradece às bases CrossRef, DOI.org e Europe PMC pelos metadados e resumos usados na validação das referências. Nenhuma dessas bases revisou o manuscrito.

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

- **Originalidade:** O manuscrito é original, não foi publicado e não está sob avaliação simultânea em outro periódico. Não reproduz o manuscrito de agosto de 2026 sobre reações adversas na doação, o de setembro de 2026 sobre motivação e retenção de doadores, nem manuscritos anteriores do autor sobre outros temas.
- **Ética:** {meta['etica']['declaracao']}
- **Disponibilidade de dados:** Não se aplica (revisão narrativa sem dados primários). Estimativas numéricas foram reproduzidas das fontes citadas.
- **Contribuições CRediT:** Conceitualização, metodologia, investigação, redação — rascunho original e revisão: {autor['nome']}.
- **ORCID:** {autor['orcid']}
- **Revista-alvo sugerida:** {meta.get('revista_alvo', 'a definir')}.
- **Data de geração do pacote:** {hoje.isoformat()}.

## Apêndice B
### Materiais suplementares do pipeline

Arquivos auxiliares gerados nesta execução: `references.bib`, `references.ris`, `verification_report.json`, `revision_log.json`, `cover_letter.md` e `export_checklist.json`.

### Nota de curadoria

A lista de DOIs foi fechada antes da redação. Não se completaram números truncados nos resumos. Dois pares de fontes não são replicações independentes: Kiss e colaboradores e Cable e colaboradores relatam desfechos diferentes do mesmo esquema de suplementação; Rigas e colaboradores e Magnussen e Ladelund descrevem o sistema dinamarquês em registro de coorte e em série de serviço.
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

Trata-se de {estudo['tipo_estudo'].lower()} sobre depleção de ferro em doadores de sangue, limites da hemoglobina como critério de aptidão, ensaios de intervalo e de reposição, e consequências para a triagem clínica de enfermagem. O trabalho dialoga com o escopo da revista ao tratar saúde do doador, inaptidão por hemoglobina e organização da coleta.

Principais contribuições:
1. Separação explícita dos limiares de ferritina e de eritropoese ferropriva usados pelas fontes, sem fundi-los numa única porcentagem.
2. Leitura conjunta da oferta de bolsas e da deficiência de ferro, ancorada no ensaio de intervalo e nas coortes de estoque.
3. Tradução para a triagem de enfermagem do que o corpus autoriza (confirmar medida, informar causa, encaminhar reposição dirigida) e do que não autoriza (protocolo nacional de dose).

Declaro que o manuscrito é original, não foi publicado e não se encontra sob avaliação em outro periódico. Não há conflitos de interesse. Não houve financiamento externo específico. Por se tratar de revisão de literatura publicada, não se aplica aprovação por comitê de ética em pesquisa.

Atenciosamente,
{autor['nome']}
{autor['email']}
"""
