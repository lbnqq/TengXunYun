#!/usr/bin/env python3
"""
测试Xingcheng API的认证和调用方式
Diagnose Xingcheng API authentication and calling methods
"""

import os
import sys
import json
import requests
import time
import hashlib
import hmac
import base64
from urllib.parse import urlencode

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_bearer_token_auth():
    """测试Bearer Token认证方式（当前使用的方式）"""
    print("🔑 测试Bearer Token认证方式")
    print("-" * 50)
    
    api_key = os.getenv('XINGCHENG_API_KEY')
    if not api_key:
        print("❌ 未找到XINGCHENG_API_KEY环境变量")
        return False
    
    print(f"API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else api_key}")
    
    url = "https://spark-api-open.xf-yun.com/v2/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "x1",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        print(f"🌐 发送请求到: {url}")
        print(f"📋 请求头: {headers}")
        print(f"📦 请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        print(f"📝 响应内容: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Bearer Token认证成功")
            return True
        else:
            print(f"❌ Bearer Token认证失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_api_key_secret_auth():
    """测试API Key + Secret认证方式（科大讯飞常用方式）"""
    print("\n🔐 测试API Key + Secret认证方式")
    print("-" * 50)
    
    api_key = os.getenv('XINGCHENG_API_KEY')
    api_secret = os.getenv('XINGCHENG_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ 未找到XINGCHENG_API_KEY或XINGCHENG_API_SECRET环境变量")
        return False
    
    print(f"API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else api_key}")
    print(f"API Secret: {api_secret[:10]}...{api_secret[-10:] if len(api_secret) > 20 else api_secret}")
    
    # 尝试生成签名（科大讯飞常用的HMAC-SHA256签名）
    timestamp = str(int(time.time()))
    nonce = "test_nonce_123"
    
    # 构建签名字符串
    sign_string = f"api_key={api_key}&timestamp={timestamp}&nonce={nonce}"
    signature = hmac.new(
        api_secret.encode('utf-8'),
        sign_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    url = "https://spark-api-open.xf-yun.com/v2/chat/completions"
    
    # 方式1: 在Header中传递认证信息
    headers_v1 = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
        "X-API-Secret": api_secret,
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": signature
    }
    
    # 方式2: 使用Authorization header
    auth_string = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()
    headers_v2 = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_string}"
    }
    
    # 方式3: 使用自定义Authorization
    headers_v3 = {
        "Content-Type": "application/json",
        "Authorization": f"XFYUN {api_key}:{signature}"
    }
    
    payload = {
        "model": "x1",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    # 测试不同的认证方式
    auth_methods = [
        ("自定义Header", headers_v1),
        ("Basic Auth", headers_v2),
        ("XFYUN Auth", headers_v3)
    ]
    
    for method_name, headers in auth_methods:
        try:
            print(f"\n🧪 测试{method_name}认证...")
            print(f"📋 请求头: {headers}")
            
            response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
            
            print(f"📊 响应状态码: {response.status_code}")
            print(f"📝 响应内容: {response.text[:200]}...")
            
            if response.status_code == 200:
                print(f"✅ {method_name}认证成功")
                return True
            else:
                print(f"❌ {method_name}认证失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {method_name}请求异常: {e}")
    
    return False

def test_different_endpoints():
    """测试不同的API端点"""
    print("\n🌐 测试不同的API端点")
    print("-" * 50)
    
    api_key = os.getenv('XINGCHENG_API_KEY')
    if not api_key:
        print("❌ 未找到XINGCHENG_API_KEY环境变量")
        return False
    
    # 可能的API端点
    endpoints = [
        "https://spark-api-open.xf-yun.com/v2/chat/completions",
        "https://spark-api-open.xf-yun.com/v1/chat/completions",
        "https://spark-api.xf-yun.com/v2/chat/completions",
        "https://spark-api.xf-yun.com/v1/chat/completions",
        "https://api.xf-yun.com/v2/chat/completions",
        "https://api.xf-yun.com/v1/chat/completions"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "x1",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    for endpoint in endpoints:
        try:
            print(f"\n🔗 测试端点: {endpoint}")
            
            response = requests.post(endpoint, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
            
            print(f"📊 状态码: {response.status_code}")
            if response.status_code != 404:  # 只显示非404的响应
                print(f"📝 响应: {response.text[:200]}...")
            
            if response.status_code == 200:
                print(f"✅ 端点 {endpoint} 可用")
                return True
                
        except requests.exceptions.Timeout:
            print("⏰ 请求超时")
        except requests.exceptions.ConnectionError:
            print("🔌 连接错误")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    return False

def test_minimal_request():
    """测试最简化的请求"""
    print("\n🎯 测试最简化的请求")
    print("-" * 50)
    
    api_key = os.getenv('XINGCHENG_API_KEY')
    if not api_key:
        print("❌ 未找到XINGCHENG_API_KEY环境变量")
        return False
    
    url = "https://spark-api-open.xf-yun.com/v2/chat/completions"
    
    # 最简化的请求
    minimal_payload = {
        "model": "x1",
        "messages": [{"role": "user", "content": "hi"}]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📦 最简请求: {json.dumps(minimal_payload)}")
        
        response = requests.post(url, json=minimal_payload, headers={'Content-Type': 'application/json'}, timeout=30)
        
        print(f"📊 状态码: {response.status_code}")
        print(f"📝 完整响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 最简请求成功")
            return True
        else:
            print(f"❌ 最简请求失败")
            # 尝试解析错误信息
            try:
                error_data = response.json()
                print(f"🔍 错误详情: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始Xingcheng API诊断测试")
    print("=" * 60)
    
    # 检查环境变量
    api_key = os.getenv('XINGCHENG_API_KEY')
    api_secret = os.getenv('XINGCHENG_API_SECRET')
    
    print(f"🔍 环境变量检查:")
    print(f"  - XINGCHENG_API_KEY: {'✅ 已设置' if api_key else '❌ 未设置'}")
    print(f"  - XINGCHENG_API_SECRET: {'✅ 已设置' if api_secret else '❌ 未设置'}")
    
    if not api_key:
        print("\n❌ 请设置XINGCHENG_API_KEY环境变量")
        return False
    
    tests = [
        ("Bearer Token认证", test_bearer_token_auth),
        ("API Key + Secret认证", test_api_key_secret_auth),
        ("不同API端点", test_different_endpoints),
        ("最简化请求", test_minimal_request)
    ]
    
    success_count = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                success_count += 1
                print(f"\n✅ {test_name} 测试成功")
                break  # 找到一个成功的方法就停止
            else:
                print(f"\n❌ {test_name} 测试失败")
        except Exception as e:
            print(f"\n💥 {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 60)
    if success_count > 0:
        print("🎉 找到了可用的认证方式！")
        return True
    else:
        print("😞 所有认证方式都失败了，请检查API密钥或联系服务提供商")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
