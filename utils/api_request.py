# 火山的ds
import os
import pdb
import time
from openai import OpenAI
from typing import List, Dict, Tuple, Union, Any, Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import json
import hashlib
import json


import time
# import pandas as pd
import requests
class Qianfan():
    def __init__(self,url):
        self.url = url
        self.API_KEY = "F49JHlNCPZOavDQqEjQeD3gs"
        self.SECRET_KEY = "Nt31T10pCQVXXPKPOK7ymDMgS0RLQATL"
    def get_access_token(self):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.API_KEY,
            "client_secret": self.SECRET_KEY,
        }
        return str(requests.post(url, params=params).json().get("access_token"))


    def get_completion_bd(self,query, temperature=0.01):
        address=self.url
        ACCESS_TOKEN = self.get_access_token()
        address = (
            address
            if address.startswith("https")
            else f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{address}"
        )

        header={"Content-Type": "application/json"}
        request_msg = {
            "messages": [{"role": "user", "content": query}],
            "temperature": temperature,
            "top_p": 0.8,
            "penalty_score": 1.2,
            "disable_search": True,
        }
        url = address + "?access_token=" + ACCESS_TOKEN
        # import pdb;pdb.set_trace()
        get_response = False
        fail_num=0
        while not get_response:
            fail_num+=1
            # import pdb;pdb.set_trace()
            try:
                response = requests.post(
                    url, headers=header, data=json.dumps(request_msg)
                )
                res_text = response.text
                if json.loads(res_text)["result"]!='':
                    return json.loads(res_text)["result"]
                elif json.loads(res_text)["choices"][0]["message"]["content"] != '':
                    return json.loads(res_text)["choices"][0]["message"]["content"]
                else:
                    raise Exception('解析错误')
            except Exception as e:
                time.sleep(2)
                print(e)
                # print("get_completion"+address+'请求失败'+str(fail_num)+'次')
                continue



    def api_auth_sign(self,params):
        # Concatenate all strings in the list
        concatenated = "".join(params)

        # Create an MD5 hash of the concatenated string
        md5_hash = hashlib.md5(concatenated.encode("utf-8")).hexdigest()

        # Check if the length of the hash is less than 22
        if len(md5_hash) < 22:
            return ""

        # Specific indices from which to pick characters from the MD5 hex string
        auth_indices = [7, 3, 17, 13, 1, 21]

        # Build the result string using characters at the specified indices
        result = ""
        for idx in auth_indices:
            result += md5_hash[idx]

        return result
