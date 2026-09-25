import pytest
from datetime import datetime
from pydantic import ValidationError
from src.schemas import ClienteSchema


def _base(**over):
    base = dict(
        id_cliente=1, nome="Ana Silva", email="ana@email.com",
        idade=30, valor_compra=100.0,
        data_registro=datetime(2026, 1, 1),
    )
    base.update(over)
    return base


def test_registro_valido():
    assert ClienteSchema(**_base()).email == "ana@email.com"


def test_email_invalido():
    with pytest.raises(ValidationError):
        ClienteSchema(**_base(email="sem-arroba"))


def test_idade_fora_do_limite():
    with pytest.raises(ValidationError):
        ClienteSchema(**_base(idade=15))


def test_valor_negativo():
    with pytest.raises(ValidationError):
        ClienteSchema(**_base(valor_compra=-10))


def test_data_futura():
    with pytest.raises(ValidationError):
        ClienteSchema(**_base(data_registro=datetime(2999, 1, 1)))
