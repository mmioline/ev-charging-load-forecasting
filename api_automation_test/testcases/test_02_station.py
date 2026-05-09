import unittest
import requests

class TestStationFlow(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:8001"
        # 实际工程中，这里可以通过某个配置文件或全局单例读取 Token
        self.headers = {"Authorization": "Bearer 填入刚才提取的_token"}

    def test_create_station_unauthorized(self):
        """异常测试：不带 Token 创建站点应被拒绝"""
        url = f"{self.base_url}/stations"
        payload = {"name": "非法站点", "capacity": 100, "slots": 5}
        r = requests.post(url, json=payload)
        self.assertEqual(r.status_code, 401)

    def test_create_station_success(self):
        """正常测试：带合法 Token 创建站点"""
        url = f"{self.base_url}/stations"
        payload = {"name": "南山科技园测试站", "capacity": 500, "slots": 20}
        r = requests.post(url, json=payload, headers=self.headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["name"], "南山科技园测试站")