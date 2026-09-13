from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://agrigrade:agrigrade@db:5432/agrigrade"
    jwt_secret: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12  # 12 hours
    storage_dir: str = "storage/images"

    class Config:
        env_file = ".env"


settings = Settings()
