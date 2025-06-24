#!/usr/bin/env python3
"""
测试增强文档解析器的功能
Test script for the Enhanced Document Parser
"""

import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.tools.document_parser import EnhancedDocumentParserTool

def test_enhanced_parser():
    """测试增强文档解析器的各种功能"""
    
    print("🚀 测试增强文档解析器")
    print("=" * 50)
    
    # 初始化解析器
    parser = EnhancedDocumentParserTool()
    
    # 测试文档路径
    test_doc_path = "test_document.txt"
    
    if not os.path.exists(test_doc_path):
        print(f"❌ 测试文档 {test_doc_path} 不存在")
        return
    
    print(f"📄 解析文档: {test_doc_path}")
    print()
    
    # 测试不同深度的分析
    analysis_depths = ["basic", "standard", "deep"]
    
    for depth in analysis_depths:
        print(f"🔍 执行 {depth.upper()} 级别分析...")
        print("-" * 30)
        
        try:
            result = parser.execute(test_doc_path, analysis_depth=depth)
            
            if "error" in result:
                print(f"❌ 错误: {result['error']}")
                continue
            
            print(f"✅ 分析完成 - 深度: {result.get('analysis_depth', 'unknown')}")
            
            # 显示基本信息
            if "text_content" in result:
                content_length = len(result["text_content"])
                print(f"📝 文档内容长度: {content_length} 字符")
            
            # 显示结构信息
            if "basic_structure" in result:
                structure = result["basic_structure"]
                print(f"📊 基本结构:")
                for key, value in structure.items():
                    if isinstance(value, (int, str, bool)):
                        print(f"   - {key}: {value}")
            
            # 显示结构化分析
            if "structural_analysis" in result:
                struct_analysis = result["structural_analysis"]
                print(f"🏗️  结构化分析:")
                print(f"   - 标题数量: {len(struct_analysis.get('headings', []))}")
                print(f"   - 段落数量: {len(struct_analysis.get('paragraphs', []))}")
                print(f"   - 列表项数量: {len(struct_analysis.get('lists', []))}")
                print(f"   - 表格行数量: {len(struct_analysis.get('tables', []))}")
                
                # 显示文档树结构
                if struct_analysis.get("document_tree"):
                    print(f"🌳 文档树结构:")
                    for i, node in enumerate(struct_analysis["document_tree"][:3]):  # 只显示前3个
                        print(f"   {i+1}. {node['text']} (级别 {node['level']})")
                        if node.get('children'):
                            for child in node['children'][:2]:  # 只显示前2个子节点
                                print(f"      - {child['text']}")
            
            # 显示关键信息
            if "key_information" in result:
                key_info = result["key_information"]
                print(f"🔑 关键信息:")
                
                # 显示统计信息
                if "statistics" in key_info:
                    stats = key_info["statistics"]
                    print(f"   📈 统计:")
                    print(f"      - 总词数: {stats.get('total_words', 0)}")
                    print(f"      - 唯一词数: {stats.get('unique_words', 0)}")
                    print(f"      - 段落数: {stats.get('total_paragraphs', 0)}")
                
                # 显示关键词
                if "keywords" in key_info and key_info["keywords"]:
                    print(f"   🏷️  关键词 (前5个):")
                    for kw in key_info["keywords"][:5]:
                        print(f"      - {kw['word']} (频率: {kw['frequency']})")
                
                # 显示实体
                if "entities" in key_info and key_info["entities"]:
                    print(f"   🏢 实体 (前5个):")
                    for entity in key_info["entities"][:5]:
                        print(f"      - {entity['entity']} (频率: {entity['frequency']})")
            
            # 显示深度分析结果
            if depth == "deep":
                if "content_patterns" in result:
                    patterns = result["content_patterns"]
                    print(f"🔍 内容模式:")
                    print(f"   - 有引言: {patterns.get('has_introduction', False)}")
                    print(f"   - 有结论: {patterns.get('has_conclusion', False)}")
                    print(f"   - 有方法论: {patterns.get('has_methodology', False)}")
                    print(f"   - 问题数量: {patterns.get('question_count', 0)}")
                    print(f"   - 感叹号数量: {patterns.get('exclamation_count', 0)}")
                
                if "document_characteristics" in result:
                    chars = result["document_characteristics"]
                    print(f"📋 文档特征:")
                    print(f"   - 文档长度: {chars.get('document_length', 'unknown')}")
                    print(f"   - 结构复杂度: {chars.get('structure_complexity', 'unknown')}")
                    print(f"   - 内容密度: {chars.get('content_density', 'unknown')}")
                    print(f"   - 正式程度: {chars.get('formality_level', 'unknown')}")
                    print(f"   - 技术水平: {chars.get('technical_level', 'unknown')}")
                
                if "writing_style" in result:
                    style = result["writing_style"]
                    print(f"✍️  写作风格:")
                    print(f"   - 平均句长: {style.get('average_sentence_length', 0)} 词")
                    print(f"   - 词汇复杂度: {style.get('vocabulary_complexity', 0):.3f}")
                    print(f"   - 问句比例: {style.get('question_ratio', 0):.3f}")
                    
                    if "style_indicators" in style:
                        indicators = style["style_indicators"]
                        print(f"   - 风格指标:")
                        print(f"     * 简洁: {indicators.get('concise', False)}")
                        print(f"     * 复杂: {indicators.get('complex', False)}")
                        print(f"     * 互动性: {indicators.get('interactive', False)}")
                        print(f"     * 强调性: {indicators.get('emphatic', False)}")
            
            print()
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            print()
    
    print("🎉 测试完成!")

