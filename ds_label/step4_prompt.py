import json
import os
import sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import pdb
from batch_data_ds.prompt import PROMPT1,PROMPT2,PROMPT3,PROMPT4
input_file=os.path.join(BASE_DIR,r'ds_label/step3_output_batch.json')
output_file=os.path.join(BASE_DIR,r'ds_label/step4_input_batch.json')
with open(input_file,'r',encoding='utf-8') as fin,open(output_file,'w',encoding='utf-8') as fout:
    for line in fin:
        try:
            input=json.loads(line)['input']
            output=json.loads(line)['output'].strip()
            time_list=eval(output)
            content=input.split('```')[-2]
            pre=content.split('# 前文')[1].split('# 正文')[0].strip()
            query=content.split('# 正文')[1].split('# 针对的行业：')[0].strip()
            industry=content.split('# 针对的行业：')[1].split('# 关注的方面：')[0].strip()
            aspect=content.split('# 关注的方面：')[1].strip()
            for time in time_list:
                final_prompt=PROMPT4.format(pre=pre,query=query,industry=industry,aspect=aspect,time=time)
                fout.write(json.dumps({'prompt':final_prompt},ensure_ascii=False)+"\n")
            # pdb.set_trace()
        except Exception as e:
            print("error",e)
            continue
