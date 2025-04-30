最终要读取一个目录下的所有txt,形成一个大的txt文件,里面是json
```json
[
    {
        "code":文档1,
        "content":[

            {
                sentence:句子,
                label_tree:{
                    "行业1":{
                        {
                            "方面1":{
                                "时间1":情感分,
                                "时间2":情感分,
                            },
                            "方面2":{
                                "时间1":情感分,
                                "时间2":情感分,
                            },
                        }
                    },
                    "行业2":{

                    }
                },
                label_flat:[
                    {"industry":xxx,"aspect":xxx,"time":xxx,"emotion":xxx},
                    {"industry":xxx,"aspect":xxx,"time":xxx,"emotion":xxx}
                ]
            
            },
        ]
    },
    {
        文档2
    },
]

批量操作，使用千帆上的用ds结果微调后的模型，刷10%全量数据的顺序：
操作顺序：
init_batch_doc
# 读取一个目录下的所有txt文稿，生成json文件，格式是readme中提到的
# 读取未标注的原txt文件，然后形成第一步标注的请求文件

parallel_fast
?当时第一步请求的程序没了？

batch_step2
integrate2
batch_step3
integrate3
batch_step4
integrate4

tree2flat