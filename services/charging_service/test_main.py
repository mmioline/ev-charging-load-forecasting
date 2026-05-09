import pytest
from httpx import ASGITransport, AsyncClient
from .main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.anyio
async def test_order_unauthorized(client):
    """验证未授权无法下单"""
    payload = {"product_id": 1, "quantity": 5}
    response = await client.post("/orders", json=payload)
    assert response.status_code == 401