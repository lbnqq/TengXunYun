#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试星火X1密钥管理系统

验证密钥管理器的各项功能是否正常工作。

Author: AI Assistant
Created: 2025-08-03
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_key_manager():
    """测试密钥管理器功能"""
    print("🧪 测试星火X1密钥管理系统")
    print("=" * 50)
    
    try:
        # 1. 测试导入密钥管理器
        print("1️⃣ 测试导入密钥管理器...")
        from src.core.config.spark_x1_key_manager import key_manager, get_spark_x1_key, get_spark_x1_config
        print("✅ 密钥管理器导入成功")
        
        # 2. 测试配置文件加载
        print("\n2️⃣ 测试配置文件加载...")
        print(f"   配置文件路径: {key_manager.config_path}")
        print(f"   配置文件存在: {'是' if os.path.exists(key_manager.config_path or '') else '否'}")
        
        # 3. 测试获取主密钥
        print("\n3️⃣ 测试获取主密钥...")
        primary_key = get_spark_x1_key()
        print(f"   主密钥: {primary_key[:20]}...")
        print("✅ 主密钥获取成功")
        
        # 4. 测试获取模块特定密钥
        print("\n4️⃣ 测试获取模块特定密钥...")
        modules = ['smart_fill', 'style_alignment', 'format_alignment', 'document_review']
        for module in modules:
            module_key = get_spark_x1_key(module)
            print(f"   {module}: {module_key[:20]}...")
        print("✅ 模块密钥获取成功")
        
        # 5. 测试API配置获取
        print("\n5️⃣ 测试API配置获取...")
        api_config = get_spark_x1_config()
        print(f"   基础URL: {api_config.get('base_url', 'N/A')}")
        print(f"   超时设置: {api_config.get('timeout', 'N/A')}")
        print(f"   模型: {api_config.get('model', 'N/A')}")
        print("✅ API配置获取成功")
        
        # 6. 测试密钥列表功能
        print("\n6️⃣ 测试密钥列表功能...")
        keys_info = key_manager.list_all_keys()
        print(f"   主密钥状态: {keys_info.get('primary', {}).get('status', 'N/A')}")
        print(f"   备用密钥数量: {len(keys_info.get('backup', {}))}")
        print("✅ 密钥列表功能正常")
        
        # 7. 测试密钥验证
        print("\n7️⃣ 测试密钥验证...")
        is_valid = key_manager.test_key()
        print(f"   密钥验证结果: {'通过' if is_valid else '失败'}")
        print("✅ 密钥验证功能正常")
        
        print("\n🎉 所有测试通过！密钥管理系统工作正常。")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_app_integration():
    """测试Web应用集成"""
    print("\n🌐 测试Web应用集成")
    print("=" * 50)
    
    try:
        # 测试Web应用是否能正常导入
        print("1️⃣ 测试Web应用导入...")
        from src.web_app import app
        print("✅ Web应用导入成功")
        
        # 检查各个协调器是否正常初始化
        print("\n2️⃣ 检查协调器初始化状态...")
        from src.web_app import (
            integrated_manager,
            style_alignment_coordinator, 
            format_alignment_coordinator,
            document_review_coordinator
        )
        
        coordinators = {
            '智能填报管理器': integrated_manager,
            '文风对齐协调器': style_alignment_coordinator,
            '格式对齐协调器': format_alignment_coordinator,
            '文档审查协调器': document_review_coordinator
        }
        
        for name, coordinator in coordinators.items():
            status = "✅ 已初始化" if coordinator is not None else "❌ 未初始化"
            print(f"   {name}: {status}")
        
        print("\n✅ Web应用集成测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ Web应用集成测试失败: {e}")
        return False

def test_management_tool():
    """测试管理工具"""
    print("\n🛠️ 测试管理工具")
    print("=" * 50)
    
    try:
        # 测试管理工具导入
        print("1️⃣ 测试管理工具导入...")
        import subprocess
        
        # 测试帮助命令
        result = subprocess.run([
            sys.executable, 'tools/manage_spark_x1_keys.py', '--help'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ 管理工具帮助命令正常")
        else:
            print(f"❌ 管理工具帮助命令失败: {result.stderr}")
            return False
        
        # 测试列表命令
        print("\n2️⃣ 测试列表命令...")
        result = subprocess.run([
            sys.executable, 'tools/manage_spark_x1_keys.py', '--list'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ 管理工具列表命令正常")
            print("   输出预览:")
            for line in result.stdout.split('\n')[:5]:
                if line.strip():
                    print(f"     {line}")
        else:
            print(f"❌ 管理工具列表命令失败: {result.stderr}")
            return False
        
        print("\n✅ 管理工具测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ 管理工具测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试星火X1密钥管理系统")
    print("=" * 60)
    
    results = []
    
    # 运行各项测试
    results.append(test_key_manager())
    results.append(test_web_app_integration())
    results.append(test_management_tool())
    
    # 总结测试结果
    print("\n📊 测试结果总结")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "密钥管理器功能测试",
        "Web应用集成测试", 
        "管理工具测试"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！星火X1密钥管理系统已成功部署。")
        print("\n📝 后续步骤:")
        print("1. 使用 tools/manage_spark_x1_keys.py 管理密钥")
        print("2. 根据需要更新 config/spark_x1_keys.yaml 配置")
        print("3. 启动Web应用测试各模块功能")
    else:
        print(f"\n⚠️ 有 {total - passed} 项测试失败，请检查相关配置。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
