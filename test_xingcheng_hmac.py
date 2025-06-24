#!/usr/bin/env python3
"""
使用HMAC签名认证测试Xingcheng API
Test Xingcheng API with HMAC signature authentication
"""

import requests
import json
import time
import hashlib
import hmac
import base64
from urllib.parse import urlparse, urlencode
from datetime import datetime

def generate_hmac_signature(api_key, api_secret, method, url, headers, body):
    """生成HMAC签名"""
    
    # 解析URL
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    path = parsed_url.path
    
    # 构建签名字符串
    # 通常格式为: METHOD\nHOST\nPATH\nTIMESTAMP\nBODY_HASH
    timestamp = str(int(time.time()))
    
    # 计算body的hash
    body_str = json.dumps(body, separators=(',', ':')) if isinstance(body, dict) else str(body)
    body_hash = hashlib.sha256(body_str.encode('utf-8')).hexdigest()
    
    # 构建签名字符串
    string_to_sign = f"{method}\n{host}\n{path}\n{timestamp}\n{body_hash}"
    
    # 生成HMAC签名
    signature = hmac.new(
        api_secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature, timestamp

def test_hmac_auth_v1():
    """测试HMAC认证方式1"""
    print("🔐 测试HMAC认证方式1")
    print("-" * 40)
    
    api_key = "MTOuKWKLqUPXBXQamzkh"
    api_secret = "lolhEjxCSkseiPhPsaKT"
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    
    payload = {
        "model": "x1",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 50
    }
    
    # 生成签名
    signature, timestamp = generate_hmac_signature(api_key, api_secret, "POST", url, {}, payload)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"HMAC-SHA256 Credential={api_key}, Signature={signature}",
        "X-Timestamp": timestamp,
        "Host": "spark-api-open.xf-yun.com"
    }
    
    print(f"🔑 API Key: {api_key}")
    print(f"🔐 Signature: {signature}")
    print(f"⏰ Timestamp: {timestamp}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"📊 状态码: {response.status_code}")
        print(f"📝 响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ HMAC认证成功")
            return True
        else:
            print("❌ HMAC认证失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_hmac_auth_v2():
    """测试HMAC认证方式2 - 科大讯飞标准格式"""
    print("\n🔐 测试HMAC认证方式2 - 科大讯飞标准格式")
    print("-" * 40)
    
    api_key = "MTOuKWKLqUPXBXQamzkh"
    api_secret = "lolhEjxCSkseiPhPsaKT"
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    
    payload = {
        "model": "x1",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 50
    }
    
    # 科大讯飞标准签名方式
    timestamp = str(int(time.time()))
    nonce = str(int(time.time() * 1000))
    
    # 构建签名字符串
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    path = parsed_url.path
    
    # 按照科大讯飞的签名规则
    string_to_sign = f"host: {host}\ndate: {timestamp}\nPOST {path} HTTP/1.1"
    
    # 生成签名
    signature = base64.b64encode(
        hmac.new(
            api_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    # 构建Authorization头
    authorization = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
        "Date": timestamp,
        "Host": host
    }
    
    print(f"🔑 API Key: {api_key}")
    print(f"🔐 Signature: {signature}")
    print(f"📋 Authorization: {authorization}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"📊 状态码: {response.status_code}")
        print(f"📝 响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 科大讯飞标准HMAC认证成功")
            return True
        else:
            print("❌ 科大讯飞标准HMAC认证失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_hmac_auth_v3():
    """测试HMAC认证方式3 - 简化版本"""
    print("\n🔐 测试HMAC认证方式3 - 简化版本")
    print("-" * 40)
    
    api_key = "MTOuKWKLqUPXBXQamzkh"
    api_secret = "lolhEjxCSkseiPhPsaKT"
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    
    payload = {
        "model": "x1",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 50
    }
    
    # 简化的签名方式
    timestamp = str(int(time.time()))
    
    # 构建签名字符串 - 包含必要的host头
    string_to_sign = f"POST\nspark-api-open.xf-yun.com\n/v1/chat/completions\n{timestamp}"
    
    # 生成签名
    signature = hmac.new(
        api_secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "X-Signature": signature,
        "X-Timestamp": timestamp,
        "Host": "spark-api-open.xf-yun.com"
    }
    
    print(f"🔑 API Key: {api_key}")
    print(f"🔐 Signature: {signature}")
    print(f"⏰ Timestamp: {timestamp}")
    print(f"📋 String to sign: {repr(string_to_sign)}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"📊 状态码: {response.status_code}")
        print(f"📝 响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 简化HMAC认证成功")
            return True
        else:
            print("❌ 简化HMAC认证失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_websocket_upgrade():
    """测试是否需要WebSocket升级"""
    print("\n🌐 测试WebSocket升级")
    print("-" * 40)
    
    # 科大讯飞的一些API使用WebSocket
    ws_url = "wss://spark-api.xf-yun.com/v1/chat"
    
    print(f"🔗 WebSocket URL: {ws_url}")
    print("ℹ️ 科大讯飞可能需要WebSocket连接而不是HTTP")
    print("💡 建议查看官方文档确认API调用方式")
    
    return False

def main():
    """主测试函数"""
    print("🚀 Xingcheng API HMAC签名认证测试")
    print("=" * 60)
    
    print("🔍 错误分析:")
    print("  - 错误信息: HMAC signature cannot be verified")
    print("  - 原因: API需要HMAC签名认证，不是简单的Bearer token")
    print("  - 解决方案: 实现正确的HMAC签名算法")
    print()
    
    tests = [
        ("HMAC认证方式1", test_hmac_auth_v1),
        ("HMAC认证方式2", test_hmac_auth_v2),
        ("HMAC认证方式3", test_hmac_auth_v3),
        ("WebSocket升级检查", test_websocket_upgrade)
    ]
    
    success_count = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                success_count += 1
                print(f"✅ {test_name} 成功")
                break  # 找到一个成功的就停止
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"💥 {test_name} 异常: {e}")
    
    print("\n" + "=" * 60)
    if success_count > 0:
        print("🎉 找到了正确的认证方式！")
        return True
    else:
        print("😞 所有HMAC认证方式都失败了")
        print("💡 建议:")
        print("  1. 查看科大讯飞官方API文档")
        print("  2. 确认API密钥格式是否正确")
        print("  3. 检查是否需要WebSocket连接")
        print("  4. 联系API提供商获取正确的认证方式")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
