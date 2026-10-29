# Frente 4: o que falta e roteiro de execução

**Projeto:** `project-ce782257-1c9c-4b6f-87a` (região `southamerica-east1`; faturamento ativo conferido em 28/10/2026, antes BigQuery Sandbox)
**Atualizado em:** 28/10/2026
**Entrega:** 03/11/2026

Cada etapa só começa depois de aprovada. Ao final de cada etapa, os arquivos dela entram neste repositório e uma linha é acrescentada em `docs/frente4/registro_acoes.md`.

## Situação em 28/10/2026, 20h30

| Etapa | Situação | Entregáveis |
|---|---|---|
| 1. Catálogo | ✅ feita; regerada em 28/10 com 28 objetos | `docs/catalogo/`, `ops/gerar_catalogo.py`, `ops/medir_tabelas.py`, `docs/finops/medicao_tabelas.md` |
| 2. `pipeline_runs` + logger | ✅ tabela criada e gravação testada (26/10 e 28/10) · ✅ Silver e Gold instrumentadas no PR `frente4-observabilidade` (a Frente 3 revisa e roda) · ⏳ Bronze e streaming ainda não usam o logger | `ops/sql/ddl_pipeline_runs.sql`, `ops/run_logger.py`, `ops/testar_alerta.py` |
| 3. Alerta por e-mail | ✅ criado em 26/10 e testado em 28/10: e-mail ≈ 1 minuto depois da falha | `ops/alerta_falha.json`, `docs/frente4/evidencias/` |
| 4. Tabela de custo | ✅ feita com o medido da Frente 3 (≈ 2,3 GB por execução) · view de custo atualizada em 28/10 · orçamento "TC Fase 02" criado em 28/10 (R$ 0,00 de R$ 50,00) | `docs/finops/tabela_custo.md` e `.csv`, `ops/sql/vw_custo_por_etapa.sql`, `ops/sql/finops/` |
| 5. README e diagrama | ✅ proposta pronta (seções das outras frentes a preencher) | `README_FRENTE4.md`, `docs/arquitetura.md` e `.png` |
| 6. Vídeo e números | ✅ roteiro pronto | `docs/roteiro_video.md`, `docs/numeros.md` |
| 7. Conferência final | 01–02/11 | — |

---

## 1. Regras de segurança (valem para todas as etapas)

1. **Nada dos outros é apagado nem alterado.** Não uso `DROP`, `DELETE`, `TRUNCATE`, `UPDATE`, `MERGE` nem `CREATE OR REPLACE` em nenhuma tabela, view ou dataset.
2. **A Frente 4 só escreve em objetos novos e dela:** `ops_tc.pipeline_runs` e `ops_tc.vw_custo_por_etapa`. Os dois são criados com `IF NOT EXISTS`. Se já existir algo com esse nome, nada acontece e eu aviso.
3. **Antes de qualquer escrita, mostro o comando exato** (SQL ou configuração) e espero o "ok".
4. **Leitura vem antes de escrita.** As etapas de levantamento só leem metadados ou fazem consultas `SELECT`.
5. **Linhas de teste ficam marcadas.** Toda linha de teste gravada em `pipeline_runs` usa `etapa = 'teste_frente4'`, para não se confundir com execução real.

---

## 2. Estado atual

### O que já foi feito

| Item do guia | Situação | Onde está |
|---|---|---|
| Medir o tamanho das tabelas (dry run) | ✅ Feito em 22/10 para as 21 tabelas que existiam | `docs/finops/medicao_tabelas.md` |
| Passo a passo da Frente 4 | ✅ Entregue no chat (rascunhos de SQL e Python) | ainda não está no repositório |

### O que mudou no BigQuery desde 22/10

Hoje existem 26 tabelas. As 5 novas, das outras frentes, ainda não foram medidas:

