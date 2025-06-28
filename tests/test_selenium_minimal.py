from selenium import webdriver
from selenium.webdriver.firefox.options import Options

print("准备启动Firefox...")
options = Options()
options.headless = False  # 可设为True
try:
    driver = webdriver.Firefox(options=options)
    print("Firefox已成功启动！")
    driver.get("https://www.baidu.com")
    print("已打开百度首页。")
    input("请观察浏览器窗口，按回车关闭...")
finally:
    driver.quit()
    print("已关闭浏览器。") 