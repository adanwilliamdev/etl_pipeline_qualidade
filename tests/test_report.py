import pandas as pd

import src.report as mod


def test_gerar_relatorio_cria_arquivo_html(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "ARQ_RELATORIO", tmp_path / "relatorio.html")
    monkeypatch.setattr(mod, "ARQ_BANCO", tmp_path / "inexistente.db")

    df_validos = pd.DataFrame([{"id_cliente": 1, "nome": "Ana"}])
    df_quarentena = pd.DataFrame([
        {"id_cliente": 2, "nome": "Bruno", "motivo_erro": "email: invalido"}
    ])

    caminho = mod.gerar_relatorio(df_validos, df_quarentena, total=2)

    assert caminho.exists()
    conteudo = caminho.read_text(encoding="utf-8")
    assert "Relatorio de Qualidade" in conteudo
    assert "ACIMA DO LIMITE" in conteudo  # 50% de erro > limite padrao (30%)
    assert "email" in conteudo


def test_gerar_relatorio_sem_rejeicoes_fica_dentro_do_esperado(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "ARQ_RELATORIO", tmp_path / "relatorio.html")
    monkeypatch.setattr(mod, "ARQ_BANCO", tmp_path / "inexistente.db")

    df_validos = pd.DataFrame([{"id_cliente": 1, "nome": "Ana"}])
    df_quarentena = pd.DataFrame()

    caminho = mod.gerar_relatorio(df_validos, df_quarentena, total=1)
    conteudo = caminho.read_text(encoding="utf-8")
    assert "DENTRO DO ESPERADO" in conteudo


def test_contar_motivos_agrupa_por_campo():
    df = pd.DataFrame([
        {"motivo_erro": "email: invalido; idade: fora do limite"},
        {"motivo_erro": "email: invalido"},
    ])
    contagem = mod._contar_motivos(df)
    assert contagem["email"] == 2
    assert contagem["idade"] == 1
