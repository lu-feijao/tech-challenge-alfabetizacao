# Tech Challenge · Fase 2 — Pipeline híbrido para análise da alfabetização no Brasil


## 1. Contexto do problema

O Compromisso Nacional Criança Alfabetizada quer que todas as crianças estejam alfabetizadas até o fim do 2º ano do ensino fundamental. O INEP define que um aluno está alfabetizado a partir de **743 pontos** na escala do Saeb, e o indicador é o **percentual de alunos que atingem esse patamar**.

Este projeto constrói, em nuvem, um pipeline que integra as tabelas do Indicador Criança Alfabetizada e entrega uma camada analítica confiável, em arquitetura medalhão (Bronze, Silver e Gold), com uma parte em lote (batch) e outra com eventos simulados (streaming).

**Fonte de dados:** [Base dos Dados](https://basedosdados.org/), dataset `br_inep_avaliacao_alfabetizacao`, disponível no BigQuery.

## 2. Arquitetura

```
 Base dos Dados (BigQuery, público)
          │
          │  bronze/bronze_ingestao.py
          ▼
 ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
 │    BRONZE     │ ──► │    SILVER     │ ──► │     GOLD      │
 │   bronze_tc   │     │   silver_tc   │     │    gold_tc    │
 └───────────────┘     └───────────────┘     └───────────────┘
   implementado         implementado          implementado
                     silver_transformacao.py  gold_transformacao.py
                            │                        ▲
                            ▼                        │ portão: só roda se a
                   regras de qualidade ──► ops_tc.dq_results   última Silver foi aprovada

 Streaming (Pub/Sub) .......... implementado (seção 3.5): producer → tópico → consumer
        └─► bronze_tc.eventos_alunos ─► silver_tc.alunos_eventos ─► gold_tc.indicador_por_origem
            (rejeitados: ops_tc.eventos_rejeitados)                 (coluna origem: oficial | simulado)
 Qualidade (ops_tc.dq_results)  implementado (seção 3.4)
 Alerta de falha .............. implementado e testado (seção 7): log tc-pipeline (ERROR) → Cloud Monitoring → e-mail
 Métricas de execução ......... implementado (seção 7): Silver e Gold gravam cada etapa em ops_tc.pipeline_runs (ops/run_logger.py)
 Orçamento .................... implementado (seção 7): Cloud Billing, R$ 50/mês, alertas por e-mail
```

Todas as camadas são datasets dentro do mesmo projeto do Google Cloud, e cada camada lê a anterior. Diagrama detalhado, com cada tabela: [`docs/arquitetura.md`](docs/arquitetura.md) ([imagem](docs/arquitetura.png)).

## 3. Estrutura do repositório

| Pasta | Conteúdo |
|---|---|
| `bronze/` | Ingestão batch: dado bruto, só acrescenta (`bronze_ingestao.py` e o notebook equivalente `bronze_ingestao.ipynb`) |
| `silver/` | Limpeza, padronização e integração das tabelas (`silver_transformacao.py` e os SQL em `silver/sql/`) |
| `gold/` | Indicadores prontos para análise (`gold_transformacao.py` e os SQL em `gold/sql/`) e a cópia da Gold em Parquet para a Fase 3 (`exportar_gold.py` e `gold/export/`) |
| `quality/` | Regras de qualidade de dados (`regras.py`) e funções de execução e registro em `ops.dq_results` (`dq.py`) |
| `streaming/` | Streaming: simulador (`producer.py`), consumidor em micro-lotes (`consumer.py`) e a validação dos eventos (`validacao.py`) |
| `tests/` | Testes unitários da triagem de eventos e do registro de métricas (`python -m unittest discover -s tests -t .`) |
| `ops/` | Observabilidade e custo: registro de métricas de execução (`run_logger.py`), DDL de `pipeline_runs` e view de custo por etapa (`sql/`), consulta de consumo real (`sql/finops/`), medição de linhas e bytes das tabelas por dry run (`medir_tabelas.py`) e a política de alerta exportada (`alerta_falha.json`) |
| `docs/` | Documentação técnica, organizada por tema (detalhe abaixo) |

Dentro de `docs/`:

| Pasta ou arquivo | Conteúdo |
|---|---|
| `arquitetura.md` e `.png` | diagrama do que foi implementado, com cada tabela |
| `numeros.md` | todo número citado no README e no vídeo, com a fonte de cada um |
| `dados/` | perfil das tabelas da Bronze, mapa de joins e catálogo de dados com o DDL de cada tabela (`catalogo/`) |
| `qualidade/` | catálogo das regras de qualidade (limiares e justificativas) e revisão contra as armadilhas do enunciado |
| `finops/` | tabela de custo (medido e projetado) e medições de tamanho das tabelas |
| `evidencias/` | evidências de execução: Bronze, resultados de qualidade (`dq_*.csv`), falha demonstrada, streaming, alerta de falha (`alerta/`) e orçamento (`finops/`) |

Arquivos na raiz: `README.md`, `requirements.txt`, `.env.example` (modelo de configuração) e `.gitignore`.


## 3.1 Bronze — dado bruto

A Bronze guarda os dados **exatamente como vieram da fonte**: sem filtro, sem limpeza e sem mudança de nomes ou tipos de colunas. Ela é o histórico do pipeline: se uma etapa seguinte der errado, reprocessa-se a partir dela sem precisar buscar a fonte de novo.

### O que entra na Bronze

Origem: `basedosdados.br_inep_avaliacao_alfabetizacao` (BigQuery público da Base dos Dados).
Destino: `<projeto>.bronze_tc.<tabela>`, com o mesmo nome da tabela de origem.

| Tabela | Conteúdo |
|---|---|
| `alunos` | Microdado individual: proficiência, presença, preenchimento do caderno, alfabetizado, peso amostral |
| `municipio` | Indicador por município, ano, série e rede |
| `uf` | Indicador por UF, ano, série e rede |
| `meta_alfabetizacao_brasil` | Trajetória nacional de metas (2024–2030) |
| `meta_alfabetizacao_uf` | Trajetória estadual de metas |
| `meta_alfabetizacao_municipio` | Trajetória municipal de metas |
| `dicionario` | Tradução oficial dos códigos (rede, série, presença etc.) |

### Colunas de controle

| Coluna | Tipo | Descrição |
|---|---|---|
| `_ingestion_timestamp` | TIMESTAMP | Data e hora (UTC) da execução. É igual para todas as tabelas da mesma execução |
| `_source` | STRING | Tabela de origem completa (por exemplo, `basedosdados.br_inep_avaliacao_alfabetizacao.municipio`) |

O `_ingestion_timestamp` faz o papel de identificador da execução: ele é gravado uma vez por execução, igual em todas as tabelas, então separa uma carga da outra sem uma coluna `execucao_id` própria. A coluna `_source` registra a tabela oficial de origem; a distinção entre dado oficial e simulado fica na coluna `origem` das tabelas de eventos (seção 3.5), já que a Bronze batch só recebe dado oficial.

### Política de escrita

- **Só acrescenta.** Cada execução usa `WRITE_APPEND`.
- **Quando a fonte oficial for atualizada:** uma nova execução acrescenta uma nova cópia completa, com um novo `_ingestion_timestamp`. As cópias anteriores continuam na tabela.
- **Linhas repetidas entre execuções são esperadas.** Rodar duas vezes sem que a fonte mude dobra a contagem de linhas. A Bronze não remove duplicatas.
- **Consequência para a Silver:** ela trabalha só com a ingestão mais recente de cada tabela (maior `_ingestion_timestamp`), conforme a seção 3.2.


### O que o script faz, por tabela

1. Lê o tamanho da origem. Se passar do `LIMITE_GB`, pula a tabela e avisa.
2. Baixa a tabela inteira, sem filtro e sem transformação.
3. Mostra `shape` e `info()`.
4. Acrescenta `_ingestion_timestamp` e `_source`.
5. Carrega na Bronze com `WRITE_APPEND`, com os mesmos tipos da origem.
6. Confere a contagem: linhas da origem = linhas baixadas = linhas acrescentadas. Se divergir, o script termina com erro.

### Evidências de execução

Cada execução do script grava um CSV em [`docs/evidencias/`](docs/evidencias/) com a contagem de linhas antes e depois, o ID do job do BigQuery e a duração de cada tabela. O notebook gera o mesmo resultado no arquivo `evidencias_bronze.csv` (dentro da sessão do Colab, e deve ser baixado e guardado em `docs/evidencias/`).


### Limitações

- A ingestão passa pela memória de quem roda o script. Tabelas acima de `LIMITE_GB` são puladas.
- A Bronze não é particionada.


## 3.2 Silver — dado limpo, padronizado e integrado

A Silver lê **só a ingestão mais recente** de cada tabela da Bronze (maior `_ingestion_timestamp`), padroniza e integra as bases. As tabelas são recriadas a cada execução (`CREATE OR REPLACE`), o que é seguro porque o histórico fica na Bronze.

Execução: `python silver/silver_transformacao.py` roda, em ordem, os arquivos de [`silver/sql/`](silver/sql/) e depois as regras de qualidade (seção 3.4).

### Tabelas

| Tabela | Linhas | Grão (chave única) | O que muda em relação à Bronze |
|---|---|---|---|
| `municipio` | 23.995 | ano + id_municipio + serie + rede | Códigos de rede e série traduzidos; UF derivada do código IBGE |
| `uf` | 145 | ano + sigla_uf + serie + rede | Códigos traduzidos; código IBGE da UF |
| `alunos` | 3.867.999 | ano + id_aluno + caderno | Todos os códigos traduzidos; coluna `avaliado`; particionada por ano e clusterizada por UF e município |
| `meta_municipio` | 37.464 | id_municipio + rede + ano_meta | Metas em formato longo (uma linha por ano de meta, 2024 a 2030); rede texto → código |
| `meta_uf` | 567 | ano_referencia + sigla_uf + rede + ano_meta | Formato longo, guardando o ano de referência de cada linha da fonte |
| `meta_brasil` | 21 | ano_referencia + rede + ano_meta | Formato longo, como `meta_uf` |
| `alunos_eventos` | 10 (testes de 23/10 e 28/10) | id_evento | Eventos de streaming deduplicados por `id_evento`, com `origem` e latência (etapa opcional: só roda se `bronze_tc.eventos_alunos` existir) |
| `de_para_uf` | 27 | cod_uf | Código IBGE da UF → sigla |
| `de_para_rede_meta` | 2 | rede_texto | `Municipal` → `3`; `Pública` → `5` |

### Decisões de tratamento

- **Tipos preservados.** O que é INT64 na fonte continua INT64 e o que é STRING continua STRING (identificadores e códigos como `rede`, `serie` e `caderno` ficam texto). Comparações com códigos usam aspas (`rede = '3'`).
- **Nulo continua nulo.** Nenhuma medida recebe valor padrão. Exemplos: as proporções por nível de 2023 (nulas na fonte), a proficiência e o peso de quem não foi avaliado e as metas nulas.
- **Códigos traduzidos pelo dicionário oficial.** Código sem tradução vira `desconhecido`, e uma regra bloqueante exige que essa contagem seja zero.
- **`avaliado`** = o aluno tem peso amostral (presente e com caderno preenchido). Na fonte, `alfabetizado = 0` também aparece para quem não fez a prova; `avaliado` separa "não avaliado" de "não alfabetizado" e define o denominador correto da taxa.
- **Rede das metas.** As tabelas de meta trazem a rede como texto (`Municipal`, `Pública`) e as de resultado como código. `Pública` foi mapeada para `5` (Pública Estadual e Municipal), porque o código `6` não aparece nas tabelas de resultado.
- **Série das metas.** As metas não têm série e foram tratadas como 2º ano, que é o recorte de todos os resultados e do compromisso nacional.
- **Metas em formato longo.** As 7 colunas de meta viram linhas. Na meta municipal as metas são idênticas nas linhas de 2023 e 2024 e são deduplicadas; nas metas de UF e Brasil a linha de 2025 traz valores arredondados, por isso cada linha guarda o seu ano de referência.
- **UF dos municípios** derivada dos 2 primeiros dígitos do código IBGE.

Detalhes: [ficha de perfil da Bronze](docs/dados/ficha_perfil_bronze.md) e [mapa de joins](docs/dados/mapa_joins.md).

### Custo medido

Medido por dry run (o BigQuery informa os bytes que a consulta leria, sem executá-la):

| Etapa | Leitura | Medição |
|---|---:|---|
| SQL da Silver (`silver/sql/`) | 1,02 GB | dry run de 28/10/2026; 1,009 GB só em `silver_tc.alunos`, as outras tabelas leem menos de 10 MB cada |
| Regras de qualidade da Silver | ≈ 1,0 GB | dry run de 21/10/2026 |
| SQL da Gold (`gold/sql/`) | 0,14 GB | dry run de 28/10/2026; 0,137 GB na validação cruzada, que lê `alunos` |
| Regras de qualidade da Gold | ≈ 0,13 GB | dry run de 21/10/2026 |
| **Execução completa (Silver + Gold + regras)** | **≈ 2,3 GB** | soma das linhas acima |

A leitura da Silver é proporcional ao tamanho da Bronze inteira: a Bronze não é particionada, então filtrar a ingestão mais recente não reduz os bytes lidos. Com 2 cargas na Bronze, `silver_tc.alunos` lê 1,009 GB, o tamanho de `bronze_tc.alunos`.


## 3.3 Gold — indicadores prontos para análise

Execução: `python gold/gold_transformacao.py`. Antes de criar qualquer tabela, o script consulta `ops.dq_results` e **só segue se a execução mais recente da Silver tiver todas as regras bloqueantes aprovadas**. Os arquivos ficam em [`gold/sql/`](gold/sql/).

| Tabela | Conteúdo | Recorte |
|---|---|---|
| `municipio_meta` | Taxa do município x meta pactuada do mesmo ano, distância à meta, status e motivo | Rede Municipal (`3`), 2º ano |
| `uf_meta` | Taxa da UF x meta do mesmo ano | Rede Pública (`5`), 2º ano |
| `brasil_meta` | Indicador nacional oficial x meta do mesmo ano | Rede Pública (`5`), 2º ano |
| `evolucao_municipio` | Taxa 2023, taxa 2024, variação e tendência por município e rede | Todas as redes publicadas |
| `indicador_por_origem` | Taxa por município com a coluna `origem` (`oficial` = publicada pelo INEP; `simulado` = recalculada dos eventos de streaming) | Rede Municipal (`3`), 2º ano (etapa opcional: só roda se `silver_tc.alunos_eventos` existir) |
| `validacao_cruzada` | Taxa recalculada a partir de `alunos` x taxa oficial, por município, UF e Brasil | Redes publicadas; redes agregadas reconstruídas a partir das redes dos alunos |

**Regras da Gold:**
- Resultado só é comparado com meta do **mesmo recorte de rede e série**.
- Meta usada: a **meta pactuada da fonte** (meta 2030 = 80). A leitura de universalização (100%) não é usada.
- **3 estados**: `atingiu`, `nao_atingiu` e `sem_meta`. Ausência de meta nunca vira "não atingiu"; a coluna `motivo_sem_meta` diz por quê (metas começam em 2024, sem meta pactuada ou meta nula na fonte).
- A variação no tempo só é calculada quando o município tem os dois anos. Nenhuma projeção até 2030 é feita.

**Resultados (execução de 21/10/2026):**

| Recorte | 2024 |
|---|---|
| Brasil, rede pública | 59,2 contra a meta de 59,9: não atingiu |
| UFs, rede pública | 11 atingiram, 13 não atingiram, 1 sem meta |
| Municípios, rede municipal | 2.788 atingiram, 2.444 não atingiram, 216 sem meta (96 sem meta pactuada e 120 com meta nula na fonte) |
| Evolução 2023 → 2024, rede municipal | 3.134 municípios subiram, 2.250 caíram, 12 estáveis, 104 sem os dois anos |

Em 2023 todos os recortes ficam em `sem_meta`, porque as metas começam em 2024. Em 2025, só existe resultado nacional: 66,0 contra a meta de 64,0.

### Validação cruzada

A taxa foi recalculada a partir dos 3,87 milhões de registros de alunos: soma do peso amostral dos avaliados alfabetizados dividida pela soma do peso de todos os avaliados.

| Cálculo (Brasil 2024, rede pública) | Taxa | Diferença da oficial |
|---|---|---|
| Oficial publicada | 59,2 | — |
| Recalculada (peso amostral, só avaliados) | **59,20** | **0,00** |
| Sem o peso amostral | 59,78 | +0,58 |
| Dividindo por todos os registros (inclui ausentes) | 52,21 | −6,99 |

Em 2024, 99,5% dos municípios (rede municipal) ficam a até 0,5 p.p. da taxa oficial, e as UFs ficam a no máximo 0,09 p.p. (redes municipal e pública).

**Anomalia documentada:** para o Brasil em 2023, o recálculo dá 57,46 e a tabela de meta publica 55,9. Como UFs e municípios de 2023 batem com o microdado (diferença média de 0,03 a 0,05 p.p.), a divergência está no número nacional de 2023 da tabela de meta, e não no pipeline. A causa não foi confirmada.

**Para a Fase 3:** `status_meta` e `distancia_meta` são derivadas de `taxa_alfabetizacao`. Se a taxa for o alvo de um modelo, essas colunas não podem entrar como features (vazamento de alvo).

### Cópia da Gold para a Fase 3

As tabelas do BigQuery podem expirar: os datasets foram criados no sandbox, com expiração padrão de 60 dias, que continua valendo depois da ativação do faturamento até ser removida. Por isso a Gold fica guardada também em [`gold/export/`](gold/export/): um arquivo Parquet por tabela e um `manifesto.csv` com as linhas no BigQuery, as linhas exportadas, a última modificação da tabela e o horário da cópia.

Para gerar de novo, depois da Gold: `python gold/exportar_gold.py`. O script lê as tabelas pela API de leitura (sem consulta SQL, então sem bytes cobrados) e termina com código 1 se alguma contagem divergir. Cópia atual: das tabelas publicadas em 28/10/2026 (execução `gold_20261029_004410_1ce122`; 6 tabelas, 58.638 linhas, cerca de 1 MB).


## 3.4 Qualidade de dados

As regras ficam em [`quality/regras.py`](quality/regras.py) e o catálogo completo, com limiares e justificativas, em [`docs/qualidade/regras_qualidade.md`](docs/qualidade/regras_qualidade.md).

- **Bloqueantes** (41 na Silver, 7 delas dos eventos de streaming, e 10 na Gold, 4 delas da tabela com `origem`): carga completa da Bronze, chave única, nulo em chave, código sem tradução, faixas válidas, alinhamento de proficiência e peso, coerência dos status e **taxa de match de cada join** (municipio × meta municipal e uf × meta estadual, limiar de 95% justificado no catálogo). Se alguma reprova, o script termina com código 1 e a Gold não é publicada.
- **Informativas** (6 na Silver e 4 na Gold): registram e seguem. Três reprovam de propósito com o dado atual: taxas de 2023 divergentes entre duas tabelas da fonte (R09), 18 cadernos fora da faixa (R10) e 25 UFs em vez de 27 (R11).
- **Registro persistente:** cada regra vira uma linha em `ops.dq_results` (execução, horário, tabela, regra, severidade, valor medido, limiar e status), gravada por **load job em modo append**. O histórico acumula entre execuções. Uma cópia de cada execução fica em `docs/evidencias/dq_<execucao>.csv`.
- **Sem `except` genérico:** só a exceção específica de regra bloqueante é tratada, e o processo termina com erro.

**Falha demonstrada:** `python silver/silver_transformacao.py --simular-falha` eleva o limiar de match da R04 para 99,9%. Na execução `silver_20261021_160213_34ac17` a R04 reprovou (97,32%), o resultado ficou gravado em `ops.dq_results`, o script terminou com código 1 e a Gold se recusou a rodar. Logs em [`docs/evidencias/falha_demonstrada/`](docs/evidencias/falha_demonstrada/).

Revisão contra as armadilhas do enunciado: [`docs/qualidade/checklist_armadilhas.md`](docs/qualidade/checklist_armadilhas.md).


## 3.5 Streaming — eventos em tempo quase real

Simula a chegada de novas medições de alunos e leva cada evento até a camada analítica, sempre com a coluna `origem`.

```
producer ──► Pub/Sub (topico-alfabetizacao) ──► consumer (micro-lotes de até 10 mensagens)
                                                   ├─ válido    ─► bronze_tc.eventos_alunos (load job, append)
                                                   ├─ rejeitado ─► ops_tc.eventos_rejeitados (motivo + mensagem original)
                                                   └─ duplicado ─► ignorado (só é confirmado)
bronze_tc.eventos_alunos ─► silver_tc.alunos_eventos (dedup por id_evento) ─► gold_tc.indicador_por_origem
```

- **Producer** (`streaming/producer.py`): cada evento tem `id_evento` único, `horario_producao` (UTC, com fuso) e `origem = 'simulado'`, no formato e nos tipos de `silver_tc.alunos`. A proficiência é sorteada na faixa real (580 a 900) e `alfabetizado` é derivada do corte de 743. Envia também, de propósito, 1 evento duplicado (mesmo `id_evento`) e 1 inválido (sem `id_municipio`).
- **Consumer** (`streaming/consumer.py`): lê em micro-lotes, classifica cada mensagem (`streaming/validacao.py`), grava por load job e **só depois confirma (ack)**. Se a gravação falhar, as mensagens não são confirmadas e o Pub/Sub as entrega de novo. A assinatura confirma em 10 s por padrão; o consumer pede 60 s antes de gravar, para uma gravação lenta não causar reentrega.
- **Rejeitados:** tabela de 4 colunas fixas (`id_evento`, `horario_recebimento`, `motivo_rejeicao`, `mensagem_bruta`). A mensagem original fica inteira, então até um JSON quebrado cabe na tabela.
- **Silver** (`silver/sql/08_alunos_eventos.sql`): fica a linha recebida primeiro de cada `id_evento`. Regras E01 a E08 (seção 3.4): chave única, sem nulos, `origem` sempre `simulado`, **latência maior que zero**, `alfabetizado` coerente com 743, faixas e match do município.
- **Gold** (`gold/sql/06_indicador_por_origem.sql`): uma tabela com a taxa por município e a coluna `origem`. O número do simulador **não é indicador oficial**: as duas origens só dividem a tabela porque `origem` as separa, e nenhuma consulta deve somá-las ou compará-las sem filtrar. Os eventos usam o ano 2026, que não existe no indicador oficial (regra G07).

### Batch × streaming (números medidos em 23/10 e 28/10/2026)

| | Batch (Bronze) | Streaming (eventos) |
|---|---|---|
| Latência | intervalo entre a atualização da fonte e a próxima execução manual do script (horas ou dias; não é medida como latência) | **0,91 a 17,11 s** por evento, medida como recebimento menos produção. 23/10: mediana 14,45 s, média 12,10 s; 28/10: 0,97 a 14,81 s, mediana 2,81 s, média 4,75 s |
| Frequência | carga completa sob demanda (2 rodadas até agora) | micro-lotes de até 10 mensagens, um load job por lote |
| Garantia | contagem conferida (origem = baixada = acrescentada) e Silver usa só a última ingestão | entrega **pelo menos uma vez**; dedup por `id_evento` no consumer e na Silver; ack só depois de gravar |
| Dado ruim | regra bloqueante interrompe a Silver e a Gold | evento inválido vai para rejeitados, sem derrubar o consumer |

A latência de até 17 s não vem do Pub/Sub: o consumer é sequencial e cada lote espera um load job do BigQuery (alguns segundos). Em 28/10 os lotes foram menores e mais frequentes, e a mediana caiu de 14,45 s para 2,81 s; o único evento lento (14,81 s) esperou a gravação do lote anterior. A inserção por streaming do BigQuery daria menos de 1 s, mas não foi usada: o teste rodou quando o projeto ainda estava no sandbox, que a bloqueia. O faturamento foi ativado em 28/10/2026 e ela passou a ser possível, mas o consumer segue com load job, que é gratuito. Os eventos seguintes esperam o consumer terminar a gravação anterior.

Evidências, jobs, contagens e prints: [`docs/evidencias/streaming/`](docs/evidencias/streaming/), com uma página por rodada ([23/10](docs/evidencias/streaming/teste_colab_2026-10-23.md) e [28/10](docs/evidencias/streaming/teste_notebook_2026-10-28.md)).

### Limitações do streaming

- O dado é **simulado** (2 rodadas de 7 mensagens, 1 município) e serve para demonstrar o fluxo, não para análise.
- As duas rodadas foram executadas com o notebook [`teste_streaming_unico.ipynb`](docs/evidencias/streaming/teste_streaming_unico.ipynb), guardado junto das evidências. Os scripts de `streaming/` têm a mesma lógica, testada por testes unitários (`tests/`), mas ainda não foram executados contra o Pub/Sub.
- A deduplicação em memória do consumer zera quando ele reinicia; a Silver deduplica de novo por `id_evento`.
- A etapa é opcional: sem `bronze_tc.eventos_alunos`, a Silver e a Gold pulam os eventos e o restante do pipeline roda normalmente.


## 4. Como reproduzir

### Pré-requisitos

- Python 3.10 ou superior e o [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) (`gcloud` e `bq`).
- Um projeto no Google Cloud com o BigQuery ativo. O batch (Bronze, Silver, Gold e qualidade) roda inclusive no sandbox do BigQuery, porque grava só por load job e `CREATE TABLE`. O streaming usa o Pub/Sub, que exige faturamento ativo no projeto.
- Permissão no projeto para criar datasets e tabelas e rodar jobs no BigQuery (e, para o streaming, publicar e assinar no Pub/Sub). Para que uma falha dispare o alerta por e-mail, quem executa também precisa do papel Gravador de registros (`roles/logging.logWriter`); sem ele, o pipeline roda normalmente e a falha fica registrada só em `pipeline_runs` e no terminal.
- Custo de referência: cerca de 2,3 GB lidos por execução completa de Silver e Gold (seção 3.2). A ingestão da Bronze não usa consulta SQL.

### Preparar um projeto novo (só na primeira vez)

Quem usa o projeto do grupo pode pular esta parte: os datasets e o tópico já existem. Para rodar em outro projeto, troque `SEU_PROJETO` pelo ID do projeto e crie os 4 datasets na mesma região:

```bash
bq --location=southamerica-east1 mk --dataset SEU_PROJETO:bronze_tc
bq --location=southamerica-east1 mk --dataset SEU_PROJETO:silver_tc
bq --location=southamerica-east1 mk --dataset SEU_PROJETO:gold_tc
bq --location=southamerica-east1 mk --dataset SEU_PROJETO:ops_tc
```

Para o streaming (opcional), ative a API e crie o tópico e a assinatura com os nomes do `.env.example`:

```bash
gcloud services enable pubsub.googleapis.com --project=SEU_PROJETO
gcloud pubsub topics create topico-alfabetizacao --project=SEU_PROJETO
gcloud pubsub subscriptions create topico-alfabetizacao-sub --topic=topico-alfabetizacao --project=SEU_PROJETO
```

As tabelas são criadas pelos próprios scripts, inclusive `ops.dq_results` e `ops.pipeline_runs`.

Para o alerta de falha por e-mail (opcional), crie um canal de e-mail no Cloud Monitoring, troque em [`ops/alerta_falha.json`](ops/alerta_falha.json) o ID do projeto e o `SUBSTITUIR_PELO_ID_DO_CANAL` pelo ID do canal, e crie a política. Para a view de custo por etapa, troque `{projeto}` e `{ops}` em [`ops/sql/vw_custo_por_etapa.sql`](ops/sql/vw_custo_por_etapa.sql) e rode o arquivo:

```bash
gcloud alpha monitoring policies create --policy-from-file=ops/alerta_falha.json --project=SEU_PROJETO
bq query --use_legacy_sql=false < ops/sql/vw_custo_por_etapa.sql
```

### Passo a passo (computador local)

1. Clone o repositório e entre na pasta:
   ```bash
   git clone https://github.com/lu-feijao/tech-challenge-alfabetizacao.git
   cd tech-challenge-alfabetizacao
   ```
2. Crie o ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # no Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Crie o arquivo de configuração a partir do modelo:
   ```bash
   cp .env.example .env             # no Windows: copy .env.example .env
   ```
   O modelo já vem com os IDs do projeto do grupo. Para rodar em outro projeto, edite o `.env` e troque o `GCP_PROJECT_ID` (e os datasets, se tiverem outros nomes).
4. Faça o login no Google Cloud (nenhuma chave fica no repositório):
   ```bash
   gcloud auth application-default login
   ```
5. Rode a ingestão da Bronze:
   ```bash
   python bronze/bronze_ingestao.py
   ```
6. Rode a Silver e depois a Gold (cada uma termina com código 1 se uma regra bloqueante reprovar):
   ```bash
   python silver/silver_transformacao.py
   python gold/gold_transformacao.py
   ```
   Para demonstrar a falha: `python silver/silver_transformacao.py --simular-falha`. Depois, rode a Silver normal de novo para liberar a Gold.

   Para guardar a Gold em Parquet (`gold/export/`): `python gold/exportar_gold.py`.
7. (Opcional) Streaming: em um terminal, deixe o consumer escutando e, em outro, rode o producer. Depois, rode de novo a Silver e a Gold para levar os eventos até `gold_tc.indicador_por_origem`:
   ```bash
   python streaming/consumer.py      # terminal 1: fica escutando
   python streaming/producer.py      # terminal 2: 5 válidos, 1 duplicado, 1 inválido
   ```
   O login do Google precisa ter permissão de publicar e assinar no Pub/Sub e de gravar em `bronze_tc` e `ops_tc`.
8. Testes unitários da triagem de eventos e do registro de métricas (sem GCP):
   ```bash
   python -m unittest discover -s tests -t .
   ```

### Passo a passo (Google Colab)

1. Em um notebook novo, clone o repositório e instale as dependências:
   ```python
   !git clone https://github.com/lu-feijao/tech-challenge-alfabetizacao.git
   %cd tech-challenge-alfabetizacao
   !pip install -q -r requirements.txt
   ```
2. Faça o login e crie o `.env` (o modelo já vem com os IDs do projeto do grupo; para outro projeto, edite o `GCP_PROJECT_ID` no `.env`):
   ```python
   from google.colab import auth
   auth.authenticate_user()
   !cp .env.example .env
   ```
3. Rode:
   ```python
   !python bronze/bronze_ingestao.py
   !python silver/silver_transformacao.py
   !python gold/gold_transformacao.py
   ```

## 5. Tecnologias utilizadas

| Tecnologia | Uso no projeto | Por quê |
|---|---|---|
| Google Cloud · BigQuery | Bronze, Silver, Gold e `ops` (4 datasets em `southamerica-east1`) | as tabelas oficiais já estão no BigQuery da Base dos Dados; SQL, armazenamento e processamento no mesmo serviço |
| Google Cloud · Pub/Sub | mensageria do streaming (`topico-alfabetizacao`) | serviço gerenciado de mensagens do GCP, com entrega "pelo menos uma vez" |
| Cloud Monitoring e Cloud Billing | alerta de falha e orçamento com alerta por e-mail (seção 7) | ferramentas nativas do mesmo projeto |
| Python 3 | scripts de ingestão, Silver, Gold, qualidade, exportação e streaming | bibliotecas oficiais do Google (`google-cloud-bigquery`, `google-cloud-pubsub`) |
| SQL (BigQuery) | transformações da Silver e da Gold, um arquivo por tabela | versionável e legível; o processamento roda no BigQuery, não na máquina de quem executa |
| pandas e pyarrow | carga da Bronze, gravação de `dq_results` e cópia da Gold em Parquet | |
| `unittest` | testes da triagem de eventos e do registro de métricas (`tests/`) | biblioteca padrão, sem dependência extra |

Versões fixadas em `requirements.txt`.

**Implementado x evolução futura.** Está implementado e executado na nuvem tudo o que as seções 3.1 a 3.5 descrevem. Ficam para uma próxima etapa, **não implementados**: orquestração com agendamento e retentativa (hoje cada etapa é um comando executado em sequência), infraestrutura como código (datasets e tópico criados pelos comandos da seção 4), particionamento da Bronze por data de ingestão e gravação do streaming pela Storage Write API.

## 6. Decisões e trade-offs

- **Nuvem única: Google Cloud.** Os dados oficiais já estão no BigQuery, então não há transferência entre nuvens nem duas contas de faturamento ou dois modelos de acesso para governar.
- **Data warehouse (BigQuery) em vez de data lake com arquivos.** Todas as camadas são tabelas do BigQuery: as transformações são SQL, os tipos ficam garantidos pelo esquema e não é preciso administrar arquivos e catálogo. O custo é ficar preso ao modelo de cobrança por bytes lidos (seção 3.2). A única saída em arquivo é a cópia da Gold em Parquet (`gold/export/`), guardada para a Fase 3.
- **Batch para os dados oficiais, streaming para eventos.** A fonte oficial muda uma vez por ano: uma carga completa sob demanda é suficiente e simples de conferir (contagem origem = baixada = acrescentada). O streaming existe para eventos que chegam aos poucos; a comparação de latência, frequência e garantias está na seção 3.5.
- **Forma de acesso à fonte: leitura direta do BigQuery público, sem baixar arquivos manualmente.** O script lê cada tabela pela API de leitura de tabelas (`list_rows`), sem consulta SQL, então a leitura da fonte não gera bytes de consulta cobrados. Os dados passam pela memória de quem roda o script (uma carga completa tem cerca de 0,5 GB, quase todo em `alunos`) e são gravados por load job, que é gratuito. Quando a Base dos Dados atualizar, uma nova execução acrescenta uma nova cópia completa e a Silver passa a usar a mais recente (seção 3.1).
- **Custo x desempenho.**
  - `silver_tc.alunos` é particionada por ano e clusterizada por UF e município: consultas que filtram ano ou município leem menos.
  - A Bronze **não** é particionada: a Silver lê a Bronze inteira a cada execução, e a leitura cresce a cada nova carga (seção 3.2). Aceitável com 2 cargas; com recargas frequentes, particionar por data de ingestão seria o primeiro ajuste.
  - Gravação por load job em vez de inserção por streaming do BigQuery: gratuita e disponível no sandbox, ao custo de alguns segundos de latência por micro-lote (seção 3.5).
  - Teto de 10 GiB faturados por consulta (`maximum_bytes_billed`, em `ops/run_logger.py`): uma consulta que passe do teto falha em vez de cobrar, e a falha dispara o alerta. A maior consulta do pipeline lê cerca de 1 GB.
- **Qualidade que bloqueia.** Regras bloqueantes interrompem a Silver e impedem a Gold (seção 3.4). Custa cerca de 1 GB lido por execução nas regras, e evita publicar indicador errado.

## 7. Monitoramento e FinOps

### 7.1 O que é monitorado

| O que o enunciado pede | Como está hoje | Onde ver |
|---|---|---|
| Resultado das validações, persistido | cada regra de cada execução vira uma linha em `ops_tc.dq_results`, que acumula: 248 resultados de 8 execuções (5 da Silver, 3 da Gold), entre eles a falha demonstrada | seção 3.4; `docs/evidencias/dq_*.csv` |
| Alerta de erro | política **"Pipeline TC - falha"** no Cloud Monitoring: qualquer entrada com severidade ERROR no log `tc-pipeline` abre um alerta e envia e-mail ao canal da frente 4. Avisa de novo a cada 5 min enquanto aberto e fecha sozinho em 30 min | [`docs/evidencias/alerta/`](docs/evidencias/alerta/) |
| Latência medida de fato | streaming: `latencia_segundos` = recebimento − produção, por evento (0,91 a 17,11 s); batch: duração de cada SQL impressa pelos scripts | seção 3.5; `bronze_tc.eventos_alunos` |
| Volume processado | linhas e bytes de cada tabela no catálogo; bytes processados por SQL na saída dos scripts | [`docs/dados/catalogo/catalogo_dados.md`](docs/dados/catalogo/catalogo_dados.md) |
| Métricas de execução persistidas (duração por etapa, linhas de entrada e saída, status) | a Silver e a Gold gravam uma linha por etapa (cada SQL, as regras, a gravação dos resultados e o portão) em `ops_tc.pipeline_runs`: início, fim, duração, linhas de entrada e saída, bytes processados e faturados, job IDs, status e erro. Gravação por load job, só acréscimo; a tabela é particionada por dia e não expira. Código em `ops/run_logger.py` | `ops_tc.pipeline_runs` |
| Custo por etapa | view `ops_tc.vw_custo_por_etapa`, que soma os bytes faturados dos jobs por label `pipeline`/`camada`/`etapa`. Os jobs da Silver e da Gold recebem esses labels em `ops/run_logger.py`; a definição da view está em `ops/sql/vw_custo_por_etapa.sql` | `ops_tc.vw_custo_por_etapa` |

**Teste com o pipeline real (29/10/2026):** `python silver/silver_transformacao.py --simular-falha` reprovou a R04, gravou a etapa `regras_bloqueantes` como falha em `pipeline_runs` às 17:35:40 (horário de Brasília), o alerta abriu às 17:35:55 (**15 s depois**) e o e-mail chegou às 17:35. Em seguida, a Silver normal e a Gold rodaram aprovadas: 10 e 8 etapas registradas, ≈ 62 s e ≈ 23 s, ≈ 2,53 GB faturados no total. Detalhes, etapa por etapa: [`docs/evidencias/alerta/teste_pipeline_2026-10-29.md`](docs/evidencias/alerta/teste_pipeline_2026-10-29.md).

**Primeiro teste do alerta (28/10/2026, horário de Brasília):** com um script de teste da frente 4, a falha simulada foi registrada às 20:20:29, o alerta abriu às 20:21:21 (52 s depois) e o e-mail chegou às 20:21, na execução `teste_20261028_232024_f5c54d`. Prints do alerta aberto e do e-mail em [`docs/evidencias/alerta/`](docs/evidencias/alerta/); registro das ações no GCP em [`docs/evidencias/alerta/registro_acoes_gcp.md`](docs/evidencias/alerta/registro_acoes_gcp.md).

### 7.2 Em produção, quem descobre que o pipeline quebrou, e em quanto tempo?

- **Falha registrada no log `tc-pipeline` com severidade ERROR:** o responsável pela frente 4 recebe o e-mail em **menos de 1 minuto** (medido: 15 s até o alerta abrir com uma falha real da Silver em 29/10; 52 s no teste de 28/10). O e-mail diz onde olhar (`pipeline_runs`, log `tc-pipeline` e `dq_results` pelo mesmo `execucao_id`).
- **Regra bloqueante reprovada, SQL com erro ou portão da Gold fechado:** o script para com código 1, a camada seguinte não é publicada, a etapa fica com `status = 'falha'` em `pipeline_runs` e o erro vai para o log `tc-pipeline`, o que dispara o mesmo alerta. Quem executou vê a falha na hora, pelo terminal; o responsável recebe o e-mail em menos de 1 minuto (demonstrado em 29/10).
- **Sem execução:** como não há orquestrador, um pipeline que simplesmente não rodou não gera alerta. Um agendador com alerta de ausência fica para uma próxima etapa (seção 5).

### 7.3 FinOps

**Ambiente.** O projeto rodou no **sandbox do BigQuery** até 28/10/2026, sem cobrança. Desde então está numa conta de faturamento **free trial** (`billingEnabled: true`), e o uso medido fica dentro das franquias gratuitas: o custo real é **R$ 0,00**.

**Orçamento com alerta (Cloud Billing).** Orçamento `TC Fase 02`: mensal, só para o projeto Tech Challenge, todos os serviços, R$ 50,00, com alerta por e-mail aos administradores de faturamento em 25%, 50%, 90% e 100% do gasto real. Os créditos promocionais do free trial **não** são descontados, para o alerta acompanhar o consumo real. Prints em [`docs/evidencias/finops/`](docs/evidencias/finops/).

**Quantidades medidas:**
- leitura por execução completa de Silver e Gold: ≈ 2,3 GB processados (2,14 GiB), por dry run (seção 3.2), e **≈ 2,53 GB faturados**, medidos em `pipeline_runs` na execução de 29/10. A diferença é o mínimo de 10 MB cobrado por consulta, nas 75 consultas de uma execução;
- armazenamento total: 1,74 GiB (catálogo);
- uma carga completa da Bronze: 0,475 GiB;
- consumo real de consultas de 17/10 a 26/10, durante o desenvolvimento: 418 consultas, 20,41 GiB faturados (`INFORMATION_SCHEMA.JOBS_BY_PROJECT`), o que daria US$ 0,22 a preço de tabela.

**Projeção para produção** (mesmo desenho, com faturamento; premissas: batch diário, streaming de 1 evento por segundo, 1 alerta). Tabela completa, com SKUs, franquias e os dois cenários: [`docs/finops/tabela_custo.md`](docs/finops/tabela_custo.md).

| Serviço | Unidade | Quantidade | Preço unitário (São Paulo) | Custo mensal projetado |
|---|---|---|---|---|
| BigQuery: consultas | TiB processado | 30 × 1,67 GiB = 50 GiB (estimado a partir do medido, supondo a Bronze particionada e a Silver lendo só a última carga) | US$ 11,25 / TiB | US$ 0,55 |
| BigQuery: armazenamento | GiB-mês | 1,74 GiB, + 0,475 GiB por carga (medido) | US$ 0,023 / GiB-mês | US$ 0,04 |
| Pub/Sub | TiB (publicação + leitura) | 4,83 GiB (premissa de 1 evento/s; o teste teve 14 mensagens) | US$ 40 / TiB | US$ 0,19 |
| BigQuery: Storage Write API (streaming) | GiB | 2,47 GiB (premissa) | US$ 0,045 / GiB | US$ 0,11 |
| Cloud Logging e Monitoring | GiB / política | < 1 MiB, 1 política | franquia | US$ 0,00 |
| **Total** | | | | **≈ US$ 0,89** sem franquia gratuita; **US$ 0** com ela |

Com o desenho **atual** (Bronze sem partição, a Silver relendo a Bronze inteira) e uma carga completa por dia, a leitura cresce a cada carga: no 6º mês seriam cerca de US$ 26,62 só em consultas. Como a fonte oficial é atualizada **uma vez por ano**, recarregar todo dia não é a cadência pretendida: a recomendação é recarregar só quando a fonte mudar, e particionar a Bronze se as recargas ficarem frequentes. Recomendações com o ganho medido de cada uma (ler só as colunas necessárias: −81%; filtrar a partição da Silver: −45%) estão na seção 5 da tabela de custo.

## 8. Aplicação em IA

A Gold foi desenhada para ser reaproveitada na Fase 3 e está guardada em Parquet em [`gold/export/`](gold/export/).

- **Predição de alfabetização.** `gold_tc.evolucao_municipio` e `gold_tc.municipio_meta` dão, por município e rede, a taxa de 2023 e de 2024. Um modelo pode tentar prever a taxa (ou se o município atinge a meta) a partir de atributos do município. Com só dois anos de série, qualquer projeção até 2030 é um cenário, não uma previsão.
- **Desigualdade educacional.** A mesma base permite comparar redes, UFs e municípios contra a meta pactuada e localizar onde a distância é maior.
- **Políticas públicas baseadas em dados.** O status `atingiu` / `nao_atingiu` / `sem_meta` separa quem falhou de quem simplesmente não tem meta cadastrada, o que evita direcionar ação para o grupo errado.

**Cuidado com vazamento de alvo.** `status_meta` e `distancia_meta` são calculadas a partir de `taxa_alfabetizacao`. Se a taxa (ou o status) for o alvo, essas colunas não podem entrar como features: o modelo acertaria tudo sem aprender nada. O mesmo vale para `variacao_pp` e `tendencia` em `evolucao_municipio` quando o alvo é a taxa de 2024, e para `media_portugues` do mesmo ano, que vem da mesma prova que define a taxa. A tabela `indicador_por_origem` mistura dado oficial e simulado e só pode ser usada filtrando `origem = 'oficial'`.

## 9. Limitações conhecidas

- **Dado simulado no streaming:** 2 rodadas de 7 mensagens de 1 município, executadas com um notebook e não com os scripts de `streaming/`; servem para demonstrar o fluxo, não para análise (seção 3.5).
- **Métricas de execução só no batch transformado:** a Silver e a Gold gravam em `pipeline_runs`; a ingestão da Bronze e o consumer do streaming ainda não (seção 7). Quem executa precisa do papel Gravador de registros (`roles/logging.logWriter`) para a falha chegar ao log e disparar o e-mail; sem ele, a falha fica só em `pipeline_runs` e no terminal.
- **Lacunas da fonte:** `uf` não traz DF nem RR; `municipio` não traz RR e tem 5.550 municípios em vez de 5.570; as proporções por nível não existem em 2023; o número nacional de 2023 da tabela de meta (55,9) diverge do recalculado a partir dos microdados (57,46), sem causa confirmada (seção 3.3).
- **Bronze sem partição:** a leitura da Silver cresce a cada nova carga (seção 6).
- **Execução manual:** sem orquestrador; as etapas são comandos executados em sequência (seção 4).
- **Ambiente:** o projeto rodou no sandbox do BigQuery até 28/10/2026, quando o faturamento foi ativado. Os datasets foram criados com a expiração padrão do sandbox (60 dias), que continua valendo até ser removida; por isso a Gold também foi guardada em Parquet.
- **Revisão de código:** os pull requests foram juntados sem revisão de outra frente.

## 10. Equipe

| Frente | Responsável |
|---|---|
| 1 · Plataforma + Batch | Luana |
| 2 · Streaming | Cauã |
| 3 · Silver/Gold + Qualidade | Ruan |
| 4 · Observabilidade + FinOps + Docs | Edgard |

## 11. Vídeo executivo

*Link a ser incluído.*
