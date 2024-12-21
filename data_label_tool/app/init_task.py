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
        print("使用方法: python init_task.py <目录路径>")
        sys.exit(1)
    
    dir_path = sys.argv[1]
    if not os.path.isdir(dir_path):
        print("请提供有效的目录路径")
        sys.exit(1)
    
    # 遍历目录下的所有文件
    for filename in os.listdir(dir_path):
        if filename.endswith('.txt'):
            txt_path = os.path.join(dir_path, filename)
            # 构造对应的 json 文件路径
            json_filename = os.path.splitext(filename)[0] + '.json'
            json_path = os.path.join(dir_path, json_filename)
            
            # 检查是否已存在对应的 json 文件
            if not os.path.exists(json_path):
                print(f"处理文件：{filename}")
                create_json(txt_path)
            else:
                print(f"跳过已存在的文件：{filename}") 