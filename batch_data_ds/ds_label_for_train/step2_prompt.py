import json
import os
import sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import pdb
from batch_data_ds.prompt import PROMPT1,PROMPT2,PROMPT3,PROMPT4
input_file=os.path.join(BASE_DIR,r'ds_label/step1_output_batch.json')
output_file=os.path.join(BASE_DIR,r'ds_label/step2_input_batch.json')
with open(input_file,'r',encoding='utf-8') as fin,open(output_file,'w',encoding='utf-8') as fout:
    for line in fin:
        try:
            input=json.loads(line)['input']
            output=json.loads(line)['output'].strip()
            industry_list=eval(output)
            content=input.split('```')[-2]
            pre=content.split('# 前文')[1].split('# 正文')[0].strip()
            query=content.split('# 正文')[1].strip()
            for industry in industry_list:
                final_prompt=PROMPT2.format(pre=pre,query=query,industry=industry)
                fout.write(json.dumps({'prompt':final_prompt},ensure_ascii=False)+"\n")
            # pdb.set_trace()
        except Exception as e:
            print("error",e)
            continue
