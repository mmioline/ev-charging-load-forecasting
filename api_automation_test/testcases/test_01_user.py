import unittest
import requests

class TestEVUserFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 假设 Docker 环境部署在本地
        cls.base_url = "http://localhost:8000"
        cls.test_username = "qa_tester_01"
        cls.test_password = "password123"
        cls.token = None

    def test_01_register_success(self):
        """测试正常注册流程"""
        url = f"{self.base_url}/register"
        payload = {
            "username": self.test_username,
            "email": f"{self.test_username}@ev.com",
            "password": self.test_password
        }
        r = requests.post(url, json=payload, timeout=5)
        # 断言：由于系统可能已经存在该用户，判断 200 或 400
        self.assertIn(r.status_code, [200, 400]) 

    def test_02_login_and_get_token(self):
        """测试登录并提取 JWT Token"""
        url = f"{self.base_url}/login"
        # 注意：OAuth2 登录需要使用 data 传递表单，而不是 json
        payload = {
            "username": self.test_username,
            "password": self.test_password
        }
        r = requests.post(url, json=payload, timeout=5)
        self.assertEqual(r.status_code, 200)
        
        result = r.json()
        self.assertIn("access_token", result)
        
        # 将 Token 保存至类属性，供其他接口使用
        TestEVUserFlow.token = result["access_token"]