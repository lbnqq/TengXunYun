import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# 需要geckodriver和firefox已安装
# 测试前请确保后端已启动，页面可访问

def test_file_upload_and_api():
    print("[TEST] 启动Selenium Firefox自动化测试...")
    options = Options()
    options.headless = False  # 可设为True
    try:
        print("[TEST] 启动Firefox浏览器...")
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(30)
        print("[TEST] 打开首页 http://127.0.0.1:5000 ...")
        driver.get('http://127.0.0.1:5000')
        time.sleep(2)
        print("[TEST] 查找文件上传input...")
        file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        test_file = os.path.abspath('tests/test_files/simple.txt')
        print(f"[TEST] 上传文件: {test_file}")
        file_input.send_keys(test_file)
        time.sleep(1)
        print("[TEST] 查找分析按钮并点击...")
        # 请根据实际按钮id/class调整
        try:
            analyze_btn = driver.find_element(By.ID, 'analyze-btn')
        except Exception:
            print("[WARN] 未找到id为analyze-btn的按钮，请检查页面元素！")
            driver.quit()
            return
        analyze_btn.click()
        print("[TEST] 已点击分析按钮，等待结果...")
        time.sleep(3)
        body = driver.find_element(By.TAG_NAME, 'body').text
        print("[TEST] 页面内容：\n", body[:200])
        assert '内容为空' not in body, '[FAIL] 页面出现"内容为空"提示！'
        print('[PASS] 页面无"内容为空"提示。请用F12/Network确认document_content字段有内容。')
    except Exception as e:
        print('[ERROR] 测试过程中发生异常：', e)
        raise
    finally:
        print("[TEST] 关闭浏览器...")
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == '__main__':
    test_file_upload_and_api() 