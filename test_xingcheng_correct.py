#!/usr/bin/env python3
"""
使用正确的AK:SK格式测试Xingcheng API
Test Xingcheng API with correct AK:SK format
"""

import os
import sys
import json
import requests

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_correct_ak_sk_format():
    """使用正确的AK:SK格式直接测试API"""
    print("🔧 使用正确的AK:SK格式测试Xingcheng API")
    print("=" * 60)
    
    # API配置
    api_key = "MTOuKWKLqUPXBXQamzkh"
    api_secret = "lolhEjxCSkseiPhPsaKT"
    ak_sk_token = f"{api_key}:{api_secret}"
    url = "https://spark-api-open.xf-yun.com/v2/chat/completions"
    
    print(f"🔑 API Key: {api_key}")
    print(f"🔐 API Secret: {api_secret}")
    print(f"🎫 AK:SK Token: {ak_sk_token}")
    print(f"🌐 URL: {url}")
    print()
    
    # 请求头
    headers = {
        "Authorization": f"Bearer {ak_sk_token}",
        "Content-Type": "application/json"
    }
    
    # 请求体
    payload = {
        "model": "x1",
        "messages": [
            {"role": "user", "content": "你好，请简单介绍一下你自己。"}
        ],
        "max_tokens": 100,
        "temperature": 0.7,
        "user": "test_user_123"
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
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        print()
        
        print("📝 响应内容:")
        response_text = response.text
        print(response_text)
        print()
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ JSON解析成功:")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                
                if 'choices' in data and len(data['choices']) > 0:
                    choice = data['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        content = choice['message']['content']
                        print(f"\n🎯 AI回复: {content}")
                        
                        # 检查usage信息
                        if 'usage' in data:
                            usage = data['usage']
                            print(f"\n📊 Token使用情况:")
                            print(f"  - 输入Token: {usage.get('prompt_tokens', 0)}")
                            print(f"  - 输出Token: {usage.get('completion_tokens', 0)}")
                            print(f"  - 总Token: {usage.get('total_tokens', 0)}")
                        
                        return True
                    else:
                        print("❌ 响应格式错误：缺少message/content")
                        return False
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

def test_with_multi_llm_client():
    """使用修复后的MultiLLMClient测试"""
    print("\n🤖 使用修复后的MultiLLMClient测试")
    print("=" * 60)
    
    # 设置环境变量
    os.environ['XINGCHENG_API_KEY'] = 'MTOuKWKLqUPXBXQamzkh'
    os.environ['XINGCHENG_API_SECRET'] = 'lolhEjxCSkseiPhPsaKT'
    
    try:
        from src.llm_clients.multi_llm import MultiLLMClient
        
        # 创建客户端
        client = MultiLLMClient()
        
        print("    🤖 客户端创建成功")
        
        # 测试简单对话
        test_prompt = "你好，请用一句话介绍人工智能。"
        
        print(f"    📝 发送测试提示: {test_prompt}")
        
        # 使用generate方法
        result = client.generate(test_prompt, model="xingcheng/x1")
        
        print(f"    📊 响应长度: {len(result)} 字符")
        print(f"    📄 响应内容: {result}")
        
        # 检查是否是错误响应
        if "[API Error:" in result:
            print("    ❌ API调用失败")
            return False
        else:
            print("    ✅ API调用成功")
            return True
            
    except Exception as e:
        print(f"    ❌ 测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_chat_completion():
    """测试聊天完成功能"""
    print("\n💬 测试聊天完成功能")
    print("=" * 60)
    
    # 设置环境变量
    os.environ['XINGCHENG_API_KEY'] = 'MTOuKWKLqUPXBXQamzkh'
    os.environ['XINGCHENG_API_SECRET'] = 'lolhEjxCSkseiPhPsaKT'
    
    try:
        from src.llm_clients.multi_llm import MultiLLMClient
        
        client = MultiLLMClient()
        
        # 测试聊天消息
        messages = [
            {"role": "system", "content": "你是一个有用的AI助手。"},
            {"role": "user", "content": "请推荐一个适合自驾游的国内景点。"}
        ]
        
        print("    💭 发送聊天消息...")
        
        # 使用chat_completion方法
        result = client.chat_completion(messages, model="xingcheng/x1")
        
        print(f"    📊 响应结构: {list(result.keys())}")
        
        if 'choices' in result and result['choices']:
            choice = result['choices'][0]
            message = choice.get('message', {})
            content = message.get('content', '')
            
            print(f"    📄 响应内容: {content[:200]}...")
            
            if content and not content.startswith("[API Error:"):
                print("    ✅ 聊天完成成功")
                
                # 显示usage信息
                if 'usage' in result:
                    usage = result['usage']
                    print(f"    📊 Token使用: {usage}")
                
                return True
            else:
                print("    ❌ 聊天完成失败")
                return False
        else:
            print("    ❌ 响应格式错误")
            return False
            
    except Exception as e:
        print(f"    ❌ 测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_openai_sdk_compatibility():
    """测试OpenAI SDK兼容性"""
    print("\n🔗 测试OpenAI SDK兼容性")
    print("=" * 60)
    
    try:
        import openai
        
        # 配置OpenAI客户端
        client = openai.OpenAI(
            api_key="MTOuKWKLqUPXBXQamzkh:lolhEjxCSkseiPhPsaKT",
            base_url="https://spark-api-open.xf-yun.com/v2/"
        )
        
        print("📦 OpenAI客户端配置成功")
        print(f"🔑 API Key: MTOuKWKLqUPXBXQamzkh:lolhEjxCSkseiPhPsaKT")
        print(f"🌐 Base URL: https://spark-api-open.xf-yun.com/v2/")
        print()
        
        print("🚀 发送请求...")
        
        response = client.chat.completions.create(
            model="x1",
            messages=[
                {"role": "user", "content": "你好，请简单介绍一下你自己。"}
            ],
            max_tokens=100,
            temperature=0.7,
            user="test_user_123"
        )
        
        print("✅ OpenAI SDK调用成功")
        print(f"🎯 AI回复: {response.choices[0].message.content}")
        print(f"📊 Token使用: {response.usage}")
        
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
    print("🚀 Xingcheng API 正确格式测试")
    print("=" * 80)
    
    print("🔍 使用正确的认证格式:")
    print("  - API Key: MTOuKWKLqUPXBXQamzkh")
    print("  - API Secret: lolhEjxCSkseiPhPsaKT")
    print("  - Bearer Token: MTOuKWKLqUPXBXQamzkh:lolhEjxCSkseiPhPsaKT")
    print("  - URL: https://spark-api-open.xf-yun.com/v2/chat/completions")
    print()
    
    tests = [
        ("直接API测试", test_correct_ak_sk_format),
        ("MultiLLMClient测试", test_with_multi_llm_client),
        ("聊天完成测试", test_chat_completion),
        ("OpenAI SDK兼容性", test_openai_sdk_compatibility)
    ]
    
    success_count = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                success_count += 1
                print(f"✅ {test_name} 成功")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"💥 {test_name} 异常: {e}")
        
        print()
    
    print("=" * 80)
    print(f"🎯 测试结果: {success_count}/{len(tests)} 通过")
    
    if success_count >= 1:
        print("🎉 Xingcheng API修复成功！")
        return True
    else:
        print("😞 Xingcheng API仍然存在问题")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
