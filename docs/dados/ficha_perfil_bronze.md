# Ficha de perfil da Bronze (Frente 3, passo 1)

Fonte: dataset `bronze_tc`, projeto GCP do grupo. Perfil feito entre 17/10 e 20/10/2026 com os scripts de `sql/profiling/`.

**Rodadas de carga:** todas as 7 tabelas têm duas rodadas idênticas (2026-10-16 19:46:40 UTC e 2026-10-17 19:19:46 UTC), com o mesmo número de linhas. Todos os números abaixo são da **última rodada** (`_ingestion_timestamp = MAX(_ingestion_timestamp)`), que é a regra de leitura da Silver.

**Colunas de controle:** `_ingestion_timestamp` (TIMESTAMP) e `_source` (STRING) em todas as tabelas. Não há `execucao_id` nem coluna `origem` (oficial x simulado) como prevê o contrato de dados.

**Tipos:** `ano` e `nivel_alfabetizacao` são INT64; medidas (taxas, metas, proporções, proficiência, peso) são FLOAT64; todo o resto é STRING, inclusive códigos (`rede`, `serie`, `caderno`) e flags (`presenca`, `alfabetizado`, `preenchimento_caderno`). Decisão do grupo: manter os tipos de origem na Silver.

## Resumo

| Tabela | Linhas | Chave única (confirmada) | Anos | `rede` | `serie` |
|---|---|---|---|---|---|
| alunos | 3.867.999 | `ano + id_aluno + caderno` | 2023, 2024 | '2', '3', '4' | '2' |
| municipio | 23.995 | `ano + id_municipio + serie + rede` | 2023, 2024 | '0', '2', '3', '5' | '2' |
| uf | 145 | `ano + sigla_uf + serie + rede` | 2023, 2024 | '0', '2', '3', '5' | '2' |
| meta_alfabetizacao_municipio | 10.704 | `ano + id_municipio + rede` | 2023, 2024 | 'Municipal' (texto) | não tem |
| meta_alfabetizacao_uf | 81 | `ano + sigla_uf + rede` | 2023, 2024, 2025 | 'Pública' (texto) | não tem |
| meta_alfabetizacao_brasil | 3 | `ano + rede` | 2023, 2024, 2025 | 'Pública' (texto) | não tem |
| dicionario | 27 | `id_tabela + nome_coluna + chave` | — | — | — |

Nenhuma tabela tem duplicidade na chave dentro da última rodada.

## alunos

- 2023: 1.747.439 linhas; 2024: 2.120.560.
- `rede`: '3' Municipal 3.432.576; '2' Estadual 435.398; '4' Privada 25 (só em 2024).
- `caderno`: '1' a '21' (175 mil a 250 mil linhas cada) e '43' com 18 linhas (todas de 2024, municípios do ES, valores normais).
- Nulos: só `proficiencia` e `peso_aluno`, 513.338 cada = 512.153 ausentes (`presenca = '0'`) + 1.185 presentes com caderno não preenchido. Demais colunas: zero nulo.
- **Alunos avaliados** (caderno preenchido, com proficiência e peso): 3.354.661. `alfabetizado = '0'` também aparece para quem não foi avaliado, então o denominador da taxa deve ser os avaliados, não o total de linhas.
- Faixas: `proficiencia` 578,46 a 904,38; `peso_aluno` 0,095 a 142,55 (nenhum peso ≤ 0).
- `id_municipio` com 7 dígitos (código IBGE).

## municipio

- 5.550 municípios distintos (o Brasil tem 5.570). Por prefixo do código IBGE: 26 UFs; **RR (14) ausente**; DF (53) com 1 município.
- Linhas por ano e rede: 2023 → '2' 1.149, '3' 5.448, '5' 4.950; 2024 → '0' 398, '2' 1.086, '3' 5.448, '5' 5.516.
- Nulos: as 9 colunas `proporcao_aluno_nivel_0..8` são nulas em **todas** as 11.547 linhas de 2023 e preenchidas em todas as de 2024. `taxa_alfabetizacao` e `media_portugues` sem nulos.
- Escala: `taxa_alfabetizacao` de 2,12 a 100 (percentual 0-100); `media_portugues` de 673,30 a 868,46; soma das proporções de 99,98 a 100,02 (2024).
- Observação: em 2023 a rede '5' (Pública, que inclui a municipal) tem menos municípios que a rede '3'.

