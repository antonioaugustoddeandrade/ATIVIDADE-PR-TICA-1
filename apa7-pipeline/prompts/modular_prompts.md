# Prompts modulares — pipeline APA 7

## Prompt geral (inicial)

Gerar um rascunho de artigo científico em estilo APA 7 com base nos dados a seguir:
{titulo_provisorio}, {objetivo}, {hipoteses}, {tipo_estudo}, {amostra}, {instrumentos},
{procedimentos}, {principais_resultados_resumidos}, {bibliografia_inicial}.

Produzir: Resumo, Introdução, Método, Resultados, Discussão, Conclusão.
Usar linguagem acadêmica, citações autor–ano com IDs de referência e formato APA 7.

## Prompt seção-por-seção

Escreva a seção [Introdução | Método | Resultados | Discussão] com base em {dados_especificos}.
Inclua especificações quando pertinente, escolhas metodológicas explícitas e análises justas.

## Prompt referências

Forme uma lista de referências em APA 7. Para cada item sem DOI/ISSN/URL, busque via
CrossRef/PubMed/Google Scholar e complete metadados. Marque qualquer referência não localizada.

## Verificação automática

Executar verificações: (1) plágio/similaridade heurística, (2) cada citação no texto corresponde
à referência completa, (3) referências com DOI válidos, (4) conformidade APA
(citações diretas <40 palavras no corpo; >40 em bloco; títulos em negrito conforme APA).
Listar erros e recomendações.

## Prompt resumo curto para submissão

Gerar carta de apresentação e resumo de submissão com pontos principais e adequação da
revista-alvo {nome_da_revista}.
