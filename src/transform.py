import logging
import pandas as pd
from pydantic import ValidationError
from src.schemas import ClienteSchema

logger = logging.getLogger(__name__)


def transform(dados: list):
    validos, quarentena = [], []

    for registro in dados:
        try:
            item = ClienteSchema(**registro)
            validos.append(item.model_dump())
        except ValidationError as e:
            erro = dict(registro)
            erro["motivo_erro"] = "; ".join(
                f"{err['loc'][0]}: {err['msg']}" for err in e.errors()
            )
            quarentena.append(erro)

    df_validos = pd.DataFrame(validos)
    df_quarentena = pd.DataFrame(quarentena)

    total = len(dados)
    ok = len(df_validos)
    bad = len(df_quarentena)
    taxa = (bad / total * 100) if total else 0.0

    logger.info("Transform: %d validos | %d em quarentena | %.1f%% erro.",
                ok, bad, taxa)
    return df_validos, df_quarentena
