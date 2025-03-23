# 火山的ds
import os
import pdb
import time
from openai import OpenAI
from typing import List, Dict, Tuple, Union, Any, Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import json
class REQUEST_AI():
    def __init__(self,platform,model,max_retries=5):
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
    BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    volcano=REQUEST_AI(platform='volcano',model='r1')
    ds=REQUEST_AI(platform='deepseek',model='r1')
    # input_file=os.path.join(BASE_DIR,r'ds_label/test.json')
    input_file=os.path.join(BASE_DIR,r'ds_label/step3_input_batch.json')
    query_list=[]
    with open(input_file,'r',encoding='utf-8') as fin:
        for line in fin:
            try: 
                query_list.append(json.loads(line)['prompt'])
            except Exception as e:
                print("error",e)
                continue
        
    output_file=input_file.replace('input','output')
    # print(output_file)
    # exit()
    with open(output_file,'w',encoding='utf-8') as fout:
        for result in volcano.get_batch(query_list, max_workers=10):
            try:
                elapsed_time = ''
                query = result["query"]
                res = result["result"]
                stat = result["status"]

                fout.write(json.dumps({'input':query,'output':res},ensure_ascii=False)+"\n")
                fout.flush()
            except Exception as e:
                print("error",e)
