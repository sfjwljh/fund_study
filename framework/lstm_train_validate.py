import numpy as np
import pickle
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import mean_squared_error
import datetime
import re
import pdb
import logging  # 导入 logging 模块
import pdb
from tqdm import tqdm
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LSTMModel, self).__init__()
        self.lstm1 = nn.LSTM(input_size, hidden_size, batch_first=True, bidirectional=False)
        self.lstm2 = nn.LSTM(hidden_size, hidden_size, batch_first=True, bidirectional=False)
        self.lstm3 = nn.LSTM(hidden_size, 20, batch_first=True, bidirectional=False)
        self.fc = nn.Linear(20, output_size)
        self.activation = nn.ReLU()

    def forward(self, x):
        x, _ = self.lstm1(x)
        x, _ = self.lstm2(x)
        x, _ = self.lstm3(x)
        x = self.activation(x[:, -1, :])  # 只取最后一个时间步的输出
        x = self.fc(x)
        return x

def train(model, train_loader, val_loader, criterion, optimizer, epochs,X_val_tensor,Y_val_tensor):
    model.train()
    for epoch in tqdm(range(epochs)):
        epoch_train_loss = 0  # 初始化每个 epoch 的训练损失
        for batch_idx, (inputs, labels) in enumerate(train_loader):
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # 记录每一步的训练损失
            epoch_train_loss += loss.item()
            # logging.info(f'Epoch [{epoch+1}/{epochs}], Batch [{batch_idx+1}/{len(train_loader)}], Training Loss: {loss.item():.8f}')

        # 计算平均训练损失
        avg_train_loss = epoch_train_loss / len(train_loader)
        
        # 验证
        model.eval()
        val_loss = 0
        with torch.no_grad():
            # 计算验证集的输出
            Y_pred = model(X_val_tensor)  # 使用整个验证集
            val_loss += criterion(Y_pred, Y_val_tensor).item()  # 计算验证损失

        val_loss /= len(val_loader)
        
        # 计算 RMSE
        val_rmse = np.sqrt(mean_squared_error(Y_val_tensor.numpy(), Y_pred.numpy()))  # 计算 RMSE

        # 记录日志
        logging.info(f'Epoch [{epoch+1}/{epochs}], Average Training Loss: {avg_train_loss:.8f}, Validation Loss: {val_loss:.8f}, Validation RMSE: {val_rmse:.8f}')  # 记录到日志文件


def data_transform(data_path):
    """
    读取lstm的数据，转换成训练、验证所需的loader。
    
    """
    # 读取数据
    with open(data_path, 'rb') as file:
        data = pickle.load(file)

    X_train = np.array(data['X_train'])  # 形状: (687, 10, 3)
    Y_train = np.array(data['Y_train'])    # 形状: (687,)
    X_val = np.array(data['X_val'])        # 形状: (172, 10, 3)
    Y_val = np.array(data['Y_val'])        # 形状: (172,)

    # pdb.set_trace()
    # 转换为 PyTorch 张量
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    Y_train_tensor = torch.tensor(Y_train, dtype=torch.float32).unsqueeze(1)  # 变为 (687, 1)
    X_val_tensor = torch.tensor(X_val, dtype=torch.float32)
    Y_val_tensor = torch.tensor(Y_val, dtype=torch.float32).unsqueeze(1)  # 变为 (172, 1)

    # 创建数据加载器
    train_dataset = TensorDataset(X_train_tensor, Y_train_tensor)
    val_dataset = TensorDataset(X_val_tensor, Y_val_tensor)
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    return X_train,Y_train,train_loader,val_loader,X_train_tensor,X_val_tensor,Y_val,Y_val_tensor,Y_val


def lstm_pipeline(data_relative_path):


    # data_relative_path = r"framework/data/0430测试.pkl"
    data_path = os.path.join(BASE_DIR, data_relative_path)
    X_train,Y_train,train_loader,val_loader,X_train_tensor,X_val_tensor,Y_val,Y_val_tensor,Y_val=data_transform(data_path)

    # 设置日志目录
    log_dir = os.path.join(BASE_DIR, "framework/logs", os.path.basename(data_relative_path).replace('.pkl','')+datetime.datetime.now().strftime("%m%d_%H%M")+'.log' ).replace("', '", "_")
    # 设置日志配置
    logging.basicConfig(filename=log_dir, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 设置超参数
    input_size = X_train.shape[2]  # 特征数
    hidden_size = 40
    output_size = 1
    epochs = 300

    # 构建模型
    model = LSTMModel(input_size, hidden_size, output_size)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 训练模型
    train(model, train_loader, val_loader, criterion, optimizer, epochs,X_val_tensor,Y_val_tensor)

    # 预测
    model.eval()
    with torch.no_grad():
        Y_pred = model(X_val_tensor)

    # 计算RMSE
    train_rmse = np.sqrt(mean_squared_error(Y_train, model(X_train_tensor).detach().numpy()))
    val_rmse = np.sqrt(mean_squared_error(Y_val, Y_pred.numpy()))
    print(f"训练集的RMSE: {train_rmse}")
    print(f"验证集的RMSE: {val_rmse}")

if __name__ == '__main__':
    data_relative_path = os.path.join("framework","data","0430测试.pkl")
    lstm_pipeline(data_relative_path)