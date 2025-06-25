#!/usr/bin/env python3
"""
测试智能引导系统功能
Test intelligent guidance system functionality
"""

import sys
import os
import json

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_scenario_inference():
    """测试场景推断功能"""
    print("🧠 测试场景推断功能")
    print("-" * 40)
    
    try:
        from src.core.guidance import EnhancedScenarioInferenceModule
        
        # 创建场景推断模块（不需要LLM客户端进行基础测试）
        inference_module = EnhancedScenarioInferenceModule(llm_client=None)
        
        # 测试文档样本
        test_documents = {
            "技术报告": """
            # 系统性能分析报告
            
            ## 摘要
            本报告分析了新系统的性能指标和优化建议。
            
            ## 方法论
            我们使用了基准测试和负载测试来评估系统性能。
            
            ## 实验结果
            测试结果显示系统在高负载下的响应时间为50ms。
            
            ## 结论
            系统性能满足预期要求，建议进一步优化数据库查询。
            """,
            
            "产品提案": """
            # 新产品开发提案
            
            ## 产品概述
            我们提议开发一个AI驱动的客户服务平台。
            
            ## 用户故事
            作为客户服务代表，我希望能够快速获得客户问题的智能建议。
            
            ## 技术栈
            前端使用React，后端使用Python Flask，AI模型使用GPT。
            
            ## 开发计划
            预计6个月完成MVP，需要5名开发人员。
            
            ## 商业价值
            预期能够提高客户满意度30%，降低服务成本20%。
            """,
            
            "会议纪要": """
            # 项目进度会议纪要
            
            ## 参会人员
            - 张三（项目经理）
            - 李四（技术负责人）
            - 王五（产品经理）
            
            ## 会议议程
            1. 项目进度回顾
            2. 技术难点讨论
            3. 下周计划
            
            ## 讨论要点
            - 当前进度符合预期
            - 数据库性能需要优化
            - 前端界面需要调整
            
            ## 决策事项
            - 增加一名数据库专家
            - 调整UI设计方案
            
            ## 行动项
            - 张三：联系HR招聘数据库专家（本周五前）
            - 李四：完成数据库优化方案（下周三前）
            - 王五：提供新的UI设计稿（下周一前）
            """
        }
        
        # 测试每个文档的场景推断
        for doc_type, content in test_documents.items():
            print(f"  📄 测试文档类型: {doc_type}")
            
            # 执行场景推断
            result = inference_module.infer_scenario_and_roles(content)
            
            if "error" in result:
                print(f"    ❌ 推断失败: {result['error']}")
                continue
            
            print(f"    ✅ 推断成功")
            print(f"    - 文档类型: {result.get('document_type', 'unknown')}")
            print(f"    - 场景: {result.get('scenario', 'unknown')}")
            print(f"    - 作者角色: {result.get('author_role', 'unknown')}")
            print(f"    - 目标受众: {result.get('target_audience', 'unknown')}")
            print(f"    - 文档目的: {result.get('document_purpose', 'unknown')}")
            print(f"    - 正式程度: {result.get('formality_level', 'unknown')}")
            
            # 显示置信度
            confidence_scores = result.get('confidence_scores', {})
            overall_confidence = confidence_scores.get('overall', 0.0)
            print(f"    - 整体置信度: {overall_confidence:.2f}")
            
            # 显示支持证据
            evidence = result.get('supporting_evidence', [])
            if evidence:
                print(f"    - 支持证据: {', '.join(evidence[:3])}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"    ❌ 场景推断测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_scenario_recommendations():
    """测试场景建议功能"""
    print("💡 测试场景建议功能")
    print("-" * 40)
    
    try:
        from src.core.guidance import EnhancedScenarioInferenceModule
        
        inference_module = EnhancedScenarioInferenceModule(llm_client=None)
        
        # 测试不同场景的建议
        test_scenarios = [
            "Technical Report",
            "Product Proposal", 
            "Meeting Minutes",
            "Business Plan",
            "Research Paper"
        ]
        
        for scenario in test_scenarios:
            print(f"  📋 测试场景: {scenario}")
            
            # 获取场景建议
            recommendations = inference_module.get_scenario_recommendations(scenario)
            
            if "error" in recommendations:
                print(f"    ❌ 获取建议失败: {recommendations['error']}")
                continue
            
            print(f"    ✅ 获取建议成功")
            print(f"    - 描述: {recommendations.get('description', 'N/A')}")
            print(f"    - 推荐审阅角色: {', '.join(recommendations.get('recommended_reviewer_roles', []))}")
            print(f"    - 默认审阅重点: {', '.join(recommendations.get('default_review_focus', []))}")
            print(f"    - 建议工具: {', '.join(recommendations.get('suggested_tools', []))}")
            
            # 获取下一步建议
            next_steps = inference_module.suggest_next_steps_and_roles(scenario)
            print(f"    - 下一步建议: {next_steps.get('suggestion', 'N/A')}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"    ❌ 场景建议测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_confirmation_prompts():
    """测试确认提示生成"""
    print("💬 测试确认提示生成")
    print("-" * 40)
    
    try:
        from src.core.guidance import EnhancedScenarioInferenceModule
        
        inference_module = EnhancedScenarioInferenceModule(llm_client=None)
        
        # 模拟推断结果
        mock_inference_result = {
            "scenario": "Technical Report",
            "author_role": "technical_lead",
            "target_audience": "technical_team",
            "confidence_scores": {"overall": 0.85},
            "supporting_evidence": [
                "Contains technical terminology",
                "Includes performance metrics",
                "Has methodology section"
            ],
            "alternative_scenarios": [
                {"scenario": "Research Paper", "confidence": 0.72}
            ]
        }
        
        # 生成增强确认提示
        print("  📝 生成增强确认提示...")
        enhanced_prompt = inference_module.generate_enhanced_confirmation_prompt(mock_inference_result)
        
        print("    ✅ 增强提示生成成功")
        print("    提示内容:")
        print("    " + "\n    ".join(enhanced_prompt.split("\n")[:10]))  # 显示前10行
        print("    ...")
        
        # 生成传统确认提示（向后兼容）
        print("  📝 生成传统确认提示...")
        traditional_prompt = inference_module.generate_user_confirmation_prompt({
            "inferred_scenario": "Technical Report",
            "supporting_evidence": "technical terminology and performance metrics",
            "inferred_reporter_role": "Technical Lead",
            "inferred_reader_role": "Technical Team"
        })
        
        print("    ✅ 传统提示生成成功")
        print("    提示内容:")
        print("    " + "\n    ".join(traditional_prompt.split("\n")[:5]))  # 显示前5行
        
        return True
        
    except Exception as e:
        print(f"    ❌ 确认提示测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_inference_quality_validation():
    """测试推断质量验证"""
    print("🔍 测试推断质量验证")
    print("-" * 40)
    
    try:
        from src.core.guidance import EnhancedScenarioInferenceModule
        
        inference_module = EnhancedScenarioInferenceModule(llm_client=None)
        
        # 测试不同质量的推断结果
        test_cases = [
            {
                "name": "高质量推断",
                "result": {
                    "confidence_scores": {"overall": 0.9},
                    "supporting_evidence": ["evidence1", "evidence2", "evidence3", "evidence4"],
                    "alternative_scenarios": []
                }
            },
            {
                "name": "中等质量推断",
                "result": {
                    "confidence_scores": {"overall": 0.6},
                    "supporting_evidence": ["evidence1", "evidence2"],
                    "alternative_scenarios": [{"confidence": 0.5}]
                }
            },
            {
                "name": "低质量推断",
                "result": {
                    "confidence_scores": {"overall": 0.3},
                    "supporting_evidence": ["evidence1"],
                    "alternative_scenarios": [{"confidence": 0.25}]
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"  📊 测试: {test_case['name']}")
            
            quality_report = inference_module.validate_inference_quality(test_case["result"])
            
            print(f"    - 整体质量: {quality_report['overall_quality']}")
            print(f"    - 置信度评估: {quality_report['confidence_assessment']}")
            print(f"    - 证据强度: {quality_report['evidence_strength']}")
            print(f"    - 一致性检查: {quality_report['consistency_check']}")
            
            if quality_report["improvement_suggestions"]:
                print(f"    - 改进建议: {', '.join(quality_report['improvement_suggestions'])}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"    ❌ 质量验证测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始智能引导系统测试")
    print("=" * 60)
    
    tests = [
        ("场景推断", test_scenario_inference),
        ("场景建议", test_scenario_recommendations),
        ("确认提示", test_confirmation_prompts),
        ("质量验证", test_inference_quality_validation)
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
        print("🎉 所有智能引导系统测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
