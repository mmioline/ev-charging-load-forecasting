import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 数据库配置（从根目录 .env 读取）
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/intelli_shop"
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()