class REQUEST_AI():
    def __init__(self,platform,model,max_retries=10):
        """
        platform: str
            平台名称,目前可选 
            volcano: 火山引擎
            deepseek: deepseek官方
        model: str
            模型名称
            r1
            v3
            doubao-1-5-pro-32k


        """
        self.max_retries = max_retries
        self.platform = platform   
        if platform=="volcano":
            self.client = OpenAI(
                api_key = "e76c1633-14c0-4c05-ab0d-1f2a8312953c",
                base_url = "https://ark.cn-beijing.volces.com/api/v3",
            )
        elif platform=="deepseek":
            self.client = OpenAI(
                api_key="sk-e6ea0646178e47f294e3d639646c707a", 
                base_url="https://api.deepseek.com"
            )
        platform_model_dict={
            "volcano":{
                "r1":"deepseek-r1-250120",
                'doubao-1-5-pro-32k':'doubao-1-5-pro-32k-250115',

            },
            "deepseek":{
                "r1":"deepseek-reasoner",
                "v3":"deepseek-chat",

            }
        }
        self.model=platform_model_dict[platform][model]




    def get_completion(self,prompt):
        client = self.client
        try:
            completion = client.chat.completions.create(
                model = self.model,  # your model endpoint ID
                messages = [
                    {"role": "system", "content": ""},
                    {"role": "user", "content": prompt},
                ],
            )
            # pdb.set_trace()
            if hasattr(completion.choices[0].message, 'reasoning_content'):
                return "<think>"+completion.choices[0].message.reasoning_content+"</think>"+completion.choices[0].message.content
            else:
                return completion.choices[0].message.content
        except Exception as e:
            print(f"Error: {str(e)}")
            return ''
    
    def get_batch(
            self,queries:Union[List[str], List[List[str]]], max_workers: int = 5
        )->Generator[str,None,None]:
        # pdb.set_trace()
        if isinstance(queries, list) and all(
            [isinstance(item, str) for item in queries]
        ):
            queries = [query for query in queries]
            origin_queries = queries
        elif isinstance(queries, list) and all(
            [isinstance(item, List) for item in queries]
        ):
            origin_queries = [item[0] for item in queries]
            queries = [item[1] for item in queries]
        total_queries = len(queries)
        # pdb.set_trace()
        progress_bar = tqdm(
            total=total_queries, desc="Processing queries", unit="query"
        )

        completed_count = 0
        successful_count = 0
        failed_count = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_query = {
                    executor.submit(self.process_single_query, origin_query,query): (
                        origin_query,
                        query,
                    )
                    for origin_query,query  in zip(origin_queries, queries)
                }

                for future in as_completed(future_to_query):
                    result = future.result()
                    completed_count += 1

                    if result["status"] == "success":
                        successful_count += 1
                    else:
                        failed_count += 1

                    progress_bar.update(1)
                    progress_bar.set_postfix(
                        {
                            "success": successful_count,
                            "failed": failed_count,
                            "success_rate": f"{(successful_count/completed_count)*100:.1f}%",
                        }
                    )

                    yield result

        progress_bar.close()

        # 打印最终统计信息
        print("\nFinal Statistics:")
        print(f"Total Processed: {completed_count}")
        print(f"Successful: {successful_count}")
        print(f"Failed: {failed_count}")
        print(f"Success Rate: {(successful_count/completed_count)*100:.1f}%")
    def process_single_query(
        self, origin_query: str,query: str= None
    ) -> Dict[str, Any]:
        result = None
        start_time = time.time()
        if not query:
            query = origin_query
        for attempt in range(self.max_retries):
            try:
                result = self.get_completion(query)
                if result:
                    elapsed_time = time.time() - start_time
                    return {
                        "query": origin_query,
                        "status": "success",
                        "result": result,
                        "elapsed_time": elapsed_time,
                    }
            except Exception as e:
                if attempt == self.max_retries - 1:
                    print(f"Error: {str(e)}")

        return {
            "query": origin_query,
            "status": "failed",
            "result": None,
            "elapsed_time": time.time() - start_time,
        }
    
if __name__=="__main__":
    #请求千帆
    qianfan_req=Qianfan('acs694cz_ljhs2_glm9b1')
    print(qianfan_req.get_completion_bd(query='你好'))
    exit()
    
    BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    volcano=REQUEST_AI(platform='volcano',model='r1')
    volcano.get_completion("你好")
    ds=REQUEST_AI(platform='deepseek',model='r1')
    # input_file=os.path.join(BASE_DIR,r'ds_label/test.json')
    input_file=os.path.join(BASE_DIR,r'ds_label/step1_input_batch.json')
    query_list=[]
    
    with open(input_file,'r',encoding='utf-8') as fin:
        for line in fin:
            try: 
                query_list.append(json.loads(line)['prompt'])
            except Exception as e:
                print("error",e)
                continue
    if 'input' in input_file:
        output_file=input_file.replace('input','output_带思考')
    else:
        print("输入文件名不包含input字样，输出文件将覆盖输入文件，是否接受？y/n")
        if input()=='y':
            output_file=input_file
        else:
            exit()
    # query_list=[{"prompt":"你好"}]
    # print(output_file)
    # exit()
    with open(output_file,'w',encoding='utf-8') as fout:
        for result in volcano.get_batch(query_list, max_workers=50):
            try:
                elapsed_time = ''
                query = result["query"]
                res = result["result"]
                stat = result["status"]

                fout.write(json.dumps({'input':query,'output':res},ensure_ascii=False)+"\n")
                fout.flush()
            except Exception as e:
                print("error",e)

    