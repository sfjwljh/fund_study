# 读取一个目录下的所有txt文稿，生成json文件，格式是readme中提到的
# 读取未标注的原txt文件，然后形成第一步标注的请求文件
import re
import os
import sys
import json
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from batch_data_ds.prompt import PROMPT1,PROMPT2,PROMPT3,PROMPT4
def load_sentence(txt_file):
    with open(txt_file, 'r', encoding='utf-8') as file:
        return file.read().strip()

def split_text_into_sentences(text):
    sentence_endings = r'[。！？]'
    sentences = re.split(sentence_endings, text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]

if __name__ == "__main__":
    input_folder=r'/Users/liujianhui02/Desktop/基金直播txt/first_batch'
    files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]
    # input_txt_file = [os.path.join(BASE_DIR, 'data_label_tool/app/data/4428308.txt')]
    output_json_file = os.path.join(BASE_DIR, 'batch_my_model/第一批1952篇汇总.json')
    rel=[]
    with open(output_json_file, 'w', encoding='utf-8') as fout:
        for file in files:
            dump_doc={
                    'code':int(file.split('.')[0]),
                    'content':[]
                }
            sentences = split_text_into_sentences(load_sentence(os.path.join(input_folder,file)))

            for sentence in sentences:
                dump_sentenc={
                    'sentence':sentence,
                    'label_tree':{},
                    'label_flat':[]
                }
                dump_doc['content'].append(dump_sentenc)
            rel.append(dump_doc)
    with open(output_json_file, 'w', encoding='utf-8') as fout:
        fout.write(json.dumps(rel, ensure_ascii=False, indent=4))

