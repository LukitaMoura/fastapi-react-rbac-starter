"""Modelos: núcleo RBAC (Usuário ⇄ Perfil ⇄ Permissão), domínio de exemplo (Chamado) e auditoria.

    Usuario ──< usuario_perfis >── Perfil ──< perfil_permissoes >── Permissao

As permissões efetivas de um usuário são a união das permissões de seus perfis.
O acesso no código é sempre checado pela CHAVE da permissão, nunca pelo nome do perfil.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

usuario_perfis = Table(
    "usuario_perfis",
    Base.metadata,
    Column("usuario_id", ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
    Column("perfil_id", ForeignKey("perfis.id", ondelete="CASCADE"), primary_key=True),
)

perfil_permissoes = Table(
    "perfil_permissoes",
    Base.metadata,
    Column("perfil_id", ForeignKey("perfis.id", ondelete="CASCADE"), primary_key=True),
    Column("permissao_id", ForeignKey("permissoes.id", ondelete="CASCADE"), primary_key=True),
)


class Permissao(Base):
    __tablename__ = "permissoes"
    id: Mapped[int] = mapped_column(primary_key=True)
    chave: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    descricao: Mapped[str] = mapped_column(String(255), default="")


class Perfil(Base):
    __tablename__ = "perfis"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)
    descricao: Mapped[str] = mapped_column(String(255), default="")
    permissoes: Mapped[list[Permissao]] = relationship(secondary=perfil_permissoes, lazy="selectin")


class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    ativo: Mapped[bool] = mapped_column(default=True)
    precisa_trocar_senha: Mapped[bool] = mapped_column(default=True)
    ultimo_acesso: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    perfis: Mapped[list[Perfil]] = relationship(secondary=usuario_perfis, lazy="selectin")

    @property
    def permissoes(self) -> set[str]:
        return {p.chave for perfil in self.perfis for p in perfil.permissoes}


class Chamado(Base):
    """Entidade de domínio de exemplo: um chamado com fluxo de status controlado."""

    __tablename__ = "chamados"
    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    descricao: Mapped[str] = mapped_column(Text, default="")
    categoria: Mapped[str] = mapped_column(String(60))
    prioridade: Mapped[str] = mapped_column(String(20), default="media")
    status: Mapped[str] = mapped_column(String(30), default="aberto", index=True)
    solicitante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    responsavel_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    solicitante: Mapped[Usuario] = relationship(foreign_keys=[solicitante_id], lazy="joined")
    responsavel: Mapped[Usuario | None] = relationship(foreign_keys=[responsavel_id], lazy="joined")
    historico: Mapped[list["HistoricoChamado"]] = relationship(
        back_populates="chamado", order_by="HistoricoChamado.criado_em", cascade="all, delete-orphan"
    )


class HistoricoChamado(Base):
    __tablename__ = "historico_chamados"
    id: Mapped[int] = mapped_column(primary_key=True)
    chamado_id: Mapped[int] = mapped_column(ForeignKey("chamados.id", ondelete="CASCADE"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    status_de: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status_para: Mapped[str] = mapped_column(String(30))
    comentario: Mapped[str] = mapped_column(Text, default="")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    chamado: Mapped[Chamado] = relationship(back_populates="historico")
    usuario: Mapped[Usuario] = relationship(lazy="joined")


class Auditoria(Base):
    """Trilha de auditoria: quem fez o quê, em qual registro, quando."""

    __tablename__ = "auditoria"
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    acao: Mapped[str] = mapped_column(String(60), index=True)
    entidade: Mapped[str] = mapped_column(String(60))
    entidade_id: Mapped[int | None] = mapped_column(nullable=True)
    detalhe: Mapped[str] = mapped_column(Text, default="")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)

    usuario: Mapped[Usuario | None] = relationship(lazy="joined")
