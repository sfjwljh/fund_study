import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from translate import my_disk_app as disk
import pymysql
import requests
import pandas as pd
db = pymysql.connect(host='bj-cynosdbmysql-grp-igalwqqk.sql.tencentcdb.com',
                        user='root',
                        password='UIBE_chat_2023',
                        database='fund_stream',
                        charset='utf8mb4',
                        port=25445,)
cursor = db.cursor()

disk_raw_list=disk.get_names('/fund_stream_project/MP3_raw','file_only')
disk_raw_list=[int(code.split('.')[0]) for code in disk_raw_list]
