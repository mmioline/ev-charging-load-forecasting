import pytest
from httpx import ASGITransport, AsyncClient
from .main import app
import random

# 定义测试固件：创建一个异步客户端
@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.anyio
async def test_quality_workflow(client):
    # 1. 健康检查
    health = await client.get("/health")
    assert health.status_code == 200

    # 2. 随机生成测试数据，防止唯一性冲突
    test_suffix = random.randint(1000, 9999)
    user_data = {
        "username": f"user_{test_suffix}",
        "email": f"test_{test_suffix}@example.com",
        "password": "secure_password"
    }

    # 3. 注册测试
    reg_res = await client.post("/register", json=user_data)
    assert reg_res.status_code == 200

    # 4. 登录测试并提取 Token
    login_data = {"username": user_data["username"], "password": user_data["password"]}
    login_res = await client.post("/login", data=login_data) # OAuth2 表单格式
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 5. 身份验证测试
    headers = {"Authorization": f"Bearer {token}"}
    me_res = await client.get("/users/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == user_data["username"]

@pytest.mark.anyio
async def test_unauthorized_access(client):
    """负面测试：验证无 Token 访问受限接口"""
    response = await client.get("/users/me")
    assert response.status_code == 401