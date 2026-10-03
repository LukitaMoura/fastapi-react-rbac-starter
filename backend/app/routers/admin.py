from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit, models, schemas
from ..database import get_db
from ..security import hash_senha, require_permission

router = APIRouter(prefix="/admin", tags=["admin"])
admin_only = require_permission("admin.gerenciar")


def _perfis(db: Session, ids: list[int]) -> list[models.Perfil]:
    perfis = db.scalars(select(models.Perfil).where(models.Perfil.id.in_(ids))).all() if ids else []
    if len(perfis) != len(set(ids)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Perfil inexistente na lista.")
    return list(perfis)


# ── Usuários ────────────────────────────────────────────────────────────
@router.get("/usuarios", response_model=list[schemas.UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db), _: models.Usuario = Depends(admin_only)):
    return db.scalars(select(models.Usuario).order_by(models.Usuario.nome)).all()


@router.post("/usuarios", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED)
def criar_usuario(dados: schemas.UsuarioCreate, db: Session = Depends(get_db),
                  admin: models.Usuario = Depends(admin_only)):
    email = dados.email.lower()
    if db.scalar(select(models.Usuario).where(models.Usuario.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um usuário com este e-mail.")
    usuario = models.Usuario(
        nome=dados.nome,
        email=email,
        senha_hash=hash_senha(dados.senha_inicial),
        precisa_trocar_senha=True,
        perfis=_perfis(db, dados.perfil_ids),
    )
    db.add(usuario)
    db.flush()
    audit.registrar(db, admin, "criar_usuario", "usuario", usuario.id, email)
    db.commit()
    return usuario


@router.patch("/usuarios/{usuario_id}", response_model=schemas.UsuarioOut)
def atualizar_usuario(usuario_id: int, dados: schemas.UsuarioUpdate, db: Session = Depends(get_db),
                      admin: models.Usuario = Depends(admin_only)):
    usuario = db.get(models.Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuário não encontrado.")
    if usuario.id == admin.id and dados.ativo is False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Você não pode desativar a si mesmo.")

    mudancas = []
    if dados.nome is not None:
        usuario.nome = dados.nome
        mudancas.append("nome")
    if dados.ativo is not None:
        usuario.ativo = dados.ativo
        mudancas.append(f"ativo={dados.ativo}")
    if dados.perfil_ids is not None:
        usuario.perfis = _perfis(db, dados.perfil_ids)
        mudancas.append("perfis=" + ",".join(p.nome for p in usuario.perfis))
    audit.registrar(db, admin, "atualizar_usuario", "usuario", usuario.id, "; ".join(mudancas))
    db.commit()
    return usuario


# ── Perfis e permissões ─────────────────────────────────────────────────
@router.get("/permissoes", response_model=list[schemas.PermissaoOut])
def listar_permissoes(db: Session = Depends(get_db), _: models.Usuario = Depends(admin_only)):
    return db.scalars(select(models.Permissao).order_by(models.Permissao.chave)).all()


@router.get("/perfis", response_model=list[schemas.PerfilOut])
def listar_perfis(db: Session = Depends(get_db), _: models.Usuario = Depends(admin_only)):
    return db.scalars(select(models.Perfil).order_by(models.Perfil.nome)).all()


@router.put("/perfis/{perfil_id}", response_model=schemas.PerfilOut)
def salvar_perfil(perfil_id: int, dados: schemas.PerfilIn, db: Session = Depends(get_db),
                  admin: models.Usuario = Depends(admin_only)):
    perfil = db.get(models.Perfil, perfil_id)
    if perfil is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Perfil não encontrado.")
    permissoes = db.scalars(select(models.Permissao).where(models.Permissao.id.in_(dados.permissao_ids))).all()
    perfil.nome, perfil.descricao, perfil.permissoes = dados.nome, dados.descricao, list(permissoes)
    audit.registrar(db, admin, "salvar_perfil", "perfil", perfil.id,
                    ",".join(sorted(p.chave for p in permissoes)))
    db.commit()
    return perfil


@router.get("/auditoria", response_model=list[schemas.AuditoriaOut])
def auditoria(limite: int = 100, db: Session = Depends(get_db),
              _: models.Usuario = Depends(require_permission("auditoria.ver"))):
    stmt = select(models.Auditoria).order_by(models.Auditoria.id.desc()).limit(min(limite, 500))
    return db.scalars(stmt).all()
