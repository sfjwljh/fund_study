# 用selenium打开浏览器
from selenium import webdriver
from selenium.webdriver.edge.service import Service

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pdb
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait  
"""
说明：用于清空飞书回收站
"""

# 设置 Edge 浏览器驱动路径
edge_driver_path = r"F:\obsidian\Master\fund_stream_project\codes\msedgedriver.exe"

# 创建 Edge 浏览器服务
service = Service(edge_driver_path)
 
# 启动 Edge 浏览器
driver = webdriver.Edge(service=service)

# 打开网页
driver.get("https://gfhvchfr2i.feishu.cn/minutes/trash")
driver.implicitly_wait(10)  # 设置隐式等待时间为10秒
# time.sleep(15)
pdb.set_trace()