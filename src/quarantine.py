import logging
import pandas as pd
from config import ARQ_QUARENTENA

logger = logging.getLogger(__name__)


def salvar_quarentena(df: pd.DataFrame) -> None:
    """Grava (ou limpa) `data/quarantine/quarentena.csv` com os registros
    atualmente rejeitados.

    O arquivo reflete sempre o estado da ultima validacao: se nao houver
    nenhum registro rejeitado (por exemplo, apos um reprocessamento que
    recuperou todos os casos), um `quarentena.csv` antigo e' removido em vez
    de deixado para tras, para nao sugerir que registros ja corrigidos
    continuam pendentes.
    """
    if df.empty:
        if ARQ_QUARENTENA.exists():
            ARQ_QUARENTENA.unlink()
        logger.info("Quarentena: nenhum registro rejeitado (arquivo de quarentena removido, se existia).")
        return
    df.to_csv(ARQ_QUARENTENA, index=False, encoding="utf-8")
    logger.warning("Quarentena: %d registros salvos em %s",
                   len(df), ARQ_QUARENTENA)
