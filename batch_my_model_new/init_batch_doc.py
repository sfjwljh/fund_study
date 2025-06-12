
import re
import os
import sys
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import pdb
sys.path.append(BASE_DIR)
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from batch_data_ds.prompt import PROMPT1,PROMPT2,PROMPT3,PROMPT4
from utils.api_request import REQUEST_AI

DOC_LENGTH=500 

def load_sentence(txt_file):
    with open(txt_file, 'r', encoding='utf-8') as file:
        return file.read().strip()

def split_text_into_sentences(text):
    sentence_endings = r'[。！？]'
    sentences = re.split(sentence_endings, text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]

def create_empty_file(input_folder,output_json_file):
    """
    创建空的json文件，包含完整的json结构
    """
    files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]
    # input_txt_file = [os.path.join(BASE_DIR, 'data_label_tool/app/data/4428308.txt')]
    rel=[]
    with open(output_json_file, 'w', encoding='utf-8') as fout:
        for file in files:
            dump_doc={
                    'code':int(file.split('.')[0]),
                    'content':[]
                }
            sentences = split_text_into_sentences(load_sentence(os.path.join(input_folder,file)))

            for idx,sentence in enumerate(sentences) :
                dump_sentenc={
                    'sen_idx': idx ,  # 添加句子索引
                    'sentence':sentence,
                    'label_tree':{},
                    'label_flat':[]
                }
                dump_doc['content'].append(dump_sentenc)
            rel.append(dump_doc)
    with open(output_json_file, 'w', encoding='utf-8') as fout:
        fout.write(json.dumps(rel, ensure_ascii=False, indent=4))

def get_data_done(input_file,output_file):
    with open(input_file,'r',encoding='utf-8') as fin:
        data=fin.read()
        data=json.loads(data)

    query_done=[]
    if os.path.exists(output_file):
        with open(output_file,'r',encoding='utf-8') as fin:
            for line in fin.readlines():
                query_done.append(json.loads(line))
    return data, query_done
def get_task_step1(input_file,output_file):
    data, query_done=get_data_done(input_file,output_file)
    query_list=[]
    for doc in data:
        code=doc['code']
        content=doc['content']
        for i,part in enumerate(content):

            # 有行业。计算一次前缀
            prefix=""
            j=i-1
            while j>=0 and len(part['sentence'])+len(prefix)+len(content[j]['sentence'])<=DOC_LENGTH:
                cur_pre=content[j]['sentence']
                prefix=cur_pre+prefix
                j-=1


            # 生成prompt
            prompt=PROMPT1.format(pre=prefix,query=part['sentence'])
            # 判断不在已经生成的里面
            task={'code':doc['code'],'sentence_number':i,'prompt':prompt}
            done_flag=False
            for done_task in query_done:
                if done_task['code']==doc['code'] and done_task['sentence_number']==i :
                    done_flag=True
                    break
            if done_flag==False:
                # 如果没有被处理过，再加入
                query_list.append(task)
    return query_list
def get_task_step2(input_file,output_file):
    # pdb.set_trace()
    data, query_done=get_data_done(input_file,output_file)

    query_list=[]
    # 用于请求的完整的列表
    success=0

    for doc in data:
        code=doc['code']
        content=doc['content']
        for i,part in enumerate(content):
            if not isinstance(part['label_tree'],dict): # 结果都不是字典，可能是错误了
                continue
            if len(part['label_tree'].keys())==0: # 字典为空，没有行业
                continue

            # 有行业。计算一次前缀
            prefix=""
            j=i-1
            while j>=0 and len(part['sentence'])+len(prefix)+len(content[j]['sentence'])<=DOC_LENGTH:
                cur_pre=content[j]['sentence']
                prefix=cur_pre+prefix
                j-=1

            for industry in part['label_tree'].keys():
                # 生成prompt
                prompt=PROMPT2.format(pre=prefix,query=part['sentence'],industry=industry)
                # 判断不在已经生成的里面
                task={'code':doc['code'],'sentence_number':i,'industry':industry,'prompt':prompt}
                done_flag=False
                for done_task in query_done:
                    if done_task['code']==doc['code'] and done_task['sentence_number']==i and done_task['industry']==industry:
                        done_flag=True
                        break
                if done_flag==False:
                    # 如果没有被处理过，再加入
                    query_list.append(task)
                    success+=1
    print(f"number of success :{success}")
    # exit()
    return query_list
