from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .database import get_db

_bearer = HTTPBearer(auto_error=False)


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode(), senha_hash.encode())
    except ValueError:  # hash malformado no banco
        return False


def criar_token(usuario: models.Usuario) -> str:
    # O exp do JWT é sempre em UTC: a biblioteca compara em UTC
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(usuario.id), "exp": exp}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    cred: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> models.Usuario:
    nao_autorizado = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Sessão inválida ou expirada.", headers={"WWW-Authenticate": "Bearer"}
    )
    if cred is None:
        raise nao_autorizado
    try:
        payload = jwt.decode(cred.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise nao_autorizado
    usuario = db.get(models.Usuario, usuario_id)
    if usuario is None or not usuario.ativo:
        raise nao_autorizado
    return usuario


def require_permission(chave: str):
    """Dependency factory: libera a rota só para quem tem a permissão `chave`.

    As permissões são lidas do banco a cada requisição (e não do token), então
    uma permissão retirada vale na hora, sem esperar o usuário relogar.
    """

    def dependencia(usuario: models.Usuario = Depends(get_current_user)) -> models.Usuario:
        if chave not in usuario.permissoes:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Permissão necessária: {chave}")
        return usuario

    return dependencia
