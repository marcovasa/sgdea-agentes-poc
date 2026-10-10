import os
from dataclasses import dataclass, field


def _lista(valor: str) -> list[str]:
    return [v.strip() for v in valor.split(",") if v.strip()]


@dataclass(frozen=True)
class Settings:
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./sgdea.db")
    )
    cors_origins: list[str] = field(default_factory=lambda: _lista(os.getenv("CORS_ORIGINS", "*")))
    seed_demo: bool = field(
        default_factory=lambda: os.getenv("SEED_DEMO", "true").lower() == "true"
    )
    version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "local"))


settings = Settings()
