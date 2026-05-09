import unittest
import requests

class TestEVForecasting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 对应 docker-compose 中的端口 8003
        cls.base_url = "http://127.0.0.1:8003"
        cls.headers = {"Content-Type": "application/json"}

    def test_get_prediction_success(self):
        """测试 LSTM 负荷预测接口是否返回有效结果"""
        url = f"{self.base_url}/predict/1"  # 假设测试 station_id 为 1
        
        try:
            # 增加超时处理以增强鲁棒性
            r = requests.get(url, headers=self.headers, timeout=10)
            self.assertEqual(r.status_code, 200)
            
            data = r.json()
            # 验证返回字段结构
            self.assertIn("station_id", data)
            self.assertIn("predicted_load_kwh", data)
            self.assertIn("model_type", data)
            
            # 验证业务逻辑：预测负荷应为正数
            self.assertGreaterEqual(data["predicted_load_kwh"], 0)
            print(f"预测结果：{data['predicted_load_kwh']} kWh")
            
        except requests.exceptions.RequestException as e:
            self.fail(f"接口连接失败: {e}")

    def test_prediction_invalid_station(self):
        """测试非法站点 ID 的异常处理"""
        url = f"{self.base_url}/predict/9999"
        r = requests.get(url, timeout=5)
        # 根据 FastAPI 定义，未找到资源应返回 404
        self.assertEqual(r.status_code, 404)