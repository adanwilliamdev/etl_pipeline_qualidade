from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from config import IDADE_MIN, IDADE_MAX, VALOR_COMPRA_MIN, NOME_MIN_LENGTH, NOME_MAX_LENGTH


class ClienteSchema(BaseModel):
    id_cliente: int
    nome: str = Field(min_length=NOME_MIN_LENGTH, max_length=NOME_MAX_LENGTH)
    email: str
    idade: int = Field(ge=IDADE_MIN, le=IDADE_MAX)
    valor_compra: float = Field(gt=VALOR_COMPRA_MIN)
    data_registro: datetime

    @field_validator("email")
    @classmethod
    def validar_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Formato de e-mail invalido")
        return value

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, value: str) -> str:
        value = value.strip()
        if not value.replace(" ", "").isalpha():
            raise ValueError("Nome deve conter apenas letras")
        return value

    @field_validator("data_registro")
    @classmethod
    def validar_data(cls, value: datetime) -> datetime:
        if value > datetime.now():
            raise ValueError("Data de registro nao pode ser futura")
        return value
