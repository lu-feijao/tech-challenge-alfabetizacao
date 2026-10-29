# Mapa de joins (Frente 3, passo 2) — rascunho para revisão

Base: `docs/dados/ficha_perfil_bronze.md`. Todas as tabelas são lidas na última rodada de carga. "Medido" = número obtido em consulta; "esperado" = calculado a partir dos perfis, ainda não medido com o join.

## Decisões que os joins exigem

| # | Decisão | Proposta | Justificativa |
|---|---|---|---|
| D1 | `rede` das metas é texto; nas tabelas de resultado é código | Tabela de-para na Silver: 'Municipal' → '3'; 'Pública' → '5' | O dicionário traduz '3' como Municipal. Para 'Pública' há dois códigos possíveis ('5' Estadual+Municipal e '6' Federal+Estadual+Municipal); '6' não aparece em `uf` nem em `municipio`, então '5' é o único recorte público com resultado para comparar; `alunos` não tem nenhum aluno da rede federal ('1'). **Aprovada por Ruan em 20/10/2026.** |
| D2 | As metas não têm `serie` | Tratar a meta como 2º ano (`serie = '2'`) | Todos os resultados são do 2º ano e o enunciado define o compromisso como alfabetização até o fim do 2º ano. |
| D3 | As metas se repetem por `ano` (linhas de 2023 e 2024 com as mesmas metas) | Silver de meta em formato longo: uma linha por local, rede e ano da meta (2024 a 2030) | Evita comparar resultado com a linha de meta errada e resolve o formato largo. |
| D4 | `alunos` e `municipio` não têm `sigla_uf` | Derivar a UF dos 2 primeiros dígitos do `id_municipio` com uma tabela de-para de 27 linhas | Código IBGE de 7 dígitos confirmado em `alunos`, `municipio` e `meta_municipio`. |

## Joins

| # | Join | Colunas | Tipos | Match | Observações |
|---|---|---|---|---|---|
| J1 | `municipio` (rede '3') × `meta_alfabetizacao_municipio` | `id_municipio` + `ano` + rede (de-para D1) | STRING / INT64 / STRING | **Medido.** Lado da meta: 2024 = 5.352/5.352 (100%); 2023 = 5.302/5.352 (99,07%). Lado de `municipio` (chaves únicas, 1:1): 2024 = 5.352/5.448 (98,24%); 2023 = 5.302/5.448 (97,32%) | Os 96 (2024) e 146 (2023) municípios sem par ficam em "sem meta". As 50 linhas da meta sem par em 2023 têm taxa nula (municípios sem resultado em 2023). |
| J2 | `uf` (rede '5') × `meta_alfabetizacao_uf` | `sigla_uf` + `ano` + rede (de-para D1) | STRING / INT64 / STRING | **Esperado.** Lado da meta, 2023-2024: 49/54 (90,7%); 2025: 0/27 (não há resultado de 2025) | DF e RR existem na meta e não em `uf`; em 2023 `uf` tem rede '5' para 24 UFs. |
| J3 | Resultado nacional × `meta_alfabetizacao_brasil` | `ano` + rede | INT64 / STRING | Sem join | Não há tabela de resultado nacional. A própria `meta_alfabetizacao_brasil` traz a taxa oficial (55,9 / 59,2 / 66,0). Somar `uf` não reproduz o nacional (sem número de alunos para ponderar). |
| J4 | `alunos` × `municipio` (validação cruzada, passo 11) | `id_municipio` + `ano` + `serie`; rede de `alunos` agregada para o código de `municipio` ('5' = alunos das redes '2' e '3') | STRING / INT64 / STRING | A medir no passo 11 | Taxa a partir de `alunos`: ponderada por `peso_aluno`, só avaliados, multiplicada por 100. |
| J5 | `municipio`/`alunos` × de-para de UF | `SUBSTR(id_municipio, 1, 2)` → `sigla_uf` | STRING | Esperado 100% para 26 prefixos | RR não aparece nas tabelas de resultado. |
| J6 | Códigos × `dicionario` | `id_tabela` + `nome_coluna` + `chave` | STRING | Esperado 100% | Filtrar a última rodada do dicionário, senão o join duplica linhas. Códigos sem tradução vão para "desconhecido". |

## Limiar proposto para o passo 5 (J1)

**Limiar bloqueante: match ≥ 95% no lado de `municipio` (rede '3'), por ano.**

- Observado: 97,32% (2023) e 98,24% (2024). Os municípios sem par não são erro de chave: são municípios sem meta pactuada e entram no estado "sem meta".
- Um erro de chave (tipo diferente, de-para de rede errado, código com formato diferente) derruba o match para perto de zero, muito abaixo de 95%.
- A folga de cerca de 2 pontos acomoda pequenas variações de cobertura entre cargas sem deixar passar uma quebra real.
