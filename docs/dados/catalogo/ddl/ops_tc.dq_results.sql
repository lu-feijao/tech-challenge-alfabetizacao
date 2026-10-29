-- DDL de ops_tc.dq_results, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.ops_tc.dq_results`
(
  execucao_id STRING NOT NULL,
  executado_em TIMESTAMP NOT NULL,
  camada STRING,
  tabela STRING,
  regra_id STRING,
  descricao STRING,
  severidade STRING,
  valor_medido FLOAT64,
  limiar STRING,
  status STRING
)
PARTITION BY DATE(executado_em)
OPTIONS(
  partition_expiration_days=60.0
);
