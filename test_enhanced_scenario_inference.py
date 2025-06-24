#!/usr/bin/env python3
"""
测试增强场景推断引擎的功能
Test script for the Enhanced Scenario Inference Engine
"""

import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.guidance.scenario_inference import EnhancedScenarioInferenceModule
from src.core.tools.document_parser import EnhancedDocumentParserTool

class MockLLMClient:
    """模拟LLM客户端用于测试"""
    
    def generate(self, prompt: str) -> str:
        # 根据提示内容返回不同的模拟响应
        if "人工智能" in prompt or "AI" in prompt or "技术报告" in prompt:
            return json.dumps({
                "document_type": "technical_report",
                "scenario": "Technical Report",
                "author_role": "Technical Lead",
                "target_audience": "Technical Team",
                "document_purpose": "informational",
                "formality_level": "semi_formal",
                "confidence": 0.85,
                "supporting_evidence": ["technical terminology", "structured sections", "methodology discussion"],
                "key_topics": ["AI", "document processing", "system architecture"],
                "writing_style": "technical and structured",
                "complexity_level": "advanced"
            })
        elif "产品" in prompt or "product" in prompt:
            return json.dumps({
                "document_type": "product_proposal",
                "scenario": "Product Proposal",
                "author_role": "Product Manager",
                "target_audience": "Development Team",
                "document_purpose": "persuasive",
                "formality_level": "semi_formal",
                "confidence": 0.78,
                "supporting_evidence": ["feature descriptions", "user stories", "business value"],
                "key_topics": ["product features", "user experience", "market fit"],
                "writing_style": "persuasive and structured",
                "complexity_level": "intermediate"
            })
        else:
            return json.dumps({
                "document_type": "general_document",
                "scenario": "General Document",
                "author_role": "General Author",
                "target_audience": "General Audience",
                "document_purpose": "informational",
                "formality_level": "neutral",
                "confidence": 0.6,
                "supporting_evidence": ["general content"],
                "key_topics": ["various topics"],
                "writing_style": "standard",
                "complexity_level": "intermediate"
            })

