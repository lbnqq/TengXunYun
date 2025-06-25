#!/usr/bin/env python3
"""
LLM接口连通性测试脚本
"""

import os
import json
from dotenv import load_dotenv
from src.llm_clients.xingcheng_llm import XingchengLLMClient

def test_llm_connection():
    """测试LLM接口连通性"""
    print("=== 科大讯飞星辰平台 X1 模型接口测试 ===\n")
    
    # 加载环境变量
    load_dotenv()
    
    # 获取配置
    api_key = os.getenv("XINGCHENG_API_KEY")
    api_secret = os.getenv("XINGCHENG_API_SECRET")
    model_name = os.getenv("LLM_MODEL_NAME", "x1")
    
    if not api_key:
        print("❌ 错误: 未找到 XINGCHENG_API_KEY 环境变量")
        print("请检查 .env 文件配置或设置环境变量")
        print("获取API密钥地址: https://console.xfyun.cn/services/bmx1")
        return False
    
    print(f"✅ API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else '***'}")
    print(f"✅ Model: {model_name}")
    print(f"✅ API URL: https://spark-api-open.xf-yun.com/v2/chat/completions")
    print()
    
    try:
        # 初始化客户端
        print("🔄 初始化LLM客户端...")
        llm_client = XingchengLLMClient(
            api_key=api_key,
            api_secret=api_secret,
            model_name=model_name
        )
        print("✅ LLM客户端初始化成功")
        print()
        
        # 测试简单对话
        print("🔄 测试简单对话...")
        test_prompt = "你好，请简单介绍一下你自己。"
        print(f"发送内容: {test_prompt}")
        
        response = llm_client.generate(test_prompt, temperature=0.7, max_tokens=100)
        
        print("✅ 收到响应:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        # 测试JSON格式响应
        print("\n🔄 测试JSON格式响应...")
        json_prompt = """请分析以下文档内容，并以JSON格式返回分析结果：
        
        文档内容：这是一个产品需求文档，包含了用户故事、技术栈选择和开发计划。
        
        请返回JSON格式：
        {
            "inferred_scenario": "场景类型",
            "supporting_evidence": "支持证据",
            "inferred_reporter_role": "作者角色",
            "inferred_reader_role": "读者角色"
        }"""
        
        print(f"发送内容: {json_prompt[:100]}...")
        
        json_response = llm_client.generate(json_prompt, temperature=0.3, max_tokens=200)
        
        print("✅ 收到JSON响应:")
        print("-" * 50)
        print(json_response)
        print("-" * 50)
        
        # 尝试解析JSON
        try:
            parsed_json = json.loads(json_response)
            print("✅ JSON解析成功")
            print(f"推断场景: {parsed_json.get('inferred_scenario', 'N/A')}")
            print(f"作者角色: {parsed_json.get('inferred_reporter_role', 'N/A')}")
        except json.JSONDecodeError:
            print("⚠️  JSON解析失败，但API调用成功")
        
        print("\n🎉 LLM接口测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("\n可能的原因:")
        print("1. API密钥无效或已过期")
        print("2. 网络连接问题")
        print("3. API服务暂时不可用")
        print("4. 请求格式错误")
        return False

if __name__ == "__main__":
    success = test_llm_connection()
    if success:
        print("\n✅ 接口测试通过，可以正常使用LLM功能")
    else:
        print("\n❌ 接口测试失败，请检查配置") 