import logging
import pandas as pd
from pydantic import ValidationError
from src.schemas import ClienteSchema

logger = logging.getLogger(__name__)


def _validar_registros(dados: list):
    """Primeira etapa: valida cada registro contra o schema (Pydantic).

    Retorna (validos_brutos, quarentena), onde validos_brutos e' uma lista
    de tuplas (registro_original, item_validado) - o registro original e'
    mantido para que, se o item acabar em quarentena por duplicidade, o
    texto bruto (nao normalizado) seja preservado no arquivo de quarentena.
    """
    validos_brutos = []
    quarentena = []

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

        validos_brutos.append((registro, item))

    return validos_brutos, quarentena


def _resolver_duplicatas(validos_brutos: list):
    """Segunda etapa: entre registros ja validos, resolve duplicatas de
    `id_cliente`.

    Estrategia: mantem o registro com `data_registro` mais recente (em caso
    de empate, o ultimo encontrado no arquivo/lote); os demais vao para
    quarentena com um motivo que indica se eram duplicatas identicas (todos
    os campos iguais) ou conflitantes (mesmos id_cliente, dados diferentes),
    o que ajuda a priorizar a revisao manual dos casos mais suspeitos.
    """
    por_id: dict = {}
    for registro, item in validos_brutos:
        por_id.setdefault(item.id_cliente, []).append((registro, item))

    validos = []
    quarentena = []
    duplicados = 0

    for id_cliente, grupo in por_id.items():
        if len(grupo) == 1:
            validos.append(grupo[0][1].model_dump())
            continue

        duplicados += len(grupo) - 1
        grupo_ordenado = sorted(grupo, key=lambda par: par[1].data_registro)
        _, vencedor = grupo_ordenado[-1]
        validos.append(vencedor.model_dump())

        dados_vencedor = vencedor.model_dump(exclude={"data_registro"})
        for registro_perdedor, item_perdedor in grupo_ordenado[:-1]:
            identico = item_perdedor.model_dump(exclude={"data_registro"}) == dados_vencedor
            tipo = "identica" if identico else "com dados conflitantes"
            erro = dict(registro_perdedor)
            erro["motivo_erro"] = (
                f"id_cliente: {id_cliente} duplicado ({tipo}); "
                f"mantido o registro mais recente (data_registro={vencedor.data_registro.date()})"
            )
            quarentena.append(erro)

    return validos, quarentena, duplicados


def transform(dados: list):
    """Valida cada registro contra o schema e separa validos de quarentena.

    Alem da validacao estrutural/de negocio (Pydantic), aplica uma regra de
    qualidade adicional para `id_cliente` duplicado: mantem o registro com
    `data_registro` mais recente como valido e envia os demais para
    quarentena, sinalizando se eram duplicatas identicas ou conflitantes.
    """
    validos_brutos, quarentena_invalidos = _validar_registros(dados)
    validos, quarentena_duplicados, duplicados = _resolver_duplicatas(validos_brutos)

    df_validos = pd.DataFrame(validos)
    df_quarentena = pd.DataFrame(quarentena_invalidos + quarentena_duplicados)

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
