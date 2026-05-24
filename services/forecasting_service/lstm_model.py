import torch
import torch.nn as nn

# 这就是你提到的 LSTMForecaster，它是自定义的类
class LSTMForecaster(nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=100, output_size=1):
        """
        input_size: 输入特征维度（当前只使用充电负荷，所以是1）
        hidden_layer_size: 隐藏层神经元数量
        output_size: 输出维度（预测下一时段负荷，所以是1）
        """
        super().__init__()
        self.hidden_layer_size = hidden_layer_size
        # 定义 LSTM 层
        self.lstm = nn.LSTM(input_size, hidden_layer_size)
        # 定义全连接层，将 LSTM 输出转为最终预测值
        self.linear = nn.Linear(hidden_layer_size, output_size)
        # 初始化隐藏状态
        self.hidden_cell = (torch.zeros(1,1,self.hidden_layer_size),
                            torch.zeros(1,1,self.hidden_layer_size))

    def forward(self, input_seq):
        # 前向传播逻辑
        lstm_out, self.hidden_cell = self.lstm(input_seq.view(len(input_seq) ,1, -1), self.hidden_cell)
        predictions = self.linear(lstm_out.view(len(input_seq), -1))
        return predictions[-1]
