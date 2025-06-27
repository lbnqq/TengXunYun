#!/usr/bin/env python3
"""
逐步测试web_app.py的导入
"""

print("开始逐步测试导入...")

try:
    print("1. 测试基础模块...")
    import os
    import sys
    import json
    import uuid
    import time
    import traceback
    from datetime import datetime
    print("✅ 基础模块导入成功")
except Exception as e:
    print(f"❌ 基础模块导入失败: {e}")
    exit(1)

try:
    print("2. 测试Flask...")
    from flask import Flask, request, jsonify, render_template, send_from_directory
    print("✅ Flask导入成功")
except Exception as e:
    print(f"❌ Flask导入失败: {e}")
    exit(1)

try:
    print("3. 测试flask_cors...")
    from flask_cors import CORS
    print("✅ flask_cors导入成功")
except Exception as e:
    print(f"❌ flask_cors导入失败: {e}")
    exit(1)

try:
    print("4. 测试werkzeug...")
    from werkzeug.utils import secure_filename
    print("✅ werkzeug导入成功")
except Exception as e:
    print(f"❌ werkzeug导入失败: {e}")
    exit(1)

try:
    print("5. 测试dotenv...")
    from dotenv import load_dotenv
    print("✅ dotenv导入成功")
except Exception as e:
    print(f"❌ dotenv导入失败: {e}")
    exit(1)

try:
    print("6. 测试pandas...")
    import pandas as pd
    print("✅ pandas导入成功")
except Exception as e:
    print(f"❌ pandas导入失败: {e}")
    exit(1)

try:
    print("7. 测试doc_processor...")
    from doc_processor import DocumentProcessor
    print("✅ doc_processor导入成功")
except Exception as e:
    print(f"❌ doc_processor导入失败: {e}")
    print(f"   错误详情: {e}")

print("\n🎉 所有导入测试完成！")
