import os
import pymysql
import requests
import pandas as pd
# 文件夹路径
folder_path = r"C:\Users\LJH\Desktop\txt存放\飞书"

# 获取文件夹内所有txt文件的路径
txt_files = [f.split('.')[0] for f in os.listdir(folder_path) if f.endswith('.txt')]
db = pymysql.connect(host='bj-cynosdbmysql-grp-igalwqqk.sql.tencentcdb.com',
                        user='root',
                        password='UIBE_chat_2023',
                        database='fund_stream',
                        charset='utf8mb4',
                        port=25445,)
cursor = db.cursor()
date_code_dict={}
for code in txt_files:
    query="select date from total where code={}".format(code)
    cursor.execute(query)
    result=cursor.fetchone()[0]
    if result not in date_code_dict.keys():
        date_code_dict[str(result)]=[code]
    else:
        date_code_dict[str(result)].append(code)
date_code_dict