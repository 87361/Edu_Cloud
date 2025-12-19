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
    
    # 服务器配置
    host: str = "0.0.0.0"  # 监听地址，0.0.0.0 表示所有网络接口
    port: int = 5000  # 监听端口
    debug: bool = False  # 生产环境应设为 False
    
    # CORS 配置
    cors_origins: str = "*"  # 允许的来源，生产环境应设置为具体域名，如 "https://example.com,https://www.example.com"
    cors_supports_credentials: bool = True  # 是否支持 credentials


settings = Settings()
