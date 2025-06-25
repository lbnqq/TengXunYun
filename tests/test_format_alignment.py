#!/usr/bin/env python3
"""
测试文档格式对齐功能
"""

import os
import sys
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.core.tools.document_format_extractor import DocumentFormatExtractor
from src.core.tools.format_alignment_coordinator import FormatAlignmentCoordinator

def test_format_extraction():
    """测试格式提取功能"""
    print("=== 测试格式提取功能 ===")
    
    # 创建测试文档内容
    test_document = """关于加强办公文档管理的通知

各部门、各单位：

    为进一步规范办公文档管理，提高工作效率，现将有关事项通知如下：

一、文档格式要求
    1. 标题使用黑体小三号字体
    2. 正文使用宋体小四号字体
    3. 行距设置为1.5倍

二、管理规定
    1. 所有文档必须按照统一格式编写
    2. 文档审核后方可发布
    3. 定期检查文档质量

    特此通知。

                                办公室
                            2024年1月15日"""
    
    # 初始化格式提取器
    extractor = DocumentFormatExtractor()
    
    # 提取格式
    result = extractor.extract_format_from_document(test_document, "测试通知文档")
    
    if "error" in result:
        print(f"格式提取失败: {result['error']}")
        return False
    
    print(f"模板ID: {result['template_id']}")
    print(f"文档名称: {result['document_name']}")
    print("\n生成的格式提示词:")
    print(result['format_prompt'])
    
    # 保存格式模板
    save_result = extractor.save_format_template(result)
    if save_result.get("success"):
        print(f"\n格式模板已保存: {save_result['template_name']}")
    else:
        print(f"保存失败: {save_result.get('error', '未知错误')}")
    
    return True

def test_format_alignment():
    """测试格式对齐功能"""
    print("\n=== 测试格式对齐功能 ===")
    
    # 创建协调器
    coordinator = FormatAlignmentCoordinator()
    
    # 源文档（待调整格式）
    source_doc = """项目进展报告

项目概述
本项目旨在开发智能办公系统。

进展情况
目前已完成需求分析阶段。

下一步计划
将开始系统设计工作。"""
    
    # 目标文档（格式参考）
    target_doc = """关于项目管理的规定

各项目组：

一、项目管理要求
    1. 严格按照项目计划执行
    2. 定期汇报项目进展

二、质量控制
    1. 建立质量检查机制
    2. 确保项目质量达标

    特此通知。

                                项目管理办公室
                            2024年1月20日"""
    
    # 添加文档到会话
    coordinator.add_document("项目报告.txt", source_doc)
    coordinator.add_document("管理规定.txt", target_doc)
    
    # 处理格式对齐请求
    user_input = "让项目报告.txt与管理规定.txt格式对齐"
    result = coordinator.process_user_request(user_input)
    
    if result.get("success"):
        print("格式对齐成功！")
        print(f"源文档: {result['source_document']}")
        print(f"目标文档: {result['target_document']}")
        print(f"模板名称: {result['template_name']}")
        print(f"模板ID: {result['template_id']}")
        
        if result.get("format_prompt"):
            print("\n生成的格式提示词:")
            print(result['format_prompt'])
        
        return True
    else:
        print(f"格式对齐失败: {result.get('error', '未知错误')}")
        return False

def test_template_management():
    """测试模板管理功能"""
    print("\n=== 测试模板管理功能 ===")
    
    extractor = DocumentFormatExtractor()
    
    # 列出所有模板
    templates = extractor.list_format_templates()
    print(f"找到 {len(templates)} 个格式模板:")
    
    for template in templates:
        print(f"- {template['name']} (ID: {template['template_id']})")
        print(f"  描述: {template['description']}")
        print(f"  创建时间: {template['created_time']}")
        print()
    
    return len(templates) > 0

def test_natural_language_processing():
    """测试自然语言处理功能"""
    print("\n=== 测试自然语言处理功能 ===")
    
    coordinator = FormatAlignmentCoordinator()
    
    # 测试不同的用户输入
    test_inputs = [
        "让文档1与文档2格式对齐",
        "查看所有格式模板",
        "保存当前文档的格式",
        "使用已保存的格式模板",
        "这是一个普通的查询"
    ]
    
    for user_input in test_inputs:
        print(f"\n用户输入: {user_input}")
        result = coordinator.process_user_request(user_input)
        
        if "response" in result:
            print(f"系统回复: {result['response']}")
        
        if "suggestions" in result:
            print("建议:")
            for suggestion in result["suggestions"]:
                print(f"  - {suggestion}")
    
    return True

def main():
    """主测试函数"""
    print("开始测试文档格式对齐功能...\n")
    
    tests = [
        ("格式提取", test_format_extraction),
        ("格式对齐", test_format_alignment),
        ("模板管理", test_template_management),
        ("自然语言处理", test_natural_language_processing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"\n{test_name}测试: {'通过' if success else '失败'}")
        except Exception as e:
            print(f"\n{test_name}测试出错: {str(e)}")
            results.append((test_name, False))
        
        print("-" * 50)
    
    # 总结
    print("\n=== 测试总结 ===")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！格式对齐功能正常工作。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
