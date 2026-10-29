# Regras de qualidade (frente 3)

Implementadas em `quality/regras.py` e executadas por `silver/silver_transformacao.py` e `gold/gold_transformacao.py`.

- **Bloqueante:** se reprovar, o script termina com código 1. A Gold consulta `ops.dq_results` antes de rodar e não é publicada se a última execução da Silver tiver alguma bloqueante reprovada.
- **Informativa:** o resultado é registrado e a execução segue.
- **Registro:** toda regra, aprovada ou não, vira uma linha em `ops.dq_results` (execução, horário, camada, tabela, regra, severidade, valor medido, limiar e status), gravada por load job em modo append, e uma cópia em `docs/evidencias/dq_<execucao>.csv`.

## Silver (e Bronze)

| ID | Tipo | Regra | Onde | Limiar |
|---|---|---|---|---|
| R07 | Bloqueante | Carga completa: a última rodada da Bronze tem pelo menos 95% das linhas da anterior | as 7 tabelas da Bronze | ≥ 95% |
| R01 | Bloqueante | Chave única (duplicidade) | as 6 tabelas da Silver | 0 duplicadas |
| R02 | Bloqueante | Sem nulo em coluna de chave | as 6 tabelas da Silver | 0 |
| R03 | Bloqueante | Nenhum código sem tradução ("desconhecido") e nenhuma UF sem de-para | as 6 tabelas da Silver | 0 |
| R04 | Bloqueante | Match `municipio` (rede 3) × `meta_municipio`, lado de `municipio`, pior ano | J1 | ≥ 95% |
| R12 | Bloqueante | Match `uf` (rede 5) × `meta_uf`, lado de `uf`, pior ano | J2 | ≥ 95% |
| R05 | Bloqueante | Taxas e metas entre 0 e 100; proficiência e peso > 0 | 6 tabelas | 0 violações |
| R06 | Bloqueante | Proficiência e peso nulos nas mesmas linhas (define quem é avaliado) | alunos | 0 |
| R08 | Informativa | Soma das 9 proporções de nível = 100 ± 0,05 | municipio, uf (só 2024 tem proporções) | 0 violações |
| R09 | Informativa | % de municípios com taxa da meta municipal = taxa de `municipio` (tolerância 0,01) | meta_municipio × municipio | ≥ 95% |
| R10 | Informativa | Cadernos fora da faixa 1 a 21 | alunos | 0 |
| R11 | Informativa | UFs com resultado em `uf` | uf | 27 |

## Gold

| ID | Tipo | Regra | Onde | Limiar |
|---|---|---|---|---|
| G01 | Bloqueante | Status de meta só é calculado com taxa e meta preenchidas | municipio_meta, uf_meta, brasil_meta | 0 |
| G02 | Bloqueante | Status de meta é sempre um dos 3 estados | municipio_meta, uf_meta, brasil_meta | 0 |
| R13 | Informativa | Municípios em "sem_meta" em 2024 | municipio_meta | só medição |
| V01 | Informativa | Validação cruzada Brasil 2024: diferença entre taxa recalculada e oficial | validacao_cruzada | ≤ 0,5 p.p. |
| V02 | Informativa | Validação cruzada municípios 2024: % a até 0,5 p.p. da oficial | validacao_cruzada | ≥ 95% |

## Eventos de streaming (silver.alunos_eventos e gold.indicador_por_origem)

Entram na execução só quando `bronze_tc.eventos_alunos` (Silver) ou `silver_tc.alunos_eventos` (Gold) existem.

| ID | Tipo | Regra | Onde | Limiar |
|---|---|---|---|---|
| E01 | Bloqueante | Chave única: um `id_evento` por linha (deduplicação) | alunos_eventos | 0 duplicadas |
| E02 | Bloqueante | Sem nulo em `id_evento`, `origem`, `id_municipio`, `id_aluno`, `ano` e horários | alunos_eventos | 0 |
| E03 | Bloqueante | Toda linha tem `origem = 'simulado'` | alunos_eventos | 0 violações |
| E04 | Bloqueante | Latência medida e maior que zero (carimbos iguais dariam zero e a medida não mediria nada) | alunos_eventos | 0 violações |
| E05 | Bloqueante | `alfabetizado` coerente com a proficiência (corte de 743) | alunos_eventos | 0 |
| E06 | Bloqueante | Proficiência entre 0 e 1000 e peso > 0 | alunos_eventos | 0 |
| E07 | Bloqueante | Match evento × município (`silver.municipio`) e UF com de-para | alunos_eventos | ≥ 95% |
| E08 | Informativa | Linhas repetidas por `id_evento` removidas da Bronze de eventos | alunos_eventos | só medição |
| G03 | Bloqueante | `origem` sempre `oficial` ou `simulado` | indicador_por_origem | 0 |
| G04 | Bloqueante | Chave única por origem, ano, município, série e rede | indicador_por_origem | 0 |
| G05 | Bloqueante | Os eventos simulados chegaram à Gold | indicador_por_origem | ≥ 1 linha |
| G06 | Bloqueante | Taxa entre 0 e 100 nas duas origens | indicador_por_origem | 0 |
| G07 | Informativa | Eventos simulados não usam anos do indicador oficial | indicador_por_origem | 0 anos em comum |

Resultado da execução de 23/10/2026: todas aprovadas; E08 = 0 (o consumer já havia deduplicado em memória, então a Bronze não tinha repetição).

## Justificativa dos limiares de match

- **R04 (95%):** observado 97,32% (2023) e 98,24% (2024). Os municípios sem par não são erro de chave: não têm meta pactuada e entram no estado "sem meta". Um erro real de chave (tipo, de-para de rede, formato do código) derruba o match para perto de zero.
- **R12 (95%):** toda UF com resultado público tem meta (100% observado). Do lado da meta o match é menor (DF e RR têm meta, mas não aparecem em `uf`), e isso é registrado como informação de cobertura (R11).

## Resultados esperados com a Bronze atual

Todas as bloqueantes aprovam. Informativas que reprovam de propósito, mostrando que informativa não para o pipeline: R09 (taxas de 2023 divergem entre as duas tabelas da fonte), R10 (18 cadernos "43") e R11 (25 UFs: sem DF e RR).

## Falha demonstrada (passo 9)

`python silver/silver_transformacao.py --simular-falha` eleva o limiar da R04 para 99,9%. A R04 reprova (o match real é 97,32%), o resultado fica gravado em `ops.dq_results`, o script termina com código 1 e a Gold se recusa a rodar até uma nova execução aprovada da Silver.
