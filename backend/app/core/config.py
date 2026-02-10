from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Secondhand Marketplace API"
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120
    jwt_refresh_expire_minutes: int = 60 * 24 * 14
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    admin_email: str = "admin@example.com"
    admin_password: str = "Admin1234!"
    admin_nickname: str = "market-admin"


settings = Settings()
