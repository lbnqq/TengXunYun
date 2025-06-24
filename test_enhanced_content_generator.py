#!/usr/bin/env python3
"""
测试增强内容生成与优化引擎的功能
Test script for the Enhanced Content Generator Tool
"""

import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.tools.content_filler import EnhancedContentGeneratorTool

class MockLLMClient:
    """模拟LLM客户端用于测试"""
    
    def generate(self, prompt: str) -> str:
        if "executive summary" in prompt.lower():
            return """This executive summary outlines the key findings and recommendations from our comprehensive analysis. 
            The project demonstrates significant potential for improving operational efficiency by 30% while reducing costs by 15%. 
            We recommend immediate implementation of the proposed solution with a phased rollout approach."""
        elif "technical section" in prompt.lower():
            return """The technical implementation involves a microservices architecture built on cloud-native technologies. 
            The system utilizes containerization with Docker and orchestration through Kubernetes. 
            Performance benchmarks indicate 99.9% uptime with sub-100ms response times."""
        else:
            return "Generated content based on the provided context and parameters."

def test_template_filling():
    """测试模板填充功能"""
    
    print("🚀 测试模板填充功能")
    print("=" * 40)
    
    # 初始化内容生成器
    mock_llm = MockLLMClient()
    generator = EnhancedContentGeneratorTool(llm_client=mock_llm)
    
    # 测试模板
    template = """
# {{document_title}}

**作者**: {{author}}
**日期**: {{date}}
**版本**: {{version}}

## 项目概述
{{project_overview}}

## 关键发现
{{key_findings}}

## 建议
{{recommendations}}

## 下一步行动
{{next_steps}}

---
文档状态: {{status}}
优先级: {{priority}}
"""
    
    # 测试数据
    test_data = {
        "document_title": "AI文档处理系统分析报告",
        "author": "张三",
        "project_overview": "本项目旨在开发智能文档处理系统，提高办公效率。",
        "key_findings": "系统可以提高文档处理效率50%，减少人工错误90%。",
        "recommendations": "建议立即启动项目开发，采用敏捷开发方法。",
        "next_steps": "1. 组建开发团队 2. 制定详细计划 3. 开始原型开发"
    }
    
    # 上下文信息
    context = {
        "document_type": "analysis_report",
        "target_audience": "management",
        "style": "formal"
    }
    
    print("📝 原始模板:")
    print(template[:200] + "...")
    print()
    
    # 执行模板填充
    result = generator.fill_template(template, test_data, context)
    
    if result.get("success"):
        print("✅ 模板填充成功!")
        print(f"📊 填充统计:")
        print(f"   - 发现占位符: {result['placeholders_found']}")
        print(f"   - 已填充占位符: {len(result['placeholders_filled'])}")
        print(f"   - 填充率: {result['processing_metadata']['fill_ratio']:.1%}")
        
        print(f"\n📄 填充后的内容:")
        print("-" * 40)
        print(result["filled_content"][:500] + "...")
        
        print(f"\n🔍 填充详情:")
        for item in result["placeholders_filled"][:5]:  # 显示前5个
            print(f"   - {item['placeholder']}: {item['value'][:50]}... ({item['method']})")
    else:
        print(f"❌ 模板填充失败: {result.get('error')}")

def test_content_optimization():
    """测试内容优化功能"""
    
    print(f"\n🔧 测试内容优化功能")
    print("=" * 40)
    
    generator = EnhancedContentGeneratorTool()
    
    # 测试内容（故意包含需要优化的问题）
    test_content = """
    In order to facilitate the implementation of this very important project, we need to utilize 
    advanced technologies and methodologies. It is important to note that this initiative will 
    demonstrate significant improvements in operational efficiency. Due to the fact that the current 
    system is quite outdated, we really need to initiate a comprehensive modernization process. 
    The team will accommodate all requirements and terminate any legacy processes that are not 
    effective. This is really awesome and will be very beneficial for the organization.
    """
    
    print("📝 原始内容:")
    print(test_content.strip())
    print()
    
    # 测试不同的优化目标
    optimization_goals = ["clarity", "conciseness", "professionalism", "readability"]
    
    for goal in optimization_goals:
        print(f"🎯 优化目标: {goal.upper()}")
        print("-" * 30)
        
        result = generator.optimize_content(test_content, [goal])
        
        if result.get("success"):
            print(f"✅ 优化完成")
            print(f"📊 改进指标:")
            metrics = result["improvement_metrics"]
            print(f"   - 长度变化: {metrics['length_reduction']} 字符 ({metrics['length_reduction_percent']:.1f}%)")
            print(f"   - 词数变化: {metrics['word_count_original']} → {metrics['word_count_optimized']}")
            
            if result["optimizations_applied"]:
                print(f"🔧 应用的优化:")
                for opt in result["optimizations_applied"][:3]:  # 显示前3个
                    print(f"   - {opt}")
            
            print(f"📄 优化后内容:")
            print(result["optimized_content"][:200] + "...")
        else:
            print(f"❌ 优化失败: {result.get('error')}")
        
        print()

