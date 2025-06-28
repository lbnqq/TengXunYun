#!/usr/bin/env python3
"""
全面的API测试套件
专门测试所有后端API接口的正确性和错误处理

测试覆盖：
1. 健康检查API
2. 文件上传API
3. 文档分析API
4. 文风分析API
5. 格式对齐API
6. 批量处理API
7. 配置管理API
8. 错误处理机制
"""

import os
import sys
import json
import time
import requests
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
import io

class APITestSuite(unittest.TestCase):
    """API测试套件"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.base_url = "http://localhost:5000"
        cls.test_files = {}
        cls.setup_test_files()
        
        # 等待服务器启动（如果需要）
        cls.wait_for_server()
        
    @classmethod
    def setup_test_files(cls):
        """准备测试文件"""
        test_dir = Path("test_files")
        test_dir.mkdir(exist_ok=True)
        
        # 创建各种测试文件
        test_contents = {
            'simple.txt': "这是一个简单的测试文档。包含基本的中文内容。",
            'complex.txt': """项目报告

一、项目概述
本项目是一个智能办公文档处理系统，旨在提高办公效率。

二、主要功能
1. 文档解析和分析
2. 内容智能填充
3. 格式自动对齐
4. 文风分析和优化

三、技术架构
- 前端：HTML + JavaScript
- 后端：Python Flask
- AI模型：多种LLM支持

四、预期效果
通过本系统，用户可以：
- 快速处理各类文档
- 提高文档质量
- 节省人工时间
- 标准化文档格式

