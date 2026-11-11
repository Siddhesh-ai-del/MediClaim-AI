from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DATABASE_URL: str
    JWT_SECRET: str
    BCRYPT_ROUNDS: int = 12
    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    OCR_PRIMARY: str = "paddleocr"
    OCR_FALLBACK: str = "tesseract"
    CLOUD_OCR_ENABLED: bool = False
    CORS_ORIGINS: str = "http://localhost:3000"
    STORAGE_PATH: str = "./data/uploads"
    STORAGE_BACKEND: str = "local"
    SENTRY_DSN: str = ""
    DEMO_MODE: bool = False
    APP_ENV: str = "dev"
    MAX_UPLOAD_MB: int = 20
    MAX_FILES_PER_CLAIM: int = 10
    ADMIN_EMAIL: str = "admin@demo.med"
    ADMIN_PASSWORD: str = ""
    LOG_LEVEL: str = "info"
    DOCS_ENABLED: bool = True
    ACCESS_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 7

    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()  # type: ignore[call-arg]
