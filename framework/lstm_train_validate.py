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
from math import sqrt
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

def train(model, train_loader, val_loader, criterion, optimizer, epochs):
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
        
        RMSE=get_rmse(val_loader,model,criterion)


        # 记录日志
        logging.info(f'Epoch [{epoch+1}/{epochs}], Average Training Loss: {avg_train_loss:.8f}, Validation RMSE: {RMSE:.8f}')  # 记录到日志文件


def data_transform(data_path,batch_size=16):
    """
    读取lstm的数据，转换成训练、验证所需的loader。
    
    """
    # 读取数据
    with open(data_path, 'rb') as file:
        data = pickle.load(file)

    X_train = np.array(data['X_train'])  # 形状: (n,step, 特征数)
    Y_train = np.array(data['Y_train'])    # 形状: (n,1)
    X_val = np.array(data['X_val'])        
    Y_val = np.array(data['Y_val'])        

    # pdb.set_trace()
    # 转换为 PyTorch 张量
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    Y_train_tensor = torch.tensor(Y_train, dtype=torch.float32).unsqueeze(1)  # 变为 (687, 1)
    X_val_tensor = torch.tensor(X_val, dtype=torch.float32)
    Y_val_tensor = torch.tensor(Y_val, dtype=torch.float32).unsqueeze(1)  # 变为 (172, 1)

    # 创建数据加载器
    train_dataset = TensorDataset(X_train_tensor, Y_train_tensor)
    val_dataset = TensorDataset(X_val_tensor, Y_val_tensor)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    return X_train,Y_train,train_loader,val_loader

def get_rmse(loader,model,criterion):
    # 验证
    model.eval()

    val_loss_by_loader=0
    total_samples=0
    with torch.no_grad():
        for batch_idx, (inputs, labels) in enumerate(loader):
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            val_loss_by_loader += loss.item()* len(labels)  # 计算每个批次的损失
            total_samples+= len(labels)  # 统计样本总数
    RMSE=sqrt(val_loss_by_loader/total_samples)
    return RMSE

def lstm_pipeline(data_relative_path):


    # data_relative_path = r"framework/data/0430测试.pkl"
    data_path = os.path.join(BASE_DIR, data_relative_path)
    X_train,Y_train,train_loader,val_loader=data_transform(data_path)

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
    train(model, train_loader, val_loader, criterion, optimizer, epochs)

    train_rmse=get_rmse(train_loader,model,criterion)
    val_rmse=get_rmse(val_loader,model,criterion)
    print(f"训练集的RMSE: {train_rmse}")
    print(f"验证集的RMSE: {val_rmse}")

if __name__ == '__main__':
    data_relative_path = os.path.join("framework","data","0430测试.pkl")
    lstm_pipeline(data_relative_path)