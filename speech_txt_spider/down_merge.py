import os
import pdb
import re
import sys
import queue
import base64
import platform
import time
import requests
import urllib3
import subprocess
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import pymysql
import requests
import pandas as pd
from datetime import datetime
import shutil

####运行说明：
# 1.新建一个空目录，地址中不含中文、空格

# 2.运行该程序







def shell_run_cmd_block(cmd):
    p = subprocess.Popen(cmd,
                        shell=True,
                        stdout=sys.stdout,
                        stderr=sys.stderr,
                        )
    p.wait()
    print('cmd ret=%d' % p.returncode)



def output_mp3(_file_path):
    cmd =  cmd = 'ffmpeg -allowed_extensions ALL -i "%s.m3u8" -acodec libmp3lame -vn %s.mp3' % (_file_path, _file_path)
    print(cmd)
    shell_run_cmd_block(cmd)

def delete_file(_file_path):
    file = os.listdir(_file_path)
    for item in file:
        os.remove(os.path.join(_file_path, item))
    os.removedirs(_file_path)
    os.remove(_file_path + '.m3u8')



if __name__ == "__main__":
    db = pymysql.connect(host='bj-cynosdbmysql-grp-igalwqqk.sql.tencentcdb.com',
                        user='root',
                        password='UIBE_chat_2023',
                        database='fund_stream',
                        charset='utf8mb4',
                        port=25445,)
    cursor = db.cursor()
    while 1:
        # pdb.set_trace()
        
        
        already_file_path=os.path.join(os.getcwd(), 'tmp_ignore_sync','succeeded')
        files=os.listdir(already_file_path)
        if len(files) >0:
            name = files[0]
            print("正在合并"+str(name))
            file_path=os.path.join(os.getcwd(), 'tmp_ignore_sync',str(files[0]))
            output_mp3(file_path)
            delete_file(file_path)
            os.remove(os.path.join(already_file_path,str(files[0])))
            # 成功合并，下载结束，更新数据库状态
            query = "UPDATE total SET downloaded=1,occupied =NULL,occupied_time=NULL,down_succeed_time=CURDATE()  WHERE CODE = %s"
            cursor.execute(query, (name))
            db.commit()

        else:
            print("暂无可合并项目，等待中")
            # 清理多余的
            # tmp_path=already_file_path=os.path.join(os.getcwd(), 'tmp_ignore_sync')
            # items=os.listdir(tmp_path)
            # directories = [item for item in items if os.path.isdir(os.path.join(tmp_path, item))]    
            # m3u8_files = [item.split('.')[0] for item in items if item.endswith('.m3u8')]
            # with open(os.path.join(os.getcwd(), 'tmp_ignore_sync','downloading.txt'),'r') as f:
            #     working_code=f.readline()
            # if working_code in directories:
            #     for code in directories:
            #         if code != working_code and code != 'succeeded':
            #             shutil.rmtree(os.path.join(tmp_path, code))
            #     for code in m3u8_files:
            #         if code != working_code:
            #             os.remove(os.path.join(tmp_path, code+'.m3u8'))
            time.sleep(5)


