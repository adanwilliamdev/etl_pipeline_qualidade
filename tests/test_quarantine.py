import pandas as pd

import src.quarantine as mod


def test_salvar_quarentena_grava_arquivo_quando_ha_registros(tmp_path, monkeypatch):
    arq = tmp_path / "quarentena.csv"
    monkeypatch.setattr(mod, "ARQ_QUARENTENA", arq)

    df = pd.DataFrame([{"id_cliente": 1, "motivo_erro": "email: invalido"}])
    mod.salvar_quarentena(df)

    assert arq.exists()
    assert "email" in arq.read_text(encoding="utf-8")


def test_salvar_quarentena_remove_arquivo_antigo_quando_vazio(tmp_path, monkeypatch):
    arq = tmp_path / "quarentena.csv"
    arq.write_text("lixo de uma execucao anterior", encoding="utf-8")
    monkeypatch.setattr(mod, "ARQ_QUARENTENA", arq)

    mod.salvar_quarentena(pd.DataFrame())

    assert not arq.exists()


def test_salvar_quarentena_vazio_sem_arquivo_previo_nao_quebra(tmp_path, monkeypatch):
    arq = tmp_path / "quarentena.csv"
    monkeypatch.setattr(mod, "ARQ_QUARENTENA", arq)

    mod.salvar_quarentena(pd.DataFrame())  # nao deve lancar excecao

    assert not arq.exists()
