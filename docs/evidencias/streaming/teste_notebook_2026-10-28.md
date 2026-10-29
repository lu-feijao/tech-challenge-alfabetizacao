# Evidência do streaming: segunda rodada, 28/10/2026 (21:17, horário de Brasília)

Executada com o notebook [`teste_streaming_unico.ipynb`](teste_streaming_unico.ipynb) (producer e consumer na mesma sessão, consumer em segundo plano), contra o tópico `topico-alfabetizacao` e a assinatura `topico-alfabetizacao-sub` do projeto do grupo.
O notebook tem a mesma lógica dos scripts de [`streaming/`](../../../streaming/), mas não é o código do pipeline: fica aqui como evidência. Os scripts `streaming/producer.py` e `streaming/consumer.py` ainda não foram executados contra o Pub/Sub (ver Limitações no README).

Diferente da primeira rodada (23/10), as tabelas **não** foram apagadas antes: a Bronze de eventos só acrescenta, e os eventos desta rodada se separam dos anteriores pelo horário de recebimento.

## Saída do notebook (producer + consumer)

```
Escutando topico-alfabetizacao-sub (para após 20s sem mensagens ou em 180s)...
Iniciando envio para o tópico: projects/project-ce782257-1c9c-4b6f-87a/topics/topico-alfabetizacao
[1/5] válido enviado | id_evento=f7949f9e-902d-4025-8c3e-add5c4b0751f | pubsub=20335441516443862
[2/5] válido enviado | id_evento=dba5f840-62fb-4b20-b3d3-ad550c8f2d75 | pubsub=20335443236735063
[3/5] válido enviado | id_evento=0ef20faa-47a1-42ab-af09-a57625eeba72 | pubsub=22129090020552508
1 linhas gravadas em project-ce782257-1c9c-4b6f-87a.bronze_tc.eventos_alunos (job 490532f2-460c-4570-bde6-8bbba7b152b5)
Lote: 1 recebidas | 1 válidas | 0 duplicadas ignoradas | 0 rejeitadas
Latência (s): mín 0.97 | média 0.97 | máx 0.97
[4/5] válido enviado | id_evento=fb85975f-21ec-4ee1-9a35-2991d49e3258 | pubsub=20335491421635699
[5/5] válido enviado | id_evento=fbefd9d5-1a53-4052-8af5-adb145e7ffef | pubsub=22127284098106188
2 linhas gravadas em project-ce782257-1c9c-4b6f-87a.bronze_tc.eventos_alunos (job eaebf962-9402-4918-b27d-30d6aa67e7c1)
Lote: 2 recebidas | 2 válidas | 0 duplicadas ignoradas | 0 rejeitadas
Latência (s): mín 1.55 | média 2.57 | máx 3.59
duplicado enviado | id_evento=fbefd9d5-1a53-4052-8af5-adb145e7ffef
inválido enviado (sem id_municipio) | id_evento=dabc107b-1308-484c-8811-7915b0b2d427
Fim. Esperado no consumer: 5 válidos, 1 duplicado ignorado, 1 rejeitado(s).
1 linhas gravadas em project-ce782257-1c9c-4b6f-87a.bronze_tc.eventos_alunos (job cef5dfe2-8526-4d90-8485-5ca73efab932)
1 linhas gravadas em project-ce782257-1c9c-4b6f-87a.ops_tc.eventos_rejeitados (job 06378d54-d0e8-4959-b68a-13f64bf51931)
Lote: 2 recebidas | 1 válidas | 0 duplicadas ignoradas | 1 rejeitadas
Latência (s): mín 2.81 | média 2.81 | máx 2.81
1 linhas gravadas em project-ce782257-1c9c-4b6f-87a.bronze_tc.eventos_alunos (job f7fd2f27-4562-4979-b537-5fced5cc8dc8)
Lote: 2 recebidas | 1 válidas | 1 duplicadas ignoradas | 0 rejeitadas
Latência (s): mín 14.81 | média 14.81 | máx 14.81
Fim da escuta. Mensagens recebidas no total: 7
Teste concluído.
```

Print: [`2026-10-28_01_terminal_notebook.png`](2026-10-28_01_terminal_notebook.png).

## Conferência no BigQuery (leitura, 28/10/2026)

| Tabela | Resultado | Print |
|---|---|---|
| `bronze_tc.eventos_alunos` | 5 linhas novas, todas com `origem = simulado` e latência maior que zero; o duplicado não entrou. Total da tabela: 10 linhas e 10 `id_evento` distintos (5 de 23/10 + 5 de 28/10) | [`2026-10-28_02_bronze_eventos.png`](2026-10-28_02_bronze_eventos.png) |
| `ops_tc.eventos_rejeitados` | 1 linha nova: `dabc107b…`, motivo `campos ausentes: ['id_municipio']`, com a mensagem original em `mensagem_bruta` | [`2026-10-28_03_rejeitados.png`](2026-10-28_03_rejeitados.png) |
| Load jobs (`INFORMATION_SCHEMA.JOBS_BY_PROJECT`) | 5 jobs entre 21:17:09 e 21:17:29, todos concluídos sem erro: 4 em `eventos_alunos` e 1 em `eventos_rejeitados`, com os mesmos IDs da saída acima | — |

Latência por evento (s): 0,97; 3,59; 1,55; 14,81; 2,81 (mediana 2,81; média 4,75). O evento de 14,81 s esperou a gravação do lote anterior terminar (consumer sequencial, um load job por lote).

Métricas do Pub/Sub no console (Cloud Monitoring): publicação no tópico e consumo pela assinatura às 21:17–21:19, sem mensagens pendentes de confirmação depois. Prints: [`2026-10-28_04_metricas_assinatura.png`](2026-10-28_04_metricas_assinatura.png) e [`2026-10-28_05_metricas_topico.png`](2026-10-28_05_metricas_topico.png).

## Depois da Bronze: Silver e Gold (28/10/2026, 21:42–21:44)

- `silver_tc.alunos_eventos`: 10 linhas, 10 `id_evento` distintos; regras E01 a E07 aprovadas (execução `silver_20261029_004245_73669e`).
- `gold_tc.indicador_por_origem`: 10.896 linhas `oficial` e 1 linha `simulado` (município 3550308, 2026: taxa 34,86 sobre 10 eventos avaliados); regras G03 a G07 aprovadas (execução `gold_20261029_004410_1ce122`).
