from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


def make_engine(url: str):
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    # Banco remoto: sem timeout de socket, uma conexão ociosa derrubada pelo
    # firewall trava a requisição para sempre ("carrega infinito"). O
    # read_timeout faz o pre_ping falhar rápido e o pool troca a conexão.
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=280,
        connect_args={"connect_timeout": 10, "read_timeout": 60, "write_timeout": 60},
    )


engine = make_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
