# -*- coding:utf-8 -*-
#### 读取txt，让大模型返回观点+所属板块
from doubao_api import get_doubao
from pathlib import Path
import os
import pdb
import pymysql
db = pymysql.connect(host='bj-cynosdbmysql-grp-igalwqqk.sql.tencentcdb.com',
                        user='root',
                        password='UIBE_chat_2023',
                        database='fund_stream',
                        charset='utf8mb4',
                        port=25445,)
cursor = db.cursor()
def deal_text(file_path,code):
    print('dealing'+str(code))
    txt_path=os.path.join(file_path,(str(code)+'.txt'))
    with open(txt_path, 'r', encoding='utf-8') as f:
        context1=f.read()
    system1="你是一个专注于金融领域观点提取和情感分析的专家。请你从下面的文档中提取出有用的信息，包括但不限于以下方面如：包括客观的时事信息、对时事信息的主观评价及分析、对未来金融市场走向的影响及预测。请不要列序号，不要分小节，每一条信息单独一行。\n"
    system2="""你是一个专注于金融领域观点提取和情感分析的专家。这里有一些相互独立的金融板块，他们的编号和板块名称对应如下：1:医疗保健,2:生物医药,3:疫苗,4:证券公司,5:机器人,6:半导体,7:化工,8:有色金属,9:消费,10:新能源,11:通信,12:农业,13:环保,14:金融,15:军工,16:银行,17:电力,18:传媒,19:互联网,20:食品饮料,21:汽车,22:煤炭,23:建筑材料,24:光伏,25:电子,26:房地产,27:物联网,28:智能汽车,29:中药,30:新材料,31:畜牧养殖,32:装备产业,33:运输,34:钢铁,35:金融地产,36:高铁,37:低碳经济,38:基建工程,39:能源化工,40:绿色电力,41:饲料豆粕,42:工业互联网,43:车联网,44:云计算,45:数字经济,46:财富管理,47:高端制造,48:保险,49:芯片,50:金融科技,51:软件服务,52:房地产,53:石油天然气,54:计算机,55:装备制造,56:清洁能源,57:生物科技,58:宏观整体市场。
    请遵循如下指示：
    我将给出一条金融消息，请你返回价格可能受这条消息影响而波动的板块的序号，如果有多个，用空格” “隔开。如果这条消息没有提到任何板块，就返回“-1”。
    示例1
    输入：昨日世卫组织关于HPV疫苗的消息导致相关上市公司跳水，创业板指数受新能源和医药权重股影响下跌。
    返回：1 2 3 57
    示例2
    输入： 市场可能存在潜在做多机会，多头准备的三把刀分别是以煤炭、钢铁、有色、化工为代表的资源品，以航空机场白酒食品为代表的后疫情时代，大金融中的银行券商猪周期为代表的基本面分歧严重但走出独立行情的板块。
    返回：7 8 22 34  20 14 4
    示例3
    输入：公募基金经理最怕相对收益，即别人有收益自己还在亏钱。
    返回：-1
    示例4
    输入：- 对于风险偏好不高的投资者，建议选择货币基金、债基等底层资产，如中信建投的伟艺90天。
    返回：-1
    示例5
    输入：- 美国加息缩表对高估值成长股不利，缩表对离岸市场流动性有冲击，可能影响新兴市场国家，港股第二脚可能在美联储缩表后出现。
    返回：58
    示例6
    输入：- 市场以3150为轴上下震荡，考虑的问题包括GDP 5.5的实现路径、疫情、乌俄战争、缩表等。
    返回：58

    根据上面的要求和示例，下面是需要你回答的问题：“【sec1】”
    请你回答："""

    # 从整篇文本提取出观点句子
    cot1=get_doubao(system1, context1)
    # pdb.set_trace()
    ops=cot1.split('\n')
    # 分析观点句子，提取和它相关的板块序号
    for op in ops:
        cot2=get_doubao('',system2.replace("【sec1】",op))
        if ' ' in cot2:
            codes=[ i for i in cot2.split(' ') if len(i)!=0]
        else:
            codes=[cot2]
        tmp=[]
        for ind_code in codes:
            try:
                tmp.append(int(ind_code))
            except:
                pass   

        if len(tmp)==0: # 没有提取出整数，就在数据库里标0
            insert_query="INSERT INTO opinions (code, op, industry) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (code, op, 0))
            print(str(code)+' '+op+' 0')
            db.commit()
            continue
            
        if -1 in tmp:  #无用.数据库标-1
            insert_query="INSERT INTO opinions (code, op, industry) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (code, op, -1))
            print(str(code)+' '+op+' -1')
            db.commit()
            continue

        for tmpp in tmp:  #正常整数，插入数据库
            insert_query="INSERT INTO opinions (code, op, industry) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (code, op, tmpp))
            print(str(code)+' '+op+' '+str(tmpp) )
            db.commit()
                

file_path=r"C:\Users\Liu\Desktop\基金直播文本样例-大模型测试用"
directory=Path(file_path)
while 1:
    for file in directory.iterdir():
        if file.suffix=='.txt':
            code=file.stem
        # pdb.set_trace()
        if "(" in code:
            continue
        check_exist_sql="select * from opinions where code={}".format(code) 
        cursor.execute(check_exist_sql)
        result=cursor.fetchall()
        if len(result)==0:
            deal_text(file_path,code)



