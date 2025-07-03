# 处理训练数据
import pickle


import pdb
import json
from typing import List
import pandas as pd
import numpy as np
import os 
import sys
import os
import pandas as pd
import json
import time

# pdb.set_trace()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from framework.lstm_train_validate import lstm_pipeline

fund_path = os.path.dirname(BASE_DIR)


def get_date_opi_dict():
    """
    获取 {日期：[{行业，方面，时间，情感}，「观点」]}
    这是包含所有行业的
    """
    # 读取编号-日期对应数据
    code_date=pd.read_csv(os.path.join(BASE_DIR,r'framework/code_date.csv'), sep='\t', header=None)
    code_date_dict = dict(zip(code_date.iloc[:, 0], code_date.iloc[:, 1]))

    #读取情感标注数据，这里只有code，需要用上面的dict映射到日期
    model_emotion_label_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好_step4_整合_带flat.json')
    with open(model_emotion_label_file, 'r', encoding='utf-8') as f:
        line = f.read()
        ec=emotion_content=json.loads(line)

        date_set=set(code_date.iloc[:, 1])
    date_opi_dict={date:[] for date in date_set}  
    # 将情感加到日期中
    for doc in ec:
        code=doc['code']

        for content in doc['content']:
            if len(content['label_flat'])==0:
                continue
            sentence=content['sentence']
            date=code_date_dict.get(code,'')

            if date=='':
                print(str(code)+"不在code_date.csv中")
                continue
            for label in content['label_flat']:
                new_label = label.copy()
                new_label['code']=code
                new_label['sentence']=sentence
                date_opi_dict[date].append(new_label)
    return date_opi_dict

def get_certain_indusry_date_opi_dict(ind_name):
    """
    输入：所有行业的{日期：观点}+要检索的行业名称
    输出：该行业的{日期：[{方面，时间，情感}]}
    """
    date_opi_dict=get_date_opi_dict()
    ind_date_opi_dict={date:[] for date in date_opi_dict.keys()}
    # pdb.set_trace()
    for date,opi_list in date_opi_dict.items():
        for opi in opi_list:
            if opi['industry'] == ind_name:
                opi.pop('industry')
                ind_date_opi_dict[date].append(opi)
    return ind_date_opi_dict

def compress_opi_list(date_opi_dict):
    """
    压缩list，计算出每个date的特征
    输入：{日期：[{方面，时间，情感}]}
    输出：一个df：日期,特征1,特征2,特征3
    """
    aspect_list=["上游产业情况","下游产业情况","行业自身情况","国家政策方向","宏观市场","子板块"]
    time_list=["现在","未来","过去","始终"]
    total_option={}
    for asp in aspect_list:
        for tme in time_list:
            total_option[asp+'_'+tme]=[] #得到每个方面*时间。共24维
    date_egin={date:total_option.copy() for date in date_opi_dict.keys()}
    for date,opi_list in date_opi_dict.items():
        # pdb.set_trace()
        for opi in opi_list:
            aspect=opi['aspect']
            time=opi['time']
            emotion=opi['emotion']
            date_egin[date][aspect+'_'+time].append(emotion)
        # pdb.set_trace()
        for egin in total_option.keys():
            if len(date_egin[date][egin])==0:
                date_egin[date][egin]=None
            else:
                date_egin[date][egin]=sum(date_egin[date][egin])/len(date_egin[date][egin])
                # 每个特征取均值
        data = {'日期': list(date_egin.keys())}

    for feature in total_option.keys():
        data[feature] = [date_egin[date][feature] for date in date_egin.keys()]

    # 创建 DataFrame
    df = pd.DataFrame(data)
    return df
        
        
            


def industry_get_index(industry):
    """
    输入：行业名称
    输出：该行业的指数的历史价格的dataframe
                  日期      开盘价      收盘价      最高价      最低价     涨跌幅  成交量(万手)  成交额(亿元)
    """
    # 读取CSV文件
    file_path = os.path.join(BASE_DIR,'行业-编号-指数编号.csv')  
    # 读取csv文件,第一行不是标题行  
    df = pd.read_csv(file_path,header=None)

    # 初始化结果变量
    result_value = None

    # 遍历数据框的每一行
    for index, row in df.iterrows():
        if row.iloc[0] == industry:  # 根据名称匹配
            result_value = row.iloc[2]  # 获取第三列的值
            break  # 找到后立即停止

    # 输出结果
    if result_value is not None:
        # print(industry)
        if result_value!='nan':
            # pdb.set_trace()
            path=fund_path+r"/指数历史数据"
            path=os.path.join(path,str(result_value)+'.xls')
            df = pd.read_excel(path)
            return df
        else:
            print(result_value+'无数据')
            return None

    else:
        print("没有找到匹配的值。")
        return None

