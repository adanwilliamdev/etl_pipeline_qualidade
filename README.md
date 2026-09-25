# ETL Pipeline - Validacao e Qualidade de Dados

Pipeline ETL com validacao estrutural e de negocio, com estrategia de quarentena.

## Como executar

    pip install -r requirements.txt
    python main.py

## Entrada

Coloque um ou mais arquivos `.csv` em `data/raw/`, todos com as colunas:

    id_cliente,nome,email,idade,valor_compra,data_registro

- Todos os `.csv` encontrados na pasta sao lidos e combinados em uma unica coleta.
- Um arquivo corrompido, vazio ou ilegivel e' registrado em log e ignorado,
  sem interromper o restante do pipeline.
- Os valores sao lidos como texto; e' o schema (Pydantic, em `src/schemas.py`)
  quem valida e converte tipos — assim toda a logica de validacao fica
  centralizada em um unico lugar.

Um arquivo de exemplo (`data/raw/clientes.csv`) ja vem incluido para teste.

## Saidas

- data/processed/dados_validados.csv
- data/processed/clientes.db
- data/quarantine/quarentena.csv
- logs/etl.log
