-- DDL de ops_tc.eventos_rejeitados, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.ops_tc.eventos_rejeitados`
(
  id_evento STRING,
  horario_recebimento TIMESTAMP,
  motivo_rejeicao STRING,
  mensagem_bruta STRING
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-22T22:17:14.138Z"
);
