-- DDL de bronze_tc.eventos_alunos, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.bronze_tc.eventos_alunos`
(
  id_evento STRING,
  origem STRING,
  horario_producao TIMESTAMP,
  horario_recebimento TIMESTAMP,
  latencia_segundos FLOAT64,
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
  peso_aluno FLOAT64
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-22T22:16:50.112Z"
);
