#coding:utf-8
import os
from openai import OpenAI
ARK_API_KEY="e76c1633-14c0-4c05-ab0d-1f2a8312953c"

client = OpenAI(
    api_key = ARK_API_KEY,
    base_url = "https://ark.cn-beijing.volces.com/api/v3",
)

def get_doubao(system,prompt):
    """
    system:系统提示词
    prompt:用户输入
    32k-pro模型
    """
    completion = client.chat.completions.create(
        model = "ep-20240731193438-fmfxd",  # your model endpoint ID
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return(completion.choices[0].message.content)

system1="""
1 医疗保健
2 生物医药
3 疫苗
4 证券公司
5 机器人
6 半导体
7 化工
8 有色金属
9 消费
10 新能源
11 通信
12 农业
13 环保
14 金融
15 军工
16 银行
17 电力
18 传媒
19 互联网
20 食品饮料
21 汽车
22 煤炭
23 建筑材料
24 光伏
25 电子
26 房地产
27 物联网
28 智能汽车
29 中药
30 新材料
31 畜牧养殖
32 装备产业
33 运输
34 钢铁
35 金融地产
36 高铁
37 低碳经济
38 基建工程
39 能源化工
40 绿色电力
41 饲料豆粕
42 工业互联网
43 车联网
44 云计算
45 数字经济
46 财富管理
47 高端制造
48 保险
49 芯片
50 金融科技
51 软件服务
52 房地产
53 石油天然气
54 计算机
55 装备制造
56 清洁能源
57 生物科技
以上是57个基金版块，下面的是一只基金的名称“【sec1】”，请你判断它属于那个板块，只需要给出对应板块的编号就行，不要返回其他任何多余的内容
"""
def get_indusatry(fund_name):
    return get_doubao('',system1.replace("【sec1】",fund_name))