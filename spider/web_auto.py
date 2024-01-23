from selenium import webdriver
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import datetime
import os
import pandas as pd
webdriver_path = r'E:\obsidian\研究生\基金直播\codes\spider\msedgedriver.exe'  # 替换成你的WebDriver路径
start_page=450
end_page=2500
page=1 #用于记录当前页面数
db_path=r'E:\obsidian\研究生\基金直播\codes\spider\db.pickle'

if not os.path.exists(db_path):
    # 创建空的二维表
    df = pd.DataFrame(columns=['code', 'date', 'title', 'company', 'host', 'catch_url', 'm3u8_url', 'downloaded', 'stt', 'key_word', 'abstract'])
    # 保存为pickle文件
    df.to_pickle(db_path)


# 获取页面内容
def soup_page():
    result=[]
    html = driver.page_source
    # 解析HTML
    soup = BeautifulSoup(html, 'html.parser')
    # 提取所有class="item"的块
    items = soup.find_all('div', {'class': 'item'})
    for item in items:
        code = int(item.find('a')['href'].split('/')[-1])  #唯一编号
        type = item.find('span', {'class': 'ly-type'}).text.strip()  #预告/直播中/回顾
        if type!="回顾":
            continue
        title = item.find('span', {'class': 'ly-title'}).text.strip() #标题
        date = item.find('span', {'class': 'ly-time'}).text.strip().split(' ')[0] #日期
        if date=="今天":
            date=datetime.datetime.now().date()
        else:
            date=datetime.date(int(date.split('-')[0]),int(date.split('-')[1]),int(date.split('-')[2]))
        result.append([code, type, title, date])
    return result

# 跳转指定页数
def jump(page_num):
    page=page_num
    input_page_form = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[4]/ul/form/input")
    input_page_form.clear()  # 清空输入框内容
    input_page_form.send_keys(str(page))
    time.sleep(1)
    jump_page_bottom = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[4]/ul/span")
    jump_page_bottom.click()
    time.sleep(1)

# 点击 下一页
def next_page():
    next_page_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[4]/ul/li[11]")
    # /html/body/div[1]/div[2]/div[4]/ul/li[6]/a

    next_page_button.click()

# 读取页面内容并保存到本地
def html2db(html_content,path2db):
    content=html_content
    # 读取pickle文件为DataFrame对象
    df = pd.read_pickle(path2db)
    for line in content:
        # 检查当前行是否存在
        if (df['code'] == line[0]).any():
            pass
        else:
            # 新建一行数据
            new_row = {'code': line[0], 'date': line[3], 'title': line[2], 'company': '', 'host': '', 'catch_url': '', 'm3u8_url': '', 'downloaded': '', 'stt': '', 'key_word': '', 'abstract': ''}
            # 将新行数据转换为DataFrame对象
            new_df = pd.DataFrame([new_row])

            # 将新行数据与原DataFrame对象进行合并
            df = pd.concat([df, new_df], ignore_index=True)

    df.to_pickle(path2db)

# 创建Edge浏览器实例
driver = webdriver.Edge(executable_path=webdriver_path)

# 打开网页
driver.get('https://roadshow.eastmoney.com/list?type=1')


#点击 基金公司路演
fund_company_button = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div/span[2]")
fund_company_button.click()

time.sleep(2)
jump(start_page)
time.sleep(2)
page=start_page
while page<=end_page:
    content=soup_page()
    if len(content)==0:
        page+=1
        jump(page)
        time.sleep(1)

    html2db(html_content=content,path2db=db_path)
    page+=1
    jump(page)
    time.sleep(1)
