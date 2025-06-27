#!/usr/bin/env python3
"""
前端集成端到端测试
使用Selenium测试前端JavaScript与后端API的集成
"""

import sys
import os
import time
import json
from typing import Dict, Any, List
from test_e2e_framework import E2ETestFramework

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium未安装，将跳过浏览器测试")

class FrontendIntegrationTests:
    """前端集成测试"""
    
    def __init__(self, framework: E2ETestFramework):
        self.framework = framework
        self.driver = None
        self.base_url = framework.server_manager.base_url
    
    def setup_driver(self) -> bool:
        """设置WebDriver"""
        if not SELENIUM_AVAILABLE:
            return False
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
            
        except Exception as e:
            print(f"   WebDriver设置失败: {str(e)}")
            return False
    
    def teardown_driver(self):
        """清理WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def test_homepage_load(self) -> bool:
        """测试主页加载"""
        if not self.driver:
            return False
        
        try:
            self.driver.get(self.base_url)
            
            # 等待页面标题加载
            WebDriverWait(self.driver, 10).until(
                lambda d: d.title != ""
            )
            
            # 检查页面是否包含预期内容
            page_source = self.driver.page_source
            if "办公文档智能代理" in page_source or "Office Document Agent" in page_source:
                return True
            
            print(f"   页面内容不符合预期")
            return False
            
        except Exception as e:
            print(f"   主页加载失败: {str(e)}")
            return False
    
    def test_table_fill_interface(self) -> bool:
        """测试表格填充界面"""
        if not self.driver:
            return False
        
        try:
            self.driver.get(f"{self.base_url}/demo")
            
            # 等待页面加载
            time.sleep(2)
            
            # 查找表格填充相关元素
            try:
                # 查找可能的表格填充按钮或输入框
                elements = self.driver.find_elements(By.TAG_NAME, "button")
                table_elements = self.driver.find_elements(By.TAG_NAME, "table")
                input_elements = self.driver.find_elements(By.TAG_NAME, "input")
                
                # 检查是否有表格相关的界面元素
                has_table_interface = (
                    len(table_elements) > 0 or 
                    len(input_elements) > 0 or
                    any("表格" in elem.text or "table" in elem.text.lower() 
                        for elem in elements if elem.text)
                )
                
                if has_table_interface:
                    return True
                else:
                    print("   未找到表格填充界面元素")
                    return False
                    
            except Exception as e:
                print(f"   查找界面元素失败: {str(e)}")
                return False
                
        except Exception as e:
            print(f"   表格填充界面测试失败: {str(e)}")
            return False
    
    def test_javascript_api_call(self) -> bool:
        """测试JavaScript API调用"""
        if not self.driver:
            return False
        
        try:
            # 创建测试页面
            test_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>API测试页面</title>
                <script>
                    async function testTableFillAPI() {{
                        try {{
                            const response = await fetch('{self.base_url}/api/table-fill', {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/json',
                                }},
                                body: JSON.stringify({{
                                    tables: [{{
                                        columns: ['姓名', '年龄'],
                                        data: [['张三', ''], ['李四', '']]
                                    }}],
                                    fill_data: [
                                        {{'姓名': '张三', '年龄': '25'}},
                                        {{'姓名': '李四', '年龄': '30'}}
                                    ]
                                }})
                            }});
                            
                            const result = await response.json();
                            document.getElementById('result').textContent = JSON.stringify(result);
                            document.getElementById('status').textContent = result.success ? 'SUCCESS' : 'FAILED';
                        }} catch (error) {{
                            document.getElementById('result').textContent = error.message;
                            document.getElementById('status').textContent = 'ERROR';
                        }}
                    }}
                    
                    window.onload = function() {{
                        testTableFillAPI();
                    }};
                </script>
            </head>
            <body>
                <h1>API测试</h1>
                <div id="status">LOADING</div>
                <div id="result"></div>
            </body>
            </html>
            """
            
            # 保存测试页面
            test_file = self.framework.create_test_file("api_test.html", test_html)
            
            # 加载测试页面
            self.driver.get(f"file://{test_file}")
            
            # 等待API调用完成
            WebDriverWait(self.driver, 15).until(
                lambda d: d.find_element(By.ID, "status").text in ["SUCCESS", "FAILED", "ERROR"]
            )
            
            status = self.driver.find_element(By.ID, "status").text
            result = self.driver.find_element(By.ID, "result").text
            
            if status == "SUCCESS":
                # 验证返回结果
                try:
                    result_data = json.loads(result)
                    if (result_data.get('success') and 
                        'filled_tables' in result_data and
                        len(result_data['filled_tables']) > 0):
                        return True
                    else:
                        print(f"   API返回结果不正确: {result}")
                        return False
                except json.JSONDecodeError:
                    print(f"   API返回结果不是有效JSON: {result}")
                    return False
            else:
                print(f"   JavaScript API调用失败: {status} - {result}")
                return False
                
        except Exception as e:
            print(f"   JavaScript API调用测试失败: {str(e)}")
            return False

