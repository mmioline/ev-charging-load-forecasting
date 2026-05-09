# api_pytest/conftest.py
import pytest
import requests

@pytest.fixture(scope="session")
def env_urls():
    """定义微服务基础路由地址"""
    return {
        "user": "http://127.0.0.1:8000",
        "station": "http://127.0.0.1:8001",
        "forecast": "http://127.0.0.1:8003"
    }

@pytest.fixture(scope="session")
def auth_headers(env_urls):
    """
    自动化鉴权夹具：
    1. 确保测试用户存在。
    2. 获取 JWT Token 并返回标准 Headers。
    """
    user_url = env_urls["user"]
    test_user = {"username": "pytest_admin", "password": "password_123"}
    
    # 步骤 1: 尝试注册用户
    # 使用 json=payload 发送 JSON 格式数据进行注册
    reg_payload = {
        "username": test_user["username"], 
        "email": "pytest_admin@ev.com", 
        "password": test_user["password"]
    }
    reg_response = requests.post(f"{user_url}/register", json=reg_payload, timeout=5)
    
    # 如果注册失败且不是因为“用户已存在”，则输出调试信息
    if reg_response.status_code != 200:
        # 很多时候 400 是因为用户已存在，这在测试中是可以接受的
        print(f"\n[DEBUG] 注册状态码: {reg_response.status_code}, 详情: {reg_response.text}")
    
    # 步骤 2: 执行登录获取 Token
    # 注意：FastAPI 登录通常要求 Form Data 格式，所以使用 data=test_user
    login_response = requests.post(f"{user_url}/login", data=test_user, timeout=5)
    
    if login_response.status_code != 200:
        # 如果登录失败（返回 400/401），强制打印错误原因，方便定位是密码错还是用户不存在
        print(f"\n[DEBUG] 登录失败! 状态码: {login_response.status_code}, 错误内容: {login_response.text}")
        pytest.fail("无法获取鉴权 Token，后续业务测试将无法进行。")
    
    token = login_response.json().get("access_token")
    
    # 返回标准的请求头
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }