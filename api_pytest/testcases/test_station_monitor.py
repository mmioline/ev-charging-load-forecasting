import requests

def test_create_station_success(env_urls, auth_headers):
    """
    依赖注入：auth_headers 会自动在请求前获取到合法的 Token。
    """
    url = f"{env_urls['station']}/stations"
    payload = {
        "name": "Pytest 自动化网点", 
        "capacity": 800,
        "slots": 10
    }
    
    response = requests.post(url, json=payload, headers=auth_headers, timeout=5)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Pytest 自动化网点"
    assert data["status"] == "空闲"
    assert "last_updated_at" in data

def test_update_station_status_success(env_urls, auth_headers):
    create_url = f"{env_urls['station']}/stations"
    create_payload = {
        "name": "Pytest 状态测试站",
        "capacity": 500,
        "slots": 6
    }
    create_response = requests.post(
        create_url,
        json=create_payload,
        headers=auth_headers,
        timeout=5
    )
    assert create_response.status_code == 200
    station_id = create_response.json()["id"]

    status_url = f"{env_urls['station']}/stations/{station_id}/status"
    update_response = requests.put(
        status_url,
        json={"status": "充电中"},
        headers=auth_headers,
        timeout=5
    )

    assert update_response.status_code == 200
    assert update_response.json()["station_id"] == station_id
    assert update_response.json()["status"] == "充电中"

def test_list_available_stations_success(env_urls, auth_headers):
    url = f"{env_urls['station']}/stations/status/available"
    response = requests.get(url, headers=auth_headers, timeout=5)

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_station_unauthorized(env_urls):
    """反向测试：故意不注入 auth_headers"""
    url = f"{env_urls['station']}/stations"
    payload = {"name": "非法网点", "capacity": 100, "slots": 2}
    
    response = requests.post(url, json=payload, timeout=5)
    
    assert response.status_code == 401
