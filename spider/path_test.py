import os
print(os.getcwd()) # 获取当前工作目录，即当前python脚本所在的路径,如果是vscdoe中运行，则获取的是工作环境目录
print(os.path.dirname(__file__))# 获取当前文件所在的目录
print(os.path.abspath(__file__))# 获取当前文件所在的绝对路径