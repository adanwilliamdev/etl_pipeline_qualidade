import logging
from config import ARQ_VALIDADOS, ARQ_LOG
from src.extract import extract
from src.transform import transform
from src.load import load
from src.quarantine import salvar_quarentena
from src.notify import verificar_alerta


def configurar_log() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(ARQ_LOG, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main() -> None:
    configurar_log()
    logger = logging.getLogger("main")
    logger.info("Iniciando pipeline ETL de Qualidade de Dados")

    dados_brutos = extract()
    df_validos, df_quarentena = transform(dados_brutos)

    if not df_validos.empty:
        df_validos.to_csv(ARQ_VALIDADOS, index=False, encoding="utf-8")
        logger.info("Validos exportados para %s", ARQ_VALIDADOS)
        load(df_validos)

    salvar_quarentena(df_quarentena)
    verificar_alerta(len(dados_brutos), len(df_quarentena))

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


if __name__ == "__main__":
    main()
