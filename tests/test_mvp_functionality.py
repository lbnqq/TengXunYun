#!/usr/bin/env python3
"""
MVP功能测试脚本
测试所有MVP化的桩子函数和新增功能

Author: AI Assistant
Date: 2025-01-28
"""

import os
import sys
import json
import time
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from flask import Flask
from flask.testing import FlaskClient

# 导入项目模块
from src.web_app import app
from src.core.analysis.precise_format_applier import PreciseFormatApplier, ContentElement
from src.core.analysis.efficient_document_classifier import EfficientDocumentClassifier
from src.core.database.repositories import DocumentRepository, DocumentRecord


class TestMVPFunctionality(unittest.TestCase):
    """MVP功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.app = app.test_client()
        self.app.testing = True
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 模拟数据库记录
        self.mock_record = DocumentRecord(
            id=1,
            original_filename="test_document.txt",
            file_path="/tmp/test.txt",
            file_size=1024,
            file_hash="abc123",
            document_type="test",
            intent_type="test",
            processing_status="completed",
            confidence_score=0.95,
            processing_time_ms=1000,
            error_message=None,
            created_at=datetime.now(),
            completed_at=datetime.now()
        )
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_get_api_health_mvp(self):
        """测试API健康检查MVP功能"""
        print("🔍 测试API健康检查MVP功能...")
        
        with patch('src.web_app.orchestrator_instance') as mock_orchestrator:
            mock_orchestrator.llm_client.get_health_status.return_value = {'status': 'healthy'}
            
            response = self.app.get('/api/performance/health')
            data = json.loads(response.data)
            
            # 验证响应结构
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertIn('data', data)
            self.assertIn('overall_health', data['data'])
            self.assertIn('llm_client', data['data'])
            self.assertIn('database', data['data'])
            self.assertIn('file_system', data['data'])
            
            print("✅ API健康检查MVP功能测试通过")
    
    def test_get_processing_history_mvp(self):
        """测试处理历史记录MVP功能"""
        print("🔍 测试处理历史记录MVP功能...")
        
        with patch('src.web_app.DocumentRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_processing_history.return_value = [self.mock_record]
            mock_repo_class.return_value = mock_repo
            
            response = self.app.get('/api/performance/history')
            data = json.loads(response.data)
            
            # 验证响应结构
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertIn('data', data)
            self.assertIn('records', data['data'])
            self.assertIn('total', data['data'])
            self.assertIn('note', data['data'])
            
            # 验证MVP限制：只返回最近10条
            self.assertLessEqual(len(data['data']['records']), 10)
            
            # 验证字段精简
            if data['data']['records']:
                record = data['data']['records'][0]
                expected_fields = {'id', 'timestamp', 'operation', 'success', 'filename'}
                self.assertTrue(expected_fields.issubset(set(record.keys())))
            
            print("✅ 处理历史记录MVP功能测试通过")
    
    def test_export_performance_data_mvp(self):
        """测试性能数据导出MVP功能"""
        print("🔍 测试性能数据导出MVP功能...")
        
        with patch('src.web_app.DocumentRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_processing_history.return_value = [self.mock_record]
            mock_repo_class.return_value = mock_repo
            
            # 测试JSON格式导出
            response = self.app.post('/api/performance/export', 
                                   json={'format': 'json'})
            data = json.loads(response.data)
            
            # 验证响应结构
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertIn('data', data)
            self.assertIn('records', data['data'])
            self.assertIn('total_records', data['data'])
            self.assertIn('format', data['data'])
            self.assertEqual(data['data']['format'], 'json')
            
            # 验证MVP限制：只导出最近10条
            self.assertLessEqual(len(data['data']['records']), 10)
            
            # 测试不支持CSV格式
            response = self.app.post('/api/performance/export', 
                                   json={'format': 'csv'})
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 400)
            self.assertFalse(data['success'])
            self.assertIn('MVP', data['error'])
            
            print("✅ 性能数据导出MVP功能测试通过")
    
    def test_generate_pdf_document_mvp(self):
        """测试PDF文档生成MVP功能"""
        print("🔍 测试PDF文档生成MVP功能...")
        
        applier = PreciseFormatApplier()
        
        # 创建测试内容元素
        content_elements = [
            ContentElement(type='title', content='测试标题'),
            ContentElement(type='paragraph', content='这是一个测试段落。'),
            ContentElement(type='table', content='', table_data=[['A', 'B'], ['1', '2']])
        ]
        
        template_data = {'name': 'test_template'}
        
        # 测试PDF生成
        result = applier._generate_pdf_document(content_elements, template_data)
        
        # 验证结果
        if 'error' in result:
            # 如果没有安装reportlab，应该返回错误信息
            self.assertIn('reportlab', result['error'])
            print("⚠️ PDF生成需要reportlab库，跳过实际生成测试")
        else:
            # 如果成功生成，验证结果结构
            self.assertTrue(result['success'])
            self.assertIn('output_path', result)
            self.assertIn('file_size', result)
            self.assertIn('note', result)
            self.assertIn('MVP', result['note'])
            
            # 验证文件存在
            self.assertTrue(os.path.exists(result['output_path']))
            
            print("✅ PDF文档生成MVP功能测试通过")
    
    def test_load_precise_templates_mvp(self):
        """测试精确模板加载MVP功能"""
        print("🔍 测试精确模板加载MVP功能...")
        
        classifier = EfficientDocumentClassifier()
        
        # 测试模板加载
        templates = classifier._load_precise_templates()
        
        # 验证MVP实现：返回空字典
        self.assertIsInstance(templates, dict)
        self.assertEqual(len(templates), 0)
        
        print("✅ 精确模板加载MVP功能测试通过")
    
    def test_excel_document_generation_mvp(self):
        """测试Excel文档生成MVP功能"""
        print("🔍 测试Excel文档生成MVP功能...")
        
        applier = PreciseFormatApplier()
        
        content_elements = [
            ContentElement(type='title', content='测试标题'),
            ContentElement(type='paragraph', content='测试内容')
        ]
        
        template_data = {'name': 'test_template'}
        
        # 测试Excel生成
        result = applier._generate_excel_document(content_elements, template_data)
        
        # 验证MVP实现：返回错误信息
        self.assertIn('error', result)
        self.assertIn('MVP', result['error'])
        self.assertIn('Excel生成功能待实现', result['error'])
        
        print("✅ Excel文档生成MVP功能测试通过")
    
    def test_ppt_document_generation_mvp(self):
        """测试PowerPoint文档生成MVP功能"""
        print("🔍 测试PowerPoint文档生成MVP功能...")
        
        applier = PreciseFormatApplier()
        
        content_elements = [
            ContentElement(type='title', content='测试标题'),
            ContentElement(type='paragraph', content='测试内容')
        ]
        
        template_data = {'name': 'test_template'}
        
        # 测试PPT生成
        result = applier._generate_ppt_document(content_elements, template_data)
        
        # 验证MVP实现：返回错误信息
        self.assertIn('error', result)
        self.assertIn('MVP', result['error'])
        self.assertIn('PowerPoint生成功能待实现', result['error'])
        
        print("✅ PowerPoint文档生成MVP功能测试通过")
    
    def test_mvp_error_handling(self):
        """测试MVP功能的错误处理"""
        print("🔍 测试MVP功能的错误处理...")
        
        # 测试API健康检查异常处理
        with patch('src.web_app.orchestrator_instance', None):
            response = self.app.get('/api/performance/health')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['llm_client']['status'], 'unknown')
        
        # 测试处理历史记录异常处理
        with patch('src.web_app.DocumentRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_processing_history.side_effect = Exception("数据库连接失败")
            mock_repo_class.return_value = mock_repo
            
            response = self.app.get('/api/performance/history')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])
            self.assertIn('error', data)
        
        print("✅ MVP功能错误处理测试通过")
    
    def test_mvp_documentation_consistency(self):
        """测试MVP功能的文档一致性"""
        print("🔍 测试MVP功能的文档一致性...")
        
        # 检查所有MVP函数都有正确的docstring
        mvp_functions = [
            ('src.web_app', 'get_api_health'),
            ('src.web_app', 'get_processing_history'),
            ('src.web_app', 'export_performance_data'),
            ('src.core.analysis.precise_format_applier', '_generate_pdf_document'),
            ('src.core.analysis.precise_format_applier', '_generate_excel_document'),
            ('src.core.analysis.precise_format_applier', '_generate_ppt_document'),
            ('src.core.analysis.efficient_document_classifier', '_load_precise_templates')
        ]
        
        for module_name, func_name in mvp_functions:
            try:
                module = __import__(module_name, fromlist=[func_name])
                func = getattr(module, func_name)
                
                # 检查docstring
                self.assertIsNotNone(func.__doc__)
                self.assertIn('MVP', func.__doc__)
                self.assertIn('当前实现范围', func.__doc__)
                self.assertIn('后续扩展点', func.__doc__)
                
            except (ImportError, AttributeError) as e:
                print(f"⚠️ 无法检查 {module_name}.{func_name}: {e}")
        
        print("✅ MVP功能文档一致性测试通过")


def run_mvp_tests():
    """运行所有MVP测试"""
    print("🚀 开始运行MVP功能测试...")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMVPFunctionality)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    print(f"📊 MVP测试结果:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ 错误的测试:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    # 返回测试结果
    success = len(result.failures) == 0 and len(result.errors) == 0
    return success


if __name__ == '__main__':
    success = run_mvp_tests()
    sys.exit(0 if success else 1) 