def get_task_step3(input_file,output_file):
    data, query_done=get_data_done(input_file,output_file)
    success=0
    query_list=[]
    for ii,doc in enumerate(data):
        # code=doc['code']
        doc_number=ii
        content=doc['content']
        for i,part in enumerate(content):
            if not isinstance(part['label_tree'],dict): # 结果都不是字典，可能是错误了
                continue
            if len(part['label_tree'].keys())==0: # 字典为空，没有行业
                continue
            for industry in part['label_tree'].keys():

                if part['label_tree'][industry]=='' or len(part['label_tree'][industry].keys())==0:  #该行业没有方面，跳过
                    continue

                # 有方面。计算一次前缀
                prefix=""
                j=i-1
                while j>=0 and len(part['sentence'])+len(prefix)+len(content[j]['sentence'])<=DOC_LENGTH:
                    cur_pre=content[j]['sentence']
                    prefix=cur_pre+prefix
                    j-=1

                for aspect in part['label_tree'][industry].keys():
                    # 生成prompt
                    prompt=PROMPT3.format(pre=prefix,query=part['sentence'],industry=industry,aspect=aspect)
                    # 判断不在已经生成的里面
                    task={'code':doc['code'],'sentence_number':i,'industry':industry,'aspect':aspect,'prompt':prompt}
                    done_flag=False
                    for done_task in query_done:
                        if done_task['code']==doc['code'] and done_task['sentence_number']==task['sentence_number'] and done_task['industry']==task['industry'] and done_task['aspect']==task['aspect']:
                            done_flag=True
                            break
                    if done_flag==False:
                        # 如果没有被处理过，再加入
                        query_list.append(task)
                        success+=1
    print(f"number of success :{success}")
    # exit()
    return query_list
def get_task_step4(input_file,output_file):
    data, query_done=get_data_done(input_file,output_file)
    success=0
    query_list=[]
    for ii,doc in enumerate(data):
        # code=doc['code']
        doc_number=ii
        content=doc['content']
        for i,part in enumerate(content):
            if not isinstance(part['label_tree'],dict): # 结果都不是字典，可能是错误了
                continue
            if len(part['label_tree'].keys())==0: # 字典为空，没有行业
                continue
            for industry in part['label_tree'].keys():
                if part['label_tree'][industry]=='' or len(part['label_tree'][industry].keys())==0:  #该行业没有方面，跳过
                    continue
                for aspect in part['label_tree'][industry].keys():
                    if part['label_tree'][industry][aspect]=='' or len(part['label_tree'][industry][aspect].keys())==0: #没有时间，跳过
                        continue

                    # 时间。计算一次前缀
                    prefix=""
                    j=i-1
                    while j>=0 and len(part['sentence'])+len(prefix)+len(content[j]['sentence'])<=DOC_LENGTH:
                        cur_pre=content[j]['sentence']
                        prefix=cur_pre+prefix
                        j-=1

                    for time in part['label_tree'][industry][aspect].keys():
                        # 生成prompt
                        prompt=PROMPT4.format(pre=prefix,query=part['sentence'],industry=industry,aspect=aspect,time=time)
                        # 判断不在已经生成的里面
                        task={'code':doc['code'],'sentence_number':i,'industry':industry,'aspect':aspect,'time':time,'prompt':prompt}
                        done_flag=False
                        for done_task in query_done:
                            if done_task['code']==doc['code'] and done_task['sentence_number']==task['sentence_number'] and done_task['industry']==task['industry'] and done_task['aspect']==task['aspect'] and done_task['time']==task['time']:
                                done_flag=True
                                break
                        if done_flag==False:
                            # 如果没有被处理过，再加入
                            query_list.append(task)
                            success+=1
    print(f"number of success :{success}")
    # exit()
    return query_list
