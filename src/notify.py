import logging
from config import LIMITE_ALERTA_ERROS

logger = logging.getLogger(__name__)


def verificar_alerta(total: int, rejeitados: int) -> None:
    if total == 0:
        return
    taxa = rejeitados / total * 100
    if taxa >= LIMITE_ALERTA_ERROS:
        logger.error("ALERTA: taxa de rejeicao %.1f%% ultrapassou o limite %.1f%%",
                     taxa, LIMITE_ALERTA_ERROS)
    else:
        logger.info("Taxa de rejeicao dentro do aceitavel (%.1f%%).", taxa)
