-- DDL de gold_tc.brasil_meta, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.gold_tc.brasil_meta`
(
  ano INT64,
  local STRING,
  serie STRING,
  rede STRING,
  taxa_alfabetizacao FLOAT64,
  percentual_participacao FLOAT64,
  meta_alfabetizacao FLOAT64,
  distancia_meta FLOAT64,
  status_meta STRING,
  motivo_sem_meta STRING,
  _gold_timestamp TIMESTAMP
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-22T22:49:47.304Z"
);
