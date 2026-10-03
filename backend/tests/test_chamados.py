import pytest

from app import workflow


def _abrir(client, headers, titulo="Ar-condicionado sem funcionar"):
    r = client.post("/api/chamados", json={"titulo": titulo, "categoria": "Manutenção", "prioridade": "alta"},
                    headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def test_solicitante_ve_apenas_os_proprios_chamados(client, login):
    solicitante = login("solicitante@exemplo.com")
    gestor = login("gestor@exemplo.com")
    meu = _abrir(client, solicitante, "Meu chamado")
    alheio = _abrir(client, gestor, "Chamado do gestor")

    lista = client.get("/api/chamados", headers=solicitante).json()
    assert [c["id"] for c in lista["itens"]] == [meu["id"]]
    # o chamado alheio responde 404 (e não 403): não revela que existe
    assert client.get(f"/api/chamados/{alheio['id']}", headers=solicitante).status_code == 404

    todos = client.get("/api/chamados", headers=gestor).json()
    assert todos["total"] == 2


def test_fluxo_completo_com_historico_e_responsavel(client, login):
    solicitante = login("solicitante@exemplo.com")
    analista = login("analista@exemplo.com")
    c = _abrir(client, solicitante)
    assert c["status"] == "aberto"
    assert c["transicoes_possiveis"] == ["cancelado", "em_andamento"]

    c = client.post(f"/api/chamados/{c['id']}/transicao", json={"status": "em_andamento"}, headers=analista).json()
    assert c["responsavel"]["email"] == "analista@exemplo.com"  # quem assume vira responsável

    for status in ("aguardando", "em_andamento", "resolvido", "fechado"):
        r = client.post(f"/api/chamados/{c['id']}/transicao",
                        json={"status": status, "comentario": "peça do fornecedor"}, headers=analista)
        assert r.status_code == 200, r.text
    c = r.json()
    assert [h["status_para"] for h in c["historico"]] == [
        "aberto", "em_andamento", "aguardando", "em_andamento", "resolvido", "fechado"]
    assert c["transicoes_possiveis"] == []


def test_transicao_invalida_e_bloqueada(client, login):
    analista = login("analista@exemplo.com")
    c = _abrir(client, analista)
    r = client.post(f"/api/chamados/{c['id']}/transicao", json={"status": "fechado"}, headers=analista)
    assert r.status_code == 400
    assert "aberto → fechado" in r.json()["detail"]


def test_aguardando_exige_comentario(client, login):
    analista = login("analista@exemplo.com")
    c = _abrir(client, analista)
    client.post(f"/api/chamados/{c['id']}/transicao", json={"status": "em_andamento"}, headers=analista)
    r = client.post(f"/api/chamados/{c['id']}/transicao", json={"status": "aguardando"}, headers=analista)
    assert r.status_code == 400


def test_solicitante_nao_pode_mudar_status(client, login):
    solicitante = login("solicitante@exemplo.com")
    c = _abrir(client, solicitante)
    r = client.post(f"/api/chamados/{c['id']}/transicao", json={"status": "em_andamento"}, headers=solicitante)
    assert r.status_code == 403


def test_atribuir_exige_responsavel_que_trata_chamados(client, login):
    gestor = login("gestor@exemplo.com")
    admin = login("admin@exemplo.com")
    c = _abrir(client, gestor)
    usuarios = {u["email"]: u["id"] for u in client.get("/api/admin/usuarios", headers=admin).json()}

    r = client.post(f"/api/chamados/{c['id']}/atribuir",
                    json={"responsavel_id": usuarios["solicitante@exemplo.com"]}, headers=gestor)
    assert r.status_code == 400
    r = client.post(f"/api/chamados/{c['id']}/atribuir",
                    json={"responsavel_id": usuarios["analista@exemplo.com"]}, headers=gestor)
    assert r.json()["responsavel"]["email"] == "analista@exemplo.com"


def test_filtros_busca_e_paginacao(client, login):
    analista = login("analista@exemplo.com")
    for i in range(5):
        _abrir(client, analista, f"Impressora {i}")
    _abrir(client, analista, "Cadeira quebrada")

    r = client.get("/api/chamados", params={"busca": "impressora", "por_pagina": 2, "pagina": 2},
                   headers=analista).json()
    assert r["total"] == 5
    assert len(r["itens"]) == 2


def test_busca_com_caracteres_de_sql_e_segura(client, login):
    analista = login("analista@exemplo.com")
    _abrir(client, analista)
    r = client.get("/api/chamados", params={"busca": "' OR '1'='1"}, headers=analista)
    assert r.status_code == 200
    assert r.json()["total"] == 0


def test_dashboard_conta_por_status(client, login):
    analista = login("analista@exemplo.com")
    c = _abrir(client, analista)
    _abrir(client, analista)
    client.post(f"/api/chamados/{c['id']}/transicao", json={"status": "em_andamento"}, headers=analista)
    d = client.get("/api/chamados/dashboard", headers=analista).json()
    assert d["por_status"]["aberto"] == 1
    assert d["por_status"]["em_andamento"] == 1
    assert set(d["por_status"]) == set(workflow.STATUS)


def test_acoes_ficam_na_auditoria(client, login):
    analista = login("analista@exemplo.com")
    c = _abrir(client, analista)
    client.post(f"/api/chamados/{c['id']}/transicao", json={"status": "em_andamento"}, headers=analista)

    admin = login("admin@exemplo.com")
    acoes = [a["acao"] for a in client.get("/api/admin/auditoria", headers=admin).json()]
    assert {"criar_chamado", "transicao_chamado", "login"} <= set(acoes)
    assert client.get("/api/admin/auditoria", headers=analista).status_code == 403


@pytest.mark.parametrize("de,para,esperado", [
    ("aberto", "em_andamento", True),
    ("aberto", "resolvido", False),
    ("resolvido", "em_andamento", True),
    ("fechado", "aberto", False),
    ("inexistente", "aberto", False),
])
def test_maquina_de_estados(de, para, esperado):
    assert workflow.pode_transitar(de, para) is esperado
