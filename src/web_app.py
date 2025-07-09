#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用主文件

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""













import os
import sys
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入智能填报模块
try:
    from llm_clients.spark_x1_client import SparkX1Client
    from core.tools.simple_smart_fill_manager import SimpleSmartFillManager
    SPARK_X1_AVAILABLE = True
except ImportError as e:
    print(f"警告: 智能填报模块导入失败: {e}")
    SPARK_X1_AVAILABLE = False

# 创建Flask应用
app = Flask(__name__, 
           template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
           static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 启用CORS
CORS(app)

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化智能填报管理器
integrated_manager = None
if SPARK_X1_AVAILABLE:
    try:
        smart_fill_config = {
            'spark_x1_api_password': 'NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh'
        }
        integrated_manager = SimpleSmartFillManager(smart_fill_config)
        print("✅ 简化智能填报管理器初始化成功")
    except Exception as e:
        print(f"❌ 智能填报管理器初始化失败: {e}")
        integrated_manager = None

# 模拟数据存储
document_history = []
format_templates = [
    {'id': 'template1', 'name': '标准格式', 'description': '标准文档格式模板', 'type': 'baseline'}
]
writing_style_templates = [
    {'id': 'style1', 'name': '正式文风', 'description': '正式商务文风模板'}
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

# 主页路由
@app.route('/')
def index():
    """主页"""
    try:
        return render_template('enhanced-frontend-complete.html')
    except Exception as e:
        # 如果模板不存在，返回简单的HTML页面
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI文档处理系统</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>AI文档处理系统</h1>
            <p>系统正在运行中...</p>
            <p>API端点：</p>
            <ul>
                <li><a href="/api/health">健康检查</a></li>
                <li><a href="/dashboard">仪表板</a></li>
                <li>POST /api/upload - 文件上传</li>
            </ul>
            <p>错误信息: {str(e)}</p>
        </body>
        </html>
        '''

# 健康检查路由
@app.route('/api/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'AI文档处理系统'
    })

@app.route('/dashboard')
def dashboard():
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400
            
        # 支持多种参数格式
        source_content = data.get('source_content', '')
        target_content = data.get('target_content', '')
        
        # 如果直接传入了文件内容，使用文件内容
        if not source_content and 'source_file' in data:
            source_content = data['source_file']
        if not target_content and 'target_file' in data:
            target_content = data['target_file']
            
        # 如果传入了files数组，尝试从files中获取内容
        if not source_content or not target_content:
            files = data.get('files', [])
            if len(files) >= 2:
                # 处理files参数 - 支持字符串数组和对象数组
                if isinstance(files[0], dict):
                    source_content = f"参考文件内容: {files[0].get('name', 'source.txt')}"
                    target_content = f"目标文件内容: {files[1].get('name', 'target.txt')}"
                else:
                    # files是字符串数组
                    source_content = f"参考文件内容: {files[0]}"
                    target_content = f"目标文件内容: {files[1]}"
        
        if not source_content or not target_content:
            return jsonify({'success': False, 'error': '缺少必要参数：需要source_content和target_content，或者包含两个文件的files数组'}), 400
        
        # 模拟格式对齐结果
        result = {
            'aligned_content': f"对齐后的内容: {source_content[:50]}...",
            'alignment_score': 0.85,
            'suggestions': ['建议优化格式结构', '增加段落分隔'],
            'source_length': len(source_content),
            'target_length': len(target_content),
            'session_id': data.get('session_id', ''),
            'status': 'completed'
        }
        
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/writing-style/analyze', methods=['POST'])
def analyze_writing_style():
    try:
        data = request.get_json()
        template_content = data.get('template_content', '')
        fill_data = data.get('data', {})
        
        if not template_content:
            return jsonify({'success': False, 'error': '缺少模板内容'}), 400
        
        # 模拟文档填写结果
        result = {
            'filled_content': f"填写后的内容: {template_content[:50]}...",
            'fill_status': 'completed',
            'filled_fields': len(fill_data)
        }
        
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/document/parse', methods=['POST'])
def document_parse():
    try:
        return jsonify({
            'success': True,
            'history': document_history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documents/history/<record_id>/reapply', methods=['POST'])
def reapply_document_operation(record_id):
    return jsonify({
        'success': True,
        'config': {
            'version': '1.0.0',
            'features': ['format_alignment', 'writing_style', 'document_fill'],
            'max_file_size': '16MB'
        }
    })

@app.route('/api/models')
def get_models():
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'templates': format_templates
        })
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '请求数据为空'}), 400
            
            name = data.get('name', '')
            content = data.get('content', '')
            template_type = data.get('type', 'custom')
            
            if not name:
                return jsonify({'success': False, 'error': '模板名称不能为空'}), 400
            
            # 创建新模板
            new_template = {
                'id': f"template_{len(format_templates) + 1}",
                'name': name,
                'description': f'{template_type}格式模板',
                'type': template_type,
                'created_at': datetime.now().isoformat()
            }
            
            format_templates.append(new_template)
            
            return jsonify({
                'success': True,
                'template': new_template,
                'message': '格式模板保存成功'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/writing-style/templates')
def get_writing_style_templates():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400
        
        name = data.get('name', '')
        content = data.get('content', '')
        
        if not name:
            return jsonify({'success': False, 'error': '模板名称不能为空'}), 400
        
        # 创建新模板
        new_template = {
            'id': f"style_{len(writing_style_templates) + 1}",
            'name': name,
            'description': '自定义文风模板',
            'created_at': datetime.now().isoformat()
        }
        
        writing_style_templates.append(new_template)
        
        return jsonify({
            'success': True,
            'template': new_template,
            'message': '文风模板保存成功'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/style-alignment/preview', methods=['POST'])
def style_alignment_preview():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400
        
        document = data.get('document', '')
        standard = data.get('standard', '')
        requirements = data.get('requirements', '')
        
        if not document:
            return jsonify({'success': False, 'error': '缺少文档内容'}), 400
        
        # 模拟文档审查结果
        result = {
            'review_status': 'completed',
            'issues_found': 3,
            'suggestions': ['语法错误修正', '格式优化建议', '内容完整性检查'],
            'score': 85,
            'review_summary': f"文档审查完成，发现{3}个问题，总体评分85分"
        }
        
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 智能填报模块 ====================

@app.route('/smart-fill-demo')
def smart_fill_demo():
    """智能填报演示页面"""
    return render_template('smart_fill_demo.html')

# ==================== 智能填报模块 API端点 ====================

@app.route('/api/smart-fill/generate-summary', methods=['POST'])
def generate_summary():
    """生成年度总结"""
    try:
        if not SPARK_X1_AVAILABLE:
            return jsonify({
                'success': False,
                'error': '星火X1客户端不可用，请检查配置'
            }), 500

        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数：content'
            }), 400

        work_content = data['content']
        api_password = data.get('api_password') or "NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh"

        # 创建星火X1客户端
        client = SparkX1Client(api_password=api_password)

        # 生成年度总结
        result = client.generate_summary(work_content)

        if result['success']:
            return jsonify({
                'success': True,
                'message': '年度总结生成成功',
                'content': result['content'],
                'filename': result['filename'],
                'file_path': result['file_path'],
                'usage': result.get('usage', {}),
                'data': {
                    'content': result['content'],
                    'filename': result['filename'],
                    'file_path': result['file_path'],
                    'usage': result.get('usage', {})
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'生成年度总结失败: {str(e)}'
        }), 500

@app.route('/api/smart-fill/generate-resume', methods=['POST'])
def generate_resume():
    """生成个人简历"""
    try:
        if not SPARK_X1_AVAILABLE:
            return jsonify({
                'success': False,
                'error': '星火X1客户端不可用，请检查配置'
            }), 500

        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数：content'
            }), 400

        personal_info = data['content']
        api_password = data.get('api_password') or "NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh"

        # 创建星火X1客户端
        client = SparkX1Client(api_password=api_password)

        # 生成简历
        result = client.generate_resume(personal_info)

        if result['success']:
            return jsonify({
                'success': True,
                'message': '简历生成成功',
                'resume_data': result['data'],
                'filename': result['filename'],
                'file_path': result['file_path'],
                'usage': result.get('usage', {}),
                'data': {
                    'resume_data': result['data'],
                    'filename': result['filename'],
                    'file_path': result['file_path'],
                    'usage': result.get('usage', {})
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'生成简历失败: {str(e)}'
        }), 500

@app.route('/api/smart-fill/download/<path:filename>')
def download_file(filename):
    """下载生成的文件"""
    try:
        import tempfile
        import urllib.parse

        # URL解码文件名
        decoded_filename = urllib.parse.unquote(filename)

        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, decoded_filename)

        print(f"尝试下载文件: {decoded_filename}")
        print(f"文件路径: {file_path}")
        print(f"文件是否存在: {os.path.exists(file_path)}")

        # 如果文件不存在，尝试查找类似的文件
        if not os.path.exists(file_path):
            # 列出临时目录中的所有文件
            temp_files = []
            try:
                temp_files = os.listdir(temp_dir)
                print(f"临时目录中的文件: {temp_files}")

                # 查找包含关键词的文件
                if '年度工作总结' in decoded_filename:
                    matching_files = [f for f in temp_files if '年度工作总结' in f and f.endswith('.docx')]
                elif '个人简历' in decoded_filename:
                    matching_files = [f for f in temp_files if '个人简历' in f and f.endswith('.docx')]
                else:
                    matching_files = [f for f in temp_files if decoded_filename in f]

                if matching_files:
                    # 使用最新的文件
                    matching_files.sort(reverse=True)
                    actual_filename = matching_files[0]
                    file_path = os.path.join(temp_dir, actual_filename)
                    print(f"找到匹配文件: {actual_filename}")
                else:
                    print(f"未找到匹配文件，搜索关键词: {decoded_filename}")
            except Exception as e:
                print(f"列出临时目录文件失败: {e}")

        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': f'文件不存在: {decoded_filename}',
                'debug_info': {
                    'temp_dir': temp_dir,
                    'requested_file': decoded_filename,
                    'file_path': file_path,
                    'temp_files': temp_files[:10] if 'temp_files' in locals() else []
                }
            }), 404

        return send_from_directory(
            temp_dir,
            os.path.basename(file_path),
            as_attachment=True,
            download_name=decoded_filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'文件下载失败: {str(e)}'
        }), 500

@app.route('/api/smart-fill/status')
def smart_fill_status():
    """智能填报模块状态检查"""
    try:
        if integrated_manager:
            # 使用简化管理器获取状态
            status = integrated_manager.get_status()
        else:
            # 备用状态信息
            status = {
                'spark_x1_available': SPARK_X1_AVAILABLE,
                'core_components_available': False,
                'supported_types': ['summary', 'resume'],
                'supported_functions': ['generate_summary', 'generate_resume'],
                'integration_mode': 'simplified_spark_x1_only',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            }

            if SPARK_X1_AVAILABLE:
                # 测试API连接
                try:
                    client = SparkX1Client(api_password="NJFASGuFsRYYjeyLpZFk:jhjQJHHgIeoKVzbAORPh")
                    api_status = client.is_available()
                    status['api_connection'] = 'connected' if api_status else 'disconnected'
                except Exception as e:
                    status['api_connection'] = f'error: {str(e)}'

        return jsonify({
            'success': True,
            'data': status
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'状态检查失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
