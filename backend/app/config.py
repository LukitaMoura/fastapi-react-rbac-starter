import logging
import secrets

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuração lida de variáveis de ambiente / backend/.env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # SQLite por padrão para rodar sem infraestrutura; em produção use
    # mysql+pymysql://usuario:senha@host:3306/banco
    database_url: str = "sqlite:///./starter.db"

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480  # limite absoluto da sessão (8h)

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @model_validator(mode="after")
    def _segredo(self):
        # Nenhum segredo fixo no código: sem JWT_SECRET, gera um aleatório.
        # Funciona para desenvolvimento, mas os tokens caem a cada reinício.
        if not self.jwt_secret:
            self.jwt_secret = secrets.token_hex(32)
            log.warning("JWT_SECRET não definido: usando segredo temporário (defina no .env em produção)")
        return self


settings = Settings()
