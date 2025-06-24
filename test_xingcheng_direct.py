#!/usr/bin/env python3
"""
直接测试Xingcheng API，不依赖客户端代码
Direct test of Xingcheng API without client code dependencies
"""

import requests
import json
import time

def test_xingcheng_api_raw():
    """直接使用requests测试Xingcheng API"""
    print("🔧 直接测试Xingcheng API")
    print("=" * 50)
    
    # API配置
    api_key = "MTOuKWKLqUPXBXQamzkh"
    api_secret = "lolhEjxCSkseiPhPsaKT"
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    
    print(f"🔑 API Key: {api_key}")
    print(f"🔐 API Secret: {api_secret}")
    print(f"🌐 URL: {url}")
    print()
    
    # 请求头 - 使用Bearer token方式
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 请求体
    payload = {
        "model": "x1",
        "messages": [
            {"role": "user", "content": "你好，请简单介绍一下你自己。"}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    print("📋 请求头:")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    print()
    
    print("📦 请求体:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print()
    
    try:
        print("🚀 发送请求...")
        start_time = time.time()
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        response_time = time.time() - start_time
        
        print(f"⏱️ 响应时间: {response_time:.2f}秒")
        print(f"📊 状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        print()
        
        print("📝 响应内容:")
        print(response.text)
        print()
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ JSON解析成功:")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    print(f"\n🎯 AI回复: {content}")
                    return True
                else:
                    print("❌ 响应格式错误：缺少choices")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                return False
        else:
            print(f"❌ API调用失败，状态码: {response.status_code}")
            
            # 尝试解析错误信息
            try:
                error_data = response.json()
                print("🔍 错误详情:")
                print(json.dumps(error_data, ensure_ascii=False, indent=2))
            except:
                print("🔍 错误详情（原始文本）:")
                print(response.text)
            
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
        return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_different_auth_methods():
    """测试不同的认证方法"""
    print("\n🔐 测试不同的认证方法")
    print("=" * 50)
    
    api_key = "MTOuKWKLqUPXBXQamzkh"
    api_secret = "lolhEjxCSkseiPhPsaKT"
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    
    payload = {
        "model": "x1",
        "messages": [{"role": "user", "content": "测试"}],
        "max_tokens": 50
    }
    
    # 方法1: Bearer Token (API Key)
    print("🧪 方法1: Bearer Token (API Key)")
    headers1 = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers1, json=payload, timeout=10)
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ 成功")
            return True
        else:
            print(f"  ❌ 失败: {response.text[:100]}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    
    # 方法2: Bearer Token (API Secret)
    print("\n🧪 方法2: Bearer Token (API Secret)")
    headers2 = {
        "Authorization": f"Bearer {api_secret}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers2, json=payload, timeout=10)
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ 成功")
            return True
        else:
            print(f"  ❌ 失败: {response.text[:100]}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    
    # 方法3: 组合密钥
    print("\n🧪 方法3: 组合密钥 (key:secret)")
    combined_key = f"{api_key}:{api_secret}"
    headers3 = {
        "Authorization": f"Bearer {combined_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers3, json=payload, timeout=10)
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ 成功")
            return True
        else:
            print(f"  ❌ 失败: {response.text[:100]}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    
    # 方法4: 自定义头部
    print("\n🧪 方法4: 自定义头部")
    headers4 = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
        "X-API-Secret": api_secret
    }
    
    try:
        response = requests.post(url, headers=headers4, json=payload, timeout=10)
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ 成功")
            return True
        else:
            print(f"  ❌ 失败: {response.text[:100]}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
    
    return False

def test_openai_sdk_compatibility():
    """测试OpenAI SDK兼容性"""
    print("\n🤖 测试OpenAI SDK兼容性")
    print("=" * 50)
    
    try:
        import openai
        
        # 配置OpenAI客户端
        client = openai.OpenAI(
            api_key="MTOuKWKLqUPXBXQamzkh",
            base_url="https://spark-api-open.xf-yun.com/v1/"
        )
        
        print("📦 OpenAI客户端配置成功")
        print(f"🔑 API Key: MTOuKWKLqUPXBXQamzkh")
        print(f"🌐 Base URL: https://spark-api-open.xf-yun.com/v1/")
        print()
        
        print("🚀 发送请求...")
        
        response = client.chat.completions.create(
            model="x1",
            messages=[
                {"role": "user", "content": "你好，请简单介绍一下你自己。"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        print("✅ OpenAI SDK调用成功")
        print(f"🎯 AI回复: {response.choices[0].message.content}")
        
        return True
        
    except ImportError:
        print("❌ OpenAI SDK未安装，跳过此测试")
        print("💡 可以运行: pip install openai")
        return False
    except Exception as e:
        print(f"❌ OpenAI SDK测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Xingcheng API 直接测试")
    print("=" * 60)
    
    tests = [
        ("原始API测试", test_xingcheng_api_raw),
        ("不同认证方法", test_different_auth_methods),
        ("OpenAI SDK兼容性", test_openai_sdk_compatibility)
    ]
    
    success_count = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 开始测试: {test_name}")
        try:
            if test_func():
                success_count += 1
                print(f"✅ {test_name} 成功")
                if success_count == 1:  # 第一个成功就够了
                    break
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"💥 {test_name} 异常: {e}")
    
    print("\n" + "=" * 60)
    if success_count > 0:
        print("🎉 找到了可用的API调用方式！")
        return True
    else:
        print("😞 所有测试都失败了")
        print("💡 建议检查:")
        print("  1. API密钥是否正确")
        print("  2. 网络连接是否正常")
        print("  3. API服务是否可用")
        print("  4. 是否需要特殊的认证方式")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
