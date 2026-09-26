import src.notify as mod


def test_verificar_alerta_nao_envia_webhook_se_nao_configurado(monkeypatch, caplog):
    monkeypatch.setattr(mod, "SLACK_WEBHOOK_URL", None)
    chamadas = []
    monkeypatch.setattr(mod.urllib.request, "urlopen", lambda *a, **k: chamadas.append(1))

    mod.verificar_alerta(total=10, rejeitados=8)  # 80% > limite padrao

    assert chamadas == []


def test_verificar_alerta_envia_webhook_quando_configurado(monkeypatch):
    monkeypatch.setattr(mod, "SLACK_WEBHOOK_URL", "https://hooks.example.com/x")
    chamadas = []
    monkeypatch.setattr(mod.urllib.request, "urlopen", lambda req, timeout=5: chamadas.append(req))

    mod.verificar_alerta(total=10, rejeitados=8)  # 80% > limite padrao

    assert len(chamadas) == 1


def test_verificar_alerta_nao_envia_webhook_quando_taxa_ok(monkeypatch):
    monkeypatch.setattr(mod, "SLACK_WEBHOOK_URL", "https://hooks.example.com/x")
    chamadas = []
    monkeypatch.setattr(mod.urllib.request, "urlopen", lambda req, timeout=5: chamadas.append(req))

    mod.verificar_alerta(total=10, rejeitados=1)  # 10% < limite padrao

    assert chamadas == []