def price_calculate_technical_indicators(input_df, indicator_names: List):
    """
    计算波动率和技术指标。波动率无需传入，会自动计算。只需输入需要计算的技术指标
    可选：['ADX','RSI','MACD', 'TRANGE', 'ATR', 'NATR', 'CCI', 'PPO', 'ROC', 'OBV', 'ADOSC']
    """
    # new_df按照日期排序
    new_df = input_df.copy()
    new_df = new_df.sort_values(by='日期', ascending=True)

    # 计算对数收益率
    new_df['对数收益率'] = np.log(new_df['收盘价'] / new_df['收盘价'].shift(1))
    # 计算过去10天对数收益率的标准差（波动率）
    new_df['波动率']   = new_df['对数收益率'].rolling(window=10).std()

    # 原有指标
    if 'ADX' in indicator_names:
        new_df['ADX'] = new_df['对数收益率'].rolling(window=14).mean()

    if 'RSI' in indicator_names:
        new_df['涨跌幅']       = new_df['收盘价'].diff()
        new_df['上涨幅度']     = new_df['涨跌幅'].clip(lower=0)
        new_df['下跌幅度']     = new_df['涨跌幅'].clip(upper=0).abs()
        new_df['平均上涨幅度'] = new_df['上涨幅度'].ewm(span=14).mean()
        new_df['平均下跌幅度'] = new_df['下跌幅度'].ewm(span=14).mean()
        new_df['RS']         = new_df['平均上涨幅度'] / new_df['平均下跌幅度']
        new_df['RSI']        = 100 - (100 / (1 + new_df['RS']))
        new_df = new_df.drop(columns=['涨跌幅','上涨幅度','下跌幅度','平均上涨幅度','平均下跌幅度','RS'])

    if 'MACD' in indicator_names:
        new_df['EMA_12'] = new_df['收盘价'].ewm(span=12, adjust=False).mean()
        new_df['EMA_26'] = new_df['收盘价'].ewm(span=26, adjust=False).mean()
        new_df['DIF']    = new_df['EMA_12'] - new_df['EMA_26']
        new_df['DEA']    = new_df['DIF'].ewm(span=9, adjust=False).mean()
        new_df['MACD']   = (new_df['DIF'] - new_df['DEA']) * 2
        # 保留 EMA_12/EMA_26 以便后续 PPO 计算，待最后再清理
        # new_df = new_df.drop(columns=['EMA_12','EMA_26','DIF','DEA'])

    # —— 新增 8 个技术指标 —— #

    # 1. True Range
    if 'TRANGE' in indicator_names:
        high       = new_df['最高价']
        low        = new_df['最低价']
        prev_close = new_df['收盘价'].shift(1)
        new_df['TRANGE'] = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low  - prev_close).abs()
        ], axis=1).max(axis=1)

    # 2. Average True Range (ATR)
    if 'ATR' in indicator_names:
        new_df['ATR'] = new_df['TRANGE'].rolling(window=14).mean()

    # 3. Normalized ATR (NATR)
    if 'NATR' in indicator_names:
        new_df['NATR'] = new_df['TRANGE'] / new_df['收盘价'] * 100

    # 4. Commodity Channel Index (CCI)
    if 'CCI' in indicator_names:
        tp     = (new_df['最高价'] + new_df['最低价'] + new_df['收盘价']) / 3
        ma_tp  = tp.rolling(window=20).mean()
        md     = tp.rolling(window=20).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
        new_df['CCI'] = (tp - ma_tp) / (0.015 * md)

    # 5. Percentage Price Oscillator (PPO)
    if 'PPO' in indicator_names:
        ema_short = new_df['收盘价'].ewm(span=12, adjust=False).mean()
        ema_long  = new_df['收盘价'].ewm(span=26, adjust=False).mean()
        new_df['PPO'] = (ema_short - ema_long) / ema_long * 100

    # 6. Rate of Change (ROC)
    if 'ROC' in indicator_names:
        n = 12
        new_df['ROC'] = (new_df['收盘价'] - new_df['收盘价'].shift(n)) / new_df['收盘价'].shift(n) * 100

    # 7. On-Balance Volume (OBV)
    if 'OBV' in indicator_names:
        direction       = np.sign(new_df['收盘价'].diff()).fillna(0)
        volume          = new_df['成交量(万手)']
        new_df['OBV']   = (direction * volume).cumsum()

    # 8. Chaikin A/D Oscillator (ADOSC)
    if 'ADOSC' in indicator_names:
        high   = new_df['最高价']
        low    = new_df['最低价']
        close  = new_df['收盘价']
        vol    = new_df['成交量(万手)']
        mfm    = ((close - low) - (high - close)) / (high - low)
        mfv    = mfm * vol
        adl    = mfv.cumsum()
        new_df['ADOSC'] = adl.ewm(span=3,  adjust=False).mean() - adl.ewm(span=10, adjust=False).mean()

    # —— 清理 MACD 中间列 —— #
    if 'MACD' in indicator_names:
        new_df = new_df.drop(columns=['EMA_12','EMA_26','DIF','DEA'])

    return new_df

