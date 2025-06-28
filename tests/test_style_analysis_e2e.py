import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

BACKEND_URL = 'http://127.0.0.1:5000/api/writing-style/analyze'
FRONTEND_URL = 'http://127.0.0.1:5000/'
TEST_FILE = os.path.abspath('tests/test_files/simple.txt')


def test_backend_api():
    print('【1】检测后端API...')
    if not os.path.exists(TEST_FILE):
        print(f'  ✗ 测试文件不存在: {TEST_FILE}')
        return False
    try:
        with open(TEST_FILE, 'rb') as f:
            files = {'file': f}
            resp = requests.post(BACKEND_URL, files=files, timeout=10)
        if resp.status_code != 200:
            print(f'  ✗ 后端API返回状态码: {resp.status_code}')
            return False
        data = resp.json()
        if not data.get('success'):
            print(f'  ✗ 后端API未返回 success=true: {data}')
            return False
        if not data.get('style_type') or not data.get('writing_recommendations'):
            print(f'  ✗ 后端API返回内容缺失: {data}')
            return False
        print('  ✓ 后端API检测通过')
        return True
    except Exception as e:
        print(f'  ✗ 后端API请求异常: {e}')
        return False

def test_frontend_e2e():
    print('\u30102\u3011\u68c0\u6d4b\u524d\u7aef\u9875\u9762...')
    try:
        options = FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options, service=FirefoxService())
        driver.get(FRONTEND_URL)
        # \u5207\u6362\u5230\u6587\u98ce\u5206\u6790\u573a\u666f\uff08\u5982\u6709tab\u6216\u6309\u94ae\u9700\u8865\u5145\uff09
        time.sleep(1)
        upload = driver.find_element(By.ID, 'style-analysis-input')
        upload.send_keys(TEST_FILE)
        time.sleep(1)
        # \u5982\u6709\u5206\u6790\u6309\u94ae\u9700\u70b9\u51fb
        try:
            analyze_btn = driver.find_element(By.ID, 'analyze-text-btn')
            analyze_btn.click()
        except Exception:
            pass  # \u6709\u7684\u5b9e\u73b0\u662f\u81ea\u52a8\u5206\u6790
        # \u7b49\u5f85\u7ed3\u679c\u533a\u51fa\u73b0
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'style-analysis-result'))
        )
        result_section = driver.find_element(By.ID, 'style-analysis-result')
        content = result_section.get_attribute('innerText')
        driver.save_screenshot('style_analysis_result.png')
        if not content or '--' in content or not any(k in content for k in ['style_type', 'style_prompt', 'writing_recommendations']):
            print('  \u2717 \u524d\u7aef\u9875\u9762\u672a\u6b63\u786e\u5c55\u793a\u5206\u6790\u7ed3\u679c')
            driver.quit()
            return False
        print('  \u2713 \u524d\u7aef\u9875\u9762\u68c0\u6d4b\u901a\u8fc7')
        driver.quit()
        return True
    except Exception as e:
        print(f'  \u2717 \u524d\u7aef\u9875\u9762\u68c0\u6d4b\u5f02\u5e38: {e}')
        return False

def main():
    print('==== 文风分析端到端一键自测脚本 ====')
    backend_ok = test_backend_api()
    if not backend_ok:
        print('\n【终止】后端API未通过，前端检测跳过。请先修复后端API。')
        return
    frontend_ok = test_frontend_e2e()
    if not frontend_ok:
        print('\n【终止】前端页面未通过。请检查前端渲染和JS逻辑。')
        return
    print('\n【全部通过】文风分析端到端链路正常！')

if __name__ == '__main__':
    main() 