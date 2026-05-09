from pydantic import BaseModel, EmailStr, ConfigDict # 引入 ConfigDict
from typing import Optional

# 注册时，客户端发送的数据格式
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# 返回给客户端的数据格式
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    # Pydantic V2 的新写法，确保从 ORM 模型加载数据
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str