# Medição das tabelas: bronze, silver, gold e ops

**Projeto:** `project-ce782257-1c9c-4b6f-87a` (Tech Challenge)
**Responsável:** Frente 4 (Observabilidade + FinOps + Docs)

## Atualização de 24/10/2026: 26 tabelas

**Como foi medido:** por consulta de leitura em `INFORMATION_SCHEMA` e nas metatabelas `__TABLES__`, com a SQL em `ops/sql/catalogo/catalogo_tabelas.sql` (leu 40 MB). O detalhe por tabela está em `docs/catalogo/catalogo_dados.md` e em `docs/finops/medicoes_dry_run.csv`.

| Dataset | Tabelas | Linhas | Bytes lógicos |
|---|---:|---:|---:|
| bronze_tc | 9 | 7.805.967 | 972,63 MiB |
| silver_tc | 9 | 3.930.225 | 803,77 MiB |
| gold_tc | 6 | 58.638 | 5,41 MiB |
| ops_tc | 2 | 188 | 30,63 KiB |
| **Total** | **26** | **11.795.018** | **1.781,84 MiB (≈ 1,74 GiB)** |

**O que mudou desde 22/10:**

- **5 tabelas novas:**
  - `bronze_tc.eventos_alunos` (5 linhas)
  - `silver_tc.alunos_eventos` (5)
  - `gold_tc.indicador_por_origem` (10.897)
  - `ops_tc.eventos_rejeitados` (1)
  - `ops_tc.dq_results` (187; já existia em 22/10, mas ficou fora daquela medição)
- **A Silver e a Gold foram recriadas em 23/10, entre 19:48 e 19:49.** O tamanho delas praticamente não mudou. `silver_tc.alunos` continua com 3.867.999 linhas e 794,32 MiB.
- **A Bronze não muda desde 17/10.** `bronze_tc.alunos` continua com 7.735.998 linhas, o dobro da Silver, o que é consistente com 2 cargas em acréscimo.
- **Os bytes físicos não foram medidos de novo.** O `INFORMATION_SCHEMA.TABLE_STORAGE` não está habilitado no projeto, e habilitá-lo seria uma mudança de configuração. Os bytes físicos de 22/10 estão abaixo.
- **Particionamento no Sandbox:** `ops_tc.dq_results` é particionada por dia, e as partições dela expiram em 60 dias. É o limite do Sandbox.

---

## Medição original de 22/10/2026: 21 tabelas

**Datasets medidos:** `bronze_tc`, `silver_tc`, `gold_tc`. O `ops_tc` existia, mas ficou fora desta medição.

## Como foi medido

- **Linhas e bytes:** lidos na aba **Detalhes** de cada tabela, no console do BigQuery. Isso não executa consulta e não cria job.
- **Dry run:** consultas digitadas no editor do console, lendo a estimativa "Esta consulta vai processar…". Nenhuma foi executada, e o editor foi limpo depois.
- **Nada foi criado, alterado ou executado no projeto.**
- **Unidades:** as mesmas do console, em base binária. 1 KB = 1.024 bytes e 1 MB = 1.048.576 bytes.

## Resumo por camada

| Camada | Tabelas | Linhas | Bytes lógicos | Bytes físicos |
|---|---:|---:|---:|---:|
| bronze_tc | 8 | 7.805.962 | 972,62 MB | 83,22 MB |
| silver_tc | 8 | 3.930.220 | 803,76 MB | 108,68 MB |
| gold_tc | 5 | 47.741 | 4,56 MB | 1,21 MB |
| **Total** | **21** | **11.783.923** | **1.780,95 MB (≈ 1,74 GiB)** | **193,11 MB** |

Os **bytes lógicos** são a base de cobrança das consultas sob demanda e do armazenamento no modelo lógico, que é o padrão.

Em todas as tabelas os bytes lógicos de longo prazo estão em **0 B**. Ou seja, todo o armazenamento conta como ativo, porque as tabelas têm menos de 90 dias.

Todas as tabelas estão em **southamerica-east1** (São Paulo).

## bronze_tc

