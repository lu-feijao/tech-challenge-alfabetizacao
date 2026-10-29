"""Funções compartilhadas pela Silver e pela Gold: configuração, execução de SQL e regras de qualidade.

Os resultados das regras são gravados em ops.dq_results por LOAD JOB (WRITE_APPEND), e não por INSERT:
load job funciona inclusive no BigQuery sandbox, que bloqueia DML.
"""
import copy
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google.api_core.exceptions import NotFound
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import bigquery

RAIZ = Path(__file__).resolve().parents[1]
PASTA_EVIDENCIAS = RAIZ / "docs" / "evidencias"

VARIAVEIS = {
    "projeto": "GCP_PROJECT_ID",
    "bronze": "BQ_BRONZE_DATASET",
    "silver": "BQ_SILVER_DATASET",
    "gold": "BQ_GOLD_DATASET",
    "ops": "BQ_OPS_DATASET",
}

SCHEMA_DQ = [
    bigquery.SchemaField("execucao_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("executado_em", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("camada", "STRING"),
    bigquery.SchemaField("tabela", "STRING"),
    bigquery.SchemaField("regra_id", "STRING"),
    bigquery.SchemaField("descricao", "STRING"),
    bigquery.SchemaField("severidade", "STRING"),
    bigquery.SchemaField("valor_medido", "FLOAT"),
    bigquery.SchemaField("limiar", "STRING"),
    bigquery.SchemaField("status", "STRING"),
]


class RegraBloqueanteReprovada(Exception):
    """Uma ou mais regras bloqueantes reprovaram: a camada seguinte não deve ser publicada."""


def carregar_config() -> dict:
    """Lê projeto e datasets do .env (ou das variáveis de ambiente). Nenhum ID fixo no código."""
    load_dotenv(RAIZ / ".env")
    cfg = {chave: os.getenv(var, "").strip() for chave, var in VARIAVEIS.items()}
    faltando = [VARIAVEIS[c] for c, v in cfg.items() if not v]
    if faltando:
        sys.exit(f"Configuração incompleta no .env: {', '.join(faltando)}. Use .env.example como modelo.")
    return cfg


def conectar(cfg: dict) -> bigquery.Client:
    try:
        client = bigquery.Client(project=cfg["projeto"])
    except DefaultCredentialsError:
        sys.exit(
            "Sem credenciais do Google. Local: rode 'gcloud auth application-default login'. "
            "Colab: rode 'from google.colab import auth; auth.authenticate_user()' antes."
        )
    for chave in ["bronze", "silver", "gold", "ops"]:
        try:
            client.get_dataset(f"{cfg['projeto']}.{cfg[chave]}")
        except NotFound:
            sys.exit(f"Dataset {cfg['projeto']}.{cfg[chave]} não encontrado. Crie-o ou corrija o .env.")
    print("Conectado ao projeto:", client.project)
    return client


def novo_execucao_id(etapa: str) -> str:
    return f"{etapa}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}"


def executar_sql(client: bigquery.Client, arquivo: Path, cfg: dict, job_config=None) -> dict:
    """Executa um arquivo .sql (pode ter várias instruções) com os marcadores preenchidos pelo .env.
    job_config (opcional) traz os labels e o teto de bytes de ops/run_logger.py."""
    sql = arquivo.read_text(encoding="utf-8").format(**cfg)
    inicio = datetime.now(timezone.utc)
    job = client.query(sql, job_config=job_config)
    job.result()  # erro de SQL interrompe aqui, de propósito
    duracao = (datetime.now(timezone.utc) - inicio).total_seconds()
    gb = (job.total_bytes_processed or 0) / 1e9
    print(f"   {arquivo.name}: ok | job {job.job_id} | {gb:.3f} GB processados | {duracao:.1f} s")
    return {
        "arquivo": arquivo.name, "job_id": job.job_id, "gb_processados": round(gb, 4), "duracao_s": round(duracao, 1),
        "bytes_processados": job.total_bytes_processed or 0, "bytes_faturados": job.total_bytes_billed or 0,
        "sql": sql,
    }


def tabela_existe(client: bigquery.Client, id_tabela: str) -> bool:
    try:
        client.get_table(id_tabela)
        return True
    except NotFound:
        return False


def requisitos_pendentes(client: bigquery.Client, arquivo: Path, cfg: dict) -> list:
    """Lê as linhas '-- @requer: projeto.dataset.tabela' do início do .sql e devolve as tabelas que não existem.
    Serve às etapas opcionais (eventos de streaming): sem a tabela de entrada, o arquivo é pulado com aviso,
    e a parte batch do pipeline continua funcionando num clone limpo."""
    pendentes = []
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        if not linha.startswith("--"):
            break
        if linha.startswith("-- @requer:"):
            tabela = linha.split(":", 1)[1].strip().format(**cfg)
            if not tabela_existe(client, tabela):
                pendentes.append(tabela)
    return pendentes


def _aprovada(valor, operador, limiar) -> bool:
    if operador is None:
        return True
    if valor is None:
        return False
    return {"==": valor == limiar, "<=": valor <= limiar, ">=": valor >= limiar}[operador]


def avaliar_regras(client: bigquery.Client, regras: list, cfg: dict, execucao_id: str, job_config=None,
                   medida=None) -> list:
    """Avalia as regras. job_config e medida (opcionais) vêm de ops/run_logger.py: labels, teto de bytes
    e a soma de jobs e bytes da etapa de regras."""
    executado_em = datetime.now(timezone.utc)
    resultados = []
    for r in regras:
        job = client.query(r.sql.format(**cfg), job_config=copy.deepcopy(job_config))
        linhas = list(job.result())
        if medida is not None:
            medida.adicionar_job({"job_id": job.job_id, "bytes_processados": job.total_bytes_processed,
                                  "bytes_faturados": job.total_bytes_billed})
        valor = linhas[0]["valor"] if linhas else None
        valor = float(valor) if valor is not None else None
        if r.operador is None:
            status = "medida"
        else:
            status = "aprovada" if _aprovada(valor, r.operador, r.limiar) else "reprovada"
        resultados.append({
            "execucao_id": execucao_id,
            "executado_em": executado_em.isoformat(),
            "camada": r.camada,
            "tabela": r.tabela,
            "regra_id": r.id,
            "descricao": r.descricao,
            "severidade": r.severidade,
            "valor_medido": valor,
            "limiar": None if r.operador is None else f"{r.operador} {r.limiar:g}",
            "status": status,
        })
        marca = {"aprovada": "ok", "reprovada": "REPROVADA", "medida": "medida"}[status]
        print(f"   [{marca:>9}] {r.id} {r.severidade:<11} {r.tabela:<28} valor={valor}")
    return resultados


def gravar_resultados(client: bigquery.Client, cfg: dict, resultados: list, etapa: str) -> None:
    """Grava em ops.dq_results (load job, append) e guarda uma cópia em docs/evidencias/."""
    executar_sql(client, RAIZ / "quality" / "sql" / "00_dq_results.sql", cfg)
    destino = f"{cfg['projeto']}.{cfg['ops']}.dq_results"
    job_config = bigquery.LoadJobConfig(schema=SCHEMA_DQ, write_disposition="WRITE_APPEND")
    job = client.load_table_from_json(resultados, destino, job_config=job_config)
    job.result()
    print(f"   {len(resultados)} resultados gravados em {destino} (job {job.job_id})")

    PASTA_EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    arquivo = PASTA_EVIDENCIAS / f"dq_{resultados[0]['execucao_id']}.csv"
    pd.DataFrame(resultados).to_csv(arquivo, index=False)
    print(f"   cópia local: {arquivo.relative_to(RAIZ)}")


def exigir_bloqueantes_aprovadas(resultados: list) -> None:
    reprovadas = [r for r in resultados if r["severidade"] == "bloqueante" and r["status"] == "reprovada"]
    if reprovadas:
        detalhes = "; ".join(f"{r['regra_id']} {r['tabela']} (valor {r['valor_medido']}, limiar {r['limiar']})" for r in reprovadas)
        raise RegraBloqueanteReprovada(f"{len(reprovadas)} regra(s) bloqueante(s) reprovada(s): {detalhes}")


def ultima_validacao_silver_aprovada(client: bigquery.Client, cfg: dict) -> bool:
    """Portão da Gold: a execução mais recente da Silver precisa ter todas as bloqueantes aprovadas."""
    sql = f"""
    WITH ultima AS (
      SELECT execucao_id FROM `{cfg['projeto']}.{cfg['ops']}.dq_results`
      WHERE STARTS_WITH(execucao_id, 'silver_')
      ORDER BY executado_em DESC LIMIT 1
    )
    SELECT COUNT(*) AS linhas, COUNTIF(severidade = 'bloqueante' AND status = 'reprovada') AS reprovadas
    FROM `{cfg['projeto']}.{cfg['ops']}.dq_results`
    WHERE execucao_id = (SELECT execucao_id FROM ultima)
    """
    try:
        linha = list(client.query(sql).result())[0]
    except NotFound:
        return False
    return linha["linhas"] > 0 and linha["reprovadas"] == 0
