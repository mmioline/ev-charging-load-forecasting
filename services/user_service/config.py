import os  # 新增：导入 os 模块以支持路径处理
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 数据库连接配置
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/ev_charging"
    # JWT 加密配置
    SECRET_KEY: str = "your-super-secret-key-for-ev-charging"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 自动读取根目录的 .env 文件
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
