#!/usr/bin/env python3
"""Tech Challenge Fase 2 - Camada Gold + regras de qualidade.

1. Portão: só segue se a execução mais recente da Silver tiver todas as regras bloqueantes aprovadas
   (consulta ops.dq_results).
2. Executa, em ordem, os arquivos de gold/sql/ (meta x resultado, evolução e validação cruzada).
3. Avalia as regras da Gold e grava em ops.dq_results (load job) e em docs/evidencias/.
4. Cada etapa (portão, cada SQL, as regras e a gravação) vira uma linha em ops.pipeline_runs
   (ops/run_logger.py). Uma falha também é escrita no log tc-pipeline, que dispara o alerta por e-mail.

Uso (a partir da raiz do repositório, depois da Silver):
    python gold/gold_transformacao.py

Código de saída: 0 = Gold publicada e aprovada | 1 = Silver não aprovada ou regra bloqueante da Gold reprovada
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from quality.dq import (  # noqa: E402
    RegraBloqueanteReprovada,
    avaliar_regras,
    carregar_config,
    conectar,
    executar_sql,
    exigir_bloqueantes_aprovadas,
    gravar_resultados,
    novo_execucao_id,
    requisitos_pendentes,
    tabela_existe,
    ultima_validacao_silver_aprovada,
)
from quality.regras import regras_gold  # noqa: E402
from ops.run_logger import RegistroExecucao, executar_sql_registrado  # noqa: E402

PASTA_SQL = RAIZ / "gold" / "sql"


def main() -> int:
    cfg = carregar_config()
    client = conectar(cfg)
    execucao_id = novo_execucao_id("gold")
    registro = RegistroExecucao(client, cfg, execucao_id, camada="gold")

    try:
        print("== Portão: última validação da Silver ==")
        if not ultima_validacao_silver_aprovada(client, cfg):
            print("ERRO: a última execução da Silver não foi aprovada (ou não existe). Gold não publicada.")
            print("Rode 'python silver/silver_transformacao.py' e corrija as regras reprovadas.")
            registro.falha("portao_silver", "Última execução da Silver não aprovada (ou inexistente): Gold não publicada")
            return 1
        print("   Silver aprovada.\n")

        print("Execução:", execucao_id, "\n")

        print("== Gold: transformações ==")
        for arquivo in sorted(PASTA_SQL.glob("*.sql")):
            pendentes = requisitos_pendentes(client, arquivo, cfg)
            if pendentes:
                print(f"   {arquivo.name}: PULADO (etapa opcional; falta {', '.join(pendentes)})")
                continue
            executar_sql_registrado(registro, arquivo, executar_sql)

        print("\n== Gold: regras de qualidade ==")
        com_eventos = tabela_existe(client, f"{cfg['projeto']}.{cfg['gold']}.indicador_por_origem")
        regras = regras_gold(incluir_eventos=com_eventos)
        with registro.etapa("regras_qualidade") as medida:
            resultados = avaliar_regras(client, regras, cfg, execucao_id,
                                        job_config=registro.config_job("regras_qualidade"), medida=medida)
            medida.linhas_entrada, medida.linhas_saida = len(regras), len(resultados)

        print("\n== Gravação dos resultados ==")
        with registro.etapa("gravar_dq_results", tabela=f"{cfg['ops']}.dq_results") as medida:
            gravar_resultados(client, cfg, resultados, "gold")
            medida.linhas_saida = len(resultados)

        try:
            exigir_bloqueantes_aprovadas(resultados)
        except RegraBloqueanteReprovada as erro:
            print(f"\nERRO: {erro}")
            registro.falha("regras_bloqueantes", str(erro), tabela=f"{cfg['ops']}.dq_results")
            return 1

        print("\nGold publicada: todas as regras bloqueantes aprovadas.")
        return 0
    finally:
        print("\n== Métricas de execução ==")
        registro.gravar()


if __name__ == "__main__":
    sys.exit(main())
