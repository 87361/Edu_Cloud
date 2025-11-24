from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False  # Allow case-insensitive env var matching

settings = Settings()
