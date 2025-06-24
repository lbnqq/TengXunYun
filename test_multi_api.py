#!/usr/bin/env python3
"""
测试多API功能的脚本
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm_clients.multi_llm import MultiLLMClient
from src.llm_clients.xingcheng_llm import XingchengLLMClient

def test_multi_api_client():
    """测试多API客户端"""
    print("=" * 60)
    print("测试多API客户端")
    print("=" * 60)
    
    try:
        # 初始化多API客户端
        multi_client = MultiLLMClient()
        print("✅ MultiLLMClient 初始化成功")
        
        # 获取可用模型
        available_models = multi_client.get_available_models()
        print(f"📋 可用模型: {available_models}")
        
        # 测试消息
        test_messages = [
            {"role": "user", "content": "请简单介绍一下人工智能的发展历程"}
        ]
        
        # 测试自动模式
        print("\n🔄 测试自动模式...")
        try:
            response = multi_client.chat_completion(test_messages, model="auto")
            print("✅ 自动模式测试成功")
            print(f"📝 响应内容: {response['choices'][0]['message']['content'][:100]}...")
        except Exception as e:
            print(f"❌ 自动模式测试失败: {e}")
        
        # 测试特定API
        print("\n🔄 测试七牛云API...")
        try:
            response = multi_client.chat_completion(test_messages, model="qiniu/deepseek-v3")
            print("✅ 七牛云API测试成功")
            print(f"📝 响应内容: {response['choices'][0]['message']['content'][:100]}...")
        except Exception as e:
            print(f"❌ 七牛云API测试失败: {e}")
        
        # 测试Together.ai API
        print("\n🔄 测试Together.ai API...")
        try:
            response = multi_client.chat_completion(test_messages, model="together/mistralai/Mixtral-8x7B-Instruct-v0.1")
            print("✅ Together.ai API测试成功")
            print(f"📝 响应内容: {response['choices'][0]['message']['content'][:100]}...")
        except Exception as e:
            print(f"❌ Together.ai API测试失败: {e}")
        
        # 测试OpenRouter API
        print("\n🔄 测试OpenRouter API...")
        try:
            response = multi_client.chat_completion(test_messages, model="openrouter/mistralai/mixtral-8x7b-instruct")
            print("✅ OpenRouter API测试成功")
            print(f"📝 响应内容: {response['choices'][0]['message']['content'][:100]}...")
        except Exception as e:
            print(f"❌ OpenRouter API测试失败: {e}")
            
    except Exception as e:
        print(f"❌ MultiLLMClient 初始化失败: {e}")

def test_xingcheng_client():
    """测试讯飞星火客户端"""
    print("\n" + "=" * 60)
    print("测试讯飞星火客户端")
    print("=" * 60)
    
    try:
        # 检查环境变量
        api_key = os.getenv("XINGCHENG_API_KEY")
        api_secret = os.getenv("XINGCHENG_API_SECRET")
        
        if not api_key or not api_secret:
            print("⚠️ 讯飞星火API密钥未配置，跳过测试")
            return
        
        # 初始化客户端
        xingcheng_client = XingchengLLMClient(
            api_key=api_key,
            api_secret=api_secret,
            model_name="x1"
        )
        print("✅ XingchengLLMClient 初始化成功")
        
        # 测试消息
        test_messages = [
            {"role": "user", "content": "请简单介绍一下人工智能的发展历程"}
        ]
        
        # 测试聊天完成
        print("\n🔄 测试聊天完成...")
        try:
            response = xingcheng_client.chat_completion(test_messages)
            print("✅ 讯飞星火API测试成功")
            print(f"📝 响应内容: {response['choices'][0]['message']['content'][:100]}...")
        except Exception as e:
            print(f"❌ 讯飞星火API测试失败: {e}")
            
    except Exception as e:
        print(f"❌ XingchengLLMClient 初始化失败: {e}")

def test_api_configuration():
    """测试API配置"""
    print("\n" + "=" * 60)
    print("API配置检查")
    print("=" * 60)
    
    # 检查环境变量
    api_keys = {
        'XINGCHENG_API_KEY': os.getenv("XINGCHENG_API_KEY"),
        'XINGCHENG_API_SECRET': os.getenv("XINGCHENG_API_SECRET"),
        'QINIU_API_KEY': os.getenv("QINIU_API_KEY"),
        'TOGETHER_API_KEY': os.getenv("TOGETHER_API_KEY"),
        'OPENROUTER_API_KEY': os.getenv("OPENROUTER_API_KEY"),
        'SILICONFLOW_API_KEY': os.getenv("SILICONFLOW_API_KEY")
    }
    
    print("📋 API配置状态:")
    for name, key in api_keys.items():
        if key:
            print(f"✅ {name}: 已配置")
        else:
            print(f"❌ {name}: 未配置")
    
    # 统计已配置的API
    configured_count = sum(1 for key in api_keys.values() if key)
    print(f"\n📊 总计: {configured_count}/{len(api_keys)} 个API已配置")

def main():
    """主函数"""
    print("🚀 开始测试多API功能")
    print("=" * 60)
    
    # 加载环境变量
    load_dotenv()
    
    # 测试API配置
    test_api_configuration()
    
    # 测试多API客户端
    test_multi_api_client()
    
    # 测试讯飞星火客户端
    test_xingcheng_client()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main() 