def test_enhanced_scenario_inference():
    """测试增强场景推断引擎的各种功能"""
    
    print("🚀 测试增强场景推断引擎")
    print("=" * 50)
    
    # 初始化模拟LLM客户端和推断引擎
    mock_llm = MockLLMClient()
    inference_engine = EnhancedScenarioInferenceModule(mock_llm)
    
    # 测试文档
    test_documents = [
        {
            "name": "技术报告",
            "content": """
# 人工智能文档处理系统技术报告

## 1. 项目概述
本项目旨在开发一个基于AI的智能文档处理系统，能够自动分析、优化和生成办公文档。

## 2. 技术方案
### 2.1 系统架构
系统采用模块化设计，主要包括：
- 文档解析模块
- 场景推断引擎
- 内容生成器
- 虚拟审稿系统

### 2.2 核心算法
我们使用了以下先进技术：
- 自然语言处理 (NLP)
- 机器学习 (ML)
- 深度学习 (DL)

## 3. 实验结果
经过测试，系统在文档分类方面达到了95.2%的准确率。

## 4. 结论
本系统成功实现了智能化文档处理的目标。
            """
        },
        {
            "name": "产品提案",
            "content": """
# 智能办公助手产品提案

## 产品概述
我们计划开发一款革命性的智能办公助手，帮助用户提高工作效率。

## 核心功能
1. 智能文档处理
2. 自动化工作流
3. 智能日程管理
4. 团队协作工具

## 用户故事
作为一名办公室工作人员，我希望能够快速处理大量文档，以便节省时间专注于更重要的工作。

## 商业价值
- 提高工作效率30%
- 减少人工错误
- 降低运营成本

## 开发计划
第一阶段：核心功能开发（3个月）
第二阶段：用户测试和优化（2个月）
第三阶段：正式发布（1个月）
            """
        },
        {
            "name": "会议纪要",
            "content": """
# 产品评审会议纪要

**会议时间**: 2024年1月15日 14:00-16:00
**参会人员**: 张三(产品经理)、李四(技术负责人)、王五(设计师)

## 会议议程
1. 产品功能评审
2. 技术方案讨论
3. 设计稿确认
4. 下一步计划

## 讨论要点
- 用户界面需要进一步优化
- 后端API性能需要提升
- 移动端适配问题

## 决策事项
1. 采用新的UI设计方案
2. 优化数据库查询性能
3. 增加移动端支持

## 行动项
- 张三：更新产品需求文档 (截止日期：1月20日)
- 李四：优化API性能 (截止日期：1月25日)
- 王五：完成移动端设计 (截止日期：1月22日)
            """
        }
    ]
    
    # 测试每个文档
    for i, doc in enumerate(test_documents, 1):
        print(f"\n📄 测试文档 {i}: {doc['name']}")
        print("-" * 40)
        
        try:
            # 执行场景推断
            result = inference_engine.infer_scenario_and_roles(doc['content'])
            
            if "error" in result:
                print(f"❌ 推断失败: {result['error']}")
                continue
            
            print(f"✅ 推断完成")
            print(f"📋 文档类型: {result.get('document_type', 'Unknown')}")
            print(f"🎯 应用场景: {result.get('scenario', 'Unknown')}")
            print(f"👤 作者角色: {result.get('author_role', 'Unknown')}")
            print(f"👥 目标读者: {result.get('target_audience', 'Unknown')}")
            print(f"🎨 文档目的: {result.get('document_purpose', 'Unknown')}")
            print(f"📝 正式程度: {result.get('formality_level', 'Unknown')}")
            
            # 显示置信度分数
            confidence_scores = result.get('confidence_scores', {})
            if confidence_scores:
                print(f"📊 置信度分数:")
                for metric, score in confidence_scores.items():
                    print(f"   - {metric}: {score:.2%}")
            
            # 显示支持证据
            evidence = result.get('supporting_evidence', [])
            if evidence:
                print(f"🔍 支持证据:")
                for ev in evidence[:3]:  # 只显示前3个
                    print(f"   - {ev}")
                if len(evidence) > 3:
                    print(f"   - ... 还有 {len(evidence) - 3} 个证据")
            
            # 显示备选场景
            alternatives = result.get('alternative_scenarios', [])
            if alternatives:
                print(f"🔄 备选场景:")
                for alt in alternatives:
                    print(f"   - {alt['scenario']} (置信度: {alt['confidence']:.2%})")
            
            # 生成用户确认提示
            print(f"\n💬 用户确认提示:")
            confirmation_prompt = inference_engine.generate_enhanced_confirmation_prompt(result)
            print(confirmation_prompt)
            
            # 验证推断质量
            quality_report = inference_engine.validate_inference_quality(result)
            print(f"🔍 质量评估:")
            print(f"   - 整体质量: {quality_report['overall_quality']}")
            print(f"   - 置信度评估: {quality_report['confidence_assessment']}")
            print(f"   - 证据强度: {quality_report['evidence_strength']}")
            print(f"   - 一致性检查: {quality_report['consistency_check']}")
            
            if quality_report['improvement_suggestions']:
                print(f"   💡 改进建议:")
                for suggestion in quality_report['improvement_suggestions']:
                    print(f"      - {suggestion}")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print(f"\n🎉 测试完成!")

def test_scenario_recommendations():
    """测试场景推荐功能"""
    
    print(f"\n🔧 测试场景推荐功能")
    print("-" * 30)
    
    mock_llm = MockLLMClient()
    inference_engine = EnhancedScenarioInferenceModule(mock_llm)
    
    # 测试已知场景
    test_scenarios = ["Product Proposal", "Technical Report", "Market Analysis"]
    
    for scenario in test_scenarios:
        print(f"\n📋 场景: {scenario}")
        recommendations = inference_engine.get_scenario_recommendations(scenario)
        
        if "error" in recommendations:
            print(f"❌ {recommendations['error']}")
        else:
            print(f"✅ 推荐的审阅角色: {recommendations.get('recommended_reviewer_roles', [])}")
            print(f"🎯 默认审阅重点: {recommendations.get('default_review_focus', [])}")

if __name__ == "__main__":
    test_enhanced_scenario_inference()
    test_scenario_recommendations()
