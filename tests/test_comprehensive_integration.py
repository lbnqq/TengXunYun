#!/usr/bin/env python3
"""
综合集成测试套件
专门针对严重可用性问题进行全面测试

测试覆盖：
1. 文件上传功能
2. 文档分析功能  
3. 文风分析功能
4. 格式对齐功能
5. 前后端集成
6. 错误处理机制
"""

import os
import sys
import json
import time
import requests
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
import subprocess
import threading
import signal

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class IntegrationTestFramework:
    """集成测试框架"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        self.server_process = None
        self.test_files = {}
        self.setup_test_files()
        
    def setup_test_files(self):
        """准备测试文件"""
        # 创建测试文件
        test_dir = Path("test_files")
        test_dir.mkdir(exist_ok=True)
        
        # 创建TXT测试文件
        txt_content = """这是一个测试文档。
        
项目概述：
本项目旨在开发一个智能办公文档处理系统。

主要功能：
1. 文档解析和分析
2. 内容智能填充
3. 格式自动对齐
4. 文风分析和优化

技术特点：
- 支持多种文档格式
- 集成AI大模型
- 提供Web界面
- 支持批量处理

预期效果：
通过本系统，用户可以快速处理各类办公文档，提高工作效率。
"""
        
        txt_file = test_dir / "test_document.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        self.test_files['txt'] = str(txt_file)
        
        # 创建简单的文档内容用于其他测试
        simple_content = "这是一个简单的测试文档，用于验证文风分析功能。文档包含多个句子，具有不同的语言特征。"
        simple_file = test_dir / "simple_test.txt"
        with open(simple_file, 'w', encoding='utf-8') as f:
            f.write(simple_content)
        
        self.test_files['simple'] = str(simple_file)
        
    def log_test(self, test_name, status, details=None, error=None):
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'status': status,  # 'PASS', 'FAIL', 'SKIP'
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'error': str(error) if error else None
        }
        self.test_results.append(result)
        
        # 实时输出
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   详情: {details}")
        if error:
            print(f"   错误: {error}")
        print()
        
    def start_test_server(self):
        """启动测试服务器"""
        print("🚀 启动测试服务器...")
        try:
            # 使用venv中的Python启动服务器
            python_path = "venv/Scripts/python.exe" if os.name == 'nt' else "venv/bin/python"
            if not os.path.exists(python_path):
                python_path = "python"
            
            self.server_process = subprocess.Popen(
                [python_path, "src/web_app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # 等待服务器启动
            max_wait = 30
            for i in range(max_wait):
                try:
                    response = requests.get(f"{self.base_url}/api/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ 测试服务器启动成功")
                        return True
                except:
                    time.sleep(1)
                    
            print("❌ 测试服务器启动超时")
            return False
            
        except Exception as e:
            print(f"❌ 启动测试服务器失败: {e}")
            return False
    
    def stop_test_server(self):
        """停止测试服务器"""
        if self.server_process:
            print("🛑 停止测试服务器...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None
            
    def test_server_health(self):
        """测试服务器健康状态"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("服务器健康检查", "PASS", f"状态: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("服务器健康检查", "FAIL", f"HTTP状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("服务器健康检查", "FAIL", error=e)
            return False
    
    def test_file_upload_basic(self):
        """测试基本文件上传功能"""
        try:
            with open(self.test_files['txt'], 'rb') as f:
                files = {'file': ('test_document.txt', f, 'text/plain')}
                data = {'api_type': 'mock', 'model_name': 'mock-model'}
                
                response = requests.post(
                    f"{self.base_url}/api/upload",
                    files=files,
                    data=data,
                    timeout=30
                )
                
            if response.status_code == 200:
                result = response.json()
                self.log_test("基本文件上传", "PASS", f"文件ID: {result.get('file_id', 'unknown')}")
                return True
            else:
                self.log_test("基本文件上传", "FAIL", f"HTTP状态码: {response.status_code}, 响应: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("基本文件上传", "FAIL", error=e)
            return False
    
    def test_file_upload_error_handling(self):
        """测试文件上传错误处理"""
        test_cases = [
            {
                'name': '无文件上传',
                'files': None,
                'data': {'api_type': 'mock'},
                'expected_status': 400
            },
            {
                'name': '空文件名',
                'files': {'file': ('', b'', 'text/plain')},
                'data': {'api_type': 'mock'},
                'expected_status': 400
            },
            {
                'name': '不支持的文件类型',
                'files': {'file': ('test.exe', b'fake exe content', 'application/octet-stream')},
                'data': {'api_type': 'mock'},
                'expected_status': 400
            }
        ]
        
        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/upload",
                    files=case['files'],
                    data=case['data'],
                    timeout=10
                )
                
                if response.status_code == case['expected_status']:
                    self.log_test(f"错误处理-{case['name']}", "PASS", f"正确返回状态码: {response.status_code}")
                else:
                    self.log_test(f"错误处理-{case['name']}", "FAIL", 
                                f"期望状态码: {case['expected_status']}, 实际: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"错误处理-{case['name']}", "FAIL", error=e)
    
    def test_document_analysis(self):
        """测试文档分析功能"""
        try:
            with open(self.test_files['txt'], 'rb') as f:
                files = {'file': ('test_document.txt', f, 'text/plain')}
                data = {'api_type': 'mock', 'model_name': 'mock-model'}
                
                response = requests.post(
                    f"{self.base_url}/api/upload",
                    files=files,
                    data=data,
                    timeout=30
                )
                
            if response.status_code == 200:
                result = response.json()
                
                # 检查分析结果的关键字段
                required_fields = ['document_type', 'scenario', 'key_entities', 'analysis']
                missing_fields = [field for field in required_fields if field not in result]
                
                if not missing_fields:
                    self.log_test("文档分析功能", "PASS", f"包含所有必需字段: {required_fields}")
                    return True
                else:
                    self.log_test("文档分析功能", "FAIL", f"缺少字段: {missing_fields}")
                    return False
            else:
                self.log_test("文档分析功能", "FAIL", f"上传失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("文档分析功能", "FAIL", error=e)
            return False
    
    def test_writing_style_analysis(self):
        """测试文风分析功能"""
        try:
            # 测试文风分析API
            with open(self.test_files['simple'], 'rb') as f:
                files = {'file': ('simple_test.txt', f, 'text/plain')}
                data = {'analysis_type': 'style', 'api_type': 'mock'}

                response = requests.post(
                    f"{self.base_url}/api/analyze_style",
                    files=files,
                    data=data,
                    timeout=30
                )

            if response.status_code == 200:
                result = response.json()

                # 检查文风分析结果
                if 'style_features' in result or 'analysis' in result:
                    self.log_test("文风分析功能", "PASS", "成功返回文风分析结果")
                    return True
                else:
                    self.log_test("文风分析功能", "FAIL", "响应中缺少文风分析数据")
                    return False
            else:
                self.log_test("文风分析功能", "FAIL", f"HTTP状态码: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("文风分析功能", "FAIL", error=e)
            return False

    def test_format_alignment(self):
        """测试格式对齐功能"""
        try:
            # 准备源文档和目标文档
            with open(self.test_files['txt'], 'rb') as source_file, \
                 open(self.test_files['simple'], 'rb') as target_file:

                files = {
                    'source_file': ('source.txt', source_file, 'text/plain'),
                    'target_file': ('target.txt', target_file, 'text/plain')
                }
                data = {'api_type': 'mock', 'alignment_type': 'format'}

                response = requests.post(
                    f"{self.base_url}/api/format_alignment",
                    files=files,
                    data=data,
                    timeout=30
                )

            if response.status_code == 200:
                result = response.json()

                # 检查格式对齐结果
                if 'aligned_content' in result or 'alignment_result' in result:
                    self.log_test("格式对齐功能", "PASS", "成功返回格式对齐结果")
                    return True
                else:
                    self.log_test("格式对齐功能", "FAIL", "响应中缺少格式对齐数据")
                    return False
            else:
                self.log_test("格式对齐功能", "FAIL", f"HTTP状态码: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("格式对齐功能", "FAIL", error=e)
            return False

    def test_batch_processing(self):
        """测试批量处理功能"""
        try:
            # 测试批量上传
            files = []
            for i, file_path in enumerate([self.test_files['txt'], self.test_files['simple']]):
                with open(file_path, 'rb') as f:
                    files.append(('files', (f'batch_test_{i}.txt', f.read(), 'text/plain')))

            data = {'batch_upload': 'true', 'api_type': 'mock'}

            response = requests.post(
                f"{self.base_url}/api/upload",
                files=files,
                data=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                # 检查批量处理结果
                if 'batch_id' in result or 'uploaded_files' in result:
                    self.log_test("批量处理功能", "PASS", "成功处理批量上传")
                    return True
                else:
                    self.log_test("批量处理功能", "FAIL", "响应中缺少批量处理数据")
                    return False
            else:
                self.log_test("批量处理功能", "FAIL", f"HTTP状态码: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("批量处理功能", "FAIL", error=e)
            return False

    def test_api_configuration(self):
        """测试API配置功能"""
        try:
            # 测试获取可用模型
            response = requests.get(f"{self.base_url}/api/models", timeout=10)

            if response.status_code == 200:
                result = response.json()

                if 'models' in result and isinstance(result['models'], dict):
                    self.log_test("API配置功能", "PASS", f"成功获取模型配置: {list(result['models'].keys())}")
                    return True
                else:
                    self.log_test("API配置功能", "FAIL", "模型配置格式不正确")
                    return False
            else:
                self.log_test("API配置功能", "FAIL", f"HTTP状态码: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("API配置功能", "FAIL", error=e)
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("🧪 开始综合集成测试")
        print("=" * 80)
        
        # 启动服务器
        if not self.start_test_server():
            print("❌ 无法启动测试服务器，测试终止")
            return False
        
        try:
            # 运行测试
            tests = [
                self.test_server_health,
                self.test_file_upload_basic,
                self.test_file_upload_error_handling,
                self.test_document_analysis,
                self.test_writing_style_analysis,
                self.test_format_alignment,
                self.test_batch_processing,
                self.test_api_configuration,
            ]
            
            for test in tests:
                try:
                    test()
                except Exception as e:
                    self.log_test(test.__name__, "FAIL", error=e)
                    
        finally:
            # 停止服务器
            self.stop_test_server()
        
        # 生成测试报告
        self.generate_report()
        
        # 返回测试结果
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        total = len(self.test_results)
        
        print("=" * 80)
        print(f"🏁 测试完成: {passed}/{total} 通过")
        print("=" * 80)
        
        return passed == total
    
    def generate_report(self):
        """生成测试报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': len(self.test_results),
                'passed': sum(1 for r in self.test_results if r['status'] == 'PASS'),
                'failed': sum(1 for r in self.test_results if r['status'] == 'FAIL'),
                'skipped': sum(1 for r in self.test_results if r['status'] == 'SKIP')
            },
            'tests': self.test_results
        }
        
        report_file = f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📊 测试报告已保存: {report_file}")

if __name__ == "__main__":
    framework = IntegrationTestFramework()
    success = framework.run_all_tests()
    sys.exit(0 if success else 1)
