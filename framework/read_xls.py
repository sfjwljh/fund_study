import pandas as pd

# 读取 XLS 文件
file_path =r'F:\obsidian\Master\fund_stream_project\指数历史数据\399412.xls'  # 替换为你的 XLS 文件路径
df = pd.read_excel(file_path)

# 输出数据框的前几行
print(df.head())