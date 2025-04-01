# 把第二部请求得到的文件整合到统一的里面
import os
import sys
import json
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_req_file=os.path.join(BASE_DIR,r'batch_my_model/test_integrate_step2.json')
input_data_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好.json')
output_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好_step2_整合test.json')

with open(input_data_file,'r',encoding='utf-8') as fin:
    data=fin.read()
    data=json.loads(data)

with open(input_req_file,'r',encoding='utf-8') as fin:
    for line in fin.readlines():
        content=json.loads(line)
        code=content['code']
        sentence_number=content['sentence_number']
        industry=content['industry']
        response=content['response'].strip()
        try:
            