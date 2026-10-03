"""Cria permissões, perfis e usuários de demonstração. Idempotente: pode rodar várias vezes.

Uso:  python -m app.seed
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .database import Base, SessionLocal, engine
from .security import hash_senha

PERMISSOES = {
    "chamados.criar": "Abrir chamados",
    "chamados.tratar": "Assumir e mudar o status de chamados",
    "chamados.ver_todos": "Ver chamados de todos os usuários",
    "chamados.atribuir": "Atribuir responsável a um chamado",
    "auditoria.ver": "Consultar a trilha de auditoria",
    "admin.gerenciar": "Gerenciar usuários, perfis e permissões",
}

PERFIS = {
    "Administrador": ("Acesso total", list(PERMISSOES)),
    "Gestor": ("Acompanha a fila e distribui chamados",
               ["chamados.criar", "chamados.tratar", "chamados.ver_todos", "chamados.atribuir", "auditoria.ver"]),
    "Analista": ("Trata chamados da fila", ["chamados.criar", "chamados.tratar", "chamados.ver_todos"]),
    "Solicitante": ("Abre e acompanha os próprios chamados", ["chamados.criar"]),
}

USUARIOS_DEMO = [
    ("Ana Admin", "admin@exemplo.com", "Administrador"),
    ("Gabriel Gestor", "gestor@exemplo.com", "Gestor"),
    ("Alice Analista", "analista@exemplo.com", "Analista"),
    ("Sérgio Solicitante", "solicitante@exemplo.com", "Solicitante"),
]
SENHA_DEMO = "demo12345"


def seed(db: Session, com_usuarios_demo: bool = True) -> None:
    permissoes = {}
    for chave, descricao in PERMISSOES.items():
        p = db.scalar(select(models.Permissao).where(models.Permissao.chave == chave))
        if p is None:
            p = models.Permissao(chave=chave, descricao=descricao)
            db.add(p)
        permissoes[chave] = p

    perfis = {}
    for nome, (descricao, chaves) in PERFIS.items():
        perfil = db.scalar(select(models.Perfil).where(models.Perfil.nome == nome))
        if perfil is None:
            perfil = models.Perfil(nome=nome, descricao=descricao)
            db.add(perfil)
        perfil.permissoes = [permissoes[c] for c in chaves]
        perfis[nome] = perfil

    if com_usuarios_demo:
        for nome, email, perfil in USUARIOS_DEMO:
            if db.scalar(select(models.Usuario).where(models.Usuario.email == email)) is None:
                db.add(models.Usuario(nome=nome, email=email, senha_hash=hash_senha(SENHA_DEMO),
                                      precisa_trocar_senha=False, perfis=[perfis[perfil]]))
    db.commit()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        seed(session)
    print(f"Seed concluído. Usuários de demo com a senha '{SENHA_DEMO}':")
    for _, email, perfil in USUARIOS_DEMO:
        print(f"  {email:28} {perfil}")
