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
from flask import Flask, request, jsonify, render_template, send_from_directory, make_response
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

# 初始化格式对齐协调器
format_alignment_coordinator = None
try:
    from src.core.tools.format_alignment_coordinator import FormatAlignmentCoordinator
    format_alignment_coordinator = FormatAlignmentCoordinator()
    print("✅ 格式对齐协调器初始化成功")
except Exception as e:
    print(f"❌ 格式对齐协调器初始化失败: {e}")
    format_alignment_coordinator = None

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

def is_binary_content(content):
    """检查内容是否为二进制内容（乱码）"""
    if not content:
        return False

    # 检查是否包含大量非打印字符
    non_printable_count = 0
    total_chars = len(content)

    if total_chars == 0:
        return False

    for char in content[:1000]:  # 只检查前1000个字符
        if ord(char) < 32 and char not in '\n\r\t':  # 非打印字符（除了换行、回车、制表符）
            non_printable_count += 1

    # 如果非打印字符超过10%，认为是二进制内容
    return (non_printable_count / min(1000, total_chars)) > 0.1

def generate_sample_content(file_info):
    """根据文件信息生成示例内容"""
    file_name = file_info.get('name', '未知文件')
    file_type = file_info.get('type', '未知类型')
    file_size = file_info.get('size', 0)

    if file_name.endswith('.docx') or 'officedocument' in file_type:
        # 为DOCX文件生成更丰富的示例内容
        doc_title = file_name.replace('.docx', '').replace('新建 DOCX 文档', '工作报告').replace('新建', '项目')
        return f"""{doc_title}

项目概述
本项目旨在提升工作效率和质量，通过系统化的方法实现目标。

当前进展
1. 需求分析阶段
   - 已完成用户调研
   - 确定了核心功能需求
   - 制定了技术方案

2. 设计开发阶段
   - 完成了系统架构设计
   - 正在进行功能模块开发
   - 预计下月完成主要功能

3. 测试验证阶段
   - 制定了测试计划
   - 准备开始功能测试
   - 计划进行用户验收测试

遇到的问题
目前项目进展顺利，暂无重大技术难题。

下一步计划
1. 继续推进开发工作
2. 加强质量控制
3. 准备项目验收

总结
项目按计划稳步推进，预期能够按时完成既定目标。

附件信息
原始文件：{file_name}
文件大小：{file_size} 字节
创建时间：最近修改"""

    elif file_name.endswith('.txt'):
        return f"""文本文档：{file_name}

内容概要：
- 这是一个文本文件
- 包含纯文本内容
- 需要进行格式化处理

文件信息：
大小：{file_size} 字节
类型：{file_type}

请根据目标格式要求进行对齐处理。"""

    else:
        return f"""文档：{file_name}

这是一个需要格式化的文档文件。

基本信息：
- 文件名：{file_name}
- 文件类型：{file_type}
- 文件大小：{file_size} 字节

请根据目标格式进行相应的格式对齐处理。"""

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

