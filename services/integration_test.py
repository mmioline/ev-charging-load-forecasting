import pytest
import httpx
import random
import asyncio

# 定义各服务的基础 URL (指向宿主机映射的端口)
USER_SERVICE_URL = "http://localhost:8000"
STATION_SERVICE_URL = "http://localhost:8001"

@pytest.mark.anyio
async def test_full_ev_workflow():
    async with httpx.AsyncClient() as client:
        # --- 1. 注册新用户 ---
        test_id = random.randint(1000, 9999)
        username = f"tester_{test_id}"
        user_payload = {
            "username": username,
            "email": f"{username}@example.com",
            "password": "password123"
        }
        
        reg_res = await client.post(f"{USER_SERVICE_URL}/register", json=user_payload)
        assert reg_res.status_code == 200, f"注册失败: {reg_res.text}"
        print(f"\n[Step 1] 用户 {username} 注册成功")

        # --- 2. 登录获取 Token ---
        login_data = {
            "username": username,
            "password": "password123"
        }
        # 注意：OAuth2 登录接口通常使用表单数据 (data) 而非 JSON
        login_res = await client.post(f"{USER_SERVICE_URL}/login", data=login_data)
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"[Step 2] 登录成功，获取 Token: {token[:10]}...")

        # --- 3. 使用 Token 创建充电站 ---
        station_payload = {
            "name": f"测试充电站_{test_id}",
            "location": "集成测试路1号",
            "capacity": 150.0,
            "slots": 20
        }
        create_res = await client.post(
            f"{STATION_SERVICE_URL}/stations", 
            json=station_payload, 
            headers=headers
        )
        assert create_res.status_code == 200, f"创建站点失败: {create_res.text}"
        station_id = create_res.json()["id"]
        print(f"[Step 3] 充电站创建成功，ID: {station_id}")

        # --- 4. 验证站点是否创建成功 (查询) ---
        # 我们可以通过获取所有站点列表，验证刚才创建的 ID 是否在其中
        get_res = await client.get(f"{STATION_SERVICE_URL}/stations", headers=headers)
        assert get_res.status_code == 200
        stations = get_res.json()
        
        # 检查返回的列表中是否包含刚才创建的 ID
        found = any(s["id"] == station_id for s in stations)
        assert found, f"在站点列表中未找到刚创建的站点 ID: {station_id}"
        print(f"[Step 4] 验证成功：站点 {station_id} 已存在于系统中")