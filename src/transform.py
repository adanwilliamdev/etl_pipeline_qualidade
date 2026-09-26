import logging
import pandas as pd
from pydantic import ValidationError
from src.schemas import ClienteSchema

logger = logging.getLogger(__name__)


def transform(dados: list):
    """Valida cada registro contra o schema e separa validos de quarentena.

    Alem da validacao estrutural/de negocio (Pydantic), aplica uma regra de
    qualidade adicional: registros com `id_cliente` duplicado. O primeiro
    registro visto com um dado id_cliente e mantido como valido; ocorrencias
    seguintes do mesmo id_cliente sao enviadas para quarentena, para que um
    mesmo cliente nao gere linhas conflitantes na base final.
    """
    validos, quarentena = [], []
    ids_vistos = set()
    duplicados = 0

    for registro in dados:
        try:
            item = ClienteSchema(**registro)
        except ValidationError as e:
            erro = dict(registro)
            erro["motivo_erro"] = "; ".join(
                f"{err['loc'][0]}: {err['msg']}" for err in e.errors()
            )
            quarentena.append(erro)
            continue

        if item.id_cliente in ids_vistos:
            erro = dict(registro)
            erro["motivo_erro"] = (
                f"id_cliente: {item.id_cliente} duplicado "
                "(mantido o primeiro registro encontrado)"
            )
            quarentena.append(erro)
            duplicados += 1
            continue

        ids_vistos.add(item.id_cliente)
        validos.append(item.model_dump())

    df_validos = pd.DataFrame(validos)
    df_quarentena = pd.DataFrame(quarentena)

    total = len(dados)
    ok = len(df_validos)
    bad = len(df_quarentena)
    taxa = (bad / total * 100) if total else 0.0

    logger.info("Transform: %d validos | %d em quarentena | %.1f%% erro.",
                ok, bad, taxa)
    if duplicados:
        logger.warning("Transform: %d registro(s) em quarentena por id_cliente duplicado.",
                        duplicados)
    return df_validos, df_quarentena
