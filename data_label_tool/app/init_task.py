import os
import json
import re

def load_sentence(txt_file):
    with open(txt_file, 'r', encoding='utf-8') as file:
        return file.read().strip()

def split_text_into_sentences(text):
    sentence_endings = r'[。！？]'
    sentences = re.split(sentence_endings, text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]

def create_json(txt_path):
    # 获取文件名（不含扩展名）
    base_name = os.path.splitext(os.path.basename(txt_path))[0]
    
    # 创建 data 目录（如果不存在）
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # 构造 json 文件路径
    json_path = os.path.join(data_dir, f"{base_name}.json")
    
    # 读取并处理文本
    content = load_sentence(txt_path)
    sentences = split_text_into_sentences(content)
    data = [{"sentence": sentence, "entities": []} for sentence in sentences]
    
    # 保存 JSON 文件
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)
    
    print(f"已创建 JSON 文件：{json_path}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("使用方法: python init_task.py <txt文件路径>")
        sys.exit(1)
    
    txt_path = sys.argv[1]
    if not txt_path.endswith('.txt'):
        print("请提供 .txt 文件")
        sys.exit(1)
    
    create_json(txt_path) 