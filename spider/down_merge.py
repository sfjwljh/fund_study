import os
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
        already_file_path=os.path.join(os.getcwd(), 'tmp_ignore_sync','succeeded')
        files=os.listdir(already_file_path)
        if len(files) >0:
            name = files[0]
            file_path=already_file_path=os.path.join(os.getcwd(), 'tmp_ignore_sync',str(files[0]))
            output_mp3()
            delete_file()
            print('no file')


