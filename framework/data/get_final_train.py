# 处理训练数据
import pickle
import pymysql
from tool import get_inudstry_name
from collections import defaultdict, Counter
import pdb
import json
import pandas as pd
import numpy as np
import os 
industry=10
# pdb.set_trace()
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
from utils.database.connect import connect_db
db,cursor=connect_db()
fund_path = os.path.dirname(BASE_DIR)

def industry_get_date_emotion(industry):
    """
    输入：行业编号
    从数据库拿到该行业的所有直播观点，返回每种情感的数量
    输出：一个dataframe，该行业的所有观点{(日期，emotion=1数量,emotion=2数量,emotion=3数量)}
                 日期  emotion=1  emotion=2  emotion=3
    """


    sql="""select date,emotion from (
        select o.code, o.emotion, t.date
        from opinions o
        join total t on o.code = t.code
        where o.industry={} and (o.emotion=1 or o.emotion=2 or o.emotion=3)
    ) as subquery""".format(industry)
    cursor.execute(sql)
    sql_result = cursor.fetchall()


    # 创建一个字典来存储每个日期的情感
    emotion_dict = defaultdict(list)

    # 填充字典
    for date, emotion in sql_result:
        emotion_dict[date].append(emotion)

    # 创建一个新的列表来存储结果
    result = []
    for date, emotions in emotion_dict.items():
        # 得到emotion=1,2,3的数量
        emotion_count = Counter(emotions)
        result.append((date, emotion_count[1], emotion_count[2], emotion_count[3]))

    return pd.DataFrame(result, columns=['日期', 'emotion=1', 'emotion=2', 'emotion=3'])

    # # 计算每个日期的情感众数
    # for date, emotions in emotion_dict.items():
    #     # 使用Counter来计算众数
    #     most_common_emotion = Counter(emotions).most_common(1)[0][0]
    #     result.append((date, most_common_emotion))

    # # 输出结果
    # return(pd.DataFrame(result, columns=['日期','emotion']))

