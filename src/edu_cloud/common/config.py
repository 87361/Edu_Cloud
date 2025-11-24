from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False  # Allow case-insensitive env var matching
    )
    
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "default_secret_key_change_in_production"
    access_token_expire_minutes: int = 30


settings = Settings()
