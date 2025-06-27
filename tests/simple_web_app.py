#!/usr/bin/env python3
"""
简化的Web应用
专门用于测试和调试，包含基本功能
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

# 加载环境变量
load_dotenv()

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir

# 创建Flask应用，指定模板和静态文件路径
app = Flask(__name__,
           template_folder=os.path.join(project_root, 'templates'),
           static_folder=os.path.join(project_root, 'static'))
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(project_root, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(project_root, 'output'), exist_ok=True)

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def mock_process_document(file_path):
    """模拟文档处理"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 模拟分析结果
        analysis = {
            'document_type': '通用文档',
            'scenario': '文档分析',
            'key_entities': [
                {'type': '关键词', 'value': '测试'},
                {'type': '关键词', 'value': '文档'},
                {'type': '关键词', 'value': '处理'}
            ],
            'summary': f'这是一个包含{len(content)}个字符的文档',
            'completeness': 85,
            'suggestions': ['建议增加更多详细信息', '建议优化文档结构']
        }
        
        return {
            'file_id': str(uuid.uuid4()),
            'analysis': analysis,
            'document_type': analysis['document_type'],
            'scenario': analysis['scenario'],
            'key_entities': analysis['key_entities'],
            'processing_time': time.time(),
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'error': f'文档处理失败: {str(e)}',
            'status': 'error'
        }

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/debug_test.html')
def debug_test():
    """调试测试页面"""
    try:
        with open('debug_test.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Debug test page not found", 404

@app.route('/test_upload.html')
def test_upload():
    """文件上传测试页面"""
    try:
        with open('test_upload.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Upload test page not found", 404

@app.route('/fixed_upload.js')
def fixed_upload_js():
    """修复的上传脚本"""
    try:
        with open('fixed_upload.js', 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "Fixed upload script not found", 404

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0-simple'
    })

@app.route('/api/config')
def get_config():
    """获取配置信息"""
    return jsonify({
        'api_types': ['mock'],
        'max_file_size': app.config['MAX_CONTENT_LENGTH'],
        'allowed_extensions': list(app.config['ALLOWED_EXTENSIONS']),
        'features': {
            'document_analysis': True,
            'style_analysis': True,
            'format_alignment': True,
            'batch_processing': True
        }
    })

@app.route('/api/models')
def get_models():
    """获取可用模型"""
    return jsonify({
        'models': {
            'mock': ['mock-model', 'test-model']
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传和处理"""
    print("=" * 80)
    print("🚀 UPLOAD REQUEST RECEIVED")
    print("=" * 80)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print(f"🌐 Remote address: {request.remote_addr}")
    
    # 检查是否是批量处理上传
    batch_upload = request.form.get('batch_upload', 'false').lower() == 'true'
    print(f"📦 Batch upload mode: {batch_upload}")
    
    if batch_upload:
        return handle_batch_upload()
    
    # Debug request information
    print(f"📋 Request method: {request.method}")
    print(f"📋 Request content type: {request.content_type}")
    print(f"📋 Request files: {list(request.files.keys())}")
    print(f"📋 Request form data: {dict(request.form)}")
    
    if 'file' not in request.files:
        print("❌ ERROR: No file provided in request")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        print("❌ ERROR: No file selected")
        return jsonify({'error': 'No file selected'}), 400
    
    print(f"📄 File info:")
    print(f"   - Filename: {file.filename}")
    print(f"   - Content type: {file.content_type}")
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    print(f"   - File size: {file_size} bytes")
    
    if not allowed_file(file.filename):
        print(f"❌ ERROR: File type not allowed: {file.filename}")
        return jsonify({'error': 'Unsupported file type'}), 400
    
    # 获取API类型和模型名称
    api_type = request.form.get('api_type', 'mock')
    model_name = request.form.get('model_name', 'mock-model')
    
    print(f"🔧 Processing configuration:")
    print(f"   - API type: {api_type}")
    print(f"   - Model name: {model_name}")
    
    # Generate unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    print(f"💾 Saving file to: {filepath}")
    print(f"💾 Directory exists: {os.path.exists(os.path.dirname(filepath))}")
    print(f"💾 Directory writable: {os.access(os.path.dirname(filepath), os.W_OK)}")
    
    try:
        file.save(filepath)
        print(f"✅ File saved successfully")
    except Exception as save_error:
        print(f"❌ ERROR: File save failed with exception: {save_error}")
        return jsonify({'error': f'File save failed: {str(save_error)}'}), 500
    
    # Verify file exists and is readable
    if os.path.exists(filepath):
        file_size_on_disk = os.path.getsize(filepath)
        print(f"✅ File verified on disk: {file_size_on_disk} bytes")
        print(f"✅ File readable: {os.access(filepath, os.R_OK)}")
    else:
        print(f"❌ ERROR: File not found on disk after save!")
        return jsonify({'error': 'File save failed - file not found on disk'}), 500
    
    # Process document
    print(f"🔄 Starting document processing...")
    try:
        result = mock_process_document(filepath)
        print(f"✅ Document processing completed")

        # 包装结果以匹配前端期望的格式
        response = {
            'success': True,
            'result': result,
            'message': '文档处理成功'
        }
        return jsonify(response)

    except Exception as e:
        print(f"❌ ERROR: Document processing failed: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Document processing failed: {str(e)}'}), 500

def handle_batch_upload():
    """处理批量上传"""
    print("📦 Processing batch upload...")
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files provided for batch upload'}), 400
    
    uploaded_files = []
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            try:
                file.save(filepath)
                uploaded_files.append({
                    'original_name': file.filename,
                    'saved_name': unique_filename,
                    'file_path': filepath,
                    'status': 'success'
                })
            except Exception as e:
                uploaded_files.append({
                    'original_name': file.filename,
                    'status': 'error',
                    'error': str(e)
                })
    
    return jsonify({
        'batch_id': str(uuid.uuid4()),
        'uploaded_files': uploaded_files,
        'total_files': len(files),
        'successful_uploads': len([f for f in uploaded_files if f['status'] == 'success'])
    })

@app.route('/api/analyze_style', methods=['POST'])
def analyze_style():
    """文风分析API"""
    print("🎨 Style analysis request received")
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # 保存文件
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    
    # 模拟文风分析
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        style_analysis = {
            'style_features': {
                'formality': 0.7,
                'complexity': 0.6,
                'emotion': 0.5,
                'objectivity': 0.8
            },
            'analysis': {
                'sentence_length': 'medium',
                'vocabulary_level': 'professional',
                'tone': 'formal',
                'structure': 'organized'
            },
            'suggestions': [
                '保持当前的正式语调',
                '可以适当增加一些生动的表达'
            ]
        }
        
        return jsonify(style_analysis)
        
    except Exception as e:
        return jsonify({'error': f'Style analysis failed: {str(e)}'}), 500

@app.route('/api/format_alignment', methods=['POST'])
def format_alignment():
    """格式对齐API"""
    print("📐 Format alignment request received")

    if 'source_file' not in request.files or 'target_file' not in request.files:
        return jsonify({'error': 'Both source and target files are required'}), 400

    # 模拟格式对齐
    alignment_result = {
        'aligned_content': '这是对齐后的内容示例',
        'alignment_result': {
            'changes_made': ['调整段落间距', '统一标题格式', '优化列表样式'],
            'similarity_score': 0.85,
            'alignment_quality': 'good'
        }
    }

    return jsonify(alignment_result)

@app.route('/api/format-templates')
def get_format_templates():
    """获取格式模板"""
    return jsonify({
        'success': True,
        'templates': [
            {'id': 'business', 'name': '商务文档', 'description': '正式商务文档格式'},
            {'id': 'academic', 'name': '学术论文', 'description': '学术论文格式'},
            {'id': 'report', 'name': '报告格式', 'description': '标准报告格式'}
        ]
    })

@app.route('/api/document-fill/start', methods=['POST'])
def start_document_fill():
    """启动文档填充"""
    print("📝 Document fill start request received")

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # 模拟文档填充启动
    return jsonify({
        'task_id': str(uuid.uuid4()),
        'status': 'started',
        'message': '文档填充任务已启动',
        'estimated_time': 30
    })

@app.route('/batch')
def batch_page():
    """批量处理页面"""
    return render_template('batch.html')

@app.route('/dashboard')
def dashboard_page():
    """仪表板页面"""
    return render_template('dashboard.html')

# 文档填充相关API端点
@app.route('/api/document-fill/add-material', methods=['POST'])
def add_material():
    """添加填充材料"""
    return jsonify({'success': True, 'message': '材料已添加'})

@app.route('/api/writing-style/templates')
def get_writing_style_templates():
    """获取文风模板"""
    return jsonify({
        'success': True,
        'templates': [
            {'id': 'formal', 'name': '正式文风', 'description': '正式商务文风'},
            {'id': 'casual', 'name': '轻松文风', 'description': '轻松友好文风'},
            {'id': 'academic', 'name': '学术文风', 'description': '学术论文文风'}
        ]
    })

@app.route('/api/document-fill/set-style', methods=['POST'])
def set_style():
    """设置文风"""
    return jsonify({'success': True, 'message': '文风已设置'})

@app.route('/api/document-fill/respond', methods=['POST'])
def respond_to_fill():
    """响应填充请求"""
    return jsonify({'success': True, 'message': '响应已处理'})

@app.route('/api/document-fill/result')
def get_fill_result():
    """获取填充结果"""
    return jsonify({
        'success': True,
        'result': {
            'filled_content': '这是填充后的文档内容示例',
            'completion_rate': 85,
            'suggestions': ['建议1', '建议2']
        }
    })

@app.route('/api/document-fill/download')
def download_filled_document():
    """下载填充后的文档"""
    return jsonify({'success': True, 'download_url': '/static/sample.docx'})

@app.route('/api/format-templates/<template_id>/apply', methods=['POST'])
def apply_format_template(template_id):
    """应用格式模板"""
    return jsonify({
        'success': True,
        'message': f'格式模板 {template_id} 已应用',
        'formatted_content': '这是应用格式模板后的内容'
    })

if __name__ == '__main__':
    print("Starting Simple Office Document Agent Web Server...")
    print(f"Project root: {project_root}")
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    print("Web interface will be available at: http://localhost:5000")
    print("API endpoints:")
    print("  - GET  /api/health     - Health check")
    print("  - GET  /api/config     - Configuration info")
    print("  - GET  /api/models     - Available models")
    print("  - POST /api/upload     - Upload and process document")
    print("  - POST /api/analyze_style - Style analysis")
    print("  - POST /api/format_alignment - Format alignment")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
