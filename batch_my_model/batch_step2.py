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

input_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好.json')
output_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好_step2.json')

with open(input_file,'r',encoding='utf-8') as fin:
    data=fin.read()
    data=json.loads(data)

query_list=[]
# 用于请求的完整的列表

for doc in data:
    code=doc['code']
    content=doc['content']
    for i,part in enumerate(content):
        if not isinstance(part['label_tree'],dict): # 结果都不是字典，可能是错误了
            continue
        if len(part['label_tree'].keys())==0: # 字典为空，没有行业
            continue

        # 有行业。计算一次前缀
        prefix=""
        j=i-1
        while j>=0 and len(part['sentence'])+len(prefix)+len(content[j]['sentence'])<=DOC_LENGTH:
            cur_pre=content[j]['sentence']
            prefix=cur_pre+prefix
            j-=1

        for industry in part['label_tree'].keys():
            # 生成prompt
            prompt=PROMPT2.format(pre=prefix,query=part['sentence'],industry=industry)
            query_list.append({'code':doc['code'],'sentence_number':i,'industry':industry,'prompt':prompt})

def process_query(query):
    """处理单个 query 的函数"""
    result = model.get_completion_bd(query=query['prompt'])
    if result:
        return {'code': query['code'], 'sentence_number': query['sentence_number'], 'industry': query['industry'], 'prompt': query['prompt'], 'response': result}
    else:
        print(f"Error processing query: {query}")
        return None

model = Qianfan('acs694cz_ljhs2_glm9b1')
with open(output_file, 'w', encoding='utf-8') as fout:
    with ThreadPoolExecutor(max_workers=4) as executor:  # 设置最大线程数
        future_to_query = {executor.submit(process_query, query): query for query in query_list}
        # 使用 tqdm 包装 as_completed 以显示进度条
        for future in tqdm(as_completed(future_to_query), total=len(query_list), desc="Processing queries"):
            result = future.result()
            if result:
                fout.write(json.dumps(result, ensure_ascii=False) + "\n")

