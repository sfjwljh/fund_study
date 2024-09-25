# 处理训练数据
import pymysql
from tool import get_inudstry_code
from collections import defaultdict, Counter
import pdb
import json
import pandas as pd
import numpy as np
import os 
industry=10
# pdb.set_trace()

fund_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def industry_get_date_emotion(industry):
    """
    输入：行业编号
    从数据库拿到该行业的所有直播观点，计算出每一天的众数观点
    输出：集合，{(日期，观点)}
    """
    # 连接数据库
    db = pymysql.connect(host='bj-cynosdbmysql-grp-igalwqqk.sql.tencentcdb.com',
                            user='root',
                            password='UIBE_chat_2023',
                            database='fund_stream',
                            charset='utf8mb4',
                            port=25445,)
    cursor = db.cursor()
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

    # 计算每个日期的情感众数
    for date, emotions in emotion_dict.items():
        # 使用Counter来计算众数
        most_common_emotion = Counter(emotions).most_common(1)[0][0]
        result.append((date, most_common_emotion))

    # 输出结果
    return(pd.DataFrame(result, columns=['日期','emotion']))

def industry_get_index(industry):
    """
    输入：行业编号
    输出：该行业的指数的历史价格的dataframe
    """
    # 读取CSV文件
    file_path = r'行业-编号-指数编号.csv'  # 替换为你的CSV文件路径
    df = pd.read_csv(file_path)

    # 指定特定值
    specific_value = 10  # 替换为你要查找的特定值

    # 初始化结果变量
    result_value = None

    # 遍历数据框的每一行
    for index, row in df.iterrows():
        if row.iloc[1] == specific_value:  # 检查第二列的值
            result_value = row.iloc[2]  # 获取第三列的值
            break  # 找到后立即停止

    # 输出结果
    if result_value is not None:
        if result_value!='nan':
            # pdb.set_trace()
            path=fund_path+r"/指数历史数据"
            path=os.path.join(path,str(result_value)+'.xls')
            df = pd.read_excel(path)
            return df
        else:
            print(result_value+'无数据')

    else:
        print("没有找到匹配的值。")

def merge_price_emotion(industry):
    """
    输入：行业编号
    输出：合并好，按日期数据密度筛过，填充过空值，计算好波动率的dataframe
    """
    emotion_df = industry_get_date_emotion(industry)
    df=industry_get_index(industry)
    # 确保日期列的格式一致
    df['日期'] = pd.to_datetime(df['日期'])
    emotion_df['日期'] = pd.to_datetime(emotion_df['日期'])
    # 合并两个 DataFrame
    new_df = pd.merge(emotion_df, df, on='日期', how='right')  # 使用 right 合并

    new_df = new_df[['日期', '收盘价', '最高价', '最低价', '涨跌幅', '成交量(万手)', '成交额(亿元)', 'emotion']]

    # 计算对数收益率
    new_df['对数收益率'] = np.log(new_df['收盘价'] / new_df['收盘价'].shift(1))
    # 计算过去10天对数收益率的标准差（波动率）
    new_df['波动率'] = new_df['对数收益率'].rolling(window=10).std()
    new_df = new_df.dropna(subset=['波动率'])

    # 提取 emotion 不为 NaN 的行的日期
    emotion_not_nan_dates = new_df[new_df['emotion'].notna()]['日期']

    # 计算前25%分位点和后25%分位点
    quantiles = emotion_not_nan_dates.quantile([0.25, 0.75])

    # 截取这两个日期之间的行
    new_df = new_df[(new_df['日期'] >= quantiles.iloc[0]) & (new_df['日期'] <= quantiles.iloc[1])]



    # 计算 emotion 列中不为 NaN 的个数
    emotion_not_na_count = new_df['emotion'].notna().sum()

    macro=industry_get_date_emotion(58)
    macro['日期'] = pd.to_datetime(macro['日期'])

    # 筛选出 emotion 列为空的行
    emotion_na_mask = new_df['emotion'].isna()

    # 尝试填充同一日期的 macro 的 emotion 值
    new_df.loc[emotion_na_mask, 'emotion'] = new_df.loc[emotion_na_mask, '日期'].map(
        macro.set_index('日期')['emotion']
    )

    # 创建一个新的 Series 存储填充值
    filled_emotion = new_df['emotion'].fillna(3)

    # 使用这个 Series 更新原来的 DataFrame
    new_df['emotion'] = filled_emotion
    # pdb.set_trace()
    return new_df

ind_list=[-1,58,9,10,1,57,2,54,49,6,19,45,29,51,20,14,16,26,46,50,15,21,24,5,4]
for industry in ind_list:
    df=merge_price_emotion(industry)
    df.to_pickle('framework/train_data/'+str(industry)+'.pkl')
