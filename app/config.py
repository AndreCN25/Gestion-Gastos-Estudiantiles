from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str = ""
    database_url: str = "sqlite:///./cuentaclara.db"
    access_token_minutes: int = 60
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    admin_email: str = ""
    admin_password: str = ""
    cors_origins: str = "http://127.0.0.1:8000,http://localhost:8000"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
