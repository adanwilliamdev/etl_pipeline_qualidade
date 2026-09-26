import json
import logging
import urllib.request
from config import LIMITE_ALERTA_ERROS, SLACK_WEBHOOK_URL

logger = logging.getLogger(__name__)


def _enviar_webhook(mensagem: str) -> None:
    """Envia um alerta para um webhook estilo Slack, se configurado.

    Controlado pela variavel de ambiente SLACK_WEBHOOK_URL. Se nao estiver
    definida, a funcao nao faz nada. Qualquer falha de rede e' apenas
    registrada em log, sem interromper o pipeline.
    """
    if not SLACK_WEBHOOK_URL:
        return
    try:
        payload = json.dumps({"text": mensagem}).encode("utf-8")
        req = urllib.request.Request(
            SLACK_WEBHOOK_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
        logger.info("Notify: alerta enviado ao webhook configurado.")
    except Exception as exc:
        logger.error("Notify: falha ao enviar alerta via webhook (%s).", exc)


def verificar_alerta(total: int, rejeitados: int) -> None:
    if total == 0:
        return
    taxa = rejeitados / total * 100
    if taxa >= LIMITE_ALERTA_ERROS:
        mensagem = (
            f"ALERTA: taxa de rejeicao {taxa:.1f}% ultrapassou o limite "
            f"{LIMITE_ALERTA_ERROS:.1f}%"
        )
        logger.error(mensagem)
        _enviar_webhook(f":rotating_light: {mensagem}")
    else:
        logger.info("Taxa de rejeicao dentro do aceitavel (%.1f%%).", taxa)
