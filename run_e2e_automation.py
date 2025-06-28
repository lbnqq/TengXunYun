#!/usr/bin/env python3
"""
端到端自动化测试脚本
在虚拟环境下启动服务、前端，并运行完整的测试套件

功能包括：
1. 虚拟环境检查和设置
2. 依赖安装和验证
3. 后端服务启动
4. 前端界面测试
5. 端到端功能测试
6. 性能监控
7. 测试报告生成
8. 环境清理
"""

import os
import sys
import json
import time
import signal
import subprocess
import threading
import requests
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('e2e_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class E2EAutomationTest:
    """端到端自动化测试类"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.server_process = None
        self.server_url = "http://localhost:5000"
        self.test_results = {}
        self.start_time = datetime.now()
        
        # 测试配置
        self.config = {
            'server_timeout': 30,
            'test_timeout': 300,
            'max_retries': 3,
            'wait_interval': 2
        }
        
    def log_step(self, step_name, status="INFO", details=None):
        """记录测试步骤"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "WARNING": "⚠️",
            "RUNNING": "🔄"
        }.get(status, "ℹ️")
        
        message = f"[{timestamp}] {status_icon} {step_name}"
        if details:
            message += f" - {details}"
        
        logger.info(message)
        print(message)
        
    def check_python_version(self):
        """检查Python版本"""
        self.log_step("检查Python版本", "INFO")
        version = sys.version_info
        if version < (3, 8):
            self.log_step(f"Python版本过低: {version.major}.{version.minor}", "ERROR")
            return False
        
        self.log_step(f"Python版本: {version.major}.{version.minor}.{version.micro}", "SUCCESS")
        return True
    
    def setup_virtual_environment(self):
        """设置虚拟环境"""
        self.log_step("设置虚拟环境", "RUNNING")
        
        try:
            # 检查是否已存在虚拟环境
            if self.venv_path.exists():
                self.log_step("虚拟环境已存在", "INFO")
                return True
            
            # 创建虚拟环境
            self.log_step("创建虚拟环境...", "INFO")
            result = subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                self.log_step(f"创建虚拟环境失败: {result.stderr}", "ERROR")
                return False
            
            self.log_step("虚拟环境创建成功", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_step(f"设置虚拟环境异常: {e}", "ERROR")
            return False
    
    def get_venv_python(self):
        """获取虚拟环境中的Python路径"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux
            return self.venv_path / "bin" / "python"
    
    def get_venv_pip(self):
        """获取虚拟环境中的pip路径"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "pip.exe"
        else:  # Unix/Linux
            return self.venv_path / "bin" / "pip"
    
    def install_dependencies(self):
        """安装项目依赖"""
        self.log_step("安装项目依赖", "RUNNING")
        
        try:
            pip_path = self.get_venv_pip()
            requirements_file = self.project_root / "requirements.txt"
            
            if not requirements_file.exists():
                self.log_step("requirements.txt文件不存在", "ERROR")
                return False
            
            # 升级pip
            self.log_step("升级pip...", "INFO")
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], 
                         capture_output=True, check=True)
            
            # 安装依赖
            self.log_step("安装项目依赖...", "INFO")
            result = subprocess.run([
                str(pip_path), "install", "-r", str(requirements_file)
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                self.log_step(f"依赖安装失败: {result.stderr}", "ERROR")
                return False
            
            self.log_step("依赖安装成功", "SUCCESS")
            return True
            
        except subprocess.TimeoutExpired:
            self.log_step("依赖安装超时", "ERROR")
            return False
        except Exception as e:
            self.log_step(f"安装依赖异常: {e}", "ERROR")
            return False
    
    def create_test_directories(self):
        """创建测试所需目录"""
        self.log_step("创建测试目录", "INFO")
        
        directories = [
            'uploads',
            'output', 
            'test_files',
            'test_results',
            'temp'
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
        
        self.log_step("测试目录创建完成", "SUCCESS")
    
    def start_server(self):
        """启动后端服务"""
        self.log_step("启动后端服务", "RUNNING")
        
        try:
            python_path = self.get_venv_python()
            server_script = self.project_root / "src" / "web_app.py"
            
            # 设置环境变量
            env = os.environ.copy()
            env['FLASK_ENV'] = 'testing'
            env['FLASK_DEBUG'] = '0'
            
            # 启动服务器
            self.server_process = subprocess.Popen([
                str(python_path), str(server_script)
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待服务器启动
            self.log_step("等待服务器启动...", "INFO")
            for i in range(self.config['server_timeout']):
                try:
                    response = requests.get(f"{self.server_url}/api/health", timeout=2)
                    if response.status_code == 200:
                        self.log_step("后端服务启动成功", "SUCCESS")
                        return True
                except requests.RequestException:
                    pass
                
                time.sleep(1)
                if i % 5 == 0:
                    self.log_step(f"等待服务器启动... ({i+1}s)", "INFO")
            
            self.log_step("服务器启动超时", "ERROR")
            return False
            
        except Exception as e:
            self.log_step(f"启动服务器异常: {e}", "ERROR")
            return False
    
    def test_server_health(self):
        """测试服务器健康状态"""
        self.log_step("测试服务器健康状态", "INFO")
        
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                self.log_step(f"服务器健康: {health_data.get('status', 'unknown')}", "SUCCESS")
                return True
            else:
                self.log_step(f"服务器健康检查失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log_step(f"健康检查异常: {e}", "ERROR")
            return False
    
    def test_frontend_pages(self):
        """测试前端页面"""
        self.log_step("测试前端页面", "RUNNING")
        
        pages_to_test = [
            "/",
            "/demo", 
            "/enhanced-frontend-complete"
        ]
        
        success_count = 0
        for page in pages_to_test:
            try:
                response = requests.get(f"{self.server_url}{page}", timeout=10)
                if response.status_code == 200:
                    self.log_step(f"页面 {page} 访问成功", "SUCCESS")
                    success_count += 1
                else:
                    self.log_step(f"页面 {page} 访问失败: {response.status_code}", "ERROR")
            except Exception as e:
                self.log_step(f"页面 {page} 访问异常: {e}", "ERROR")
        
        self.log_step(f"前端页面测试完成: {success_count}/{len(pages_to_test)}", 
                     "SUCCESS" if success_count == len(pages_to_test) else "WARNING")
        return success_count == len(pages_to_test)
    
    def test_api_endpoints(self):
        """测试API端点"""
        self.log_step("测试API端点", "RUNNING")
        
        # 测试文件上传
        test_file_content = "这是一个测试文档内容。\n包含多行文本用于测试。"
        test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        test_file.write(test_file_content)
        test_file.close()
        
        try:
            with open(test_file.name, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                response = requests.post(f"{self.server_url}/api/upload", files=files, timeout=30)
                
                if response.status_code == 200:
                    upload_result = response.json()
                    self.log_step("文件上传API测试成功", "SUCCESS")
                    
                    # 测试文档解析
                    if upload_result.get('success'):
                        file_path = upload_result.get('file_path')
                        if file_path:
                            parse_data = {'file_path': file_path}
                            parse_response = requests.post(
                                f"{self.server_url}/api/document/parse",
                                json=parse_data,
                                timeout=30
                            )
                            
                            if parse_response.status_code == 200:
                                self.log_step("文档解析API测试成功", "SUCCESS")
                            else:
                                self.log_step(f"文档解析API测试失败: {parse_response.status_code}", "ERROR")
                else:
                    self.log_step(f"文件上传API测试失败: {response.status_code}", "ERROR")
                    
        except Exception as e:
            self.log_step(f"API测试异常: {e}", "ERROR")
        finally:
            # 清理测试文件
            if os.path.exists(test_file.name):
                os.unlink(test_file.name)
    
    def run_comprehensive_tests(self):
        """运行综合测试套件"""
        self.log_step("运行综合测试套件", "RUNNING")
        
        try:
            python_path = self.get_venv_python()
            test_script = self.project_root / "tests" / "run_comprehensive_tests.py"
            
            if not test_script.exists():
                self.log_step("综合测试脚本不存在", "WARNING")
                return True
            
            result = subprocess.run([
                str(python_path), str(test_script)
            ], capture_output=True, text=True, timeout=self.config['test_timeout'])
            
            if result.returncode == 0:
                self.log_step("综合测试套件执行成功", "SUCCESS")
                return True
            else:
                self.log_step(f"综合测试套件执行失败: {result.stderr}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_step("综合测试套件执行超时", "ERROR")
            return False
        except Exception as e:
            self.log_step(f"综合测试套件执行异常: {e}", "ERROR")
            return False
    
    def generate_test_report(self):
        """生成测试报告"""
        self.log_step("生成测试报告", "INFO")
        
        report = {
            'test_start_time': self.start_time.isoformat(),
            'test_end_time': datetime.now().isoformat(),
            'test_duration': str(datetime.now() - self.start_time),
            'test_results': self.test_results,
            'server_url': self.server_url,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'project_root': str(self.project_root)
        }
        
        report_file = self.project_root / "test_results" / f"e2e_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log_step(f"测试报告已生成: {report_file}", "SUCCESS")
        return report_file
    
    def cleanup(self):
        """清理测试环境"""
        self.log_step("清理测试环境", "INFO")
        
        # 停止服务器
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                self.log_step("服务器已停止", "SUCCESS")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.log_step("强制停止服务器", "WARNING")
            except Exception as e:
                self.log_step(f"停止服务器异常: {e}", "WARNING")
        
        # 清理临时文件
        temp_dir = self.project_root / "temp"
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                self.log_step("临时文件已清理", "SUCCESS")
            except Exception as e:
                self.log_step(f"清理临时文件异常: {e}", "WARNING")
    
    def run_full_e2e_test(self):
        """运行完整的端到端测试"""
        print("=" * 80)
        print("🚀 开始端到端自动化测试")
        print(f"⏰ 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        try:
            # 1. 环境检查
            if not self.check_python_version():
                return False
            
            # 2. 设置虚拟环境
            if not self.setup_virtual_environment():
                return False
            
            # 3. 安装依赖
            if not self.install_dependencies():
                return False
            
            # 4. 创建测试目录
            self.create_test_directories()
            
            # 5. 启动服务器
            if not self.start_server():
                return False
            
            # 6. 测试服务器健康状态
            if not self.test_server_health():
                return False
            
            # 7. 测试前端页面
            self.test_frontend_pages()
            
            # 8. 测试API端点
            self.test_api_endpoints()
            
            # 9. 运行综合测试套件
            self.run_comprehensive_tests()
            
            # 10. 生成测试报告
            report_file = self.generate_test_report()
            
            print("=" * 80)
            print("🎉 端到端自动化测试完成")
            print(f"📊 测试报告: {report_file}")
            print("=" * 80)
            
            return True
            
        except KeyboardInterrupt:
            self.log_step("测试被用户中断", "WARNING")
            return False
        except Exception as e:
            self.log_step(f"测试执行异常: {e}", "ERROR")
            return False
        finally:
            self.cleanup()

def main():
    """主函数"""
    test_runner = E2EAutomationTest()
    success = test_runner.run_full_e2e_test()
    
    if success:
        print("✅ 端到端测试成功完成")
        sys.exit(0)
    else:
        print("❌ 端到端测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 