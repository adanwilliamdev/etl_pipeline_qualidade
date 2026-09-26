import sqlite3

import pandas as pd
from src.load import load, registrar_execucao


def test_load_dataframe_vazio_nao_quebra():
    load(pd.DataFrame())


def _registro(id_cliente=1, nome="Ana", email="a@b.com"):
    return {
        "id_cliente": id_cliente, "nome": nome, "email": email,
        "idade": 30, "valor_compra": 10.0,
        "data_registro": "2026-01-01",
    }


def test_load_cria_tabela(tmp_path, monkeypatch):
    import src.load as mod
    monkeypatch.setattr(mod, "ARQ_BANCO", tmp_path / "t.db")

    df = pd.DataFrame([_registro()])
    load(df)
    assert (tmp_path / "t.db").exists()


def test_load_e_incremental_e_faz_upsert(tmp_path, monkeypatch):
    """Uma segunda execucao com um cliente novo deve manter o cliente
    carregado na execucao anterior (upsert, nao substituicao total)."""
    import src.load as mod
    monkeypatch.setattr(mod, "ARQ_BANCO", tmp_path / "t.db")

    load(pd.DataFrame([_registro(id_cliente=1, nome="Ana")]))
    load(pd.DataFrame([_registro(id_cliente=2, nome="Bruno", email="b@b.com")]))

    with sqlite3.connect(tmp_path / "t.db") as conn:
        ids = {row[0] for row in conn.execute("SELECT id_cliente FROM clientes")}
    assert ids == {1, 2}


def test_load_atualiza_registro_existente(tmp_path, monkeypatch):
    """Uma nova execucao com o mesmo id_cliente deve atualizar os dados
    (upsert), nao duplicar a linha."""
    import src.load as mod
    monkeypatch.setattr(mod, "ARQ_BANCO", tmp_path / "t.db")

    load(pd.DataFrame([_registro(id_cliente=1, nome="Ana Velha")]))
    load(pd.DataFrame([_registro(id_cliente=1, nome="Ana Nova")]))

    with sqlite3.connect(tmp_path / "t.db") as conn:
        linhas = conn.execute("SELECT nome FROM clientes WHERE id_cliente=1").fetchall()
    assert linhas == [("Ana Nova",)]


def test_registrar_execucao_cria_historico(tmp_path, monkeypatch):
    import src.load as mod
    monkeypatch.setattr(mod, "ARQ_BANCO", tmp_path / "t.db")

    registrar_execucao(total=10, validos=8, quarentena=2)

    with sqlite3.connect(tmp_path / "t.db") as conn:
        linhas = conn.execute("SELECT total, validos, quarentena FROM execucoes").fetchall()
    assert linhas == [(10, 8, 2)]