def industry_get_index(industry):
    """
    输入：行业编号
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
        if row.iloc[1] == industry:  # 检查第二列的值
            result_value = row.iloc[2]  # 获取第三列的值
            break  # 找到后立即停止

    # 输出结果
    if result_value is not None:
        print(industry)
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

def merge_price_emotion(industry):
    """
    输入：行业编号
    输出：合并好，按日期数据密度筛过，填充过空值，计算好波动率的dataframe
    """
    emotion_df = industry_get_date_emotion(industry)
    df=industry_get_index(industry)
    if df is None:
        print(str(industry)+'没找到指数')
        return None
    # 确保日期列的格式一致
    df['日期'] = pd.to_datetime(df['日期'])
    emotion_df['日期'] = pd.to_datetime(emotion_df['日期'])
    # 合并两个 DataFrame
    new_df = pd.merge(emotion_df, df, on='日期', how='right')  # 使用 right 合并
    #new_df按照日期排序
    new_df=new_df.sort_values(by='日期',ascending=True)

    ###计算金融技术指标

    # 计算对数收益率
    new_df['对数收益率'] = np.log(new_df['收盘价'] / new_df['收盘价'].shift(1))
    # 计算过去10天对数收益率的标准差（波动率）
    new_df['波动率'] = new_df['对数收益率'].rolling(window=10).std()
    # new_df = new_df.dropna(subset=['波动率'])

    # 计算股票中的ADX指标
    new_df['ADX'] = new_df['对数收益率'].rolling(window=14).mean()

    # 计算股票价格中的RSI指标
    new_df['涨跌幅'] = new_df['收盘价'].diff()
    new_df['上涨幅度'] = new_df['涨跌幅'].clip(lower=0)
    new_df['下跌幅度'] = new_df['涨跌幅'].clip(upper=0).abs()
    new_df['平均上涨幅度'] = new_df['上涨幅度'].ewm(span=14).mean()
    new_df['平均下跌幅度'] = new_df['下跌幅度'].ewm(span=14).mean()
    new_df['RS'] = new_df['平均上涨幅度'] / new_df['平均下跌幅度']
    new_df['RSI'] = 100 - (100 / (1 + new_df['RS']))

   
    # 计算股票价格中的MACD指标
    new_df['EMA_12'] = new_df['收盘价'].ewm(span=12, adjust=False).mean()
    new_df['EMA_26'] = new_df['收盘价'].ewm(span=26, adjust=False).mean()
    new_df['DIF'] = new_df['EMA_12'] - new_df['EMA_26']
    new_df['DEA'] = new_df['DIF'].ewm(span=9, adjust=False).mean()
    new_df['MACD'] = (new_df['DIF'] - new_df['DEA']) * 2

    new_df=new_df[['日期','开盘价','收盘价','最高价','最低价','涨跌幅','成交量(万手)','成交额(亿元)','对数收益率','波动率','ADX','RSI','MACD','emotion=1','emotion=2','emotion=3']]
    # pdb.set_trace()
    #3种emotion允许为空，其他列不允许为空。
    new_df = new_df.dropna(subset=new_df.columns.difference(['emotion=1', 'emotion=2', 'emotion=3']))

    #替换3种emotion的空值为0
    new_df['emotion=1']=new_df['emotion=1'].fillna(0)
    new_df['emotion=2']=new_df['emotion=2'].fillna(0)
    new_df['emotion=3']=new_df['emotion=3'].fillna(0)

    ####计算emotion
    #计算一列，是3种emotion的和
    new_df['emotion_count']=new_df['emotion=1']+new_df['emotion=2']+new_df['emotion=3']

    # 筛选指定日期区间
    end_date='2024-07-01'
    start_date='2023-10-31'
    new_df=new_df[(new_df['日期']>=start_date)&(new_df['日期']<=end_date)]

    # 提取 emotion 不为 NaN 的行的日期
    emotion_not_nan_dates = new_df[new_df['emotion_count']>0]['日期']

    # 计算前25%分位点和后25%分位点
    quantiles = emotion_not_nan_dates.quantile([0.1, 0.9])

    # 截取这两个日期之间的行
    new_df = new_df[(new_df['日期'] >= quantiles.iloc[0]) & (new_df['日期'] <= quantiles.iloc[1])]

    ###填充emotion空值#############先不处理
    # macro=industry_get_date_emotion(58)
    # macro['日期'] = pd.to_datetime(macro['日期'])

    # # 筛选出 emotion 列为空的行
    # emotion_na_mask = new_df[new_df['emotion_count']==0]

    # # 尝试填充同一日期的 macro 的 emotion 值
    # new_df.loc[emotion_na_mask, 'emotion'] = new_df.loc[emotion_na_mask, '日期'].map(
    #     macro.set_index('日期')['emotion']
    # )

    # # 创建一个新的 Series 存储填充值
    # filled_emotion = new_df['emotion'].fillna(3)

    # # 使用这个 Series 更新原来的 DataFrame
    # new_df['emotion'] = filled_emotion

    # pdb.set_trace()
    return new_df

# ind_list=[-1,58,9,10,1,57,2,54,49,6,19,45,29,51,20,14,16,26,46,50,15,21,24,5,4]
# for industry in ind_list:
#     df=merge_price_emotion(industry)
#     df.to_pickle('framework/train_data/'+str(industry)+'.pkl')

if __name__ == '__main__':
    total=0
    ind_list=[9,10,1,57,2,54,49,6,19,45,29,51,20,14,16,26,46,50,15,21,24,5,4]
    data={}
    for industry in ind_list:
        df=merge_price_emotion(industry)
        total+=len(df)
        data[str(industry)]=df
    print("总行数："+str(total))
    with open(r'F:\BaiduSyncdisk\obsidian\Master\fund_stream_project\codes\framework\data\data.pkl','wb') as file:  
        pickle.dump(data,file)
