from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import audit, models, schemas, workflow
from ..database import get_db
from ..security import get_current_user, require_permission

router = APIRouter(prefix="/chamados", tags=["chamados"])

VER_TODOS = "chamados.ver_todos"


def _visiveis(usuario: models.Usuario):
    """Quem não tem `chamados.ver_todos` enxerga apenas os próprios chamados."""
    stmt = select(models.Chamado)
    if VER_TODOS not in usuario.permissoes:
        stmt = stmt.where(models.Chamado.solicitante_id == usuario.id)
    return stmt


def _obter(db: Session, chamado_id: int, usuario: models.Usuario) -> models.Chamado:
    chamado = db.scalar(_visiveis(usuario).where(models.Chamado.id == chamado_id))
    if chamado is None:  # 404 também para chamado alheio: não revela que ele existe
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chamado não encontrado.")
    return chamado


def _detalhe(chamado: models.Chamado) -> dict:
    out = schemas.ChamadoOut.model_validate(chamado).model_dump()
    out["historico"] = [schemas.HistoricoOut.model_validate(h).model_dump() for h in chamado.historico]
    out["transicoes_possiveis"] = workflow.transicoes_possiveis(chamado.status)
    return out


# Rotas literais antes de /{chamado_id}, senão "dashboard" seria lido como id
@router.get("/dashboard", response_model=schemas.DashboardOut)
def dashboard(db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    base = _visiveis(usuario).subquery()
    por_status = dict(db.execute(select(base.c.status, func.count()).group_by(base.c.status)).all())
    por_prioridade = dict(db.execute(select(base.c.prioridade, func.count()).group_by(base.c.prioridade)).all())
    limite = datetime.now() - timedelta(days=7)
    antigos = db.scalar(
        select(func.count()).select_from(base)
        .where(base.c.status.in_(["aberto", "em_andamento", "aguardando"]), base.c.criado_em < limite)
    )
    return {
        "por_status": {s: por_status.get(s, 0) for s in workflow.STATUS},
        "por_prioridade": por_prioridade,
        "abertos_ha_mais_de_7_dias": antigos,
    }


@router.get("", response_model=schemas.Pagina)
def listar(
    status_: str | None = Query(None, alias="status"),
    prioridade: str | None = None,
    busca: str | None = None,
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_user),
):
    stmt = _visiveis(usuario)
    if status_:
        stmt = stmt.where(models.Chamado.status == status_)
    if prioridade:
        stmt = stmt.where(models.Chamado.prioridade == prioridade)
    if busca:
        stmt = stmt.where(models.Chamado.titulo.ilike(f"%{busca}%"))  # parametrizado pelo SQLAlchemy

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    itens = db.scalars(
        stmt.order_by(models.Chamado.id.desc()).offset((pagina - 1) * por_pagina).limit(por_pagina)
    ).unique().all()
    return {"total": total, "itens": itens}


@router.post("", response_model=schemas.ChamadoDetalhe, status_code=status.HTTP_201_CREATED)
def criar(dados: schemas.ChamadoCreate, db: Session = Depends(get_db),
          usuario: models.Usuario = Depends(require_permission("chamados.criar"))):
    chamado = models.Chamado(**dados.model_dump(), solicitante_id=usuario.id)
    chamado.historico.append(models.HistoricoChamado(usuario_id=usuario.id, status_para="aberto",
                                                     comentario="Chamado aberto"))
    db.add(chamado)
    db.flush()
    audit.registrar(db, usuario, "criar_chamado", "chamado", chamado.id, dados.titulo)
    db.commit()
    db.refresh(chamado)
    return _detalhe(chamado)


@router.get("/{chamado_id}", response_model=schemas.ChamadoDetalhe)
def detalhe(chamado_id: int, db: Session = Depends(get_db),
            usuario: models.Usuario = Depends(get_current_user)):
    return _detalhe(_obter(db, chamado_id, usuario))


@router.post("/{chamado_id}/transicao", response_model=schemas.ChamadoDetalhe)
def transicionar(chamado_id: int, dados: schemas.TransicaoIn, db: Session = Depends(get_db),
                 usuario: models.Usuario = Depends(require_permission("chamados.tratar"))):
    chamado = _obter(db, chamado_id, usuario)
    if not workflow.pode_transitar(chamado.status, dados.status):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Transição inválida: {chamado.status} → {dados.status}. "
            f"Possíveis: {', '.join(workflow.transicoes_possiveis(chamado.status)) or 'nenhuma'}",
        )
    if dados.status == "aguardando" and not dados.comentario.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Informe o que está sendo aguardado.")

    de = chamado.status
    chamado.status = dados.status
    if chamado.responsavel_id is None and dados.status == "em_andamento":
        chamado.responsavel_id = usuario.id  # quem assume o chamado vira responsável
    chamado.historico.append(models.HistoricoChamado(
        usuario_id=usuario.id, status_de=de, status_para=dados.status, comentario=dados.comentario))
    audit.registrar(db, usuario, "transicao_chamado", "chamado", chamado.id, f"{de} → {dados.status}")
    db.commit()
    db.refresh(chamado)
    return _detalhe(chamado)


@router.post("/{chamado_id}/atribuir", response_model=schemas.ChamadoDetalhe)
def atribuir(chamado_id: int, dados: schemas.AtribuirIn, db: Session = Depends(get_db),
             usuario: models.Usuario = Depends(require_permission("chamados.atribuir"))):
    chamado = _obter(db, chamado_id, usuario)
    responsavel = db.get(models.Usuario, dados.responsavel_id)
    if responsavel is None or not responsavel.ativo or "chamados.tratar" not in responsavel.permissoes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Responsável precisa ser um usuário ativo que trata chamados.")
    chamado.responsavel_id = responsavel.id
    audit.registrar(db, usuario, "atribuir_chamado", "chamado", chamado.id, responsavel.email)
    db.commit()
    db.refresh(chamado)
    return _detalhe(chamado)