## uf

- **25 UFs: faltam DF e RR.**
- Linhas por ano e rede: 2023 → '2' 22, '3' 24, '5' 24; 2024 → '0' 1, '2' 24, '3' 25, '5' 25.
- Nulos: proporções por nível nulas em todas as 70 linhas de 2023 (mesmo padrão de `municipio`).
- Escala: `taxa_alfabetizacao` de 30,57 a 86,21; `media_portugues` de 712,56 a 797,34.

## meta_alfabetizacao_municipio

- 5.352 municípios × 2 anos (2023 e 2024). `nivel_alfabetizacao` não faz parte do grão (é atributo).
- `rede` só tem o texto 'Municipal' (em `municipio` o código é '3').
- `id_municipio` com 7 dígitos; maior código 5222302 (GO), então o DF não aparece.
- As metas de 2024 a 2030 são idênticas nas linhas de 2023 e de 2024 do mesmo município; `meta_alfabetizacao_2030 = 80` para todos.
- `nivel_alfabetizacao`: valores 0 a 5, sem tradução no dicionário; muda entre os anos em 3.430 municípios.
- Nulos: `taxa_alfabetizacao`, `nivel_alfabetizacao` e `percentual_participacao` com 120 nulos cada, todos em 2023 e nas mesmas linhas; `meta_alfabetizacao_2024` com 240 nulos (120 por ano); metas de 2025 a 2030 sem nulos.
- Faixas: taxa 4,4 a 100; meta 2024 de 7,94 a 80; participação 70 a 100.

## meta_alfabetizacao_uf

- 27 UFs × 3 anos (2023, 2024, 2025): **inclui DF e RR**, que não existem em `uf`.
- `rede` só tem o texto 'Pública'.
- Nulos: `taxa_alfabetizacao` 4, `meta_alfabetizacao_2024` 9, `meta_alfabetizacao_2025` 3, `meta_alfabetizacao_2030` 2, `percentual_participacao` 4.

## meta_alfabetizacao_brasil

| ano | rede | taxa | meta 2024 | 2025 | 2026 | 2027 | 2028 | 2029 | 2030 | participação |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023 | Pública | 55,9 | 59,9 | 63,77 | 67,47 | 70,97 | 74,23 | 77,24 | 80,0 | 86,0 |
| 2024 | Pública | 59,2 | 59,9 | 63,77 | 67,47 | 70,97 | 74,23 | 77,24 | 80,0 | 87,37 |
| 2025 | Pública | 66,0 | 60,0 | 64,0 | 67,0 | 71,0 | 74,0 | 77,0 | 80,0 | 88,0 |

- Sem nulos. A linha de 2025 traz as metas arredondadas.
- **2025 só existe nas tabelas de meta** (UF e Brasil); `alunos`, `municipio` e `uf` vão até 2024.

## dicionario

- 27 linhas; conteúdo idêntico nas duas rodadas.
- `rede`: 0 Total (Federal, Estadual, Municipal e Privada); 1 Federal; 2 Estadual; 3 Municipal; 4 Privada; 5 Pública (Estadual e Municipal); 6 Pública (Federal, Estadual e Municipal). Os códigos 0, 5 e 6 são agregados e só existem em `municipio` e `uf`.
- `serie` 2 = 2º ano do Ensino Fundamental; `presenca` 0/1 = Ausente/Presente; `preenchimento_caderno` 0/1 = Prova não preenchida/preenchida; `alfabetizado` 0/1 = Não/Sim.
- Não traduz `caderno`, `nivel_alfabetizacao`, `sigla_uf` nem as colunas das tabelas de meta.