def test_style_transfer():
    """测试风格转换功能"""
    
    print(f"🎨 测试风格转换功能")
    print("=" * 40)
    
    generator = EnhancedContentGeneratorTool()
    
    # 测试内容
    informal_content = """
    Hey guys! This is really cool stuff we're working on. We can't wait to show you what we've built. 
    It's awesome and will totally change how you work with documents. You'll love it!
    """
    
    formal_content = """
    We hereby present the findings of our comprehensive analysis. The proposed solution demonstrates 
    significant potential for organizational improvement. We cannot overstate the importance of this initiative.
    """
    
    test_cases = [
        {
            "name": "非正式 → 正式",
            "content": informal_content,
            "target_style": "formal"
        },
        {
            "name": "正式 → 非正式", 
            "content": formal_content,
            "target_style": "informal"
        },
        {
            "name": "通用 → 技术性",
            "content": "This system works well and provides good results for users.",
            "target_style": "technical"
        }
    ]
    
    for test_case in test_cases:
        print(f"📝 测试: {test_case['name']}")
        print("-" * 30)
        print(f"原始内容: {test_case['content'][:100]}...")
        
        result = generator.transfer_style(test_case['content'], test_case['target_style'])
        
        if result.get("success"):
            print(f"✅ 风格转换成功")
            print(f"📊 转换信息:")
            print(f"   - 源风格: {result['source_style']}")
            print(f"   - 目标风格: {result['target_style']}")
            print(f"   - 转换置信度: {result['transfer_confidence']:.1%}")
            
            if result["style_changes"]:
                print(f"🔧 风格变化:")
                for change in result["style_changes"][:3]:
                    print(f"   - {change}")
            
            print(f"📄 转换后内容:")
            print(result["transferred_content"][:150] + "...")
        else:
            print(f"❌ 风格转换失败: {result.get('error')}")
        
        print()

def test_content_generation():
    """测试内容生成功能"""
    
    print(f"📝 测试内容生成功能")
    print("=" * 40)
    
    mock_llm = MockLLMClient()
    generator = EnhancedContentGeneratorTool(llm_client=mock_llm)
    
    # 测试不同类型的内容生成
    test_cases = [
        {
            "content_type": "executive_summary",
            "parameters": {
                "topic": "AI文档处理系统",
                "findings": "效率提升30%，成本降低15%",
                "recommendations": "立即实施分阶段推出"
            }
        },
        {
            "content_type": "technical_section", 
            "parameters": {
                "background": "现有系统性能不足",
                "methodology": "微服务架构设计",
                "implementation": "容器化部署",
                "results": "99.9%可用性"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"📋 生成内容类型: {test_case['content_type']}")
        print("-" * 30)
        
        result = generator.generate_content(
            test_case['content_type'], 
            test_case['parameters']
        )
        
        if result.get("success"):
            print(f"✅ 内容生成成功")
            print(f"📊 生成信息:")
            metadata = result["generation_metadata"]
            print(f"   - 使用参数: {metadata['parameters_used']}")
            print(f"   - 内容长度: {metadata['content_length']} 字符")
            print(f"   - 生成方法: {metadata['generation_method']}")
            
            print(f"📄 生成的内容:")
            print(result["generated_content"][:300] + "...")
        else:
            print(f"❌ 内容生成失败: {result.get('error')}")
        
        print()

if __name__ == "__main__":
    test_template_filling()
    test_content_optimization()
    test_style_transfer()
    test_content_generation()
    print("🎉 所有测试完成!")
