from src.transform import transform


def test_transform_separa_validos_e_quarentena():
    dados = [
        dict(id_cliente=1, nome="Ana Silva", email="ana@email.com",
             idade=30, valor_compra=100.0, data_registro="2026-01-01"),
        dict(id_cliente=2, nome="Bruno Costa", email="invalido",
             idade=30, valor_compra=100.0, data_registro="2026-01-01"),
    ]
    validos, quarentena = transform(dados)
    assert len(validos) == 1
    assert len(quarentena) == 1
    assert "motivo_erro" in quarentena.columns


def test_transform_mantem_registro_mais_recente_em_duplicata():
    """Entre duplicatas de id_cliente, o registro com data_registro mais
    recente e' o mantido como valido; o(s) mais antigo(s) vao para
    quarentena, sinalizados como duplicata."""
    dados = [
        dict(id_cliente=1, nome="Ana Silva", email="ana_antiga@email.com",
             idade=30, valor_compra=100.0, data_registro="2026-01-01"),
        dict(id_cliente=1, nome="Ana Silva", email="ana_nova@email.com",
             idade=31, valor_compra=200.0, data_registro="2026-01-02"),
    ]
    validos, quarentena = transform(dados)

    assert len(validos) == 1
    assert len(quarentena) == 1
    assert validos.iloc[0]["email"] == "ana_nova@email.com"
    assert "duplicado" in quarentena.iloc[0]["motivo_erro"]
    assert "mais recente" in quarentena.iloc[0]["motivo_erro"]


def test_transform_distingue_duplicata_identica_de_conflitante():
    dados_identicos = [
        dict(id_cliente=1, nome="Ana Silva", email="ana@email.com",
             idade=30, valor_compra=100.0, data_registro="2026-01-01"),
        dict(id_cliente=1, nome="Ana Silva", email="ana@email.com",
             idade=30, valor_compra=100.0, data_registro="2026-01-01"),
    ]
    _, quarentena_identica = transform(dados_identicos)
    assert "identica" in quarentena_identica.iloc[0]["motivo_erro"]

    dados_conflitantes = [
        dict(id_cliente=2, nome="Bruno Costa", email="bruno1@email.com",
             idade=40, valor_compra=50.0, data_registro="2026-01-01"),
        dict(id_cliente=2, nome="Bruno Costa", email="bruno2@email.com",
             idade=41, valor_compra=60.0, data_registro="2026-02-01"),
    ]
    _, quarentena_conflito = transform(dados_conflitantes)
    assert "conflitantes" in quarentena_conflito.iloc[0]["motivo_erro"]


def test_transform_nao_confunde_duplicado_com_invalido():
    """Um registro invalido nao deve ser contado como duplicado de um valido
    com o mesmo id_cliente; cada um recebe seu proprio motivo de rejeicao."""
    dados = [
        dict(id_cliente=1, nome="Ana Silva", email="ana@email.com",
             idade=30, valor_compra=100.0, data_registro="2026-01-01"),
        dict(id_cliente=2, nome="Bruno Costa", email="invalido",
             idade=30, valor_compra=100.0, data_registro="2026-01-01"),
    ]
    validos, quarentena = transform(dados)
    assert len(validos) == 1
    assert len(quarentena) == 1
    assert "email" in quarentena.iloc[0]["motivo_erro"]
