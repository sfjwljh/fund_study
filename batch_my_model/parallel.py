# encoding: utf-8
import json
from collections import Counter
import os
import pdb
from tqdm import tqdm
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 读取数据
prompt_code_pairs = []  # 存储 (prompt, code) 对
with open(os.path.join(BASE_DIR,r'ds_label/第一批1952篇-校对编号-不带prefix.jsonl'), 'r', encoding='utf-8') as fin:
    for line in fin:
        line = json.loads(line)
        prompt_code_pairs.append((line['prompt'], line['code']))

# 统计 prompt 出现的次数
prompt_counts = Counter(p for p, c in prompt_code_pairs)

# 过滤出只出现一次的 (prompt, code) 对
unique_prompt_code_pairs = [(p, c) for p, c in prompt_code_pairs if prompt_counts[p] == 1]
# print(f"唯一的 prompt 数量: {len(unique_prompt_code_pairs)}")

batch_rel=[]
# 是[句子，标注行业列表]的二维俩表
with open('/Users/liujianhui02/Desktop/0327第一批1952篇.json','r',encoding='utf-8') as fin:
    for line in fin:
        line=json.loads(line)
        sentece=line['prompt'].split('# 正文\n')[-1].split('\n```\n输出')[0]
        try:
            batch_rel.append([sentece,line['response'].strip()])
        except:
            # pdb.set_trace()
            continue

with open(r'/Users/liujianhui02/Desktop/sync/obsidian/Master/fund_stream_project/codes/batch_my_model/第一批1952篇汇总.json','r',encoding='utf-8') as fin:
    data=json.load(fin)
# pdb.set_trace()
for prompt,code in tqdm(unique_prompt_code_pairs):
    # 找到不重复的句子和编号
    response=[x[1] for x in batch_rel if x[0]==prompt]
    # 找到标注文档中该句子的标注结果
    if  len(response)!=1:
        continue
    response=response[0].strip()
    try:
        response=eval(response)
        assert(isinstance(response,list))
    except:
        continue

    rel_tmp = {res_industry: {} for res_industry in response}
    for i,doc in enumerate(data):
        if doc['code']!=code:
            continue
        # 找到编号对应的文档
        for j,sentence in enumerate(doc['content']):
            if sentence['sentence']!=prompt:
                continue
            # 找到对应的句子
            data[i]['content'][j]['label_tree']=rel_tmp
with open(r"/Users/liujianhui02/Desktop/0327第一批1952篇_补充好.json", 'w', encoding='utf-8') as fout:
    fout.write(json.dumps(data, ensure_ascii=False, indent=4))

