import logging

import pandas as pd

from config import ARQ_QUARENTENA
from src.transform import transform

logger = logging.getLogger(__name__)


def reprocessar_quarentena():
    """Tenta revalidar os registros atualmente em `data/quarantine/quarentena.csv`.

    Util depois que os dados de origem sao corrigidos manualmente (por
    exemplo, um e-mail arrumado direto na planilha de quarentena). Reaplica
    a mesma logica de validacao e deduplicacao usada pelo `transform`
    normal, entao registros corrigidos que agora passam nas regras podem ser
    recuperados sem precisar reprocessar o pipeline inteiro do zero.

    A coluna auxiliar `motivo_erro` (e `arquivo_origem`, se presente) e'
    descartada antes da revalidacao: sao campos de controle do proprio
    pipeline, nao dados de negocio, e o schema os ignoraria de qualquer
    forma.

    Retorna (df_recuperados, df_ainda_quarentena, total_reprocessado).
    """
    if not ARQ_QUARENTENA.exists():
        logger.info("Reprocessamento: nenhum arquivo de quarentena encontrado em %s",
                     ARQ_QUARENTENA)
        return pd.DataFrame(), pd.DataFrame(), 0

    df_atual = pd.read_csv(ARQ_QUARENTENA, dtype=str, keep_default_na=False)
    if df_atual.empty:
        logger.info("Reprocessamento: quarentena esta vazia, nada a fazer.")
        return pd.DataFrame(), pd.DataFrame(), 0

    registros = df_atual.drop(columns=["motivo_erro"], errors="ignore").to_dict(orient="records")
    df_recuperados, df_ainda_quarentena = transform(registros)

    logger.info(
        "Reprocessamento: %d registro(s) recuperado(s) de %d em quarentena.",
        len(df_recuperados), len(registros),
    )
    return df_recuperados, df_ainda_quarentena, len(registros)
