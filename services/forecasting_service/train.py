import torch
import torch.nn as nn
import torch.optim as optim
from .processor import fetch_and_prepare_data
from .lstm_model import LSTMForecaster
import os

def train_model(product_id: int, epochs=200):
    # 1. 获取并预处理数据
    data, scaler = fetch_and_prepare_data(product_id)
    if data is None or len(data) < 10:
        print(f"商品 {product_id} 数据量不足，取消训练。")
        return

    # 2. 实例化模型、损失函数和优化器
    model = LSTMForecaster()
    loss_function = nn.MSELoss() # 均方误差损失
    optimizer = optim.Adam(model.parameters(), lr=0.001) # Adam优化器

    model.train()
    print(f"开始训练商品 {product_id} 的预测模型...")

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
    
    torch.save(model.state_dict(), f"{model_dir}/station_{product_id}.pth")
    print(f"模型已保存至 models/station_{product_id}.pth")

if __name__ == "__main__":
    # 为 1 号充电站训练模型
    train_model(1)