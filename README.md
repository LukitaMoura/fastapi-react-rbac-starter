# 🔐 FastAPI + React RBAC Starter

Base full stack para **sistemas internos corporativos**: autenticação JWT, controle de acesso por permissão (RBAC), fluxo de status controlado, trilha de auditoria e o ciclo de sessão completo no navegador. Vem com um domínio de exemplo pronto: uma **fila de chamados**.

É a versão aberta e genérica do padrão de arquitetura que criei e uso em **5 sistemas em produção** na empresa onde trabalho: financeiro, operacional, RH/Facilities, gestão de ativos e um portal de dados. Cada sistema novo nasce deste núcleo, em vez de reinventar login, permissões e layout.

## O que vem pronto

| Camada | Recurso |
|---|---|
| **Auth** | Login com JWT, hash bcrypt, troca de senha, flag "precisa trocar senha" |
| **RBAC** | `Usuário ⇄ Perfil ⇄ Permissão` (N:N). As rotas checam **chaves de permissão**, nunca nomes de perfil |
| **Workflow** | Máquina de estados do chamado, com transições válidas definidas num único lugar |
| **Visibilidade** | Quem não tem `chamados.ver_todos` só enxerga os próprios chamados; o chamado de outra pessoa responde 404, não 403 |
| **Auditoria** | Toda ação administrativa e de negócio registra quem, o quê, qual registro e quando |
| **Sessão** | 3 camadas: `sessionStorage` (fechar a aba encerra), logout após 30 min de inatividade e expiração do JWT (8h) |
| **UI** | Menu e rotas filtrados pela mesma chave de permissão do backend; layout responsivo |
| **Infra** | SQLite para desenvolvimento, MySQL em produção (pool com timeouts), `.htaccess` para SPA e cache |

## Rodando

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m app.seed                       # perfis + 4 usuários de demonstração
uvicorn app.main:app --reload            # http://127.0.0.1:8000/docs

# Frontend
cd frontend
npm install
npm run dev                              # http://localhost:5173 (proxy /api → :8000)
```

Contas de demonstração (senha `demo12345`): `admin@`, `gestor@`, `analista@` e `solicitante@exemplo.com`. Entre com cada uma e veja o menu, as ações e os dados mudarem conforme a permissão.

## Testes

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v      # 25 testes
```

Os testes cobrem login, mensagem de erro que não revela quais e-mails existem, token adulterado (401), falta de permissão (403), **permissão retirada valendo sem relogar**, usuário desativado perdendo acesso na hora, visibilidade por dono, máquina de estados, transição inválida, filtros, paginação, busca com payload de SQL injection e auditoria.

## Arquitetura

```
Navegador ──HTTPS──▶ Apache/Nginx ──┬── /        → SPA estática (frontend/dist)
                                    └── /api/*   → uvicorn 127.0.0.1 (nunca exposto)
                                                     │
                                         FastAPI ── require_permission("chave")
                                                     │
                                         SQLAlchemy 2 ──▶ MySQL / SQLite
```

```
backend/app/
├── main.py         app, CORS, routers sob /api
├── config.py       settings via env (pydantic-settings)
├── database.py     engine com pre_ping + timeouts para banco remoto
├── models.py       RBAC + Chamado + Histórico + Auditoria
├── security.py     bcrypt, JWT, get_current_user, require_permission()
├── workflow.py     máquina de estados (fonte única das transições)
├── audit.py        registrar() — entra na mesma transação da ação
├── seed.py         permissões, perfis e usuários de demo (idempotente)
└── routers/        auth · admin · chamados

frontend/src/
├── lib/api.js              fetch autenticado + tratamento de 401
├── context/AuthContext.jsx sessão + pode("chave")
├── hooks/useIdleLogout.js  logout por inatividade
├── components/ProtectedRoute.jsx
├── layouts/InternalLayout.jsx  sidebar filtrada por permissão
└── pages/                  Login · Início · Chamados · Detalhe · Admin · Auditoria
```

## Decisões que vieram da produção

Cada uma destas regras saiu de um problema real que enfrentei nos sistemas em produção:

- **Permissões lidas do banco a cada requisição**, não do token. Na primeira versão, elas viajavam dentro do JWT, e uma permissão retirada só valia quando o usuário relogava.
- **`sessionStorage` em vez de `localStorage`**. Em máquina compartilhada, o próximo usuário abria o sistema já logado na conta do anterior.
- **`pool_pre_ping` + `read_timeout`** no MySQL remoto. Sem eles, uma conexão ociosa derrubada pelo firewall deixava a tela "carregando para sempre" até o usuário apertar F5.
- **Rotas literais antes de `/{id}`**. Sem essa ordem, `/chamados/dashboard` era interpretado como id e respondia 422.
- **Gate da UI com a mesma chave do endpoint**. Quando divergiam, o usuário via um botão e recebia 403 ao clicar.
- **`bcrypt` direto, sem `passlib`**. O `passlib` quebra com versões novas do bcrypt no Python 3.12+.
- **Nenhum segredo fixo no código**. Sem `JWT_SECRET`, o app gera um segredo aleatório e emite um alerta no log.

## Stack

**Backend:** Python 3.11+ · FastAPI · SQLAlchemy 2 · Pydantic v2 · PyJWT · bcrypt · pytest
**Frontend:** React 19 · Vite · Tailwind CSS 4 · React Router 7 · lucide-react
