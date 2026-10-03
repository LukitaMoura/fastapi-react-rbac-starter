from app.seed import SENHA_DEMO


def test_login_devolve_token_e_permissoes(client):
    r = client.post("/api/auth/login", json={"email": "analista@exemplo.com", "senha": SENHA_DEMO})
    assert r.status_code == 200
    body = r.json()
    assert body["access_token"]
    assert "chamados.tratar" in body["usuario"]["permissoes"]
    assert "admin.gerenciar" not in body["usuario"]["permissoes"]


def test_login_com_senha_errada_nao_revela_se_email_existe(client):
    errada = client.post("/api/auth/login", json={"email": "analista@exemplo.com", "senha": "x" * 9})
    inexistente = client.post("/api/auth/login", json={"email": "ninguem@exemplo.com", "senha": "x" * 9})
    assert errada.status_code == inexistente.status_code == 401
    assert errada.json() == inexistente.json()


def test_sem_token_retorna_401(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/chamados").status_code == 401


def test_token_adulterado_retorna_401(client, login):
    headers = login("admin@exemplo.com")
    headers["Authorization"] += "x"
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_sem_permissao_retorna_403(client, login):
    headers = login("solicitante@exemplo.com")
    r = client.get("/api/admin/usuarios", headers=headers)
    assert r.status_code == 403
    assert "admin.gerenciar" in r.json()["detail"]


def test_permissao_retirada_vale_sem_relogar(client, login):
    admin = login("admin@exemplo.com")
    analista = login("analista@exemplo.com")
    assert client.get("/api/chamados/dashboard", headers=analista).status_code == 200

    usuarios = client.get("/api/admin/usuarios", headers=admin).json()
    analista_id = next(u["id"] for u in usuarios if u["email"] == "analista@exemplo.com")
    perfis = client.get("/api/admin/perfis", headers=admin).json()
    solicitante_id = next(p["id"] for p in perfis if p["nome"] == "Solicitante")
    client.patch(f"/api/admin/usuarios/{analista_id}", json={"perfil_ids": [solicitante_id]}, headers=admin)

    # mesmo token de antes, mas a permissão é lida do banco a cada request
    me = client.get("/api/auth/me", headers=analista).json()
    assert "chamados.tratar" not in me["permissoes"]


def test_usuario_desativado_perde_acesso_imediatamente(client, login):
    admin = login("admin@exemplo.com")
    solicitante = login("solicitante@exemplo.com")
    usuarios = client.get("/api/admin/usuarios", headers=admin).json()
    sid = next(u["id"] for u in usuarios if u["email"] == "solicitante@exemplo.com")
    client.patch(f"/api/admin/usuarios/{sid}", json={"ativo": False}, headers=admin)
    assert client.get("/api/auth/me", headers=solicitante).status_code == 401


def test_admin_nao_pode_se_desativar(client, login):
    admin = login("admin@exemplo.com")
    me = client.get("/api/auth/me", headers=admin).json()
    r = client.patch(f"/api/admin/usuarios/{me['id']}", json={"ativo": False}, headers=admin)
    assert r.status_code == 400


def test_criar_usuario_e_email_duplicado(client, login):
    admin = login("admin@exemplo.com")
    novo = {"nome": "Novo", "email": "Novo@Exemplo.com", "senha_inicial": "senhaforte1"}
    r = client.post("/api/admin/usuarios", json=novo, headers=admin)
    assert r.status_code == 201
    assert r.json()["email"] == "novo@exemplo.com"
    assert r.json()["precisa_trocar_senha"] is True
    assert client.post("/api/admin/usuarios", json=novo, headers=admin).status_code == 409


def test_trocar_senha(client, login):
    headers = login("solicitante@exemplo.com")
    r = client.post("/api/auth/trocar-senha", json={"senha_atual": SENHA_DEMO, "nova_senha": "novasenha123"},
                    headers=headers)
    assert r.status_code == 204
    ok = client.post("/api/auth/login", json={"email": "solicitante@exemplo.com", "senha": "novasenha123"})
    assert ok.status_code == 200
