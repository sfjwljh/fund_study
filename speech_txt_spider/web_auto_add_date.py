from selenium import webdriver
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service

import datetime
import os



import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import pdb
# pdb.set_trace()
print(BASE_DIR)
from utils.database.connect import connect_db
db,cursor=connect_db()
webdriver_path = os.path.join(BASE_DIR,r'speech_txt_spider\msedgedriver.exe')  # 替换成你的WebDriver路径
start_page=40
end_page=25000
page=1 #用于记录当前页面数



# 拿到表里没有日期的code
select_query = "select code from total where isnull(title)" 
cursor.execute(select_query)
db_code_list=cursor.fetchall()
db_code_list=[i[0] for i in db_code_list]
driver=webdriver.Edge(service=Service(webdriver_path))
for code in db_code_list:
    row={'date':'','company':'','host':'','title':''}
    url='https://roadshow.eastmoney.com/luyan/'+str(code)
    # 创建Edge浏览器实例
    # 打开网页
    driver.get(url)
    time.sleep(1)
    print('正在处理{}'.format(code))
    try:
        date=driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div/span").text
        date=date.split(' ')[0]
        date=datetime.date(int(date.split('.')[0]),int(date.split('.')[1]),int(date.split('.')[2]))
        row['date']=date
    except:
        row['date']="无"
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
    try:
        title=driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/h1").text
        row['title']=title
    except:
        row['title']="无"
    sql="update total set date=%s,company=%s,host=%s,title=%s where code=%s"
    # import pdb
    # pdb.set_trace()
    cursor.execute(sql,(row['date'],row['company'],row['host'],row['title'],code))
    db.commit() 
    print('处理完成{}'.format(code))
 