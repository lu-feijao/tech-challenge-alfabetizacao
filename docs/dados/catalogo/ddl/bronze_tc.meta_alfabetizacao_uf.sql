-- DDL de bronze_tc.meta_alfabetizacao_uf, extraído do INFORMATION_SCHEMA em 24/10/2026 22:35.
-- SOMENTE DOCUMENTAÇÃO. NÃO EXECUTAR: a tabela já existe e pertence ao dono indicado no catálogo.

CREATE TABLE `project-ce782257-1c9c-4b6f-87a.bronze_tc.meta_alfabetizacao_uf`
(
  ano INT64 OPTIONS(description="Ano da avaliação"),
  sigla_uf STRING OPTIONS(description="Sigla da unidade da federação"),
  rede STRING OPTIONS(description="Rede de ensino"),
  taxa_alfabetizacao FLOAT64 OPTIONS(description="Percentual dos alunos avaliados no estado que foram considerados, mediante o resultado da avaliação estadual, como alfabetizados"),
  meta_alfabetizacao_2024 FLOAT64 OPTIONS(description="Meta de alfabetização no ano de 2024"),
  meta_alfabetizacao_2025 FLOAT64 OPTIONS(description="Meta de alfabetização no ano de 2025"),
  meta_alfabetizacao_2026 FLOAT64 OPTIONS(description="Meta de alfabetização no ano de 2026"),
  meta_alfabetizacao_2027 FLOAT64 OPTIONS(description="Meta de alfabetização no ano de 2027"),
  meta_alfabetizacao_2028 FLOAT64 OPTIONS(description="Meta de alfabetização no ano de 2028"),
  meta_alfabetizacao_2029 FLOAT64 OPTIONS(description="Meta de alfabetização no ano de 2029"),
  meta_alfabetizacao_2030 FLOAT64 OPTIONS(description="Meta de alfabetização no ano de 2030"),
  percentual_participacao FLOAT64 OPTIONS(description="Percentual de participação no estado"),
  _ingestion_timestamp TIMESTAMP OPTIONS(description="Timestamp de ingestão da tabela"),
  _source STRING OPTIONS(description="Origem da tabela")
)
OPTIONS(
  expiration_timestamp=TIMESTAMP "2026-12-15T19:48:23.458Z"
);
