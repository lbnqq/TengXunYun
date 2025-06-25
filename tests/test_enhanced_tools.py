#!/usr/bin/env python3
"""
测试增强工具功能
Test enhanced tools functionality
"""

import sys
import os
import json

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_enhanced_style_generator():
    """测试增强样式生成器"""
    print("🎨 测试增强样式生成器")
    print("-" * 40)
    
    try:
        from src.core.tools.style_generator import EnhancedStyleGeneratorTool
        
        # 创建样式生成器（不需要LLM客户端进行基础测试）
        style_generator = EnhancedStyleGeneratorTool(llm_client=None)
        
        # 测试文本
        test_text = """
        This is a test document. We need to check if the style transformation works properly.
        The system should be able to convert this text to different styles effectively.
        """
        
        # 测试样式转换
        print("  📝 测试样式转换...")
        result = style_generator.transform_style(
            text_content=test_text,
            target_style="professional"
        )
        
        if result.get("success"):
            print("    ✅ 样式转换成功")
            print(f"    - 原始文本长度: {len(result['original_text'])} 字符")
            print(f"    - 转换后长度: {len(result['rewritten_text'])} 字符")
            print(f"    - 目标样式: {result['target_style']}")
            print(f"    - 转换方法: {result.get('transformation_method', 'LLM')}")
        else:
            print(f"    ❌ 样式转换失败: {result.get('error')}")
        
        # 测试样式分析
        print("  🔍 测试样式分析...")
        analysis_result = style_generator.analyze_style(test_text)
        
        if analysis_result.get("success"):
            print("    ✅ 样式分析成功")
            analysis = analysis_result["style_analysis"]
            print(f"    - 推测样式: {analysis.get('likely_style')}")
            print(f"    - 平均句长: {analysis.get('avg_sentence_length', 0):.1f} 词")
            print(f"    - 包含缩写: {analysis.get('has_contractions')}")
        else:
            print(f"    ❌ 样式分析失败: {analysis_result.get('error')}")
        
        # 测试样式比较
        print("  ⚖️ 测试样式比较...")
        comparison_result = style_generator.compare_styles(
            text_content=test_text,
            styles_to_compare=["professional", "casual", "technical"]
        )
        
        if comparison_result.get("success"):
            print("    ✅ 样式比较成功")
            comparisons = comparison_result["style_comparisons"]
            print(f"    - 比较了 {len(comparisons)} 种样式")
            for style, data in comparisons.items():
                if "suitability_score" in data:
                    print(f"      * {style}: 适合度 {data['suitability_score']:.2f}")
        else:
            print(f"    ❌ 样式比较失败: {comparison_result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ 样式生成器测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_enhanced_virtual_reviewer():
    """测试增强虚拟审阅器"""
    print("\n👥 测试增强虚拟审阅器")
    print("-" * 40)
    
    try:
        from src.core.tools.virtual_reviewer import EnhancedVirtualReviewerTool
        
        # 模拟知识库
        mock_kb = {
            "roles": [
                {
                    "role_name": "technical_reviewer",
                    "background": "Senior software engineer with 10+ years experience in system architecture and code review."
                },
                {
                    "role_name": "business_analyst", 
                    "background": "Business analyst specializing in requirements analysis and stakeholder management."
                }
            ]
        }
        
        # 创建虚拟审阅器
        reviewer = EnhancedVirtualReviewerTool(llm_client=None, knowledge_base=mock_kb)
        
        # 测试文档
        test_document = """
        # Project Proposal: AI Document Processing System
        
        ## Overview
        This project aims to develop an AI-powered document processing system.
        
        ## Technical Approach
        We will use machine learning algorithms to analyze documents.
        The system will include natural language processing capabilities.
        
        ## Business Value
        This system will improve efficiency and reduce manual work.
        Expected ROI is 200% within the first year.
        """
        
        # 测试单个审阅者
        print("  📋 测试技术审阅...")
        tech_review = reviewer.review_document(
            document_content=test_document,
            reviewer_role_name="technical_reviewer",
            review_focus="Technical feasibility and implementation"
        )
        
        if tech_review.get("success"):
            print("    ✅ 技术审阅成功")
            comments = tech_review["review_comments"]["comments"]
            print(f"    - 审阅意见数量: {len(comments)}")
            print(f"    - 质量评分: {tech_review['review_metrics']['quality_score']}")
            
            # 显示前几个意见
            for i, comment in enumerate(comments[:3]):
                print(f"      {i+1}. [{comment['severity']}] {comment['area']}: {comment['comment'][:80]}...")
        else:
            print(f"    ❌ 技术审阅失败: {tech_review.get('error')}")
        
        # 测试多审阅者会话
        print("  👥 测试多审阅者会话...")
        multi_review = reviewer.multi_reviewer_session(
            document_content=test_document,
            reviewer_roles=["technical_reviewer", "business_analyst"],
            review_focus="Overall project feasibility"
        )
        
        if multi_review.get("success"):
            print("    ✅ 多审阅者会话成功")
            session = multi_review["session_results"]
            print(f"    - 参与审阅者: {len(session['reviewer_results'])}")
            print(f"    - 共识水平: {session['consensus_analysis']['agreement_level']}")
            print(f"    - 总体建议: {session['session_summary']['overall_recommendation']}")
        else:
            print(f"    ❌ 多审阅者会话失败: {multi_review.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ 虚拟审阅器测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def test_enhanced_content_generator():
    """测试增强内容生成器"""
    print("\n📝 测试增强内容生成器")
    print("-" * 40)
    
    try:
        from src.core.tools.content_filler import EnhancedContentGeneratorTool
        
        # 创建内容生成器
        generator = EnhancedContentGeneratorTool(llm_client=None)
        
        # 测试模板填充
        print("  📋 测试模板填充...")
        template = """
        项目名称: {{project_name}}
        负责人: {{author}}
        开始日期: {{start_date}}
        
        项目描述:
        {{description}}
        
        预期成果:
        {{expected_outcomes}}
        """
        
        data = {
            "project_name": "AI文档处理系统",
            "author": "张三",
            "description": "开发一个智能文档处理平台"
        }
        
        fill_result = generator.fill_template(
            template_content=template,
            data=data,
            context={"document_type": "project_proposal"}
        )
        
        if fill_result.get("success"):
            print("    ✅ 模板填充成功")
            print(f"    - 占位符数量: {fill_result['placeholders_found']}")
            print(f"    - 填充比例: {fill_result['processing_metadata']['fill_ratio']:.2f}")
            print(f"    - 原始长度: {fill_result['processing_metadata']['template_length']}")
            print(f"    - 填充后长度: {fill_result['processing_metadata']['filled_length']}")
        else:
            print(f"    ❌ 模板填充失败: {fill_result.get('error')}")
        
        # 测试内容优化
        print("  🔧 测试内容优化...")
        test_content = """
        This is a very very long sentence that could be improved for clarity and it contains redundant words and phrases that should be optimized for better readability and user experience.
        """
        
        optimize_result = generator.optimize_content(
            content=test_content,
            optimization_goals=["clarity", "conciseness"]
        )
        
        if optimize_result.get("success"):
            print("    ✅ 内容优化成功")
            print(f"    - 原始长度: {optimize_result['original_length']}")
            print(f"    - 优化后长度: {optimize_result['optimized_length']}")
            print(f"    - 应用的优化: {len(optimize_result['optimizations_applied'])}")
        else:
            print(f"    ❌ 内容优化失败: {optimize_result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ 内容生成器测试失败: {e}")
        import traceback
        print(f"    详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始增强工具功能测试")
    print("=" * 60)
    
    tests = [
        ("增强样式生成器", test_enhanced_style_generator),
        ("增强虚拟审阅器", test_enhanced_virtual_reviewer),
        ("增强内容生成器", test_enhanced_content_generator)
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
    
    print("\n" + "=" * 60)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有增强工具测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