def create_sample_document():
    """创建一个示例文档用于测试"""
    sample_content = """# 人工智能文档处理系统技术报告

## 1. 项目概述

本项目旨在开发一个基于AI的智能文档处理系统，能够自动分析、优化和生成办公文档。

### 1.1 背景

随着数字化办公的普及，文档处理效率成为企业关注的重点。传统的文档处理方式存在以下问题：

- 人工处理效率低下
- 格式不统一
- 质量参差不齐
- 审阅流程繁琐

### 1.2 目标

我们的目标是构建一个智能化的文档处理平台，具备以下核心能力：

1. 深度文档理解
2. 智能场景推断
3. 自动内容生成
4. 虚拟角色审稿

## 2. 技术方案

### 2.1 系统架构

系统采用模块化设计，主要包括：

- 文档解析模块
- 场景推断引擎
- 内容生成器
- 虚拟审稿系统

### 2.2 核心算法

我们使用了以下先进技术：

* 自然语言处理 (NLP)
* 机器学习 (ML)
* 深度学习 (DL)
* 知识图谱 (KG)

## 3. 实验结果

经过测试，系统在以下方面表现优异：

| 指标 | 准确率 | 召回率 | F1分数 |
|------|--------|--------|--------|
| 文档分类 | 95.2% | 93.8% | 94.5% |
| 内容生成 | 89.7% | 91.3% | 90.5% |
| 质量评估 | 92.1% | 88.9% | 90.5% |

## 4. 结论

本系统成功实现了智能化文档处理的目标，为企业数字化转型提供了有力支撑。

### 4.1 主要贡献

1. 提出了创新的文档理解框架
2. 实现了高精度的场景推断算法
3. 构建了多角色虚拟审稿系统

### 4.2 未来工作

- 扩展支持更多文档格式
- 优化算法性能
- 增强用户体验

---

**参考文献**

1. Smith, J. (2023). "AI in Document Processing". Journal of AI Research.
2. 张三 (2023). "智能文档系统设计". 计算机科学杂志.

**联系方式**: ai-team@company.com
"""
    
    with open("test_document.txt", "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print("📝 已创建示例文档: test_document.txt")

if __name__ == "__main__":
    # 如果测试文档不存在，创建一个
    if not os.path.exists("test_document.txt"):
        create_sample_document()
    
    # 运行测试
    test_enhanced_parser()
