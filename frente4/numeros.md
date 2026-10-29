# Números do projeto e de onde vêm

Todo número que aparece no README ou no vídeo precisa estar aqui, com a fonte. Se um número mudar, atualize esta tabela primeiro.

**Legenda:** ✅ medido · ≈ estimado a partir de medições · ⏳ pendente

## Dados e camadas

| # | Número | Valor | Fonte | Medido em |
|---|---|---|---|---|
| 1 | Tabelas no projeto | **28 objetos**: 27 tabelas e 1 view (bronze 9, silver 9, gold 6, ops 4) | `docs/catalogo/catalogo_dados.md` (`ops/sql/catalogo/catalogo_tabelas.sql`) | ✅ 28/10 |
| 2 | Linhas de `bronze_tc.alunos` | **7.735.998** | catálogo | ✅ 24/10 |
| 3 | Linhas de `silver_tc.alunos` | **3.867.999**, exatamente metade da Bronze, que tem 2 cargas em acréscimo | catálogo | ✅ 24/10 |
| 4 | Armazenamento total | **1,74 GiB** lógicos (1.781,84 MiB) | catálogo | ✅ 28/10 |
| 5 | Tamanho de uma carga completa da Bronze | **486 MiB** (0,475 GiB) | 972,63 MiB ÷ 2 cargas | ✅ 24/10 |

## Qualidade (Frente 3)

| # | Número | Valor | Fonte | Medido em |
|---|---|---|---|---|
| 6 | Resultados de regras gravados | **187** em `ops_tc.dq_results` | `SELECT ... GROUP BY camada, severidade, status` | ✅ 24/10 |
| 7 | Regras bloqueantes aprovadas | **158** (bronze 28, silver 114, gold 16) | idem | ✅ 24/10 |
| 8 | Falha bloqueante registrada (pipeline parou) | **1**, na silver, em 21/10/2026 às 13:02 | idem | ✅ 24/10 |
| 9 | Regras informativas reprovadas (só avisam) | **12** na silver | idem | ✅ 24/10 |

## Streaming (Frente 2)

| # | Número | Valor | Fonte | Medido em |
|---|---|---|---|---|
| 10 | Eventos simulados recebidos | **5** | `ops/sql/finops/numeros_streaming.sql` | ✅ 24/10 |
| 11 | Latência produção → recebimento | **média de 12,1 s** (mínima 0,9 s; máxima 17,1 s) | `bronze_tc.eventos_alunos.latencia_segundos` | ✅ 24/10 |
| 12 | Eventos rejeitados | **1**, por campo ausente (`id_municipio`) | `ops_tc.eventos_rejeitados` | ✅ 24/10 |
| 13 | Linhas por origem na Gold | **10.896 oficiais + 1 simulada** | `gold_tc.indicador_por_origem` | ✅ 24/10 |

## Custo (Frente 4)

| # | Número | Valor | Fonte | Medido em |
|---|---|---|---|---|
| 14 | Custo real hoje | **R$ 0,00** gastos de R$ 50,00 no orçamento "TC Fase 02"; faturamento ativo desde 28/10 (free trial), uso dentro das franquias gratuitas | print `docs/evidencias/finops/orcamento_01_lista.png` e `gcloud billing projects describe` (`billingEnabled: true`) | ✅ 28/10 |
| 15 | Preço de consulta em São Paulo | **US$ 11,25 / TiB**, contra US$ 6,25 nos EUA | catálogo de SKUs do Google, SKU 491C-41CF-D16D | ✅ 24/10 |
| 16 | Leitura por execução completa (Silver + Gold + regras) | **≈ 2,3 GB** (2,14 GiB); a Silver lê a Bronze inteira (1,009 GB) | README do grupo, "Custo medido" (Frente 3) | ✅ 28/10 |
| 17 | Ler 5 colunas em vez de `SELECT *` (Bronze alunos) | **−81%** (962 → 184 MiB) | dry run no editor | ✅ 22/10 |
| 18 | Filtrar a partição `ano = 2024` (Silver alunos) | **−45%** (794 → 436 MiB) | dry run no editor | ✅ 22/10 |
| 19 | Consultas no mês 6, desenho atual (a Silver relê toda a Bronze) | **US$ 26,62/mês** | `docs/finops/tabela_custo.md`, cenário A | ≈ |
| 20 | Consultas no mês 6, lendo só a última carga | **US$ 0,55/mês** | idem, cenário B | ≈ |
| 21 | Total mensal em produção (cenário B) | **≈ US$ 0,89** sem franquia; **US$ 0** com franquia | idem | ≈ |
| 21a | Consumo real de consultas (17/10 a 26/10) | **418 consultas, 20,41 GiB faturados, 17 com erro**; ≈ US$ 0,22 sem franquia | `ops/sql/finops/consumo_consultas_30d.sql` | ✅ 26/10 |
| 21b | Cargas na Bronze de alunos | **2** (16/10 16:46 e 17/10 16:19), cada uma com 3.867.999 linhas | `SELECT _ingestion_timestamp, COUNT(*)` | ✅ 26/10 |
| 21c | Status da meta na Gold, por município | **atingiu 2.788 · não atingiu 2.444 · sem meta 5.664** | `gold_tc.municipio_meta` | ✅ 26/10 |

## Observabilidade (Frente 4)

| # | Número | Valor | Fonte | Medido em |
|---|---|---|---|---|
| 22 | Execuções registradas em `ops_tc.pipeline_runs` | **4 linhas de teste** (`etapa='teste_frente4'`), de 2 execuções: 26/10 e 28/10, cada uma com 1 sucesso e 1 falha. Nenhuma etapa real ainda usa o logger | `SELECT * FROM ops_tc.pipeline_runs` | ✅ 28/10 |
| 23 | Tempo entre a falha e o e-mail | **≈ 1 minuto**: falha às 20:20:29, alerta aberto às 20:21:21 (52 s), e-mail recebido às 20:21 | teste `python -m ops.testar_alerta`, execução `teste_20261028_232024_f5c54d`; print em `docs/frente4/evidencias/` | ✅ 28/10 |
| 24 | Duração de uma execução completa do batch | **pendente**: vem de `pipeline_runs` | `SELECT SUM(duracao_seg) ... GROUP BY execucao_id` | ⏳ |
