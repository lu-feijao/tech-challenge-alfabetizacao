# Checklist de armadilhas — frente 3 (Silver, Gold e qualidade)

Revisão contra a seção "Erros comuns em pipelines de dados públicos" do enunciado, feita em 21/10/2026 com a execução real (`silver_20261021_160450_efd37f` e `gold_20261021_160141_03d23c`).

| # | Armadilha | Situação | Como foi tratada e evidência |
|---|---|---|---|
| 1 | Join que não casa não dá erro, dá nulo | ok | Match medido depois de cada join e reprovado abaixo do limiar: R04 (municipio × meta municipal, 97,32% no pior ano, limiar 95%) e R12 (uf × meta estadual, 100%, limiar 95%). Joins com dicionário e de-paras medidos pela R03 (0 sem par) |
| 2 | Chaves que "não falam a mesma língua" | ok | A rede das metas é texto (`Municipal`, `Pública`) e a dos resultados é código (`3`, `5`). De-para explícito em `silver_tc.de_para_rede_meta` (decisão D1). Tipos conferidos: `id_municipio`, `rede` e `serie` são STRING em todas as tabelas; a Silver preserva o tipo de origem |
| 3 | Preencher nulo com zero | ok | Nenhuma medida recebe valor padrão. Proporções por nível de 2023 (nulas na fonte), metas nulas e proficiência/peso de não avaliados continuam nulos. `COALESCE` só é usado para gerar a descrição `desconhecido` de códigos |
| 4 | "Sem meta" tratado como "não atingiu" | ok | 3 estados (`atingiu`, `nao_atingiu`, `sem_meta`) mais a coluna `motivo_sem_meta` (metas começam em 2024, sem meta pactuada, meta nula na fonte). G01 e G02 garantem que nenhum status é calculado sem taxa e meta |
| 5 | Média simples entre municípios como indicador nacional | ok | A Gold não agrega municípios. O indicador nacional vem da própria fonte (`meta_alfabetizacao_brasil`) e o recálculo nacional usa o microdado com peso amostral |
| 6 | Misturar recortes de rede e série | ok | Municípios comparados só na rede Municipal (`3`) com a meta municipal; UFs e Brasil só na rede Pública (`5`) com as metas pública; todos no 2º ano (`serie = '2'`). Redes agregadas (`0`, `5`, `6`) nunca são somadas |
| 7 | Denominador errado | ok | Coluna `avaliado` (tem peso amostral) em `silver_tc.alunos`. Validação cruzada Brasil 2024: 59,20 recalculado = 59,2 oficial; com o denominador errado (todos os registros) daria 52,21 |
| 8 | Fallback que apaga informação | ok | Código sem tradução vira `desconhecido`, e a R03 (bloqueante) exige contagem zero |
| 9 | Projeção até 2030 com 2 ou 3 anos | ok (não usado) | Nenhuma projeção foi construída. As metas 2024 a 2030 aparecem como trajetória pactuada da fonte (meta 2030 = 80), não como previsão |
| 10 | Exceção engolida por `except` genérico | ok | Só a exceção específica `RegraBloqueanteReprovada` é tratada, e o script devolve código 1. Erros de SQL não são capturados. Falha demonstrada: `docs/evidencias/falha_demonstrada/` |
| 11 | Leitura da meta de 2030 (pactuada x universalização) | ok | Só a meta pactuada da fonte é usada; a leitura aspiracional (100%) não aparece na Gold |
| 12 | Vazamento de alvo na base de features (Fase 3) | atenção | `status_meta` e `distancia_meta` são derivados de `taxa_alfabetizacao`. Se a taxa for o alvo do modelo na Fase 3, essas colunas não podem entrar como features. Registrar na seção "Aplicação em IA" do README |
| 13 | Latência sempre zero no streaming | n/a | Fora do escopo da frente 3 (frente 2) |

## Achados documentados (diferencial "investigação documentada")

- **Brasil 2023:** o recálculo a partir do microdado dá 57,46, e a tabela `meta_alfabetizacao_brasil` publica 55,9 (+1,56 p.p.). UFs e municípios de 2023 batem com o microdado, então a divergência está no número nacional de 2023 da tabela de meta, não no pipeline. Causa não confirmada.
- **Taxas de 2023 na meta municipal x `municipio`:** só 62,5% iguais com tolerância de 0,01 (R09, informativa). As duas ficam a cerca de 0,04 p.p. do microdado, em média: diferenças pequenas, compatíveis com arredondamento (hipótese).
- **Cobertura:** DF e RR não aparecem em `uf`; RR não aparece em `municipio`; 18 alunos com caderno `43` (todos do ES, 2024).
