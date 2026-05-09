import os
import pandas as pd
import numpy as np
from sqlalchemy import text
from .database import engine
from sklearn.preprocessing import MinMaxScaler
import torch
from .lstm_model import LSTMForecaster

def fetch_and_prepare_data(station_id: int):
    # 修正：查询充电记录表，统计 kWh 消耗
    query = text("SELECT created_at, kwh_consumed FROM charging_records WHERE station_id = :sid ORDER BY created_at")
    df = pd.read_sql(query, engine, params={"sid": station_id})
    
    if df.empty:
        return None, None

    df['created_at'] = pd.to_datetime(df['created_at'])
    df.set_index('created_at', inplace=True)
    # 关键修改：将 'H' 改为小写的 'h'
    daily_load = df.resample('h').sum().fillna(0) #
    
    scaler = MinMaxScaler(feature_range=(-1, 1))
    data_normalized = scaler.fit_transform(daily_load['kwh_consumed'].values.reshape(-1, 1))
    
    return torch.FloatTensor(data_normalized).view(-1), scaler

def predict_next_day(product_id: int):
    data, scaler = fetch_and_prepare_data(product_id)
    if data is None or len(data) < 7:
        return "数据量不足，无法预测"
    
    model = LSTMForecaster()
    model_path = os.path.join(os.path.dirname(__file__), f"models/product_{product_id}.pth")
    
    # 检查是否有训练好的模型，如果有则加载
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
        print(f"成功加载商品 {product_id} 的预训练模型。")
    else:
        print("未发现预训练模型，使用随机初始化权重（预测结果可能不准）。")

    model.eval()
    with torch.no_grad():
        model.hidden_cell = (torch.zeros(1, 1, model.hidden_layer_size),
                            torch.zeros(1, 1, model.hidden_layer_size))
        # 使用最后 5 天的数据进行预测
        prediction = model(data[-5:])
        
    # 逆归一化回到真实数值
    real_prediction = scaler.inverse_transform(np.array([[prediction.item()]]))[0][0]
    return max(0, round(real_prediction, 2))