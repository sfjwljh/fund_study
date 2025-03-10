import json
import pdb
input_file=r'/Users/liujianhui02/Desktop/sync/obsidian/Master/fund_stream_project/codes/data_label_tool/app/alpaca_train.json'
output_file=r"/Users/liujianhui02/Desktop/sync/obsidian/Master/fund_stream_project/codes/ds_label/step1_input.jsonl"
system_1="""
我会为你提供一句需要标注的句子，请你判断在该句子内是否有谈到下面所有行业中的一种或多种
[
医疗保健,生物医药,疫苗,证券公司,机器人,半导体,化工,有色金属,新能源,通信,农业,环保,金融,军工,银行,电力,传媒,互联网,食品饮料,汽车,煤炭,建筑材料,光伏,电子,房地产,物联网,智能汽车,中药,新材料,畜牧养殖,装备产业,运输,钢铁,高铁,低碳经济,基建工程,能源化工,绿色电力,饲料豆粕,工业互联网,车联网,云计算,数字经济,财富管理,高端制造,保险,芯片,金融科技,软件服务,房地产,石油天然气,计算机,装备制造,清洁能源,生物科技,宏观市场
]
请以列表的形式将提到的行业结果返回。注意，为了不让一句话过于孤立影响解读，我会为你提供一部分前文用于理解当前的句子并判断，他们之间用“$$$”隔开。你只需要关注判断“$$$”之后的内容就行

示例1输入：
就在所有的二级指数，白酒是涨幅第一的， 15 年化涨幅是30%，那就更是超出了超过巴菲特，对对对，超过对，所以这个这涨回了全球的投资市场比较罕见的这个东西，这个东西是在我们这个去年底写的这个把你的复盘报告里面一段，这个我们从书面或者从历史，包括从各个的事实角度，从三个国家，美国、日本和中国来表现出来消费涨幅低，它本来就是一个规律，它是应该的啊我这就说到这么多，好徐叔这边有没有什么相互冲的哈哈哈，那个刚才我就说嘛，这个白酒的话，中国 a 股这白酒这十几年，是吧$$$涨幅的年化税率超过巴菲特了，这个我这个还是非常惊人的东西，因为毕竟我们中国这个 20 年来实际上就是一个这个高速发展的一个阶段，发展的结果的话就是大家收入水平提升了，收入水平提升以后的话就会更多的消费升级，更多的消费品类，这之后就带来了我们这个 a 股上的消费品类，尤其是食品饮料大幅上涨
示例1输出：
["消费"]
示例1思考过程及解释：“$$$”后的句子中只提到了“消费”板块，因此返回只有“消费”板块的列表。

示例2输入：
所以总体来说大家可以看到这两天确实只有几个板块相对是比较稳定的，比如说像家电，比如说像煤炭，对，那包括像石化、石油这些，偏偏能源的板块，偏偏电力啊对啊，那不就是诶，资金上的一个差异对诶，好像都是咱们这个赛道选机保推进的板块哈对啊对啊，所以大家我们说说我们的 Excel 群举报，大家可以这个积极关注一下啊嗯，那另外一方面就是我们接下来要探讨的诶，那是不是以后其他板块就没有机会了是啊，对吧那会不会以后就是像这两天，就只有像这个能源板块有机会，其他板块没有机会，那也不见得啊首先第一个我们说对于其他板块来说，达人们未来也会这些大的企业，嗯，它也会加大分红力度，是因为我们说像一些科技板块啊那么以前我们说它的主要任务是，对吧在投机，对吧$$$因为它整个行业发展比较快，那么我们就加大投，再投资，那么你可以为投资者赚取更高的一个回报
示例2输出：
["机器人","半导体","光伏","芯片","软件服务","计算机","生物科技"]
示例2思考过程及解释：
“$$$”后的句子中提到了“它整个行业”，根据前文可知“它”指的是“科技”板块。从给出的行业列表中找到“机器人”、“半导体”、“光伏”、“芯片”、“软件服务”、“计算机”、“生物科技”属于“科技的范畴，因此将他们加入列表返回。

示例3输入：
024年3月7日 上午 9:37|1小时 31分钟 33秒\n\n关键词:\n品类、投资、产品、估值、新基金、长安、指数、核心、机会、医疗保健、资本市场、基金经理、超额收益、长安基金、消费基金、首席分析师、时间维度、投资策略\n\n文字记录:\n哎呦，他这个还得调调啊$$$这个王总出镜头了，他上面第一，上面那个好了，差不多了，其实整体有点偏离，就这样吧，没办法运营
示例3输出：
[]
示例3思考过程及解释：
并没有提到相关内容，因此返回空列表

下面请你根据上面的说明和例子，直接给出回答，无需输出思考过程解释。上面例子中的过程解释只是为了说明任务，你只要输出列表内容即可。
输入：
{query}
输出：
"""

with open(input_file,'r',encoding='utf-8') as fin,open(output_file,'w',encoding='utf-8') as fout:
    for line in json.loads(fin.read()):
        train_line={'system':'','prompt':'','response':''}
        train_line['system']=''
        train_line['prompt']=system_1.format(query=line.get('input',''))
        fout.write(json.dumps(train_line,ensure_ascii=False)+"\n")
        # pdb.set_trace()
