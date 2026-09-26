# ETL Pipeline - Validacao e Qualidade de Dados

Pipeline ETL com validacao estrutural e de negocio, estrategia de quarentena,
carga incremental, historico de execucoes, relatorio de qualidade e alertas.

## Como executar

    pip install -r requirements.txt
    python main.py

### Opcoes de linha de comando

    python main.py --raw-dir /caminho/para/outra/pasta   # usa outra pasta de entrada
    python main.py --dry-run                              # valida e gera relatorio,
                                                            # sem gravar no banco/historico

### Com Docker

    docker build -t etl-qualidade .
    docker run --rm -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs etl-qualidade

Ou, com o `Makefile` incluido: `make install`, `make test`, `make run`,
`make dry-run`, `make docker-build`, `make docker-run`.

## Entrada

Coloque um ou mais arquivos `.csv` em `data/raw/` (ou na pasta indicada por
`--raw-dir`), todos com as colunas:

    id_cliente,nome,email,idade,valor_compra,data_registro

- Todos os `.csv` encontrados na pasta sao lidos e combinados em uma unica coleta.
- Um arquivo corrompido, vazio ou ilegivel e' registrado em log e ignorado,
  sem interromper o restante do pipeline.
- Os valores sao lidos como texto; e' o schema (Pydantic, em `src/schemas.py`)
  quem valida e converte tipos — assim toda a logica de validacao fica
  centralizada em um unico lugar.
- Registros com `id_cliente` repetido sao tratados como duplicatas: o
  primeiro e' mantido como valido, os seguintes vao para quarentena.

Um arquivo de exemplo (`data/raw/clientes.csv`) ja vem incluido para teste.

## Qualidade e observabilidade

- **Carga incremental (upsert):** cada execucao atualiza/insere clientes em
  `clientes.db` por `id_cliente`, sem apagar dados carregados anteriormente —
  o pipeline pode ser rodado repetidamente com arquivos parciais.
- **Historico de execucoes:** cada rodada grava suas metricas (total, validos,
  quarentena, taxa de erro) na tabela `execucoes` do mesmo banco.
- **Relatorio HTML de qualidade:** gerado a cada execucao em
  `data/processed/relatorio_qualidade.html`, com contagem de validos/quarentena,
  principais motivos de rejeicao e tendencia das ultimas execucoes.
- **Alerta via webhook:** se a taxa de rejeicao ultrapassar o limite
  (`LIMITE_ALERTA_ERROS` em `config.py`), o alerta e' registrado em log e,
  se a variavel de ambiente `SLACK_WEBHOOK_URL` estiver definida, tambem
  enviado para esse webhook (compativel com Slack/Teams/etc.).
- **Logs com rotacao:** `logs/etl.log` roda em ate 5 arquivos de 1 MB cada,
  para nao crescer indefinidamente.

## Saidas

- data/processed/dados_validados.csv
- data/processed/clientes.db (tabelas `clientes` e `execucoes`)
- data/processed/relatorio_qualidade.html
- data/quarantine/quarentena.csv
- logs/etl.log (com rotacao)

## Testes e CI

    make test          # ou: pytest -v

Um workflow de CI (`.github/workflows/ci.yml`) roda a suite de testes e um
smoke test do pipeline (`--dry-run`) em Python 3.10, 3.11 e 3.12 a cada push
ou pull request para `main`.
