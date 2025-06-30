#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本功能测试脚本

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""

import requests
import json
import time
from datetime import datetime

def test_basic_functionality():
    """测试基本功能"""
    server_url = "http://localhost:5000"
    
    print("=" * 60)
    print("开始基本功能测试")
    print("=" * 60)
    
    # 1. 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{server_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False
    
    # 2. 测试主页访问
    print("\n2. 测试主页访问...")
    try:
        response = requests.get(f"{server_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ 主页访问通过")
            print(f"   内容长度: {len(response.text)} 字符")
        else:
            print(f"❌ 主页访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 主页访问异常: {e}")
        return False
    
    # 3. 测试API端点
    print("\n3. 测试API端点...")
    api_endpoints = [
        '/api/config',
        '/api/models',
        '/api/format-templates',
        '/api/writing-style/templates'
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(f"{server_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint} 通过")
            else:
                print(f"❌ {endpoint} 失败: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} 异常: {e}")
    
    # 4. 测试格式对齐API
    print("\n4. 测试格式对齐API...")
    try:
        test_data = {
            'source_content': '测试源文档内容',
            'target_content': '测试目标文档内容'
        }
        response = requests.post(
            f"{server_url}/api/format-alignment",
            json=test_data,
            timeout=30
        )
        if response.status_code == 200:
            print("✅ 格式对齐API通过")
            result = response.json()
            print(f"   结果: {result.get('result', {}).get('alignment_score', 'N/A')}")
        else:
            print(f"❌ 格式对齐API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 格式对齐API异常: {e}")
    
    # 5. 测试文风分析API
    print("\n5. 测试文风分析API...")
    try:
        test_data = {
            'content': '测试文档内容用于文风分析'
        }
        response = requests.post(
            f"{server_url}/api/writing-style/analyze",
            json=test_data,
            timeout=30
        )
        if response.status_code == 200:
            print("✅ 文风分析API通过")
            result = response.json()
            print(f"   文风类型: {result.get('result', {}).get('style_type', 'N/A')}")
        else:
            print(f"❌ 文风分析API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 文风分析API异常: {e}")
    
    # 6. 测试文档填写API
    print("\n6. 测试文档填写API...")
    try:
        test_data = {
            'template_content': '测试模板内容',
            'data': {'field1': 'value1', 'field2': 'value2'}
        }
        response = requests.post(
            f"{server_url}/api/document-fill/start",
            json=test_data,
            timeout=30
        )
        if response.status_code == 200:
            print("✅ 文档填写API通过")
            result = response.json()
            print(f"   填写状态: {result.get('result', {}).get('fill_status', 'N/A')}")
        else:
            print(f"❌ 文档填写API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 文档填写API异常: {e}")
    
    # 7. 测试文档解析API
    print("\n7. 测试文档解析API...")
    try:
        test_data = {
            'content': '测试文档内容用于解析分析'
        }
        response = requests.post(
            f"{server_url}/api/document/parse",
            json=test_data,
            timeout=30
        )
        if response.status_code == 200:
            print("✅ 文档解析API通过")
            result = response.json()
            print(f"   文档类型: {result.get('result', {}).get('document_type', 'N/A')}")
        else:
            print(f"❌ 文档解析API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 文档解析API异常: {e}")
    
    print("\n" + "=" * 60)
    print("基本功能测试完成")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_basic_functionality() 