import os  # 新增：导入 os 模块
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.security import OAuth2PasswordBearer

class Settings(BaseSettings):
    # 数据库连接
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/ev_charging"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 安全加密 (必须与 user_service 保持一致)
    SECRET_KEY: str = "your-super-secret-key-for-ev-charging"
    ALGORITHM: str = "HS256"
    
    # 定义 OAuth2 方案
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/login")

    # 自动读取根目录的 .env 文件
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
