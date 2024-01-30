import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
print(sys.path)
from baidu_disk.demo.myupload import myupload

myupload(r"C:\Users\Liu\Desktop\4380398_02.mp3","/api_test")