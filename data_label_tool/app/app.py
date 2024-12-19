from flask import Flask, render_template, request, jsonify
import os
import json
import re
import sys
app = Flask(__name__)
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)


# 中文句子分隔符正则
sentence_endings = r'[。！？]'


# 加载文本文件内容
def load_sentence(txt_file):
    with open(txt_file, 'r', encoding='utf-8') as file:
        return file.read().strip()

# 将文本分割为句子
def split_text_into_sentences(text):
    sentences = re.split(sentence_endings, text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]
def create_json(txt_path, json_path):
    content = load_sentence(txt_path)
    sentences = split_text_into_sentences(content)
    
    # 创建包含句子和空实体列表的字典
    data = [{"sentence": sentence, "entities": []} for sentence in sentences]
    
    # 将数据写入JSON文件
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

# 新增：获取启动参数
if len(sys.argv) ==2:
    input_arg = sys.argv[1]
    if input_arg.endswith('.json'):
        json_file = input_arg  # 直接使用json文件路径
    elif input_arg.endswith('.txt'):
        # import pdb;pdb.set_trace()
        base_name = os.path.splitext(os.path.basename(input_arg))[0]  # 提取文件名不包含后缀
        json_file=os.path.join(BASE_DIR,f"data/{base_name}.json")
        if not os.path.exists(json_file):
            create_json(input_arg,json_file)
    elif input_arg.isdigit():
        base_name = os.path.join(BASE_DIR,f"data/{input_arg}.json")  # 使用编号构造json文件路径
        json_file = base_name
    else:
        print("无效的输入参数")
        sys.exit(1)
else:
    print("请输入待处理的文件路径或编号，启动格式` python app.py txt或json文件的路径或者编号`，比如：\n python app.py F:\\BaiduSyncdisk\\obsidian\\Master\\fund_stream_project\\codes\\data_label_tool\\app\\data\\3853966.json\n或者\npython app.py F:\\BaiduSyncdisk\\obsidian\\Master\\fund_stream_project\\codes\\data_label_tool\\data\\3853966.txt \n或者\n python app.py 386573")
    exit()




# 加载JSON数据
def load_json_data():
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# 保存标注数据到JSON
def save_json_data(data):
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 首页
@app.route('/')
def index():
    return render_template("index.html")

# 获取句子列表
@app.route('/get_sentences')
def get_sentences():
    data_list = load_json_data()
    return jsonify(data_list)

# 获取指定句子的实体数据
@app.route('/get_entities/<int:sentence_id>', methods=['GET'])
def get_entities(sentence_id):
    data_list = load_json_data()
    if sentence_id < len(data_list):
        return jsonify(data_list[sentence_id]["entities"])
    return jsonify([])

# 更新实体数据
@app.route('/save_entities', methods=['POST'])
def save_entities():
    data = request.json
    sentence_id = data['sentence_id']
    entities = data['entities']
    
    data_list = load_json_data()
    if sentence_id < len(data_list):
        data_list[sentence_id]["entities"] = entities
        save_json_data(data_list)
        return jsonify({"message": "数据已保存"})
    return jsonify({"message": "错误：句子 ID 无效"}), 400

# 启动服务器
if __name__ == '__main__':
    app.run(debug=True, port=15207)
