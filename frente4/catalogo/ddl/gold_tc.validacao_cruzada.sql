-- DDL de gold_tc.validacao_cruzada, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.gold_tc.validacao_cruzada`
(
  nivel STRING,
  ano INT64,
  local STRING,
  rede STRING,
  taxa_oficial FLOAT64,
  taxa_recalculada FLOAT64,
  diferenca_pp FLOAT64,
  taxa_sem_peso FLOAT64,
  taxa_todos_registros FLOAT64,
  n_avaliados INT64,
  n_registros INT64,
  taxa_na_tabela_meta FLOAT64,
  _gold_timestamp TIMESTAMP
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-22T22:49:50.657Z"
);
