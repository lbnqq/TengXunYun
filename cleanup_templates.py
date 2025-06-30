#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup Templates

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import os
import shutil
from pathlib import Path

def cleanup_templates():
    """清理模板文件"""
    templates_dir = Path("templates")
    
    print("🧹 开始清理模板文件...")
    
    # 保留的文件列表
    keep_files = [
        "enhanced-frontend-complete.html",  # 主入口页面
        "demo.html",                        # 演示页面
        "batch.html",                       # 批量处理页面
        "README.md"                         # 说明文档
    ]
    
    # 需要备份的文件列表
    backup_files = [
        "dashboard.html"  # 用户选择保留
    ]
    
    # 检查当前状态
    current_files = list(templates_dir.glob("*.html"))
    print(f"📁 当前模板文件: {[f.name for f in current_files]}")
    
    # 处理需要备份的文件
    for file_name in backup_files:
        file_path = templates_dir / file_name
        if file_path.exists():
            backup_path = templates_dir / f"{file_name}.backup"
            if not backup_path.exists():
                shutil.move(str(file_path), str(backup_path))
                print(f"📦 已备份: {file_name} -> {file_name}.backup")
            else:
                print(f"⚠️  备份文件已存在: {file_name}.backup")
    
    # 检查保留的文件
    print("\n✅ 保留的模板文件:")
    for file_name in keep_files:
        file_path = templates_dir / file_name
        if file_path.exists():
            print(f"  ✓ {file_name}")
        else:
            print(f"  ❌ {file_name} (缺失)")
    
    # 显示最终状态
    final_files = list(templates_dir.glob("*.html"))
    print(f"\n📋 清理后的模板文件:")
    for file_path in final_files:
        if file_path.name in keep_files:
            print(f"  ✅ {file_path.name}")
        else:
            print(f"  📦 {file_path.name} (已备份)")
    
    print("\n🎉 模板文件清理完成!")
    print("\n📝 建议:")
    print("1. 主页面使用: enhanced-frontend-complete.html")
    print("2. 演示页面使用: demo.html") 
    print("3. 批量处理使用: batch.html")
    print("4. 如需dashboard功能，可从备份文件恢复")

if __name__ == "__main__":
    cleanup_templates() 