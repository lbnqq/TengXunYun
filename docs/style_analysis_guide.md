# 文风特征提取与对齐功能指南

## 概述

本系统实现了基于LLM和开源库相结合的中文文风特征提取和对齐功能，能够全面分析文档的写作风格，并实现智能的文风对齐和转换。

## 核心特性

### 🔍 综合特征提取
- **量化特征提取**: 使用jieba等开源库进行词汇、句法、标点符号的精确统计分析
- **深度特征提取**: 利用LLM进行风格评分、情感分析、修辞识别等高级分析
- **特征融合**: 整合多维度特征，生成综合的文风特征向量

### 📊 文风分析维度
- **词汇风格**: TTR、词长分布、正式程度、专业术语使用
- **句法结构**: 句长分布、复合句比例、句式多样性
- **表达方式**: 语气强度、情感色彩、修辞手法
- **文本组织**: 段落结构、逻辑连接、过渡方式
- **语言习惯**: 口语化程度、书面语规范、行业特色

### 🎯 智能对齐功能
- **风格相似度计算**: 多种距离度量方法
- **智能风格迁移**: 基于LLM的文风转换
- **质量评估**: 内容保真度、风格匹配度、语言流畅度

## 系统架构

```
综合文风处理器 (ComprehensiveStyleProcessor)
├── 增强特征提取器 (EnhancedStyleExtractor)
│   ├── 量化特征提取器 (QuantitativeFeatureExtractor)
│   └── LLM风格分析器 (LLMStyleAnalyzer)
├── 特征融合处理器 (FeatureFusionProcessor)
├── 高级LLM分析器 (AdvancedLLMStyleAnalyzer)
└── 风格对齐引擎 (StyleAlignmentEngine)
    ├── 相似度计算器 (StyleSimilarityCalculator)
    └── 风格迁移引擎 (StyleTransferEngine)
```

## 快速开始

### 1. 安装依赖

```bash
pip install jieba scikit-learn transformers torch
```

### 2. 基本使用

```python
from core.tools.comprehensive_style_processor import ComprehensiveStyleProcessor

# 初始化处理器
processor = ComprehensiveStyleProcessor(llm_client=your_llm_client)

# 提取文风特征
text = "这是一个测试文档，用于演示文风分析功能。"
features = processor.extract_comprehensive_style_features(text, "测试文档")

# 比较两个文档的风格
text1 = "正式的商务文档内容..."
text2 = "随意的日常文档内容..."
comparison = processor.compare_document_styles(text1, text2)

# 文风对齐
content = "需要对齐的内容..."
alignment = processor.align_text_style(text2, text1, content)
```

## 详细功能说明

### 量化特征提取

#### 词汇特征
- **TTR (Type-Token Ratio)**: 词汇丰富度指标
- **平均词长**: 反映用词复杂程度
- **词性分布**: 名词、动词、形容词等比例
- **特定词汇密度**: 正式词汇、非正式词汇、虚词使用频率

```python
extractor = QuantitativeFeatureExtractor()
lexical_features = extractor.extract_lexical_features(text)
print(f"TTR: {lexical_features['ttr']}")
print(f"正式词汇密度: {lexical_features['formal_word_density']}")
```

#### 句法特征
- **句长统计**: 平均句长、句长标准差
- **句型分布**: 长短句比例、复合句使用
- **句式多样性**: 并列句、从句等结构分析

```python
syntactic_features = extractor.extract_syntactic_features(text)
print(f"平均句长: {syntactic_features['avg_sentence_length']}")
print(f"复合句比例: {syntactic_features['compound_sentence_ratio']}")
```

### LLM深度分析

#### 综合风格分析
使用精心设计的提示词模板，让LLM从多个维度评估文本风格：

```python
analyzer = AdvancedLLMStyleAnalyzer(llm_client)
analysis = analyzer.comprehensive_style_analysis(text)
```

#### 成语和修辞分析
专门识别和分析中文文本中的成语使用和修辞手法：

```python
rhetoric_analysis = analyzer.analyze_idioms_and_rhetoric(text)
```

#### 正式程度分析
评估文本的正式程度和语域特征：

```python
formality_analysis = analyzer.analyze_formality(text)
```

### 特征融合策略

#### 加权拼接融合
```python
fusion_processor = FeatureFusionProcessor()
fusion_result = fusion_processor.fuse_features(
    quantitative_features, 
    llm_features, 
    fusion_method="weighted_concat"
)
```

#### 分层融合
```python
fusion_result = fusion_processor.fuse_features(
    quantitative_features, 
    llm_features, 
    fusion_method="hierarchical"
)
```

#### 注意力机制融合
```python
fusion_result = fusion_processor.fuse_features(
    quantitative_features, 
    llm_features, 
    fusion_method="attention"
)
```

### 风格对齐引擎

