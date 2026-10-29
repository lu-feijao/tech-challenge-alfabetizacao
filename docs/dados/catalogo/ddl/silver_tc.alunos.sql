-- DDL de silver_tc.alunos, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.silver_tc.alunos`
(
  ano INT64,
  id_municipio STRING,
  cod_uf STRING,
  sigla_uf STRING,
  id_escola STRING,
  id_aluno STRING,
  caderno STRING,
  serie STRING,
  serie_descricao STRING,
  rede STRING,
  rede_descricao STRING,
  presenca STRING,
  presenca_descricao STRING,
  preenchimento_caderno STRING,
  preenchimento_caderno_descricao STRING,
  alfabetizado STRING,
  alfabetizado_descricao STRING,
  avaliado BOOL,
  proficiencia FLOAT64,
  peso_aluno FLOAT64,
  _ingestion_timestamp TIMESTAMP,
  _source STRING
)
PARTITION BY RANGE_BUCKET(ano, GENERATE_ARRAY(2023, 2031, 1))
CLUSTER BY sigla_uf, id_municipio
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-22T22:48:48.614Z"
);
