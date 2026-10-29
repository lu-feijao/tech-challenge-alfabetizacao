# Arquitetura implementada

Versão em imagem: [`arquitetura.png`](arquitetura.png).

O diagrama mostra **só o que existe no projeto em 28/10/2026**, conferido pelo catálogo (`docs/catalogo/catalogo_dados.md`). Linhas tracejadas são fluxos de controle ou observabilidade. A Silver e a Gold gravam em `pipeline_runs`; a Bronze e o streaming ainda não usam o logger. Os itens marcados como *pendente* ou *a confirmar* ainda não foram verificados no projeto.

```mermaid
flowchart LR
    F[("Tabelas oficiais<br/>alfabetização infantil")]

    subgraph BRONZE["bronze_tc · dado como veio, só acréscimo"]
        B1[("alunos · municipio · uf<br/>meta_alfabetizacao_*<br/>dicionario")]
        B2[("eventos_alunos")]
    end

    subgraph SILVER["silver_tc · limpo e padronizado"]
        S1[("alunos (part. ano)<br/>municipio · uf<br/>meta_* · de_para_*")]
        S2[("alunos_eventos")]
    end

    subgraph GOLD["gold_tc · pronto para análise"]
        G2[("indicador_por_origem<br/>oficial x simulado")]
        G1[("municipio_meta · uf_meta · brasil_meta<br/>evolucao_municipio · validacao_cruzada")]
    end

    subgraph OPS["ops_tc · operação"]
        DQ[("dq_results")]
        REJ[("eventos_rejeitados")]
        PR[("pipeline_runs")]
    end

    SIM["Simulador de eventos"] --> MSG["Pub/Sub<br/>topico-alfabetizacao<br/>(assinatura pull)"] --> CONS["Consumidor<br/>micro-lotes"]

    F -- "batch, acréscimo" --> B1
    CONS -- "válidos" --> B2
    CONS -- "inválidos" --> REJ
    B1 --> S1
    B2 --> S2
    S2 --> G2
    S1 --> G2
    S1 --> G1

    S1 -. "regras de qualidade" .-> DQ
    G1 -. "regras de qualidade" .-> DQ
    S1 -. "cada etapa (logger)" .-> PR
    G1 -. "cada etapa (logger)" .-> PR
    PR -. "falha" .-> LOG["Cloud Logging<br/>log tc-pipeline"]
    LOG -. "política Pipeline TC - falha" .-> AL["Alerta por e-mail<br/>edgge05@gmail.com"]
```

## O que cada parte guarda

| Dataset | Tabelas | Linhas | Tamanho |
|---|---:|---:|---:|
| `bronze_tc` | 9 | 7.805.967 | 972,63 MiB |
| `silver_tc` | 9 | 3.930.225 | 803,77 MiB |
| `gold_tc` | 6 | 58.638 | 5,41 MiB |
| `ops_tc` | 3 tabelas e 1 view (`vw_custo_por_etapa`); `pipeline_runs` tem só as 4 linhas dos testes de 26/10 e 28/10 | 192 | 31,31 KiB |

**Região:** `southamerica-east1`. **Ambiente:** faturamento ativo (conferido em 28/10/2026; antes, BigQuery Sandbox). As tabelas criadas no Sandbox mantêm a data de expiração: 15/12 (Bronze) e 22/12 (Silver e Gold).
