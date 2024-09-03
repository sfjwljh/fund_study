from selenium import webdriver
from selenium.webdriver.edge.service import Service
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 设置 Edge 浏览器驱动路径
edge_driver_path = r"F:\obsidian\Master\fund_stream_project\codes\msedgedriver.exe"
service = Service(edge_driver_path)
driver = webdriver.Edge(service=service)
driver.get("https://gfhvchfr2i.feishu.cn/minutes/home")
driver.implicitly_wait(10)
time.sleep(15)

def click_three_dots(driver, wait, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            # 定位并点击三个点按钮
            more_button_xpath = '//*[@id="main-content"]/div/div[3]/div/div/div[1]/div[1]/div/div/span[2]/button'
            more_button = wait.until(EC.element_to_be_clickable((By.XPATH, more_button_xpath)))
            more_button.click()
            return True
        except Exception as e:
            print(f"Error clicking three dots: {e}")
            retries += 1
            time.sleep(2)  # 等待2秒再重试
    return False

while True:
    driver.refresh()
    items = driver.find_elements(By.CLASS_NAME, "meeting-list-item-home")
    if len(items) == 0:
        print("全部转录完毕，等待中")
        time.sleep(300)
        continue

    exit_executable = 0
    for item in items:
        try:
            text = item.text
        except:
            continue
        if "秒" not in item.text:
            continue
        else:
            exit_executable = 1
            print("正在处理" + item.find_element(By.CLASS_NAME, "no-tag").text)

            link = item.get_attribute("href")
            driver.execute_script("window.open('" + link + "', '_blank');")
            window_handles = driver.window_handles
            driver.switch_to.window(window_handles[-1])
            time.sleep(6)

            # 使用显式等待
            wait = WebDriverWait(driver, 15)
            try:
                # 尝试点击三个点
                if not click_three_dots(driver, wait):
                    raise Exception("Failed to click three dots")

                # 点击 “导出文字记录”
                export_text_xpath = '//*[text()="导出文字记录"]'
                export_text_button = wait.until(EC.element_to_be_clickable((By.XPATH, export_text_xpath)))
                export_text_button.click()
                time.sleep(2)

                # 点击选择框中的选项
                click_ = driver.find_elements(By.CLASS_NAME, 'ud__checkbox__label-content')
                for button in click_:
                    button.click()

                # 点击选择框中 "导出为" 的下拉菜单
                driver.find_element(By.CSS_SELECTOR, '.ud__select.export-modal-select').click()
                time.sleep(1)

                # 选择导出的文件格式
                actions = ActionChains(driver)
                actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
                time.sleep(1)

                # 点击 “确认导出” 按钮
                element = driver.find_element(By.CSS_SELECTOR, '.ud__modal__footer__btns')
                export_button = element.find_element(By.CSS_SELECTOR, '.ud__button--filled-default')
                export_button.click()
                time.sleep(1)

                # 关闭当前窗口，返回原窗口
                driver.close()
                driver.switch_to.window(window_handles[0])

                # 删除已处理的会议记录
                del_btn = item.find_element(By.CLASS_NAME, 'meeting-list-item-delete')
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
                time.sleep(1)
                del_btn.click()

                element = driver.find_element(By.XPATH, "//*[contains(text(), '移除')]")
                element.click()

                checkbox_container = driver.find_element(By.CSS_SELECTOR, '.ud__modal__body .checkbox-container')
                checkbox_label = checkbox_container.find_element(By.CSS_SELECTOR, '.ud__checkbox__label-content')
                checkbox_label.click()
                time.sleep(1)
                driver.find_element(By.CLASS_NAME, 'ud__button--filled-danger').click()
                time.sleep(1)
            except Exception as e:
                print(f"Error processing item: {e}")
                driver.close()
                driver.switch_to.window(window_handles[0])
                driver.get("https://gfhvchfr2i.feishu.cn/minutes/home")
                time.sleep(15)
                continue  # 重新开始处理这个文档

    if exit_executable == 0:
        print("暂无可下载的，等待中")
        time.sleep(10)
