# Tabela de custo: Tech Challenge Fase 2

**Responsável:** Frente 4 · **Atualizado em:** 28/10/2026
**Projeto:** `project-ce782257-1c9c-4b6f-87a` · **Região:** `southamerica-east1` (São Paulo)

## 1. Ambiente atual: faturamento ativo, uso dentro da franquia gratuita

**O faturamento foi ativado em 28/10/2026**, numa conta de avaliação (free trial). O projeto está ligado à conta `018F61-800C0C-6090DB` ("Minha conta de faturamento"), com `billingEnabled: true` (`gcloud billing projects describe`, conferido em 28/10). Antes, o projeto rodava no **BigQuery Sandbox**, sem faturamento.

**O que mudou com o faturamento:**
- **Cobrança:** passa a existir, mas o uso medido fica bem abaixo das franquias gratuitas mensais da seção 2 (1 TiB de consulta, 10 GiB de armazenamento, 50 GiB de logs, 10 GiB de Pub/Sub). O **custo esperado é US$ 0,00**. O valor efetivo aparece no relatório de faturamento da conta.
- **Orçamento:** criado em 28/10. "TC Fase 02", mensal, só para o projeto Tech Challenge, R$ 50,00, com e-mail aos administradores de faturamento em 25%, 50%, 90% e 100% do gasto real; os créditos do free trial não são descontados. **Gasto registrado: R$ 0,00 de R$ 50,00.** Prints em `docs/evidencias/finops/`.
- **Streaming insert:** deixa de ser bloqueado, mas é cobrado. O pipeline continua gravando por *load job*, que é gratuito.

**O que não mudou:**
- **As tabelas já criadas mantêm a data de expiração** que ganharam no Sandbox: a maior parte da Bronze vence em 15/12/2026; a Silver, a Gold e parte de `ops_tc`, em 22/12/2026. As partições de `ops_tc.dq_results` expiram 60 dias depois de gravadas; em `ops_tc.pipeline_runs` essa expiração foi removida em 28/10. Os datasets não têm mais expiração padrão (`bq show`, 28/10), então tabelas novas não expiram. Remover as datas antigas exige `ALTER TABLE` feito pelo dono de cada tabela. A Gold já tem cópia em Parquet (`gold/export/`).

A tabela abaixo usa as **quantidades medidas** e os **preços de tabela da região de São Paulo**. Ela mostra quanto o mesmo desenho custa quando a franquia gratuita não cobre tudo.

## 2. Preços usados (preço de tabela, USD)

Fonte: catálogo oficial de SKUs do Google Cloud, consultado em 24/10/2026.

| Serviço | SKU | Unidade | Franquia gratuita (por conta, por mês) | Preço acima da franquia |
|---|---|---|---|---|
| BigQuery: consultas sob demanda | Analysis (southamerica-east1), 491C-41CF-D16D | TiB processado | 1 TiB | **US$ 11,25 / TiB** |
| BigQuery: armazenamento lógico ativo | Active Logical Storage (southamerica-east1), 6568-9B41-38B1 | GiB-mês | 10 GiB | US$ 0,023 / GiB-mês |
| BigQuery: armazenamento lógico de longo prazo | Long Term Logical Storage (southamerica-east1), 5ED8-561B-E2D5 | GiB-mês | 10 GiB | US$ 0,016 / GiB-mês |
| BigQuery: Storage Write API | BigQuery Storage API - Write (southamerica-east1) | GiB | 2 TiB | US$ 0,045 / GiB |
| BigQuery: load jobs (carga em lote) | — | — | gratuito | US$ 0 |
| Pub/Sub: entrega de mensagens | Message Delivery Basic, 027D-B6C7-CCA2 (global) | TiB (publicação + leitura) | 10 GiB | US$ 40 / TiB |
| Cloud Logging: armazenamento de logs | — | GiB | 50 GiB por projeto | US$ 0,50 / GiB |
| Cloud Monitoring: políticas de alerta | — | referência de métrica por mês | gratuito até 31/08/2027 | US$ 0,35 / mês a partir de 01/09/2027 |

**Atenção:** em São Paulo, a consulta custa **80% a mais que nos EUA** (US$ 11,25 contra US$ 6,25 por TiB).

