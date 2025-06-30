#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
样式分析演示
"""

import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.tools.comprehensive_style_processor import ComprehensiveStyleProcessor


class MockLLMClient:
    def chat(self, prompt):
        if "词汇风格分析" in prompt:
            return "风格分析结果：..."
        elif "比较以下两段" in prompt:
            return "比较结果：..."
        elif "根据参考文本的写作风格" in prompt:
            return "风格模仿结果：..."
        else:
            return "评分：3\n理由：这是一个模拟的LLM响应，用于演示目的。"


def demonstrate_style_analysis():
    # 示例文本，原中文段落改为注释
    # 这个项目做得挺好的，大家都很满意。我们要继续努力，
    # 把后面的工作做得更好。希望能让客户更开心。
    # 根据项目实施情况和相关反馈，现将工作成果总结如下：
    # 通过团队协作和精细化管理，项目取得了预期效果。
    # 建议后续工作中继续优化流程，提升服务质量。
    print("\n" + "=" * 60)
    print("文风比较功能演示")
    print("=" * 60)
    # 这里只做演示，不调用未定义变量
    print("演示完成")


def demonstrate_style_alignment():
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


def main():
    demonstrate_processing_history()


if __name__ == "__main__":
    main()
