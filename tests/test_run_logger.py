"""Testes do registro de métricas de execução (ops/run_logger.py), sem acesso ao GCP."""
import unittest
from unittest import mock

from ops import run_logger
from ops.run_logger import RegistroExecucao, tabelas_citadas, valor_label

CFG = {"projeto": "p", "bronze": "bronze_tc", "silver": "silver_tc", "gold": "gold_tc", "ops": "ops_tc"}


def novo_registro():
    registro = RegistroExecucao(mock.MagicMock(), CFG, "silver_20261029_000000_abc123", camada="silver")
    registro._escrever_log = mock.MagicMock()  # não toca no Cloud Logging
    return registro


class TestRunLogger(unittest.TestCase):
    def test_etapa_com_sucesso_vira_uma_linha(self):
        registro = novo_registro()
        with registro.etapa("07_alunos", tabela="silver_tc.alunos") as medida:
            medida.adicionar_job({"job_id": "j1", "bytes_processados": 10, "bytes_faturados": 20})
            medida.linhas_saida = 5
        linha = registro.linhas[0]
        self.assertEqual(linha["status"], "sucesso")
        self.assertEqual(linha["job_ids"], ["j1"])
        self.assertEqual((linha["bytes_processados"], linha["bytes_faturados"], linha["linhas_saida"]), (10, 20, 5))
        registro._escrever_log.assert_not_called()

    def test_excecao_registra_falha_escreve_erro_e_repassa(self):
        registro = novo_registro()
        with self.assertRaises(ValueError):
            with registro.etapa("02_municipio"):
                raise ValueError("SQL quebrado")
        self.assertEqual(registro.linhas[0]["status"], "falha")
        self.assertIn("ValueError: SQL quebrado", registro.linhas[0]["erro"])
        self.assertEqual(registro._escrever_log.call_args[0][0], "ERROR")

    def test_falha_sem_excecao_tambem_escreve_erro(self):
        registro = novo_registro()
        registro.falha("regras_bloqueantes", "1 regra(s) bloqueante(s) reprovada(s)")
        self.assertEqual(registro.linhas[0]["status"], "falha")
        self.assertEqual(registro._escrever_log.call_args[0][0], "ERROR")

    def test_config_job_tem_labels_validos_e_teto(self):
        config = novo_registro().config_job("07_Alunos.v2")
        self.assertEqual(config.labels, {"pipeline": "tc", "camada": "silver", "etapa": "07_alunos_v2"})
        self.assertEqual(config.maximum_bytes_billed, run_logger.TETO_BYTES_FATURADOS)
        self.assertEqual(valor_label("A" * 80), "a" * 63)

    def test_tabelas_citadas_separa_destino_e_entrada(self):
        sql = ("CREATE OR REPLACE TABLE `p.silver_tc.alunos` AS SELECT * FROM `p.bronze_tc.alunos` "
               "JOIN `p.silver_tc.de_para_uf` USING (cod_uf)")
        self.assertEqual(tabelas_citadas(sql), {
            "destino": ["p.silver_tc.alunos"], "entrada": ["p.bronze_tc.alunos", "p.silver_tc.de_para_uf"],
        })

    def test_gravar_sem_linhas_nao_chama_o_bigquery(self):
        registro = novo_registro()
        registro.gravar()
        registro.client.load_table_from_json.assert_not_called()


if __name__ == "__main__":
    unittest.main()
