"""
Application configuration.

Reads from environment variables (with sensible local-dev defaults) so the same
codebase runs unmodified in:
  - local dev (SQLite, no external services)
  - docker-compose (Postgres, service-name hostnames)
  - a real cloud deployment (env vars injected by the platform)

AI_PROVIDER controls the extraction/commentary layer (see app/ai_commentary.py
and app/ingestion/extract_pdfs.py):
  - "none"   (default): deterministic rule-based extraction + templated commentary.
              Works out of the box with zero external credentials - this is the
              "demo mode" the app ships in.
  - "openai": if OPENAI_API_KEY is set, LLM calls are used to structure ambiguous
              text and to draft board commentary, with the deterministic path
              kept as an automatic fallback if the call fails or no key is present.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Senus Board Report API"
    environment: str = "development"

    database_url: str = "sqlite:///./senus_board_report.db"

    jwt_secret: str = "dev-secret-change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 480

    demo_ceo_email: str = "ceo@senus.com"
    demo_ceo_password: str = "Senus2030!"

    ai_provider: str = "none"  # "none" | "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Absolute path to the repo's data/ directory. Left unset for local dev,
    # where gold_dataset.py/extract_pdfs.py derive it by walking up from this
    # file's location. In Docker the backend's code is copied to /app (with no
    # surrounding "backend/" folder), which sits one directory level shallower
    # than the local layout - so relative traversal gives the wrong answer
    # there. docker-compose.yml sets DATA_DIR=/app/data explicitly instead of
    # relying on that traversal; see app/ingestion/gold_dataset.py.
    data_dir: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
