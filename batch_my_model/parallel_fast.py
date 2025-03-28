# encoding: utf-8
import json
from collections import Counter
import os
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 读取数据
prompt_code_pairs = []
with open(os.path.join(BASE_DIR, r'ds_label/第一批1952篇-校对编号-不带prefix.jsonl'), 'r', encoding='utf-8') as fin:
    for line in fin:
        line = json.loads(line)
        prompt_code_pairs.append((line['prompt'], line['code']))

# 统计 prompt 出现的次数
prompt_counts = Counter(p for p, c in prompt_code_pairs)

# 过滤出只出现一次的 (prompt, code) 对
unique_prompt_code_pairs = [(p, c) for p, c in prompt_code_pairs if prompt_counts[p] == 1]

# 读取 batch_rel，转换为字典（O(1) 查询）
batch_rel_dict = {}
with open('/Users/liujianhui02/Desktop/0327第一批1952篇.json', 'r', encoding='utf-8') as fin:
    for line in fin:
        line = json.loads(line)
        sentence = line['prompt'].split('# 正文\n')[-1].split('\n```\n输出')[0]
        try:
            response = line['response'].strip()
        except:
            continue
        batch_rel_dict[sentence] = response  # 直接存到字典里，方便快速查询

# 读取 data，转换为字典（O(1) 查询）
with open(r'/Users/liujianhui02/Desktop/sync/obsidian/Master/fund_stream_project/codes/batch_my_model/第一批1952篇汇总.json', 'r', encoding='utf-8') as fin:
    data = json.load(fin)

# 创建 code -> doc 映射，方便 O(1) 查询
data_dict = {doc['code']: doc for doc in data}

# 遍历 unique_prompt_code_pairs 进行匹配
for prompt, code in tqdm(unique_prompt_code_pairs, total=len(unique_prompt_code_pairs)):
    if prompt not in batch_rel_dict:
        continue

    response = batch_rel_dict[prompt]
    try:
        response = eval(response)  # 解析为 Python list
        assert isinstance(response, list)
    except:
        continue

    # 生成 label_tree
    rel_tmp = {res_industry: {} for res_industry in response}

    # 直接查询 code 是否在 data_dict 里
    if code not in data_dict:
        continue

    doc = data_dict[code]

    # 在 doc['content'] 中找到匹配的 sentence，并修改 label_tree
    for sentence in doc['content']:
        if sentence['sentence'] == prompt:
            sentence['label_tree'] = rel_tmp  # 直接修改数据结构

# 保存优化后的 JSON
with open(r"/Users/liujianhui02/Desktop/0327第一批1952篇_补充好.json", 'w', encoding='utf-8') as fout:
    fout.write(json.dumps(data, ensure_ascii=False, indent=4))