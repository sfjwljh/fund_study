import json
import os
import pdb
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LABEL_DATA_DIR = os.path.join(BASE_DIR, '已标注汇总')
OUTPUT_DIR=os.path.join(BASE_DIR, 'alpaca_train.json')
DOC_LENGTH=500    #上下文总长度
total_num=0
unrelated=0
verifed_list=[]
illegal_collected={'industry':[],'level1':[],'time_attr':[],'score':[]}
def convert_to_alpaca_format(json_file_path, alpaca_data):
    global illegal_collected
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            # 使用 strict=False 允许放宽部分控制字符检查，但它不会修正漏逗号等语法错误
            data = json.load(file, strict=False)
    except json.JSONDecodeError as e:
        print(f"读取文件 {json_file_path} 时发生 JSONDecodeError: {e}")
        # 跳过当前格式错误的 JSON 文件
        return

    for i,entry in enumerate(data):
        global total_num,unrelated
        sentence = entry.get("sentence", "")
        # 句子平均长度42，最长216。
        prefix=""
        j=i-1
        while j>=0 and len(sentence)+len(prefix)+len(data[j]['sentence'].split("$$$")[-1])<=DOC_LENGTH:
            cur_pre=data[j]['sentence'].split("$$$")[-1]
            prefix=cur_pre+prefix
            j-=1

        sentence=prefix+"$$$"+sentence
        entities = entry.get("entities", [])
        if len(entities)==0:
            total_num+=1
            unrelated+=1
            continue
        
        for entity in entities:
            alpaca_entry = {
                "instruction": "",
                "input": sentence,
                "output": "",
            }
            total_num+=1

            if entity.get('score',"")=="":  #说明无关，根本没被点过
                related_flag=False
                alpaca_entry["output"]=json.dumps([{'status':"无关"}],ensure_ascii=False)
                alpaca_data.append(alpaca_entry)
                unrelated+=1
                continue
            # Convert entity to a string representation if needed

            # 删去不需要的字段
            keys_to_remove = {'level2', 'status', 'doubt_remark'}
            flitered_entity = {k: v for k, v in entity.items() if k not in keys_to_remove}

            # 检查封闭字段合法性
            allowed={"level1":['无关','上游产业情况','下游产业情况','行业自身情况','国家政策方向','宏观市场','子板块'],"time_attr":['过去','现在','未来','始终','无'],"score":['-2','-1','0','1','2']}
            
            illegal_keys=[key for key in allowed if flitered_entity.get(key) not in allowed.get(key)]
            if illegal_keys:
                print(f"非法字段{flitered_entity}\n句子：{sentence}\n键{illegal_keys}\n编号{json_file_path.replace(".json","")}\n")
                for ill_key in illegal_keys:
                    illegal_collected[ill_key].append(flitered_entity[ill_key])
                continue
            entities_str = json.dumps([flitered_entity], ensure_ascii=False)


            last_one=[]
            try:
                last_one=alpaca_data.pop()

            except:

                alpaca_entry['output'] = entities_str
                alpaca_data.append(alpaca_entry)
                continue


            # Create an Alpaca format entry
            alpaca_entry['output'] = entities_str

            if last_one['input']==alpaca_entry['input']:
                # pdb.set_trace()
                # 一句有多个实体
                if last_one['output']==alpaca_entry['output']:

                    #并且一级条目、时间、分数都相同，相当于重复
                    alpaca_data.append(last_one)
                    continue
                else:
                    # pdb.set_trace()
                    # 有不同
                    try:
                        last_one['output']=json.dumps(json.loads(last_one['output'])+(json.loads(alpaca_entry['output'])),ensure_ascii=False)
                        alpaca_data.append(last_one)
                        continue
                    except Exception as e:
                        pdb.set_trace()
                        print(e)
            
            alpaca_data.append(last_one)
            alpaca_data.append(alpaca_entry)

def process_directory(directory_path, output_file_path):


    alpaca_data = []
    
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            json_file_path = os.path.join(directory_path, filename)
            convert_to_alpaca_format(json_file_path, alpaca_data)
    
    # Write the combined Alpaca data to a single JSON file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(alpaca_data, output_file, ensure_ascii=False, indent=2)


process_directory(LABEL_DATA_DIR, OUTPUT_DIR)
print(f"总计{total_num-unrelated}条非空标注，{unrelated}条无关信息")
print(illegal_collected)