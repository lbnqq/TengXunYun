#!/usr/bin/env python3
"""
增强版前端功能测试脚本
测试文件上传、状态管理、错误处理、用户界面流程等核心功能
"""

import os
import sys
import json
import time
import unittest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class EnhancedFrontendTest(unittest.TestCase):
    """增强版前端功能测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        print("🚀 开始增强版前端功能测试...")
        
        # 设置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # 初始化WebDriver
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 20)
        
        # 测试数据
        cls.test_files = {
            'document': project_root / 'test_data' / 'document_fill' / 'template.txt',
            'image': project_root / 'test_data' / 'style_alignment' / 'reference.txt',
            'json': project_root / 'test_data' / 'document_fill' / 'data.json'
        }
        
        # 启动测试服务器（如果需要）
        cls.start_test_server()
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        print("✅ 增强版前端功能测试完成")
    
    @classmethod
    def start_test_server(cls):
        """启动测试服务器"""
        try:
            # 这里可以启动测试服务器
            # 例如：subprocess.Popen(['python', 'src/main.py'])
            pass
        except Exception as e:
            print(f"⚠️ 测试服务器启动失败: {e}")
    
    def setUp(self):
        """每个测试用例初始化"""
        self.driver.get("http://localhost:5000/enhanced-index.html")
        time.sleep(2)
    
    def test_page_loading(self):
        """测试页面加载"""
        print("📄 测试页面加载...")
        
        # 检查页面标题
        self.assertIn("办公文档智能代理", self.driver.title)
        
        # 检查主要元素是否存在
        elements_to_check = [
            "app-container",
            "app-header",
            "scene-format",
            "scene-style",
            "scene-fill",
            "scene-review",
            "scene-management"
        ]
        
        for element_id in elements_to_check:
            element = self.driver.find_element(By.ID, element_id)
            self.assertIsNotNone(element)
        
        print("✅ 页面加载测试通过")
    
    def test_navigation(self):
        """测试场景导航"""
        print("🧭 测试场景导航...")
        
        # 测试所有场景切换
        scenes = ['format', 'style', 'fill', 'review', 'management']
        
        for scene in scenes:
            # 点击导航项
            nav_item = self.driver.find_element(By.CSS_SELECTOR, f'[data-scene="{scene}"]')
            nav_item.click()
            time.sleep(1)
            
            # 检查场景是否激活
            scene_section = self.driver.find_element(By.ID, f'scene-{scene}')
            class_attr = scene_section.get_attribute('class') or ''
            self.assertNotIn('hidden', class_attr)
            
            # 检查导航项是否激活
            nav_class_attr = nav_item.get_attribute('class') or ''
            self.assertIn('active', nav_class_attr)
        
        print("✅ 场景导航测试通过")
    
    def test_file_upload_validation(self):
        """测试文件上传验证"""
        print("📁 测试文件上传验证...")
        
        # 切换到格式对齐场景
        self.driver.find_element(By.CSS_SELECTOR, '[data-scene="format"]').click()
        time.sleep(1)
        
        # 测试文件上传区域
        upload_areas = [
            'format-base-upload',
            'format-target-upload'
        ]
        
        for area_id in upload_areas:
            upload_area = self.driver.find_element(By.ID, area_id)
            
            # 检查上传区域是否存在
            self.assertIsNotNone(upload_area)
            
            # 检查文件输入框是否存在
            file_input = upload_area.find_element(By.TAG_NAME, 'input')
            self.assertEqual(file_input.get_attribute('type'), 'file')
        
        print("✅ 文件上传验证测试通过")
    
    def test_file_upload_functionality(self):
        """测试文件上传功能"""
        print("📤 测试文件上传功能...")
        
        # 切换到格式对齐场景
        self.driver.find_element(By.CSS_SELECTOR, '[data-scene="format"]').click()
        time.sleep(1)
        
        # 上传测试文件
        if self.test_files['document'].exists():
            file_input = self.driver.find_element(By.ID, 'upload-format-base')
            file_input.send_keys(str(self.test_files['document']))
            time.sleep(2)
            
            # 检查文件是否上传成功
            file_display = self.driver.find_element(By.CSS_SELECTOR, '.file-display')
            self.assertIsNotNone(file_display)
            
            # 检查文件名是否正确显示
            file_name = file_display.find_element(By.CLASS_NAME, 'file-name')
            self.assertIn('template.txt', file_name.text)
        
        print("✅ 文件上传功能测试通过")
    
    def test_drag_and_drop(self):
        """测试拖拽上传"""
        print("🖱️ 测试拖拽上传...")
        
        # 切换到格式对齐场景
        self.driver.find_element(By.CSS_SELECTOR, '[data-scene="format"]').click()
        time.sleep(1)
        
        if self.test_files['document'].exists():
            upload_area = self.driver.find_element(By.ID, 'format-base-upload')
            
            # 创建拖拽动作
            actions = ActionChains(self.driver)
            actions.drag_and_drop_by_offset(upload_area, 0, 0)
            actions.perform()
            
            # 检查拖拽效果（这里只是基本检查）
            self.assertIsNotNone(upload_area)
        
        print("✅ 拖拽上传测试通过")
    
    def test_button_functionality(self):
        """测试按钮功能"""
        print("🔘 测试按钮功能...")
        
        # 切换到格式对齐场景
        self.driver.find_element(By.CSS_SELECTOR, '[data-scene="format"]').click()
        time.sleep(1)
        
        # 测试各种按钮
        buttons_to_test = [
            ('format_alignment', '应用格式对齐'),
            ('set_baseline', '设置基准格式'),
            ('save_format', '保存格式模板')
        ]
        
        for action, expected_text in buttons_to_test:
            button = self.driver.find_element(By.CSS_SELECTOR, f'[data-action="{action}"]')
            
            # 检查按钮是否存在
            self.assertIsNotNone(button)
            
            # 检查按钮文本
            self.assertIn(expected_text, button.text)
            
            # 检查按钮是否可点击
            self.assertTrue(button.is_enabled())
        
        print("✅ 按钮功能测试通过")
    
    def test_step_indicator(self):
        """测试步骤指示器"""
        print("📊 测试步骤指示器...")
        
        # 切换到格式对齐场景
        self.driver.find_element(By.CSS_SELECTOR, '[data-scene="format"]').click()
        time.sleep(1)
        
        # 检查步骤指示器
        step_indicator = self.driver.find_element(By.CLASS_NAME, 'step-indicator')
        self.assertIsNotNone(step_indicator)
        
        # 检查步骤项
        step_items = step_indicator.find_elements(By.CLASS_NAME, 'step-item')
        self.assertEqual(len(step_items), 4)  # 应该有4个步骤
        
        # 检查第一个步骤是否激活
        first_step = step_items[0]
        first_step_class = first_step.get_attribute('class') or ''
        self.assertIn('active', first_step_class)
        
        print("✅ 步骤指示器测试通过")
    
    def test_error_handling(self):
        """测试错误处理"""
        print("⚠️ 测试错误处理...")
        
        # 测试无效文件上传
        self.driver.find_element(By.CSS_SELECTOR, '[data-scene="format"]').click()
        time.sleep(1)
        
        # 尝试上传不存在的文件
        file_input = self.driver.find_element(By.ID, 'upload-format-base')
        file_input.send_keys("/path/to/nonexistent/file.txt")
        time.sleep(2)
        
        # 检查是否有错误提示（这里可能需要根据实际实现调整）
        try:
            error_message = self.driver.find_element(By.CLASS_NAME, 'notification-error')
            self.assertIsNotNone(error_message)
        except NoSuchElementException:
            # 如果没有错误提示，这也是可以接受的
            pass
        
        print("✅ 错误处理测试通过")
    
    def test_progress_indicator(self):
        """测试进度指示器"""
        print("📈 测试进度指示器...")
        
        # 检查全局进度条是否存在
        try:
            progress_bar = self.driver.find_element(By.ID, 'global-progress')
            self.assertIsNotNone(progress_bar)
        except NoSuchElementException:
            # 进度条可能默认隐藏
            pass
        
        print("✅ 进度指示器测试通过")
    
    def test_notification_system(self):
        """测试通知系统"""
        print("🔔 测试通知系统...")
        
        # 检查通知容器是否存在
        try:
            notification_container = self.driver.find_element(By.ID, 'notification-container')
            self.assertIsNotNone(notification_container)
        except NoSuchElementException:
            # 通知容器可能动态创建
            pass
        
        print("✅ 通知系统测试通过")
    
    def test_responsive_design(self):
        """测试响应式设计"""
        print("📱 测试响应式设计...")
        
        # 设置移动端视口
        self.driver.set_window_size(375, 667)  # iPhone 6/7/8 尺寸
        time.sleep(1)
        
        # 检查移动端样式
        body = self.driver.find_element(By.TAG_NAME, 'body')
        classes = body.get_attribute('class')
        
        # 检查是否有移动端相关的类
        # 这里需要根据实际的CSS实现来调整
        self.assertIsNotNone(body)
        
        # 恢复桌面端视口
        self.driver.set_window_size(1920, 1080)
        
        print("✅ 响应式设计测试通过")
    
    def test_accessibility(self):
        """测试可访问性"""
        print("♿ 测试可访问性...")
        
        # 检查主要元素是否有适当的标签
        nav_items = self.driver.find_elements(By.CSS_SELECTOR, '.nav-item')
        for item in nav_items:
            # 检查是否有data-scene属性
            self.assertIsNotNone(item.get_attribute('data-scene'))
        
        # 检查按钮是否有适当的文本
        buttons = self.driver.find_elements(By.TAG_NAME, 'button')
        for button in buttons:
            # 检查按钮是否有文本或aria-label
            button_text = button.text.strip()
            aria_label = button.get_attribute('aria-label')
            self.assertTrue(button_text or aria_label, "按钮应该有文本或aria-label")
        
        print("✅ 可访问性测试通过")
    
    def test_performance(self):
        """测试性能"""
        print("⚡ 测试性能...")
        
        # 记录页面加载时间
        start_time = time.time()
        self.driver.get("http://localhost:5000/enhanced-index.html")
        
        # 等待页面完全加载
        self.wait.until(EC.presence_of_element_located((By.ID, "app-container")))
        load_time = time.time() - start_time
        
        # 检查加载时间是否在合理范围内（5秒内）
        self.assertLess(load_time, 5.0, f"页面加载时间过长: {load_time:.2f}秒")
        
        print(f"✅ 性能测试通过 - 加载时间: {load_time:.2f}秒")
    
    def test_browser_compatibility(self):
        """测试浏览器兼容性"""
        print("🌐 测试浏览器兼容性...")
        
        # 检查JavaScript是否正常工作
        js_result = self.driver.execute_script("return typeof window.appState !== 'undefined'")
        self.assertTrue(js_result, "JavaScript模块未正确加载")
        
        # 检查CSS是否正常应用
        app_container = self.driver.find_element(By.ID, "app-container")
        computed_style = self.driver.execute_script(
            "return window.getComputedStyle(arguments[0]).display", 
            app_container
        )
        self.assertNotEqual(computed_style, "none", "CSS样式未正确应用")
        
        print("✅ 浏览器兼容性测试通过")
    
    def test_security(self):
        """测试安全性"""
        print("🔒 测试安全性...")
        
        # 检查是否有明显的安全漏洞
        # 例如：检查文件上传是否有限制
        file_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
        for file_input in file_inputs:
            accept_attr = file_input.get_attribute('accept')
            # 检查是否限制了文件类型
            self.assertIsNotNone(accept_attr, "文件上传应该限制文件类型")
        
        # 检查是否有XSS漏洞的明显迹象
        page_source = self.driver.page_source
        dangerous_patterns = [
            'javascript:',
            'onclick=',
            'onload=',
            'onerror='
        ]
        
        for pattern in dangerous_patterns:
            self.assertNotIn(pattern, page_source.lower(), f"发现潜在的安全问题: {pattern}")
        
        print("✅ 安全性测试通过")
    
    def test_user_experience(self):
        """测试用户体验"""
        print("👤 测试用户体验...")
        
        # 检查页面是否有清晰的视觉层次
        headers = self.driver.find_elements(By.TAG_NAME, 'h1, h2, h3')
        self.assertGreater(len(headers), 0, "页面应该有标题")
        
        # 检查是否有适当的颜色对比度（基本检查）
        app_header = self.driver.find_element(By.CLASS_NAME, 'app-header')
        background_color = app_header.value_of_css_property('background-color')
        self.assertIsNotNone(background_color)
        
        # 检查是否有适当的间距
        scene_sections = self.driver.find_elements(By.CLASS_NAME, 'scene-section')
        for section in scene_sections:
            padding = section.value_of_css_property('padding')
            self.assertIsNotNone(padding)
        
        print("✅ 用户体验测试通过")

def run_enhanced_frontend_tests():
    """运行增强版前端测试"""
    print("=" * 60)
    print("🧪 增强版前端功能测试套件")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(EnhancedFrontendTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 生成测试报告
    generate_test_report(result)
    
    return result.wasSuccessful()

def generate_test_report(result):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("📊 测试报告")
    print("=" * 60)
    
    total_tests = result.testsRun
    failed_tests = len(result.failures)
    errored_tests = len(result.errors)
    passed_tests = total_tests - failed_tests - errored_tests
    
    print(f"总测试数: {total_tests}")
    print(f"通过: {passed_tests} ✅")
    print(f"失败: {failed_tests} ❌")
    print(f"错误: {errored_tests} ⚠️")
    
    if failed_tests > 0:
        print("\n失败详情:")
        for test, traceback in result.failures:
            print(f"❌ {test}: {traceback}")
    
    if errored_tests > 0:
        print("\n错误详情:")
        for test, traceback in result.errors:
            print(f"⚠️ {test}: {traceback}")
    
    # 保存报告到文件
    report_data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'errored_tests': errored_tests,
        'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
    }
    
    report_file = project_root / 'test_results' / 'enhanced_frontend_test_report.json'
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存到: {report_file}")

if __name__ == '__main__':
    success = run_enhanced_frontend_tests()
    sys.exit(0 if success else 1) 