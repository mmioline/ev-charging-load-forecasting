import pytest
from httpx import ASGITransport, AsyncClient
from .main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.anyio
async def test_station_auth_required(client):
    # 模拟一个有效的 Token (实际测试中应通过 user_service 获取，此处演示流程)
    # 注意：在集成测试中，我们通常需要一个 Mock Token 或者预先运行登录
    headers = {"Authorization": "Bearer MOCK_TOKEN_LOGIC"}
    
    # 1. 测试创建充电站
    station_data = {
        "name": "测试充电站",
        "location": "自动化测试路",
        "capacity": 99.9,
        "slots": 10
    }
    # 此处假设你已有一个有效的 Token 
    # res = await client.post("/stations", json=station_data, headers=headers)
    # assert res.status_code in [200, 401] # 401 是因为 MOCK_TOKEN 会失效
    
    # 2. 测试匿名访问（应被拦截）
    anon_res = await client.get("/stations")
    assert anon_res.status_code == 401