| Tabela nova | Provável dono |
|---|---|
| `bronze_tc.eventos_alunos` | Frente 2 (streaming) |
| `silver_tc.alunos_eventos` | Frente 2 |
| `gold_tc.indicador_por_origem` | Frente 2 / 3 |
| `ops_tc.eventos_rejeitados` | Frente 2 |
| `ops_tc.dq_results` (187 linhas, particionada por dia em `executado_em`) | Frente 3 |

Em `ops_tc` **ainda não existe `pipeline_runs`**.

A `dq_results` usa colunas em português (`execucao_id`, `executado_em`, `camada`, `tabela`, `status`). A `pipeline_runs` vai seguir o mesmo padrão. Assim, as duas se ligam pelo mesmo `execucao_id`.

### O que falta, pelo checklist do guia

| # | Item da Frente 4 | Falta |
|---|---|---|
| 1 | Medir tabelas | Medir as 5 tabelas novas e versionar a medição e o script |
| 2 | `ops.pipeline_runs` | Tudo: tabela, função de registro (logger) e integração com as outras frentes |
| 3 | Alerta de falha por e-mail | Tudo: canal de e-mail, alerta, teste com falha provocada e evidência |
| 4 | Tabela de custo | Tudo: preços da região de São Paulo, quantidades medidas e projeção para produção |
| 5 | README | Tudo: esqueleto, diagrama e seções da Frente 4 |
| 6 | "Quem descobre que quebrou e em quanto tempo?" | Depende do item 3 |
| 7 | Roteiro do vídeo | Tudo |
| + | **Catálogo de dados para o git** (pedido extra) | Tudo |

---

## 3. Roteiro

### Etapa 0: Forma de acesso (decisão sua)

| Opção | Como funciona | Trabalho para você |
|---|---|---|
| **A. Console no navegador** (atual) | Eu opero o console do BigQuery no navegador do app | Aprovar cada abertura de página |
| **B. Conector do BigQuery** | Eu rodo SQL direto pelo conector | Conceder uma vez o papel **MCP Tool User** à sua conta, no IAM do projeto. Hoje falta a permissão `mcp.tools.call` |

As duas opções obedecem às mesmas regras de segurança. A B é mais rápida e deixa registro exato de cada comando.

### Etapa 1: Catálogo de dados (somente leitura)

**O que eu faço:** leio os metadados das 26 tabelas e gero o catálogo.

Com sua aprovação, rodo 3 consultas `SELECT` de leitura em `INFORMATION_SCHEMA`:
- `TABLES`: tipo da tabela, data de criação e DDL;
- `COLUMN_FIELD_PATHS`: colunas, tipos e descrições;
- `TABLE_STORAGE`: linhas e bytes.

Cada consulta custa no mínimo 10 MB. As três ficam dentro do 1 TiB gratuito do mês.

Também rodo 1 `SELECT DISTINCT status FROM ops_tc.dq_results`, para alinhar os valores de status da `pipeline_runs` com os da Frente 3.

**Cria no GCP:** nada.

**Arquivos para o git:**
- `docs/catalogo/catalogo_dados.md`: uma seção por tabela, com camada, dono provável, descrição, linhas, tamanho, partição, cluster, colunas e tipos;
- `docs/catalogo/catalogo_dados.csv`: uma linha por coluna, para filtrar;
- `docs/catalogo/ddl/<dataset>.<tabela>.sql`: DDL de cada tabela, **só como documentação**, com o aviso "não executar" no topo;
- `docs/finops/medicao_tabelas.md`: atualizado com as 5 tabelas novas;
- `ops/medir_tabelas.py`: script que repete a medição (só metadados e dry run).

**Como você confere:** o número de tabelas do catálogo deve bater com o que aparece no console (26).

### Etapa 2: Tabela `ops_tc.pipeline_runs` e o logger

**O que eu faço:**
1. Mostro o DDL abaixo e espero o "ok".
2. Crio a tabela.
3. Gravo 1 linha de teste.
4. Entrego o logger para as outras frentes.

