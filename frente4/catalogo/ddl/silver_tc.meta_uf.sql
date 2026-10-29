-- DDL de silver_tc.meta_uf, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.silver_tc.meta_uf`
(
  ano_referencia INT64,
  cod_uf STRING,
  sigla_uf STRING,
  serie STRING,
  rede_texto STRING,
  rede STRING,
  taxa_referencia FLOAT64,
  percentual_participacao FLOAT64,
  ano_meta INT64,
  meta_alfabetizacao FLOAT64,
  _ingestion_timestamp TIMESTAMP,
  _source STRING
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-22T22:48:39.267Z"
);
