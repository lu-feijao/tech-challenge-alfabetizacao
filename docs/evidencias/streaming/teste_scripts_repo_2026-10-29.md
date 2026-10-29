# Evidência do streaming: scripts do repositório, a partir de um clone limpo (29/10/2026)

Terceira rodada do streaming e a primeira com os scripts de [`streaming/`](../../../streaming/) (e não com o notebook). Feita num clone novo do repositório, com ambiente virtual novo e `requirements.txt` instalado do zero, seguindo o passo 7 da seção 4 do README: consumer num terminal, producer em outro. Horários em UTC (Brasília = UTC−3).

## Terminal 1: `python streaming/consumer.py`

```
Escutando projects/project-ce782257-1c9c-4b6f-87a/subscriptions/topico-alfabetizacao-sub (para após 45s sem mensagens ou em 300s)...
1 linhas gravadas em project-ce782257-1c9c-4b6f-87a.bronze_tc.eventos_alunos (job a4a090d4-6f81-4f8a-aead-238314c37e3c)
Lote: 1 recebidas | 1 válidas | 0 duplicadas ignoradas | 0 rejeitadas
Latência (s): mín 1.54 | média 1.54 | máx 1.54
1 linhas gravadas em project-ce782257-1c9c-4b6f-87a.bronze_tc.eventos_alunos (job 997cbca2-5937-4678-b560-e0d9e9cabf77)
Lote: 1 recebidas | 1 válidas | 0 duplicadas ignoradas | 0 rejeitadas
Latência (s): mín 4.23 | média 4.23 | máx 4.23
3 linhas gravadas em project-ce782257-1c9c-4b6f-87a.bronze_tc.eventos_alunos (job 976494dd-74ad-418b-990c-25646abb433a)
1 linhas gravadas em project-ce782257-1c9c-4b6f-87a.ops_tc.eventos_rejeitados (job 4036335a-bc46-47cc-b5f1-273e806a8684)
Lote: 5 recebidas | 3 válidas | 1 duplicadas ignoradas | 1 rejeitadas
Latência (s): mín 2.67 | média 4.78 | máx 6.90
Fim da escuta. Mensagens recebidas no total: 7
```

## Terminal 2: `python streaming/producer.py`

```
Publicando em: projects/project-ce782257-1c9c-4b6f-87a/topics/topico-alfabetizacao
[1/5] válido enviado | id_evento=b363dd8f-2a14-44a4-81f6-955d7068fff7
[2/5] válido enviado | id_evento=86a62f12-3224-4ee9-8c9d-d6a9a787f037
[3/5] válido enviado | id_evento=3a772db1-ae32-4f9b-a80c-feb38bf1ad7c
[4/5] válido enviado | id_evento=5ab6661b-568e-4125-928c-ff1fbaabc586
[5/5] válido enviado | id_evento=72e8ee53-5134-4da4-b484-fa322474acf5
duplicado enviado | id_evento=72e8ee53-5134-4da4-b484-fa322474acf5
inválido enviado (sem id_municipio) | id_evento=2ca13426-375b-4ab3-b4ab-4205d84b64c0
```

## Conferência no BigQuery (leitura, 29/10/2026)

| Tabela | Resultado |
|---|---|
| `bronze_tc.eventos_alunos` | 5 linhas novas (recebidas entre 20:59:55 e 21:00:05), todas com `origem = simulado`; o duplicado `72e8ee53…` aparece **uma vez**. Total da tabela: 15 linhas e 15 `id_evento` distintos (3 rodadas) |
| `ops_tc.eventos_rejeitados` | 1 linha nova: `2ca13426…`, motivo `campos ausentes: ['id_municipio']`. Total: 3 (uma por rodada) |
| Load jobs | os 4 jobs da saída do consumer, todos concluídos: 3 em `eventos_alunos` e 1 em `eventos_rejeitados` |

Latência por evento (s): 1,54; 4,23; 6,90; 4,78; 2,67 (mediana 4,23; média 4,02), todas maiores que zero.

## Até a Gold (mesmo clone, em seguida)

- Silver `silver_20261029_210013_3d9c32`: `silver_tc.alunos_eventos` com 15 linhas e 15 `id_evento` distintos; regras E01 a E07 aprovadas; 10 etapas em `ops_tc.pipeline_runs`.
- Gold `gold_20261029_210133_58139e`: `gold_tc.indicador_por_origem` com 10.896 linhas `oficial` e 1 `simulado` (município 3550308, 2026, taxa 49,82 sobre 15 eventos avaliados); regras G03 a G07 aprovadas; 8 etapas em `pipeline_runs`.
