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
    assert response.json()["name"] == "Pytest 自动化网点"

def test_create_station_unauthorized(env_urls):
    """反向测试：故意不注入 auth_headers"""
    url = f"{env_urls['station']}/stations"
    payload = {"name": "非法网点", "capacity": 100, "slots": 2}
    
    response = requests.post(url, json=payload, timeout=5)
    
    assert response.status_code == 401