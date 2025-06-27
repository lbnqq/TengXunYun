#!/usr/bin/env python3
"""
最小化的web_app.py版本
包含核心功能但优雅处理缺失的依赖
"""

import os
import sys
import json
import uuid
import time
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import pandas as pd

# 尝试导入CORS，如果失败则跳过
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    print("⚠️  flask_cors not available, CORS will be disabled")
    CORS_AVAILABLE = False

# 尝试导入可选依赖，如果失败则使用模拟版本
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not available, skipping environment loading")
    def load_dotenv():
        pass

# 尝试导入项目模块，如果失败则使用模拟版本
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    from doc_processor import DocumentProcessor
    DOC_PROCESSOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  DocumentProcessor not available: {e}")
    DOC_PROCESSOR_AVAILABLE = False
    
    class DocumentProcessor:
        def __init__(self):
            pass
        
        def fill_tables(self, tables, fill_data):
            # 简化的填充逻辑
            filled_tables = []
            for df in tables:
                if not isinstance(df, pd.DataFrame) or df.empty:
                    filled_tables.append(df)
                    continue
                
                df_copy = df.copy()
                table_columns = set(df_copy.columns)
                
                matching_fill_data = []
                for row in fill_data:
                    row_columns = set(row.keys())
                    if table_columns.intersection(row_columns):
                        matching_fill_data.append(row)
                
                for i, row in enumerate(matching_fill_data):
                    if i < len(df_copy):
                        for col in df_copy.columns:
                            if col in row and row[col] is not None:
                                df_copy.at[i, col] = row[col]
                
                filled_tables.append(df_copy)
            return filled_tables

# 尝试导入其他模块，如果失败则跳过
try:
    from core.agent.agent_orchestrator import AgentOrchestrator
    AGENT_AVAILABLE = True
except ImportError:
    print("⚠️  AgentOrchestrator not available")
    AGENT_AVAILABLE = False
    class AgentOrchestrator:
        def __init__(self, *args, **kwargs):
            pass

try:
    from core.database import get_database_manager, ProcessingStatus
    DATABASE_AVAILABLE = True
except ImportError:
    print("⚠️  Database modules not available")
    DATABASE_AVAILABLE = False
    def get_database_manager():
        return None
    
    class ProcessingStatus:
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

# 创建Flask应用
app = Flask(__name__)
if CORS_AVAILABLE:
    CORS(app)
else:
    # 手动添加CORS头部
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

# 配置
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 全局变量
doc_processor = DocumentProcessor()
agent_orchestrator = None
if AGENT_AVAILABLE:
    try:
        # 尝试创建AgentOrchestrator，如果失败则设为None
        agent_orchestrator = AgentOrchestrator(llm_client=None)
    except Exception as e:
        print(f"⚠️  AgentOrchestrator initialization failed: {e}")
        agent_orchestrator = None

@app.route('/')
def index():
    """主页"""
    return jsonify({
        'status': 'ok',
        'message': '办公文档智能代理系统',
        'version': '1.0.0',
        'features': {
            'doc_processor': DOC_PROCESSOR_AVAILABLE,
            'agent_orchestrator': AGENT_AVAILABLE,
            'database': DATABASE_AVAILABLE
        }
    })

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'document_processor': 'active' if DOC_PROCESSOR_AVAILABLE else 'mock',
            'agent_orchestrator': 'active' if AGENT_AVAILABLE else 'mock',
            'database': 'active' if DATABASE_AVAILABLE else 'mock'
        }
    })

@app.route('/api/table-fill', methods=['POST'])
def api_table_fill():
    """智能表格批量填充API"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': '请求必须是JSON格式'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
        
        if 'tables' not in data:
            return jsonify({'success': False, 'error': '缺少必需字段: tables'}), 400
        
        if 'fill_data' not in data:
            return jsonify({'success': False, 'error': '缺少必需字段: fill_data'}), 400
        
        tables = data['tables']
        fill_data = data['fill_data']
        
        if not isinstance(tables, list):
            return jsonify({'success': False, 'error': 'tables必须是数组'}), 400
        
        if not isinstance(fill_data, list):
            return jsonify({'success': False, 'error': 'fill_data必须是数组'}), 400
        
        if len(tables) == 0:
            return jsonify({'success': True, 'filled_tables': []})
        
        # 验证表格结构
        pd_tables = []
        for i, t in enumerate(tables):
            if not isinstance(t, dict):
                return jsonify({'success': False, 'error': f'表格{i+1}必须是对象'}), 400
            
            if 'columns' not in t or 'data' not in t:
                return jsonify({'success': False, 'error': f'表格{i+1}缺少必需字段'}), 400
            
            if not isinstance(t['columns'], list) or not isinstance(t['data'], list):
                return jsonify({'success': False, 'error': f'表格{i+1}格式错误'}), 400
            
            try:
                df = pd.DataFrame(t['data'], columns=t['columns'])
                pd_tables.append(df)
            except Exception as e:
                return jsonify({'success': False, 'error': f'表格{i+1}数据格式错误: {str(e)}'}), 400
        
        # 验证填充数据
        for i, item in enumerate(fill_data):
            if not isinstance(item, dict):
                return jsonify({'success': False, 'error': f'填充数据{i+1}必须是对象'}), 400
        
        # 执行表格填充
        filled_tables = doc_processor.fill_tables(pd_tables, fill_data)
        
        # 返回结果
        result = []
        for df in filled_tables:
            result.append({
                'columns': list(df.columns),
                'data': df.values.tolist()
            })
        
        return jsonify({'success': True, 'filled_tables': result})
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器内部错误: {str(e)}'}), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """文件上传API"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400
        
        # 检查文件类型
        allowed_extensions = {'txt', 'pdf', 'docx', 'doc'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False, 
                'error': f'不支持的文件类型: {file_ext}'
            }), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except:
                content = "无法读取文件内容"
        
        return jsonify({
            'success': True,
            'message': '文件上传成功',
            'filename': filename,
            'size': os.path.getsize(file_path),
            'content_preview': content[:200] + '...' if len(content) > 200 else content,
            'doc_processor_available': DOC_PROCESSOR_AVAILABLE
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'文件上传失败: {str(e)}'}), 500

@app.route('/api/documents', methods=['GET'])
def api_documents():
    """获取文档列表"""
    try:
        # 模拟文档列表
        documents = [
            {
                'id': '1',
                'filename': 'sample1.txt',
                'status': 'completed',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': '2', 
                'filename': 'sample2.docx',
                'status': 'processing',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        return jsonify({
            'success': True,
            'documents': documents,
            'total': len(documents)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/settings', methods=['GET'])
def api_settings():
    """获取系统设置"""
    try:
        settings = {
            'max_file_size': app.config['MAX_CONTENT_LENGTH'],
            'allowed_extensions': ['txt', 'pdf', 'docx', 'doc'],
            'features': {
                'doc_processor': DOC_PROCESSOR_AVAILABLE,
                'agent_orchestrator': AGENT_AVAILABLE,
                'database': DATABASE_AVAILABLE
            }
        }
        
        return jsonify({
            'success': True,
            'settings': settings
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'API端点不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 启动最小化Web应用: http://{host}:{port}")
    print(f"📋 功能状态:")
    print(f"   DocumentProcessor: {'✅' if DOC_PROCESSOR_AVAILABLE else '⚠️  模拟'}")
    print(f"   AgentOrchestrator: {'✅' if AGENT_AVAILABLE else '⚠️  模拟'}")
    print(f"   Database: {'✅' if DATABASE_AVAILABLE else '⚠️  模拟'}")
    
    app.run(host=host, port=port, debug=debug)
