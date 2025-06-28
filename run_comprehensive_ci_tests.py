#!/usr/bin/env python3
"""
虚拟环境下全面CI自动化集成测试运行脚本

Author: AI Assistant
Date: 2025-01-28
"""

import os
import sys
import subprocess
import venv
import platform
from pathlib import Path

def create_virtual_environment():
    """创建虚拟环境"""
    print("🔧 创建虚拟环境...")
    
    venv_path = Path("venv_ci_test")
    if venv_path.exists():
        print("⚠️ 虚拟环境已存在，跳过创建")
        return venv_path
    
    venv.create(venv_path, with_pip=True)
    print(f"✅ 虚拟环境已创建: {venv_path}")
    return venv_path

def get_python_executable(venv_path):
    """获取虚拟环境中的Python可执行文件路径"""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

def get_pip_executable(venv_path):
    """获取虚拟环境中的pip可执行文件路径"""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"

def install_dependencies(venv_path):
    """在虚拟环境中安装依赖"""
    print("📦 安装依赖包...")
    
    python_exe = get_python_executable(venv_path)
    pip_exe = get_pip_executable(venv_path)
    
    # 升级pip
    subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # 安装requirements.txt中的依赖
    subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], check=True)
    
    print("✅ 依赖安装完成")

def run_tests_in_venv(venv_path):
    """在虚拟环境中运行测试"""
    print("🚀 在虚拟环境中运行测试...")
    
    python_exe = get_python_executable(venv_path)
    
    # 设置环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())
    
    # 1. 运行代码质量检查
    print("\n🔍 运行代码质量检查...")
    try:
        subprocess.run([str(python_exe), "-m", "flake8", "src/", "tests/", "--max-line-length=120", "--ignore=E203,W503"], 
                      check=True, env=env)
        print("✅ Flake8检查通过")
    except subprocess.CalledProcessError:
        print("❌ Flake8检查失败")
        return False
    
    try:
        subprocess.run([str(python_exe), "-m", "mypy", "src/", "--ignore-missing-imports", "--no-strict-optional"], 
                      check=True, env=env)
        print("✅ MyPy类型检查通过")
    except subprocess.CalledProcessError:
        print("❌ MyPy类型检查失败")
        return False
    
    # 2. 运行单元测试
    print("\n🔍 运行单元测试...")
    try:
        subprocess.run([str(python_exe), "-m", "pytest", "tests/", "-v", "--tb=short"], 
                      check=True, env=env)
        print("✅ 单元测试通过")
    except subprocess.CalledProcessError:
        print("❌ 单元测试失败")
        return False
    
    # 3. 运行覆盖率测试
    print("\n🔍 运行覆盖率测试...")
    try:
        subprocess.run([str(python_exe), "-m", "pytest", "tests/", "--cov=src", "--cov-report=html", "--cov-report=term-missing"], 
                      check=True, env=env)
        print("✅ 覆盖率测试通过")
    except subprocess.CalledProcessError:
        print("❌ 覆盖率测试失败")
        return False
    
    # 4. 运行MVP功能测试
    print("\n🔍 运行MVP功能测试...")
    try:
        subprocess.run([str(python_exe), "tests/test_mvp_functionality.py"], 
                      check=True, env=env)
        print("✅ MVP功能测试通过")
    except subprocess.CalledProcessError:
        print("❌ MVP功能测试失败")
        return False
    
    # 5. 运行安全检查
    print("\n🔍 运行安全检查...")
    try:
        subprocess.run([str(python_exe), "-m", "bandit", "-r", "src/", "-f", "json"], 
                      check=True, env=env)
        print("✅ 安全检查通过")
    except subprocess.CalledProcessError:
        print("❌ 安全检查失败")
        return False
    
    # 6. 运行桩子函数检测
    print("\n🔍 运行桩子函数检测...")
    try:
        subprocess.run([str(python_exe), "tools/stub_function_detector.py", "--json", "docs/stub_detection_result.json"], 
                      check=True, env=env)
        print("✅ 桩子函数检测通过")
    except subprocess.CalledProcessError:
        print("❌ 桩子函数检测失败")
        return False
    
    # 7. 生成测试报告
    print("\n🔍 生成测试报告...")
    try:
        subprocess.run([str(python_exe), "tests/generate_test_report.py"], 
                      check=True, env=env)
        print("✅ 测试报告生成完成")
    except subprocess.CalledProcessError:
        print("❌ 测试报告生成失败")
        return False
    
    return True

