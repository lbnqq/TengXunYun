"""
文风分析和对齐功能演示
展示如何使用综合文风处理器进行文风分析、比较和对齐
"""

import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.tools.comprehensive_style_processor import ComprehensiveStyleProcessor


class MockLLMClient:
    """模拟LLM客户端，用于演示"""
    
    def generate(self, prompt: str) -> str:
        """模拟LLM响应"""
        if "词汇风格分析" in prompt:
            return """
## 1. 词汇风格分析
评分：4
特征描述：词汇使用较为正式，包含专业术语和规范表达
典型词汇：根据、按照、实施、优化、提升

## 2. 句式结构分析  
评分：4
特征描述：句子结构较为复杂，多使用复合句和并列句
典型句式：通过...方式，实现...目标

## 3. 语气情感分析
评分：3
特征描述：语气较为客观、正式，情感色彩适中
情感倾向：中性

## 4. 表达方式分析
评分：4
特征描述：表达方式直接明确，逻辑性强
修辞手法：排比、对偶

## 5. 文本组织分析
评分：4
特征描述：结构清晰，层次分明，逻辑连贯
组织特点：总分结构，递进关系

## 6. 整体风格判断
主要风格类型：商务专业
风格强度：4
风格一致性：4

## 7. 风格特色总结
核心特征：正式、专业、逻辑清晰、结构完整
适用场景：商务报告、工作总结、项目方案
改进建议：可适当增加一些生动的表达方式
"""
        elif "比较以下两段" in prompt:
            return """
## 相似度评估
整体相似度：2
相似原因：都是中文文本，都有完整的句子结构

## 差异分析
### 词汇使用差异
文本A特点：使用较多正式词汇和专业术语
文本B特点：使用较多口语化表达和简单词汇
差异程度：4

### 句式结构差异  
文本A特点：句子较长，结构复杂，多用复合句
文本B特点：句子较短，结构简单，多用简单句
差异程度：4

### 语气情感差异
文本A特点：语气正式、客观，情感色彩较淡
文本B特点：语气随意、主观，情感色彩较浓
差异程度：3

## 风格迁移建议
如要将文本B改写为文本A的风格，需要：
1. 替换口语化词汇为正式词汇
2. 增加句子长度和复杂度
3. 调整语气为更加客观正式

## 总结
主要差异：正式程度和句式复杂度
风格距离：4
"""
        elif "根据参考文本的写作风格" in prompt:
            return """
### 重写结果：
根据相关要求和实际情况，我们需要进一步提升产品质量水平，持续改善客户服务体验，确保客户满意度的稳步提升。

### 调整说明：
1. 词汇调整：将"提高"改为"提升"，"增加"改为"改善"，增加了"根据相关要求"等正式表达
2. 句式调整：将简单句改为复合句，增加了修饰成分和逻辑连接
3. 语气调整：从直接表达改为更加正式、客观的表达方式
4. 其他调整：增加了"持续"、"确保"等体现专业性的词汇

### 对齐效果评估：
风格匹配度：4
内容保真度：5
语言流畅度：4
"""
        else:
            return "评分：3\n理由：这是一个模拟的LLM响应，用于演示目的。"


def demonstrate_style_analysis():
    """演示文风分析功能"""
    print("=" * 60)
    print("文风分析功能演示")
    print("=" * 60)
    
    # 初始化处理器
    mock_llm = MockLLMClient()
    processor = ComprehensiveStyleProcessor(
        llm_client=mock_llm,
        storage_path="demo_storage"
    )
    
    # 示例文本
    business_text = """
    根据公司第三季度业务发展情况，现将相关工作总结汇报如下：
    通过实施精细化管理策略，我们成功实现了销售业绩的稳步增长。
    具体而言，销售额较上季度增长15%，客户满意度提升至92%。
    建议下一阶段继续优化产品结构，加强市场推广力度，提升服务质量。
    """
    
    casual_text = """
    这个季度我们做得还不错！销售比上个季度多了15%，客户也挺满意的。
    大家都很努力，产品卖得挺好的。下次我们要继续加油，
    把产品做得更好，让更多客户喜欢我们的东西。
    """
    
    print("\n1. 提取商务文档的文风特征...")
    business_features = processor.extract_comprehensive_style_features(
        business_text, "商务报告"
    )
    
    if business_features.get("success"):
        print("✅ 商务文档特征提取成功")
        summary = business_features.get("processing_summary", {})
        print(f"   - 提取特征数量: {summary.get('features_extracted', 0)}")
        print(f"   - 使用的分析模块: {', '.join(summary.get('analysis_modules_used', []))}")
        print(f"   - 关键特征: {', '.join(summary.get('key_characteristics', []))}")
    else:
        print("❌ 商务文档特征提取失败")
        print(f"   错误: {business_features.get('error', '未知错误')}")
    
    print("\n2. 提取随意文档的文风特征...")
    casual_features = processor.extract_comprehensive_style_features(
        casual_text, "随意文档"
    )
    
    if casual_features.get("success"):
        print("✅ 随意文档特征提取成功")
        summary = casual_features.get("processing_summary", {})
        print(f"   - 提取特征数量: {summary.get('features_extracted', 0)}")
    else:
        print("❌ 随意文档特征提取失败")
    
    return business_features, casual_features


