import json
import random
import os
base=r'F:\obsidian\Master\fund_stream_project\codes\framework'
# 定义划分比例
train_ratio = 0.8  # 80% 作为训练集，20% 作为测试集

# 读取jsonl文件
with open(os.path.join(base,'output.jsonl'), 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 打乱数据
random.shuffle(lines)

# 按照比例划分
split_index = int(len(lines) * train_ratio)
train_data = lines[:split_index]
test_data = lines[split_index:]

# 将数据写入train.jsonl和test.jsonl文件
with open(os.path.join(base,'train.jsonl'), 'w', encoding='utf-8') as f_train:
    for line in train_data:
        f_train.write(line)

with open(os.path.join(base,'test.jsonl'), 'w', encoding='utf-8') as f_test:
    for line in test_data:
        f_test.write(line)

print("数据集已按照比例划分为train和test")