def run_integration_tests(venv_path):
    """运行集成测试"""
    print("\n🔍 运行集成测试...")
    
    python_exe = get_python_executable(venv_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())
    
    integration_tests = [
        "tests/test_integration.py",
        "tests/test_comprehensive_integration.py",
        "tests/test_e2e_complete_system.py",
        "tests/test_e2e_workflow.py"
    ]
    
    for test_file in integration_tests:
        if Path(test_file).exists():
            print(f"  运行 {test_file}...")
            try:
                subprocess.run([str(python_exe), "-m", "pytest", test_file, "-v", "--timeout=300"], 
                              check=True, env=env)
                print(f"  ✅ {test_file} 通过")
            except subprocess.CalledProcessError:
                print(f"  ❌ {test_file} 失败")
                return False
        else:
            print(f"  ⚠️ {test_file} 不存在，跳过")
    
    return True

def run_api_tests(venv_path):
    """运行API测试"""
    print("\n🔍 运行API测试...")
    
    python_exe = get_python_executable(venv_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())
    
    api_tests = [
        "tests/test_api_comprehensive.py",
        "tests/test_api_content_type.py"
    ]
    
    for test_file in api_tests:
        if Path(test_file).exists():
            print(f"  运行 {test_file}...")
            try:
                subprocess.run([str(python_exe), "-m", "pytest", test_file, "-v", "--timeout=300"], 
                              check=True, env=env)
                print(f"  ✅ {test_file} 通过")
            except subprocess.CalledProcessError:
                print(f"  ❌ {test_file} 失败")
                return False
        else:
            print(f"  ⚠️ {test_file} 不存在，跳过")
    
    return True

def cleanup_venv(venv_path):
    """清理虚拟环境"""
    print(f"\n🧹 清理虚拟环境: {venv_path}")
    import shutil
    if venv_path.exists():
        shutil.rmtree(venv_path)
        print("✅ 虚拟环境已清理")

def main():
    """主函数"""
    print("🚀 开始虚拟环境下全面CI自动化集成测试")
    print("=" * 60)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    
    print(f"✅ Python版本: {sys.version}")
    
    venv_path = None
    try:
        # 1. 创建虚拟环境
        venv_path = create_virtual_environment()
        
        # 2. 安装依赖
        install_dependencies(venv_path)
        
        # 3. 运行基础测试
        if not run_tests_in_venv(venv_path):
            print("❌ 基础测试失败")
            sys.exit(1)
        
        # 4. 运行集成测试
        if not run_integration_tests(venv_path):
            print("❌ 集成测试失败")
            sys.exit(1)
        
        # 5. 运行API测试
        if not run_api_tests(venv_path):
            print("❌ API测试失败")
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        
        # 显示测试结果文件
        test_results = list(Path("test_results").glob("*.json"))
        if test_results:
            latest_result = max(test_results, key=lambda p: p.stat().st_mtime)
            print(f"📊 测试报告: {latest_result}")
        
        html_results = list(Path("test_results").glob("*.html"))
        if html_results:
            latest_html = max(html_results, key=lambda p: p.stat().st_mtime)
            print(f"📊 HTML报告: {latest_html}")
        
        if Path("htmlcov").exists():
            print(f"📊 覆盖率报告: htmlcov/index.html")
        
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)
    finally:
        # 询问是否清理虚拟环境
        if venv_path and venv_path.exists():
            response = input("\n是否清理虚拟环境？(y/N): ").strip().lower()
            if response in ['y', 'yes']:
                cleanup_venv(venv_path)

if __name__ == '__main__':
    main() 