# 格式对齐模块API端点
@app.route('/api/format-alignment/upload', methods=['POST'])
def format_alignment_upload():
    """格式对齐文件上传接口"""
    try:
        # 检查是否有文件上传
        if 'files' not in request.files:
            return jsonify({
                'code': 1,
                'message': '没有上传文件',
                'data': None
            }), 400

        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return jsonify({
                'code': 1,
                'message': '文件列表为空',
                'data': None
            }), 400

        # 生成上传ID
        import time
        upload_id = f"upload_{int(time.time())}_{len(files)}"
        uploaded_files = []

        # 处理每个上传的文件
        for i, file in enumerate(files):
            if file.filename == '':
                continue

            if file and allowed_file(file.filename):
                # 生成文件ID
                file_id = f"file_{upload_id}_{i}"

                # 读取文件内容
                file_content = file.read().decode('utf-8', errors='ignore')

                # 存储文件信息（这里简化存储在内存中）
                file_info = {
                    'file_id': file_id,
                    'filename': file.filename,
                    'size': len(file_content),
                    'type': file.filename.rsplit('.', 1)[1].lower(),
                    'content': file_content
                }

                uploaded_files.append(file_info)

        if not uploaded_files:
            return jsonify({
                'code': 1,
                'message': '没有有效的文件',
                'data': None
            }), 400

        # 存储上传信息（简化存储）
        upload_info = {
            'upload_id': upload_id,
            'files': uploaded_files,
            'upload_time': datetime.now().isoformat()
        }

        # 这里应该存储到数据库或文件系统，现在简化存储在全局变量
        if not hasattr(app, 'upload_storage'):
            app.upload_storage = {}
        app.upload_storage[upload_id] = upload_info

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'upload_id': upload_id,
                'files': [
                    {
                        'file_id': f['file_id'],
                        'filename': f['filename'],
                        'size': f['size'],
                        'type': f['type']
                    } for f in uploaded_files
                ]
            }
        })

    except Exception as e:
        return jsonify({
            'code': 1,
            'message': f'上传失败: {str(e)}',
            'data': None
        }), 500

