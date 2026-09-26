import html
import logging
import sqlite3
from datetime import datetime

import pandas as pd

from config import ARQ_BANCO, ARQ_RELATORIO, HISTORICO_EXECUCOES, LIMITE_ALERTA_ERROS

logger = logging.getLogger(__name__)


def _contar_motivos(df_quarentena: pd.DataFrame) -> dict:
    """Conta quantas vezes cada campo aparece como motivo de rejeicao.

    Cada registro em quarentena pode ter varios motivos (ex.: "idade: ...;
    email: ..."); aqui contamos por campo para dar uma visao agregada dos
    problemas mais comuns nos dados.
    """
    contagem: dict = {}
    if df_quarentena.empty or "motivo_erro" not in df_quarentena.columns:
        return contagem

    for motivos in df_quarentena["motivo_erro"]:
        for parte in str(motivos).split("; "):
            campo = parte.split(":")[0].strip() or "outro"
            contagem[campo] = contagem.get(campo, 0) + 1

    return dict(sorted(contagem.items(), key=lambda item: -item[1]))


def _ler_historico() -> pd.DataFrame:
    if not ARQ_BANCO.exists():
        return pd.DataFrame()
    try:
        with sqlite3.connect(ARQ_BANCO) as conn:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='execucoes'"
            )
            if not cur.fetchone():
                return pd.DataFrame()
            return pd.read_sql(
                f"SELECT * FROM execucoes ORDER BY timestamp DESC LIMIT {HISTORICO_EXECUCOES}",
                conn,
            )
    except Exception as exc:
        logger.error("Relatorio: falha ao ler historico de execucoes (%s).", exc)
        return pd.DataFrame()


def _barra_html(valor: float, maximo: float, cor: str) -> str:
    largura = 0 if maximo <= 0 else max(2, round(valor / maximo * 100))
    return (
        f'<div class="barra-fundo"><div class="barra" '
        f'style="width:{largura}%;background:{cor};"></div></div>'
    )


def gerar_relatorio(df_validos: pd.DataFrame, df_quarentena: pd.DataFrame, total: int):
    """Gera um relatorio HTML autocontido com metricas de qualidade da execucao.

    Inclui: contagem de validos/quarentena, taxa de erro frente ao limite de
    alerta, principais motivos de rejeicao e a tendencia das ultimas
    execucoes (quando ha' historico disponivel no banco). Retorna o caminho
    do arquivo gerado.
    """
    ok = len(df_validos)
    bad = len(df_quarentena)
    taxa = (bad / total * 100) if total else 0.0
    status_cor = "#c0392b" if taxa >= LIMITE_ALERTA_ERROS else "#1e8e5a"
    status_texto = "ACIMA DO LIMITE" if taxa >= LIMITE_ALERTA_ERROS else "DENTRO DO ESPERADO"

    motivos = _contar_motivos(df_quarentena)
    max_motivo = max(motivos.values()) if motivos else 0
    linhas_motivos = "".join(
        f"<tr><td>{html.escape(campo)}</td><td>{qtd}</td>"
        f"<td>{_barra_html(qtd, max_motivo, '#c0392b')}</td></tr>"
        for campo, qtd in motivos.items()
    ) or "<tr><td colspan='3'>Nenhum registro rejeitado nesta execucao.</td></tr>"

    historico = _ler_historico()
    if not historico.empty:
        max_taxa = max(historico["taxa_erro"].max(), taxa, 1.0)
        linhas_historico = "".join(
            f"<tr><td>{html.escape(str(row['timestamp']))}</td>"
            f"<td>{int(row['total'])}</td><td>{int(row['validos'])}</td>"
            f"<td>{int(row['quarentena'])}</td>"
            f"<td>{row['taxa_erro']:.1f}%{_barra_html(row['taxa_erro'], max_taxa, '#2d6cdf')}</td></tr>"
            for _, row in historico.iterrows()
        )
    else:
        linhas_historico = "<tr><td colspan='5'>Ainda nao ha' historico de execucoes anteriores.</td></tr>"

    gerado_em = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    conteudo = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Relatorio de Qualidade de Dados</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif;
          background:#f4f6f8; color:#1c1c1c; margin:0; padding:32px; }}
  .container {{ max-width:900px; margin:0 auto; }}
  h1 {{ font-size:1.5rem; margin-bottom:4px; }}
  .subtitulo {{ color:#666; margin-top:0; margin-bottom:24px; }}
  .cards {{ display:flex; gap:16px; flex-wrap:wrap; margin-bottom:28px; }}
  .card {{ background:#fff; border-radius:10px; padding:16px 20px; flex:1;
           min-width:150px; box-shadow:0 1px 3px rgba(0,0,0,0.08); }}
  .card .valor {{ font-size:1.8rem; font-weight:700; }}
  .card .rotulo {{ color:#666; font-size:0.85rem; text-transform:uppercase; }}
  .status {{ display:inline-block; padding:2px 10px; border-radius:999px;
             color:#fff; font-size:0.75rem; font-weight:600; margin-top:6px; }}
  table {{ width:100%; border-collapse:collapse; background:#fff; border-radius:10px;
           overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.08); margin-bottom:28px; }}
  th, td {{ text-align:left; padding:10px 14px; border-bottom:1px solid #eee; font-size:0.9rem; }}
  th {{ background:#fafafa; color:#555; }}
  .barra-fundo {{ background:#f0f0f0; border-radius:4px; height:8px; width:120px; }}
  .barra {{ height:8px; border-radius:4px; }}
  .rodape {{ color:#999; font-size:0.8rem; text-align:center; margin-top:24px; }}
</style>
</head>
<body>
<div class="container">
  <h1>Relatorio de Qualidade de Dados</h1>
  <p class="subtitulo">Gerado em {gerado_em}</p>

  <div class="cards">
    <div class="card"><div class="valor">{total}</div><div class="rotulo">Registros processados</div></div>
    <div class="card"><div class="valor">{ok}</div><div class="rotulo">Validos</div></div>
    <div class="card"><div class="valor">{bad}</div><div class="rotulo">Em quarentena</div></div>
    <div class="card">
      <div class="valor">{taxa:.1f}%</div>
      <div class="rotulo">Taxa de erro (limite {LIMITE_ALERTA_ERROS:.0f}%)</div>
      <div class="status" style="background:{status_cor};">{status_texto}</div>
    </div>
  </div>

  <h2>Principais motivos de rejeicao</h2>
  <table>
    <tr><th>Campo</th><th>Ocorrencias</th><th></th></tr>
    {linhas_motivos}
  </table>

  <h2>Tendencia das ultimas execucoes</h2>
  <table>
    <tr><th>Quando</th><th>Total</th><th>Validos</th><th>Quarentena</th><th>Taxa de erro</th></tr>
    {linhas_historico}
  </table>

  <p class="rodape">Pipeline ETL de Qualidade de Dados</p>
</div>
</body>
</html>"""

    ARQ_RELATORIO.write_text(conteudo, encoding="utf-8")
    logger.info("Relatorio: relatorio de qualidade gerado em %s", ARQ_RELATORIO)
    return ARQ_RELATORIO
