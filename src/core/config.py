import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    open_meteo_url: str = field(
        default_factory=lambda: os.getenv(
            "OPEN_METEO_URL",
            "https://api.open-meteo.com/v1/forecast",
        )
    )
    gee_credentials_file: str = field(
        default_factory=lambda: os.getenv("GEE_CREDENTIALS_FILE", "")
    )
    gee_credentials_json: str = field(
        default_factory=lambda: os.getenv("GEE_CREDENTIALS_JSON", "")
    )
    gee_project_id: str | None = field(
        default_factory=lambda: os.getenv("GEE_PROJECT_ID", None)
    )
    gee_collection_name: str = field(
        default_factory=lambda: os.getenv(
            "GEE_COLLECTION_NAME",
            "COPERNICUS/S2_SR_HARMONIZED",
        )
    )
    database_dsn: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_DSN",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/agrotech",
        )
    )
    database_echo: bool = field(
        default_factory=lambda: os.getenv("DATABASE_ECHO", "false").lower() == "true"
    )


settings = Settings()
