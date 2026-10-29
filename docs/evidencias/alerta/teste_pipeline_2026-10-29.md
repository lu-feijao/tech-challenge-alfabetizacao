# Evidência: métricas de execução e alerta com o pipeline real (29/10/2026)

Primeira execução da Silver e da Gold com o registro de métricas ([`ops/run_logger.py`](../../../ops/run_logger.py)). Três execuções seguidas, a partir da raiz do repositório (horários em UTC; Brasília = UTC−3):

| # | Comando | `execucao_id` | Resultado | Etapas em `pipeline_runs` |
|---|---|---|---|---|
| 1 | `python silver/silver_transformacao.py --simular-falha` | `silver_20261029_203436_1ab15d` | R04 reprovada (97,32% contra o limiar de 99,9%), código de saída 1 | 11, 1 com falha (`regras_bloqueantes`) |
| 2 | `python silver/silver_transformacao.py` | `silver_20261029_203556_4491c4` | todas as bloqueantes aprovadas | 10, 0 com falha |
| 3 | `python gold/gold_transformacao.py` | `gold_20261029_203709_d24b2e` | portão aberto, todas as bloqueantes aprovadas | 8, 0 com falha |

## Do erro ao e-mail

| Momento (UTC) | O quê | Fonte |
|---|---|---|
| 20:35:40 | etapa `regras_bloqueantes` gravada com `status = 'falha'` e ERROR escrito no log `tc-pipeline` | `ops_tc.pipeline_runs` |
| 20:35:55 | alerta "Pipeline TC - falha" aberto (**15 s depois**) | Cloud Monitoring |
| 20:35 | e-mail "[ALERT - Error] Pipeline TC - falha" recebido no canal da frente 4 | prints [`2026-10-29_email_alerta_1.png`](2026-10-29_email_alerta_1.png) e [`2026-10-29_email_alerta_2.png`](2026-10-29_email_alerta_2.png) |

Mensagem gravada em `pipeline_runs.erro`: `1 regra(s) bloqueante(s) reprovada(s): R04 municipio x meta_municipio (valor 97.32011747430249, limiar >= 99.9)`.

## Etapas da Silver normal (execução 2)

| Etapa | Tabela | Duração (s) | Linhas de entrada | Linhas de saída | Faturado (GB) |
|---|---|---:|---:|---:|---:|
| 01_de_para | silver_tc.de_para_uf | 3,1 | — | 29 | 0,000 |
| 02_municipio | silver_tc.municipio | 2,2 | 48.071 | 23.995 | 0,031 |
| 03_meta_municipio | silver_tc.meta_municipio | 2,0 | 21.437 | 37.464 | 0,031 |
| 04_uf | silver_tc.uf | 1,7 | 371 | 145 | 0,031 |
| 05_meta_uf | silver_tc.meta_uf | 1,6 | 191 | 567 | 0,031 |
| 06_meta_brasil | silver_tc.meta_brasil | 1,6 | 8 | 21 | 0,021 |
| 07_alunos | silver_tc.alunos | 8,6 | 7.736.079 | 3.867.999 | 1,010 |
| 08_alunos_eventos | silver_tc.alunos_eventos | 1,5 | 37 | 10 | 0,021 |
| regras_qualidade | — | 37,1 | 47 regras | 47 resultados | 0,989 |
| gravar_dq_results | ops_tc.dq_results | 2,9 | — | 47 | 0,000 |

Linhas de entrada = soma das linhas das tabelas que o SQL lê (a Bronze tem as 2 cargas; a Silver usa só a mais recente). As linhas de saída maiores que as de entrada nas metas vêm da passagem do formato largo para o longo (uma linha por ano de meta).

## Totais por execução

| Execução | Duração somada das etapas | Faturado |
|---|---:|---:|
| Silver | 62,2 s | 2,166 GB |
| Gold | 23,1 s | 0,368 GB |
| **Silver + Gold** | **≈ 85 s** | **≈ 2,53 GB** |

O faturado fica acima dos ≈ 2,3 GB processados (seção 3.2 do README) porque o BigQuery cobra no mínimo 10 MB por consulta, e cada execução completa faz 75 consultas (14 SQL e 61 regras).

## Custo por etapa

A view `ops_tc.vw_custo_por_etapa` passou a separar o custo por camada e etapa, porque os jobs da Silver e da Gold agora levam os labels `pipeline`/`camada`/`etapa`. As etapas mais caras são `silver/07_alunos` e `silver/regras_qualidade` (≈ 0,9 GiB cada por execução). Nos últimos 30 dias, as duas somam ≈ US$ 0,04 a preço de tabela.

## Como conferir

```sql
SELECT execucao_id, etapa, status, duracao_seg, linhas_entrada, linhas_saida, bytes_faturados, erro
FROM `project-ce782257-1c9c-4b6f-87a.ops_tc.pipeline_runs`
WHERE DATE(inicio) = '2026-10-29' AND etapa != 'teste_frente4'
ORDER BY inicio;
```
