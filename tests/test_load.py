import pandas as pd
from src.load import load


def test_load_dataframe_vazio_nao_quebra():
    load(pd.DataFrame())


def test_load_cria_tabela(tmp_path, monkeypatch):
    import src.load as mod
    monkeypatch.setattr(mod, "ARQ_BANCO", tmp_path / "t.db")

    df = pd.DataFrame([{
        "id_cliente": 1, "nome": "Ana", "email": "a@b.com",
        "idade": 30, "valor_compra": 10.0,
        "data_registro": "2026-01-01",
    }])
    load(df)
    assert (tmp_path / "t.db").exists()