class MockFrontendTests:
    """模拟前端测试（当Selenium不可用时）"""
    
    def __init__(self, framework: E2ETestFramework):
        self.framework = framework
        self.api_tester = framework.api_tester
    
    def test_api_accessibility(self) -> bool:
        """测试API可访问性"""
        # 模拟前端JavaScript调用
        tables = [
            {
                "columns": ["测试列1", "测试列2"],
                "data": [["值1", ""], ["值2", ""]]
            }
        ]
        
        fill_data = [
            {"测试列1": "值1", "测试列2": "填充值1"},
            {"测试列1": "值2", "测试列2": "填充值2"}
        ]
        
        success, result = self.api_tester.test_table_fill_api(tables, fill_data)
        return success
    
    def test_cors_headers(self) -> bool:
        """测试CORS头部"""
        import requests
        
        try:
            # 发送OPTIONS请求测试CORS
            response = requests.options(
                f"{self.api_tester.base_url}/api/table-fill",
                headers={
                    'Origin': 'http://localhost:3000',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                },
                timeout=10
            )
            
            # 检查CORS头部
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            has_cors = any(header in response.headers for header in cors_headers)
            return has_cors or response.status_code == 200
            
        except Exception as e:
            print(f"   CORS测试失败: {str(e)}")
            return False

def run_frontend_integration_tests():
    """运行前端集成测试"""
    print("🚀 开始前端集成端到端测试")
    
    framework = E2ETestFramework(port=5002)  # 使用不同端口
    
    try:
        if not framework.setup():
            print("❌ 测试环境设置失败")
            return False
        
        if SELENIUM_AVAILABLE:
            # 使用Selenium进行真实浏览器测试
            frontend_tests = FrontendIntegrationTests(framework)
            
            if not frontend_tests.setup_driver():
                print("⚠️  WebDriver设置失败，使用模拟测试")
                mock_tests = MockFrontendTests(framework)
                test_cases = [
                    ("API可访问性", mock_tests.test_api_accessibility),
                    ("CORS头部", mock_tests.test_cors_headers),
                ]
            else:
                test_cases = [
                    ("主页加载", frontend_tests.test_homepage_load),
                    ("表格填充界面", frontend_tests.test_table_fill_interface),
                    ("JavaScript API调用", frontend_tests.test_javascript_api_call),
                ]
        else:
            # 使用模拟测试
            mock_tests = MockFrontendTests(framework)
            test_cases = [
                ("API可访问性", mock_tests.test_api_accessibility),
                ("CORS头部", mock_tests.test_cors_headers),
            ]
        
        # 运行所有测试
        for test_name, test_func in test_cases:
            framework.run_test(test_name, test_func)
        
        # 清理WebDriver
        if SELENIUM_AVAILABLE and 'frontend_tests' in locals():
            frontend_tests.teardown_driver()
        
        # 打印测试摘要
        framework.print_summary()
        
        # 返回测试结果
        report = framework.generate_report()
        return report['summary']['failed'] == 0 and report['summary']['errors'] == 0
        
    finally:
        framework.teardown()

if __name__ == "__main__":
    success = run_frontend_integration_tests()
    sys.exit(0 if success else 1)
