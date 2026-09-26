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


def test_transform_quarentena_id_cliente_duplicado():
    """O primeiro registro de um id_cliente e' valido; duplicatas vao para
    quarentena com um motivo especifico, sem gerar excecao no schema."""
    dados = [
        dict(id_cliente=1, nome="Ana Silva", email="ana@email.com",
             idade=30, valor_compra=100.0, data_registro="2026-01-01"),
        dict(id_cliente=1, nome="Ana Silva", email="ana2@email.com",
             idade=31, valor_compra=200.0, data_registro="2026-01-02"),
    ]
    validos, quarentena = transform(dados)

    assert len(validos) == 1
    assert len(quarentena) == 1
    assert validos.iloc[0]["email"] == "ana@email.com"
    assert "duplicado" in quarentena.iloc[0]["motivo_erro"]


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
