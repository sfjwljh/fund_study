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