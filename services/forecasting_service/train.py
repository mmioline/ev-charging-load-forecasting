import torch
import torch.nn as nn
import torch.optim as optim
from sqlalchemy import text

from .database import engine
from .processor import fetch_and_prepare_data
from .lstm_model import LSTMForecaster
import os

def train_model(station_id: int, epochs=200):
    # 1. 获取并预处理数据
    data, scaler = fetch_and_prepare_data(station_id)
    if data is None or len(data) < 10:
        print(f"站点 {station_id} 数据量不足，取消训练。")
        return False

    # 2. 实例化模型、损失函数和优化器
    model = LSTMForecaster()
    loss_function = nn.MSELoss() # 均方误差损失
    optimizer = optim.Adam(model.parameters(), lr=0.001) # Adam优化器

    model.train()
    print(f"开始训练站点 {station_id} 的预测模型...")

    for i in range(epochs):
        # 这里的逻辑是将数据喂给 LSTM
        # 为了演示，我们使用滑动窗口简化处理
        optimizer.zero_grad()
        model.hidden_cell = (torch.zeros(1, 1, model.hidden_layer_size),
                            torch.zeros(1, 1, model.hidden_layer_size))

        # 预测输出
        y_pred = model(data[:-1]) 
        
        # 计算损失 (拿最后一天的数据作为真实值进行对比)
        single_loss = loss_function(y_pred, data[-1:])
        single_loss.backward()
        optimizer.step()

        if i % 50 == 0:
            print(f'Epoch {i} loss: {single_loss.item():.10f}')

    # 3. 保存训练好的模型权重
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    torch.save(model.state_dict(), f"{model_dir}/station_{station_id}.pth")
    print(f"模型已保存至 models/station_{station_id}.pth")
    return True


def get_station_ids_with_records():
    query = text(
        """
        SELECT station_id
        FROM charging_records
        GROUP BY station_id
        HAVING COUNT(*) >= 10
        ORDER BY station_id
        """
    )
    with engine.connect() as connection:
        return [row[0] for row in connection.execute(query).fetchall()]

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train station forecasting models.")
    parser.add_argument("station_ids", nargs="*", type=int, help="要训练的站点 ID；不填则训练所有有足够记录的站点")
    parser.add_argument("--epochs", type=int, default=200)
    args = parser.parse_args()

    station_ids = args.station_ids or get_station_ids_with_records()
    if not station_ids:
        print("没有找到可训练的站点记录。")
    for station_id in station_ids:
        train_model(station_id, epochs=args.epochs)