def demonstrate_style_comparison(business_features, casual_features):
    """演示文风比较功能"""
    print("\n" + "=" * 60)
    print("文风比较功能演示")
    print("=" * 60)
    
    mock_llm = MockLLMClient()
    processor = ComprehensiveStyleProcessor(llm_client=mock_llm)
    
    business_text = """
    根据公司第三季度业务发展情况，现将相关工作总结汇报如下：
    通过实施精细化管理策略，我们成功实现了销售业绩的稳步增长。
    """
    
    casual_text = """
    这个季度我们做得还不错！销售比上个季度多了15%，客户也挺满意的。
    """
    
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
    """演示文风对齐功能"""
    print("\n" + "=" * 60)
    print("文风对齐功能演示")
    print("=" * 60)
    
    mock_llm = MockLLMClient()
    processor = ComprehensiveStyleProcessor(llm_client=mock_llm)
    
    # 源文档（随意风格）
    source_text = """
    这个项目做得挺好的，大家都很满意。我们要继续努力，
    把后面的工作做得更好。希望能让客户更开心。
    """
    
    # 目标文档（正式风格）
    target_text = """
    根据项目实施情况和相关反馈，现将工作成果总结如下：
    通过团队协作和精细化管理，项目取得了预期效果。
    建议后续工作中继续优化流程，提升服务质量。
    """
    
    # 需要对齐的内容
    content_to_align = "我们要提高产品质量，让客户更满意。"
    
    print(f"\n原始内容: {content_to_align}")
    print("正在执行文风对齐...")
    
    alignment_result = processor.align_text_style(
        source_text, target_text, content_to_align,
        "随意文档", "正式文档"
    )
    
    if alignment_result.get("success"):
        print("✅ 文风对齐成功")
        
        aligned_content = alignment_result.get("aligned_content", "")
        print(f"对齐后内容: {aligned_content}")
        
        quality = alignment_result.get("quality_assessment", {})
        if quality:
            print(f"\n质量评估:")
            print(f"   - 内容保持度: {quality.get('content_preservation', 0):.3f}")
            print(f"   - 风格对齐度: {quality.get('style_alignment', 0):.3f}")
            print(f"   - 语言流畅度: {quality.get('fluency', 0):.3f}")
            print(f"   - 整体质量: {quality.get('overall_quality', 0):.3f}")
    else:
        print("❌ 文风对齐失败")
        print(f"   错误: {alignment_result.get('error', '未知错误')}")
    
    return alignment_result


def demonstrate_batch_processing():
    """演示批量处理功能"""
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
    """演示处理历史功能"""
    print("\n" + "=" * 60)
    print("处理历史功能演示")
    print("=" * 60)
    
    mock_llm = MockLLMClient()
    processor = ComprehensiveStyleProcessor(llm_client=mock_llm)
    
    # 执行几次处理以生成历史记录
    test_texts = [
        "这是历史记录测试文档1。",
        "这是历史记录测试文档2。",
        "这是历史记录测试文档3。"
    ]
    
    print("正在生成处理历史...")
    for i, text in enumerate(test_texts):
        processor.extract_comprehensive_style_features(text, f"历史测试{i+1}")
    
    # 获取处理历史
    history = processor.get_processing_history()
    
    print(f"✅ 处理历史记录: {len(history)} 条")
    
    if history:
        print("\n最近的处理记录:")
        for i, entry in enumerate(history[-3:]):  # 显示最近3条
            print(f"   {i+1}. {entry.get('document_name', '未知')} "
                  f"({entry.get('processing_time', '未知时间')[:19]})")
            print(f"      文本长度: {entry.get('text_length', 0)} 字符")
            print(f"      特征数量: {entry.get('features_count', 0)}")
            print(f"      处理状态: {'成功' if entry.get('success') else '失败'}")
    
    return history


def main():
    """主演示函数"""
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
