-- DDL de gold_tc.municipio_meta, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.gold_tc.municipio_meta`
(
  ano INT64,
  id_municipio STRING,
  cod_uf STRING,
  sigla_uf STRING,
  serie STRING,
  serie_descricao STRING,
  rede STRING,
  rede_descricao STRING,
  taxa_alfabetizacao FLOAT64,
  meta_alfabetizacao FLOAT64,
  distancia_meta FLOAT64,
  status_meta STRING,
  motivo_sem_meta STRING,
  media_portugues FLOAT64,
  _gold_timestamp TIMESTAMP
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-22T22:49:44.173Z"
);
