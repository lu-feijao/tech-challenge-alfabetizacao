-- DDL de bronze_tc.alunos, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.bronze_tc.alunos`
(
  ano INT64 OPTIONS(description="Ano de aplicação da avaliação estadual"),
  id_municipio STRING OPTIONS(description="ID Município de 7 dígitos"),
  id_escola STRING OPTIONS(description="Máscara do código da escola (códigos fictícios)"),
  id_aluno STRING OPTIONS(description="Código do aluno"),
  caderno STRING OPTIONS(description="Código do caderno atribuído ao aluno na prova de língua portuguesa"),
  serie STRING OPTIONS(description="Ano escolar"),
  rede STRING OPTIONS(description="Dependência administrativa da escola"),
  presenca STRING OPTIONS(description="Indicador de presença na prova de língua portuguesa"),
  preenchimento_caderno STRING OPTIONS(description="Indicador de preenchimento da prova de língua portuguesa"),
  alfabetizado STRING OPTIONS(description="Indica se o aluno, mediante o resultado da avaliação estadual, é considerado alfabetizado"),
  proficiencia FLOAT64 OPTIONS(description="Proficiência do aluno em língua portuguesa calculada na escala equalizada com o SAEB"),
  peso_aluno FLOAT64 OPTIONS(description="Peso do aluno na prova de língua portuguesa"),
  _ingestion_timestamp TIMESTAMP OPTIONS(description="Timestamp de ingestão da tabela"),
  _source STRING OPTIONS(description="Origem da tabela")
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-15T19:49:18.732Z"
);
