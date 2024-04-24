import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
print(sys.path)
from baidu_disk.demo.myupload import myupload

myupload(BASE_DIR+'/tmp_ignore_sync/{}.mp3'.format(4336591),'/fund_stream_project/MP3_raw')