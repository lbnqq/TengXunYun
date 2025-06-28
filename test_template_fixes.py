#!/usr/bin/env python3
"""
模板保存修复验证测试脚本
测试统一参数接口、模板格式标准化和错误处理增强功能
"""

import json
import requests
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.tools.template_schema import TemplateSchema
from src.core.tools.error_handler import error_handler

def test_template_schema():
    """测试模板Schema功能"""
    print("🔍 测试模板Schema功能...")
    
    # 测试格式模板验证
    format_template = {
        "template_id": "1234567890abcdef1234567890abcdef",
        "document_name": "测试格式模板",
        "structure_analysis": {
            "total_lines": 10,
            "headings": [],
            "paragraphs": [],
            "lists": [],
            "special_elements": [],
            "estimated_format": {},
            "analysis_confidence": 0.8
        },
        "format_rules": {
            "heading_formats": {},
            "paragraph_formats": {},
            "list_formats": {},
            "font_settings": {},
            "spacing_settings": {}
        },
        "format_prompt": "这是一个测试格式提示词"
    }
    
    validation_result = TemplateSchema.validate_format_template(format_template)
    print(f"✅ 格式模板验证结果: {validation_result['success']}")
    
    # 测试文风模板验证
    style_template = {
        "template_id": "abcdef1234567890abcdef1234567890",
        "document_name": "测试文风模板",
        "style_features": {
            "sentence_structure": {},
            "vocabulary_choice": {},
            "expression_style": {},
            "text_organization": {},
            "language_habits": {}
        },
        "style_type": "business_professional",
        "style_prompt": "这是一个测试文风提示词"
    }
    
    validation_result = TemplateSchema.validate_style_template(style_template)
    print(f"✅ 文风模板验证结果: {validation_result['success']}")
    
    # 测试模板标准化
    normalized_format = TemplateSchema.normalize_format_template({
        "document_name": "测试标准化"
    })
    print(f"✅ 格式模板标准化: {normalized_format['template_id']}")
    
    normalized_style = TemplateSchema.normalize_style_template({
        "document_name": "测试标准化"
    })
    print(f"✅ 文风模板标准化: {normalized_style['template_id']}")

def test_error_handler():
    """测试错误处理功能"""
    print("\n🔍 测试错误处理功能...")
    
    # 测试验证错误
    try:
        raise ValueError("缺少必需字段: template_id")
    except Exception as e:
        result = error_handler.handle_error(e, {"context": "template_validation"})
        print(f"✅ 验证错误处理: {result['category']}")
    
    # 测试API错误
    try:
        raise requests.RequestException("API调用失败")
    except Exception as e:
        result = error_handler.handle_error(e, {"context": "api_call"})
        print(f"✅ API错误处理: {result['category']}")
    
    # 测试文件IO错误
    try:
        raise FileNotFoundError("模板文件不存在")
    except Exception as e:
        result = error_handler.handle_error(e, {"context": "file_operation"})
        print(f"✅ 文件IO错误处理: {result['category']}")

def test_api_endpoints():
    """测试API端点"""
    print("\n🔍 测试API端点...")
    
    base_url = "http://localhost:5000"
    
    # 测试格式模板保存 - 格式1
    format_data_1 = {
        "template_name": "测试格式模板1",
        "template_data": {
            "document_name": "测试格式模板1",
            "structure_analysis": {
                "total_lines": 10,
                "headings": [],
                "paragraphs": [],
                "lists": [],
                "special_elements": [],
                "estimated_format": {},
                "analysis_confidence": 0.8
            },
            "format_rules": {
                "heading_formats": {},
                "paragraph_formats": {},
                "list_formats": {},
                "font_settings": {},
                "spacing_settings": {}
            },
            "format_prompt": "测试格式提示词"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/format-templates", json=format_data_1)
        print(f"✅ 格式模板保存(格式1): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   模板ID: {result.get('template_id', 'N/A')}")
    except Exception as e:
        print(f"❌ 格式模板保存(格式1)失败: {e}")
    
    # 测试格式模板保存 - 格式2
    format_data_2 = {
        "template_id": "1234567890abcdef1234567890abcdef",
        "document_name": "测试格式模板2",
        "structure_analysis": {
            "total_lines": 10,
            "headings": [],
            "paragraphs": [],
            "lists": [],
            "special_elements": [],
            "estimated_format": {},
            "analysis_confidence": 0.8
        },
        "format_rules": {
            "heading_formats": {},
            "paragraph_formats": {},
            "list_formats": {},
            "font_settings": {},
            "spacing_settings": {}
        },
        "format_prompt": "测试格式提示词"
    }
    
    try:
        response = requests.post(f"{base_url}/api/format-templates", json=format_data_2)
        print(f"✅ 格式模板保存(格式2): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   模板ID: {result.get('template_id', 'N/A')}")
    except Exception as e:
        print(f"❌ 格式模板保存(格式2)失败: {e}")
    
    # 测试文风模板保存 - 格式1
    style_data_1 = {
        "reference_content": "这是一个测试文档，用于验证文风分析功能。",
        "reference_name": "测试文风文档"
    }
    
    try:
        response = requests.post(f"{base_url}/api/writing-style/save-template", json=style_data_1)
        print(f"✅ 文风模板保存(格式1): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   模板ID: {result.get('template_id', 'N/A')}")
    except Exception as e:
        print(f"❌ 文风模板保存(格式1)失败: {e}")
    
    # 测试文风模板保存 - 格式2
    style_data_2 = {
        "template_id": "abcdef1234567890abcdef1234567890",
        "document_name": "测试文风模板2",
        "style_features": {
            "sentence_structure": {},
            "vocabulary_choice": {},
            "expression_style": {},
            "text_organization": {},
            "language_habits": {}
        },
        "style_type": "business_professional",
        "style_prompt": "测试文风提示词"
    }
    
    try:
        response = requests.post(f"{base_url}/api/writing-style/save-template", json=style_data_2)
        print(f"✅ 文风模板保存(格式2): {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   模板ID: {result.get('template_id', 'N/A')}")
    except Exception as e:
        print(f"❌ 文风模板保存(格式2)失败: {e}")

def test_error_scenarios():
    """测试错误场景"""
    print("\n🔍 测试错误场景...")
    
    base_url = "http://localhost:5000"
    
    # 测试无效数据
    invalid_data = {
        "invalid_field": "invalid_value"
    }
    
    try:
        response = requests.post(f"{base_url}/api/format-templates", json=invalid_data)
        print(f"✅ 无效数据测试: {response.status_code}")
        if response.status_code != 200:
            result = response.json()
            print(f"   错误信息: {result.get('error', 'N/A')}")
    except Exception as e:
        print(f"❌ 无效数据测试失败: {e}")
    
    # 测试空数据
    try:
        response = requests.post(f"{base_url}/api/writing-style/save-template", json={})
        print(f"✅ 空数据测试: {response.status_code}")
        if response.status_code != 200:
            result = response.json()
            print(f"   错误信息: {result.get('error', 'N/A')}")
    except Exception as e:
        print(f"❌ 空数据测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始模板保存修复验证测试")
    print("=" * 50)
    
    # 测试模板Schema
    test_template_schema()
    
    # 测试错误处理
    test_error_handler()
    
    # 测试API端点
    test_api_endpoints()
    
    # 测试错误场景
    test_error_scenarios()
    
    print("\n" + "=" * 50)
    print("✅ 模板保存修复验证测试完成")

if __name__ == "__main__":
    main() 