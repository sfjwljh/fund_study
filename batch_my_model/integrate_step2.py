# 把第二部请求得到的文件整合到统一的里面
import os
import sys
import json

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_req_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好_step2.json')
input_data_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好.json')
output_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好_step2_整合.json')

with open(input_data_file,'r',encoding='utf-8') as fin:
    data=fin.read()
    data=json.loads(data)

index2code_dict={}
for i,doc in enumerate(data):
    index2code_dict[doc['code']]=i


with open(input_req_file,'r',encoding='utf-8') as fin:
    for line in fin.readlines():
        content=json.loads(line)
        code=content['code']
        sentence_number=content['sentence_number']
        industry=content['industry']

        #把行业结果解析成列表
        response=content['response'].strip()
        try:
            response=eval(response)
            if not isinstance(response,list):
                continue
        except:
            continue
        data[index2code_dict[code]]['content'][sentence_number]['label_tree'][industry]={aspect:'' for aspect in response}

with open(output_file,'w',encoding='utf-8') as fout:
    fout.write(json.dumps(data, ensure_ascii=False, indent=4))
        



