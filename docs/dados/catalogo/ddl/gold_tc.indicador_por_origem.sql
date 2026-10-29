-- DDL de gold_tc.indicador_por_origem, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.gold_tc.indicador_por_origem`
(
  origem STRING,
  ano INT64,
  id_municipio STRING,
  cod_uf STRING,
  sigla_uf STRING,
  serie STRING,
  rede STRING,
  taxa_alfabetizacao FLOAT64,
  n_eventos INT64,
  n_avaliados INT64,
  metodo STRING,
  _gold_timestamp TIMESTAMP
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-22T22:49:52.200Z"
);
