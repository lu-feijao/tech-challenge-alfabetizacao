# Catálogo de dados

**Projeto:** `project-ce782257-1c9c-4b6f-87a` · **Região:** `southamerica-east1` · **Gerado em:** 24/10/2026 22:35

Gerado por `ops/gerar_catalogo.py` a partir de `ops/sql/catalogo/catalogo_tabelas.sql`. A consulta só lê o INFORMATION_SCHEMA.

O **dono provável** e a **finalidade** de cada tabela foram inferidos pela Frente 4 a partir do nome e das colunas. O dono de cada tabela deve confirmar ou corrigir esses campos em `INFO`, dentro de `ops/gerar_catalogo.py`.

## Resumo por dataset

| Dataset | Camada | Tabelas | Linhas | Bytes lógicos |
|---|---|---:|---:|---:|
| `bronze_tc` | Bronze | 9 | 7.805.967 | 972,63 MiB |
| `silver_tc` | Silver | 9 | 3.930.225 | 803,77 MiB |
| `gold_tc` | Gold | 6 | 58.638 | 5,41 MiB |
| `ops_tc` | Operação | 2 | 188 | 30,63 KiB |
| **Total** | | **26** | **11.795.018** | **1.781,84 MiB** |

## Tabelas

| Tabela | Dono provável | Linhas | Bytes lógicos | Partição / cluster | Expira |
|---|---|---:|---:|---|---|
| [`bronze_tc.alunos`](#bronze_tcalunos) | Frente 1 | 7.735.998 | 962,24 MiB | — | 15/12/2026 |
| [`bronze_tc.dicionario`](#bronze_tcdicionario) | Frente 1 | 54 | 5,72 KiB | — | 15/12/2026 |
| [`bronze_tc.dicionario_copy`](#bronze_tcdicionario_copy) | a confirmar | 54 | 5,72 KiB | — | 17/12/2026 |
| [`bronze_tc.eventos_alunos`](#bronze_tceventos_alunos) | Frente 2 | 5 | 1,09 KiB | — | 22/12/2026 |
| [`bronze_tc.meta_alfabetizacao_brasil`](#bronze_tcmeta_alfabetizacao_brasil) | Frente 1 | 6 | 1020 B | — | 15/12/2026 |
| [`bronze_tc.meta_alfabetizacao_municipio`](#bronze_tcmeta_alfabetizacao_municipio) | Frente 1 | 21.408 | 3,89 MiB | — | 15/12/2026 |
| [`bronze_tc.meta_alfabetizacao_uf`](#bronze_tcmeta_alfabetizacao_uf) | Frente 1 | 162 | 26,43 KiB | — | 15/12/2026 |
| [`bronze_tc.municipio`](#bronze_tcmunicipio) | Frente 1 | 47.990 | 6,42 MiB | — | 15/12/2026 |
| [`bronze_tc.uf`](#bronze_tcuf) | Frente 1 | 290 | 36,32 KiB | — | 15/12/2026 |
| [`gold_tc.brasil_meta`](#gold_tcbrasil_meta) | Frente 3 | 3 | 214 B | — | 22/12/2026 |
| [`gold_tc.evolucao_municipio`](#gold_tcevolucao_municipio) | Frente 3 | 12.650 | 1.019,33 KiB | — | 22/12/2026 |
| [`gold_tc.indicador_por_origem`](#gold_tcindicador_por_origem) | Frente 2 / Frente 3 | 10.897 | 872,67 KiB | — | 22/12/2026 |
| [`gold_tc.municipio_meta`](#gold_tcmunicipio_meta) | Frente 3 | 10.896 | 1,33 MiB | — | 22/12/2026 |
| [`gold_tc.uf_meta`](#gold_tcuf_meta) | Frente 3 | 49 | 6,73 KiB | — | 22/12/2026 |
| [`gold_tc.validacao_cruzada`](#gold_tcvalidacao_cruzada) | Frente 3 | 24.143 | 2,23 MiB | — | 22/12/2026 |
| [`ops_tc.dq_results`](#ops_tcdq_results) | Frente 3 | 187 | 29,95 KiB | executado_em | partições expiram em 60 dias |
| [`ops_tc.eventos_rejeitados`](#ops_tceventos_rejeitados) | Frente 2 | 1 | 694 B | — | 22/12/2026 |
| [`silver_tc.alunos`](#silver_tcalunos) | Frente 3 | 3.867.999 | 794,32 MiB | ano / sigla_uf,id_municipio | 22/12/2026 |
| [`silver_tc.alunos_eventos`](#silver_tcalunos_eventos) | Frente 2 | 5 | 1,09 KiB | — | 22/12/2026 |
| [`silver_tc.de_para_rede_meta`](#silver_tcde_para_rede_meta) | Frente 3 | 2 | 27 B | — | 22/12/2026 |
| [`silver_tc.de_para_uf`](#silver_tcde_para_uf) | Frente 3 | 27 | 216 B | — | 22/12/2026 |
| [`silver_tc.meta_brasil`](#silver_tcmeta_brasil) | Frente 3 | 21 | 2,87 KiB | — | 22/12/2026 |
| [`silver_tc.meta_municipio`](#silver_tcmeta_municipio) | Frente 3 | 37.464 | 4,75 MiB | — | 22/12/2026 |
| [`silver_tc.meta_uf`](#silver_tcmeta_uf) | Frente 3 | 567 | 76,91 KiB | — | 22/12/2026 |
| [`silver_tc.municipio`](#silver_tcmunicipio) | Frente 3 | 23.995 | 4,59 MiB | — | 22/12/2026 |
| [`silver_tc.uf`](#silver_tcuf) | Frente 3 | 145 | 25,72 KiB | — | 22/12/2026 |

### `bronze_tc.alunos`

Microdados de alunos da avaliação estadual, como vieram da fonte. Acréscimo a cada carga, com _ingestion_timestamp e _source.

- **Camada:** Bronze · **Dono provável:** Frente 1
- **Linhas:** 7.735.998 · **Bytes lógicos:** 962,24 MiB
- **Criada em:** 2026-10-16 16:49 · **Última modificação:** 2026-10-17 16:22 · **Expira:** 15/12/2026
- **DDL:** [`ddl/bronze_tc.alunos.sql`](ddl/bronze_tc.alunos.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano` | INT64 | não | Ano de aplicação da avaliação estadual |
| 2 | `id_municipio` | STRING | não | ID Município de 7 dígitos |
| 3 | `id_escola` | STRING | não | Máscara do código da escola (códigos fictícios) |
| 4 | `id_aluno` | STRING | não | Código do aluno |
| 5 | `caderno` | STRING | não | Código do caderno atribuído ao aluno na prova de língua portuguesa |
| 6 | `serie` | STRING | não | Ano escolar |
| 7 | `rede` | STRING | não | Dependência administrativa da escola |
| 8 | `presenca` | STRING | não | Indicador de presença na prova de língua portuguesa |
| 9 | `preenchimento_caderno` | STRING | não | Indicador de preenchimento da prova de língua portuguesa |
| 10 | `alfabetizado` | STRING | não | Indica se o aluno, mediante o resultado da avaliação estadual, é considerado alfabetizado |
| 11 | `proficiencia` | FLOAT64 | não | Proficiência do aluno em língua portuguesa calculada na escala equalizada com o SAEB |
| 12 | `peso_aluno` | FLOAT64 | não | Peso do aluno na prova de língua portuguesa |
| 13 | `_ingestion_timestamp` | TIMESTAMP | não | Timestamp de ingestão da tabela |
| 14 | `_source` | STRING | não | Origem da tabela |

### `bronze_tc.dicionario`

Dicionário de códigos da fonte (id_tabela, nome_coluna, chave → valor).

- **Camada:** Bronze · **Dono provável:** Frente 1
- **Linhas:** 54 · **Bytes lógicos:** 5,72 KiB
- **Criada em:** 2026-10-16 16:48 · **Última modificação:** 2026-10-17 16:22 · **Expira:** 15/12/2026
- **DDL:** [`ddl/bronze_tc.dicionario.sql`](ddl/bronze_tc.dicionario.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `id_tabela` | STRING | não |  |
| 2 | `nome_coluna` | STRING | não |  |
| 3 | `chave` | STRING | não |  |
| 4 | `cobertura_temporal` | STRING | não |  |
| 5 | `valor` | STRING | não |  |
| 6 | `_ingestion_timestamp` | TIMESTAMP | não |  |
| 7 | `_source` | STRING | não |  |

### `bronze_tc.dicionario_copy`

Mesmo conteúdo de bronze_tc.dicionario (54 linhas), criada em 18/10. Parece cópia de teste.

- **Camada:** Bronze · **Dono provável:** a confirmar
- **Linhas:** 54 · **Bytes lógicos:** 5,72 KiB
- **Criada em:** 2026-10-18 11:42 · **Última modificação:** 2026-10-18 11:42 · **Expira:** 17/12/2026
- **DDL:** [`ddl/bronze_tc.dicionario_copy.sql`](ddl/bronze_tc.dicionario_copy.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `id_tabela` | STRING | não |  |
| 2 | `nome_coluna` | STRING | não |  |
| 3 | `chave` | STRING | não |  |
| 4 | `cobertura_temporal` | STRING | não |  |
| 5 | `valor` | STRING | não |  |
| 6 | `_ingestion_timestamp` | TIMESTAMP | não |  |
| 7 | `_source` | STRING | não |  |

### `bronze_tc.eventos_alunos`

Eventos simulados de alunos recebidos pelo streaming, com origem, horário de produção, horário de recebimento e latência.

- **Camada:** Bronze · **Dono provável:** Frente 2
- **Linhas:** 5 · **Bytes lógicos:** 1,09 KiB
- **Criada em:** 2026-10-23 19:16 · **Última modificação:** 2026-10-23 19:17 · **Expira:** 22/12/2026
- **DDL:** [`ddl/bronze_tc.eventos_alunos.sql`](ddl/bronze_tc.eventos_alunos.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `id_evento` | STRING | não |  |
| 2 | `origem` | STRING | não |  |
| 3 | `horario_producao` | TIMESTAMP | não |  |
| 4 | `horario_recebimento` | TIMESTAMP | não |  |
| 5 | `latencia_segundos` | FLOAT64 | não |  |
| 6 | `ano` | INT64 | não |  |
| 7 | `id_municipio` | STRING | não |  |
| 8 | `cod_uf` | STRING | não |  |
| 9 | `sigla_uf` | STRING | não |  |
| 10 | `id_escola` | STRING | não |  |
| 11 | `id_aluno` | STRING | não |  |
| 12 | `caderno` | STRING | não |  |
| 13 | `serie` | STRING | não |  |
| 14 | `serie_descricao` | STRING | não |  |
| 15 | `rede` | STRING | não |  |
| 16 | `rede_descricao` | STRING | não |  |
| 17 | `presenca` | STRING | não |  |
| 18 | `presenca_descricao` | STRING | não |  |
| 19 | `preenchimento_caderno` | STRING | não |  |
| 20 | `preenchimento_caderno_descricao` | STRING | não |  |
| 21 | `alfabetizado` | STRING | não |  |
| 22 | `alfabetizado_descricao` | STRING | não |  |
| 23 | `avaliado` | BOOL | não |  |
| 24 | `proficiencia` | FLOAT64 | não |  |
| 25 | `peso_aluno` | FLOAT64 | não |  |

### `bronze_tc.meta_alfabetizacao_brasil`

Taxa de alfabetização e metas 2024–2030 para o Brasil, por rede.

- **Camada:** Bronze · **Dono provável:** Frente 1
- **Linhas:** 6 · **Bytes lógicos:** 1020 B
- **Criada em:** 2026-10-16 16:48 · **Última modificação:** 2026-10-17 16:21 · **Expira:** 15/12/2026
- **DDL:** [`ddl/bronze_tc.meta_alfabetizacao_brasil.sql`](ddl/bronze_tc.meta_alfabetizacao_brasil.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano` | INT64 | não | Ano da avaliação |
| 2 | `rede` | STRING | não | Rede de ensino |
| 3 | `taxa_alfabetizacao` | FLOAT64 | não | Percentual dos alunos avaliados no estado que foram considerados, mediante o resultado da avaliação estadual, como alfabetizados |
| 4 | `meta_alfabetizacao_2024` | FLOAT64 | não | Meta de alfabetização no ano de 2024 |
| 5 | `meta_alfabetizacao_2025` | FLOAT64 | não | Meta de alfabetização no ano de 2025 |
| 6 | `meta_alfabetizacao_2026` | FLOAT64 | não | Meta de alfabetização no ano de 2026 |
| 7 | `meta_alfabetizacao_2027` | FLOAT64 | não | Meta de alfabetização no ano de 2027 |
| 8 | `meta_alfabetizacao_2028` | FLOAT64 | não | Meta de alfabetização no ano de 2028 |
| 9 | `meta_alfabetizacao_2029` | FLOAT64 | não | Meta de alfabetização no ano de 2029 |
| 10 | `meta_alfabetizacao_2030` | FLOAT64 | não | Meta de alfabetização no ano de 2030 |
| 11 | `percentual_participacao` | FLOAT64 | não | Percentual de participação no estado |
| 12 | `_ingestion_timestamp` | TIMESTAMP | não | Timestamp de ingestão da tabela |
| 13 | `_source` | STRING | não | Origem da tabela |

### `bronze_tc.meta_alfabetizacao_municipio`

Taxa de alfabetização e metas 2024–2030 por município e rede.

- **Camada:** Bronze · **Dono provável:** Frente 1
- **Linhas:** 21.408 · **Bytes lógicos:** 3,89 MiB
- **Criada em:** 2026-10-16 16:48 · **Última modificação:** 2026-10-17 16:21 · **Expira:** 15/12/2026
- **DDL:** [`ddl/bronze_tc.meta_alfabetizacao_municipio.sql`](ddl/bronze_tc.meta_alfabetizacao_municipio.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano` | INT64 | não | Ano da avaliação |
| 2 | `id_municipio` | STRING | não | Sigla da unidade da federação |
| 3 | `rede` | STRING | não | Rede de ensino |
| 4 | `taxa_alfabetizacao` | FLOAT64 | não | Percentual dos alunos avaliados no estado que foram considerados, mediante o resultado da avaliação estadual, como alfabetizados |
| 5 | `meta_alfabetizacao_2024` | FLOAT64 | não | Meta de alfabetização no ano de 2024 |
| 6 | `meta_alfabetizacao_2025` | FLOAT64 | não | Meta de alfabetização no ano de 2025 |
| 7 | `meta_alfabetizacao_2026` | FLOAT64 | não | Meta de alfabetização no ano de 2026 |
| 8 | `meta_alfabetizacao_2027` | FLOAT64 | não | Meta de alfabetização no ano de 2027 |
| 9 | `meta_alfabetizacao_2028` | FLOAT64 | não | Meta de alfabetização no ano de 2028 |
| 10 | `meta_alfabetizacao_2029` | FLOAT64 | não | Meta de alfabetização no ano de 2029 |
| 11 | `meta_alfabetizacao_2030` | FLOAT64 | não | Meta de alfabetização no ano de 2030 |
| 12 | `nivel_alfabetizacao` | INT64 | não | Nível de alfabetização |
| 13 | `percentual_participacao` | FLOAT64 | não | Percentual de participação por município |
| 14 | `_ingestion_timestamp` | TIMESTAMP | não | Timestamp de ingestão da tabela |
| 15 | `_source` | STRING | não | Origem da tabela |

### `bronze_tc.meta_alfabetizacao_uf`

Taxa de alfabetização e metas 2024–2030 por UF e rede.

- **Camada:** Bronze · **Dono provável:** Frente 1
- **Linhas:** 162 · **Bytes lógicos:** 26,43 KiB
- **Criada em:** 2026-10-16 16:48 · **Última modificação:** 2026-10-17 16:21 · **Expira:** 15/12/2026
- **DDL:** [`ddl/bronze_tc.meta_alfabetizacao_uf.sql`](ddl/bronze_tc.meta_alfabetizacao_uf.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano` | INT64 | não | Ano da avaliação |
| 2 | `sigla_uf` | STRING | não | Sigla da unidade da federação |
| 3 | `rede` | STRING | não | Rede de ensino |
| 4 | `taxa_alfabetizacao` | FLOAT64 | não | Percentual dos alunos avaliados no estado que foram considerados, mediante o resultado da avaliação estadual, como alfabetizados |
| 5 | `meta_alfabetizacao_2024` | FLOAT64 | não | Meta de alfabetização no ano de 2024 |
| 6 | `meta_alfabetizacao_2025` | FLOAT64 | não | Meta de alfabetização no ano de 2025 |
| 7 | `meta_alfabetizacao_2026` | FLOAT64 | não | Meta de alfabetização no ano de 2026 |
| 8 | `meta_alfabetizacao_2027` | FLOAT64 | não | Meta de alfabetização no ano de 2027 |
| 9 | `meta_alfabetizacao_2028` | FLOAT64 | não | Meta de alfabetização no ano de 2028 |
| 10 | `meta_alfabetizacao_2029` | FLOAT64 | não | Meta de alfabetização no ano de 2029 |
| 11 | `meta_alfabetizacao_2030` | FLOAT64 | não | Meta de alfabetização no ano de 2030 |
| 12 | `percentual_participacao` | FLOAT64 | não | Percentual de participação no estado |
| 13 | `_ingestion_timestamp` | TIMESTAMP | não | Timestamp de ingestão da tabela |
| 14 | `_source` | STRING | não | Origem da tabela |

### `bronze_tc.municipio`

Resultado por município: taxa de alfabetização, média em português e proporção de alunos por nível.

- **Camada:** Bronze · **Dono provável:** Frente 1
- **Linhas:** 47.990 · **Bytes lógicos:** 6,42 MiB
- **Criada em:** 2026-10-16 16:48 · **Última modificação:** 2026-10-17 16:21 · **Expira:** 15/12/2026
- **DDL:** [`ddl/bronze_tc.municipio.sql`](ddl/bronze_tc.municipio.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano` | INT64 | não | Ano de aplicação da avaliação estadual |
| 2 | `id_municipio` | STRING | não | ID Município |
| 3 | `serie` | STRING | não | Ano escolar |
| 4 | `rede` | STRING | não | Rede de ensino |
| 5 | `taxa_alfabetizacao` | FLOAT64 | não | Percentual dos alunos avaliados no município que foram considerados, mediante o resultado da avaliação estadual, como alfabetizados |
| 6 | `media_portugues` | FLOAT64 | não | Média ponderada do município na avaliação estadual na disciplina Língua Portuguesa (LP) equalizada com o SAEB |
| 7 | `proporcao_aluno_nivel_0` | FLOAT64 | não | Percentual de alunos avaliados no município que foram alocados no nível de desempenho 0 na avaliação estadual de Lingua Portuguesa (LP) |
| 8 | `proporcao_aluno_nivel_1` | FLOAT64 | não | Percentual de alunos avaliados no município que foram alocados no nível de desempenho 1 na avaliação estadual de Lingua Portuguesa (LP) |
| 9 | `proporcao_aluno_nivel_2` | FLOAT64 | não | Percentual de alunos avaliados no município que foram alocados no nível de desempenho 2 na avaliação estadual de Lingua Portuguesa (LP) |
| 10 | `proporcao_aluno_nivel_3` | FLOAT64 | não | Percentual de alunos avaliados no município que foram alocados no nível de desempenho 3 na avaliação estadual de Língua Portuguesa (LP) |
| 11 | `proporcao_aluno_nivel_4` | FLOAT64 | não | Percentual de alunos avaliados no município que foram alocados no nível de desempenho 3 na avaliação estadual de Lingua Portuguesa (LP) |
| 12 | `proporcao_aluno_nivel_5` | FLOAT64 | não | Percentual de alunos avaliados no município que foram alocados no nível de desempenho 4 na avaliação estadual de Lingua Portuguesa (LP) |
| 13 | `proporcao_aluno_nivel_6` | FLOAT64 | não | Percentual de alunos avaliados no município que foram alocados no nível de desempenho 5 na avaliação estadual de Lingua Portuguesa (LP) |
| 14 | `proporcao_aluno_nivel_7` | FLOAT64 | não | Percentual de alunos avaliados no município que foram alocados no nível de desempenho 6 na avaliação estadual de Lingua Portuguesa (LP) |
| 15 | `proporcao_aluno_nivel_8` | FLOAT64 | não | Percentual de alunos avaliados no município que foram alocados no nível de desempenho 7 na avaliação estadual de Lingua Portuguesa (LP) |
| 16 | `_ingestion_timestamp` | TIMESTAMP | não | Timestamp de ingestão da tabela |
| 17 | `_source` | STRING | não | Origem da tabela |

### `bronze_tc.uf`

Resultado por UF: taxa de alfabetização, média em português e proporção de alunos por nível.

- **Camada:** Bronze · **Dono provável:** Frente 1
- **Linhas:** 290 · **Bytes lógicos:** 36,32 KiB
- **Criada em:** 2026-10-16 16:48 · **Última modificação:** 2026-10-17 16:21 · **Expira:** 15/12/2026
- **DDL:** [`ddl/bronze_tc.uf.sql`](ddl/bronze_tc.uf.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano` | INT64 | não | Ano de aplicação da avaliação estadual |
| 2 | `sigla_uf` | STRING | não | Sigla da unidade da federação |
| 3 | `serie` | STRING | não | Ano escolar |
| 4 | `rede` | STRING | não | Rede de ensino avaliada para construção do resultado |
| 5 | `taxa_alfabetizacao` | FLOAT64 | não | Percentual dos alunos avaliados no estado que foram considerados, mediante o resultado da avaliação estadual, como alfabetizados |
| 6 | `media_portugues` | FLOAT64 | não | Média ponderada do estado na avaliação estadual na disciplina Língua Portuguesa equalizada com o SAEB |
| 7 | `proporcao_aluno_nivel_0` | FLOAT64 | não | Percentual de alunos avaliados na UF que foram alocados no nível de desempenho 0 |
| 8 | `proporcao_aluno_nivel_1` | FLOAT64 | não | Percentual de alunos avaliados na UF que foram alocados no nível de desempenho 1 |
| 9 | `proporcao_aluno_nivel_2` | FLOAT64 | não | Percentual de alunos avaliados na UF que foram alocados no nível de desempenho 2 |
| 10 | `proporcao_aluno_nivel_3` | FLOAT64 | não | Percentual de alunos avaliados na UF que foram alocados no nível de desempenho 3 |
| 11 | `proporcao_aluno_nivel_4` | FLOAT64 | não | Percentual de alunos avaliados na UF que foram alocados no nível de desempenho 4 |
| 12 | `proporcao_aluno_nivel_5` | FLOAT64 | não | Percentual de alunos avaliados na UF que foram alocados no nível de desempenho 5 |
| 13 | `proporcao_aluno_nivel_6` | FLOAT64 | não | Percentual de alunos avaliados na UF que foram alocados no nível de desempenho 6 |
| 14 | `proporcao_aluno_nivel_7` | FLOAT64 | não | Percentual de alunos avaliados na UF que foram alocados no nível de desempenho 7 |
| 15 | `proporcao_aluno_nivel_8` | FLOAT64 | não | Percentual de alunos avaliados na UF que foram alocados no nível de desempenho 8 |
| 16 | `_ingestion_timestamp` | TIMESTAMP | não | Timestamp de ingestão da tabela |
| 17 | `_source` | STRING | não | Origem da tabela |

### `gold_tc.brasil_meta`

Taxa x meta para o Brasil, com distância da meta e status.

- **Camada:** Gold · **Dono provável:** Frente 3
- **Linhas:** 3 · **Bytes lógicos:** 214 B
- **Criada em:** 2026-10-23 19:49 · **Última modificação:** 2026-10-23 19:49 · **Expira:** 22/12/2026
- **DDL:** [`ddl/gold_tc.brasil_meta.sql`](ddl/gold_tc.brasil_meta.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano` | INT64 | não |  |
| 2 | `local` | STRING | não |  |
| 3 | `serie` | STRING | não |  |
| 4 | `rede` | STRING | não |  |
| 5 | `taxa_alfabetizacao` | FLOAT64 | não |  |
| 6 | `percentual_participacao` | FLOAT64 | não |  |
| 7 | `meta_alfabetizacao` | FLOAT64 | não |  |
| 8 | `distancia_meta` | FLOAT64 | não |  |
| 9 | `status_meta` | STRING | não |  |
| 10 | `motivo_sem_meta` | STRING | não |  |
| 11 | `_gold_timestamp` | TIMESTAMP | não |  |

### `gold_tc.evolucao_municipio`

Evolução da taxa por município entre 2023 e 2024 (variação em p.p. e tendência).

- **Camada:** Gold · **Dono provável:** Frente 3
- **Linhas:** 12.650 · **Bytes lógicos:** 1.019,33 KiB
- **Criada em:** 2026-10-23 19:49 · **Última modificação:** 2026-10-23 19:49 · **Expira:** 22/12/2026
- **DDL:** [`ddl/gold_tc.evolucao_municipio.sql`](ddl/gold_tc.evolucao_municipio.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `id_municipio` | STRING | não |  |
| 2 | `cod_uf` | STRING | não |  |
| 3 | `sigla_uf` | STRING | não |  |
| 4 | `serie` | STRING | não |  |
| 5 | `rede` | STRING | não |  |
| 6 | `rede_descricao` | STRING | não |  |
| 7 | `taxa_2023` | FLOAT64 | não |  |
| 8 | `taxa_2024` | FLOAT64 | não |  |
| 9 | `variacao_pp` | FLOAT64 | não |  |
| 10 | `tendencia` | STRING | não |  |
| 11 | `_gold_timestamp` | TIMESTAMP | não |  |

### `gold_tc.indicador_por_origem`

Indicador por município separado por origem (dado oficial x simulado).

- **Camada:** Gold · **Dono provável:** Frente 2 / Frente 3
- **Linhas:** 10.897 · **Bytes lógicos:** 872,67 KiB
- **Criada em:** 2026-10-23 19:49 · **Última modificação:** 2026-10-23 19:49 · **Expira:** 22/12/2026
- **DDL:** [`ddl/gold_tc.indicador_por_origem.sql`](ddl/gold_tc.indicador_por_origem.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `origem` | STRING | não |  |
| 2 | `ano` | INT64 | não |  |
| 3 | `id_municipio` | STRING | não |  |
| 4 | `cod_uf` | STRING | não |  |
| 5 | `sigla_uf` | STRING | não |  |
| 6 | `serie` | STRING | não |  |
| 7 | `rede` | STRING | não |  |
| 8 | `taxa_alfabetizacao` | FLOAT64 | não |  |
| 9 | `n_eventos` | INT64 | não |  |
| 10 | `n_avaliados` | INT64 | não |  |
| 11 | `metodo` | STRING | não |  |
| 12 | `_gold_timestamp` | TIMESTAMP | não |  |

### `gold_tc.municipio_meta`

Taxa x meta por município, com status da meta (atingiu, não atingiu, sem meta).

- **Camada:** Gold · **Dono provável:** Frente 3
- **Linhas:** 10.896 · **Bytes lógicos:** 1,33 MiB
- **Criada em:** 2026-10-23 19:49 · **Última modificação:** 2026-10-23 19:49 · **Expira:** 22/12/2026
- **DDL:** [`ddl/gold_tc.municipio_meta.sql`](ddl/gold_tc.municipio_meta.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano` | INT64 | não |  |
| 2 | `id_municipio` | STRING | não |  |
| 3 | `cod_uf` | STRING | não |  |
| 4 | `sigla_uf` | STRING | não |  |
| 5 | `serie` | STRING | não |  |
| 6 | `serie_descricao` | STRING | não |  |
| 7 | `rede` | STRING | não |  |
| 8 | `rede_descricao` | STRING | não |  |
| 9 | `taxa_alfabetizacao` | FLOAT64 | não |  |
| 10 | `meta_alfabetizacao` | FLOAT64 | não |  |
| 11 | `distancia_meta` | FLOAT64 | não |  |
| 12 | `status_meta` | STRING | não |  |
| 13 | `motivo_sem_meta` | STRING | não |  |
| 14 | `media_portugues` | FLOAT64 | não |  |
| 15 | `_gold_timestamp` | TIMESTAMP | não |  |

### `gold_tc.uf_meta`

Taxa x meta por UF, com status da meta.

- **Camada:** Gold · **Dono provável:** Frente 3
- **Linhas:** 49 · **Bytes lógicos:** 6,73 KiB
- **Criada em:** 2026-10-23 19:49 · **Última modificação:** 2026-10-23 19:49 · **Expira:** 22/12/2026
- **DDL:** [`ddl/gold_tc.uf_meta.sql`](ddl/gold_tc.uf_meta.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano` | INT64 | não |  |
| 2 | `cod_uf` | STRING | não |  |
| 3 | `sigla_uf` | STRING | não |  |
| 4 | `serie` | STRING | não |  |
| 5 | `serie_descricao` | STRING | não |  |
| 6 | `rede` | STRING | não |  |
| 7 | `rede_descricao` | STRING | não |  |
| 8 | `taxa_alfabetizacao` | FLOAT64 | não |  |
| 9 | `meta_alfabetizacao` | FLOAT64 | não |  |
| 10 | `distancia_meta` | FLOAT64 | não |  |
| 11 | `status_meta` | STRING | não |  |
| 12 | `motivo_sem_meta` | STRING | não |  |
| 13 | `media_portugues` | FLOAT64 | não |  |
| 14 | `_gold_timestamp` | TIMESTAMP | não |  |

### `gold_tc.validacao_cruzada`

Taxa recalculada a partir dos alunos (com peso amostral) comparada à taxa oficial.

- **Camada:** Gold · **Dono provável:** Frente 3
- **Linhas:** 24.143 · **Bytes lógicos:** 2,23 MiB
- **Criada em:** 2026-10-23 19:49 · **Última modificação:** 2026-10-23 19:49 · **Expira:** 22/12/2026
- **DDL:** [`ddl/gold_tc.validacao_cruzada.sql`](ddl/gold_tc.validacao_cruzada.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `nivel` | STRING | não |  |
| 2 | `ano` | INT64 | não |  |
| 3 | `local` | STRING | não |  |
| 4 | `rede` | STRING | não |  |
| 5 | `taxa_oficial` | FLOAT64 | não |  |
| 6 | `taxa_recalculada` | FLOAT64 | não |  |
| 7 | `diferenca_pp` | FLOAT64 | não |  |
| 8 | `taxa_sem_peso` | FLOAT64 | não |  |
| 9 | `taxa_todos_registros` | FLOAT64 | não |  |
| 10 | `n_avaliados` | INT64 | não |  |
| 11 | `n_registros` | INT64 | não |  |
| 12 | `taxa_na_tabela_meta` | FLOAT64 | não |  |
| 13 | `_gold_timestamp` | TIMESTAMP | não |  |

### `ops_tc.dq_results`

Resultado de cada regra de qualidade por execução (bloqueante ou informativa).

- **Camada:** Operação · **Dono provável:** Frente 3
- **Linhas:** 187 · **Bytes lógicos:** 29,95 KiB
- **Criada em:** 2026-10-20 18:09 · **Última modificação:** 2026-10-23 19:50 · **Expira:** partições expiram em 60 dias
- **Partição:** executado_em · **Cluster:** —
- **DDL:** [`ddl/ops_tc.dq_results.sql`](ddl/ops_tc.dq_results.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `execucao_id` | STRING | sim |  |
| 2 | `executado_em` | TIMESTAMP | sim |  |
| 3 | `camada` | STRING | não |  |
| 4 | `tabela` | STRING | não |  |
| 5 | `regra_id` | STRING | não |  |
| 6 | `descricao` | STRING | não |  |
| 7 | `severidade` | STRING | não |  |
| 8 | `valor_medido` | FLOAT64 | não |  |
| 9 | `limiar` | STRING | não |  |
| 10 | `status` | STRING | não |  |

### `ops_tc.eventos_rejeitados`

Eventos de streaming rejeitados, com motivo e mensagem original.

- **Camada:** Operação · **Dono provável:** Frente 2
- **Linhas:** 1 · **Bytes lógicos:** 694 B
- **Criada em:** 2026-10-23 19:17 · **Última modificação:** 2026-10-23 19:17 · **Expira:** 22/12/2026
- **DDL:** [`ddl/ops_tc.eventos_rejeitados.sql`](ddl/ops_tc.eventos_rejeitados.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `id_evento` | STRING | não |  |
| 2 | `horario_recebimento` | TIMESTAMP | não |  |
| 3 | `motivo_rejeicao` | STRING | não |  |
| 4 | `mensagem_bruta` | STRING | não |  |

### `silver_tc.alunos`

Alunos limpos e padronizados, com códigos traduzidos pelo dicionário. Particionada por ano e agrupada por UF e município.

- **Camada:** Silver · **Dono provável:** Frente 3
- **Linhas:** 3.867.999 · **Bytes lógicos:** 794,32 MiB
- **Criada em:** 2026-10-23 19:48 · **Última modificação:** 2026-10-23 19:48 · **Expira:** 22/12/2026
- **Partição:** ano · **Cluster:** sigla_uf,id_municipio
- **DDL:** [`ddl/silver_tc.alunos.sql`](ddl/silver_tc.alunos.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano` | INT64 | não |  |
| 2 | `id_municipio` | STRING | não |  |
| 3 | `cod_uf` | STRING | não |  |
| 4 | `sigla_uf` | STRING | não |  |
| 5 | `id_escola` | STRING | não |  |
| 6 | `id_aluno` | STRING | não |  |
| 7 | `caderno` | STRING | não |  |
| 8 | `serie` | STRING | não |  |
| 9 | `serie_descricao` | STRING | não |  |
| 10 | `rede` | STRING | não |  |
| 11 | `rede_descricao` | STRING | não |  |
| 12 | `presenca` | STRING | não |  |
| 13 | `presenca_descricao` | STRING | não |  |
| 14 | `preenchimento_caderno` | STRING | não |  |
| 15 | `preenchimento_caderno_descricao` | STRING | não |  |
| 16 | `alfabetizado` | STRING | não |  |
| 17 | `alfabetizado_descricao` | STRING | não |  |
| 18 | `avaliado` | BOOL | não |  |
| 19 | `proficiencia` | FLOAT64 | não |  |
| 20 | `peso_aluno` | FLOAT64 | não |  |
| 21 | `_ingestion_timestamp` | TIMESTAMP | não |  |
| 22 | `_source` | STRING | não |  |

### `silver_tc.alunos_eventos`

Eventos simulados no formato da Silver de alunos, mantendo origem e horários do evento.

- **Camada:** Silver · **Dono provável:** Frente 2
- **Linhas:** 5 · **Bytes lógicos:** 1,09 KiB
- **Criada em:** 2026-10-23 19:48 · **Última modificação:** 2026-10-23 19:48 · **Expira:** 22/12/2026
- **DDL:** [`ddl/silver_tc.alunos_eventos.sql`](ddl/silver_tc.alunos_eventos.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `id_evento` | STRING | não |  |
| 2 | `origem` | STRING | não |  |
| 3 | `horario_producao` | TIMESTAMP | não |  |
| 4 | `horario_recebimento` | TIMESTAMP | não |  |
| 5 | `latencia_segundos` | FLOAT64 | não |  |
| 6 | `ano` | INT64 | não |  |
| 7 | `id_municipio` | STRING | não |  |
| 8 | `cod_uf` | STRING | não |  |
| 9 | `sigla_uf` | STRING | não |  |
| 10 | `id_escola` | STRING | não |  |
| 11 | `id_aluno` | STRING | não |  |
| 12 | `caderno` | STRING | não |  |
| 13 | `serie` | STRING | não |  |
| 14 | `serie_descricao` | STRING | não |  |
| 15 | `rede` | STRING | não |  |
| 16 | `rede_descricao` | STRING | não |  |
| 17 | `presenca` | STRING | não |  |
| 18 | `presenca_descricao` | STRING | não |  |
| 19 | `preenchimento_caderno` | STRING | não |  |
| 20 | `preenchimento_caderno_descricao` | STRING | não |  |
| 21 | `alfabetizado` | STRING | não |  |
| 22 | `alfabetizado_descricao` | STRING | não |  |
| 23 | `avaliado` | BOOL | não |  |
| 24 | `proficiencia` | FLOAT64 | não |  |
| 25 | `peso_aluno` | FLOAT64 | não |  |

### `silver_tc.de_para_rede_meta`

De-para do texto de rede usado nas metas para o código de rede.

- **Camada:** Silver · **Dono provável:** Frente 3
- **Linhas:** 2 · **Bytes lógicos:** 27 B
- **Criada em:** 2026-10-23 19:48 · **Última modificação:** 2026-10-23 19:48 · **Expira:** 22/12/2026
- **DDL:** [`ddl/silver_tc.de_para_rede_meta.sql`](ddl/silver_tc.de_para_rede_meta.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `rede_texto` | STRING | não |  |
| 2 | `rede` | STRING | não |  |

### `silver_tc.de_para_uf`

De-para do código IBGE da UF para a sigla.

- **Camada:** Silver · **Dono provável:** Frente 3
- **Linhas:** 27 · **Bytes lógicos:** 216 B
- **Criada em:** 2026-10-23 19:48 · **Última modificação:** 2026-10-23 19:48 · **Expira:** 22/12/2026
- **DDL:** [`ddl/silver_tc.de_para_uf.sql`](ddl/silver_tc.de_para_uf.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `cod_uf` | STRING | não |  |
| 2 | `sigla_uf` | STRING | não |  |

### `silver_tc.meta_brasil`

Metas do Brasil em formato longo (uma linha por ano de meta).

- **Camada:** Silver · **Dono provável:** Frente 3
- **Linhas:** 21 · **Bytes lógicos:** 2,87 KiB
- **Criada em:** 2026-10-23 19:48 · **Última modificação:** 2026-10-23 19:48 · **Expira:** 22/12/2026
- **DDL:** [`ddl/silver_tc.meta_brasil.sql`](ddl/silver_tc.meta_brasil.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano_referencia` | INT64 | não |  |
| 2 | `local` | STRING | não |  |
| 3 | `serie` | STRING | não |  |
| 4 | `rede_texto` | STRING | não |  |
| 5 | `rede` | STRING | não |  |
| 6 | `taxa_referencia` | FLOAT64 | não |  |
| 7 | `percentual_participacao` | FLOAT64 | não |  |
| 8 | `ano_meta` | INT64 | não |  |
| 9 | `meta_alfabetizacao` | FLOAT64 | não |  |
| 10 | `_ingestion_timestamp` | TIMESTAMP | não |  |
| 11 | `_source` | STRING | não |  |

### `silver_tc.meta_municipio`

Metas por município em formato longo (uma linha por ano de meta).

- **Camada:** Silver · **Dono provável:** Frente 3
- **Linhas:** 37.464 · **Bytes lógicos:** 4,75 MiB
- **Criada em:** 2026-10-23 19:48 · **Última modificação:** 2026-10-23 19:48 · **Expira:** 22/12/2026
- **DDL:** [`ddl/silver_tc.meta_municipio.sql`](ddl/silver_tc.meta_municipio.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `id_municipio` | STRING | não |  |
| 2 | `cod_uf` | STRING | não |  |
| 3 | `sigla_uf` | STRING | não |  |
| 4 | `serie` | STRING | não |  |
| 5 | `rede_texto` | STRING | não |  |
| 6 | `rede` | STRING | não |  |
| 7 | `ano_meta` | INT64 | não |  |
| 8 | `meta_alfabetizacao` | FLOAT64 | não |  |
| 9 | `_ingestion_timestamp` | TIMESTAMP | não |  |
| 10 | `_source` | STRING | não |  |

### `silver_tc.meta_uf`

Metas por UF em formato longo (uma linha por ano de meta).

- **Camada:** Silver · **Dono provável:** Frente 3
- **Linhas:** 567 · **Bytes lógicos:** 76,91 KiB
- **Criada em:** 2026-10-23 19:48 · **Última modificação:** 2026-10-23 19:48 · **Expira:** 22/12/2026
- **DDL:** [`ddl/silver_tc.meta_uf.sql`](ddl/silver_tc.meta_uf.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano_referencia` | INT64 | não |  |
| 2 | `cod_uf` | STRING | não |  |
| 3 | `sigla_uf` | STRING | não |  |
| 4 | `serie` | STRING | não |  |
| 5 | `rede_texto` | STRING | não |  |
| 6 | `rede` | STRING | não |  |
| 7 | `taxa_referencia` | FLOAT64 | não |  |
| 8 | `percentual_participacao` | FLOAT64 | não |  |
| 9 | `ano_meta` | INT64 | não |  |
| 10 | `meta_alfabetizacao` | FLOAT64 | não |  |
| 11 | `_ingestion_timestamp` | TIMESTAMP | não |  |
| 12 | `_source` | STRING | não |  |

### `silver_tc.municipio`

Resultado por município padronizado, com UF e descrições de série e rede.

- **Camada:** Silver · **Dono provável:** Frente 3
- **Linhas:** 23.995 · **Bytes lógicos:** 4,59 MiB
- **Criada em:** 2026-10-23 19:48 · **Última modificação:** 2026-10-23 19:48 · **Expira:** 22/12/2026
- **DDL:** [`ddl/silver_tc.municipio.sql`](ddl/silver_tc.municipio.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano` | INT64 | não |  |
| 2 | `id_municipio` | STRING | não |  |
| 3 | `cod_uf` | STRING | não |  |
| 4 | `sigla_uf` | STRING | não |  |
| 5 | `serie` | STRING | não |  |
| 6 | `serie_descricao` | STRING | não |  |
| 7 | `rede` | STRING | não |  |
| 8 | `rede_descricao` | STRING | não |  |
| 9 | `taxa_alfabetizacao` | FLOAT64 | não |  |
| 10 | `media_portugues` | FLOAT64 | não |  |
| 11 | `proporcao_aluno_nivel_0` | FLOAT64 | não |  |
| 12 | `proporcao_aluno_nivel_1` | FLOAT64 | não |  |
| 13 | `proporcao_aluno_nivel_2` | FLOAT64 | não |  |
| 14 | `proporcao_aluno_nivel_3` | FLOAT64 | não |  |
| 15 | `proporcao_aluno_nivel_4` | FLOAT64 | não |  |
| 16 | `proporcao_aluno_nivel_5` | FLOAT64 | não |  |
| 17 | `proporcao_aluno_nivel_6` | FLOAT64 | não |  |
| 18 | `proporcao_aluno_nivel_7` | FLOAT64 | não |  |
| 19 | `proporcao_aluno_nivel_8` | FLOAT64 | não |  |
| 20 | `_ingestion_timestamp` | TIMESTAMP | não |  |
| 21 | `_source` | STRING | não |  |

### `silver_tc.uf`

Resultado por UF padronizado, com descrições de série e rede.

- **Camada:** Silver · **Dono provável:** Frente 3
- **Linhas:** 145 · **Bytes lógicos:** 25,72 KiB
- **Criada em:** 2026-10-23 19:48 · **Última modificação:** 2026-10-23 19:48 · **Expira:** 22/12/2026
- **DDL:** [`ddl/silver_tc.uf.sql`](ddl/silver_tc.uf.sql)

| # | Coluna | Tipo | Obrigatória | Descrição |
|---:|---|---|---|---|
| 1 | `ano` | INT64 | não |  |
| 2 | `cod_uf` | STRING | não |  |
| 3 | `sigla_uf` | STRING | não |  |
| 4 | `serie` | STRING | não |  |
| 5 | `serie_descricao` | STRING | não |  |
| 6 | `rede` | STRING | não |  |
| 7 | `rede_descricao` | STRING | não |  |
| 8 | `taxa_alfabetizacao` | FLOAT64 | não |  |
| 9 | `media_portugues` | FLOAT64 | não |  |
| 10 | `proporcao_aluno_nivel_0` | FLOAT64 | não |  |
| 11 | `proporcao_aluno_nivel_1` | FLOAT64 | não |  |
| 12 | `proporcao_aluno_nivel_2` | FLOAT64 | não |  |
| 13 | `proporcao_aluno_nivel_3` | FLOAT64 | não |  |
| 14 | `proporcao_aluno_nivel_4` | FLOAT64 | não |  |
| 15 | `proporcao_aluno_nivel_5` | FLOAT64 | não |  |
| 16 | `proporcao_aluno_nivel_6` | FLOAT64 | não |  |
| 17 | `proporcao_aluno_nivel_7` | FLOAT64 | não |  |
| 18 | `proporcao_aluno_nivel_8` | FLOAT64 | não |  |
| 19 | `_ingestion_timestamp` | TIMESTAMP | não |  |
| 20 | `_source` | STRING | não |  |
