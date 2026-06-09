import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "sport_color_db"
    
    # Allows overriding with a single URL string
    DATABASE_URL: str | None = None
    
    # JWT Auth settings
    JWT_SECRET: str = "supersecretjwtkeychangeinproduction1234567890"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Use pydantic-settings to read from .env if present
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Construct standard MySQL url using pymysql
        pwd = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return f"mysql+pymysql://{self.DB_USER}{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
