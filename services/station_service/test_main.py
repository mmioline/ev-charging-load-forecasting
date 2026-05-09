import pytest
from httpx import ASGITransport, AsyncClient
from .main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.anyio
async def test_product_flow(client):
    # 模拟一个有效的 Token (实际测试中应通过 user_service 获取，此处演示流程)
    # 注意：在集成测试中，我们通常需要一个 Mock Token 或者预先运行登录
    headers = {"Authorization": "Bearer MOCK_TOKEN_LOGIC"}
    
    # 1. 测试创建商品
    product_data = {
        "name": "测试商品",
        "description": "自动化测试描述",
        "price": 99.9,
        "stock": 100
    }
    # 此处假设你已有一个有效的 Token 
    # res = await client.post("/products", json=product_data, headers=headers)
    # assert res.status_code in [200, 401] # 401 是因为 MOCK_TOKEN 会失效
    
    # 2. 测试匿名访问（应被拦截）
    anon_res = await client.get("/products")
    assert anon_res.status_code == 401