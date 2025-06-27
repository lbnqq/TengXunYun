#!/usr/bin/env python3
"""
端到端测试框架
提供完整的Web应用测试功能，包括服务器管理、API测试、前端集成测试
"""

import os
import sys
import time
import json
import requests
import subprocess
import threading
import signal
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

class WebServerManager:
    """Web服务器管理器"""
    
    def __init__(self, port: int = 5000, host: str = "127.0.0.1"):
        self.port = port
        self.host = host
        self.process = None
        self.base_url = f"http://{host}:{port}"
        
    def start_server(self, timeout: int = 30) -> bool:
        """启动Web服务器"""
        print(f"🚀 启动Web服务器 {self.base_url}")
        
        try:
            # 启动简化的测试服务器
            env = os.environ.copy()
            env['FLASK_ENV'] = 'testing'
            env['FLASK_DEBUG'] = 'False'
            env['PORT'] = str(self.port)
            env['HOST'] = self.host

            self.process = subprocess.Popen(
                [sys.executable, "test_server.py"],
                cwd=os.getcwd(),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    response = requests.get(f"{self.base_url}/", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ 服务器启动成功: {self.base_url}")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    continue
            
            print(f"❌ 服务器启动超时 ({timeout}秒)")
            self.stop_server()
            return False
            
        except Exception as e:
            print(f"❌ 启动服务器失败: {str(e)}")
            return False
    
    def stop_server(self):
        """停止Web服务器"""
        if self.process:
            print("🛑 停止Web服务器")
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
    
    def is_running(self) -> bool:
        """检查服务器是否运行"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=2)
            return response.status_code == 200
        except:
            return False

class APITester:
    """API测试器"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def test_table_fill_api(self, tables: List[Dict], fill_data: List[Dict]) -> Tuple[bool, Dict]:
        """测试表格填充API"""
        url = f"{self.base_url}/api/table-fill"
        payload = {
            "tables": tables,
            "fill_data": fill_data
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=30)
            result = response.json()
            
            success = (
                response.status_code == 200 and 
                result.get('success', False) and
                'filled_tables' in result
            )
            
            return success, result
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def test_upload_api(self, file_path: str) -> Tuple[bool, Dict]:
        """测试文件上传API"""
        url = f"{self.base_url}/api/upload"

        try:
            # 创建一个新的session，不使用JSON headers
            upload_session = requests.Session()

            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'text/plain')}
                response = upload_session.post(url, files=files, timeout=30)

            result = response.json()
            success = response.status_code == 200 and result.get('success', False)

            return success, result

        except Exception as e:
            return False, {"error": str(e)}
    
    def test_health_check(self) -> bool:
        """健康检查"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False

class E2ETestFramework:
    """端到端测试框架"""
    
    def __init__(self, port: int = 5000):
        self.server_manager = WebServerManager(port=port)
        self.api_tester = APITester(self.server_manager.base_url)
        self.test_results = []
        self.temp_dir = None
    
    def setup(self) -> bool:
        """设置测试环境"""
        print("🔧 设置测试环境...")
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="e2e_test_")
        print(f"📁 临时目录: {self.temp_dir}")
        
        # 启动服务器
        if not self.server_manager.start_server():
            return False
        
        # 健康检查
        if not self.api_tester.test_health_check():
            print("❌ 服务器健康检查失败")
            return False
        
        print("✅ 测试环境设置完成")
        return True
    
    def teardown(self):
        """清理测试环境"""
        print("🧹 清理测试环境...")
        
        # 停止服务器
        self.server_manager.stop_server()
        
        # 清理临时文件
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        print("✅ 测试环境清理完成")
    
    def run_test(self, test_name: str, test_func) -> bool:
        """运行单个测试"""
        print(f"\n🧪 运行测试: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func()
            duration = time.time() - start_time
            
            if result:
                print(f"✅ {test_name} - 通过 ({duration:.2f}s)")
                self.test_results.append({
                    'name': test_name,
                    'status': 'PASS',
                    'duration': duration,
                    'timestamp': datetime.now().isoformat()
                })
                return True
            else:
                print(f"❌ {test_name} - 失败 ({duration:.2f}s)")
                self.test_results.append({
                    'name': test_name,
                    'status': 'FAIL',
                    'duration': duration,
                    'timestamp': datetime.now().isoformat()
                })
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {test_name} - 异常: {str(e)} ({duration:.2f}s)")
            self.test_results.append({
                'name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def create_test_file(self, filename: str, content: str) -> str:
        """创建测试文件"""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def generate_report(self) -> Dict:
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.test_results if r['status'] == 'ERROR'])
        
        total_duration = sum(r['duration'] for r in self.test_results)
        
        report = {
            'summary': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'errors': error_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'total_duration': total_duration
            },
            'tests': self.test_results,
            'timestamp': datetime.now().isoformat()
        }
        
        return report
    
    def print_summary(self):
        """打印测试摘要"""
        report = self.generate_report()
        summary = report['summary']
        
        print("\n" + "="*60)
        print("📊 端到端测试报告")
        print("="*60)
        print(f"总测试数: {summary['total']}")
        print(f"通过: {summary['passed']} ✅")
        print(f"失败: {summary['failed']} ❌")
        print(f"错误: {summary['errors']} 💥")
        print(f"成功率: {summary['success_rate']:.1f}%")
        print(f"总耗时: {summary['total_duration']:.2f}秒")
        print("="*60)
        
        # 详细结果
        for test in self.test_results:
            status_icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥"}[test['status']]
            print(f"{status_icon} {test['name']} ({test['duration']:.2f}s)")
            if 'error' in test:
                print(f"   错误: {test['error']}")

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n🛑 收到中断信号，正在清理...")
    sys.exit(0)

if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 启动端到端测试框架")
    
    framework = E2ETestFramework()
    
    try:
        if not framework.setup():
            print("❌ 测试环境设置失败")
            sys.exit(1)
        
        # 这里可以添加具体的测试用例
        print("✅ 测试框架就绪，可以开始运行测试")
        
        # 示例：简单的健康检查测试
        def test_health():
            return framework.api_tester.test_health_check()
        
        framework.run_test("健康检查", test_health)
        
        # 打印测试摘要
        framework.print_summary()
        
    finally:
        framework.teardown()