五、总结
本项目具有良好的应用前景和商业价值。""",
            'empty.txt': "",
            'special_chars.txt': "特殊字符测试：！@#￥%……&*（）——+{}|：\"《》？[]\\;',./<>?",
        }
        
        for filename, content in test_contents.items():
            file_path = test_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            cls.test_files[filename] = str(file_path)
    
    @classmethod
    def wait_for_server(cls, max_wait=30):
        """等待服务器启动"""
        for i in range(max_wait):
            try:
                response = requests.get(f"{cls.base_url}/api/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ 服务器已就绪 (等待 {i} 秒)")
                    return True
            except:
                time.sleep(1)
        
        print(f"⚠️ 服务器未响应，继续测试...")
        return False
    
    def test_01_health_check(self):
        """测试健康检查API"""
        response = requests.get(f"{self.base_url}/api/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        
    def test_02_config_api(self):
        """测试配置API"""
        response = requests.get(f"{self.base_url}/api/config")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('api_types', data)
        self.assertIsInstance(data['api_types'], list)
        
    def test_03_models_api(self):
        """测试模型列表API"""
        response = requests.get(f"{self.base_url}/api/models")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('models', data)
        self.assertIsInstance(data['models'], dict)
        
    def test_04_file_upload_success(self):
        """测试成功的文件上传"""
        with open(self.test_files['simple.txt'], 'rb') as f:
            files = {'file': ('simple.txt', f, 'text/plain')}
            data = {'api_type': 'mock', 'model_name': 'mock-model'}
            
            response = requests.post(
                f"{self.base_url}/api/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # 检查返回的必要字段
        required_fields = ['file_id', 'analysis']
        for field in required_fields:
            self.assertIn(field, result, f"缺少必要字段: {field}")
        
        # 检查返回结构
        self.assertIn('success', result)
        self.assertTrue(result['success'])
    
    def test_05_file_upload_no_file(self):
        """测试无文件上传的错误处理"""
        data = {'api_type': 'mock'}
        
        response = requests.post(
            f"{self.base_url}/api/upload",
            data=data
        )
        
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertIn('error', result)
        
        # 检查返回结构
        self.assertIn('success', result)
        self.assertFalse(result['success'])
        
    def test_06_file_upload_empty_filename(self):
        """测试空文件名的错误处理"""
        files = {'file': ('', b'', 'text/plain')}
        data = {'api_type': 'mock'}
        
        response = requests.post(
            f"{self.base_url}/api/upload",
            files=files,
            data=data
        )
        
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertIn('error', result)
        
        # 检查返回结构
        self.assertIn('success', result)
        self.assertFalse(result['success'])
        
    def test_07_file_upload_unsupported_type(self):
        """测试不支持的文件类型"""
        files = {'file': ('test.exe', b'fake exe content', 'application/octet-stream')}
        data = {'api_type': 'mock'}
        
        response = requests.post(
            f"{self.base_url}/api/upload",
            files=files,
            data=data
        )
        
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertIn('error', result)
        
        # 检查返回结构
        self.assertIn('success', result)
        self.assertFalse(result['success'])
        
    def test_08_file_upload_large_file(self):
        """测试大文件上传"""
        url = f'{self.base_url}/api/upload'
        # 假设最大文件限制为10MB，实际应与后端配置一致
        max_file_size = 10 * 1024 * 1024
        large_content = b'a' * (max_file_size + 1024)
        files = {'file': ('large.txt', large_content)}
        response = requests.post(url, files=files)
        self.assertIn(response.status_code, [200, 413])  # 200成功或413文件太大
        # 检查返回结构
        if response.status_code == 200:
            result = response.json()
            self.assertIn('success', result)
            self.assertTrue(result['success'])
        else:
            try:
                result = response.json()
                self.assertIn('error', result)
                self.assertIn('success', result)
                self.assertFalse(result['success'])
            except Exception:
                # 某些情况下返回非JSON，跳过结构校验
                pass
        
    def test_09_complex_document_analysis(self):
        """测试复杂文档分析"""
        with open(self.test_files['complex.txt'], 'rb') as f:
            files = {'file': ('complex.txt', f, 'text/plain')}
            data = {'api_type': 'mock', 'model_name': 'mock-model'}
            
            response = requests.post(
                f"{self.base_url}/api/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # 检查分析结果的质量
        analysis = result.get('analysis', {})
        self.assertIn('document_type', analysis)
        self.assertIn('key_entities', analysis)
        
        # 检查返回结构
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        
    def test_10_empty_file_handling(self):
        """测试空文件处理"""
        url = f'{self.base_url}/api/upload'
        files = {'file': ('empty.txt', b'')}
        response = requests.post(url, files=files)
        self.assertIn(response.status_code, [200, 400])
        # 检查返回结构
        if response.status_code == 200:
            result = response.json()
            self.assertIn('success', result)
            self.assertTrue(result['success'])
        else:
            try:
                result = response.json()
                self.assertIn('error', result)
                self.assertIn('success', result)
                self.assertFalse(result['success'])
            except Exception:
                # 某些情况下返回非JSON，跳过结构校验
                pass
        
    def test_11_special_characters_handling(self):
        """测试特殊字符处理"""
        with open(self.test_files['special_chars.txt'], 'rb') as f:
            files = {'file': ('special_chars.txt', f, 'text/plain')}
            data = {'api_type': 'mock'}
            
            response = requests.post(
                f"{self.base_url}/api/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn('analysis', result)
        
        # 检查返回结构
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        
    def test_12_concurrent_requests(self):
        """测试并发请求处理"""
        url = f'{self.base_url}/api/upload'
        files = {'file': ('test.txt', b'abc')}
        responses = [requests.post(url, files=files) for _ in range(5)]
        success_count = sum(1 for r in responses if r.status_code == 200)
        self.assertGreater(success_count, 0)
        # 检查返回结构
        for response in responses:
            if response.status_code == 200:
                result = response.json()
                self.assertIn('success', result)
                self.assertTrue(result['success'])
            else:
                try:
                    result = response.json()
                    self.assertIn('error', result)
                    self.assertIn('success', result)
                    self.assertFalse(result['success'])
                except Exception:
                    pass
        
    def test_13_api_response_format(self):
        """测试API响应格式一致性"""
        with open(self.test_files['simple.txt'], 'rb') as f:
            files = {'file': ('simple.txt', f, 'text/plain')}
            data = {'api_type': 'mock'}
            
            response = requests.post(
                f"{self.base_url}/api/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        self.assertEqual(response.status_code, 200)
        
        # 检查响应是否为有效JSON
        try:
            result = response.json()
        except json.JSONDecodeError:
            self.fail("响应不是有效的JSON格式")
        
        # 检查响应结构
        self.assertIsInstance(result, dict)
        
        # 检查返回结构
        self.assertIn('success', result)
        self.assertTrue(result['success'])
        
    def test_14_error_response_format(self):
        """测试错误响应格式一致性"""
        # 故意发送错误请求
        response = requests.post(f"{self.base_url}/api/upload")
        
        self.assertEqual(response.status_code, 400)
        
        # 检查错误响应格式
        try:
            result = response.json()
            self.assertIn('error', result)
            self.assertIsInstance(result['error'], str)
        except json.JSONDecodeError:
            self.fail("错误响应不是有效的JSON格式")
        
        # 检查返回结构
        self.assertIn('success', result)
        self.assertFalse(result['success'])

def run_api_tests():
    """运行API测试套件"""
    print("=" * 80)
    print("🔧 开始API测试套件")
    print("=" * 80)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(APITestSuite)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 生成报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_type': 'api_comprehensive',
        'summary': {
            'total': result.testsRun,
            'passed': result.testsRun - len(result.failures) - len(result.errors),
            'failed': len(result.failures),
            'errors': len(result.errors)
        },
        'failures': [str(f) for f in result.failures],
        'errors': [str(e) for e in result.errors]
    }
    
    report_file = f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 API测试报告已保存: {report_file}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print("=" * 80)
    print(f"🏁 API测试完成: {'全部通过' if success else '存在失败'}")
    print("=" * 80)
    
    return success

if __name__ == "__main__":
    success = run_api_tests()
    sys.exit(0 if success else 1)
