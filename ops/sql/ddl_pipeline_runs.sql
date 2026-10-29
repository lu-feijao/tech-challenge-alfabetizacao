-- ops · pipeline_runs: métricas de execução, uma linha por etapa e execução.
-- IF NOT EXISTS (nunca REPLACE): o histórico de execuções acumula entre execuções.
-- As linhas são gravadas por load job (WRITE_APPEND) em ops/run_logger.py.
-- Liga-se a ops.dq_results pelo mesmo execucao_id.
CREATE TABLE IF NOT EXISTS `{projeto}.{ops}.pipeline_runs` (
  execucao_id       STRING    NOT NULL OPTIONS(description="ID da execução, no mesmo formato de ops_tc.dq_results (ex.: silver_20261023_224832_50621d)"),
  etapa             STRING    NOT NULL OPTIONS(description="Nome da etapa (ex.: 07_alunos, regras_qualidade)"),
  camada            STRING             OPTIONS(description="bronze | silver | gold | streaming | ops"),
  tabela            STRING             OPTIONS(description="Tabela de destino da etapa, no formato dataset.tabela"),
  inicio            TIMESTAMP NOT NULL OPTIONS(description="Início da etapa (UTC)"),
  fim               TIMESTAMP          OPTIONS(description="Fim da etapa (UTC)"),
  duracao_seg       FLOAT64            OPTIONS(description="fim - inicio, em segundos"),
  linhas_entrada    INT64              OPTIONS(description="Linhas lidas pela etapa, quando aplicável"),
  linhas_saida      INT64              OPTIONS(description="Linhas gravadas pela etapa, quando aplicável"),
  status            STRING    NOT NULL OPTIONS(description="sucesso | falha"),
  erro              STRING             OPTIONS(description="Tipo e mensagem do erro quando status = falha"),
  job_ids           ARRAY<STRING>      OPTIONS(description="IDs dos jobs do BigQuery executados pela etapa"),
  bytes_processados INT64              OPTIONS(description="Soma de total_bytes_processed dos jobs da etapa"),
  bytes_faturados   INT64              OPTIONS(description="Soma de total_bytes_billed dos jobs da etapa"),
  executado_por     STRING             OPTIONS(description="Usuário do sistema que rodou a etapa")
)
PARTITION BY DATE(inicio)
CLUSTER BY etapa, status
OPTIONS(description="Uma linha por etapa por execução do pipeline. Somente acréscimo.");
