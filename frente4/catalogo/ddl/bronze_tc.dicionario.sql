-- DDL de bronze_tc.dicionario, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.bronze_tc.dicionario`
(
  id_tabela STRING,
  nome_coluna STRING,
  chave STRING,
  cobertura_temporal STRING,
  valor STRING,
  _ingestion_timestamp TIMESTAMP,
  _source STRING
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-15T19:48:45.757Z"
);
