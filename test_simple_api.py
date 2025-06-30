#!/usr/bin/env python3
import requests
import json

def test_format_alignment_api():
    """测试格式对齐API"""
    url = "http://127.0.0.1:5000/api/format-alignment"
    data = {
        "session_id": "test_123",
        "files": ["test1.docx", "test2.docx"]
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_health_check():
    """测试健康检查"""
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        print(f"主页状态码: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

if __name__ == "__main__":
    print("🔍 测试Web应用可用性...")
    
    # 健康检查
    if test_health_check():
        print("✅ 主页访问正常")
    else:
        print("❌ 主页访问失败")
        exit(1)
    
    # API测试
    if test_format_alignment_api():
        print("✅ 格式对齐API正常")
    else:
        print("❌ 格式对齐API失败") 