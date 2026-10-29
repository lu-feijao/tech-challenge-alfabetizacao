-- Silver · tabelas de de-para (decisões D1 e D4 de docs/dados/mapa_joins.md)
-- Marcadores {projeto}, {silver} etc. são preenchidos pelo silver_transformacao.py a partir do .env.

-- D4: código IBGE da UF (2 primeiros dígitos do id_municipio) -> sigla
CREATE OR REPLACE TABLE `{projeto}.{silver}.de_para_uf` AS
SELECT cod_uf, sigla_uf
FROM UNNEST([
  STRUCT('11' AS cod_uf, 'RO' AS sigla_uf), ('12', 'AC'), ('13', 'AM'), ('14', 'RR'), ('15', 'PA'),
  ('16', 'AP'), ('17', 'TO'), ('21', 'MA'), ('22', 'PI'), ('23', 'CE'), ('24', 'RN'), ('25', 'PB'),
  ('26', 'PE'), ('27', 'AL'), ('28', 'SE'), ('29', 'BA'), ('31', 'MG'), ('32', 'ES'), ('33', 'RJ'),
  ('35', 'SP'), ('41', 'PR'), ('42', 'SC'), ('43', 'RS'), ('50', 'MS'), ('51', 'MT'), ('52', 'GO'),
  ('53', 'DF')
]);

-- D1: a rede das tabelas de meta vem como texto; nas tabelas de resultado é código do dicionário.
-- 'Pública' -> '5' (Pública Estadual e Municipal): o código '6' não aparece nas tabelas de resultado.
CREATE OR REPLACE TABLE `{projeto}.{silver}.de_para_rede_meta` AS
SELECT rede_texto, rede
FROM UNNEST([
  STRUCT('Municipal' AS rede_texto, '3' AS rede),
  ('Pública', '5')
]);
