#!/usr/bin/env python3
"""
基础功能测试脚本
Test basic functionality of the office document agent
"""

import sys
import os
import traceback

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """测试基础模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试核心工具导入
        print("  - 导入核心工具...")
        from src.core.tools import DocumentParserTool, ContentFillerTool
        print("    ✅ 核心工具导入成功")
        
        # 测试LLM客户端导入
        print("  - 导入LLM客户端...")
        from src.llm_clients.base_llm import BaseLLMClient
        from src.llm_clients.multi_llm import MultiLLMClient
        print("    ✅ LLM客户端导入成功")
        
        # 测试智能引导导入
        print("  - 导入智能引导模块...")
        from src.core.guidance import ScenarioInferenceModule
        print("    ✅ 智能引导模块导入成功")
        
        # 测试代理编排器导入
        print("  - 导入代理编排器...")
        from src.core.agent.agent_orchestrator import AgentOrchestrator
        print("    ✅ 代理编排器导入成功")
        
        return True
        
    except Exception as e:
        print(f"    ❌ 导入失败: {e}")
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_basic_tools():
    """测试基础工具功能"""
    print("\n🛠️ 测试基础工具...")
    
    try:
        from src.core.tools import DocumentParserTool
        
        # 创建测试文档
        test_content = """# 测试文档
        
这是一个测试文档，用于验证文档解析功能。

## 主要内容

1. 第一项内容
2. 第二项内容
3. 第三项内容

### 详细说明

这里是详细的说明内容，包含了一些重要信息。
"""
        
        test_file = "test_basic.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # 测试文档解析
        parser = DocumentParserTool()
        result = parser.execute(test_file)
        
        if "error" in result:
            print(f"    ❌ 文档解析失败: {result['error']}")
            return False
        
        print("    ✅ 文档解析成功")
        print(f"    - 内容长度: {len(result.get('text_content', ''))}")
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"    ❌ 工具测试失败: {e}")
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_llm_clients():
    """测试LLM客户端"""
    print("\n🤖 测试LLM客户端...")
    
    try:
        from src.llm_clients.multi_llm import MultiLLMClient
        
        # 创建多API客户端（不需要真实API密钥）
        client = MultiLLMClient()
        
        # 获取可用模型
        models = client.get_available_models()
        print(f"    ✅ 多API客户端创建成功")
        print(f"    - 可用模型: {len(models)}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ LLM客户端测试失败: {e}")
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_web_app_imports():
    """测试Web应用相关导入"""
    print("\n🌐 测试Web应用导入...")
    
    try:
        # 测试Flask应用导入
        from src.web_app import app
        print("    ✅ Flask应用导入成功")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Web应用导入失败: {e}")
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始基础功能测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("基础工具", test_basic_tools),
        ("LLM客户端", test_llm_clients),
        ("Web应用", test_web_app_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有基础功能测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败，需要修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