#### 相似度计算
支持多种相似度计算方法：

```python
calculator = StyleSimilarityCalculator()

# 余弦相似度
cosine_sim = calculator.calculate_similarity(features1, features2, method="cosine")

# 欧氏距离
euclidean_sim = calculator.calculate_similarity(features1, features2, method="euclidean")

# 加权相似度
weighted_sim = calculator.calculate_similarity(features1, features2, method="weighted", weights=weights)
```

#### 风格迁移策略

**直接迁移**：一步到位的风格转换
```python
transfer_engine = StyleTransferEngine(llm_client)
result = transfer_engine.perform_style_transfer(
    source_features, target_features, content, strategy="direct"
)
```

**渐进式迁移**：分步骤的风格调整
```python
result = transfer_engine.perform_style_transfer(
    source_features, target_features, content, strategy="gradual"
)
```

**选择性迁移**：重点调整特定方面
```python
result = transfer_engine.perform_style_transfer(
    source_features, target_features, content, strategy="selective"
)
```

## 高级功能

### 批量处理
```python
documents = [
    {"text": "文档1内容...", "name": "文档1"},
    {"text": "文档2内容...", "name": "文档2"},
]

batch_result = processor.batch_process_documents(documents, "extract")
```

### 处理历史管理
```python
# 获取处理历史
history = processor.get_processing_history()

# 保存处理结果
filepath = processor.save_processing_result(result, "my_analysis.json")
```

### 降维和特征选择
```python
# PCA降维
reduction_result = fusion_processor.apply_dimensionality_reduction(
    feature_vector, method="pca", target_dimensions=10
)

# 特征重要性分析
importance = fusion_processor.calculate_feature_importance(features_list)
```

## 配置和优化

### 特征权重调整
```python
processor.fusion_processor.feature_weights = {
    "quantitative": {
        "lexical": 0.4,      # 增加词汇特征权重
        "syntactic": 0.3,
        "punctuation": 0.1
    },
    "llm": {
        "vocabulary_style": 0.25,
        "sentence_structure": 0.25,
        "tone_emotion": 0.2,
        "formality": 0.2,
        "professionalism": 0.05,
        "creativity": 0.05
    }
}
```

### LLM提示词自定义
```python
# 自定义提示词模板
custom_prompt = """
请分析以下文本的专业性程度：
{text}

请从以下方面评估：
1. 专业术语使用
2. 表达规范性
3. 逻辑严密性
"""

analyzer.templates.custom_analysis_prompt = custom_prompt
```

## 性能优化建议

1. **依赖管理**: 确保安装所有必要的依赖包
2. **缓存机制**: 利用内置的LLM响应缓存减少重复调用
3. **批量处理**: 对大量文档使用批量处理功能
4. **特征选择**: 根据具体需求选择合适的特征维度
5. **存储管理**: 定期清理临时文件和缓存

## 故障排除

### 常见问题

**Q: 提示"Dependencies not available"错误**
A: 请安装必要的依赖包：`pip install jieba scikit-learn`

**Q: LLM分析失败**
A: 检查LLM客户端配置，确保API可用且有足够的配额

**Q: 特征提取结果为空**
A: 检查输入文本是否为空或格式是否正确

**Q: 内存使用过高**
A: 考虑使用降维功能或减少批量处理的文档数量

### 调试模式
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查各组件状态
print(f"jieba可用: {DEPENDENCIES_AVAILABLE}")
print(f"sklearn可用: {SKLEARN_AVAILABLE}")
```

## 扩展开发

### 自定义特征提取器
```python
class CustomFeatureExtractor:
    def extract_custom_features(self, text):
        # 实现自定义特征提取逻辑
        return {"custom_feature": value}

# 集成到主处理器
processor.custom_extractor = CustomFeatureExtractor()
```

### 自定义融合策略
```python
def custom_fusion_method(quant_vector, llm_vector, quant_names, llm_names):
    # 实现自定义融合逻辑
    return fused_vector, feature_names, weights

# 注册自定义方法
processor.fusion_processor.custom_fusion = custom_fusion_method
```

## 最佳实践

1. **文本预处理**: 确保输入文本格式规范，去除无关字符
2. **特征选择**: 根据应用场景选择合适的特征维度
3. **模型调优**: 根据实际效果调整特征权重和融合策略
4. **结果验证**: 使用测试集验证分析结果的准确性
5. **持续优化**: 根据用户反馈不断改进提示词和算法

## 版本更新

### v1.0.0 (当前版本)
- 实现基础的量化特征提取
- 集成LLM深度分析功能
- 支持多种特征融合策略
- 提供完整的文风对齐功能
- 包含批量处理和历史管理

### 计划功能
- 支持更多文档格式
- 增加可视化分析界面
- 优化LLM提示词模板
- 扩展多语言支持
- 提供REST API接口