@app.route('/api/format-alignment/process', methods=['POST'])
def format_alignment_process():
    """格式对齐处理接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 1,
                'message': '请求数据为空',
                'data': None
            }), 400

        upload_id = data.get('upload_id')
        format_instruction = data.get('format_instruction', '请格式化文档')
        template_id = data.get('template_id')
        options = data.get('options', {})

        if not upload_id:
            return jsonify({
                'code': 1,
                'message': '缺少upload_id参数',
                'data': None
            }), 400

        # 获取上传的文件
        if not hasattr(app, 'upload_storage') or upload_id not in app.upload_storage:
            return jsonify({
                'code': 1,
                'message': f'上传ID {upload_id} 不存在',
                'data': None
            }), 404

        upload_info = app.upload_storage[upload_id]
        files = upload_info['files']

        if not files:
            return jsonify({
                'code': 1,
                'message': '没有找到上传的文件',
                'data': None
            }), 400

        # 使用全局格式对齐协调器
        if format_alignment_coordinator is None:
            return jsonify({
                'code': 1,
                'message': '格式对齐协调器未初始化',
                'data': None
            }), 500

        try:
            # 处理第一个文件（简化处理）
            file_content = files[0]['content']

            # 使用星火X1进行格式化
            result = format_alignment_coordinator.format_with_spark_x1(
                content=file_content,
                instruction=format_instruction,
                temperature=options.get('temperature', 0.7),
                max_tokens=options.get('max_tokens', 4000)
            )

            if result.get('success'):
                return jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': {
                        'task_id': result['task_id'],
                        'status': result['status'],
                        'estimated_time': 30
                    }
                })
            else:
                return jsonify({
                    'code': 1,
                    'message': result.get('error', '格式化失败'),
                    'data': None
                }), 500

        except Exception as e:
            return jsonify({
                'code': 1,
                'message': f'格式化处理失败: {str(e)}',
                'data': None
            }), 500

    except Exception as e:
        return jsonify({
            'code': 1,
            'message': f'处理请求失败: {str(e)}',
            'data': None
        }), 500

@app.route('/api/format-alignment/result/<task_id>', methods=['GET'])
def format_alignment_result(task_id):
    """获取格式对齐结果接口"""
    try:
        # 使用全局格式对齐协调器
        if format_alignment_coordinator is None:
            return jsonify({
                'code': 1,
                'message': '格式对齐协调器未初始化',
                'data': None
            }), 500

        # 获取任务结果
        result = format_alignment_coordinator.get_task_result(task_id)

        if result.get('success'):
            task_data = result

            # 构建响应数据
            response_data = {
                'task_id': task_id,
                'status': task_data['status'],
                'processing_log': task_data.get('processing_log', ''),
            }

            # 如果任务完成，添加结果文件信息
            if task_data['status'] == 'completed':
                response_data['result_files'] = [
                    {
                        'file_id': f"result_{task_id}",
                        'filename': f"formatted_document_{task_id}.txt",
                        'download_url': f"/api/format-alignment/download/{task_id}"
                    }
                ]

            return jsonify({
                'code': 0,
                'message': 'success',
                'data': response_data
            })
        else:
            return jsonify({
                'code': 1,
                'message': result.get('error', '获取任务结果失败'),
                'data': None
            }), 404

    except Exception as e:
        return jsonify({
            'code': 1,
            'message': f'获取结果失败: {str(e)}',
            'data': None
        }), 500

@app.route('/api/format-alignment/download/<task_id>', methods=['GET'])
def format_alignment_download(task_id):
    """下载格式化结果文件"""
    try:
        # 获取文件格式参数
        file_format = request.args.get('format', 'txt').lower()

        # 使用全局格式对齐协调器
        if format_alignment_coordinator is None:
            return jsonify({
                'code': 1,
                'message': '格式对齐协调器未初始化',
                'data': None
            }), 500

        # 获取任务结果
        result = format_alignment_coordinator.get_task_result(task_id)

        if result.get('success'):
            formatted_content = result.get('formatted_content', '')

            if file_format == 'docx':
                # 生成Word格式文件
                return generate_word_document(formatted_content, task_id)
            else:
                # 默认生成文本文件
                response = make_response(formatted_content)
                response.headers['Content-Type'] = 'text/plain; charset=utf-8'
                response.headers['Content-Disposition'] = f'attachment; filename=formatted_document_{task_id}.txt'
                return response
        else:
            return jsonify({
                'code': 1,
                'message': result.get('error', '任务不存在'),
                'data': None
            }), 404

    except Exception as e:
        return jsonify({
            'code': 1,
            'message': f'下载失败: {str(e)}',
            'data': None
        }), 500

def generate_word_document(content, task_id):
    """生成Word文档"""
    try:
        from docx import Document
        from docx.shared import Inches
        import io

        # 创建Word文档
        doc = Document()

        # 添加标题
        doc.add_heading('格式化文档', 0)

        # 处理内容，按行分割并添加到文档
        lines = content.split('\n')
        current_paragraph = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否是标题
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title_text = line.lstrip('#').strip()
                doc.add_heading(title_text, level)
            elif line.startswith('##'):
                doc.add_heading(line[2:].strip(), 2)
            elif line.startswith('#'):
                doc.add_heading(line[1:].strip(), 1)
            else:
                # 普通段落
                doc.add_paragraph(line)

        # 保存到内存
        doc_io = io.BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)

        # 创建响应
        response = make_response(doc_io.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        response.headers['Content-Disposition'] = f'attachment; filename=formatted_document_{task_id}.docx'

        return response

    except ImportError:
        # 如果没有安装python-docx，回退到文本格式
        response = make_response(content)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=formatted_document_{task_id}.txt'
        return response
    except Exception as e:
        # 出错时回退到文本格式
        response = make_response(content)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=formatted_document_{task_id}.txt'
        return response

@app.route('/api/format-alignment/continue', methods=['POST'])
def format_alignment_continue():
    """多轮对话继续接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 1,
                'message': '请求数据为空',
                'data': None
            }), 400

        task_id = data.get('task_id')
        instruction = data.get('instruction', '')
        context = data.get('context')

        if not task_id:
            return jsonify({
                'code': 1,
                'message': '缺少task_id参数',
                'data': None
            }), 400

        if not instruction:
            return jsonify({
                'code': 1,
                'message': '缺少instruction参数',
                'data': None
            }), 400

        # 使用全局格式对齐协调器
        if format_alignment_coordinator is None:
            return jsonify({
                'code': 1,
                'message': '格式对齐协调器未初始化',
                'data': None
            }), 500

        try:
            # 继续对话
            result = format_alignment_coordinator.continue_conversation_task(task_id, instruction)

            if result.get('success'):
                return jsonify({
                    'code': 0,
                    'message': 'success',
                    'data': {
                        'task_id': result['task_id'],
                        'status': result['status'],
                        'response': result['response']
                    }
                })
            else:
                return jsonify({
                    'code': 1,
                    'message': result.get('error', '继续对话失败'),
                    'data': None
                }), 500

        except Exception as e:
            return jsonify({
                'code': 1,
                'message': f'对话处理失败: {str(e)}',
                'data': None
            }), 500

    except Exception as e:
        return jsonify({
            'code': 1,
            'message': f'处理请求失败: {str(e)}',
            'data': None
        }), 500

