#!/usr/bin/env python3
"""
测试Dashboard链接功能
"""

import os
import sys

def test_dashboard_link():
    """测试Dashboard链接功能"""
    print("🔗 测试Dashboard链接功能...")
    
    # 检查文件是否存在
    files_to_check = [
        "templates/dashboard.html",
        "static/js/dashboard.js",
        "src/web_app.py"
    ]
    
    print("\n📁 检查必要文件:")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (缺失)")
    
    # 检查路由配置
    print("\n🔍 检查路由配置:")
    try:
        with open("src/web_app.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "@app.route('/dashboard')" in content:
                print("  ✅ Dashboard路由已配置")
            else:
                print("  ❌ Dashboard路由未找到")
    except Exception as e:
        print(f"  ❌ 无法读取web_app.py: {e}")
    
    # 检查主页面链接
    print("\n🔗 检查主页面链接:")
    try:
        with open("templates/enhanced-frontend-complete.html", "r", encoding="utf-8") as f:
            content = f.read()
            if 'href="/dashboard"' in content:
                print("  ✅ Dashboard链接已添加到主页面")
            else:
                print("  ❌ Dashboard链接未找到")
            
            if 'dashboard-link' in content:
                print("  ✅ Dashboard链接样式类已添加")
            else:
                print("  ❌ Dashboard链接样式类未找到")
    except Exception as e:
        print(f"  ❌ 无法读取主页面: {e}")
    
    # 检查CSS样式
    print("\n🎨 检查CSS样式:")
    try:
        with open("static/css/enhanced-frontend-complete.css", "r", encoding="utf-8") as f:
            content = f.read()
            if '.dashboard-link' in content:
                print("  ✅ Dashboard链接CSS样式已添加")
            else:
                print("  ❌ Dashboard链接CSS样式未找到")
    except Exception as e:
        print(f"  ❌ 无法读取CSS文件: {e}")
    
    print("\n🎉 Dashboard链接功能测试完成!")
    print("\n📝 使用说明:")
    print("1. 启动服务器: python src/web_app.py")
    print("2. 访问主页面: http://localhost:5000")
    print("3. 点击导航栏中的'📊 性能监控'链接")
    print("4. Dashboard将在新标签页中打开")

if __name__ == "__main__":
    test_dashboard_link() 