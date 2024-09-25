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
import pdb
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait  
"""
说明：自动化从飞书上下载文本的selenium脚本
"""

# 设置 Edge 浏览器驱动路径
edge_driver_path = r"F:\obsidian\Master\fund_stream_project\codes\msedgedriver.exe"
edge_driver_path = r"F:\obsidian\Master\fund_stream_project\codes\msedgedriver.exe"

# 创建 Edge 浏览器服务
service = Service(edge_driver_path)
 
# 启动 Edge 浏览器
driver = webdriver.Edge(service=service)

# 打开网页
driver.get("https://gfhvchfr2i.feishu.cn/minutes/home")
driver.implicitly_wait(10)  # 设置隐式等待时间为10秒
time.sleep(15)
time.sleep(15)
# 关闭浏览器



while 1:
    driver.refresh()
    items = driver.find_elements(By.CLASS_NAME,"meeting-list-item-home")
    if len(items)==0:
        print("全部转录完毕，等待中")
        time.sleep(300)
        continue
    exit_executable=0
    for item in items:
        try:
            text=item.text
        except:
            continue
        if "秒" not in item.text:
            continue
        else:
            exit_executable=1
            print("正在处理"+item.find_element(By.CLASS_NAME,"no-tag").text)

            # pdb.set_trace()

            link = item.get_attribute("href")
            driver.execute_script("window.open('"+link+"', '_blank');")
            # # 获取所有窗口句柄
            window_handles = driver.window_handles
            # # 切换到新窗口
            driver.switch_to.window(window_handles[-1])
            time.sleep(6)
            # 定位按钮 A
            try_time=0
            # pdb.set_trace()
            while try_time<=3:
                button_a = driver.find_elements(By.CLASS_NAME,"transcript-header-btn-item")
                if len(button_a)==0:
                    time.sleep(1)
                    try_time+=1
                else:
                    button_a=button_a[1]
                    break

            # 创建 ActionChains 对象
            actions = ActionChains(driver)

            # 在按钮 A 上执行悬停操作
            actions.move_to_element(button_a).perform()
            # pdb.set_trace()
            time.sleep(1)
            # # 等待列表 B 出现
            # wait = WebDriverWait(driver, 10)
            # list_b = wait.until(EC.visibility_of_element_located((By.XPATH, "//xpath_of_list_B")))

            # button_b = driver.find_element(By.XPATH,"/html/body/div[6]/div/div/ul/li[1]")
            # actions.move_to_element(button_b).perform()
            # button_b.click()

            # pdb.set_trace()
            button_b = driver.find_element(By.CSS_SELECTOR,'li.transcript-header-more-btn-menu-item')
            button_b.click()


            # 不包含说话人和时间戳
            click_=driver.find_elements(By.CLASS_NAME,'ud__checkbox__label-content')
            for button in click_:
                button.click()


            # 格式下拉框
            # driver.find_element(By.XPATH,'/html/body/div[7]/div/div[3]/div/div/div/div[2]/div/div[2]/div').click()
            driver.find_element(By.CSS_SELECTOR,'.ud__select.export-modal-select').click()


            time.sleep(1)

            # 在页面上模拟按下方向下键和回车键
            actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
            time.sleep(1)

            # driver.find_element(By.XPATH,'/html/body/div[6]/div/div/div/div/div/div/div[1]/div/div/div[2]/div/div[1]').click()
            # driver.find_element(By.CLASS_NAME,'ud__button--filled').click()
            # pdb.set_trace()
            # 点击“导出"
            element = driver.find_element(By.CSS_SELECTOR, '.ud__modal__footer__btns') 
            export_button = element.find_element(By.CSS_SELECTOR, '.ud__button--filled-default')
            export_button.click()
            time.sleep(1)


            driver.close()
            driver.switch_to.window(window_handles[0])

            # ############################## 删除
            del_btn=item.find_element(By.CLASS_NAME,'meeting-list-item-delete')
            # 将元素滚动到屏幕中间
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
            time.sleep(1)
            del_btn.click()

            # 使用 XPath 找到包含文本“移除”的元素并点击它
            element = driver.find_element(By.XPATH,"//*[contains(text(), '移除')]")
            element.click()
            # pdb.set_trace()
            checkbox_container = driver.find_element(By.CSS_SELECTOR, '.ud__modal__body .checkbox-container')
            checkbox_label = checkbox_container.find_element(By.CSS_SELECTOR, '.ud__checkbox__label-content')
            checkbox_label.click()
            time.sleep(1)
            driver.find_element(By.CLASS_NAME,'ud__button--filled-danger').click()
            time.sleep(1)
    if exit_executable==0:
        print("暂无可下载的，等待中")
        time.sleep(10)