```sql
CREATE TABLE IF NOT EXISTS `project-ce782257-1c9c-4b6f-87a.ops_tc.pipeline_runs` (
  execucao_id STRING NOT NULL,     -- mesmo ID usado em ops_tc.dq_results
  etapa STRING NOT NULL,           -- ex.: ingestao_alunos, silver_municipio
  camada STRING,                   -- bronze | silver | gold | streaming | ops
  tabela STRING,
  inicio TIMESTAMP NOT NULL,
  fim TIMESTAMP,
  duracao_seg FLOAT64,
  linhas_entrada INT64,
  linhas_saida INT64,
  status STRING NOT NULL,          -- valores alinhados com dq_results (Etapa 1)
  erro STRING,
  job_ids ARRAY<STRING>,
  bytes_processados INT64,
  bytes_faturados INT64,
  executado_por STRING
)
PARTITION BY DATE(inicio)
CLUSTER BY etapa, status
OPTIONS (description = 'Frente 4: uma linha por etapa por execução. Somente acréscimo.');
```

**Ajuste por causa do Sandbox:** o logger grava por **load job em modo append** (`load_table_from_json` com `WRITE_APPEND`), e não por streaming (`insert_rows_json`). O Sandbox não aceita streaming, e o load job é gratuito.

**Cria no GCP:** só `ops_tc.pipeline_runs`.

**Arquivos para o git:**
- `ops/sql/ddl_pipeline_runs.sql`
- `ops/run_logger.py`
- `ops/exemplo_uso_logger.py`
- trecho do README explicando como cada frente usa o logger

**Como você confere:** a tabela aparece em `ops_tc` com 1 linha (`etapa = 'teste_frente4'`, status de sucesso).

**Depende das outras frentes:** as Frentes 1, 2 e 3 precisam envolver as etapas delas com `registrar_etapa(...)`. Eu preparo o trecho de código para cada uma, mas não altero o código delas sem que o dono aprove.

### Etapa 3: Alerta de falha por e-mail

**O que eu faço:**
1. **Confiro se o Cloud Logging e o Cloud Monitoring funcionam neste projeto sem faturamento.** Ainda não está confirmado. Se não funcionarem, paro e trago as alternativas antes de seguir.
2. **Mostro a configuração e espero o "ok"** antes de criar:
   - o canal de notificação por e-mail, no endereço que você indicar;
   - o alerta baseado em log, com o filtro `logName=".../logs/tc-pipeline" AND severity>=ERROR`.
3. **Provoco uma falha simulada** pelo logger, com `etapa = 'teste_frente4'`. Rodo no Cloud Shell, com a sua sessão, sem chave de serviço.
4. **Anoto o horário do log e o horário em que o e-mail chegou.**
5. **Exporto a política de alerta** para o repositório.

**Cria no GCP:** 1 canal de e-mail e 1 política de alerta. Hoje o custo é zero: o Google só começa a cobrar alertas em 01/09/2027.

**Arquivos para o git:**
- `ops/alerta_falha.json` (a política exportada, sem os IDs)
- `docs/evidencias/alerta_*.png` (prints do log, da linha FALHA e do e-mail)
- `docs/frente4/teste_alerta.md` (horários e tempo até o e-mail chegar)

**Como você confere:** o e-mail chega na sua caixa de entrada.

**Orçamento (budget):** no Sandbox não existe conta de faturamento, então não dá para criar orçamento. A proteção que funciona é o teto `maximum_bytes_billed` em cada consulta, que entra no logger. Isso fica documentado no README.

### Etapa 4: Tabela de custo

**O que eu faço:**
1. Busco os preços oficiais da região **southamerica-east1** para:
   - BigQuery: consulta por TiB e armazenamento ativo e de longo prazo;
   - Pub/Sub;
   - Cloud Logging;
   - Cloud Monitoring.
2. Mostro o SQL da view abaixo e espero o "ok".
3. Crio a view e preencho a tabela de custo.

