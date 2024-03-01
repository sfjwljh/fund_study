from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
option = Options()
# 开启开发者工具（F12）
option.add_argument("--auto-open-devtools-for-tabs")
# options.add_argument('--headless')  # 启用无头模式
webdriver_path = "d:\迅雷下载\chromedriver-win64\chromedriver.exe"
driver = webdriver.Chrome(chrome_options=option,executable_path=webdriver_path)
# 指定 Chrome WebDriver 的路径

# 打开页面
driver.get("https://gfhvchfr2i.feishu.cn/minutes/home")

time.sleep(10)


# 找到其中的所有 class="meeting-list-item-wrapper meeting-list-item-normal" 的元素
meeting_list_items = driver.find_elements(By.CLASS_NAME,"meeting-list-item-home")



# 遍历每个元素
for item in meeting_list_items:
    print("正在处理"+item.find_element(By.CLASS_NAME,"no-tag").text)
    
    # 跳过 class="meeting-list-item-state" 不为空的元素,这是没转录好的
    if len(item.find_element(By.CLASS_NAME,"meeting-list-item-state").text)>0:
        print("working")
        continue
    else: 
        # 如果找不到，说明已经转好了，则进入链接
        link = item.get_attribute("href")

        # print(item)# 打开一个新窗口并加载给定的URL
        driver.execute_script("window.open('"+link+"', '_blank');")
        # 获取所有窗口句柄
        window_handles = driver.window_handles
        time.sleep(1)
        # 切换到新窗口
        driver.switch_to.window(window_handles[1])
        time.sleep(1)

        # 定位右上角
        
        button_a = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/div[3]/div/div[1]/div/div[4]/div[1]/div/span[2]/button/span")
        button_a = driver.find_element(By.CLASS_NAME,"universe-icon")
        


        # 创建 ActionChains 对象
        actions = ActionChains(driver)

        # 在按钮 A 上执行悬停操作
        actions.move_to_element(button_a).perform()
        time.sleep(0.7)
        # # 等待列表 B 出现
        button_b = driver.find_element(By.XPATH,"/html/body/div[6]/div/div/ul/li[1]")
        actions.move_to_element(button_b).perform()
        #点击导出文字
        button_b.click()

        #点击不带时间戳和说话人
        click_=driver.find_elements(By.CLASS_NAME,'ud__checkbox__label-content')
        for button in click_:
            button.click()

        # 点击导出格式选择
        button=driver.find_element(By.CLASS_NAME,'ud__select__selector__content')
        actions.move_to_element(button).click().perform()


        time.sleep(0.5)

        # 在页面上模拟按下方向下键和回车键，选择txt
        actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
        time.sleep(1)

        # 点击确认
        driver.find_element(By.XPATH,'/html/body/div[7]/div/div[3]/div/div/div/div[3]/div/button[1]').click()
        time.sleep(1)

        #关闭当前窗口
        driver.close()
        time.sleep(1)
        driver.switch_to.window(window_handles[0])
        time.sleep(1)



        # 删除
        item.find_element(By.CLASS_NAME,'meeting-list-item-delete').click()

        # 使用 XPath 找到包含文本“移除”的元素并点击它
        element = driver.find_element(By.XPATH,"//*[contains(text(), '移除')]")
        element.click()


        time.sleep(0.5)
        driver.find_element(By.CLASS_NAME,'checkbox-container').click()
        time.sleep(0.5)
        driver.find_element(By.CLASS_NAME,'ud__button--filled-danger').click()

        break