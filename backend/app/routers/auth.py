from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audit, models, schemas
from ..database import get_db
from ..security import criar_token, get_current_user, hash_senha, verificar_senha

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.LoginOut)
def login(dados: schemas.LoginIn, db: Session = Depends(get_db)):
    usuario = db.scalar(select(models.Usuario).where(models.Usuario.email == dados.email.lower()))
    # Mesma mensagem para e-mail inexistente e senha errada: não revela quais e-mails existem
    if usuario is None or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha incorretos.")
    if not usuario.ativo:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuário desativado.")

    usuario.ultimo_acesso = datetime.now()
    audit.registrar(db, usuario, "login", "usuario", usuario.id)
    db.commit()
    return {"access_token": criar_token(usuario), "usuario": usuario}


@router.get("/me", response_model=schemas.UsuarioOut)
def me(usuario: models.Usuario = Depends(get_current_user)):
    return usuario


@router.post("/trocar-senha", status_code=status.HTTP_204_NO_CONTENT)
def trocar_senha(dados: schemas.TrocarSenhaIn, db: Session = Depends(get_db),
                 usuario: models.Usuario = Depends(get_current_user)):
    if not verificar_senha(dados.senha_atual, usuario.senha_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Senha atual incorreta.")
    usuario.senha_hash = hash_senha(dados.nova_senha)
    usuario.precisa_trocar_senha = False
    audit.registrar(db, usuario, "trocar_senha", "usuario", usuario.id)
    db.commit()
