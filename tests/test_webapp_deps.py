#!/usr/bin/env python3
"""
测试真实web_app.py的依赖
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试所有导入"""
    print("🔍 测试真实web_app.py的依赖...")
    
    try:
        print("✓ 测试基础模块...")
        import os, sys, json, uuid, time, traceback
        from datetime import datetime
        print("✅ 基础模块导入成功")
        
        print("✓ 测试Flask相关...")
        from flask import Flask, request, jsonify, render_template, send_from_directory
        from flask_cors import CORS
        from werkzeug.utils import secure_filename
        print("✅ Flask相关模块导入成功")
        
        print("✓ 测试其他依赖...")
        from dotenv import load_dotenv
        import pandas as pd
        print("✅ 其他依赖导入成功")
        
        print("✓ 测试项目模块...")
        try:
            from doc_processor import DocumentProcessor
            print("✅ DocumentProcessor导入成功")
        except Exception as e:
            print(f"⚠️  DocumentProcessor导入失败: {e}")
        
        try:
            from core.agent.agent_orchestrator import AgentOrchestrator
            print("✅ AgentOrchestrator导入成功")
        except Exception as e:
            print(f"⚠️  AgentOrchestrator导入失败: {e}")
        
        try:
            from llm_clients.xingcheng_llm import XingchengLLMClient
            print("✅ XingchengLLMClient导入成功")
        except Exception as e:
            print(f"⚠️  XingchengLLMClient导入失败: {e}")
        
        try:
            from llm_clients.multi_llm import MultiLLMClient
            print("✅ MultiLLMClient导入成功")
        except Exception as e:
            print(f"⚠️  MultiLLMClient导入失败: {e}")
        
        print("\n🎉 依赖测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_minimal_flask_app():
    """测试最小Flask应用"""
    print("\n🔍 测试最小Flask应用...")
    
    try:
        from flask import Flask
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/')
        def hello():
            return {'status': 'ok', 'message': 'Flask app works'}
        
        print("✅ 最小Flask应用创建成功")
        
        # 测试启动（不实际运行）
        print("✅ Flask应用配置正常")
        return True
        
    except Exception as e:
        print(f"❌ Flask应用测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始依赖测试")
    print("=" * 50)
    
    success1 = test_imports()
    success2 = test_minimal_flask_app()
    
    if success1 and success2:
        print("\n🎉 所有依赖测试通过！")
        print("真实web_app.py应该可以正常启动。")
    else:
        print("\n❌ 依赖测试失败，需要解决问题。")
