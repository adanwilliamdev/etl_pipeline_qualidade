import logging
import os
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR       = BASE_DIR / "data"
RAW_DIR        = DATA_DIR / "raw"
PROCESSED_DIR  = DATA_DIR / "processed"
QUARANTINE_DIR = DATA_DIR / "quarantine"
LOGS_DIR       = BASE_DIR / "logs"

for p in (RAW_DIR, PROCESSED_DIR, QUARANTINE_DIR, LOGS_DIR):
    p.mkdir(parents=True, exist_ok=True)

ARQ_VALIDADOS   = PROCESSED_DIR / "dados_validados.csv"
ARQ_RECUPERADOS = PROCESSED_DIR / "recuperados_quarentena.csv"
ARQ_QUARENTENA  = QUARANTINE_DIR / "quarentena.csv"
ARQ_BANCO       = PROCESSED_DIR / "clientes.db"
ARQ_LOG         = LOGS_DIR / "etl.log"
ARQ_RELATORIO   = PROCESSED_DIR / "relatorio_qualidade.html"

# Regras de qualidade/negocio configuraveis -----------------------------
#
# Os valores abaixo sao os padroes usados quando `regras_qualidade.yaml`
# (na raiz do projeto) nao existe ou nao pode ser lido. Editar esse arquivo
# permite ajustar os limites de validacao sem alterar codigo Python.
REGRAS_PADRAO = {
    "idade_min": 18,
    "idade_max": 120,
    "valor_compra_min": 0.0,
    "nome_min_length": 2,
    "nome_max_length": 120,
    "limite_alerta_erros": 30.0,
}

ARQ_REGRAS = BASE_DIR / "regras_qualidade.yaml"


def _carregar_regras(caminho: Path = None) -> dict:
    """Le `regras_qualidade.yaml` e mescla com os padroes (REGRAS_PADRAO).

    - Chaves ausentes no YAML mantem o valor padrao.
    - Chaves desconhecidas no YAML sao ignoradas (nao "vazam" para o resto
      do sistema por engano).
    - Se o arquivo nao existir ou nao puder ser lido/parseado, os padroes
      sao usados integralmente e um aviso e' logado.
    """
    caminho = caminho if caminho is not None else ARQ_REGRAS
    regras = dict(REGRAS_PADRAO)

    if not caminho.exists():
        return regras

    try:
        with open(caminho, encoding="utf-8") as f:
            conteudo = yaml.safe_load(f) or {}
        if not isinstance(conteudo, dict):
            raise ValueError("o arquivo de regras deve conter um mapeamento chave: valor")
        regras.update({k: v for k, v in conteudo.items() if k in REGRAS_PADRAO})
    except Exception as exc:
        logger.warning(
            "Config: falha ao ler %s (%s); usando regras de qualidade padrao.",
            caminho, exc,
        )
        return dict(REGRAS_PADRAO)

    return regras


_REGRAS = _carregar_regras()

IDADE_MIN            = _REGRAS["idade_min"]
IDADE_MAX            = _REGRAS["idade_max"]
VALOR_COMPRA_MIN     = _REGRAS["valor_compra_min"]
NOME_MIN_LENGTH      = _REGRAS["nome_min_length"]
NOME_MAX_LENGTH      = _REGRAS["nome_max_length"]
LIMITE_ALERTA_ERROS  = _REGRAS["limite_alerta_erros"]

# Rotacao de logs: evita que logs/etl.log cresca indefinidamente.
LOG_MAX_BYTES    = 1_000_000  # 1 MB
LOG_BACKUP_COUNT = 5

# Webhook opcional (Slack ou compativel) para alertas de qualidade.
# Defina a variavel de ambiente SLACK_WEBHOOK_URL para ativar.
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "").strip() or None

# Quantas execucoes recentes mostrar na secao de tendencia do relatorio.
HISTORICO_EXECUCOES = 10
