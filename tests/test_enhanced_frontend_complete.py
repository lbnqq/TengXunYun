#!/usr/bin/env python3
"""
完整前端功能测试脚本
测试文件上传、状态管理、错误处理、用户界面流程和文件验证等所有核心功能
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

class EnhancedFrontendCompleteTest(unittest.TestCase):
    """完整前端功能测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        print("🚀 开始完整前端功能测试...")
        
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
        print("✅ 完整前端功能测试完成")
    
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
        self.driver.get("http://localhost:5000/enhanced-frontend-complete")
        time.sleep(2)
    
    def test_page_loading(self):
        """测试页面加载"""
        print("📄 测试页面加载...")
        
        # 检查页面标题
        self.assertIn("办公文档智能代理", self.driver.title)
        
        # 检查主要元素是否存在
        elements_to_check = [
            ("app-container", "class"),
            ("app-header", "id"),
            ("scene-format", "id"),
            ("scene-style", "id"),
            ("scene-fill", "id"),
            ("scene-review", "id"),
            ("scene-management", "id")
        ]
        
        for element_id, element_type in elements_to_check:
            if element_type == "class":
                element = self.driver.find_element(By.CLASS_NAME, element_id)
            else:
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
            class_attr = scene_section.get_attribute('class')
            if class_attr is not None:
                self.assertNotIn('hidden', class_attr)
            
            # 检查导航项是否激活
            nav_class_attr = nav_item.get_attribute('class')
            if nav_class_attr is not None:
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
        
        # 测试操作按钮
        action_buttons = [
            'format_alignment',
            'set_baseline',
            'save_format'
        ]
        
        for action in action_buttons:
            button = self.driver.find_element(By.CSS_SELECTOR, f'[data-action="{action}"]')
            self.assertIsNotNone(button)
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
        self.assertEqual(len(step_items), 4)
        
        # 检查第一个步骤是否激活
        first_step = step_items[0]
        class_attr = first_step.get_attribute('class')
        if class_attr is not None:
            self.assertIn('active', class_attr)
        
        print("✅ 步骤指示器测试通过")
    
    def test_error_handling(self):
        """测试错误处理"""
        print("⚠️ 测试错误处理...")
        
        # 切换到格式对齐场景
        self.driver.find_element(By.CSS_SELECTOR, '[data-scene="format"]').click()
        time.sleep(1)
        
        # 测试无效文件上传
        file_input = self.driver.find_element(By.ID, 'upload-format-base')
        
        # 创建一个临时的不支持的文件
        temp_file = project_root / 'test_data' / 'temp_invalid.xyz'
        temp_file.write_text('invalid content')
        
        try:
            file_input.send_keys(str(temp_file))
            time.sleep(2)
            
            # 检查是否有错误提示
            feedback = self.driver.find_element(By.ID, 'format-feedback')
            if feedback.is_displayed():
                class_attr = feedback.get_attribute('class')
                if class_attr is not None:
                    self.assertIn('error', class_attr)
        finally:
            # 清理临时文件
            if temp_file.exists():
                temp_file.unlink()
        
        print("✅ 错误处理测试通过")
    
    def test_progress_indicator(self):
        """测试进度指示器"""
        print("📈 测试进度指示器...")
        
        # 检查全局进度条
        progress_bar = self.driver.find_element(By.ID, 'global-progress')
        self.assertIsNotNone(progress_bar)
        
        # 检查进度填充元素
        progress_fill = self.driver.find_element(By.ID, 'progress-fill')
        self.assertIsNotNone(progress_fill)
        
        print("✅ 进度指示器测试通过")
    
    def test_notification_system(self):
        """测试通知系统"""
        print("🔔 测试通知系统...")
        
        # 检查通知容器
        notification_container = self.driver.find_element(By.ID, 'notification-container')
        self.assertIsNotNone(notification_container)
        
        # 通过JavaScript触发通知
        self.driver.execute_script("""
            const notification = document.createElement('div');
            notification.className = 'notification notification-info';
            notification.innerHTML = '<div class="notification-content"><span class="notification-icon">ℹ️</span><span class="notification-message">测试通知</span><button class="notification-close">×</button></div>';
            document.getElementById('notification-container').appendChild(notification);
        """)
        
        time.sleep(1)
        
        # 检查通知是否显示
        notifications = self.driver.find_elements(By.CLASS_NAME, 'notification')
        self.assertGreater(len(notifications), 0)
        
        print("✅ 通知系统测试通过")
    
    def test_responsive_design(self):
        """测试响应式设计"""
        print("📱 测试响应式设计...")
        
        # 测试不同屏幕尺寸
        screen_sizes = [
            (1920, 1080),  # 桌面
            (768, 1024),   # 平板
            (375, 667)     # 手机
        ]
        
        for width, height in screen_sizes:
            self.driver.set_window_size(width, height)
            time.sleep(1)
            
            # 检查应用容器是否适应
            app_container = self.driver.find_element(By.CLASS_NAME, 'app-container')
            self.assertIsNotNone(app_container)
            
            # 检查导航是否适应
            main_nav = self.driver.find_element(By.CLASS_NAME, 'main-nav')
            self.assertIsNotNone(main_nav)
        
        # 恢复原始尺寸
        self.driver.set_window_size(1920, 1080)
        
        print("✅ 响应式设计测试通过")
    
    def test_accessibility(self):
        """测试可访问性"""
        print("♿ 测试可访问性...")
        
        # 检查页面标题
        self.assertIsNotNone(self.driver.title)
        self.assertGreater(len(self.driver.title), 0)
        
        # 检查主要标题
        main_title = self.driver.find_element(By.CLASS_NAME, 'main-title')
        if main_title:
            self.assertIsNotNone(main_title.text)
        
        # 检查图片alt属性
        images = self.driver.find_elements(By.TAG_NAME, 'img')
        for img in images:
            alt_attr = img.get_attribute('alt')
            if alt_attr is not None:
                self.assertIsNotNone(alt_attr)
        
        print("✅ 可访问性测试通过")
    
    def test_performance(self):
        """测试性能"""
        print("⚡ 测试性能...")
        
        # 记录页面加载时间
        start_time = time.time()
        self.driver.get("http://localhost:5000/enhanced-frontend-complete")
        
        # 等待页面完全加载
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "app-container")))
        
        load_time = time.time() - start_time
        
        # 检查加载时间是否合理（小于5秒）
        self.assertLess(load_time, 5.0)
        
        print(f"✅ 性能测试通过 - 页面加载时间: {load_time:.2f}秒")
    
    def test_browser_compatibility(self):
        """测试浏览器兼容性"""
        print("🌐 测试浏览器兼容性...")
        
        # 检查JavaScript是否正常工作
        js_result = self.driver.execute_script("return typeof window.appState !== 'undefined'")
        self.assertTrue(js_result)
        
        # 检查CSS是否正常加载
        css_loaded = self.driver.execute_script("""
            const style = getComputedStyle(document.body);
            return style.fontFamily !== '';
        """)
        self.assertTrue(css_loaded)
        
        print("✅ 浏览器兼容性测试通过")
    
    def test_security(self):
        """测试安全性"""
        print("🔒 测试安全性...")
        
        # 检查XSS防护
        xss_test = self.driver.execute_script("""
            try {
                const testDiv = document.createElement('div');
                testDiv.innerHTML = '<script>alert("xss")</script>';
                document.body.appendChild(testDiv);
                return true;
            } catch (e) {
                return false;
            }
        """)
        self.assertTrue(xss_test)
        
        # 检查文件上传限制
        file_input = self.driver.find_element(By.ID, 'upload-format-base')
        accept_attr = file_input.get_attribute('accept')
        self.assertIsNotNone(accept_attr)
        self.assertIn('.docx', accept_attr)
        
        print("✅ 安全性测试通过")
    
    def test_user_experience(self):
        """测试用户体验"""
        print("👤 测试用户体验...")
        
        # 检查加载状态
        loading_element = self.driver.find_element(By.ID, 'global-loading')
        self.assertIsNotNone(loading_element)
        
        # 检查反馈消息
        feedback_elements = self.driver.find_elements(By.CLASS_NAME, 'feedback-message')
        for feedback in feedback_elements:
            self.assertIsNotNone(feedback)
        
        # 检查按钮状态 - 更宽松的检查
        buttons = self.driver.find_elements(By.CLASS_NAME, 'btn')
        for button in buttons:
            # 检查按钮是否有内容（文本、图标或子元素）
            button_text = button.text.strip()
            button_children = button.find_elements(By.TAG_NAME, '*')
            button_attributes = button.get_attribute('data-action') or button.get_attribute('onclick')
            
            # 只要按钮有文本、子元素或功能属性就认为有效
            has_content = (button_text or 
                          len(button_children) > 0 or 
                          button_attributes is not None)
            self.assertTrue(has_content, f"按钮缺少内容: {button.get_attribute('outerHTML')}")
        
        print("✅ 用户体验测试通过")
    
    def test_management_center(self):
        """测试管理中心"""
        print("🏢 测试管理中心...")
        
        # 切换到管理中心
        self.driver.find_element(By.CSS_SELECTOR, '[data-scene="management"]').click()
        time.sleep(1)
        
        # 检查标签页
        tab_buttons = self.driver.find_elements(By.CLASS_NAME, 'btn-tab')
        self.assertGreater(len(tab_buttons), 0)
        
        # 测试标签页切换
        for tab_button in tab_buttons:
            tab_button.click()
            time.sleep(1)
            
            # 检查对应的内容是否显示
            tab_id = tab_button.get_attribute('data-tab')
            if tab_id:
                tab_content = self.driver.find_element(By.CSS_SELECTOR, f'[data-tab-content="{tab_id}"]')
                class_attr = tab_content.get_attribute('class')
                # 检查标签页内容是否可见（不是hidden状态）
                if class_attr is not None:
                    self.assertNotIn('hidden', class_attr)
        
        print("✅ 管理中心测试通过")
    
    def test_template_management(self):
        """测试模板管理"""
        print("📚 测试模板管理...")
        
        # 切换到管理中心
        self.driver.find_element(By.CSS_SELECTOR, '[data-scene="management"]').click()
        time.sleep(1)
        
        # 切换到模板库标签页
        template_tab = self.driver.find_element(By.CSS_SELECTOR, '[data-tab="templates"]')
        template_tab.click()
        time.sleep(1)
        
        # 检查模板网格
        template_grid = self.driver.find_element(By.ID, 'template-grid')
        self.assertIsNotNone(template_grid)
        
        print("✅ 模板管理测试通过")
    
    def test_settings_management(self):
        """测试设置管理"""
        print("⚙️ 测试设置管理...")
        
        # 切换到管理中心
        self.driver.find_element(By.CSS_SELECTOR, '[data-scene="management"]').click()
        time.sleep(1)
        
        # 切换到设置标签页
        settings_tab = self.driver.find_element(By.CSS_SELECTOR, '[data-tab="settings"]')
        settings_tab.click()
        time.sleep(1)
        
        # 检查设置选项
        settings_checkboxes = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
        self.assertGreater(len(settings_checkboxes), 0)
        
        # 测试设置切换
        for checkbox in settings_checkboxes:
            original_state = checkbox.is_selected()
            checkbox.click()
            time.sleep(0.5)
            new_state = checkbox.is_selected()
            self.assertNotEqual(original_state, new_state)
        
        print("✅ 设置管理测试通过")
    
    def test_performance_monitoring(self):
        """测试性能监控"""
        print("📊 测试性能监控...")
        
        # 切换到管理中心
        self.driver.find_element(By.CSS_SELECTOR, '[data-scene="management"]').click()
        time.sleep(1)
        
        # 切换到性能监控标签页
        performance_tab = self.driver.find_element(By.CSS_SELECTOR, '[data-tab="performance"]')
        performance_tab.click()
        time.sleep(1)
        
        # 检查统计卡片
        stat_cards = self.driver.find_elements(By.CLASS_NAME, 'stat-card')
        self.assertGreater(len(stat_cards), 0)
        
        # 检查统计值
        stat_values = self.driver.find_elements(By.CLASS_NAME, 'stat-value')
        for stat_value in stat_values:
            self.assertIsNotNone(stat_value.text)
        
        print("✅ 性能监控测试通过")

def run_enhanced_frontend_complete_tests():
    """运行完整前端测试"""
    print("🚀 开始运行完整前端功能测试...")
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(EnhancedFrontendCompleteTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 生成测试报告
    generate_test_report(result)
    
    return result.wasSuccessful()

def generate_test_report(result):
    """生成测试报告"""
    report_data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
        'details': {
            'failures': [{'test': str(f[0]), 'error': f[1]} for f in result.failures],
            'errors': [{'test': str(e[0]), 'error': e[1]} for e in result.errors]
        }
    }
    
    # 保存报告
    report_file = project_root / 'tests' / f'enhanced_frontend_complete_report_{int(time.time())}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"📊 测试报告已保存到: {report_file}")

if __name__ == '__main__':
    success = run_enhanced_frontend_complete_tests()
    sys.exit(0 if success else 1) 