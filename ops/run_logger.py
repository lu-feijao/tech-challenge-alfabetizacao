"""Métricas de execução do pipeline: uma linha por etapa em ops.pipeline_runs e o log tc-pipeline.

- Cada etapa grava início, fim, duração, linhas de entrada e saída, bytes, job IDs e status.
- As linhas são gravadas por LOAD JOB (WRITE_APPEND), no mesmo padrão de ops.dq_results: o histórico acumula.
- Uma falha também vai para o Cloud Logging, no log `tc-pipeline`, com severidade ERROR. A política de alerta
  "Pipeline TC - falha" (ops/alerta_falha.json) escuta esse log e envia e-mail.
- Os jobs de consulta recebem os labels pipeline/camada/etapa (lidos por ops.vw_custo_por_etapa) e um teto de
  bytes faturados: uma consulta acima do teto falha em vez de cobrar.

Uso:
    registro = RegistroExecucao(client, cfg, execucao_id, camada="silver")
    try:
        with registro.etapa("07_alunos", tabela="silver_tc.alunos") as medida:
            job = executar_sql(client, arquivo, cfg, job_config=registro.config_job("07_alunos"))
            medida.adicionar_job(job)
    finally:
        registro.gravar()
"""
import getpass
import re
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from google.api_core.exceptions import GoogleAPICallError
from google.auth.exceptions import GoogleAuthError
from google.cloud import bigquery

RAIZ = Path(__file__).resolve().parents[1]
NOME_LOG = "tc-pipeline"
TETO_BYTES_FATURADOS = 10 * 1024**3  # 10 GiB por consulta; a maior consulta do pipeline lê cerca de 1 GB