def merge_price_emotion(price_df,emotion_df):
    """
    输入：行业编号
    输出：合并好，按日期数据密度筛过，填充过空值，计算好波动率的dataframe
    """


    if price_df is None:
        print(str(industry)+'没找到指数')
        return None
    # 确保日期列的格式一致
    price_df['日期'] = pd.to_datetime(price_df['日期'])
    emotion_df['日期'] = pd.to_datetime(emotion_df['日期'])
    # 合并两个 DataFrame
    new_df = pd.merge(emotion_df, price_df, on='日期', how='right')  # 使用 right 合并
    


    return new_df

def empty_process(df):
    """
    处理空值。主要是情感特征，可能不是每一天都有
    """
    emotion_feature_list=['上游产业情况_现在', '上游产业情况_未来', '上游产业情况_过去', '上游产业情况_始终', '下游产业情况_现在',
       '下游产业情况_未来', '下游产业情况_过去', '下游产业情况_始终', '行业自身情况_现在', '行业自身情况_未来',
       '行业自身情况_过去', '行业自身情况_始终', '国家政策方向_现在', '国家政策方向_未来', '国家政策方向_过去',
       '国家政策方向_始终', '宏观市场_现在', '宏观市场_未来', '宏观市场_过去', '宏观市场_始终', '子板块_现在',
       '子板块_未来', '子板块_过去', '子板块_始终']
    for emotion_feature in emotion_feature_list:
        df[emotion_feature]=df[emotion_feature].fillna(0)
    df = df.dropna()
    return df

def trans2lstm_train(step, industry_df_dict, feature_list, val_ratio=0.2):
    """
    把合并好的df转成lstm训练所需的训练集、验证集。
    step：LSTM输入时间步长
    industry_df_dict：{行业名: df, ...}，必须按日期升序
    feature_list：输入特征列名
    val_ratio：每个行业最后 val_ratio 的数据作为验证集（基于窗口划分）
    """
    X_train, Y_train = [], []
    X_val, Y_val = [], []

    for industry, df in industry_df_dict.items():
        df = df.sort_values(by='日期')  # 确保按时间顺序

        X_tmp, Y_tmp = [], []
        for i in range(len(df) - step - 1):
            X_tmp.append(df[feature_list].iloc[i:i + step].values)
            Y_tmp.append(df['波动率'].iloc[i + step + 1])  # label 是 step+1 天的波动率

        X_tmp = np.array(X_tmp)
        Y_tmp = np.array(Y_tmp)

        cutoff = int(len(X_tmp) * (1 - val_ratio))
        X_train.extend(X_tmp[:cutoff])
        Y_train.extend(Y_tmp[:cutoff])
        X_val.extend(X_tmp[cutoff:])
        Y_val.extend(Y_tmp[cutoff:])

    # 转换为 numpy
    X_train = np.array(X_train)
    Y_train = np.array(Y_train)
    X_val = np.array(X_val)
    Y_val = np.array(Y_val)

    print("X_train shape:", X_train.shape)
    print("Y_train shape:", Y_train.shape)
    print("X_val shape:", X_val.shape)
    print("Y_val shape:", Y_val.shape)

    return {
        'X_train': X_train.tolist(),
        'Y_train': Y_train.tolist(),
        'X_val': X_val.tolist(),
        'Y_val': Y_val.tolist()
    }

if __name__ == '__main__':

    industry_list=["医疗保健",'生物医药','半导体','新能源','银行','汽车','煤炭','光伏','芯片','房地产']
    industry_df_dict={}
    features=[]
    for industry in industry_list:
        # 获取每一个行业的特征
        emotion_df = compress_opi_list(get_certain_indusry_date_opi_dict(industry))  #情感特征
        price_df=industry_get_index(industry)  # 指数价格
        price_df=price_calculate_technical_indicators(price_df,['ADX','RSI','MACD'])  #计算波动率和技术特征
        new_df=merge_price_emotion(price_df,emotion_df)  # 合并数据

        # 筛选指定日期区间
        end_date='2024-02-02'
        start_date='2023-11-20'
        new_df=new_df[(new_df['日期']>=start_date)&(new_df['日期']<=end_date)]

        #空值处理
        new_df=empty_process(new_df)

        features=new_df.columns.tolist() #当前的所有特征
        industry_df_dict[industry]=new_df

    print("所有可选特征\n"+str(features))
    # 筛选特征
    features.remove('日期')  # 在这里筛选需要进入实验的特征。日期是必删的
    # features=['波动率']
    features=['波动率','行业自身情况_现在', '行业自身情况_未来']
    
    print("进入实验的特征\n"+str(features))
    features_selected=features
    
    # 特征转换成lstm训练所需的格式
    lstm_data=trans2lstm_train(step=10,industry_df_dict=industry_df_dict,feature_list=features_selected)

    name_tag='0430测试'  
    # pdb.set_trace()
    # 保存数据，方便同一份数据修改超参多次实验
    relative_path=os.path.join('framework', 'data', '0622新验证集'+'.pkl')
    abs_path=os.path.join(BASE_DIR,relative_path)
    with open(abs_path,'wb') as file:  
        pickle.dump(lstm_data,file)
    
    # 训练lstm并预测
    lstm_pipeline(relative_path)
