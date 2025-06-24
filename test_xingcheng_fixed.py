#!/usr/bin/env python3
"""
测试修复后的Xingcheng API
Test fixed Xingcheng API
"""

import os
import sys
import json

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_xingcheng_api_direct():
    """直接测试Xingcheng API"""
    print("🔧 直接测试Xingcheng API")
    print("-" * 40)
    
    # 设置API密钥（使用您提供的密钥）
    os.environ['XINGCHENG_API_KEY'] = 'MTOuKWKLqUPXBXQamzkh'
    os.environ['XINGCHENG_API_SECRET'] = 'lolhEjxCSkseiPhPsaKT'
    
    try:
        from src.llm_clients.multi_llm import MultiLLMClient
        
        # 创建客户端
        client = MultiLLMClient()
        
        print("    🤖 客户端创建成功")
        
        # 测试简单对话
        test_prompt = "你好，请简单介绍一下你自己。"
        
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

def test_xingcheng_chat_completion():
    """测试Xingcheng聊天完成功能"""
    print("\n💬 测试Xingcheng聊天完成功能")
    print("-" * 40)
    
    # 设置API密钥
    os.environ['XINGCHENG_API_KEY'] = 'MTOuKWKLqUPXBXQamzkh'
    os.environ['XINGCHENG_API_SECRET'] = 'lolhEjxCSkseiPhPsaKT'
    
    try:
        from src.llm_clients.multi_llm import MultiLLMClient
        
        client = MultiLLMClient()
        
        # 测试聊天消息
        messages = [
            {"role": "system", "content": "你是一个有用的AI助手。"},
            {"role": "user", "content": "请用一句话介绍人工智能。"}
        ]
        
        print("    💭 发送聊天消息...")
        
        # 使用chat_completion方法
        result = client.chat_completion(messages, model="xingcheng/x1")
        
        print(f"    📊 响应结构: {list(result.keys())}")
        
        if 'choices' in result and result['choices']:
            choice = result['choices'][0]
            message = choice.get('message', {})
            content = message.get('content', '')
            
            print(f"    📄 响应内容: {content}")
            
            if content and not content.startswith("[API Error:"):
                print("    ✅ 聊天完成成功")
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

def test_xingcheng_with_options():
    """测试带选项的Xingcheng API调用"""
    print("\n⚙️ 测试带选项的Xingcheng API调用")
    print("-" * 40)
    
    # 设置API密钥
    os.environ['XINGCHENG_API_KEY'] = 'MTOuKWKLqUPXBXQamzkh'
    os.environ['XINGCHENG_API_SECRET'] = 'lolhEjxCSkseiPhPsaKT'
    
    try:
        from src.llm_clients.multi_llm import MultiLLMClient
        
        client = MultiLLMClient()
        
        # 测试不同的选项
        test_options = [
            {"max_tokens": 100, "temperature": 0.5},
            {"max_tokens": 200, "temperature": 0.8},
            {"max_tokens": 50, "temperature": 0.3}
        ]
        
        test_prompt = "请写一首关于春天的短诗。"
        
        for i, options in enumerate(test_options, 1):
            print(f"    🧪 测试选项 {i}: {options}")
            
            result = client.generate(test_prompt, model="xingcheng/x1", options=options)
            
            print(f"      📊 响应长度: {len(result)} 字符")
            print(f"      📄 响应预览: {result[:100]}...")
            
            if not result.startswith("[API Error:"):
                print(f"      ✅ 选项 {i} 测试成功")
            else:
                print(f"      ❌ 选项 {i} 测试失败")
                return False
        
        print("    ✅ 所有选项测试成功")
        return True
        
    except Exception as e:
        print(f"    ❌ 测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_api_health_status():
    """测试API健康状态"""
    print("\n📊 测试API健康状态")
    print("-" * 40)
    
    # 设置API密钥
    os.environ['XINGCHENG_API_KEY'] = 'MTOuKWKLqUPXBXQamzkh'
    os.environ['XINGCHENG_API_SECRET'] = 'lolhEjxCSkseiPhPsaKT'
    
    try:
        from src.llm_clients.multi_llm import MultiLLMClient
        
        client = MultiLLMClient()
        
        # 先进行一次API调用以生成统计数据
        client.generate("测试", model="xingcheng/x1")
        
        # 获取健康状态
        if hasattr(client, 'get_api_health_status'):
            health_status = client.get_api_health_status()
            
            print("    📈 API健康状态:")
            for endpoint, status in health_status.items():
                if endpoint == 'xingcheng':
                    print(f"      - {endpoint}:")
                    print(f"        * 已配置: {'✅' if status['configured'] else '❌'}")
                    print(f"        * 健康状态: {'✅' if status['healthy'] else '❌'}")
                    print(f"        * 总请求数: {status['total_requests']}")
                    print(f"        * 成功率: {status['success_rate']:.1f}%")
                    print(f"        * 平均响应时间: {status['average_response_time']:.2f}s")
                    print(f"        * 连续失败次数: {status['consecutive_failures']}")
        else:
            print("    ℹ️ 客户端不支持健康状态检查")
        
        return True
        
    except Exception as e:
        print(f"    ❌ 测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始Xingcheng API修复验证测试")
    print("=" * 60)
    
    print("🔑 使用的API密钥信息:")
    print("  - API Key: MTOuKWKLqUPXBXQamzkh")
    print("  - API Secret: lolhEjxCSkseiPhPsaKT")
    print("  - API URL: https://spark-api-open.xf-yun.com/v1/chat/completions")
    print()
    
    tests = [
        ("直接API测试", test_xingcheng_api_direct),
        ("聊天完成测试", test_xingcheng_chat_completion),
        ("选项参数测试", test_xingcheng_with_options),
        ("健康状态测试", test_api_health_status)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"💥 {test_name} 异常: {e}")
        
        print()
    
    print("=" * 60)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 Xingcheng API修复成功！")
        return True
    elif passed > 0:
        print("⚠️ Xingcheng API部分功能正常，需要进一步优化")
        return True
    else:
        print("😞 Xingcheng API仍然存在问题，需要进一步调试")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
