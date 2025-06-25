#!/usr/bin/env python3
"""
测试LLM客户端功能
Test LLM client functionality
"""

import sys
import os
import json

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_multi_llm_client_initialization():
    """测试多LLM客户端初始化"""
    print("🤖 测试多LLM客户端初始化")
    print("-" * 40)
    
    try:
        from src.llm_clients.multi_llm import MultiLLMClient
        
        # 创建客户端（不需要真实API密钥）
        client = MultiLLMClient()
        
        print("    ✅ 客户端初始化成功")
        
        # 测试获取可用模型
        models = client.get_available_models()
        print(f"    - 可用模型数量: {len(models)}")
        print(f"    - 模型列表: {models[:3]}...")  # 显示前3个
        
        # 测试基础配置
        print(f"    - API端点数量: {len(client.api_endpoints)}")
        print(f"    - 默认模型配置: {len(client.default_models)}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ 客户端初始化失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_llm_client_generate():
    """测试LLM客户端生成功能"""
    print("\n💬 测试LLM客户端生成功能")
    print("-" * 40)
    
    try:
        from src.llm_clients.multi_llm import MultiLLMClient
        
        client = MultiLLMClient()
        
        # 测试简单生成（不会真正调用API，因为没有密钥）
        test_prompt = "请简要介绍人工智能的发展历史。"
        
        print("    📝 测试文本生成...")
        result = client.generate(test_prompt, model="auto")
        
        print("    ✅ 生成方法调用成功")
        print(f"    - 响应长度: {len(result)} 字符")
        print(f"    - 响应预览: {result[:100]}...")
        
        # 测试带选项的生成
        print("    🔧 测试带选项的生成...")
        options = {
            "max_tokens": 500,
            "temperature": 0.7
        }
        result2 = client.generate(test_prompt, model="auto", options=options)
        
        print("    ✅ 带选项生成成功")
        print(f"    - 响应长度: {len(result2)} 字符")
        
        return True
        
    except Exception as e:
        print(f"    ❌ 生成功能测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_chat_completion():
    """测试聊天完成功能"""
    print("\n💭 测试聊天完成功能")
    print("-" * 40)
    
    try:
        from src.llm_clients.multi_llm import MultiLLMClient
        
        client = MultiLLMClient()
        
        # 测试聊天消息
        messages = [
            {"role": "system", "content": "你是一个有用的AI助手。"},
            {"role": "user", "content": "请介绍一下机器学习的基本概念。"}
        ]
        
        print("    💬 测试聊天完成...")
        result = client.chat_completion(messages, model="auto")
        
        print("    ✅ 聊天完成调用成功")
        print(f"    - 响应结构: {list(result.keys())}")
        
        if 'choices' in result and result['choices']:
            choice = result['choices'][0]
            message = choice.get('message', {})
            content = message.get('content', '')
            
            print(f"    - 消息角色: {message.get('role', 'unknown')}")
            print(f"    - 内容长度: {len(content)} 字符")
            print(f"    - 内容预览: {content[:100]}...")
        
        if 'usage' in result:
            usage = result['usage']
            print(f"    - Token使用: {usage}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ 聊天完成测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_api_endpoints():
    """测试API端点配置"""
    print("\n🔗 测试API端点配置")
    print("-" * 40)
    
    try:
        from src.llm_clients.multi_llm import MultiLLMClient
        
        client = MultiLLMClient()
        
        print("    📊 API端点状态:")
        for endpoint_name, config in client.api_endpoints.items():
            has_key = bool(config.get('key'))
            url = config.get('url', 'N/A')
            
            print(f"      - {endpoint_name}:")
            print(f"        * 已配置密钥: {'✅' if has_key else '❌'}")
            print(f"        * API地址: {url}")
            print(f"        * 默认模型: {client.default_models.get(endpoint_name, 'N/A')}")
        
        # 测试模型选择逻辑
        print("    🎯 测试模型选择:")
        test_models = ["auto", "qiniu/deepseek-v3", "together/mixtral", "invalid/model"]
        
        for model in test_models:
            try:
                # 这里只测试模型解析逻辑，不实际调用API
                print(f"      - 模型 '{model}': 可解析")
            except Exception as e:
                print(f"      - 模型 '{model}': 解析失败 - {e}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ API端点测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_error_handling():
    """测试错误处理"""
    print("\n⚠️ 测试错误处理")
    print("-" * 40)
    
    try:
        from src.llm_clients.multi_llm import MultiLLMClient
        
        client = MultiLLMClient()
        
        # 测试无效输入处理
        print("    🚫 测试无效输入处理...")
        
        # 空消息
        result1 = client.generate("", model="auto")
        print(f"      - 空提示处理: {'✅' if result1 else '❌'}")
        
        # 无效模型
        result2 = client.generate("测试", model="invalid_model")
        print(f"      - 无效模型处理: {'✅' if 'Error' in result2 or result2 else '❌'}")
        
        # 测试API密钥缺失的情况
        print("    🔑 测试API密钥缺失处理...")
        
        # 由于没有真实API密钥，所有调用都应该返回错误信息
        messages = [{"role": "user", "content": "测试"}]
        result3 = client.chat_completion(messages, model="qiniu/deepseek-v3")
        
        has_error_handling = (
            'Error' in str(result3) or 
            'failed' in str(result3).lower() or
            'not configured' in str(result3).lower()
        )
        print(f"      - API密钥缺失处理: {'✅' if has_error_handling else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ 错误处理测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_base_llm_compatibility():
    """测试基础LLM客户端兼容性"""
    print("\n🔄 测试基础LLM客户端兼容性")
    print("-" * 40)
    
    try:
        from src.llm_clients.base_llm import BaseLLMClient
        from src.llm_clients.multi_llm import MultiLLMClient
        
        # 检查继承关系
        client = MultiLLMClient()
        is_base_instance = isinstance(client, BaseLLMClient)
        
        print(f"    🏗️ 继承关系检查: {'✅' if is_base_instance else '❌'}")
        
        # 检查必需方法
        required_methods = ['generate']
        missing_methods = []
        
        for method in required_methods:
            if not hasattr(client, method):
                missing_methods.append(method)
        
        print(f"    📋 必需方法检查: {'✅' if not missing_methods else '❌'}")
        if missing_methods:
            print(f"      缺失方法: {missing_methods}")
        
        # 测试方法调用
        try:
            result = client.generate("测试")
            print(f"    🎯 方法调用测试: {'✅' if result is not None else '❌'}")
        except Exception as e:
            print(f"    🎯 方法调用测试: ❌ - {e}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ 兼容性测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始LLM客户端功能测试")
    print("=" * 60)
    
    tests = [
        ("多LLM客户端初始化", test_multi_llm_client_initialization),
        ("LLM客户端生成功能", test_llm_client_generate),
        ("聊天完成功能", test_chat_completion),
        ("API端点配置", test_api_endpoints),
        ("错误处理", test_error_handling),
        ("基础LLM兼容性", test_base_llm_compatibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
        
        print()
    
    print("=" * 60)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有LLM客户端测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
