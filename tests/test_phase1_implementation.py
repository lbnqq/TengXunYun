#!/usr/bin/env python3
"""
第一阶段功能实现测试脚本
测试API健康检查、模板ID生成、Web路由和测试清理功能
"""

import os
import sys
import json
import time
import requests
import unittest
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.tools.document_format_extractor import DocumentFormatExtractor
from src.core.resource_manager import resource_manager
from src.core.database.database_manager import DatabaseManager


class Phase1ImplementationTest(unittest.TestCase):
    """第一阶段功能实现测试"""
    
    def setUp(self):
        """测试前准备"""
        self.base_url = "http://localhost:5000"
        self.format_extractor = DocumentFormatExtractor()
        
        # 创建测试数据
        self.test_document = "这是一个测试文档，用于验证模板ID生成功能。"
        self.test_format_rules = {
            "heading_formats": {
                "level_1": {"font_family": "黑体", "font_size": "三号"},
                "level_2": {"font_family": "黑体", "font_size": "四号"}
            },
            "paragraph_format": {"font_family": "宋体", "font_size": "小四"}
        }
    
    def test_01_template_id_generation(self):
        """测试模板ID生成功能"""
        print("\n🔍 测试模板ID生成功能...")
        
        # 测试基本ID生成
        template_id = self.format_extractor._generate_template_id("测试文档", self.test_format_rules)
        
        self.assertIsInstance(template_id, str)
        self.assertTrue(template_id.startswith("template_"))
        self.assertTrue(len(template_id) > 20)  # 确保ID有足够长度
        
        print(f"✅ 生成的模板ID: {template_id}")
        
        # 测试相同输入生成相同ID
        template_id2 = self.format_extractor._generate_template_id("测试文档", self.test_format_rules)
        self.assertEqual(template_id, template_id2)
        
        # 测试不同输入生成不同ID
        template_id3 = self.format_extractor._generate_template_id("另一个文档", self.test_format_rules)
        self.assertNotEqual(template_id, template_id3)
        
        print("✅ 模板ID生成功能测试通过")
    
    def test_02_database_health_check(self):
        """测试数据库健康检查功能"""
        print("\n🔍 测试数据库健康检查功能...")
        
        # 创建临时数据库
        import tempfile
        temp_db_path = tempfile.mktemp(suffix='.db')
        
        try:
            db_manager = DatabaseManager(temp_db_path)
            
            # 测试健康检查
            health_status = db_manager.check_connection()
            
            self.assertIsInstance(health_status, dict)
            self.assertIn('status', health_status)
            self.assertEqual(health_status['status'], 'healthy')
            self.assertIn('db_path', health_status)
            self.assertIn('tables', health_status)
            
            print(f"✅ 数据库健康状态: {health_status['status']}")
            print(f"   数据库路径: {health_status['db_path']}")
            print(f"   表数量: {health_status['tables']}")
            
            db_manager.close()
            
        finally:
            # 清理临时数据库
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
        
        print("✅ 数据库健康检查功能测试通过")
    
    def test_03_test_cleanup_function(self):
        """测试测试清理功能"""
        print("\n🔍 测试测试清理功能...")
        
        # 确保测试目录存在
        test_dirs = ['temp', 'cache', 'uploads']
        test_files = []
        
        for test_dir in test_dirs:
            os.makedirs(test_dir, exist_ok=True)
            
            # 创建测试文件
            test_file = os.path.join(test_dir, f"test_file_{int(time.time())}.tmp")
            with open(test_file, 'w') as f:
                f.write("test content")
            test_files.append(test_file)
            print(f"创建测试文件: {test_file}")
        
        # 验证文件存在
        for test_file in test_files:
            self.assertTrue(os.path.exists(test_file), f"测试文件未创建: {test_file}")
        
        # 执行清理 - 直接调用ResourceManager
        from src.core.resource_manager import ResourceManager
        resource_manager = ResourceManager()
        result = resource_manager.cleanup_test_resources()
        
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        print(f"清理结果: {result}")
        
        # 验证文件被清理
        for test_file in test_files:
            self.assertFalse(os.path.exists(test_file), f"测试文件未被清理: {test_file}")
        
        print("✅ 测试清理功能测试通过")
    
    def test_04_web_api_endpoints(self):
        """测试Web API端点"""
        print("\n🔍 测试Web API端点...")
        
        # 测试健康检查端点
        try:
            response = requests.get(f"{self.base_url}/api/performance/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.assertIn('success', data)
                self.assertTrue(data['success'])
                self.assertIn('data', data)
                
                health_data = data['data']
                self.assertIn('overall_health', health_data)
                self.assertIn('last_check', health_data)
                
                print(f"✅ API健康检查: {health_data['overall_health']}")
                print(f"   检查时间: {health_data['last_check']}")
                
            else:
                print(f"⚠️ 健康检查端点返回状态码: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ 无法连接到Web服务器: {e}")
            print("   请确保Web服务器正在运行")
        
        # 测试模板端点
        try:
            response = requests.get(f"{self.base_url}/api/format-templates", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.assertIn('success', data)
                self.assertTrue(data['success'])
                self.assertIn('templates', data)
                
                print(f"✅ 模板列表获取成功，共 {len(data['templates'])} 个模板")
                
            else:
                print(f"⚠️ 模板端点返回状态码: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ 无法连接到Web服务器: {e}")
        
        print("✅ Web API端点测试完成")
    
    def test_05_format_template_operations(self):
        """测试格式模板操作"""
        print("\n🔍 测试格式模板操作...")
        
        # 测试格式提取和模板保存
        result = self.format_extractor.extract_format_from_document(
            self.test_document, 
            "测试文档"
        )
        
        self.assertNotIn('error', result)
        self.assertIn('template_id', result)
        self.assertIn('format_rules', result)
        
        template_id = result['template_id']
        print(f"✅ 格式提取成功，模板ID: {template_id}")
        
        # 测试模板保存
        save_result = self.format_extractor.save_format_template(result)
        
        self.assertNotIn('error', save_result)
        self.assertIn('success', save_result)
        self.assertTrue(save_result['success'])
        
        print(f"✅ 模板保存成功: {save_result['saved_path']}")
        
        # 测试模板加载
        loaded_template = self.format_extractor.load_format_template(template_id)
        
        self.assertNotIn('error', loaded_template)
        self.assertEqual(loaded_template['template_id'], template_id)
        
        print("✅ 模板加载成功")
        
        # 测试模板列表
        templates = self.format_extractor.list_format_templates()
        
        self.assertIsInstance(templates, list)
        self.assertGreater(len(templates), 0)
        
        print(f"✅ 模板列表获取成功，共 {len(templates)} 个模板")
        
        print("✅ 格式模板操作测试通过")
    
    def test_06_error_handling(self):
        """测试错误处理"""
        print("\n🔍 测试错误处理...")
        
        # 测试加载不存在的模板
        result = self.format_extractor.load_format_template("nonexistent_template")
        
        self.assertIn('error', result)
        self.assertIn('模板不存在', result['error'])
        
        print("✅ 错误处理测试通过")
    
    def tearDown(self):
        """测试后清理"""
        # 清理测试文件
        test_dirs = ['temp', 'cache', 'uploads']
        for dir_name in test_dirs:
            if os.path.exists(dir_name):
                for filename in os.listdir(dir_name):
                    if filename.startswith('test_'):
                        file_path = os.path.join(dir_name, filename)
                        try:
                            os.remove(file_path)
                        except:
                            pass


def run_phase1_tests():
    """运行第一阶段功能测试"""
    print("🚀 开始第一阶段功能实现测试")
    print("=" * 50)
    
    # 创建测试套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(Phase1ImplementationTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("📊 第一阶段功能实现测试结果")
    print(f"运行测试: {result.testsRun}")
    print(f"失败测试: {len(result.failures)}")
    print(f"错误测试: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 所有第一阶段功能测试通过！")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查实现")
        return False


if __name__ == '__main__':
    success = run_phase1_tests()
    sys.exit(0 if success else 1) 