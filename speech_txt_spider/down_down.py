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
# 仅下载，不合并



class ThreadPoolExecutorWithQueueSizeLimit(ThreadPoolExecutor):
    def __init__(self, max_workers=None, *args, **kwargs):
        super().__init__(max_workers, *args, **kwargs)
        self._work_queue = queue.Queue(max_workers * 2)


def make_sum():
    ts_num = 0
    while True:
        yield ts_num
        ts_num += 1


class M3u8Download:
    def __init__(self, url, name, max_workers=64, num_retries=5, base64_key=None):
        self._url = url
        self._name = name
        self._max_workers = max_workers
        self._num_retries = num_retries
        self._file_path = os.path.join(os.getcwd(), 'tmp_ignore_sync',self._name)
        self._front_url = None
        self._ts_url_list = []
        self._success_sum = 0
        self._ts_sum = 0
        self._key = base64.b64decode(base64_key.encode()) if base64_key else None
        self._headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

        urllib3.disable_warnings()

        self.get_m3u8_info(self._url, self._num_retries)
        print('Downloading: %s' % self._name, 'Save path: %s' % self._file_path, sep='\n')
        
        # 记录当前正在下载的编号，免得清理时删了
        with open(os.path.join(os.getcwd(), 'tmp_ignore_sync','downloading.txt'),'w') as f:
            f.writelines(self._name)

        with ThreadPoolExecutorWithQueueSizeLimit(self._max_workers) as pool:
            for k, ts_url in enumerate(self._ts_url_list):
                pool.submit(self.download_ts, ts_url, os.path.join(self._file_path, str(k)), self._num_retries)
        if self._success_sum == self._ts_sum:
            # 下载成功后，再succeed目录下新建同名文件，表明是下载好的
            file_path=os.path.join(os.getcwd(), 'tmp_ignore_sync','succeeded',self._name)
            try:  
                with open(file_path, 'x'):  
                    pass  # 文件被创建，但没有写入任何内容  

            except FileExistsError:  
                print(f"文件 {file_path} 已存在，无法创建。")

            # self.output_mp3()
            # self.delete_file()
            print(f"Download successfully --> {self._name}")

    def shell_run_cmd_block(self, cmd):
        p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=sys.stdout,
                         stderr=sys.stderr,
                         )
        p.wait()
        print('cmd ret=%d' % p.returncode)

    def get_m3u8_info(self, m3u8_url, num_retries):
        try:
            with requests.get(m3u8_url, timeout=(3, 30), verify=False, headers=self._headers) as res:
                self._front_url = res.url.split(res.request.path_url)[0]
                if "EXT-X-STREAM-INF" in res.text:
                    for line in res.text.split('\n'):
                        if "#" in line:
                            continue
                        elif line.startswith('http'):
                            self._url = line
                        elif line.startswith('/'):
                            self._url = self._front_url + line
                        else:
                            self._url = self._url.rsplit("/", 1)[0] + '/' + line
                    self.get_m3u8_info(self._url, self._num_retries)
                else:
                    m3u8_text_str = res.text
                    self.get_ts_url(m3u8_text_str)
        except Exception as e:
            print(e)
            if num_retries > 0:
                self.get_m3u8_info(m3u8_url, num_retries - 1)

    def get_ts_url(self, m3u8_text_str):
        if not os.path.exists(self._file_path):
            os.mkdir(self._file_path)
        new_m3u8_str = ''
        ts = make_sum()
        for line in m3u8_text_str.split('\n'):
            if "#" in line:
                if "EXT-X-KEY" in line and "URI=" in line:
                    if os.path.exists(os.path.join(self._file_path, 'key')):
                        continue
                    key = self.download_key(line, 5)
                    if key:
                        new_m3u8_str += f'{key}\n'
                        continue
                new_m3u8_str += f'{line}\n'
                if "EXT-X-ENDLIST" in line:
                    break
            else:
                if line.startswith('http'):
                    self._ts_url_list.append(line)
                elif line.startswith('/'):
                    self._ts_url_list.append(self._front_url + line)
                else:
                    self._ts_url_list.append(self._url.rsplit("/", 1)[0] + '/' + line)
                new_m3u8_str += (os.path.join(self._file_path, str(next(ts))) + '\n')
        self._ts_sum = next(ts)
        with open(self._file_path + '.m3u8', "wb") as f:
            if platform.system() == 'Windows':
                f.write(new_m3u8_str.encode('gbk'))
            else:
                f.write(new_m3u8_str.encode('utf-8'))

    def download_ts(self, ts_url, name, num_retries):
        ts_url = ts_url.split('\n')[0]
        try:
            if not os.path.exists(name):
                with requests.get(ts_url, stream=True, timeout=(5, 60), verify=False, headers=self._headers) as res:
                    if res.status_code == 200:
                        with open(name, "wb") as ts:
                            for chunk in res.iter_content(chunk_size=1024):
                                if chunk:
                                    ts.write(chunk)
                        self._success_sum += 1
                        sys.stdout.write('\r[%-25s](%d/%d)' % ("*" * (100 * self._success_sum // self._ts_sum // 4),
                                                               self._success_sum, self._ts_sum))
                        sys.stdout.flush()
                    else:
                        self.download_ts(ts_url, name, num_retries - 1)
            else:
                self._success_sum += 1
        except Exception:
            if os.path.exists(name):
                os.remove(name)
            if num_retries > 0:
                self.download_ts(ts_url, name, num_retries - 1)

    def download_key(self, key_line, num_retries):
        mid_part = re.search(r"URI=[\'|\"].*?[\'|\"]", key_line).group()
        may_key_url = mid_part[5:-1]
        if self._key:
            with open(os.path.join(self._file_path, 'key'), 'wb') as f:
                f.write(self._key)
            return f'{key_line.split(mid_part)[0]}URI="./{self._name}/key"'
        if may_key_url.startswith('http'):
            true_key_url = may_key_url
        elif may_key_url.startswith('/'):
            true_key_url = self._front_url + may_key_url
        else:
            true_key_url = self._url.rsplit("/", 1)[0] + '/' + may_key_url
        try:
            with requests.get(true_key_url, timeout=(5, 30), verify=False, headers=self._headers) as res:
                with open(os.path.join(self._file_path, 'key'), 'wb') as f:
                    f.write(res.content)
            return f'{key_line.split(mid_part)[0]}URI="./{self._name}/key"{key_line.split(mid_part)[-1]}'
        except Exception as e:
            print(e)
            if os.path.exists(os.path.join(self._file_path, 'key')):
                os.remove(os.path.join(self._file_path, 'key'))
            print("加密视频,无法加载key,揭秘失败")
            if num_retries > 0:
                self.download_key(key_line, num_retries - 1)

    def output_mp4(self):
        cmd = 'ffmpeg -allowed_extensions ALL -i "%s.m3u8" -acodec copy -vcodec copy -f mp4 %s.mp4' % (self._file_path, self._name)
        print(cmd)
        self.shell_run_cmd_block(cmd)

    def output_mp3(self):
        cmd =  cmd = 'ffmpeg -allowed_extensions ALL -i "%s.m3u8" -acodec libmp3lame -vn %s.mp3' % (self._file_path, self._file_path)
        print(cmd)
        self.shell_run_cmd_block(cmd)

    def delete_file(self):
        file = os.listdir(self._file_path)
        for item in file:
            os.remove(os.path.join(self._file_path, item))
        os.removedirs(self._file_path)
        os.remove(self._file_path + '.m3u8')




def download_m3u8(url, name, max_workers=64, num_retries=5, base64_key=None):
    M3u8Download(url, name, max_workers, num_retries, base64_key)


if __name__ == "__main__":
    if not os.path.exists(os.path.join(os.getcwd(), 'tmp_ignore_sync')):
        os.mkdir(os.path.join(os.getcwd(), 'tmp_ignore_sync'))
    if not os.path.exists(os.path.join(os.getcwd(), 'tmp_ignore_sync','succeeded')):
        os.mkdir(os.path.join(os.getcwd(), 'tmp_ignore_sync','succeeded'))
 
    # 从db获取一个任务

    # 从db获取一个任务
    db = pymysql.connect(host='bj-cynosdbmysql-grp-igalwqqk.sql.tencentcdb.com',
                            user='root',
                            password='UIBE_chat_2023',
                            database='fund_stream',
                            charset='utf8mb4',
                            port=25445,)
    cursor = db.cursor()
    while True:
        select_query = "select code,m3u8_url_new from total where ((downloaded=''or downloaded IS NULL) AND (occupied IS NULL or occupied='') AND (LENGTH(m3u8_url_new)>0)) ORDER BY `date` DESC " # 选择一个没被下载过且不是正在被占用的
        cursor.execute(select_query)
        db_code_list=cursor.fetchone()
        if db_code_list==None:
            print("没有可下载的任务")
            time.sleep(10)
            continue
        working_code=db_code_list[0]
        print("正在下载"+str(working_code))
        working_url=db_code_list[1]

        # 设置占用
        occupy_query = "UPDATE total SET occupied =1,occupied_time=\""+ str(datetime.now()).split('.')[0]+"\"  WHERE CODE = %s"
        cursor.execute(occupy_query, (working_code))
        db.commit()

        try:
        #下载
            M3u8Download(working_url,str(working_code))

            # print(occupy_query)
            print(str(working_code)+"下载成功")
        except:
            print(str(working_code)+"下载失败")
            release_query = "UPDATE total SET downloaded=NULL,occupied =NULL,occupied_time=NULL  WHERE CODE = %s"
            cursor.execute(release_query, (working_code))
            db.commit()



        # release_query = "UPDATE total SET downloaded=1,occupied =NULL,occupied_time=NULL,down_succeed_time=CURDATE()  WHERE CODE = %s"
        # cursor.execute(release_query, (working_code))
        # db.commit()
    # 下载成功就释放
        
        # os.remove(BASE_DIR+'/tmp_ignore_sync/{}.mp3'.format(working_code))

