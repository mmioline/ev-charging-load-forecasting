import unittest
import requests

class TestEVForecasting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 对应 docker-compose.yml 中定义的端口
        cls.base_url = "http://127.0.0.1:8003"

    def test_01_predict_load_success(self):
        """测试正常获取充电站负荷预测结果"""
        station_id = 1
        url = f"{self.base_url}/predict/{station_id}"
        
        # 增加 timeout 预防之前的卡死问题
        response = requests.get(url, timeout=5)
        
        # 验证 HTTP 状态码
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        # 验证返回结构是否符合 schemas.py 定义
        self.assertIn("predicted_load_kwh", data)
        self.assertIsInstance(data["predicted_load_kwh"], float)
        # 业务逻辑断言：预测负荷不能为负数
        self.assertGreaterEqual(data["predicted_load_kwh"], 0)

    def test_02_predict_invalid_station(self):
        """测试不存在的站点 ID 异常返回"""
        url = f"{self.base_url}/predict/99999"
        response = requests.get(url, timeout=5)
        self.assertEqual(response.status_code, 404)