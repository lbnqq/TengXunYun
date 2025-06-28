#!/usr/bin/env python3
"""
简化的测试服务器
用于端到端测试，避免复杂依赖问题
"""

import sys
import os
import time
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import List, Dict, Any

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)
CORS(app)

def fill_tables(tables: List[pd.DataFrame], fill_data: List[Dict[str, Any]]) -> List[pd.DataFrame]:
    """
    智能表格填充逻辑
    """
    filled_tables = []
    for df in tables:
        if not isinstance(df, pd.DataFrame) or df.empty:
            filled_tables.append(df)
            continue

        # 创建一个新的DataFrame副本以避免修改原始数据
        df_copy = df.copy()

        # 智能匹配填充：根据表格列名匹配相应的填充数据
        table_columns = set(df_copy.columns)

        # 找到与当前表格列匹配的填充数据
        matching_fill_data = []
        for row in fill_data:
            row_columns = set(row.keys())
            # 如果填充数据的列与表格列有交集，则认为是匹配的
            if table_columns.intersection(row_columns):
                matching_fill_data.append(row)

        # 按行填充匹配的数据
        for i, row in enumerate(matching_fill_data):
            if i < len(df_copy):  # 只填充现有行
                for col in df_copy.columns:
                    if col in row and row[col] is not None:
                        df_copy.at[i, col] = row[col]

        filled_tables.append(df_copy)
    return filled_tables

@app.route('/')
def index():
    """主页"""
    return jsonify({
        'status': 'ok',
        'message': '测试服务器运行正常',
        'version': '1.0.0'
    })

@app.route('/api/table-fill', methods=['POST'])
def api_table_fill():
    """
    智能表格批量填充API（增强错误处理）
    """
    try:
        # 检查Content-Type
        if not request.is_json:
            return jsonify({'success': False, 'error': '请求必须是JSON格式'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

        # 严格验证必需字段
        if 'tables' not in data:
            return jsonify({'success': False, 'error': '缺少必需字段: tables'}), 400

        if 'fill_data' not in data:
            return jsonify({'success': False, 'error': '缺少必需字段: fill_data'}), 400

        tables = data['tables']
        fill_data = data['fill_data']

        # 严格类型检查
        if not isinstance(tables, list):
            return jsonify({'success': False, 'error': 'tables必须是数组'}), 400

        if not isinstance(fill_data, list):
            return jsonify({'success': False, 'error': 'fill_data必须是数组'}), 400

        # 检查空数组情况
        if len(tables) == 0:
            return jsonify({'success': True, 'filled_tables': []})

        # 验证每个表格的结构
        pd_tables = []
        for i, t in enumerate(tables):
            if not isinstance(t, dict):
                return jsonify({'success': False, 'error': f'表格{i+1}必须是对象'}), 400

            if 'columns' not in t:
                return jsonify({'success': False, 'error': f'表格{i+1}缺少columns字段'}), 400

            if 'data' not in t:
                return jsonify({'success': False, 'error': f'表格{i+1}缺少data字段'}), 400

            if not isinstance(t['columns'], list):
                return jsonify({'success': False, 'error': f'表格{i+1}的columns必须是数组'}), 400

            if not isinstance(t['data'], list):
                return jsonify({'success': False, 'error': f'表格{i+1}的data必须是数组'}), 400

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
        filled_tables = fill_tables(pd_tables, fill_data)

        # 返回json格式
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
    """
    文件上传API（增强版）
    """
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
                'error': f'不支持的文件类型: {file_ext}。支持的类型: {", ".join(allowed_extensions)}'
            }), 400

        # 读取文件内容
        content = file.read()

        # 根据文件类型处理
        if file_ext == 'txt':
            try:
                text_content = content.decode('utf-8', errors='ignore')
            except:
                text_content = content.decode('gbk', errors='ignore')
        else:
            # 对于其他文件类型，模拟处理
            text_content = f"模拟处理 {file_ext} 文件内容"

        # 模拟文档解析结果
        parsed_result = {
            'text': text_content,
            'tables': [
                {
                    'columns': ['姓名', '年龄', '职位'],
                    'data': [['张三', '', ''], ['李四', '', '']]
                }
            ],
            'metadata': {
                'filename': file.filename,
                'size': len(content),
                'type': file_ext,
                'pages': 1 if file_ext == 'txt' else 2
            }
        }

        return jsonify({
            'success': True,
            'message': '文件上传并解析成功',
            'filename': file.filename,
            'size': len(content),
            'type': file_ext,
            'parsed_result': parsed_result,
            'content_preview': text_content[:200] + '...' if len(text_content) > 200 else text_content
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'文件上传失败: {str(e)}'}), 500

@app.route('/api/document/fill', methods=['POST'])
def api_document_fill():
    """文档智能填充API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

        document_id = data.get('document_id')
        fill_data = data.get('fill_data', [])

        if not document_id:
            return jsonify({'success': False, 'error': '缺少document_id'}), 400

        # 模拟智能填充处理
        filled_content = f"已填充的文档内容 (ID: {document_id})\n"
        for item in fill_data:
            filled_content += f"- {item}\n"

        return jsonify({
            'success': True,
            'document_id': document_id,
            'filled_content': filled_content,
            'status': 'completed'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'文档填充失败: {str(e)}'}), 500

@app.route('/api/style/analyze', methods=['POST'])
def api_style_analyze():
    """文风分析API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

        text = data.get('text', '')
        if not text:
            return jsonify({'success': False, 'error': '缺少文本内容'}), 400

        # 模拟文风分析
        style_features = {
            'formality': 0.8,
            'complexity': 0.6,
            'tone': 'professional',
            'length_avg': len(text.split()) / max(text.count('.'), 1),
            'vocabulary_richness': 0.7
        }

        return jsonify({
            'success': True,
            'style_features': style_features,
            'style_type': 'formal_business',
            'confidence': 0.85
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'文风分析失败: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': pd.Timestamp.now().isoformat(),
        'services': {
            'document_parser': 'active',
            'table_filler': 'active',
            'style_analyzer': 'active'
        }
    })

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
    
    print(f"🚀 启动测试服务器: http://{host}:{port}")
    print(f"📋 可用端点:")
    print(f"   GET  /           - 主页")
    print(f"   POST /api/table-fill - 表格填充")
    print(f"   POST /api/upload     - 文件上传")
    print(f"   GET  /health         - 健康检查")
    
    app.run(host=host, port=port, debug=debug)
