#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统健康检查脚本
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_status(item, status, details=""):
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {item}")
    if details:
        print(f"   {details}")

def check_python_environment():
    """检查Python环境"""
    print_header("Python环境检查")
    
    # 检查Python版本
    try:
        python_version = sys.version
        print_status("Python版本", True, python_version.split()[0])
    except Exception as e:
        print_status("Python版本", False, str(e))
        return False
    
    # 检查虚拟环境
    venv_path = os.path.join("venv_ci_test", "Scripts", "python.exe")
    venv_exists = os.path.exists(venv_path)
    print_status("虚拟环境", venv_exists, venv_path if venv_exists else "未找到")
    
    return venv_exists

def check_dependencies():
    """检查依赖包"""
    print_header("依赖包检查")
    
    try:
        # 检查关键依赖
        critical_packages = [
            "flask", "pytest", "pandas", "numpy", 
            "paddleocr", "layoutparser", "torch"
        ]
        
        for package in critical_packages:
            try:
                __import__(package)
                print_status(f"{package}", True, "已安装")
            except ImportError:
                print_status(f"{package}", False, "未安装")
        
        return True
    except Exception as e:
        print_status("依赖检查", False, str(e))
        return False

def check_project_structure():
    """检查项目结构"""
    print_header("项目结构检查")
    
    required_dirs = ["src", "tests", "config", "templates", "static"]
    required_files = [
        "src/web_app.py", "src/main.py", "config/config.yaml", 
        "requirements.txt", "pytest.ini"
    ]
    
    all_good = True
    
    # 检查目录
    for dir_name in required_dirs:
        exists = os.path.exists(dir_name)
        print_status(f"目录 {dir_name}/", exists)
        if not exists:
            all_good = False
    
    # 检查文件
    for file_name in required_files:
        exists = os.path.exists(file_name)
        print_status(f"文件 {file_name}", exists)
        if not exists:
            all_good = False
    
    return all_good

def run_tests():
    """运行测试"""
    print_header("测试执行")
    
    try:
        # 运行pytest
        result = subprocess.run([
            "venv_ci_test/Scripts/python.exe", "-m", "pytest", 
            "tests/", "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=120)
        
        success = result.returncode == 0
        print_status("pytest测试", success)
        
        if success:
            # 统计测试结果
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if "passed" in line and "warning" in line:
                    print(f"   {line.strip()}")
                    break
        else:
            print(f"   错误: {result.stderr[:200]}...")
        
        return success
    except Exception as e:
        print_status("测试执行", False, str(e))
        return False

def check_web_app():
    """检查Web应用"""
    print_header("Web应用检查")
    
    try:
        # 添加src到路径
        sys.path.insert(0, 'src')
        
        # 尝试导入web应用
        from web_app import app
        print_status("Web应用导入", True)
        
        # 检查应用配置
        print_status("Flask应用", True, f"名称: {app.name}")
        
        return True
    except Exception as e:
        print_status("Web应用", False, str(e))
        return False

def generate_report():
    """生成健康检查报告"""
    print_header("系统健康检查报告")
    
    checks = [
        ("Python环境", check_python_environment()),
        ("依赖包", check_dependencies()),
        ("项目结构", check_project_structure()),
        ("测试执行", run_tests()),
        ("Web应用", check_web_app())
    ]
    
    passed = sum(1 for _, status in checks if status)
    total = len(checks)
    
    print(f"\n总体状态: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 系统健康状态良好，可以正常使用！")
        return True
    else:
        print("⚠️  系统存在问题，请检查失败的项目")
        return False

def main():
    """主函数"""
    print("AI_Pytest7 项目健康检查")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 切换到项目目录
    if not os.path.exists("src"):
        print("❌ 请在项目根目录运行此脚本")
        return False
    
    # 执行健康检查
    return generate_report()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
