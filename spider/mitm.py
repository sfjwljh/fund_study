import pdb
import pymysql
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
def action():
    start_code=4026672
    db = pymysql.connect(host='bj-cynosdbmysql-grp-igalwqqk.sql.tencentcdb.com',
                            user='root',
                            password='UIBE_chat_2023',
                            database='fund_stream',
                            charset='utf8mb4',
                            port=25445,)
    cursor = db.cursor()
    # 拿到表里已经有的所有code
    select_query = "SELECT code FROM total WHERE (LENGTH(m3u8_url_new)=0 or isnull(m3u8_url_new)) ORDER BY `date` DESC;"
    cursor.execute(select_query)
    db_code_list=cursor.fetchall()
    db_code_list=[i[0] for i in db_code_list]
        # 获取 code 在列表中的索引
    index = db_code_list.index(start_code)

    # 截取 code 所在位置后面的全部内容
    db_code_list = db_code_list[index+1:]


    

    # 将db.pickle的pandas列表输出为csv进行展示
    # db_path=r'E:\obsidian\Master\fund_stream_project\codes\spider\db.pickle'
    webdriver_path = r'F:\obsidian\Master\fund_stream_project\codes\msedgedriver.exe'  # 替换成你的WebDriver路径
    mitm_file_path=r'F:\obsidian\Master\fund_stream_project\codes\spider\mitm_url.txt'

    driver = webdriver.Edge(executable_path=webdriver_path)
    driver.implicitly_wait(3)
    # df = pd.read_pickle(db_path)
    # for index, row in df.iterrows():

    for code in db_code_list:
        try:
            row={'code':code,'company':'','host':'','m3u8_url_new':''}
            url='https://roadshow.eastmoney.com/luyan/'+str(row['code'])
            # 创建Edge浏览器实例
            # 打开网页
            driver.get(url)
            time.sleep(1)
            print('正在处理{}'.format(code))
            try:
                company_name=driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/p/a").text
                row['company']=company_name
            except:
                row['company']="无"
            try:
                host_name=driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div[3]/div[2]/ul/li/div[2]/h3").text
                row['host']=host_name
            except:
                row['host']="无"

            if os.path.exists(mitm_file_path):
                os.remove(mitm_file_path)
            try:
                paly_bottom=driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[1]/div/div/span[2]")
                paly_bottom.click()
            except:
                continue
            time.sleep(1)
            if not os.path.exists(mitm_file_path):
                time.sleep(2)
            if not os.path.exists(mitm_file_path):
                time.sleep(3)
            if not os.path.exists(mitm_file_path):
                continue
            row['m3u8_url_new']=pd.read_csv(mitm_file_path, header=None).iloc[0,0]
            
            update_query = "UPDATE total SET company=%s,host=%s,m3u8_url_new =%s  WHERE CODE = %s"
            cursor.execute(update_query, (row['company'],row['host'],row['m3u8_url_new'], row['code']))
            db.commit()
            print("已插入{} {} {} {}".format( row['code'],row['company'],row['host'],row['m3u8_url_new']))
        except:
            continue
        
  
        
# 添加name==main
if __name__ == '__main__':
    # webdriver_path = r'F:\obsidian\Master\fund_stream_project\codes\msedgedriver.exe'  # 替换成你的WebDriver路径

    # driver = webdriver.Edge(executable_path=webdriver_path)
    # driver.implicitly_wait(5)
    # code=4267551
    # pdb.set_trace()
    # url='https://roadshow.eastmoney.com/luyan/'+str(code)
    # driver.get(url)

    # # 创建Edge浏览器实例
    # # 打开网页
    # time.sleep(2)
    # print('正在处理{}'.format(code))

    # company_name=driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/p/a").text

    # host_name=driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div[3]/div[2]/ul/li/div[2]/h3").text


    # paly_bottom=driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[1]/div/div/span[2]")
    # paly_bottom.click()



        
    action()