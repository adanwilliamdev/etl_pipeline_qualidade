import logging
import pandas as pd
from config import ARQ_QUARENTENA

logger = logging.getLogger(__name__)


def salvar_quarentena(df: pd.DataFrame) -> None:
    if df.empty:
        logger.info("Quarentena: nenhum registro rejeitado.")
        return
    df.to_csv(ARQ_QUARENTENA, index=False, encoding="utf-8")
    logger.warning("Quarentena: %d registros salvos em %s",
                   len(df), ARQ_QUARENTENA)
