import os
import pandas as pd
import numpy as np
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
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
    hourly_load = df.resample('h').sum().fillna(0)
    if len(hourly_load) >= 10:
        training_values = hourly_load['kwh_consumed'].values
    else:
        training_values = df['kwh_consumed'].values

    if len(training_values) < 10:
        return None, None
    
    scaler = MinMaxScaler(feature_range=(-1, 1))
    data_normalized = scaler.fit_transform(training_values.reshape(-1, 1))
    
    return torch.FloatTensor(data_normalized).view(-1), scaler

def predict_next_day(product_id: int):
    data, scaler = fetch_and_prepare_data(product_id)
    if data is None or len(data) < 7:
        return "数据量不足，无法预测"
    
    model = LSTMForecaster()
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    model_path = os.path.join(model_dir, f"station_{product_id}.pth")
    legacy_model_path = os.path.join(model_dir, f"product_{product_id}.pth")
    
    # 检查是否有训练好的模型，如果有则加载
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
        print(f"成功加载站点 {product_id} 的预训练模型。")
    elif os.path.exists(legacy_model_path):
        model.load_state_dict(torch.load(legacy_model_path))
        print(f"成功加载站点 {product_id} 的兼容模型。")
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


def predict_station_idle_probability(station_id: int, horizon_hours: int = 1):
    station_query = text("SELECT slots FROM stations WHERE id = :sid")
    try:
        station_df = pd.read_sql(station_query, engine, params={"sid": station_id})
    except SQLAlchemyError:
        return None, "站点数据不可用，无法预测"

    if station_df.empty:
        return None, "站点不存在"

    slots = int(station_df.iloc[0]["slots"] or 0)
    if slots <= 0:
        return None, "站点桩位数无效，无法预测"

    records_query = text(
        """
        SELECT created_at, duration_minutes
        FROM charging_records
        WHERE station_id = :sid
        ORDER BY created_at
        """
    )
    try:
        records = pd.read_sql(records_query, engine, params={"sid": station_id})
    except SQLAlchemyError:
        return None, "充电记录数据不可用，无法预测"
    if records.empty:
        return None, "数据量不足，无法预测"

    records["created_at"] = pd.to_datetime(records["created_at"])
    records["ended_at"] = records["created_at"] + pd.to_timedelta(
        records["duration_minutes"], unit="m"
    )

    start = records["created_at"].min().floor("h")
    end = records["ended_at"].max().ceil("h")
    observation_hours = pd.date_range(start=start, end=end, freq="h")
    if len(observation_hours) < 2:
        return None, "数据量不足，无法预测"

    future_hour = (pd.Timestamp.utcnow() + pd.Timedelta(hours=horizon_hours)).hour
    same_hour_observations = []
    all_observations = []

    for hour_start in observation_hours[:-1]:
        hour_end = hour_start + pd.Timedelta(hours=1)
        active_count = int(
            ((records["created_at"] < hour_end) & (records["ended_at"] > hour_start)).sum()
        )
        is_idle = active_count < slots
        all_observations.append(is_idle)
        if hour_start.hour == future_hour:
            same_hour_observations.append(is_idle)

    observations = same_hour_observations if len(same_hour_observations) >= 3 else all_observations
    probability = round(sum(observations) / len(observations) * 100, 2)
    return probability, f"预计未来 {horizon_hours} 小时内有 {probability}% 的空闲概率"
