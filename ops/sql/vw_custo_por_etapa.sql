-- ops · vw_custo_por_etapa: bytes faturados por camada e etapa nos últimos 30 dias.
-- Conta só os jobs com o label `pipeline` (aplicado por ops/run_logger.py) e só os de primeiro nível:
-- num script com várias instruções, o job pai já soma os filhos.
-- A região do INFORMATION_SCHEMA precisa ser a dos datasets (aqui, southamerica-east1).
-- Leitura de INFORMATION_SCHEMA.JOBS_BY_PROJECT exige bigquery.jobs.listAll (papel Leitor de recursos do BigQuery).
-- Uso: bq query --use_legacy_sql=false < ops/sql/vw_custo_por_etapa.sql  (troque {projeto} e {ops} antes)
CREATE OR REPLACE VIEW `{projeto}.{ops}.vw_custo_por_etapa`
OPTIONS(description="Bytes faturados por camada e etapa nos últimos 30 dias (jobs com label pipeline).")
AS SELECT
  (SELECT value FROM UNNEST(labels) WHERE key = 'camada') AS camada,
  (SELECT value FROM UNNEST(labels) WHERE key = 'etapa')  AS etapa,
  COUNT(*) AS jobs,
  COUNTIF(error_result IS NOT NULL) AS jobs_com_erro,
  SUM(IFNULL(total_bytes_billed, 0)) / POW(1024, 3) AS gib_faturados,
  SUM(IFNULL(total_bytes_billed, 0)) / POW(1024, 4) * 11.25 AS usd_preco_tabela_sao_paulo
FROM `{projeto}.region-southamerica-east1.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND job_type = 'QUERY'
  AND parent_job_id IS NULL
  AND EXISTS (SELECT 1 FROM UNNEST(labels) WHERE key = 'pipeline')
GROUP BY camada, etapa;
