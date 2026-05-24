import pytest
from httpx import ASGITransport, AsyncClient
from .main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.anyio
async def test_charging_record_unauthorized(client):
    """验证未授权无法创建充电记录"""
    payload = {"station_id": 1, "duration_minutes": 30, "kwh_consumed": 12.5}
    response = await client.post("/charging", json=payload)
    assert response.status_code == 401
