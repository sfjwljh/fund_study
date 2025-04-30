import re
import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

input_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好_step4_整合.json')
output_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好_step4_整合_带flat.json')
with open(input_file,'r',encoding='utf-8') as fin:
    data=json.loads(fin.read())

def check_valid(label_flat):
    """
    检查四个字段的合法性
    """
    industry_list=["医疗保健","生物医药","疫苗","证券公司","机器人","半导体","化工","有色金属","新能源","通信","农业","环保","金融","军工","银行","电力","传媒","互联网","食品饮料","汽车","煤炭","建筑材料","光伏","电子","房地产","物联网","智能汽车","中药","新材料","畜牧养殖","装备产业","运输","钢铁","高铁","低碳经济","基建工程","能源化工","绿色电力","饲料豆粕","工业互联网","车联网","云计算","数字经济","财富管理","高端制造","保险","芯片","金融科技","软件服务","房地产","石油天然气","计算机","装备制造","清洁能源","生物科技","宏观市场"]
    aspect_list=["上游产业情况","下游产业情况","行业自身情况","国家政策方向","宏观市场","子板块"]
    time_list=["现在","未来","过去","始终"]
    emotion_list=[-2,-1,0,1,2]
    if label_flat['industry'] not in industry_list:
        return False
    if label_flat['aspect'] not in aspect_list:
        return False
    if label_flat['time'] not in time_list:
        return False
    if label_flat['emotion'] not in emotion_list:
        return False
    return True

for doc_ind,doc in enumerate(data):
    for part_ind,part in enumerate(doc['content']):
        label_tree=part['label_tree']
        label_flat=[]
        for industry in label_tree.keys():
            for aspect in label_tree[industry].keys():
                for time in label_tree[industry][aspect].keys():
                    tmp={"industry":industry,"aspect":aspect,"time":time,"emotion":label_tree[industry][aspect][time]}
                    if check_valid(tmp):
                        label_flat.append(tmp)
        # data[doc_ind]['content'][part_ind]['label_flat']=label_flat
        part['label_flat']=label_flat

with open(output_file,'w',encoding='utf-8') as fout:
    fout.write(json.dumps(data,ensure_ascii=False,indent=4))


output_file_csv=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_整合好.csv')
with open(output_file_csv,'w',encoding='utf-8')as fout:
    # 生成flat的csv
    for doc in data:
        code=doc['code']
        for part in doc['content']:
            sentence=part['sentence'].replace('\n','')
            for label_flat in part['label_flat']:
                content_line=[str(code),sentence,label_flat['industry'],label_flat['aspect'],label_flat['time'],str(label_flat['emotion'])]
                fout.write('\t'.join(content_line)+'\n')