def merge_step(input_req_file,input_data_file,output_file):

    with open(input_data_file,'r',encoding='utf-8') as fin:
        data=fin.read()
        data=json.loads(data)

    index2code_dict={}
    for i,doc in enumerate(data):
        index2code_dict[doc['code']]=i


    with open(input_req_file,'r',encoding='utf-8') as fin:
        for line in fin.readlines():
            content=json.loads(line)
            code=content['code']
            sentence_number=content['sentence_number']
            if 'time' in content.keys():
                industry=content['industry']
                aspect=content['aspect']
                time=content['time']
                step=4
            elif 'aspect' in content.keys():
                industry=content['industry']
                aspect=content['aspect']
                step=3
            elif 'industry' in content.keys():
                industry=content['industry']
                step=2
            else:
                step=1
            #把行业结果解析成列表(前三步)，step4是整数
            response=content['response'].strip()
            try:
                response=eval(response)
                if step!=4:
                    if not isinstance(response,list):
                        continue
                else:
                    if not isinstance(response,int):
                        continue

            except:
                continue
            if step==1:
                data[index2code_dict[code]]['content'][sentence_number]['label_tree']={industry:'' for industry in response}
            elif step==2:
                data[index2code_dict[code]]['content'][sentence_number]['label_tree'][industry]={aspect:'' for aspect in response}
            elif step==3:
                data[index2code_dict[code]]['content'][sentence_number]['label_tree'][industry][aspect]={time:'' for time in response}
            elif step==4:
                data[index2code_dict[code]]['content'][sentence_number]['label_tree'][industry][aspect][time]=response

    with open(output_file,'w',encoding='utf-8') as fout:
        fout.write(json.dumps(data, ensure_ascii=False, indent=4))
def process_query(query):
    """处理单个 query 的函数"""
    # pdb.set_trace()
    # model=REQUEST_AI('vllm','path_to_model')
    result = model.get_completion(prompt=query['prompt'],ignore_thinking=True)
    
    if result:
        if 'time' in query.keys():
            return {'code': query['code'], 'sentence_number': query['sentence_number'], 'industry': query['industry'],'aspect':query['aspect'], 'time':query['time'],'prompt': query['prompt'], 'response': result}
        elif 'aspect' in query.keys():
            return {'code': query['code'], 'sentence_number': query['sentence_number'], 'industry': query['industry'],'aspect':query['aspect'], 'prompt': query['prompt'], 'response': result}
        elif 'industry' in query.keys():
            return {'code': query['code'], 'sentence_number': query['sentence_number'], 'industry': query['industry'], 'prompt': query['prompt'], 'response': result}
        else:
            return {'code': query['code'], 'sentence_number': query['sentence_number'], 'prompt': query['prompt'], 'response': result}
    else:
        print(f"Error processing query: {query}")
        return None
def request_batch(output_file, query_list,max_workers=3):
    with open(output_file, 'a', encoding='utf-8') as fout:
        with ThreadPoolExecutor(max_workers) as executor:  # 设置最大线程数
            future_to_query = {executor.submit(process_query, query): query for query in query_list}
            # 使用 tqdm 包装 as_completed 以显示进度条
            for future in tqdm(as_completed(future_to_query), total=len(query_list), desc="Processing queries"):
                result = future.result()
                if result:
                    fout.write(json.dumps(result, ensure_ascii=False) + "\n")
if __name__ == "__main__":
    model=REQUEST_AI('volcano','r1')
    file_name='人工标注的第一个10篇'
    print("_____________输出空INIT文件___________")
    input_folder=os.path.join(BASE_DIR, r'batch_my_model_new/人工标注的第一个10篇')
    output_file = os.path.join(BASE_DIR, 'batch_my_model_new/'+file_name+'_init.json')
    create_empty_file(input_folder, output_file)
    # 读取一个目录下的所有txt文稿，生成json文件，格式是readme中提到的
    # 读取未标注的原txt文件，然后形成第一步标注的请求文件
    print("_____________初始化完成,开始推理step1___________")


    for i in range(1,5):
    
        input_file=output_file
        output_file_req=os.path.join(BASE_DIR, 'batch_my_model_new/'+file_name+'_step'+str(i)+'_req.json')
        if i==1:
            query_list= get_task_step1(input_file, output_file_req)
        elif i==2:
            query_list= get_task_step2(input_file, output_file_req)
        elif i==3:
            query_list= get_task_step3(input_file, output_file_req)
        elif i==4:
            query_list= get_task_step4(input_file, output_file_req)

        request_batch(output_file_req,query_list,max_workers=60)
        print("_____________step"+str(i)+"推理完成,开始合并step"+str(i)+"___________")
        input_req_file=output_file_req  # 推理结果文件
        input_data_file=input_file  # 初始的json
        output_file=os.path.join(BASE_DIR, 'batch_my_model_new/'+file_name+'_step'+str(i)+'_merged.json')  #补充好的json
        merge_step(input_req_file, input_data_file, output_file)
        if i!=4:
            print("_____________step"+str(i)+"合并完成,开始推理step"+str(i)+"___________")
        else:
            print("_____________step"+str(i)+"合并完成___________")





