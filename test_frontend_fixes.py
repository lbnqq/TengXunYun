#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端修复验证测试脚本
验证缺失的操作处理函数是否已正确添加
"""

import os
import sys
import json
from pathlib import Path

def test_js_file_contains_actions():
    """测试JavaScript文件是否包含所有必需的操作处理函数"""
    js_file = Path("static/js/enhanced-frontend-complete.js")
    
    if not js_file.exists():
        print("❌ JavaScript文件不存在")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必需的操作处理函数
    required_actions = [
        'auto_match_data',
        'manual_match', 
        'export_filled_doc',
        'preview_fill',
        'export_fill',
        'preview_fill_result',
        'export_fill_result',
        'preview_style',
        'export_style'
    ]
    
    missing_actions = []
    for action in required_actions:
        if f"case '{action}':" not in content:
            missing_actions.append(action)
    
    if missing_actions:
        print(f"❌ 缺少操作处理函数: {missing_actions}")
        return False
    
    print("✅ 所有必需的操作处理函数已添加")
    return True

def test_html_file_contains_buttons():
    """测试HTML文件是否包含所有必需的按钮"""
    html_file = Path("templates/enhanced-frontend-complete.html")
    
    if not html_file.exists():
        print("❌ HTML文件不存在")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必需的按钮
    required_buttons = [
        'data-action="auto_match_data"',
        'data-action="manual_match"',
        'data-action="export_filled_doc"'
    ]
    
    missing_buttons = []
    for button in required_buttons:
        if button not in content:
            missing_buttons.append(button)
    
    if missing_buttons:
        print(f"❌ 缺少按钮: {missing_buttons}")
        return False
    
    print("✅ 所有必需的按钮已添加")
    return True

def test_get_current_session_id():
    """测试getCurrentSessionId方法是否存在"""
    js_file = Path("static/js/enhanced-frontend-complete.js")
    
    if not js_file.exists():
        print("❌ JavaScript文件不存在")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "getCurrentSessionId()" not in content:
        print("❌ getCurrentSessionId方法不存在")
        return False
    
    print("✅ getCurrentSessionId方法已添加")
    return True

def main():
    """主测试函数"""
    print("🔍 开始验证前端修复...")
    print("=" * 50)
    
    tests = [
        ("JavaScript操作处理函数", test_js_file_contains_actions),
        ("HTML按钮元素", test_html_file_contains_buttons),
        ("getCurrentSessionId方法", test_get_current_session_id)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有前端修复验证通过！")
        return True
    else:
        print("⚠️ 部分前端修复验证失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 