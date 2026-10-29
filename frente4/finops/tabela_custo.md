# Tabela de custo: Tech Challenge Fase 2

**Responsável:** Frente 4 · **Atualizado em:** 26/10/2026
**Projeto:** `project-ce782257-1c9c-4b6f-87a` · **Região:** `southamerica-east1` (São Paulo)

## 1. Ambiente atual: BigQuery Sandbox, custo real US$ 0,00

O projeto roda no **BigQuery Sandbox**, sem conta de faturamento. O console mostra o selo "Sandbox" e o aviso "Configure o faturamento".

**O que isso significa:**
- não existe cobrança, então o custo real hoje é **US$ 0,00**;
- tabelas e partições expiram em **60 dias**;
- não há streaming insert nem orçamento (*budget*).

Mesmo assim, a tabela abaixo usa as **quantidades medidas** e os **preços de tabela da região de São Paulo**. Assim fica claro quanto o mesmo desenho custaria fora do Sandbox.

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
| Armazenamento lógico total (26 tabelas) | 1,74 GiB | `__TABLES__` e INFORMATION_SCHEMA, em 24/10 (`docs/catalogo/`) | **medido** |
| Tamanho de uma carga completa da Bronze | 0,475 GiB (486 MiB) | Bronze = 972,63 MiB com 2 cargas iguais | **medido** |
| Leitura Bronze → Silver (desenho atual: lê a Bronze inteira, com 2 cargas) | 1,009 GB (0,94 GiB) | execução da Silver em 23/10, medida pela Frente 3 (README, "Custo medido") | **medido** |
| Leitura das regras de qualidade | ≈ 1 GB (0,93 GiB) | dry run da Frente 3 em 21/10 | **medido** |
| Leitura Silver → Gold | ≈ 0,14 GB (0,13 GiB) | Frente 3 (a validação cruzada lê `alunos`) | **medido** |
| **Leitura por execução completa (Silver + qualidade + Gold)** | **≈ 2,2 GB (2,05 GiB)** | soma das três linhas acima, como no README da Frente 3 | **medido** |
| Mesma execução se a Silver ler só a última carga | ≈ 1,54 GiB | 0,475 GiB de uma carga + qualidade + Gold | estimado a partir de medições |
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

**Histórico (24/10):** a primeira versão desta tabela estimava ≈ 1,40 GiB por execução, supondo que a Silver lesse só a última carga. A medição da Frente 3 (≈ 2,2 GB) mostrou que a Silver lê a Bronze inteira, e a tabela passou a usar o valor medido.

## 4. Projeção para produção (mesmo desenho, com faturamento)

**Premissas:**
- batch **diário**, ou seja, 30 execuções por mês;
- streaming de **1 evento por segundo** (2,59 milhões por mês, ~1 KB por mensagem);
- **1 alerta**.

São dois cenários, que mudam só na forma como a Silver lê a Bronze.

### Cenário A: desenho atual (Bronze só acumula; a Silver relê a Bronze inteira)

A Bronze recebe uma carga completa por dia e nunca apaga, o que está correto pelo enunciado. Hoje a Silver lê a Bronze inteira a cada execução: a criação de `silver_tc.alunos` leu 1,009 GB com 2 cargas na Bronze, o mesmo tamanho da tabela. Com uma carga por dia, **o volume lido cresce todo dia**.

| Serviço | Quantidade no mês 1 | Custo sem franquia | Quantidade no mês 6 | Custo sem franquia | Custo no mês 6 com franquia |
|---|---:|---:|---:|---:|---:|
| Consultas BigQuery | 281 GiB | US$ 3,09 | 2.419 GiB (2,36 TiB) | **US$ 26,57** | US$ 15,32 |
| Armazenamento BigQuery | 16 GiB | US$ 0,37 | 87 GiB | US$ 2,01 | US$ 1,78 |
| Pub/Sub | 4,83 GiB | US$ 0,19 | 4,83 GiB | US$ 0,19 | US$ 0,00 |
| Logging e Monitoring | < 1 MiB, 1 alerta | US$ 0,00 | < 1 MiB, 1 alerta | US$ 0,00* | US$ 0,00* |
| **Total mensal** | | **≈ US$ 3,65** | | **≈ US$ 28,77** | **≈ US$ 17,10** |

### Cenário B: recomendado (Bronze particionada por data de ingestão; a Silver lê só a última carga)

| Serviço | Quantidade por mês | Custo sem franquia | Custo com franquia |
|---|---:|---:|---:|
| Consultas BigQuery | 30 × 1,54 GiB = 46,1 GiB | US$ 0,51 | US$ 0,00 |
| Armazenamento BigQuery | 1,74 GiB, crescendo 0,475 GiB por carga | US$ 0,04 + US$ 0,011 por carga | US$ 0,00 até 10 GiB |
| Pub/Sub | 4,83 GiB | US$ 0,19 | US$ 0,00 |
| Logging e Monitoring | < 1 MiB, 1 alerta | US$ 0,00* | US$ 0,00* |
| **Total mensal** | | **≈ US$ 0,74** | **US$ 0,00** |

\* A partir de 01/09/2027, o alerta passa a custar US$ 0,35 por mês.

**Como fazer a conta:** custo = (quantidade − franquia) × preço. "Sem franquia" considera que a franquia gratuita já foi usada por outros projetos da mesma conta de faturamento. "Com franquia" considera o projeto sozinho na conta.

## 5. Recomendações de FinOps (com número)

1. **Particionar a Bronze por data de ingestão e fazer a Silver ler só a última carga.** É o que separa o cenário A do B: no mês 6, são **US$ 26,57 contra US$ 0,51 por mês** em consultas. O acréscimo continua, então o histórico não se perde.
2. **Ler só as colunas necessárias.** Em `bronze_tc.alunos`, ler 5 colunas em vez de `SELECT *` reduz a leitura em **81%** (962 MiB → 184 MiB, por dry run).
3. **Filtrar pela partição na Silver.** Em `silver_tc.alunos`, `WHERE ano = 2024` reduz a leitura em **45%** (794 MiB → 436 MiB). Hoje o filtro de partição não é obrigatório.
4. **Teto de bytes por consulta.** O `ops/run_logger.py` aplica `maximum_bytes_billed` = 10 GiB por consulta. Uma consulta que passar do teto falha em vez de cobrar, e a falha dispara o alerta.
5. **Recarregar só quando a fonte mudar.** Os dados oficiais são anuais. Uma carga diária igual à anterior só aumenta a Bronze em 0,475 GiB por dia.
