#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预提交钩子脚本

在Git提交前自动运行质量检查，确保代码符合项目开发规范。
如果检查失败，将阻止提交并显示详细错误信息。

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
import subprocess
from pathlib import Path
from datetime import datetime

def run_command(cmd, cwd=None):
    """
    运行命令并返回结果
    
    Args:
        cmd (list): 命令列表
        cwd (str): 工作目录
        
    Returns:
        tuple: (returncode, stdout, stderr)
        
    Author: AI Assistant (Claude)
    Date: 2025-01-28
    AI Assisted: 是
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',  # 强制使用 utf-8 解码，避免编码错误
            cwd=cwd or Path.cwd()
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_staged_files():
    """
    检查暂存区的文件
    
    Returns:
        list: 暂存的文件列表
        
    Author: AI Assistant (Claude)
    Date: 2025-01-28
    AI Assisted: 是
    """
    returncode, stdout, stderr = run_command(['git', 'diff', '--cached', '--name-only'])
    if returncode != 0:
        print(f"❌ 获取暂存文件失败: {stderr}")
        return []
    
    staged_files = [line.strip() for line in stdout.split('\n') if line.strip()]
    return staged_files

def run_file_header_check():
    """
    运行文件头注释检查
    
    Returns:
        bool: 检查是否通过
        
    Author: AI Assistant (Claude)
    Date: 2025-01-28
    AI Assisted: 是
    """
    print("🔍 检查文件头注释规范...")
    returncode, stdout, stderr = run_command([sys.executable, 'tools/check_file_headers.py'])
    # 修复 NoneType 问题
    if returncode == 0 and stdout and "所有文件头注释都符合规范" in stdout:
        print("✅ 文件头注释检查通过")
        return True
    else:
        print("❌ 文件头注释检查失败")
        if stderr:
            print(f"错误信息: {stderr}")
        return False

def run_syntax_check():
    """
    运行语法检查
    
    Returns:
        bool: 检查是否通过
        
    Author: AI Assistant (Claude)
    Date: 2025-01-28
    AI Assisted: 是
    """
    print("🔍 检查代码语法...")
    
    staged_files = check_staged_files()
    python_files = [f for f in staged_files if f.endswith('.py')]
    
    if not python_files:
        print("✅ 没有Python文件需要检查")
        return True
    
    syntax_errors = []
    for file_path in python_files:
        returncode, stdout, stderr = run_command([sys.executable, '-m', 'py_compile', file_path])
        if returncode != 0:
            syntax_errors.append(f"{file_path}: {stderr}")
    
    if syntax_errors:
        print("❌ 发现语法错误:")
        for error in syntax_errors:
            print(f"  {error}")
        return False
    else:
        print(f"✅ 语法检查通过 ({len(python_files)} 个文件)")
        return True

def run_quality_check():
    """
    运行完整质量检查
    
    Returns:
        bool: 检查是否通过
        
    Author: AI Assistant (Claude)
    Date: 2025-01-28
    AI Assisted: 是
    """
    print("🔍 运行完整质量检查...")
    
    returncode, stdout, stderr = run_command([sys.executable, 'tools/automated_quality_check.py'])
    
    if returncode == 0:
        print("✅ 质量检查通过")
        return True
    else:
        print("❌ 质量检查失败")
        print("详细报告:")
        print(stdout)
        if stderr:
            print("错误信息:")
            print(stderr)
        return False

def main():
    """
    主函数
    
    Author: AI Assistant (Claude)
    Date: 2025-01-28
    AI Assisted: 是
    """
    print("🚀 开始预提交质量检查...")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查是否在Git仓库中
    if not Path('.git').exists():
        print("❌ 不在Git仓库中，跳过预提交检查")
        sys.exit(0)
    
    # 检查暂存的文件
    staged_files = check_staged_files()
    if not staged_files:
        print("ℹ️ 没有暂存的文件，跳过检查")
        sys.exit(0)
    
    print(f"📋 暂存文件数量: {len(staged_files)}")
    
    # 运行各项检查
    checks = [
        ("语法检查", run_syntax_check),
        ("文件头注释检查", run_file_header_check),
        ("完整质量检查", run_quality_check)
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        print(f"\n📋 执行检查: {check_name}")
        if not check_func():
            failed_checks.append(check_name)
    
    # 检查结果
    if failed_checks:
        print(f"\n❌ 预提交检查失败!")
        print(f"失败的检查: {', '.join(failed_checks)}")
        print("\n💡 修复建议:")
        print("1. 修复语法错误")
        print("2. 运行 `python tools/fix_project_headers.py` 修复文件头注释")
        print("3. 确保代码符合项目开发规范")
        print("4. 重新运行 `python tools/automated_quality_check.py` 验证修复结果")
        print("\n提交被阻止，请修复上述问题后重新提交。")
        sys.exit(1)
    else:
        print(f"\n✅ 所有预提交检查都通过了!")
        print("可以安全提交代码。")
        sys.exit(0)

if __name__ == "__main__":
    main()