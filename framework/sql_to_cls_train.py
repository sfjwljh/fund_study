# 把sql数据库里的（语料，情感）拿下来形成情感分类的训练语料
import pymysql
from tool import get_inudstry_name
import pdb
import json
db = pymysql.connect(host='bj-cynosdbmysql-grp-igalwqqk.sql.tencentcdb.com',
                        user='root',
                        password='UIBE_chat_2023',
                        database='fund_stream',
                        charset='utf8mb4',
                        port=25445,)
bankuai_path=r'F:\obsidian\Master\fund_stream_project\codes\framework\板块.txt'
cursor = db.cursor()
sql='select op,industry,emotion from opinions where emotion=1 or emotion=2 or emotion=3'
cursor.execute(sql)
result=cursor.fetchall()
# pdb.set_trace()
data=[(line[0]+'。对于'+get_inudstry_name(bankuai_path,line[1])+'板块',line[2]) for line in result]
# 打开一个文件用于写入
num_to_emo={1:'积极',2:'消极',3:'中立'}
with open(r'F:\obsidian\Master\fund_stream_project\codes\framework\output.jsonl', 'w', encoding='utf-8') as f:
    for text, label in data:
        json_obj = {"text": text, "label": num_to_emo[label]}
        f.write(json.dumps(json_obj, ensure_ascii=False) + '\n')