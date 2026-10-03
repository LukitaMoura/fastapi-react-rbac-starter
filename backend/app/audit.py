from sqlalchemy.orm import Session

from . import models


def registrar(db: Session, usuario: models.Usuario | None, acao: str, entidade: str,
              entidade_id: int | None = None, detalhe: str = "") -> None:
    """Adiciona uma linha à trilha de auditoria. Quem chama faz o commit,
    para que a ação e o registro dela entrem (ou falhem) juntos."""
    db.add(models.Auditoria(
        usuario_id=usuario.id if usuario else None,
        acao=acao,
        entidade=entidade,
        entidade_id=entidade_id,
        detalhe=detalhe,
    ))