## 3. Quantidades

| Item | Quantidade | Origem | Medido ou estimado |
|---|---:|---|---|
| Armazenamento lógico total (27 tabelas e 1 view) | 1,74 GiB | `__TABLES__` e INFORMATION_SCHEMA, em 28/10 (`docs/catalogo/`) | **medido** |
| Tamanho de uma carga completa da Bronze | 0,475 GiB (486 MiB) | Bronze = 972,63 MiB com 2 cargas iguais | **medido** |
| SQL da Silver (desenho atual: lê a Bronze inteira, com 2 cargas) | 1,02 GB, dos quais 1,009 GB em `silver_tc.alunos` | dry run da Frente 3 em 28/10 (README, "Custo medido") | **medido** |
| Regras de qualidade da Silver | ≈ 1,0 GB | dry run da Frente 3 em 21/10 | **medido** |
| SQL da Gold | 0,14 GB | dry run da Frente 3 em 28/10 (a validação cruzada lê `alunos`) | **medido** |
| Regras de qualidade da Gold | ≈ 0,13 GB | dry run da Frente 3 em 21/10 | **medido** |
| **Leitura por execução completa (Silver + Gold + regras)** | **≈ 2,3 GB (2,14 GiB)** | soma das quatro linhas acima, como no README da Frente 3 | **medido** |
| Mesma execução se a Silver ler só a última carga | ≈ 1,67 GiB | 0,475 GiB de uma carga + o resto (1,19 GiB) | estimado a partir de medições |
| Eventos de streaming | 5 eventos, 1 rejeitado | `bronze_tc.eventos_alunos`, `ops_tc.eventos_rejeitados` | medido (teste da Frente 2) |
| Logs do pipeline (`tc-pipeline`) | < 1 MiB/mês | 2 entradas de ~1 KB por etapa | estimado |
| Políticas de alerta | 1 (log de erro) | Etapa 3 da Frente 4 | — |

**Consumo real medido em 26/10/2026** (`ops/sql/finops/consumo_consultas_30d.sql`, sobre `INFORMATION_SCHEMA.JOBS_BY_PROJECT`), de 17/10 a 26/10, durante o desenvolvimento:

| Tipo de job | Jobs | Com erro | Faturado |
|---|---:|---:|---:|
| SELECT | 288 | 2 | 8,59 GiB |
| CREATE TABLE AS SELECT (Silver/Gold) | 69 | 2 | 6,55 GiB |
| SCRIPT | 36 | 6 | 5,18 GiB |
| ASSERT (qualidade) | 11 | 1 | 0,10 GiB |
| Outros (CREATE TABLE, sem tipo) | 14 | 6 | 0 |
| **Total de consultas** | **418** | **17** | **20,41 GiB** |
| LOAD (cargas da Bronze, gratuitas) | 34 | 0 | 0 |

Ao preço de São Paulo, 20,41 GiB custariam **US$ 0,22** sem a franquia gratuita, ou US$ 0 com ela. Nenhum desses jobs tinha o label `pipeline`, então a view `ops_tc.vw_custo_por_etapa` (criada em 26/10) ainda não separa custo por etapa.

**Histórico:** a primeira versão desta tabela (24/10) estimava ≈ 1,40 GiB por execução, supondo que a Silver lesse só a última carga. A medição da Frente 3 mostrou que a Silver lê a Bronze inteira: ≈ 2,2 GB em 26/10 e ≈ 2,3 GB em 28/10, quando entraram as regras de qualidade da Gold. A tabela usa o valor medido mais recente.

## 4. Projeção para produção (mesmo desenho, com faturamento)

**Premissas:**
- batch **diário**, ou seja, 30 execuções por mês;
- streaming de **1 evento por segundo** (2,59 milhões por mês, ~1 KB por mensagem), gravado pela **Storage Write API**. O consumer atual grava 1 load job por micro-lote de até 10 mensagens: com 1 evento por segundo, seriam pelo menos 8.640 load jobs por dia, acima da cota de 1.500 por tabela por dia;
- **1 alerta**.

São dois cenários, que mudam só na forma como a Silver lê a Bronze.

