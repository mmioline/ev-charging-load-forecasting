import requests

def test_lstm_prediction_positive_load(env_urls):
    """验证深度学习模型预测的负荷值具有物理合理性（非负数）"""
    # 假设上一步创建的站点 ID 为 1
    station_id = 1
    url = f"{env_urls['forecast']}/predict/{station_id}"
    
    response = requests.get(url, timeout=10)
    
    assert response.status_code == 200
    data = response.json()
    
    # 校验 AI 模型特有字段
    assert "predicted_load_kwh" in data
    assert "model_type" in data
    
    # 断言负荷预测值大于等于 0
    load_value = data["predicted_load_kwh"]
    assert load_value >= 0, f"严重异常：LSTM 预测出了负数负荷 ({load_value})"