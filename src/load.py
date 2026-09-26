import logging
import sqlite3
import pandas as pd
from config import ARQ_BANCO

logger = logging.getLogger(__name__)


def _tabela_existe(conn: sqlite3.Connection, nome: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nome,)
    )
    return cur.fetchone() is not None


def load(df: pd.DataFrame) -> None:
    """Grava os registros validos na tabela `clientes` do SQLite.

    A carga e' incremental (upsert por id_cliente): registros ja existentes
    na base sao atualizados com os dados mais recentes e novos registros sao
    inseridos, sem apagar clientes carregados em execucoes anteriores. Isso
    torna o pipeline seguro para rodar varias vezes (idempotente), inclusive
    quando cada execucao traz apenas um subconjunto dos dados.
    """
    if df.empty:
        logger.warning("Load: nenhum dado valido para carregar.")
        return

    df = df.copy()
    if "data_registro" in df.columns:
        # SQLite nao possui tipo datetime nativo: gravamos sempre como texto
        # ISO para que o dtype fique estavel entre execucoes (evita misturar
        # pandas.Timestamp com str depois de um round-trip pelo banco).
        df["data_registro"] = pd.to_datetime(df["data_registro"]).astype(str)

    with sqlite3.connect(ARQ_BANCO) as conn:
        if _tabela_existe(conn, "clientes"):
            existentes = pd.read_sql("SELECT * FROM clientes", conn)
            combinado = pd.concat([existentes, df], ignore_index=True)
        else:
            combinado = df

        combinado = combinado.drop_duplicates(subset="id_cliente", keep="last")
        combinado.to_sql("clientes", conn, if_exists="replace", index=False)

    logger.info("Load: %d registros gravados (upsert) em %s", len(df), ARQ_BANCO)


def registrar_execucao(total: int, validos: int, quarentena: int) -> None:
    """Registra metricas da execucao atual na tabela `execucoes`.

    Mantem um historico simples (timestamp, total, validos, quarentena,
    taxa de erro) usado pelo relatorio de qualidade para mostrar tendencia
    entre execucoes do pipeline.
    """
    from datetime import datetime

    taxa = (quarentena / total * 100) if total else 0.0
    with sqlite3.connect(ARQ_BANCO) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS execucoes (
                   timestamp TEXT, total INTEGER, validos INTEGER,
                   quarentena INTEGER, taxa_erro REAL
               )"""
        )
        conn.execute(
            "INSERT INTO execucoes VALUES (?, ?, ?, ?, ?)",
            (datetime.now().isoformat(timespec="seconds"), total, validos, quarentena, taxa),
        )
        conn.commit()
    logger.info("Historico: execucao registrada (%d validos, %d quarentena, %.1f%% erro).",
                validos, quarentena, taxa)