| Tabela | Linhas | Bytes lógicos | Bytes físicos | Criada | Última modificação | Expira |
|---|---:|---:|---:|---|---|---|
| alunos | 7.735.998 | 962,24 MB | 82,65 MB | 16/10 16:49 | 17/10 16:22 | 15/12/2026 |
| dicionario | 54 | 5,72 KB | 2,79 KB | 16/10 16:48 | 17/10 16:22 | 15/12/2026 |
| dicionario_copy | 54 | 5,72 KB | 2,79 KB | 18/10 11:42 | 18/10 11:42 | 17/12/2026 |
| meta_alfabetizacao_brasil | 6 | 1.020 B | 3,75 KB | 16/10 16:48 | 17/10 16:21 | 15/12/2026 |
| meta_alfabetizacao_municipio | 21.408 | 3,89 MB | 151,95 KB | 16/10 16:48 | 17/10 16:21 | 15/12/2026 |
| meta_alfabetizacao_uf | 162 | 26,43 KB | 6,57 KB | 16/10 16:48 | 17/10 16:21 | 15/12/2026 |
| municipio | 47.990 | 6,42 MB | 404,21 KB | 16/10 16:48 | 17/10 16:21 | 15/12/2026 |
| uf | 290 | 36,32 KB | 10,08 KB | 16/10 16:48 | 17/10 16:21 | 15/12/2026 |

Nenhuma tabela da Bronze é particionada.

## silver_tc

| Tabela | Linhas | Bytes lógicos | Bytes físicos | Criada | Expira |
|---|---:|---:|---:|---|---|
| alunos | 3.867.999 | 794,32 MB | 106,71 MB | 21/10 13:05 | 20/12/2026 |
| de_para_rede_meta | 2 | 27 B | 6,73 KB | 21/10 13:04 | 20/12/2026 |
| de_para_uf | 27 | 216 B | 6,24 KB | 21/10 13:04 | 20/12/2026 |
| meta_brasil | 21 | 2,87 KB | 13,78 KB | 21/10 13:04 | 20/12/2026 |
| meta_municipio | 37.464 | 4,75 MB | 330,93 KB | 21/10 13:04 | 20/12/2026 |
| meta_uf | 567 | 76,91 KB | 29,89 KB | 21/10 13:04 | 20/12/2026 |
| municipio | 23.995 | 4,59 MB | 1,54 MB | 21/10 13:04 | 20/12/2026 |
| uf | 145 | 25,72 KB | 54,35 KB | 21/10 13:04 | 20/12/2026 |

A **`silver_tc.alunos` é particionada** por intervalo de números inteiros no campo `ano`:

- intervalo de 2023 a 2031, com passo 1;
- agrupada (cluster) por `sigla_uf` e `id_municipio`;
- o filtro de partição **não é obrigatório**.

As demais tabelas da Silver não são particionadas.

## gold_tc

| Tabela | Linhas | Bytes lógicos | Bytes físicos | Criada | Expira |
|---|---:|---:|---:|---|---|
| brasil_meta | 3 | 214 B | 6,42 KB | 21/10 13:01 | 20/12/2026 |
| evolucao_municipio | 12.650 | 1.019,33 KB | 209,68 KB | 21/10 13:01 | 20/12/2026 |
| municipio_meta | 10.896 | 1,33 MB | 205,13 KB | 21/10 13:01 | 20/12/2026 |
| uf_meta | 49 | 6,73 KB | 10,35 KB | 21/10 13:01 | 20/12/2026 |
| validacao_cruzada | 24.143 | 2,23 MB | 804,41 KB | 21/10 13:01 | 20/12/2026 |

Nenhuma tabela da Gold é particionada.

## Dry run (estimativa do editor, sem executar)

| Consulta | Bytes estimados | Diferença |
|---|---:|---:|
| `SELECT * FROM bronze_tc.alunos` | 962,24 MB | referência |
| `SELECT id_municipio, serie, rede, alfabetizado, peso_aluno FROM bronze_tc.alunos` | 183,99 MB | **−81%** |
| `SELECT * FROM silver_tc.alunos` | 794,32 MB | referência |
| `SELECT * FROM silver_tc.alunos WHERE ano = 2024` | 435,56 MB | **−45%** |

O `SELECT *` estima exatamente os bytes lógicos da aba Detalhes, então as duas medições conferem.

Essas são as duas alavancas de custo que já dá para mostrar com número real:
- **ler só as colunas necessárias:** −81%;
- **filtrar pela partição:** −45%.

## Observações para o grupo

