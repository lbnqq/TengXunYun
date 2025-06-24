#!/usr/bin/env python3
"""
最终版本的Xingcheng API测试 - 修复日期头格式
Final version of Xingcheng API test - fix date header format
"""

import requests
import json
import time
import hashlib
import hmac
import base64
from urllib.parse import urlparse
from datetime import datetime, timezone
import email.utils

def test_correct_date_format():
    """使用正确的日期格式测试HMAC认证"""
    print("🔐 使用正确日期格式的HMAC认证")
    print("-" * 50)
    
    api_key = "MTOuKWKLqUPXBXQamzkh"
    api_secret = "lolhEjxCSkseiPhPsaKT"
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    
    payload = {
        "model": "x1",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 50
    }
    
    # 生成RFC 2822格式的日期
    now = datetime.now(timezone.utc)
    date_str = email.utils.formatdate(timeval=now.timestamp(), localtime=False, usegmt=True)
    
    # 解析URL
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    path = parsed_url.path
    
    # 构建签名字符串 - 科大讯飞标准格式
    string_to_sign = f"host: {host}\ndate: {date_str}\nPOST {path} HTTP/1.1"
    
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
        "Date": date_str,
        "Host": host
    }
    
    print(f"🔑 API Key: {api_key}")
    print(f"📅 Date: {date_str}")
    print(f"🔐 Signature: {signature}")
    print(f"📋 String to sign: {repr(string_to_sign)}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"📊 状态码: {response.status_code}")
        print(f"📝 响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 正确日期格式HMAC认证成功")
            try:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"🎯 AI回复: {content}")
            except:
                pass
            return True
        else:
            print("❌ 正确日期格式HMAC认证失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_x_date_header():
    """使用X-Date头的HMAC认证"""
    print("\n🔐 使用X-Date头的HMAC认证")
    print("-" * 50)
    
    api_key = "MTOuKWKLqUPXBXQamzkh"
    api_secret = "lolhEjxCSkseiPhPsaKT"
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    
    payload = {
        "model": "x1",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 50
    }
    
    # 生成RFC 2822格式的日期
    now = datetime.now(timezone.utc)
    date_str = email.utils.formatdate(timeval=now.timestamp(), localtime=False, usegmt=True)
    
    # 解析URL
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    path = parsed_url.path
    
    # 构建签名字符串 - 使用x-date
    string_to_sign = f"host: {host}\nx-date: {date_str}\nPOST {path} HTTP/1.1"
    
    # 生成签名
    signature = base64.b64encode(
        hmac.new(
            api_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    # 构建Authorization头
    authorization = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host x-date request-line", signature="{signature}"'
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
        "X-Date": date_str,
        "Host": host
    }
    
    print(f"🔑 API Key: {api_key}")
    print(f"📅 X-Date: {date_str}")
    print(f"🔐 Signature: {signature}")
    print(f"📋 String to sign: {repr(string_to_sign)}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"📊 状态码: {response.status_code}")
        print(f"📝 响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ X-Date头HMAC认证成功")
            try:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"🎯 AI回复: {content}")
            except:
                pass
            return True
        else:
            print("❌ X-Date头HMAC认证失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_timestamp_format():
    """使用时间戳格式的认证"""
    print("\n🔐 使用时间戳格式的认证")
    print("-" * 50)
    
    api_key = "MTOuKWKLqUPXBXQamzkh"
    api_secret = "lolhEjxCSkseiPhPsaKT"
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    
    payload = {
        "model": "x1",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 50
    }
    
    # 使用时间戳
    timestamp = str(int(time.time()))
    
    # 解析URL
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    path = parsed_url.path
    
    # 构建签名字符串
    string_to_sign = f"host: {host}\ntimestamp: {timestamp}\nPOST {path} HTTP/1.1"
    
    # 生成签名
    signature = base64.b64encode(
        hmac.new(
            api_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    # 构建Authorization头
    authorization = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host timestamp request-line", signature="{signature}"'
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
        "Timestamp": timestamp,
        "Host": host
    }
    
    print(f"🔑 API Key: {api_key}")
    print(f"⏰ Timestamp: {timestamp}")
    print(f"🔐 Signature: {signature}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"📊 状态码: {response.status_code}")
        print(f"📝 响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 时间戳格式认证成功")
            try:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"🎯 AI回复: {content}")
            except:
                pass
            return True
        else:
            print("❌ 时间戳格式认证失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_minimal_hmac():
    """最简化的HMAC认证"""
    print("\n🔐 最简化的HMAC认证")
    print("-" * 50)
    
    api_key = "MTOuKWKLqUPXBXQamzkh"
    api_secret = "lolhEjxCSkseiPhPsaKT"
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    
    payload = {
        "model": "x1",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 50
    }
    
    # 生成RFC 2822格式的日期
    now = datetime.now(timezone.utc)
    date_str = email.utils.formatdate(timeval=now.timestamp(), localtime=False, usegmt=True)
    
    # 最简化的签名字符串 - 只包含必要信息
    string_to_sign = f"date: {date_str}"
    
    # 生成签名
    signature = base64.b64encode(
        hmac.new(
            api_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    # 构建Authorization头
    authorization = f'api_key="{api_key}", algorithm="hmac-sha256", headers="date", signature="{signature}"'
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
        "Date": date_str
    }
    
    print(f"🔑 API Key: {api_key}")
    print(f"📅 Date: {date_str}")
    print(f"🔐 Signature: {signature}")
    print(f"📋 String to sign: {repr(string_to_sign)}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"📊 状态码: {response.status_code}")
        print(f"📝 响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 最简化HMAC认证成功")
            try:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"🎯 AI回复: {content}")
            except:
                pass
            return True
        else:
            print("❌ 最简化HMAC认证失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Xingcheng API 最终认证测试")
    print("=" * 60)
    
    print("🔍 基于之前的错误分析:")
    print("  - 需要正确的日期头格式")
    print("  - 可能需要RFC 2822格式的日期")
    print("  - 或者使用X-Date头")
    print()
    
    tests = [
        ("正确日期格式HMAC", test_correct_date_format),
        ("X-Date头HMAC", test_x_date_header),
        ("时间戳格式", test_timestamp_format),
        ("最简化HMAC", test_minimal_hmac)
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
        print("💡 现在可以更新MultiLLMClient使用正确的认证方式")
        return True
    else:
        print("😞 仍然无法找到正确的认证方式")
        print("💡 可能的原因:")
        print("  1. API密钥可能不正确或已过期")
        print("  2. 可能需要特殊的签名算法")
        print("  3. 可能需要额外的参数或头部")
        print("  4. API可能需要特殊的注册或激活")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
