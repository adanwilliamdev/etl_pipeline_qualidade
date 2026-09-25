import logging
import sqlite3
import pandas as pd
from config import ARQ_BANCO

logger = logging.getLogger(__name__)


def load(df: pd.DataFrame) -> None:
    if df.empty:
        logger.warning("Load: nenhum dado valido para carregar.")
        return
    with sqlite3.connect(ARQ_BANCO) as conn:
        df.to_sql("clientes", conn, if_exists="replace", index=False)
    logger.info("Load: %d registros gravados em %s", len(df), ARQ_BANCO)
