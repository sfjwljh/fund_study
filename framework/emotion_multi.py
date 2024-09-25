# -*- coding:utf-8 -*-
from doubao_api import get_doubao
import os
import pymysql
from tool import get_inudstry_code
from concurrent.futures import ProcessPoolExecutor

bankuai_path = r'F:\obsidian\Master\fund_stream_project\codes\framework\板块.txt'
system = """
你是一个金融情感分析专家，请根据提示完成下面的任务。
任务要求：根据一句金融文本（可能是噪声），判断其对给定板块领域的情感。如果是正向情感，就打1分；如果是负向情感，打2分；如果是中立情感，打3分；如果是噪声，所说内容和板块不想关，打0分。
示例1
输入：- 提前预告高端制造混合基金经理凡可下周一下午会来到直播间与大家交流。板块：高端制造
返回：0
示例2
输入： - 很多赛道已跌回两年前附近，这是上车的好机会。板块：宏观市场
返回：1
示例3
输入：二季度经济数据可能环比更悲观，需关注消费刺激政策出台。板块：宏观市场
返回：2
根据上面的要求和示例，下面是需要你回答的问题：芯片半导体方向有所异动，但行业景气度下行，持续性待考量。

现在的问题是：【sec1】
请你根据上面的要求和例子直接打出分数，不要返回其他任何多余的内容："""

def get_emotion(result):
    db = pymysql.connect(host='bj-cynosdbmysql-grp-igalwqqk.sql.tencentcdb.com',
                         user='root',
                         password='UIBE_chat_2023',
                         database='fund_stream',
                         charset='utf8mb4',
                         port=25445,)
    cursor = db.cursor()

    prompt = system.replace('【sec1】', result[0] + "板块：" + get_inudstry_code(bankuai_path, result[1]))
    ans = (get_doubao('', prompt))
    try:
        ans = int(ans)
        update_query = """update opinions set emotion={} where op='{}' and industry={}""".format(ans, result[0], result[1])
        cursor.execute(update_query)
        print(result[0] + ' ' + get_inudstry_code(bankuai_path, result[1]) + ' ' + str(ans))
        db.commit()
    except:
        ans = -1
        update_query = """update opinions set emotion={} where op='{}' and industry={}""".format(ans, result[0], result[1])
        cursor.execute(update_query)
        db.commit()

    cursor.close()
    db.close()

def process_data(worker_id, num_workers):
    db = pymysql.connect(host='bj-cynosdbmysql-grp-igalwqqk.sql.tencentcdb.com',
                         user='root',
                         password='UIBE_chat_2023',
                         database='fund_stream',
                         charset='utf8mb4',
                         port=25445,)
    cursor = db.cursor()

    # 根据进程的序号和总的进程数来分配数据
    select_query = "select op,industry from opinions where isnull(emotion) and industry<>-1"
    cursor.execute(select_query)
    results = cursor.fetchall()

    # 仅处理该进程分配的数据行
    for i, result in enumerate(results):
        if i % num_workers == worker_id:
            get_emotion(result)

    cursor.close()
    db.close()

if __name__ == "__main__":
    num_workers = 10  # 假设我们有4个进程
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for worker_id in range(num_workers):
            executor.submit(process_data, worker_id, num_workers)
