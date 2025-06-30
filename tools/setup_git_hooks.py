#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git钩子安装脚本

自动设置Git预提交钩子，确保代码提交前进行质量检查。

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
import shutil
from pathlib import Path

def setup_pre_commit_hook():
    """
    设置预提交钩子
    
    Author: AI Assistant (Claude)
    Date: 2025-01-28
    AI Assisted: 是
    """
    # 检查是否在Git仓库中
    if not Path('.git').exists():
        print("❌ 不在Git仓库中，请先初始化Git仓库")
        return False
    
    # Git钩子目录
    hooks_dir = Path('.git/hooks')
    pre_commit_hook = hooks_dir / 'pre-commit'
    
    # 预提交钩子内容
    hook_content = '''#!/bin/sh
# 预提交钩子 - 自动质量检查

# 运行Python预提交检查脚本
python tools/pre-commit-hook.py

# 如果检查失败，阻止提交
if [ $? -ne 0 ]; then
    echo "❌ 预提交检查失败，提交被阻止"
    exit 1
fi

echo "✅ 预提交检查通过，允许提交"
exit 0
'''
    
    try:
        # 创建钩子文件
        with open(pre_commit_hook, 'w', encoding='utf-8') as f:
            f.write(hook_content)
        
        # 设置执行权限
        os.chmod(pre_commit_hook, 0o755)
        
        print(f"✅ 预提交钩子已安装: {pre_commit_hook}")
        return True
        
    except Exception as e:
        print(f"❌ 安装预提交钩子失败: {e}")
        return False

def setup_commit_msg_hook():
    """
    设置提交消息钩子
    
    Author: AI Assistant (Claude)
    Date: 2025-01-28
    AI Assisted: 是
    """
    hooks_dir = Path('.git/hooks')
    commit_msg_hook = hooks_dir / 'commit-msg'
    
    # 提交消息钩子内容
    hook_content = '''#!/bin/sh
# 提交消息钩子 - 检查提交消息格式

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# 检查提交消息是否为空
if [ -z "$commit_msg" ]; then
    echo "❌ 提交消息不能为空"
    exit 1
fi

# 检查提交消息长度
if [ ${#commit_msg} -lt 10 ]; then
    echo "❌ 提交消息太短，请提供更详细的描述"
    exit 1
fi

# 检查是否包含常见的前缀
valid_prefixes="feat fix docs style refactor test chore"
first_word=$(echo "$commit_msg" | cut -d' ' -f1)

if [[ " $valid_prefixes " =~ " $first_word " ]]; then
    echo "✅ 提交消息格式正确"
    exit 0
else
    echo "⚠️ 建议使用标准提交前缀: $valid_prefixes"
    echo "当前提交消息: $commit_msg"
    echo "是否继续提交? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        exit 0
    else
        exit 1
    fi
fi
'''
    
    try:
        with open(commit_msg_hook, 'w', encoding='utf-8') as f:
            f.write(hook_content)
        
        os.chmod(commit_msg_hook, 0o755)
        
        print(f"✅ 提交消息钩子已安装: {commit_msg_hook}")
        return True
        
    except Exception as e:
        print(f"❌ 安装提交消息钩子失败: {e}")
        return False

def create_gitignore_entries():
    """
    创建.gitignore条目
    
    Author: AI Assistant (Claude)
    Date: 2025-01-28
    AI Assisted: 是
    """
    gitignore_file = Path('.gitignore')
    
    # 需要添加的条目
    entries = [
        '# 质量检查报告',
        'quality_check_report.md',
        'quality_check_report.json',
        'project_header_fix_report.md',
        'file_header_fix_report.md',
        '',
        '# 备份文件',
        '*.backup',
        '',
        '# 临时文件',
        '*.tmp',
        '*.temp',
        '',
        '# 日志文件',
        '*.log',
        '',
        '# 测试报告',
        'test_results/',
        'reports/',
        '',
        '# IDE文件',
        '.vscode/',
        '.idea/',
        '*.swp',
        '*.swo',
        '',
        '# 系统文件',
        '.DS_Store',
        'Thumbs.db'
    ]
    
    try:
        # 读取现有的.gitignore内容
        existing_content = ""
        if gitignore_file.exists():
            with open(gitignore_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # 检查是否已经包含这些条目
        new_entries = []
        for entry in entries:
            if entry.strip() and entry not in existing_content:
                new_entries.append(entry)
        
        if new_entries:
            # 添加新条目
            with open(gitignore_file, 'a', encoding='utf-8') as f:
                f.write('\n'.join(new_entries))
                f.write('\n')
            
            print(f"✅ 已更新 .gitignore 文件")
        else:
            print("ℹ️ .gitignore 文件已包含所需条目")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新 .gitignore 失败: {e}")
        return False

def main():
    """
    主函数
    
    Author: AI Assistant (Claude)
    Date: 2025-01-28
    AI Assisted: 是
    """
    print("🚀 开始设置Git钩子...")
    
    success_count = 0
    total_count = 0
    
    # 设置预提交钩子
    total_count += 1
    if setup_pre_commit_hook():
        success_count += 1
    
    # 设置提交消息钩子
    total_count += 1
    if setup_commit_msg_hook():
        success_count += 1
    
    # 更新.gitignore
    total_count += 1
    if create_gitignore_entries():
        success_count += 1
    
    print(f"\n📊 设置结果: {success_count}/{total_count} 项成功")
    
    if success_count == total_count:
        print("\n✅ Git钩子设置完成!")
        print("\n📋 已安装的钩子:")
        print("- pre-commit: 提交前自动运行质量检查")
        print("- commit-msg: 检查提交消息格式")
        print("\n💡 使用说明:")
        print("1. 每次提交前会自动运行质量检查")
        print("2. 如果检查失败，提交将被阻止")
        print("3. 提交消息建议使用标准前缀: feat, fix, docs, style, refactor, test, chore")
        print("4. 可以手动运行 `python tools/pre-commit-hook.py` 进行预检查")
        print("5. 可以手动运行 `python tools/automated_quality_check.py` 进行完整检查")
    else:
        print("\n⚠️ 部分设置失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main() 