#!/usr/bin/env python3
"""
测试API Content-Type问题
"""
import requests
import json

def test_document_fill_api():
    """测试文档填充API的Content-Type处理"""
    url = 'http://localhost:5000/api/document-fill/start'
    
    # 测试数据
    data = {
        'document_content': 'This is a test document content.',
        'document_name': 'test.txt'
    }
    
    # 测试1: 正确的JSON请求
    print("=== 测试1: 正确的JSON请求 ===")
    try:
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            json=data
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试2: 使用data参数而不是json参数
    print("\n=== 测试2: 使用data参数发送JSON ===")
    try:
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试3: 错误的Content-Type
    print("\n=== 测试3: 错误的Content-Type ===")
    try:
        response = requests.post(
            url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=json.dumps(data)
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    test_document_fill_api()