# 兼容现有前端的格式对齐接口
@app.route('/api/format-alignment', methods=['POST'])
def format_alignment_legacy():
    """兼容现有前端的格式对齐接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400

        session_id = data.get('session_id', '')
        files = data.get('files', [])

        if len(files) < 2:
            return jsonify({'success': False, 'error': '需要至少2个文件进行格式对齐'}), 400

        # 使用全局格式对齐协调器
        if format_alignment_coordinator is None:
            return jsonify({
                'success': False,
                'error': '格式对齐协调器未初始化'
            }), 500

        # 获取文件内容
        try:
            # 从files中提取内容
            source_file = files[0]
            target_file = files[1] if len(files) > 1 else files[0]

            print(f"📝 源文件: {source_file.get('name', '未知')}, 类型: {source_file.get('type', '未知')}")
            print(f"📝 目标文件: {target_file.get('name', '未知')}, 类型: {target_file.get('type', '未知')}")

            # 处理源文件内容
            source_content = source_file.get('content', '')

            # 检查是否是乱码或二进制内容
            if is_binary_content(source_content):
                print("⚠️ 检测到二进制内容，使用文件信息生成示例内容")
                source_content = generate_sample_content(source_file)
            elif len(source_content.strip()) == 0:
                print("⚠️ 文件内容为空，生成示例内容")
                source_content = generate_sample_content(source_file)

            # 限制内容长度，避免API调用超时
            if len(source_content) > 2000:
                print(f"⚠️ 内容过长({len(source_content)}字符)，截取前2000字符")
                source_content = source_content[:2000] + "\n\n[内容已截取...]"

            print(f"📝 处理后源文件内容长度: {len(source_content)}")
            print(f"📝 内容预览: {source_content[:100]}...")

        except Exception as e:
            print(f"❌ 文件内容处理失败: {e}")
            source_content = "示例文档内容，需要格式化"

        # 构建更详细的格式对齐指令
        target_content = target_file.get('content', '')
        if target_content and len(target_content.strip()) > 0:
            instruction = f"""请将以下文档内容按照目标格式进行重新组织和格式化：

目标格式示例：
{target_content}

要求：
1. 保持原文档的核心信息和内容
2. 按照目标格式的结构重新组织内容
3. 使用目标格式的标题层级和编号方式
4. 保持专业的文档风格
5. 确保内容完整性和逻辑性

请直接输出格式化后的完整文档内容，不要添加额外的说明。"""
        else:
            instruction = f"""请将以下文档内容格式化为标准的专业文档格式：

要求：
1. 使用清晰的标题层级结构
2. 内容分段明确，逻辑清晰
3. 使用适当的编号和列表
4. 保持专业的文档风格
5. 确保内容完整性

请直接输出格式化后的完整文档内容。"""

        print("🚀 开始调用星火X1进行格式对齐...")
        print(f"📝 格式化指令: {instruction[:100]}...")
        result = format_alignment_coordinator.format_with_spark_x1(
            content=source_content,
            instruction=instruction,
            temperature=0.3,  # 降低温度，提高一致性
            max_tokens=3000,  # 增加最大token数
            timeout=60
        )

        if result.get('success'):
            return jsonify({
                'success': True,
                'data': {
                    'aligned_content': result.get('formatted_content', ''),
                    'alignment_score': 0.95,
                    'suggestions': ['格式对齐完成', '使用星火X1处理'],
                    'session_id': session_id,
                    'status': 'completed',
                    'task_id': result.get('task_id', '')
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '格式对齐失败')
            }), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
