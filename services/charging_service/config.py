from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.security import OAuth2PasswordBearer
import os

class Settings(BaseSettings):
    # 数据库配置：从环境变量读取，若无则使用默认
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/intelli_shop"
    STATION_SERVICE_URL: str = "http://localhost:8001"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 安全加密：必须与所有服务对齐
    SECRET_KEY: str = "your-super-secret-key-for-intellishop"
    ALGORITHM: str = "HS256"
    
    # 令牌获取地址（指向用户服务）
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/login")


    model_config = SettingsConfigDict(
    # 动态定位到根目录的 .env
    env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
    env_file_encoding='utf-8',
    extra='ignore'
)

settings = Settings()
