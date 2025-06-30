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

# 模拟数据存储
document_history = []
format_templates = [
    {'id': 'template1', 'name': '标准格式', 'description': '标准文档格式模板', 'type': 'baseline'}
]
writing_style_templates = [
    {'id': 'style1', 'name': '正式文风', 'description': '正式商务文风模板'}
]

def allowed_file(filename):
    return render_template('enhanced-frontend-complete.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