```sql
CREATE VIEW IF NOT EXISTS `project-ce782257-1c9c-4b6f-87a.ops_tc.vw_custo_por_etapa` AS
SELECT
  (SELECT value FROM UNNEST(labels) WHERE key = 'camada') AS camada,
  (SELECT value FROM UNNEST(labels) WHERE key = 'etapa')  AS etapa,
  COUNT(*) AS jobs,
  SUM(total_bytes_billed) / POW(1024, 3) AS gib_faturados
FROM `project-ce782257-1c9c-4b6f-87a.region-southamerica-east1.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND job_type = 'QUERY'
  AND EXISTS (SELECT 1 FROM UNNEST(labels) WHERE key = 'pipeline')
GROUP BY camada, etapa;
```

**De onde vêm as quantidades:**
- **Armazenamento:** a medição da Etapa 1.
- **Consultas:** essa view, quando as etapas rodarem com labels. Até lá, uso as estimativas dos dry runs, com a origem anotada.
- **Pub/Sub:** o volume de mensagens que a Frente 2 informar.

**Cria no GCP:** só a view `ops_tc.vw_custo_por_etapa`.

**Arquivos para o git:**
- `ops/sql/vw_custo_por_etapa.sql`
- `docs/finops/tabela_custo.md` (colunas: serviço, unidade, quantidade medida, origem da medição, preço unitário e custo mensal; com um bloco "Ambiente: BigQuery Sandbox" e outro "Projeção para produção")
- `docs/finops/tabela_custo.csv`

### Etapa 5: README

**O que eu faço:**
- monto o esqueleto do README com as seções do enunciado e o dono de cada uma;
- desenho o diagrama Mermaid **só do que existe** no BigQuery, incluindo as tabelas de streaming;
- escrevo as seções da Frente 4: observabilidade, "quem descobre que quebrou e em quanto tempo" (com os números da Etapa 3) e custos (com os números da Etapa 4).

**Cria no GCP:** nada.

**Arquivos para o git:**
- `README_FRENTE4.md` (proposta para mesclar no README do grupo), com as seções das outras frentes marcadas como "a preencher pela Frente X"
- `docs/arquitetura.md` (o diagrama)

### Etapa 6: Roteiro do vídeo e números

**O que eu faço:**
- escrevo o roteiro de até 5 minutos em linguagem para liderança, em 5 blocos: problema, arquitetura, demonstração, custo e próximos passos;
- monto o arquivo de números: cada número falado no vídeo, com a consulta ou o arquivo de onde ele sai.

**Arquivos para o git:**
- `docs/roteiro_video.md`
- `docs/numeros.md`

### Etapa 7: Conferência final (01–02/11)

- Confiro se cada número do README e do vídeo bate com `docs/numeros.md` e com o BigQuery.
- Rodo a medição de novo (`ops/medir_tabelas.py`) e atualizo o custo.
- Faço o teste em clone limpo junto com a Frente 1.

---

## 4. Calendário sugerido

| Data | Etapas |
|---|---|
| 24–25/10 | 0 e 1 (acesso e catálogo) |
| 26/10 | 2 (pipeline_runs e logger) |
| 26–27/10 | 3 (alerta e teste) |
| 28/10 | 4 (tabela de custo) |
| 29–30/10 | 5 (README) |
| 31/10 | 6 (vídeo e números) |
| 01–02/11 | 7 (conferência final) |

---

## 5. Pontos de atenção

- **Sandbox:** tabelas e partições expiram em 60 dias. As primeiras tabelas da Bronze vencem em 15/12/2026, depois da entrega. Mesmo assim, isso fica registrado no README.
- **Região:** consultas a `INFORMATION_SCHEMA` usam `region-southamerica-east1`, e os preços da tabela de custo são os de São Paulo.
- **Dependência das outras frentes:** a `pipeline_runs` só terá linhas reais quando as Frentes 1, 2 e 3 usarem o logger. Sem isso, a evidência da Frente 4 fica só no teste.
