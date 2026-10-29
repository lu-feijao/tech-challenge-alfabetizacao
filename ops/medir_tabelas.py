#!/usr/bin/env python3
"""Mede linhas, bytes lógicos e bytes de um SELECT * (dry run) de cada tabela das 4 camadas.

Só usa metadados e dry run: não executa consultas e não tem custo. Grava docs/finops/medicoes_dry_run.csv,
a base das quantidades medidas da tabela de custo (docs/finops/tabela_custo.md).

Uso (a partir da raiz do repositório):
    python ops/medir_tabelas.py
"""
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from google.cloud import bigquery  # noqa: E402

from quality.dq import carregar_config, conectar  # noqa: E402

ARQUIVO = RAIZ / "docs" / "finops" / "medicoes_dry_run.csv"


def main() -> int:
    cfg = carregar_config()
    client = conectar(cfg)
    medido_em = datetime.now(timezone.utc).isoformat(timespec="seconds")
    dry_run = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)

    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    with ARQUIVO.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["medido_em_utc", "dataset", "tabela", "linhas", "bytes_logicos", "bytes_select_star",
                    "mib_select_star", "fonte"])
        for chave in ["bronze", "silver", "gold", "ops"]:
            dataset = cfg[chave]
            for item in client.list_tables(f"{cfg['projeto']}.{dataset}"):
                tabela = client.get_table(item.reference)
                if tabela.table_type != "TABLE":
                    continue
                job = client.query(f"SELECT * FROM `{tabela.full_table_id.replace(':', '.')}`", job_config=dry_run)
                w.writerow([medido_em, dataset, tabela.table_id, tabela.num_rows, tabela.num_bytes,
                            job.total_bytes_processed, round(job.total_bytes_processed / 1024**2, 2),
                            "metadados + dry run"])
                print(f"   {dataset}.{tabela.table_id}: {tabela.num_rows} linhas, "
                      f"{tabela.num_bytes / 1024**2:.2f} MiB")
    print(f"Medições gravadas em {ARQUIVO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
