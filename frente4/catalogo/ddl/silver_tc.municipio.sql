-- DDL de silver_tc.municipio, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.silver_tc.municipio`
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
  media_portugues FLOAT64,
  proporcao_aluno_nivel_0 FLOAT64,
  proporcao_aluno_nivel_1 FLOAT64,
  proporcao_aluno_nivel_2 FLOAT64,
  proporcao_aluno_nivel_3 FLOAT64,
  proporcao_aluno_nivel_4 FLOAT64,
  proporcao_aluno_nivel_5 FLOAT64,
  proporcao_aluno_nivel_6 FLOAT64,
  proporcao_aluno_nivel_7 FLOAT64,
  proporcao_aluno_nivel_8 FLOAT64,
  _ingestion_timestamp TIMESTAMP,
  _source STRING
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-22T22:48:33.648Z"
);
