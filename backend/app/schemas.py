from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Prioridade = Literal["baixa", "media", "alta", "critica"]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ── Auth ────────────────────────────────────────────────────────────────
class LoginIn(BaseModel):
    email: EmailStr
    senha: str


class UsuarioResumo(ORM):
    id: int
    nome: str
    email: EmailStr


class UsuarioOut(UsuarioResumo):
    ativo: bool
    precisa_trocar_senha: bool
    ultimo_acesso: datetime | None
    perfis: list["PerfilResumo"]
    permissoes: list[str]

    @field_validator("permissoes", mode="before")
    @classmethod
    def _ordenar(cls, v):
        return sorted(v)


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


class TrocarSenhaIn(BaseModel):
    senha_atual: str
    nova_senha: str = Field(min_length=8)


# ── Admin ───────────────────────────────────────────────────────────────
class PermissaoOut(ORM):
    id: int
    chave: str
    descricao: str


class PerfilResumo(ORM):
    id: int
    nome: str


class PerfilOut(PerfilResumo):
    descricao: str
    permissoes: list[PermissaoOut]


class PerfilIn(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    descricao: str = ""
    permissao_ids: list[int] = []


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha_inicial: str = Field(min_length=8)
    perfil_ids: list[int] = []


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    ativo: bool | None = None
    perfil_ids: list[int] | None = None


# ── Chamados ────────────────────────────────────────────────────────────
class ChamadoCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=200)
    descricao: str = ""
    categoria: str = Field(min_length=2, max_length=60)
    prioridade: Prioridade = "media"


class TransicaoIn(BaseModel):
    status: str
    comentario: str = ""


class AtribuirIn(BaseModel):
    responsavel_id: int


class HistoricoOut(ORM):
    status_de: str | None
    status_para: str
    comentario: str
    criado_em: datetime
    usuario: UsuarioResumo


class ChamadoOut(ORM):
    id: int
    titulo: str
    descricao: str
    categoria: str
    prioridade: str
    status: str
    criado_em: datetime
    atualizado_em: datetime
    solicitante: UsuarioResumo
    responsavel: UsuarioResumo | None


class ChamadoDetalhe(ChamadoOut):
    historico: list[HistoricoOut]
    transicoes_possiveis: list[str]


class Pagina(BaseModel):
    total: int
    itens: list[ChamadoOut]


class AuditoriaOut(ORM):
    id: int
    acao: str
    entidade: str
    entidade_id: int | None
    detalhe: str
    criado_em: datetime
    usuario: UsuarioResumo | None


class DashboardOut(BaseModel):
    por_status: dict[str, int]
    por_prioridade: dict[str, int]
    abertos_ha_mais_de_7_dias: int


UsuarioOut.model_rebuild()
