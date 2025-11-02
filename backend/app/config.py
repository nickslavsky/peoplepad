from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    google_client_id: str
    google_client_secret: str
    google_auth_url: str
    google_token_url: str
    google_redirect_uri: str
    openai_key: str
    embedding_service_key: str
    max_embedding_retries: int
    embedding_retry_delay: float
    embedding_model: str
    secret_key: str
    algorithm: str

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@db:5432/{self.postgres_db}"

    @property
    def embedding_service_url(self) -> str:
        return "http://embedding-service:8080/embed"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()