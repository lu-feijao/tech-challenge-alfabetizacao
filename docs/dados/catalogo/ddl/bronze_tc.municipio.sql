-- DDL de bronze_tc.municipio, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.bronze_tc.municipio`
(
  ano INT64 OPTIONS(description="Ano de aplicação da avaliação estadual"),
  id_municipio STRING OPTIONS(description="ID Município"),
  serie STRING OPTIONS(description="Ano escolar"),
  rede STRING OPTIONS(description="Rede de ensino"),
  taxa_alfabetizacao FLOAT64 OPTIONS(description="Percentual dos alunos avaliados no município que foram considerados, mediante o resultado da avaliação estadual, como alfabetizados"),
  media_portugues FLOAT64 OPTIONS(description="Média ponderada do município na avaliação estadual na disciplina Língua Portuguesa (LP) equalizada com o SAEB"),
  proporcao_aluno_nivel_0 FLOAT64 OPTIONS(description="Percentual de alunos avaliados no município que foram alocados no nível de desempenho 0 na avaliação estadual de Lingua Portuguesa (LP)"),
  proporcao_aluno_nivel_1 FLOAT64 OPTIONS(description="Percentual de alunos avaliados no município que foram alocados no nível de desempenho 1 na avaliação estadual de Lingua Portuguesa (LP)"),
  proporcao_aluno_nivel_2 FLOAT64 OPTIONS(description="Percentual de alunos avaliados no município que foram alocados no nível de desempenho 2 na avaliação estadual de Lingua Portuguesa (LP)"),
  proporcao_aluno_nivel_3 FLOAT64 OPTIONS(description="Percentual de alunos avaliados no município que foram alocados no nível de desempenho 3 na avaliação estadual de Língua Portuguesa (LP)"),
  proporcao_aluno_nivel_4 FLOAT64 OPTIONS(description="Percentual de alunos avaliados no município que foram alocados no nível de desempenho 3 na avaliação estadual de Lingua Portuguesa (LP)"),
  proporcao_aluno_nivel_5 FLOAT64 OPTIONS(description="Percentual de alunos avaliados no município que foram alocados no nível de desempenho 4 na avaliação estadual de Lingua Portuguesa (LP)"),
  proporcao_aluno_nivel_6 FLOAT64 OPTIONS(description="Percentual de alunos avaliados no município que foram alocados no nível de desempenho 5 na avaliação estadual de Lingua Portuguesa (LP)"),
  proporcao_aluno_nivel_7 FLOAT64 OPTIONS(description="Percentual de alunos avaliados no município que foram alocados no nível de desempenho 6 na avaliação estadual de Lingua Portuguesa (LP)"),
  proporcao_aluno_nivel_8 FLOAT64 OPTIONS(description="Percentual de alunos avaliados no município que foram alocados no nível de desempenho 7 na avaliação estadual de Lingua Portuguesa (LP)"),
  _ingestion_timestamp TIMESTAMP OPTIONS(description="Timestamp de ingestão da tabela"),
  _source STRING OPTIONS(description="Origem da tabela")
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-15T19:48:09.533Z"
);
