import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import torch
# 读取数据
df = pd.read_csv('your_dataset.csv')

# 选择需要的特征
features = ['Price', 'Volume', 'Sentiment', 'MA_10', 'RSI']
target = 'Volatility'

# 归一化特征
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_features = scaler.fit_transform(df[features])
scaled_target = scaler.fit_transform(df[[target]])

# 构建特征和目标序列
def create_lstm_dataset(X, y, time_step=10):
    Xs, ys = [], []
    for i in range(len(X) - time_step):
        v = X[i:(i + time_step)]
        Xs.append(v)
        ys.append(y[i + time_step])
    return np.array(Xs), np.array(ys)

time_step = 10
X, y = create_lstm_dataset(scaled_features, scaled_target, time_step)

# X的形状将是 (样本数量, 时间步, 特征数量)
# y的形状将是 (样本数量, 1)
print(f"X shape: {X.shape}, y shape: {y.shape}")

# 数据分割为训练集和测试集
train_size = int(len(X) * 0.8)
test_size = len(X) - train_size

train_X, test_X = X[:train_size], X[train_size:]
train_y, test_y = y[:train_size], y[train_size:]

# 转换为Tensor（如使用PyTorch）
train_X = torch.from_numpy(train_X).float()
train_y = torch.from_numpy(train_y).float()
test_X = torch.from_numpy(test_X).float()
test_y = torch.from_numpy(test_y).float()

# 现在可以将train_X, train_y, test_X, test_y输入到你的LSTM模型中进行训练和评估
