# Números do projeto e de onde vêm

Todo número que aparece no README ou no vídeo precisa estar aqui, com a fonte. Se um número mudar, atualize esta tabela primeiro.

**Legenda:** ✅ medido · ≈ estimado a partir de medições · ⏳ pendente

## Dados e camadas

| # | Número | Valor | Fonte | Medido em |
|---|---|---|---|---|
| 1 | Tabelas no projeto | **28 objetos**: 27 tabelas e 1 view (bronze 9, silver 9, gold 6, ops 4) | `docs/dados/catalogo/catalogo_dados.md` | ✅ 28/10 |
| 2 | Linhas de `bronze_tc.alunos` | **7.735.998** | catálogo | ✅ 24/10 |
| 3 | Linhas de `silver_tc.alunos` | **3.867.999**, exatamente metade da Bronze, que tem 2 cargas em acréscimo | catálogo | ✅ 24/10 |
| 4 | Armazenamento total | **1,74 GiB** lógicos (1.781,84 MiB) | catálogo | ✅ 28/10 |
| 5 | Tamanho de uma carga completa da Bronze | **486 MiB** (0,475 GiB) | 972,63 MiB ÷ 2 cargas | ✅ 24/10 |

## Qualidade (Frente 3)

| # | Número | Valor | Fonte | Medido em |
|---|---|---|---|---|
| 6 | Resultados de regras gravados | **248** em `ops_tc.dq_results`, de 8 execuções (5 da Silver, 3 da Gold) | `SELECT ... GROUP BY execucao_id, severidade, status` | ✅ 29/10 |
| 7 | Resultados bloqueantes aprovados | **209** | idem | ✅ 29/10 |
| 8 | Falha bloqueante registrada (pipeline parou) | **1**: R04 na Silver (97,32% contra o limiar de 99,9% do `--simular-falha`), execução `silver_20261021_160213_34ac17`, 21/10/2026 às 13:02 | idem | ✅ 29/10 |
| 9 | Resultados informativos reprovados (só avisam) | **15**: R09, R10 e R11 em cada uma das 5 execuções da Silver | idem | ✅ 29/10 |

## Streaming (Frente 2)

| # | Número | Valor | Fonte | Medido em |
|---|---|---|---|---|
| 10 | Eventos simulados recebidos | **15**, em 3 rodadas (23/10 e 28/10 com o notebook; 29/10 com os scripts do repositório), todos com `id_evento` distinto | `bronze_tc.eventos_alunos` | ✅ 29/10 |
| 11 | Latência produção → recebimento | **0,91 a 17,11 s** (média 6,96 s, mediana 4,23 s nas 15). Por rodada: 23/10 mediana 14,45 s; 28/10 mediana 2,81 s; 29/10 mediana 4,23 s | `bronze_tc.eventos_alunos.latencia_segundos` | ✅ 29/10 |
| 12 | Eventos rejeitados | **3**, um por rodada, por campo ausente (`id_municipio`) | `ops_tc.eventos_rejeitados` | ✅ 29/10 |
| 13 | Linhas por origem na Gold | **10.896 oficiais + 1 simulada** (município 3550308, 2026, taxa 49,82 sobre 15 eventos) | `gold_tc.indicador_por_origem` | ✅ 29/10 |

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
| 21c | Status da meta na Gold, por município (rede municipal) | **2024: atingiu 2.788 · não atingiu 2.444 · sem meta 216.** 2023: sem meta 5.448 (as metas começam em 2024). Somando os dois anos, sem meta = 5.664 | `gold_tc.municipio_meta` | ✅ 29/10 |

## Observabilidade (Frente 4)

| # | Número | Valor | Fonte | Medido em |
|---|---|---|---|---|
| 22 | Execuções registradas em `ops_tc.pipeline_runs` | **3 execuções reais em 29/10** (Silver com `--simular-falha`: 11 etapas, 1 falha; Silver: 10 etapas; Gold: 8 etapas), além das 4 linhas de teste de 26/10 e 28/10 (`etapa='teste_frente4'`) | `SELECT * FROM ops_tc.pipeline_runs` | ✅ 29/10 |
| 23 | Tempo entre a falha e o alerta | **15 s** com falha real da Silver (29/10: falha 17:35:40, alerta 17:35:55, e-mail 17:35); 52 s no teste de 28/10 | `pipeline_runs`, Cloud Monitoring; prints e detalhes em `docs/evidencias/alerta/` | ✅ 29/10 |
| 24 | Duração de uma execução completa do batch (Silver + Gold) | **≈ 85 s** (Silver 62,2 s; Gold 23,1 s); ≈ 2,53 GB faturados (Silver 2,166; Gold 0,368) | `SELECT SUM(duracao_seg), SUM(bytes_faturados) ... GROUP BY execucao_id` | ✅ 29/10 |
