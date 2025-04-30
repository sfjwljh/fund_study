import pdb
import pandas as pd
import pickle
import sys
import os
import numpy as np

BASE_DIR=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(BASE_DIR)
with open(BASE_DIR+'/framework/data/0428test.pkl','rb') as file:  
    data=pickle.load(file)

step=10   #lstm的步长
X=[]
Y=[]

df=data
# feature_list=['波动率']
# feature_list=['波动率','emotion=1','emotion=2']
# feature_list=['波动率','emotion=1','emotion=2','emotion_count','RSI','MACD',]
feature_list=['波动率','RSI','MACD','行业自身情况_现在']

# 假设 df 是您提供的数据框，step 是步长，feature_list 是特征列表
step = 10  # LSTM 的步长
X_tmp = []
Y_tmp = []

# 遍历数据框，构建输入特征和目标变量
for i in range(len(df) - step-1):
    # 提取当前步长的特征
    X_tmp.append(df[feature_list].iloc[i:i + step].values)
    # 提取目标变量（波动率）
    Y_tmp.append(df['波动率'].iloc[i + step+1])

# 将 X 和 Y 转换为 numpy 数组
X.extend(np.array(X_tmp))
Y.extend(np.array(Y_tmp))

X=np.array(X)
Y=np.array(Y)
train_size=0.8
# 从X中随机选择val比例的数据，随机抽取，不要直接按顺序
seed_value=1234
np.random.seed(seed_value)  # seed_value 是您选择的任意整数
index=np.random.choice(range(X.shape[0]),int(X.shape[0]*train_size),replace=False)
X_train=X[index]
Y_train=Y[index]
X_val=np.delete(X,index,axis=0)
Y_val=np.delete(Y,index,axis=0)
# 输出 X 和 Y 的形状以确认
print("X_train shape:", X_train.shape)
print("Y_train shape:", Y_train.shape)
print("X_val shape:", X_val.shape)
print("Y_val shape:", Y_val.shape)

data={'X_train':X_train.tolist(),'Y_train':Y_train.tolist(),'X_val':X_val.tolist(),'Y_val':Y_val.tolist()}
with open(BASE_DIR+'/framework/data/step'+str(step)+str(feature_list)+'data.pkl','wb') as file:
    pickle.dump(data,file)

