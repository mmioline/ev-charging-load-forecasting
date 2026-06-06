import requests

def test_login_success(env_urls):
    url = f"{env_urls['user']}/login"
    # 确保用户名和密码与之前注册时一致
    payload = {"username": "pytest_admin", "password": "password_123"}

    # FastAPI OAuth2 默认要求 form 格式，requests 使用 data 参数发送即为 form 格式
    response = requests.post(url, data=payload, timeout=5)

    # 如果还是 400，打印 body 看看后端报了什么错
    if response.status_code != 200:
        print(f"登录失败详情: {response.text}")

    assert response.status_code == 200
    

def test_login_wrong_password(env_urls):
    """测试密码错误的异常分支"""
    url = f"{env_urls['user']}/login"
    payload = {"username": "pytest_admin", "password": "wrong_password"}
    
    response = requests.post(url, data=payload, timeout=5)
    
    # 预期应被拒绝（通常为 400 或 401）
    assert response.status_code in [400, 401]