SCHEMA_RUNS = [
    bigquery.SchemaField("execucao_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("etapa", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("camada", "STRING"),
    bigquery.SchemaField("tabela", "STRING"),
    bigquery.SchemaField("inicio", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("fim", "TIMESTAMP"),
    bigquery.SchemaField("duracao_seg", "FLOAT"),
    bigquery.SchemaField("linhas_entrada", "INTEGER"),
    bigquery.SchemaField("linhas_saida", "INTEGER"),
    bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("erro", "STRING"),
    bigquery.SchemaField("job_ids", "STRING", mode="REPEATED"),
    bigquery.SchemaField("bytes_processados", "INTEGER"),
    bigquery.SchemaField("bytes_faturados", "INTEGER"),
    bigquery.SchemaField("executado_por", "STRING"),
]


def valor_label(texto: str) -> str:
    """Labels do BigQuery aceitam só minúsculas, dígitos, '_' e '-', até 63 caracteres."""
    return re.sub(r"[^a-z0-9_-]", "_", texto.lower())[:63]


def tabelas_citadas(sql: str) -> dict:
    """Separa as tabelas de um SQL já formatado em destino (CREATE ... TABLE) e entrada (o resto).
    Serve para medir linhas de entrada e saída pelos metadados, sem consulta extra."""
    citadas = re.findall(r"`([\w-]+\.[\w-]+\.[\w-]+)`", sql)
    destino = re.findall(r"CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`([^`]+)`", sql, re.I)
    entrada = [t for t in dict.fromkeys(citadas) if t not in destino]
    return {"destino": list(dict.fromkeys(destino)), "entrada": entrada}


def executar_sql_registrado(registro: "RegistroExecucao", arquivo: Path, executar) -> dict:
    """Roda um arquivo .sql como uma etapa de pipeline_runs. `executar` é quality.dq.executar_sql.
    Linhas de entrada = soma das linhas das tabelas que o SQL lê; linhas de saída = linhas das tabelas
    que ele cria (os dois pelos metadados das tabelas, sem consulta extra)."""
    etapa = arquivo.stem
    tabelas = tabelas_citadas(arquivo.read_text(encoding="utf-8").format(**registro.cfg))
    destino = ".".join(tabelas["destino"][0].split(".")[1:]) if tabelas["destino"] else None
    with registro.etapa(etapa, tabela=destino) as medida:
        medida.linhas_entrada = registro.contar_linhas(tabelas["entrada"])
        job = executar(registro.client, arquivo, registro.cfg, job_config=registro.config_job(etapa))
        medida.adicionar_job(job)
        medida.linhas_saida = registro.contar_linhas(tabelas["destino"])
    return job


class Medida:
    """O que uma etapa mediu. A etapa preenche; o registro transforma em linha de pipeline_runs."""

    def __init__(self):
        self.job_ids = []
        self.bytes_processados = 0
        self.bytes_faturados = 0
        self.linhas_entrada = None
        self.linhas_saida = None

    def adicionar_job(self, job: dict) -> None:
        """Recebe o dicionário devolvido por quality.dq.executar_sql."""
        self.job_ids.append(job["job_id"])
        self.bytes_processados += job.get("bytes_processados") or 0
        self.bytes_faturados += job.get("bytes_faturados") or 0


class RegistroExecucao:
    def __init__(self, client: bigquery.Client, cfg: dict, execucao_id: str, camada: str):
        self.client = client
        self.cfg = cfg
        self.execucao_id = execucao_id
        self.camada = camada
        self.linhas = []
        self.executado_por = getpass.getuser()
        self._logger = None

    def config_job(self, etapa: str) -> bigquery.QueryJobConfig:
        return bigquery.QueryJobConfig(
            labels={"pipeline": "tc", "camada": valor_label(self.camada), "etapa": valor_label(etapa)},
            maximum_bytes_billed=TETO_BYTES_FATURADOS,
        )

    def contar_linhas(self, tabelas: list):
        """Soma num_rows das tabelas (metadado, sem custo). Devolve None se nenhuma existir."""
        total, achou = 0, False
        for t in tabelas:
            try:
                total += self.client.get_table(t).num_rows or 0
                achou = True
            except GoogleAPICallError:
                continue
        return total if achou else None

    @contextmanager
    def etapa(self, nome: str, tabela: str = None):
        """Mede uma etapa. Se ela levantar exceção, registra a falha, escreve ERROR no log e repassa a exceção."""
        medida = Medida()
        inicio = datetime.now(timezone.utc)
        try:
            yield medida
        except Exception as erro:
            self._registrar(nome, tabela, inicio, medida, "falha", f"{type(erro).__name__}: {erro}")
            raise
        self._registrar(nome, tabela, inicio, medida, "sucesso", None)

    def falha(self, nome: str, mensagem: str, tabela: str = None) -> None:
        """Falha detectada sem exceção (por exemplo, regra bloqueante reprovada ou portão fechado)."""
        self._registrar(nome, tabela, datetime.now(timezone.utc), Medida(), "falha", mensagem)

    def _registrar(self, nome, tabela, inicio, medida, status, erro) -> None:
        fim = datetime.now(timezone.utc)
        linha = {
            "execucao_id": self.execucao_id,
            "etapa": nome,
            "camada": self.camada,
            "tabela": tabela,
            "inicio": inicio.isoformat(),
            "fim": fim.isoformat(),
            "duracao_seg": round((fim - inicio).total_seconds(), 3),
            "linhas_entrada": medida.linhas_entrada,
            "linhas_saida": medida.linhas_saida,
            "status": status,
            "erro": erro,
            "job_ids": medida.job_ids,
            "bytes_processados": medida.bytes_processados,
            "bytes_faturados": medida.bytes_faturados,
            "executado_por": self.executado_por,
        }
        self.linhas.append(linha)
        if status == "falha":
            self._escrever_log("ERROR", {**linha, "mensagem": f"Falha na etapa {nome} ({self.camada})"})

    def _escrever_log(self, severidade: str, conteudo: dict) -> None:
        """Escreve no log tc-pipeline. Se o log não puder ser escrito, avisa no terminal e segue:
        a falha do pipeline continua registrada em pipeline_runs e o script continua terminando com erro."""
        try:
            if self._logger is None:
                from google.cloud import logging as cloud_logging

                self._logger = cloud_logging.Client(project=self.cfg["projeto"]).logger(NOME_LOG)
            self._logger.log_struct(conteudo, severity=severidade, labels={"execucao_id": self.execucao_id})
        except (GoogleAPICallError, GoogleAuthError, ImportError) as erro:
            print(f"   [run_logger] não consegui escrever no Cloud Logging ({type(erro).__name__}: {erro}). "
                  "O alerta por e-mail depende do papel 'Gravador de registros' (roles/logging.logWriter).",
                  file=sys.stderr)

    def gravar(self) -> None:
        """Grava as linhas acumuladas em ops.pipeline_runs (load job, append) e escreve um resumo INFO no log."""
        if not self.linhas:
            return
        sql = (RAIZ / "ops" / "sql" / "ddl_pipeline_runs.sql").read_text(encoding="utf-8").format(**self.cfg)
        self.client.query(sql).result()
        destino = f"{self.cfg['projeto']}.{self.cfg['ops']}.pipeline_runs"
        job_config = bigquery.LoadJobConfig(schema=SCHEMA_RUNS, write_disposition="WRITE_APPEND")
        job = self.client.load_table_from_json(self.linhas, destino, job_config=job_config)
        job.result()
        falhas = sum(1 for linha in self.linhas if linha["status"] == "falha")
        print(f"   {len(self.linhas)} etapas gravadas em {destino} ({falhas} com falha; job {job.job_id})")
        self._escrever_log("INFO", {
            "execucao_id": self.execucao_id,
            "camada": self.camada,
            "etapas": len(self.linhas),
            "falhas": falhas,
            "duracao_total_seg": round(sum(linha["duracao_seg"] for linha in self.linhas), 3),
        })
