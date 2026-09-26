import pandas as pd

import src.reprocess as mod


def _escrever_quarentena(caminho, linhas_csv):
    caminho.write_text(linhas_csv, encoding="utf-8")


def test_reprocessar_sem_arquivo_retorna_vazio(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "ARQ_QUARENTENA", tmp_path / "nao_existe.csv")
    recuperados, ainda_quarentena, total = mod.reprocessar_quarentena()
    assert recuperados.empty
    assert ainda_quarentena.empty
    assert total == 0


def test_reprocessar_arquivo_vazio_retorna_vazio(tmp_path, monkeypatch):
    arq = tmp_path / "quarentena.csv"
    arq.write_text(
        "id_cliente,nome,email,idade,valor_compra,data_registro,motivo_erro\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "ARQ_QUARENTENA", arq)

    recuperados, ainda_quarentena, total = mod.reprocessar_quarentena()

    assert recuperados.empty
    assert ainda_quarentena.empty
    assert total == 0


def test_reprocessar_recupera_registro_corrigido(tmp_path, monkeypatch):
    """Um registro que estava em quarentena por e-mail invalido e' recuperado
    apos a correcao manual do dado na propria planilha de quarentena."""
    arq = tmp_path / "quarentena.csv"
    _escrever_quarentena(
        arq,
        "id_cliente,nome,email,idade,valor_compra,data_registro,motivo_erro\n"
        "2,Bruno Costa,bruno@email.com,35,89.90,2026-02-15,email: invalido\n",
    )
    monkeypatch.setattr(mod, "ARQ_QUARENTENA", arq)

    recuperados, ainda_quarentena, total = mod.reprocessar_quarentena()

    assert total == 1
    assert len(recuperados) == 1
    assert ainda_quarentena.empty
    assert recuperados.iloc[0]["email"] == "bruno@email.com"


def test_reprocessar_mantem_em_quarentena_o_que_continua_invalido(tmp_path, monkeypatch):
    arq = tmp_path / "quarentena.csv"
    _escrever_quarentena(
        arq,
        "id_cliente,nome,email,idade,valor_compra,data_registro,motivo_erro\n"
        "3,Carlos Souza,carlos@email.com,15,200.00,2026-03-01,idade: menor que o minimo\n",
    )
    monkeypatch.setattr(mod, "ARQ_QUARENTENA", arq)

    recuperados, ainda_quarentena, total = mod.reprocessar_quarentena()

    assert total == 1
    assert recuperados.empty
    assert len(ainda_quarentena) == 1
    assert ainda_quarentena.iloc[0]["id_cliente"] == "3"
