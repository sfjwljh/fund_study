# 把第三步请求得到的文件整合到统一的里面
import os
import sys
import json

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_req_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好_step3.json')
input_data_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好_step2_整合.json')
output_file=os.path.join(BASE_DIR,r'batch_my_model/0327第一批1952篇_补充好_step3_整合.json')

with open(input_data_file,'r',encoding='utf-8') as fin:
    data=fin.read()
    data=json.loads(data)




with open(input_req_file,'r',encoding='utf-8') as fin:
    for line in fin.readlines():
        content=json.loads(line)
        doc_number=content['doc_number']
        sentence_number=content['sentence_number']
        industry=content['industry']
        aspect=content['aspect']

        #把时间结果解析成列表
        response=content['response'].strip()
        try:
            response=eval(response)
            if not isinstance(response,list):
                continue
        except:
            continue
        data[doc_number]['content'][sentence_number]['label_tree'][industry][aspect]={time:'' for time in response}

with open(output_file,'w',encoding='utf-8') as fout:
    fout.write(json.dumps(data, ensure_ascii=False, indent=4))
        



