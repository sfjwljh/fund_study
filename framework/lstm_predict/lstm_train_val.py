import pdb
import numpy as np
import pickle
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Activation
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import mean_squared_error
import datetime
import re

# data_origin_path=r"framework\data\step10['波动率', 'emotion=1', 'emotion=2']data.pkl"
data_origin_path = r"framework\data\step10['波动率']data.pkl"

# 设置日志目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_path = os.path.join(BASE_DIR, data_origin_path)
match = re.search(r"step(\d+)\['(.*)'\]", data_path)

if match is None:
    raise ValueError("数据路径格式不正确，无法提取信息。")


log_dir = os.path.join(BASE_DIR, "framework/lstm_predict/logs", match.group(1) + '_' + match.group(2) + '_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") ).replace("', '", "_")
# 日志名称中加入时间信息

# pdb.set_trace()
# 创建 TensorBoard 日志记录器
summary_writer = tf.summary.create_file_writer(log_dir)

# 读取数据
with open(data_path, 'rb') as file:
    data = pickle.load(file)

X_train = np.array(data['X_train'])  # 形状: (687, 10, 1)
Y_train = np.array(data['Y_train'])    # 形状: (687,)
X_val = np.array(data['X_val'])        # 形状: (172, 10, 1)
Y_val = np.array(data['Y_val'])        # 形状: (172,)

print("X_train shape:", X_train.shape)  # 应该是 (样本数, 时间步数, 特征数)
print("Y_train shape:", Y_train.shape)  # 应该是 (样本数,)
print("X_val shape:", X_val.shape)      # 应该是 (样本数, 时间步数, 特征数)
print("Y_val shape:", Y_val.shape)      # 应该是 (样本数,)

def build_model(input_shape):
    """构建LSTM模型"""
    model = Sequential()

    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50, return_sequences=True))
    model.add(LSTM(20))
    model.add(Activation('relu'))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model

def train(X_train, Y_train, X_val, Y_val, model, epochs, patience):
    

    # 早停回调
    es = EarlyStopping(monitor='val_loss', patience=patience, mode='auto', verbose=1, restore_best_weights=True)

    # 记录训练过程
    for epoch in range(epochs):
        history = model.fit(X_train, Y_train, validation_data=(X_val, Y_val), epochs=1, verbose=1, callbacks=[es])
        
        # 记录训练和验证损失
        train_loss = history.history['loss'][0]
        val_loss = history.history['val_loss'][0]
        
        with summary_writer.as_default():
            tf.summary.scalar('train_loss', train_loss, step=epoch)
            tf.summary.scalar('val_loss', val_loss, step=epoch)

    # 预测
    Y_pred = model.predict(X_val)

    # 计算训练集和验证集的RMSE
    train_rmse = np.sqrt(mean_squared_error(Y_train, model.predict(X_train)))
    val_rmse = np.sqrt(mean_squared_error(Y_val, Y_pred))
    print(f"训练集的RMSE: {train_rmse}")
    print(f"验证集的RMSE: {val_rmse}")

    return model, Y_pred


epochs = 400  # 训练轮数
patience = 1  # 早停耐心值
# 构建LSTM模型
pdb.set_trace()
model_train = build_model((X_train.shape[1], X_train.shape[2]))  # (10, 3)

# 训练模型
model, Y_pred = train(X_train, Y_train, X_val, Y_val, model_train, epochs, patience)

# 计算AIC和BIC（可选）
# mse_val = mean_squared_error(Y_val, Y_pred)
# aic_val = calculate_aic(len(Y_val), mse_val, 4)
# bic_val = calculate_bic(len(Y_val), mse_val, 4)

# 输出AIC和BIC（可选）
# print(f"AIC on validation data: {aic_val}")
# print(f"BIC on validation data: {bic_val}")


