import logging

logger = logging.getLogger(__name__)


def extract() -> list:
    """Simula a ingestao de dados brutos."""
    dados_brutos = [
        {"id_cliente": 1, "nome": "Ana Silva", "email": "ana@email.com",
         "idade": 29, "valor_compra": 150.50, "data_registro": "2026-01-10"},
        {"id_cliente": 2, "nome": "Bruno Costa", "email": "bruno-email-invalido",
         "idade": 35, "valor_compra": 89.90, "data_registro": "2026-02-15"},
        {"id_cliente": 3, "nome": "Carlos Souza", "email": "carlos@email.com",
         "idade": 15, "valor_compra": 200.00, "data_registro": "2026-03-01"},
        {"id_cliente": 4, "nome": "Daniela Lima", "email": "DANIELA@EMAIL.COM",
         "idade": 42, "valor_compra": -50.00, "data_registro": "2026-03-20"},
        {"id_cliente": 5, "nome": "Eduardo Ramos", "email": "eduardo@email.com",
         "idade": 31, "valor_compra": 320.75, "data_registro": "2026-04-01"},
    ]
    logger.info("Extract: %d registros brutos coletados.", len(dados_brutos))
    return dados_brutos
