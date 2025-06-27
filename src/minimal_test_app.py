#!/usr/bin/env python3
"""
最小测试版本的web_app.py
"""

import os
import sys
import json
import uuid
import time
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import pandas as pd
from doc_processor import DocumentProcessor

print("所有导入成功！")

# 创建Flask应用
app = Flask(__name__)
CORS(app)

print("Flask应用创建成功！")

@app.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'message': '真实Web应用测试版本',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    print(f"🚀 启动真实Web应用测试版本: http://{host}:{port}")
    
    app.run(host=host, port=port, debug=False)
