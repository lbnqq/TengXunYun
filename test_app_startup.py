#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试应用启动
"""

import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_step_by_step():
    print("=== 逐步测试应用启动 ===")
    
    try:
        print("1. 测试基础导入...")
        import os, sys, json
        from datetime import datetime
        print("✅ 基础导入成功")
    except Exception as e:
        print(f"❌ 基础导入失败: {e}")
        return
    
    try:
        print("2. 测试Flask导入...")
        from flask import Flask, request, jsonify, render_template, send_from_directory
        from flask_cors import CORS
        from werkzeug.utils import secure_filename
        print("✅ Flask相关导入成功")
    except Exception as e:
        print(f"❌ Flask导入失败: {e}")
        return
    
    try:
        print("3. 测试配置加载...")
        from utils import load_config
        config = load_config("config/config.yaml")
        print(f"✅ 配置加载成功: {list(config.keys())}")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return
    
    try:
        print("4. 测试OCR引擎导入...")
        from ocr_engine import PaddleOCRWrapper
        print("✅ OCR引擎导入成功")
    except Exception as e:
        print(f"❌ OCR引擎导入失败: {e}")
        print("   这可能是正常的，因为需要模型文件")
    
    try:
        print("5. 测试Flask应用创建...")
        app = Flask(__name__)
        CORS(app)
        print("✅ Flask应用创建成功")
    except Exception as e:
        print(f"❌ Flask应用创建失败: {e}")
        return
    
    try:
        print("6. 测试简单路由...")
        @app.route('/test')
        def test_route():
            return jsonify({'status': 'ok', 'message': 'Test successful'})
        
        print("✅ 路由定义成功")
    except Exception as e:
        print(f"❌ 路由定义失败: {e}")
        return
    
    print("\n=== 启动测试服务器 ===")
    try:
        print("启动Flask开发服务器...")
        app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_step_by_step()
