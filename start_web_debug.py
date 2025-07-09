#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试模式启动Web应用
"""

import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == '__main__':
    print("=== 启动AI文档处理Web应用 ===")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    try:
        print("正在导入Web应用...")
        from web_app import app
        print("✅ Web应用导入成功")
        
        print("正在检查应用配置...")
        print(f"应用名称: {app.name}")
        print(f"调试模式: {app.debug}")
        
        print("可用路由:")
        for rule in app.url_map.iter_rules():
            methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"  {rule.rule} [{methods}]")
        
        print("\n=== 启动Flask开发服务器 ===")
        print("服务器地址: http://localhost:5000")
        print("按 Ctrl+C 停止服务器")
        print("-" * 50)
        
        # 启动应用
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