### Cenário A: desenho atual (Bronze só acumula; a Silver relê a Bronze inteira)

A Bronze recebe uma carga completa por dia e nunca apaga, o que está correto pelo enunciado. Hoje a Silver lê a Bronze inteira a cada execução: a criação de `silver_tc.alunos` leu 1,009 GB com 2 cargas na Bronze, o mesmo tamanho da tabela. Com uma carga por dia, **o volume lido cresce todo dia**.

| Serviço | Quantidade no mês 1 | Custo sem franquia | Quantidade no mês 6 | Custo sem franquia | Custo no mês 6 com franquia |
|---|---:|---:|---:|---:|---:|
| Consultas BigQuery | 285 GiB | US$ 3,13 | 2.423 GiB (2,37 TiB) | **US$ 26,62** | US$ 15,37 |
| Armazenamento BigQuery | 16 GiB | US$ 0,37 | 87 GiB | US$ 2,01 | US$ 1,78 |
| Pub/Sub | 4,83 GiB | US$ 0,19 | 4,83 GiB | US$ 0,19 | US$ 0,00 |
| Gravação do streaming (Storage Write API) | 2,47 GiB | US$ 0,11 | 2,47 GiB | US$ 0,11 | US$ 0,00 |
| Logging e Monitoring | < 1 MiB, 1 alerta | US$ 0,00 | < 1 MiB, 1 alerta | US$ 0,00* | US$ 0,00* |
| **Total mensal** | | **≈ US$ 3,80** | | **≈ US$ 28,93** | **≈ US$ 17,15** |

### Cenário B: recomendado (Bronze particionada por data de ingestão; a Silver lê só a última carga)

| Serviço | Quantidade por mês | Custo sem franquia | Custo com franquia |
|---|---:|---:|---:|
| Consultas BigQuery | 30 × 1,67 GiB = 50,0 GiB | US$ 0,55 | US$ 0,00 |
| Armazenamento BigQuery | 1,74 GiB, crescendo 0,475 GiB por carga | US$ 0,04 + US$ 0,011 por carga | US$ 0,00 até 10 GiB |
| Pub/Sub | 4,83 GiB | US$ 0,19 | US$ 0,00 |
| Gravação do streaming (Storage Write API) | 2,47 GiB | US$ 0,11 | US$ 0,00 |
| Logging e Monitoring | < 1 MiB, 1 alerta | US$ 0,00* | US$ 0,00* |
| **Total mensal** | | **≈ US$ 0,89** | **US$ 0,00** |

\* A partir de 01/09/2027, o alerta passa a custar US$ 0,35 por mês.

Os eventos do streaming também ocupam cerca de 2,5 GiB a mais de armazenamento por mês (≈ US$ 0,06 por mês, acumulando), que não estão nas linhas de armazenamento acima.

**Como fazer a conta:** custo = (quantidade − franquia) × preço. "Sem franquia" considera que a franquia gratuita já foi usada por outros projetos da mesma conta de faturamento. "Com franquia" considera o projeto sozinho na conta.

## 5. Recomendações de FinOps (com número)

1. **Particionar a Bronze por data de ingestão e fazer a Silver ler só a última carga.** É o que separa o cenário A do B: no mês 6, são **US$ 26,62 contra US$ 0,55 por mês** em consultas. O acréscimo continua, então o histórico não se perde.
2. **Ler só as colunas necessárias.** Em `bronze_tc.alunos`, ler 5 colunas em vez de `SELECT *` reduz a leitura em **81%** (962 MiB → 184 MiB, por dry run).
3. **Filtrar pela partição na Silver.** Em `silver_tc.alunos`, `WHERE ano = 2024` reduz a leitura em **45%** (794 MiB → 436 MiB). Hoje o filtro de partição não é obrigatório.
4. **Teto de bytes por consulta.** O `ops/run_logger.py` aplica `maximum_bytes_billed` = 10 GiB por consulta. Uma consulta que passar do teto falha em vez de cobrar, e a falha dispara o alerta.
5. **Recarregar só quando a fonte mudar.** Os dados oficiais são anuais. Uma carga diária igual à anterior só aumenta a Bronze em 0,475 GiB por dia.