1. **A Bronze parece ter recebido duas cargas em append.** Algumas tabelas da Bronze têm exatamente o dobro de linhas da Silver correspondente:

   | Tabela | Bronze | Silver |
   |---|---:|---:|
   | alunos | 7.735.998 | 3.867.999 |
   | municipio | 47.990 | 23.995 |
   | uf | 290 | 145 |

   Além disso, as tabelas da Bronze foram criadas em 16/10 e modificadas em 17/10. Tudo isso é consistente com o teste de rodar a ingestão duas vezes. Vale a Frente 1 confirmar pelo `_ingestion_timestamp`; eu não rodei consulta para checar isso.

2. **Cada carga completa acrescenta cerca de 486 MB lógicos à Bronze** (972,62 MB ÷ 2 cargas), e a maior parte vem da tabela de alunos (≈ 481 MB por carga). Esse é o número base para projetar o crescimento do armazenamento na tabela de custo.

3. **O projeto estava no BigQuery Sandbox, sem faturamento** (situação de 24/10; em 28/10 o faturamento já estava ativo, ver `docs/finops/tabela_custo.md`, seção 1). O console mostra o aviso "Configure o faturamento". Isso tem três consequências:
   - **As tabelas expiram 60 dias após a criação.** A Bronze some em 15/12/2026 e a Silver e a Gold em 20/12/2026. Isso fica depois da entrega (03/11), mas os dados somem se a avaliação atrasar.
   - **O Sandbox não oferece streaming, nem DML de atualização ou exclusão.** Isso afeta o plano de gravar em `ops.pipeline_runs` com `insert_rows_json`, que é streaming, e também o consumidor da Frente 2.
   - **Na tabela de custo e no README**, o ambiente deve ser descrito como *Sandbox*, não como *trial*.

4. **A região é `southamerica-east1`, não US.**
   - Consultas a `INFORMATION_SCHEMA` usam `` `region-southamerica-east1`.INFORMATION_SCHEMA... ``.
   - Os preços da tabela de custo devem ser os da região de São Paulo.

5. **`bronze_tc.dicionario_copy` não está na lista das 6 tabelas + dicionário.** Ela tem o mesmo número de linhas e o mesmo tamanho do `dicionario` e foi criada em 18/10, então parece uma cópia de teste. O grupo decide se mantém; não mexi.

6. **`silver_tc.alunos` não exige filtro de partição.** Uma consulta sem `WHERE ano = ...` lê os 794 MB inteiros. Fica a sugestão para a Frente 3; não foi alterado.

7. **Folga no nível gratuito:**
   - O armazenamento total é de cerca de 1,74 GiB, abaixo dos 10 GiB gratuitos por mês.
   - Uma varredura completa de `bronze_tc.alunos` lê cerca de 0,94 GiB. O 1 TiB gratuito de consultas por mês cobre por volta de **1.090 varreduras completas**.

## Apêndice: script de medição para o repositório (`ops/medir_tabelas.py`)

O script repete esta medição de forma reproduzível. Ele usa só chamadas de metadados e dry run, então não executa consultas e não tem custo.

```python
"""Mede linhas e bytes (dry run) das tabelas das camadas. Não executa consultas."""
import csv
import os

from google.cloud import bigquery

PROJECT = os.getenv("GCP_PROJECT_ID", "project-ce782257-1c9c-4b6f-87a")
DATASETS = ["bronze_tc", "silver_tc", "gold_tc"]

client = bigquery.Client(project=PROJECT)
cfg = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)

os.makedirs("docs/finops", exist_ok=True)
with open("docs/finops/medicoes_dry_run.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["tabela", "linhas", "bytes_select_star", "mib"])
    for ds in DATASETS:
        for t in client.list_tables(f"{PROJECT}.{ds}"):
            tid = f"{PROJECT}.{ds}.{t.table_id}"
            info = client.get_table(tid)
            job = client.query(f"SELECT * FROM `{tid}`", job_config=cfg)
            w.writerow([f"{ds}.{t.table_id}", info.num_rows, job.total_bytes_processed,
                        round(job.total_bytes_processed / 1024**2, 2)])
```

Fonte sobre as limitações do Sandbox: [BigQuery sandbox limitations](https://book.st-hakky.com/en/data-analysis/bigquery-sandbox-limitations)
