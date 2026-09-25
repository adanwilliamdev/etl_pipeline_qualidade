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
