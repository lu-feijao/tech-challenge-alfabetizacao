-- DDL de gold_tc.evolucao_municipio, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.gold_tc.evolucao_municipio`
(
  id_municipio STRING,
  cod_uf STRING,
  sigla_uf STRING,
  serie STRING,
  rede STRING,
  rede_descricao STRING,
  taxa_2023 FLOAT64,
  taxa_2024 FLOAT64,
  variacao_pp FLOAT64,
  tendencia STRING,
  _gold_timestamp TIMESTAMP
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-22T22:49:48.619Z"
);
