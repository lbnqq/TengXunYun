#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
样式分析演示

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""











import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.tools.comprehensive_style_processor import ComprehensiveStyleProcessor


class MockLLMClient:
        if "词汇风格分析" in prompt:
        elif "比较以下两段" in prompt:
        elif "根据参考文本的写作风格" in prompt:
        else:
            return "评分：3\n理由：这是一个模拟的LLM响应，用于演示目的。"


def demonstrate_style_analysis():
    根据公司第三季度业务发展情况，现将相关工作总结汇报如下：
    通过实施精细化管理策略，我们成功实现了销售业绩的稳步增长。
    具体而言，销售额较上季度增长15%，客户满意度提升至92%。
    建议下一阶段继续优化产品结构，加强市场推广力度，提升服务质量。
    这个季度我们做得还不错！销售比上个季度多了15%，客户也挺满意的。
    大家都很努力，产品卖得挺好的。下次我们要继续加油，
    把产品做得更好，让更多客户喜欢我们的东西。
    print("\n" + "=" * 60)
    print("文风比较功能演示")
    print("=" * 60)
    
    mock_llm = MockLLMClient()
    processor = ComprehensiveStyleProcessor(llm_client=mock_llm)
    
    
    
    print("\n正在比较两种文风...")
    comparison_result = processor.compare_document_styles(
        business_text, casual_text, "商务文档", "随意文档"
    )
    
    if comparison_result.get("success"):
        print("✅ 文风比较成功")
        
        summary = comparison_result.get("comparison_summary", {})
        print(f"   - 相似度分数: {summary.get('similarity_score', 0):.3f}")
        print(f"   - 风格距离: {summary.get('style_distance', '未知')}")
        print(f"   - 主要差异: {', '.join(summary.get('main_differences', []))}")
        
        # 显示详细的相似度分析
        similarity = comparison_result.get("similarity_analysis", {})
        if similarity.get("success"):
            print(f"   - 特征向量距离: {similarity.get('distance', 0):.3f}")
            feature_comp = similarity.get("feature_comparison", {})
            print(f"   - 平均特征差异: {feature_comp.get('mean_difference', 0):.3f}")
    else:
        print("❌ 文风比较失败")
        print(f"   错误: {comparison_result.get('error', '未知错误')}")
    
    return comparison_result


def demonstrate_style_alignment():
    这个项目做得挺好的，大家都很满意。我们要继续努力，
    把后面的工作做得更好。希望能让客户更开心。
    根据项目实施情况和相关反馈，现将工作成果总结如下：
    通过团队协作和精细化管理，项目取得了预期效果。
    建议后续工作中继续优化流程，提升服务质量。
    print("\n" + "=" * 60)
    print("批量处理功能演示")
    print("=" * 60)
    
    mock_llm = MockLLMClient()
    processor = ComprehensiveStyleProcessor(llm_client=mock_llm)
    
    # 准备多个文档
    documents = [
        {
            "text": "这是第一个测试文档，用于验证批量处理功能。",
            "name": "测试文档1"
        },
        {
            "text": "根据相关规定，现将第二个文档的内容汇报如下。",
            "name": "正式文档2"
        },
        {
            "text": "第三个文档比较随意，就是想看看效果怎么样。",
            "name": "随意文档3"
        }
    ]
    
    print(f"正在批量处理 {len(documents)} 个文档...")
    
    batch_result = processor.batch_process_documents(documents, "extract")
    
    if batch_result:
        print("✅ 批量处理完成")
        
        summary = batch_result.get("batch_summary", {})
        print(f"   - 总文档数: {batch_result.get('total_documents', 0)}")
        print(f"   - 成功处理: {batch_result.get('successful_processes', 0)}")
        print(f"   - 处理失败: {batch_result.get('failed_processes', 0)}")
        print(f"   - 成功率: {summary.get('success_rate', 0):.1%}")
        
        # 显示每个文档的处理结果
        print("\n各文档处理结果:")
        for i, result in enumerate(batch_result.get("processing_results", [])):
            doc_name = result.get("document_name", f"文档{i+1}")
            success = "✅" if result.get("success") else "❌"
            print(f"   {success} {doc_name}")
    else:
        print("❌ 批量处理失败")
    
    return batch_result


def demonstrate_processing_history():
    print("🎯 综合文风处理器功能演示")
    print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 文风分析演示
        business_features, casual_features = demonstrate_style_analysis()
        
        # 2. 文风比较演示
        comparison_result = demonstrate_style_comparison(business_features, casual_features)
        
        # 3. 文风对齐演示
        alignment_result = demonstrate_style_alignment()
        
        # 4. 批量处理演示
        batch_result = demonstrate_batch_processing()
        
        # 5. 处理历史演示
        history = demonstrate_processing_history()
        
        print("\n" + "=" * 60)
        print("演示总结")
        print("=" * 60)
        print("✅ 所有功能演示完成")
        print("📊 演示涵盖的功能:")
        print("   - 综合文风特征提取")
        print("   - 文档风格比较分析")
        print("   - 智能文风对齐")
        print("   - 批量文档处理")
        print("   - 处理历史管理")
        
        print("\n💡 使用建议:")
        print("   1. 确保安装所需依赖包 (jieba, scikit-learn)")
        print("   2. 配置合适的LLM客户端以获得最佳效果")
        print("   3. 根据具体需求调整特征权重和融合策略")
        print("   4. 定期清理存储目录以节省空间")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {str(e)}")
        print("请检查依赖包安装和配置是否正确")


if __name__ == "__main__":
    main()
