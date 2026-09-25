import logging
import pandas as pd
from config import RAW_DIR

logger = logging.getLogger(__name__)


def extract() -> list:
    """Le todos os arquivos .csv encontrados em data/raw e retorna os
    registros brutos como lista de dicts, prontos para validacao.

    - Varios arquivos .csv na pasta sao combinados em uma unica coleta.
    - Um arquivo que falhar ao ser lido (corrompido, vazio, encoding
      invalido) e' registrado em log e ignorado, sem interromper o pipeline.
    - Os valores sao lidos como texto (dtype=str) para que a validacao de
      tipo e formato aconteca de forma centralizada no schema (Pydantic),
      e nao aqui na extracao.
    """
    arquivos_csv = sorted(RAW_DIR.glob("*.csv"))

    if not arquivos_csv:
        logger.warning("Extract: nenhum arquivo .csv encontrado em %s", RAW_DIR)
        return []

    dataframes = []
    for arquivo in arquivos_csv:
        try:
            df = pd.read_csv(arquivo, dtype=str, keep_default_na=False)
            df["arquivo_origem"] = arquivo.name
            dataframes.append(df)
            logger.info("Extract: %d registros lidos de %s", len(df), arquivo.name)
        except Exception as exc:
            logger.error("Extract: falha ao ler %s (%s) - arquivo ignorado.",
                         arquivo.name, exc)

    if not dataframes:
        logger.warning("Extract: nenhum arquivo pode ser lido com sucesso em %s", RAW_DIR)
        return []

    df_total = pd.concat(dataframes, ignore_index=True)
    dados_brutos = df_total.to_dict(orient="records")

    logger.info("Extract: %d registros brutos coletados de %d arquivo(s).",
                len(dados_brutos), len(arquivos_csv))
    return dados_brutos
