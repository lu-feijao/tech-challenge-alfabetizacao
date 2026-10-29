"""Regras de qualidade da frente 3 (catálogo em docs/qualidade/regras_qualidade.md).

Cada regra é uma consulta que devolve uma única coluna `valor` e um critério de aprovação.
- bloqueante: se reprovar, a execução termina com erro e a camada seguinte não é publicada.
- informativa: o resultado é gravado em ops.dq_results e a execução segue.
Marcadores {projeto}, {bronze}, {silver} e {gold} vêm do .env.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Regra:
    id: str
    descricao: str
    severidade: str  # "bloqueante" | "informativa"
    camada: str
    tabela: str
    sql: str
    operador: Optional[str] = None  # "==", "<=", ">=" ou None (só medição)
    limiar: Optional[float] = None


# ── Chaves de cada tabela da Silver (ficha de perfil, passo 1) ──
CHAVES_SILVER = {
    "municipio": ["ano", "id_municipio", "serie", "rede"],
    "uf": ["ano", "sigla_uf", "serie", "rede"],
    "meta_municipio": ["id_municipio", "rede", "ano_meta"],
    "meta_uf": ["ano_referencia", "sigla_uf", "rede", "ano_meta"],
    "meta_brasil": ["ano_referencia", "rede", "ano_meta"],
    "alunos": ["ano", "id_aluno", "caderno"],
}

# Colunas que não podem ficar sem tradução (R03): descrições do dicionário, rede das metas e UF do de-para
SEM_TRADUCAO = {
    "municipio": "rede_descricao = 'desconhecido' OR serie_descricao = 'desconhecido' OR sigla_uf IS NULL",
    "uf": "rede_descricao = 'desconhecido' OR serie_descricao = 'desconhecido' OR cod_uf IS NULL",
    "meta_municipio": "rede = 'desconhecido' OR sigla_uf IS NULL",
    "meta_uf": "rede = 'desconhecido' OR cod_uf IS NULL",
    "meta_brasil": "rede = 'desconhecido'",
    "alunos": (
        "serie_descricao = 'desconhecido' OR rede_descricao = 'desconhecido' "
        "OR presenca_descricao = 'desconhecido' OR preenchimento_caderno_descricao = 'desconhecido' "
        "OR alfabetizado_descricao = 'desconhecido' OR sigla_uf IS NULL"
    ),
}

TABELAS_BRONZE = [
    "alunos", "municipio", "uf", "meta_alfabetizacao_municipio",
    "meta_alfabetizacao_uf", "meta_alfabetizacao_brasil", "dicionario",
]


def regras_eventos_silver() -> list:
    """Regras da silver.alunos_eventos (streaming). Só entram quando a Silver de eventos existe."""
    t = "alunos_eventos"
    tab = "`{projeto}.{silver}.alunos_eventos`"
    return [
        # E01 · deduplicação: um id_evento por linha (prova que o duplicado enviado de propósito não chegou à Silver)
        Regra("E01", "Chave única: um id_evento por linha (deduplicação)", "bloqueante", "silver", t,
              f"SELECT COUNT(*) - COUNT(DISTINCT id_evento) AS valor FROM {tab}", "==", 0),
        # E02 · nulo em campo obrigatório do evento
        Regra("E02", "Sem nulo em id_evento, origem, id_municipio, id_aluno, ano e horários", "bloqueante", "silver", t,
              f"""SELECT COUNTIF(id_evento IS NULL OR origem IS NULL OR id_municipio IS NULL OR id_aluno IS NULL
                  OR ano IS NULL OR horario_producao IS NULL OR horario_recebimento IS NULL) AS valor FROM {tab}""",
              "==", 0),
        # E03 · origem: todo evento declara que é simulado (nunca se passa por dado oficial)
        Regra("E03", "Toda linha tem origem = 'simulado'", "bloqueante", "silver", t,
              f"SELECT COUNTIF(origem IS NULL OR origem <> 'simulado') AS valor FROM {tab}", "==", 0),
        # E04 · latência de verdade: carimbo igual nos dois campos daria latência 0 e a medida não mediria nada
        Regra("E04", "Latência medida e maior que zero (recebimento > produção)", "bloqueante", "silver", t,
              f"SELECT COUNTIF(latencia_segundos IS NULL OR latencia_segundos <= 0) AS valor FROM {tab}", "==", 0),
        # E05 · consistência: alfabetizado precisa bater com o corte de 743 pontos
        Regra("E05", "alfabetizado coerente com a proficiência (corte de 743)", "bloqueante", "silver", t,
              f"""SELECT COUNTIF(avaliado AND alfabetizado <> IF(proficiencia >= 743, '1', '0')) AS valor FROM {tab}""",
              "==", 0),
        # E06 · faixas
        Regra("E06", "Proficiência (0 a 1000) e peso (> 0) na faixa válida", "bloqueante", "silver", t,
              f"""SELECT COUNTIF(proficiencia <= 0 OR proficiencia >= 1000 OR peso_aluno <= 0) AS valor FROM {tab}""",
              "==", 0),
        # E07 · chave de relacionamento: UF derivada do município (de-para) e município existente em silver.municipio
        Regra("E07", "Match evento x município (silver.municipio) e UF com de-para", "bloqueante", "silver", t,
              f"""
              SELECT 100 * COUNTIF(m.id_municipio IS NOT NULL AND e.sigla_uf IS NOT NULL) / COUNT(*) AS valor
              FROM {tab} e
              LEFT JOIN (SELECT DISTINCT id_municipio FROM `{{projeto}}.{{silver}}.municipio`) m USING (id_municipio)
              """, ">=", 95.0),
        # E08 · duplicados removidos: Bronze de eventos menos Silver (só medição; mostra a dedup trabalhando)
        Regra("E08", "Linhas repetidas por id_evento removidas da Bronze de eventos", "informativa", "silver", t,
              """SELECT (SELECT COUNT(*) FROM `{projeto}.{bronze}.eventos_alunos`)
                      - (SELECT COUNT(*) FROM `{projeto}.{silver}.alunos_eventos`) AS valor"""),
    ]


def regras_silver(limiar_match_municipio: float = 95.0, incluir_eventos: bool = False) -> list:
    regras = []
    if incluir_eventos:
        regras.extend(regras_eventos_silver())

    # R07 · carga completa: a última rodada da Bronze tem pelo menos 95% das linhas da anterior
    for t in TABELAS_BRONZE:
        regras.append(Regra(
            "R07", "Última rodada da Bronze com >= 95% das linhas da rodada anterior (carga completa)",
            "bloqueante", "bronze", t,
            f"""
            WITH c AS (
              SELECT _ingestion_timestamp AS ts, COUNT(*) AS n FROM `{{projeto}}.{{bronze}}.{t}` GROUP BY ts
            ), o AS (SELECT n, ROW_NUMBER() OVER (ORDER BY ts DESC) AS rn FROM c)
            SELECT IFNULL(100 * SAFE_DIVIDE(MAX(IF(rn = 1, n, NULL)), MAX(IF(rn = 2, n, NULL))), 100) AS valor FROM o
            """, ">=", 95.0))

    for t, chave in CHAVES_SILVER.items():
        cols = ", ".join(chave)
        nulos = " OR ".join(f"{c} IS NULL" for c in chave)
        # R01 · duplicidade
        regras.append(Regra(
            "R01", "Chave única após filtrar a última rodada (duplicidade)", "bloqueante", "silver", t,
            f"SELECT COUNT(*) - COUNT(DISTINCT TO_JSON_STRING(STRUCT({cols}))) AS valor FROM `{{projeto}}.{{silver}}.{t}`",
            "==", 0))
        # R02 · nulo em chave
        regras.append(Regra(
            "R02", "Sem nulo em coluna de chave", "bloqueante", "silver", t,
            f"SELECT COUNTIF({nulos}) AS valor FROM `{{projeto}}.{{silver}}.{t}`",
            "==", 0))
        # R03 · código sem tradução vira 'desconhecido' e a contagem tem de ser zero
        regras.append(Regra(
            "R03", "Nenhum código sem tradução ('desconhecido') nem UF sem de-para", "bloqueante", "silver", t,
            f"SELECT COUNTIF({SEM_TRADUCAO[t]}) AS valor FROM `{{projeto}}.{{silver}}.{t}`",
            "==", 0))

    # R04 · taxa de match J1 (municipio rede '3' x meta_municipio), lado de municipio, pior ano
    regras.append(Regra(
        "R04", "Match municipio (rede 3) x meta_municipio, lado de municipio, menor % entre os anos",
        "bloqueante", "silver", "municipio x meta_municipio",
        """
        WITH res AS (SELECT ano, id_municipio, rede FROM `{projeto}.{silver}.municipio` WHERE rede = '3'),
        met AS (SELECT DISTINCT id_municipio, rede FROM `{projeto}.{silver}.meta_municipio`),
        por_ano AS (
          SELECT res.ano, 100 * COUNTIF(met.id_municipio IS NOT NULL) / COUNT(*) AS pct
          FROM res LEFT JOIN met USING (id_municipio, rede) GROUP BY res.ano
        )
        SELECT MIN(pct) AS valor FROM por_ano
        """, ">=", limiar_match_municipio))

    # R12 · taxa de match J2 (uf rede '5' x meta_uf), lado de uf, pior ano
    regras.append(Regra(
        "R12", "Match uf (rede 5) x meta_uf, lado de uf, menor % entre os anos",
        "bloqueante", "silver", "uf x meta_uf",
        """
        WITH res AS (SELECT ano, sigla_uf, rede FROM `{projeto}.{silver}.uf` WHERE rede = '5'),
        met AS (SELECT DISTINCT ano_referencia AS ano, sigla_uf, rede FROM `{projeto}.{silver}.meta_uf`),
        por_ano AS (
          SELECT res.ano, 100 * COUNTIF(met.sigla_uf IS NOT NULL) / COUNT(*) AS pct
          FROM res LEFT JOIN met USING (ano, sigla_uf, rede) GROUP BY res.ano
        )
        SELECT MIN(pct) AS valor FROM por_ano
        """, ">=", 95.0))

    # R05 · faixas válidas
    for t, cond in [
        ("municipio", "taxa_alfabetizacao < 0 OR taxa_alfabetizacao > 100"),
        ("uf", "taxa_alfabetizacao < 0 OR taxa_alfabetizacao > 100"),
        ("meta_municipio", "meta_alfabetizacao < 0 OR meta_alfabetizacao > 100"),
        ("meta_uf", "meta_alfabetizacao < 0 OR meta_alfabetizacao > 100"),
        ("meta_brasil", "meta_alfabetizacao < 0 OR meta_alfabetizacao > 100"),
        ("alunos", "proficiencia <= 0 OR peso_aluno <= 0"),
    ]:
        regras.append(Regra(
            "R05", "Valores dentro da faixa válida (taxas e metas 0-100; proficiência e peso > 0)",
            "bloqueante", "silver", t,
            f"SELECT COUNTIF({cond}) AS valor FROM `{{projeto}}.{{silver}}.{t}`", "==", 0))

    # R06 · proficiência e peso nulos nas mesmas linhas (define quem é avaliado)
    regras.append(Regra(
        "R06", "Proficiência e peso nulos nas mesmas linhas", "bloqueante", "silver", "alunos",
        "SELECT COUNTIF((proficiencia IS NULL) <> (peso_aluno IS NULL)) AS valor FROM `{projeto}.{silver}.alunos`",
        "==", 0))

    # ── Informativas ──
    for t in ["municipio", "uf"]:
        regras.append(Regra(
            "R08", "Soma das 9 proporções de nível = 100 ± 0,05 (só linhas com proporções)", "informativa", "silver", t,
            f"""
            SELECT COUNTIF(ABS(proporcao_aluno_nivel_0 + proporcao_aluno_nivel_1 + proporcao_aluno_nivel_2
              + proporcao_aluno_nivel_3 + proporcao_aluno_nivel_4 + proporcao_aluno_nivel_5
              + proporcao_aluno_nivel_6 + proporcao_aluno_nivel_7 + proporcao_aluno_nivel_8 - 100) > 0.05) AS valor
            FROM `{{projeto}}.{{silver}}.{t}` WHERE proporcao_aluno_nivel_0 IS NOT NULL
            """, "==", 0))

    regras.append(Regra(
        "R09", "% de municípios (2023 e 2024) com taxa da meta municipal = taxa de municipio (tolerância 0,01)",
        "informativa", "silver", "meta_municipio x municipio",
        """
        WITH mt AS (
          SELECT ano, TRIM(id_municipio) AS id_municipio, taxa_alfabetizacao
          FROM `{projeto}.{bronze}.meta_alfabetizacao_municipio`
          WHERE _ingestion_timestamp = (SELECT MAX(_ingestion_timestamp) FROM `{projeto}.{bronze}.meta_alfabetizacao_municipio`)
            AND taxa_alfabetizacao IS NOT NULL
        )
        SELECT 100 * COUNTIF(ABS(mt.taxa_alfabetizacao - m.taxa_alfabetizacao) < 0.01) / COUNT(*) AS valor
        FROM mt JOIN `{projeto}.{silver}.municipio` m
          ON m.id_municipio = mt.id_municipio AND m.ano = mt.ano AND m.rede = '3'
        """, ">=", 95.0))

    regras.append(Regra(
        "R10", "Cadernos fora da faixa 1 a 21", "informativa", "silver", "alunos",
        "SELECT COUNTIF(SAFE_CAST(caderno AS INT64) NOT BETWEEN 1 AND 21) AS valor FROM `{projeto}.{silver}.alunos`",
        "==", 0))

    regras.append(Regra(
        "R11", "UFs com resultado em uf (de 27)", "informativa", "silver", "uf",
        "SELECT COUNT(DISTINCT sigla_uf) AS valor FROM `{projeto}.{silver}.uf`",
        ">=", 27))

    return regras


def regras_eventos_gold() -> list:
    """Regras da gold.indicador_por_origem (oficial + simulado, separados pela coluna origem)."""
    t = "indicador_por_origem"
    tab = "`{projeto}.{gold}.indicador_por_origem`"
    return [
        Regra("G03", "origem sempre preenchida com 'oficial' ou 'simulado'", "bloqueante", "gold", t,
              f"SELECT COUNTIF(origem IS NULL OR origem NOT IN ('oficial', 'simulado')) AS valor FROM {tab}", "==", 0),
        Regra("G04", "Chave única por origem, ano, município, série e rede", "bloqueante", "gold", t,
              f"""SELECT COUNT(*) - COUNT(DISTINCT TO_JSON_STRING(STRUCT(origem, ano, id_municipio, serie, rede))) AS valor
                  FROM {tab}""", "==", 0),
        Regra("G05", "Eventos simulados chegaram à Gold (linhas com origem = 'simulado')", "bloqueante", "gold", t,
              f"SELECT COUNTIF(origem = 'simulado') AS valor FROM {tab}", ">=", 1),
        Regra("G06", "Taxa entre 0 e 100 nas duas origens", "bloqueante", "gold", t,
              f"SELECT COUNTIF(taxa_alfabetizacao < 0 OR taxa_alfabetizacao > 100) AS valor FROM {tab}", "==", 0),
        Regra("G07", "Eventos simulados não usam anos do indicador oficial (nenhum ano em comum)", "informativa", "gold", t,
              f"""SELECT COUNT(DISTINCT s.ano) AS valor
                  FROM {tab} s JOIN {tab} o ON o.ano = s.ano AND o.origem = 'oficial'
                  WHERE s.origem = 'simulado'""", "==", 0),
    ]


def regras_gold(incluir_eventos: bool = False) -> list:
    regras = []
    if incluir_eventos:
        regras.extend(regras_eventos_gold())
    for t in ["municipio_meta", "uf_meta", "brasil_meta"]:
        regras.append(Regra(
            "G01", "Status de meta calculado só com taxa e meta preenchidas", "bloqueante", "gold", t,
            f"""
            SELECT COUNTIF(status_meta <> 'sem_meta' AND (taxa_alfabetizacao IS NULL OR meta_alfabetizacao IS NULL)) AS valor
            FROM `{{projeto}}.{{gold}}.{t}`
            """, "==", 0))
        regras.append(Regra(
            "G02", "Status de meta preenchido com um dos 3 estados", "bloqueante", "gold", t,
            f"""
            SELECT COUNTIF(status_meta IS NULL OR status_meta NOT IN ('atingiu', 'nao_atingiu', 'sem_meta')) AS valor
            FROM `{{projeto}}.{{gold}}.{t}`
            """, "==", 0))

    regras.append(Regra(
        "R13", "Municípios em 'sem_meta' em 2024 (rede municipal)", "informativa", "gold", "municipio_meta",
        "SELECT COUNTIF(ano = 2024 AND status_meta = 'sem_meta') AS valor FROM `{projeto}.{gold}.municipio_meta`"))

    regras.append(Regra(
        "V01", "Validação cruzada Brasil 2024: |taxa recalculada - oficial| em p.p.", "informativa", "gold",
        "validacao_cruzada",
        """
        SELECT ABS(diferenca_pp) AS valor FROM `{projeto}.{gold}.validacao_cruzada`
        WHERE nivel = 'brasil' AND ano = 2024 AND rede = '5'
        """, "<=", 0.5))

    regras.append(Regra(
        "V02", "Validação cruzada municípios 2024 (rede 3): % a até 0,5 p.p. da taxa oficial", "informativa", "gold",
        "validacao_cruzada",
        """
        SELECT 100 * COUNTIF(ABS(diferenca_pp) <= 0.5) / COUNTIF(diferenca_pp IS NOT NULL) AS valor
        FROM `{projeto}.{gold}.validacao_cruzada`
        WHERE nivel = 'municipio' AND ano = 2024 AND rede = '3'
        """, ">=", 95.0))
    return regras
