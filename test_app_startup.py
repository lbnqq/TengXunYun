#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试应用启动

Author: AI Assistant
Created: 2025-08-03
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_app_startup():
    """测试应用启动"""
    try:
        print("🧪 测试应用启动...")
        
        # 导入web应用
        from src.web_app import app
        
        print("✅ Web应用导入成功")
        
        # 检查路由
        print("📋 检查路由...")
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.methods} {rule.rule}")
        
        # 查找我们关心的路由
        upload_routes = [r for r in routes if '/uploads/' in r]
        export_routes = [r for r in routes if 'export' in r]
        
        print(f"📁 上传相关路由: {len(upload_routes)}")
        for route in upload_routes:
            print(f"   {route}")
            
        print(f"📤 导出相关路由: {len(export_routes)}")
        for route in export_routes:
            print(f"   {route}")
        
        print("✅ 应用启动测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_startup()
    if success:
        print("\n🎉 应用可以正常启动！")
    else:
        print("\n💥 应用启动失败，请检查错误信息。")
