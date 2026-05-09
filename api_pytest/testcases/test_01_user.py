import requests

def test_login_success(env_urls):
    """测试正常的登录流程并验证 Token 结构"""
    url = f"{env_urls['user']}/login"
    payload = {"username": "pytest_admin", "password": "password_123"}
    
    response = requests.post(url, data=payload, timeout=5)
    
    # 原生 assert 语法，失败时会自动打印 response.status_code 的实际值
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(env_urls):
    """测试密码错误的异常分支"""
    url = f"{env_urls['user']}/login"
    payload = {"username": "pytest_admin", "password": "wrong_password"}
    
    response = requests.post(url, data=payload, timeout=5)
    
    # 预期应被拒绝（通常为 400 或 401）
    assert response.status_code in [400, 401]