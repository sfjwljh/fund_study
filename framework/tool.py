import pdb
def get_inudstry_name(filepath,number):
    """
    filepath：一列，所有板块的名称
    number:想好获取的板块的序号 eg 3

    返回：板块的名称。eg 新能源
    """
    with open(filepath,'r',encoding='utf-8') as f:
        lines = f.readlines()
        # pdb.set_trace()
        return lines[number-1].strip()
# print(get_inudstry_name(r'F:\obsidian\Master\fund_stream_project\codes\framework\板块.txt',45))