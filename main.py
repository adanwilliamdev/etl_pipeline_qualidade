import argparse
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import ARQ_VALIDADOS, ARQ_LOG, LOG_MAX_BYTES, LOG_BACKUP_COUNT
from src.extract import extract
from src.transform import transform
from src.load import load, registrar_execucao
from src.quarantine import salvar_quarentena
from src.notify import verificar_alerta
from src.report import gerar_relatorio


def configurar_log() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            RotatingFileHandler(
                ARQ_LOG, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pipeline ETL com validacao e quarentena de qualidade de dados."
    )
    parser.add_argument(
        "--raw-dir", type=str, default=None,
        help="Diretorio com os .csv de entrada (padrao: data/raw).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Executa extract/transform e gera o relatorio, mas nao grava no "
             "banco de dados (clientes.db) nem no historico de execucoes.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    configurar_log()
    logger = logging.getLogger("main")
    logger.info("Iniciando pipeline ETL de Qualidade de Dados")
    if args.dry_run:
        logger.info("Modo dry-run ativo: nada sera' gravado no banco de dados.")

    raw_dir = Path(args.raw_dir) if args.raw_dir else None
    dados_brutos = extract(raw_dir=raw_dir)
    df_validos, df_quarentena = transform(dados_brutos)

    if not df_validos.empty:
        df_validos.to_csv(ARQ_VALIDADOS, index=False, encoding="utf-8")
        logger.info("Validos exportados para %s", ARQ_VALIDADOS)
        if not args.dry_run:
            load(df_validos)

    salvar_quarentena(df_quarentena)
    verificar_alerta(len(dados_brutos), len(df_quarentena))

    if not args.dry_run:
        registrar_execucao(len(dados_brutos), len(df_validos), len(df_quarentena))

    caminho_relatorio = gerar_relatorio(df_validos, df_quarentena, len(dados_brutos))
    logger.info("Relatorio de qualidade disponivel em %s", caminho_relatorio)

    logger.info("Pipeline finalizado com sucesso")

    print("\n=== DADOS VALIDADOS ===")
    print(df_validos.to_string(index=False) if not df_validos.empty
          else "(nenhum registro valido)")

    print("\n=== REGISTROS EM QUARENTENA ===")
    if not df_quarentena.empty:
        cols = [c for c in ("id_cliente", "nome", "motivo_erro")
                if c in df_quarentena.columns]
        print(df_quarentena[cols].to_string(index=False))
    else:
        print("(nenhum registro rejeitado)")

    print(f"\nRelatorio de qualidade: {caminho_relatorio}")


if __name__ == "__main__":
    main()
