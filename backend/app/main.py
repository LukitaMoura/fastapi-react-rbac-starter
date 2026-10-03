from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import admin, auth, chamados


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Em produção, prefira migrations versionadas (Alembic) a create_all
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="FastAPI + React RBAC Starter",
    description="Autenticação JWT, controle de acesso por permissão, fluxo de status e auditoria.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tudo sob /api: em produção o proxy reverso (Apache/Nginx) encaminha /api → uvicorn
for router in (auth.router, admin.router, chamados.router):
    app.include_router(router, prefix="/api")


@app.get("/api/health", tags=["infra"])
def health():
    return {"status": "ok"}
