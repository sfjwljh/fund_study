import re
import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from utils.api_request import Qianfan
from batch_data_ds.prompt import PROMPT1,PROMPT2,PROMPT3,PROMPT4
DOC_LENGTH=500 

input_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好_step3_整合.json')
output_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好_step4.json')

with open(input_file,'r',encoding='utf-8') as fin:
    data=fin.read()
    data=json.loads(data)

query_done=[]
if os.path.exists(output_file):
    with open(output_file,'r',encoding='utf-8') as fin:
        for line in fin.readlines():
            query_done.append(json.loads(line))

query_list=[]
# 用于请求的完整的列表

for ii,doc in enumerate(data):
    # code=doc['code']
    doc_number=ii
    content=doc['content']
    for i,part in enumerate(content):
        if not isinstance(part['label_tree'],dict): # 结果都不是字典，可能是错误了
            continue
        if len(part['label_tree'].keys())==0: # 字典为空，没有行业
            continue
        for industry in part['label_tree'].keys():
            if len(part['label_tree'][industry].keys())==0:  #该行业没有方面，跳过
                continue
            for aspect in part['label_tree'][industry].keys():
                if len(part['label_tree'][industry][aspect].keys())==0: #没有时间，跳过
                    continue

                # 时间。计算一次前缀
                prefix=""
                j=i-1
                while j>=0 and len(part['sentence'])+len(prefix)+len(content[j]['sentence'])<=DOC_LENGTH:
                    cur_pre=content[j]['sentence']
                    prefix=cur_pre+prefix
                    j-=1

                for time in part['label_tree'][industry][aspect].keys():
                    # 生成prompt
                    prompt=PROMPT4.format(pre=prefix,query=part['sentence'],industry=industry,aspect=aspect,time=time)
                    # 判断不在已经生成的里面
                    task={'doc_number':doc_number,'sentence_number':i,'industry':industry,'aspect':aspect,'time':time,'prompt':prompt}
                    done_flag=False
                    for done_task in query_done:
                        if done_task['doc_number']==task['doc_number'] and done_task['sentence_number']==task['sentence_number'] and done_task['industry']==task['industry'] and done_task['aspect']==task['aspect'] and done_task['time']==task['time']:
                            done_flag=True
                            break
                    if done_flag==False:
                        # 如果没有被处理过，再加入
                        query_list.append(task)

def process_query(query):
    """处理单个 query 的函数"""
    result = model.get_completion_bd(query=query['prompt'])
    if result:
        return {'doc_number': query['doc_number'], 'sentence_number': query['sentence_number'], 'industry': query['industry'],'aspect':query['aspect'], 'time':query['time'],'prompt': query['prompt'], 'response': result}
    else:
        print(f"Error processing query: {query}")
        return None

model = Qianfan('fyeblhsj_ljhs4_glm9b1')
with open(output_file, 'a', encoding='utf-8') as fout:
    with ThreadPoolExecutor(max_workers=20) as executor:  # 设置最大线程数
        future_to_query = {executor.submit(process_query, query): query for query in query_list}
        # 使用 tqdm 包装 as_completed 以显示进度条
        for future in tqdm(as_completed(future_to_query), total=len(query_list), desc="Processing queries"):
            result = future.result()
            if result:
                fout.write(json.dumps(result, ensure_ascii=False) + "\n")

