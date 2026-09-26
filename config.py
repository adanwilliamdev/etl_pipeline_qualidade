import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR       = BASE_DIR / "data"
RAW_DIR        = DATA_DIR / "raw"
PROCESSED_DIR  = DATA_DIR / "processed"
QUARANTINE_DIR = DATA_DIR / "quarantine"
LOGS_DIR       = BASE_DIR / "logs"

for p in (RAW_DIR, PROCESSED_DIR, QUARANTINE_DIR, LOGS_DIR):
    p.mkdir(parents=True, exist_ok=True)

IDADE_MIN = 18
IDADE_MAX = 120
VALOR_COMPRA_MIN = 0.0

ARQ_VALIDADOS  = PROCESSED_DIR / "dados_validados.csv"
ARQ_QUARENTENA = QUARANTINE_DIR / "quarentena.csv"
ARQ_BANCO      = PROCESSED_DIR / "clientes.db"
ARQ_LOG        = LOGS_DIR / "etl.log"
ARQ_RELATORIO  = PROCESSED_DIR / "relatorio_qualidade.html"

LIMITE_ALERTA_ERROS = 30.0

# Rotacao de logs: evita que logs/etl.log cresca indefinidamente.
LOG_MAX_BYTES    = 1_000_000  # 1 MB
LOG_BACKUP_COUNT = 5

# Webhook opcional (Slack ou compativel) para alertas de qualidade.
# Defina a variavel de ambiente SLACK_WEBHOOK_URL para ativar.
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "").strip() or None

# Quantas execucoes recentes mostrar na secao de tendencia do relatorio.
HISTORICO_EXECUCOES = 10
