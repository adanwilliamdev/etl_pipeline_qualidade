import src.extract as mod


def _escrever_csv(caminho, linhas):
    caminho.write_text(
        "id_cliente,nome,email,idade,valor_compra,data_registro\n" + linhas,
        encoding="utf-8",
    )


def test_extract_sem_arquivos_retorna_lista_vazia(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "RAW_DIR", tmp_path)
    assert mod.extract() == []


def test_extract_le_um_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "RAW_DIR", tmp_path)
    _escrever_csv(tmp_path / "clientes.csv",
                  "1,Ana Silva,ana@email.com,29,150.50,2026-01-10\n")

    dados = mod.extract()

    assert len(dados) == 1
    assert dados[0]["nome"] == "Ana Silva"
    assert dados[0]["arquivo_origem"] == "clientes.csv"


def test_extract_combina_multiplos_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "RAW_DIR", tmp_path)
    _escrever_csv(tmp_path / "a.csv",
                  "1,Ana Silva,ana@email.com,29,150.50,2026-01-10\n")
    _escrever_csv(tmp_path / "b.csv",
                  "2,Bruno Costa,bruno@email.com,35,89.90,2026-02-15\n")

    dados = mod.extract()

    assert len(dados) == 2
    origens = {d["arquivo_origem"] for d in dados}
    assert origens == {"a.csv", "b.csv"}


def test_extract_ignora_arquivo_corrompido_e_segue_com_os_demais(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "RAW_DIR", tmp_path)
    _escrever_csv(tmp_path / "bom.csv",
                  "1,Ana Silva,ana@email.com,29,150.50,2026-01-10\n")
    (tmp_path / "vazio.csv").write_text("", encoding="utf-8")

    dados = mod.extract()

    assert len(dados) == 1
    assert dados[0]["arquivo_origem"] == "bom.csv"


def test_extract_le_valores_como_texto(tmp_path, monkeypatch):
    """Os valores devem sair como string; e' o schema (Pydantic) quem
    converte e valida tipos, nao a extracao."""
    monkeypatch.setattr(mod, "RAW_DIR", tmp_path)
    _escrever_csv(tmp_path / "clientes.csv",
                  "1,Ana Silva,ana@email.com,29,150.50,2026-01-10\n")

    dados = mod.extract()

    assert dados[0]["idade"] == "29"
    assert dados[0]["valor_compra"] == "150.50"
