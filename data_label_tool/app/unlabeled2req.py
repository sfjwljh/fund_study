# 读取未标注的原txt文件，然后形成第一步标注的请求文件
import re
import os
import sys
import json
BASE_DIR=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    input_foler=r'/Users/liujianhui02/Desktop/基金直播txt/first_batch'
    files=os.listdir(input_foler)
    # input_txt_file = [os.path.join(BASE_DIR, 'data_label_tool/app/data/4428308.txt')]
    output_json_file = os.path.join(BASE_DIR, 'ds_label/第一批1952篇-校对编号-不带prefix.jsonl')
    with open(output_json_file, 'w', encoding='utf-8') as fout:
        for file in files:
            sentences = split_text_into_sentences(load_sentence(os.path.join(input_foler,file)))
            DOC_LENGTH=500    #上下文总长度
            for i,sentence in enumerate(sentences):
                # 句子平均长度42，最长216。
                prefix=""
                j=i-1
                while j>=0 and len(sentence)+len(prefix)+len(sentences[j])<=DOC_LENGTH:
                    cur_pre=sentences[j]
                    prefix=cur_pre+prefix
                    j-=1
                line=PROMPT1.format(pre=prefix,query=sentence)
                fout.write(json.dumps({'code':int(file.split('.')[0]),'prompt':sentence}, ensure_ascii=False)+"\n")
                # fout.write(json.dumps({'prompt':line,'response':''}, ensure_ascii=False)+"\n")
