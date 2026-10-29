# Frente 4: o que depende do dono do projeto

## Situação em 28/10/2026, 20h

**Não falta nenhum papel no Google Cloud.** O teste de 28/10 gravou as linhas, o log de erro, abriu o alerta e o e-mail chegou.

| Permissão | Situação |
|---|---|
| `roles/logging.logWriter` (Gravador de registros) | ✅ concedido em 28/10: o log ERROR foi gravado e o alerta disparou |
| `roles/serviceusage.serviceUsageConsumer` (Consumidor do Service Usage) | ✅ concedido em 28/10: o Cloud Shell funciona sem contorno |
| Escrita no GitHub (`lu-feijao/tech-challenge-alfabetizacao`) para a conta `Edgefalk` | ⏳ a confirmar: em 26/10 o `git push` deu 403. Quem concede é a dona do repositório, em **Settings → Collaborators → Add people → Edgefalk → Write**. Alternativa sem acesso: fork + pull request |

**Atenção para quem for rodar o pipeline:** quem roda as etapas com o logger precisa de `logging.logEntries.create` (está no papel Editor ou no `roles/logging.logWriter`). Sem ela, a linha vai para `pipeline_runs`, mas o log ERROR não é gravado e o e-mail não sai. O logger avisa no terminal: `[run_logger] não consegui escrever no Cloud Logging`.

### Histórico: situação em 26/10/2026, 21h

| Permissão | Situação |
|---|---|
| `roles/logging.viewer` | ✅ concedido: Logs Explorer abre |
| `roles/monitoring.editor` | ✅ concedido: canal de e-mail criado em 26/10 |
| `roles/bigquery.resourceViewer` | ✅ concedido: consumo real medido e `ops_tc.vw_custo_por_etapa` criada em 26/10 |
| `roles/logging.configWriter` (Gravador de configuração de registros) | ✅ concedido: política "Pipeline TC - falha" criada em 26/10 |
| Cloud Shell | ✅ conta verificada e Cloud Shell autorizado em 26/10 |
| **`roles/logging.logWriter`** (Gravador de registros) | ❌ **falta**. O teste de 26/10 às 21:27 gravou as 2 linhas em `pipeline_runs`, mas o log ERROR foi recusado: "Permission 'logging.logEntries.create' denied". Sem o log, o alerta não dispara |
| `roles/serviceusage.serviceUsageConsumer` (Consumidor do Service Usage) | ⚠️ recomendado. Sem ele, gcloud e as bibliotecas Python no Cloud Shell falham com `USER_PROJECT_DENIED`. Contorno usado: `env -u GOOGLE_CLOUD_QUOTA_PROJECT` no comando |

**Pedido ao dono do projeto:** conceder a `edgge05@gmail.com` os papéis `roles/logging.logWriter` e `roles/serviceusage.serviceUsageConsumer`. Pelo console: **IAM e administrador → IAM → editar o principal edgge05@gmail.com → Adicionar outro papel**. Ou no Cloud Shell dele:

```bash
for PAPEL in roles/logging.logWriter roles/serviceusage.serviceUsageConsumer; do
  gcloud projects add-iam-policy-binding project-ce782257-1c9c-4b6f-87a \
    --member="user:edgge05@gmail.com" --role="$PAPEL"
done
```

Os dois papéis foram concedidos em 28/10.

### Histórico: situação em 26/10/2026, 16h

Faltava `roles/logging.configWriter`. Sem ele, o console bloqueava a criação do alerta de log: "logging.notificationRules.create is also required".

---

## Histórico: situação em 24/10/2026

A conta da Frente 4 (`edgge05@gmail.com`) consegue ler e criar tabelas no BigQuery. **Não** tem permissão para:

| O que falhou | Erro observado em 24/10/2026 | Permissão ou papel que falta |
|---|---|---|
| Ver logs (Logs Explorer) | "Permissão negada. Revise suas permissões do IAM" | `roles/logging.viewer` (Visualizador de registros) |
| Criar canal de e-mail e política de alerta | "Permission denied"; botão "Criar política" desativado | `roles/monitoring.editor` (Editor do Monitoring) |
| Medir o consumo real de consultas e criar `ops_tc.vw_custo_por_etapa` | `bigquery.jobs.listAll` ausente em `INFORMATION_SCHEMA.JOBS_BY_PROJECT` | `roles/bigquery.resourceViewer` (Leitor de recursos do BigQuery) |
| Usar o Cloud Shell | "Verificar sua conta" no primeiro uso | Verificação feita pelo próprio dono da conta (não é IAM) |

## Opção 1: o dono concede os papéis (recomendado)

Pelo console: **IAM e administrador → IAM → Conceder acesso → principal `edgge05@gmail.com`**. Adicione os três papéis da tabela acima.

Ou, no Cloud Shell do dono:

```bash
PROJ=project-ce782257-1c9c-4b6f-87a
for PAPEL in roles/logging.viewer roles/monitoring.editor roles/bigquery.resourceViewer; do
  gcloud projects add-iam-policy-binding "$PROJ" --member="user:edgge05@gmail.com" --role="$PAPEL"
done
```

Depois disso, a Frente 4 cria o alerta, o canal, a view de custo e faz o teste de falha.

## Opção 2: o dono executa, em cerca de 5 minutos

```bash
PROJ=project-ce782257-1c9c-4b6f-87a
gcloud config set project "$PROJ"

# 1) APIs de log e monitoramento (normalmente já vêm ativas)
gcloud services enable logging.googleapis.com monitoring.googleapis.com

# 2) Canal de e-mail. Anote o "name" que o comando devolve
gcloud beta monitoring channels create \
  --display-name="E-mail Frente 4" --type=email \
  --channel-labels=email_address=edgge05@gmail.com

# 3) Em ops/alerta_falha.json, troque SUBSTITUIR_PELO_ID_DO_CANAL pelo ID do passo 2 e crie o alerta
gcloud alpha monitoring policies create --policy-from-file=ops/alerta_falha.json

# 4) Teste: grava 1 linha de sucesso e 1 de falha em ops_tc.pipeline_runs e gera o log ERROR
pip install google-cloud-bigquery google-cloud-logging
python -m ops.testar_alerta

# 5) View de custo (precisa de bigquery.jobs.listAll, que o dono tem)
bq query --use_legacy_sql=false < ops/sql/vw_custo_por_etapa.sql

# 6) Consumo real de consultas dos últimos 30 dias, para a tabela de custo
bq query --use_legacy_sql=false --format=prettyjson < ops/sql/finops/consumo_consultas_30d.sql
```

**Para confirmar que funcionou:**
- chega um e-mail "Pipeline TC - falha" em edgge05@gmail.com;
- `SELECT * FROM ops_tc.pipeline_runs WHERE etapa = 'teste_frente4'` retorna 2 linhas.

Anote dois horários: o que aparece no log (`falha simulada registrada em ...`) e o de chegada do e-mail. A diferença entre eles responde "em quanto tempo descobrimos" no README.

## O que já está pronto e não depende de permissão

- `ops_tc.pipeline_runs` criada em 24/10/2026.
- `ops/run_logger.py`: o logger. Grava por load job, que funciona no Sandbox, e escreve o log `tc-pipeline`.
- `ops/alerta_falha.json`: a política de alerta pronta, faltando só o ID do canal.
- `ops/sql/vw_custo_por_etapa.sql`: a view de custo, com `IF NOT EXISTS`.
