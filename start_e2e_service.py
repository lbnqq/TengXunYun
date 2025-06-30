#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start E2E Service

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import os
import sys
import time
import subprocess
import webbrowser
import requests
import signal
from pathlib import Path
from datetime import datetime

class E2EServiceStarter:
    """端到端服务启动器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.server_process = None
        self.server_url = "http://localhost:5000"
        self.start_time = datetime.now()
        
    def log_message(self, message, level="INFO"):
        """记录消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌", 
            "WARNING": "⚠️",
            "RUNNING": "🔄"
        }
        icon = icons.get(level, "ℹ️")
        print(f"[{timestamp}] {icon} {message}")
    
    def check_virtual_environment(self):
        """检查虚拟环境"""
        self.log_message("检查虚拟环境", "INFO")
        
        if not self.venv_path.exists():
            self.log_message("虚拟环境不存在，请先运行: python -m venv venv", "ERROR")
            return False
        
        self.log_message("虚拟环境检查通过", "SUCCESS")
        return True
    
    def get_venv_python(self):
        """获取虚拟环境Python路径"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux
            return self.venv_path / "bin" / "python"
    
    def check_dependencies(self):
        """检查依赖是否安装"""
        self.log_message("检查项目依赖", "INFO")
        
        try:
            python_path = self.get_venv_python()
            result = subprocess.run([
                str(python_path), "-c", "import flask, requests"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message("核心依赖检查通过", "SUCCESS")
                return True
            else:
                self.log_message("依赖未安装，请运行: pip install -r requirements.txt", "ERROR")
                return False
        except Exception as e:
            self.log_message(f"依赖检查异常: {e}", "ERROR")
            return False
    
    def create_necessary_directories(self):
        """创建必要的目录"""
        self.log_message("创建必要目录", "INFO")
        
        directories = ['uploads', 'output', 'temp', 'test_results']
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
        
        self.log_message("目录创建完成", "SUCCESS")
    
    def start_server(self):
        """启动后端服务器"""
        self.log_message("启动后端服务器", "RUNNING")
        
        try:
            python_path = self.get_venv_python()
            server_script = self.project_root / "src" / "web_app.py"
            
            # 设置环境变量
            env = os.environ.copy()
            env['FLASK_ENV'] = 'development'
            env['FLASK_DEBUG'] = '1'
            
            # 启动服务器
            self.server_process = subprocess.Popen([
                str(python_path), str(server_script)
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待服务器启动
            self.log_message("等待服务器启动...", "INFO")
            for i in range(30):  # 30秒超时
                try:
                    response = requests.get(f"{self.server_url}/api/health", timeout=2)
                    if response.status_code == 200:
                        self.log_message("后端服务器启动成功", "SUCCESS")
                        return True
                except requests.RequestException:
                    pass
                
                time.sleep(1)
                if i % 5 == 0:
                    self.log_message(f"等待服务器启动... ({i+1}s)", "INFO")
            
            self.log_message("服务器启动超时", "ERROR")
            return False
            
        except Exception as e:
            self.log_message(f"启动服务器异常: {e}", "ERROR")
            return False
    
    def test_server_health(self):
        """测试服务器健康状态"""
        self.log_message("测试服务器健康状态", "INFO")
        
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                self.log_message(f"服务器健康: {health_data.get('status', 'unknown')}", "SUCCESS")
                return True
            else:
                self.log_message(f"服务器健康检查失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log_message(f"健康检查异常: {e}", "ERROR")
            return False
    
    def open_browser(self):
        """打开浏览器访问前端"""
        self.log_message("打开浏览器", "INFO")
        
        try:
            # 等待一下确保服务器完全启动
            time.sleep(2)
            
            # 打开主页面
            webbrowser.open(self.server_url)
            self.log_message("浏览器已打开", "SUCCESS")
            
            # 显示可用的页面
            pages = [
                f"{self.server_url}/",
                f"{self.server_url}/demo",
                f"{self.server_url}/enhanced-frontend-complete"
            ]
            
            print("\n" + "="*60)
            print("🌐 可访问的页面:")
            for i, page in enumerate(pages, 1):
                print(f"  {i}. {page}")
            print("="*60)
            
        except Exception as e:
            self.log_message(f"打开浏览器异常: {e}", "WARNING")
    
    def show_server_info(self):
        """显示服务器信息"""
        print("\n" + "="*60)
        print("🚀 服务启动信息")
        print("="*60)
        print(f"后端服务地址: {self.server_url}")
        print(f"健康检查: {self.server_url}/api/health")
        print(f"API文档: {self.server_url}/api/config")
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        print("💡 提示: 按 Ctrl+C 停止服务")
        print("="*60)
    
    def cleanup(self):
        """清理资源"""
        self.log_message("清理资源", "INFO")
        
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                self.log_message("服务器已停止", "SUCCESS")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.log_message("强制停止服务器", "WARNING")
            except Exception as e:
                self.log_message(f"停止服务器异常: {e}", "WARNING")
    
    def run(self):
        """运行完整的启动流程"""
        print("="*60)
        print("🚀 端到端服务启动器")
        print("="*60)
        
        try:
            # 1. 检查虚拟环境
            if not self.check_virtual_environment():
                return False
            
            # 2. 检查依赖
            if not self.check_dependencies():
                return False
            
            # 3. 创建必要目录
            self.create_necessary_directories()
            
            # 4. 启动服务器
            if not self.start_server():
                return False
            
            # 5. 测试服务器健康状态
            if not self.test_server_health():
                return False
            
            # 6. 显示服务器信息
            self.show_server_info()
            
            # 7. 打开浏览器
            self.open_browser()
            
            # 8. 保持服务运行
            self.log_message("服务正在运行，按 Ctrl+C 停止", "INFO")
            
            # 等待用户中断
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.log_message("收到停止信号", "INFO")
            
            return True
            
        except Exception as e:
            self.log_message(f"启动流程异常: {e}", "ERROR")
            return False
        finally:
            self.cleanup()

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n🛑 收到停止信号，正在清理...")
    sys.exit(0)

def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    starter = E2EServiceStarter()
    success = starter.run()
    
    if success:
        print("✅ 服务启动成功")
        sys.exit(0)
    else:
        print("❌ 服务启动失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 