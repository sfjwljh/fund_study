import pdb
def get_inudstry_code(filepath,number):
    with open(filepath,'r',encoding='utf-8') as f:
        lines = f.readlines()
        # pdb.set_trace()
        return lines[number-1].strip()
# print(get_inudstry_code(r'F:\obsidian\Master\fund_stream_project\codes\framework\板块.txt',45))