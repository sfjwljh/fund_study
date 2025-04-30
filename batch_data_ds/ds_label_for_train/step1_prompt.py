import json
import pdb
import sys
import os
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)
sys.path.append(BASE_DIR)
from batch_data_ds.prompt import PROMPT1,PROMPT2,PROMPT3,PROMPT4
# exit()
input_file=os.path.join(BASE_DIR,r'data_label_tool/app/alpaca_train.json')
output_file=os.path.join(BASE_DIR,r'ds_label/step1_input_batch.json')



def get_train_s1():
    with open(input_file,'r',encoding='utf-8') as fin,open(output_file,'w',encoding='utf-8') as fout:
        for line in json.loads(fin.read()):
            train_line={'system':'','prompt':'','response':''}
            train_line['system']=''
            train_line['prompt']=PROMPT1.format(query=line.get('input',''))
            fout.write(json.dumps(train_line,ensure_ascii=False)+"\n")
            # pdb.set_trace()

def get_batch_input_s1():
    with open(input_file,'r',encoding='utf-8') as fin,open(output_file,'w',encoding='utf-8') as fout:
        for line in json.loads(fin.read()):
            input=line.get('input','')
            pre=input.split('$$$')[0]
            query=input.split('$$$')[1]
            prompt= PROMPT1.format(pre=pre,query=query)
            fout.write(json.dumps({'prompt':prompt},ensure_ascii=False)+"\n")
get_batch_input_s1()