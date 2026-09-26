import config


def test_carregar_regras_usa_padrao_quando_arquivo_nao_existe(tmp_path):
    regras = config._carregar_regras(tmp_path / "nao_existe.yaml")
    assert regras == config.REGRAS_PADRAO


def test_carregar_regras_le_valores_customizados(tmp_path):
    arq = tmp_path / "regras.yaml"
    arq.write_text("idade_min: 21\nlimite_alerta_erros: 10\n", encoding="utf-8")

    regras = config._carregar_regras(arq)

    assert regras["idade_min"] == 21
    assert regras["limite_alerta_erros"] == 10
    # chaves nao sobrescritas mantem o padrao
    assert regras["idade_max"] == config.REGRAS_PADRAO["idade_max"]


def test_carregar_regras_ignora_chaves_desconhecidas(tmp_path):
    arq = tmp_path / "regras.yaml"
    arq.write_text("idade_min: 21\nchave_que_nao_existe: 999\n", encoding="utf-8")

    regras = config._carregar_regras(arq)

    assert "chave_que_nao_existe" not in regras
    assert regras["idade_min"] == 21


def test_carregar_regras_arquivo_invalido_usa_padrao(tmp_path, caplog):
    arq = tmp_path / "regras.yaml"
    arq.write_text("isso: [nao fecha a lista\n", encoding="utf-8")

    regras = config._carregar_regras(arq)

    assert regras == config.REGRAS_PADRAO


def test_carregar_regras_conteudo_nao_e_mapeamento_usa_padrao(tmp_path):
    arq = tmp_path / "regras.yaml"
    arq.write_text("- item1\n- item2\n", encoding="utf-8")

    regras = config._carregar_regras(arq)

    assert regras == config.REGRAS_PADRAO
