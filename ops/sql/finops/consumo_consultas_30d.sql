-- FinOps · consumo real de consultas nos últimos 30 dias, por tipo de instrução.
-- Fonte das quantidades medidas da tabela de custo (docs/finops/tabela_custo.md).
-- Só jobs de primeiro nível (parent_job_id IS NULL), para não contar duas vezes os filhos de um script.
-- Exige bigquery.jobs.listAll (papel Leitor de recursos do BigQuery). Troque {projeto} antes de rodar.
SELECT
  job_type,
  IFNULL(statement_type, '(sem tipo)') AS statement_type,
  COUNT(*) AS jobs,
  COUNTIF(error_result IS NOT NULL) AS jobs_com_erro,
  ROUND(SUM(IFNULL(total_bytes_billed, 0)) / POW(1024, 3), 2) AS gib_faturados,
  ROUND(SUM(IFNULL(total_bytes_billed, 0)) / POW(1024, 4) * 11.25, 2) AS usd_preco_tabela_sao_paulo
FROM `{projeto}.region-southamerica-east1.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND parent_job_id IS NULL
GROUP BY job_type, statement_type
ORDER BY gib_faturados DESC;
