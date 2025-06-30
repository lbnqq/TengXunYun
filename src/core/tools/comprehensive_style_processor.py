#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Style Processor - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .enhanced_style_extractor import EnhancedStyleExtractor
from .llm_style_analyzer import AdvancedLLMStyleAnalyzer
from .feature_fusion_processor import FeatureFusionProcessor
from .style_alignment_engine import StyleAlignmentEngine

# 导入语义空间行为算法组件
try:
    from .semantic_space_behavior_engine import SemanticSpaceBehaviorEngine
    SEMANTIC_BEHAVIOR_AVAILABLE = True
except ImportError:
    SEMANTIC_BEHAVIOR_AVAILABLE = False
    print("Warning: Semantic space behavior analysis not available.")


class ComprehensiveStyleProcessor:
    """综合文风处理器 - 主接口类"""
    
    def __init__(self, llm_client=None, storage_path: str = "src/core/knowledge_base/comprehensive_style"):
        """
        初始化综合文风处理器
        
        Args:
            llm_client: LLM客户端
            storage_path: 存储路径
        """
        self.llm_client = llm_client
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # 初始化各个组件
        self.style_extractor = EnhancedStyleExtractor(llm_client,
            os.path.join(storage_path, "extracted_features"))
        self.llm_analyzer = AdvancedLLMStyleAnalyzer(llm_client)
        self.fusion_processor = FeatureFusionProcessor(
            os.path.join(storage_path, "fusion_models"))
        self.alignment_engine = StyleAlignmentEngine(llm_client,
            os.path.join(storage_path, "alignments"))

        # 初始化语义空间行为算法引擎
        if SEMANTIC_BEHAVIOR_AVAILABLE and llm_client:
            self.semantic_engine = SemanticSpaceBehaviorEngine(
                llm_client=llm_client,
                storage_path=os.path.join(storage_path, "semantic_behavior")
            )
            self.semantic_analysis_enabled = True
            print("✅ 语义空间行为分析功能已启用")
        else:
            self.semantic_engine = None
            self.semantic_analysis_enabled = False
            print("⚠️ 语义空间行为分析功能未启用")
        
        # 处理历史记录
        self.processing_history = []
    
    def extract_comprehensive_style_features(self, text: str, document_name: str = None,
                                           include_advanced_analysis: bool = True) -> Dict[str, Any]:
        """
        提取综合文风特征
        
        Args:
            text: 文本内容
            document_name: 文档名称
            include_advanced_analysis: 是否包含高级分析
        """
        print(f"开始提取文风特征: {document_name or '未命名文档'}")
        
        result = {
            "processing_id": self._generate_processing_id(),
            "document_name": document_name or "未命名文档",
            "processing_time": datetime.now().isoformat(),
            "text_length": len(text),
            "basic_features": {},
            "advanced_features": {},
            "comprehensive_analysis": {},
            "processing_summary": {},
            "success": False
        }
        
        try:
            # 1. 基础特征提取
            print("正在提取基础特征...")
            basic_features = self.style_extractor.extract_comprehensive_features(text, document_name)
            result["basic_features"] = basic_features
            
            # 2. 高级LLM分析（如果启用）
            if include_advanced_analysis and self.llm_client:
                print("正在进行高级LLM分析...")
                advanced_features = {}
                
                # 综合文风分析
                comprehensive_analysis = self.llm_analyzer.comprehensive_style_analysis(text)
                advanced_features["comprehensive_analysis"] = comprehensive_analysis
                
                # 成语和修辞分析
                rhetoric_analysis = self.llm_analyzer.analyze_idioms_and_rhetoric(text)
                advanced_features["rhetoric_analysis"] = rhetoric_analysis
                
                # 正式程度分析
                formality_analysis = self.llm_analyzer.analyze_formality(text)
                advanced_features["formality_analysis"] = formality_analysis
                
                result["advanced_features"] = advanced_features
            
            # 3. 特征融合
            if basic_features.get("success") and result.get("advanced_features"):
                print("正在进行特征融合...")
                fusion_result = self.fusion_processor.fuse_features(
                    basic_features.get("quantitative_features", {}),
                    basic_features.get("llm_features", {}),
                    fusion_method="weighted_concat"
                )
                result["comprehensive_analysis"]["fusion_result"] = fusion_result
            
            # 4. 生成处理摘要
            result["processing_summary"] = self._generate_processing_summary(result)
            result["success"] = True
            
            # 5. 记录处理历史
            self._record_processing_history(result)
            
            print("文风特征提取完成!")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"文风特征提取失败: {str(e)}")
        
        return result
    
    def compare_document_styles(self, text1: str, text2: str, 
                              doc1_name: str = None, doc2_name: str = None) -> Dict[str, Any]:
        """
        比较两个文档的文风
        
        Args:
            text1: 第一个文档文本
            text2: 第二个文档文本
            doc1_name: 第一个文档名称
            doc2_name: 第二个文档名称
        """
        print(f"开始比较文档风格: {doc1_name or '文档1'} vs {doc2_name or '文档2'}")
        
        result = {
            "comparison_id": self._generate_processing_id(),
            "comparison_time": datetime.now().isoformat(),
            "document1_name": doc1_name or "文档1",
            "document2_name": doc2_name or "文档2",
            "document1_features": {},
            "document2_features": {},
            "similarity_analysis": {},
            "difference_analysis": {},
            "comparison_summary": {},
            "success": False
        }
        
        try:
            # 1. 提取两个文档的特征
            print("正在提取第一个文档的特征...")
            doc1_features = self.extract_comprehensive_style_features(text1, doc1_name, True)
            result["document1_features"] = doc1_features
            
            print("正在提取第二个文档的特征...")
            doc2_features = self.extract_comprehensive_style_features(text2, doc2_name, True)
            result["document2_features"] = doc2_features
            
            # 2. 计算相似度
            if (doc1_features.get("success") and doc2_features.get("success") and
                doc1_features.get("basic_features", {}).get("feature_vector") and
                doc2_features.get("basic_features", {}).get("feature_vector")):
                
                print("正在计算风格相似度...")
                similarity_result = self.alignment_engine.similarity_calculator.calculate_similarity(
                    doc1_features["basic_features"]["feature_vector"],
                    doc2_features["basic_features"]["feature_vector"],
                    method="cosine"
                )
                result["similarity_analysis"] = similarity_result
            
            # 3. LLM对比分析
            if self.llm_client:
                print("正在进行LLM对比分析...")
                llm_comparison = self.llm_analyzer.compare_styles(text1, text2)
                result["difference_analysis"] = llm_comparison
            
            # 4. 生成比较摘要
            result["comparison_summary"] = self._generate_comparison_summary(result)
            result["success"] = True
            
            print("文档风格比较完成!")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"文档风格比较失败: {str(e)}")
        
        return result
    
    def align_text_style(self, source_text: str, target_text: str, content_to_align: str,
                        source_name: str = None, target_name: str = None) -> Dict[str, Any]:
        """
        将文本对齐到目标风格
        
        Args:
            source_text: 源文档文本（当前风格）
            target_text: 目标文档文本（目标风格）
            content_to_align: 需要对齐的内容
            source_name: 源文档名称
            target_name: 目标文档名称
        """
        print(f"开始文风对齐: {source_name or '源文档'} -> {target_name or '目标文档'}")
        
        result = {
            "alignment_id": self._generate_processing_id(),
            "alignment_time": datetime.now().isoformat(),
            "source_name": source_name or "源文档",
            "target_name": target_name or "目标文档",
            "original_content": content_to_align,
            "aligned_content": "",
            "source_features": {},
            "target_features": {},
            "alignment_result": {},
            "quality_assessment": {},
            "success": False
        }
        
        try:
            # 1. 提取源文档和目标文档的特征
            print("正在分析源文档风格...")
            source_features = self.extract_comprehensive_style_features(source_text, source_name, True)
            result["source_features"] = source_features
            
            print("正在分析目标文档风格...")
            target_features = self.extract_comprehensive_style_features(target_text, target_name, True)
            result["target_features"] = target_features
            
            # 2. 执行文风对齐
            if source_features.get("success") and target_features.get("success"):
                print("正在执行文风对齐...")
                alignment_result = self.alignment_engine.align_style(
                    source_features, target_features, content_to_align, "comprehensive"
                )
                result["alignment_result"] = alignment_result
                
                if alignment_result.get("success"):
                    transfer_result = alignment_result.get("transfer_result", {})
                    result["aligned_content"] = transfer_result.get("rewritten_content", "")
                    result["quality_assessment"] = alignment_result.get("alignment_quality", {})
            
            result["success"] = True
            print("文风对齐完成!")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"文风对齐失败: {str(e)}")
        
        return result

    def analyze_semantic_behavior(self, text: str, document_name: str = None,
                                analysis_depth: str = "comprehensive") -> Dict[str, Any]:
        """
        执行语义空间行为分析

        Args:
            text: 文本内容
            document_name: 文档名称
            analysis_depth: 分析深度 ("basic", "standard", "comprehensive")
        """
        if not self.semantic_analysis_enabled:
            return {"error": "语义空间行为分析功能未启用"}

        print(f"🧠 开始语义空间行为分析: {document_name or '未命名文档'}")

        result = {
            "analysis_type": "semantic_behavior",
            "analysis_time": datetime.now().isoformat(),
            "document_name": document_name or "未命名文档",
            "analysis_depth": analysis_depth,
            "semantic_analysis": {},
            "integration_with_traditional": {},
            "comprehensive_insights": {},
            "success": False
        }

        try:
            # 1. 执行语义空间行为分析
            semantic_analysis = self.semantic_engine.analyze_semantic_behavior(
                text, document_name, analysis_depth
            )
            result["semantic_analysis"] = semantic_analysis

            # 2. 如果语义分析成功，尝试与传统分析结合
            if semantic_analysis.get("success"):
                print("🔄 正在整合传统文风分析...")
                traditional_analysis = self.extract_comprehensive_style_features(
                    text, document_name, include_advanced_analysis=True
                )
                result["traditional_analysis"] = traditional_analysis

                # 3. 整合两种分析结果
                if traditional_analysis.get("success"):
                    integration_result = self._integrate_semantic_and_traditional_analysis(
                        semantic_analysis, traditional_analysis
                    )
                    result["integration_with_traditional"] = integration_result

                    # 4. 生成综合洞察
                    comprehensive_insights = self._generate_comprehensive_insights(
                        semantic_analysis, traditional_analysis, integration_result
                    )
                    result["comprehensive_insights"] = comprehensive_insights

            result["success"] = True
            print("✅ 语义空间行为分析完成")

        except Exception as e:
            result["error"] = str(e)
            print(f"❌ 语义空间行为分析失败: {str(e)}")

        return result

    def compare_semantic_profiles(self, text1: str, text2: str,
                                doc1_name: str = None, doc2_name: str = None) -> Dict[str, Any]:
        """比较两个文档的语义风格画像"""
        if not self.semantic_analysis_enabled:
            return {"error": "语义空间行为分析功能未启用"}

        print(f"🔍 开始语义风格画像比较: {doc1_name or '文档1'} vs {doc2_name or '文档2'}")

        try:
            comparison_result = self.semantic_engine.compare_semantic_profiles(
                text1, text2, doc1_name, doc2_name
            )

            if comparison_result.get("success"):
                print("✅ 语义风格画像比较完成")
            else:
                print("❌ 语义风格画像比较失败")

            return comparison_result

        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "comparison_time": datetime.now().isoformat()
            }

    def _integrate_semantic_and_traditional_analysis(self, semantic_analysis: Dict[str, Any],
                                                   traditional_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """整合语义分析和传统分析结果"""
        integration = {
            "integration_time": datetime.now().isoformat(),
            "feature_correlation": {},
            "complementary_insights": {},
            "unified_assessment": {},
            "success": False
        }

        try:
            # 1. 特征关联分析
            semantic_profile = semantic_analysis.get("final_profile", {})
            traditional_features = traditional_analysis.get("basic_features", {})

            if semantic_profile.get("success") and traditional_features.get("success"):
                # 提取关键指标进行关联
                semantic_scores = semantic_profile.get("style_scores", {})
                traditional_vector = traditional_features.get("feature_vector", [])

                integration["feature_correlation"] = {
                    "semantic_conceptual_organization": semantic_scores.get("conceptual_organization", 3.0),
                    "traditional_feature_count": len(traditional_vector),
                    "semantic_creativity": semantic_scores.get("creative_association", 3.0),
                    "traditional_complexity": traditional_features.get("processing_summary", {}).get("features_extracted", 0)
                }

            # 2. 互补洞察
            complementary_insights = []

            # 语义分析的独特发现
            semantic_summary = semantic_analysis.get("analysis_summary", {})
            semantic_findings = semantic_summary.get("key_findings", [])
            for finding in semantic_findings:
                complementary_insights.append(f"语义分析发现: {finding}")

            # 传统分析的独特发现
            traditional_summary = traditional_analysis.get("processing_summary", {})
            traditional_modules = traditional_summary.get("analysis_modules_used", [])
            if traditional_modules:
                complementary_insights.append(f"传统分析模块: {', '.join(traditional_modules)}")

            integration["complementary_insights"] = complementary_insights

            # 3. 统一评估
            unified_assessment = self._create_unified_assessment(
                semantic_analysis, traditional_analysis
            )
            integration["unified_assessment"] = unified_assessment

            integration["success"] = True

        except Exception as e:
            integration["error"] = str(e)

        return integration

    def _create_unified_assessment(self, semantic_analysis: Dict[str, Any],
                                 traditional_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """创建统一评估"""
        assessment = {
            "overall_style_type": "unknown",
            "confidence_level": 0.0,
            "key_characteristics": [],
            "writing_strengths": [],
            "improvement_suggestions": []
        }

        try:
            # 从语义分析中提取风格类型
            semantic_profile = semantic_analysis.get("final_profile", {})
            if semantic_profile.get("success"):
                style_classification = semantic_profile.get("style_classification", {})
                assessment["overall_style_type"] = style_classification.get("primary_style", "unknown")

                # 关键特征
                characteristics = style_classification.get("style_characteristics", [])
                assessment["key_characteristics"].extend(characteristics)

                # 写作优势
                profile_summary = semantic_profile.get("profile_summary", {})
                strengths = profile_summary.get("key_strengths", [])
                assessment["writing_strengths"].extend(strengths)

            # 从传统分析中补充信息
            traditional_features = traditional_analysis.get("basic_features", {})
            if traditional_features.get("success"):
                processing_summary = traditional_features.get("processing_summary", {})
                key_chars = processing_summary.get("key_characteristics", [])
                assessment["key_characteristics"].extend(key_chars)

            # 计算置信度（基于两种分析的成功程度）
            semantic_success = 1.0 if semantic_analysis.get("success") else 0.0
            traditional_success = 1.0 if traditional_analysis.get("success") else 0.0
            assessment["confidence_level"] = (semantic_success + traditional_success) / 2.0

            # 去重
            assessment["key_characteristics"] = list(set(assessment["key_characteristics"]))
            assessment["writing_strengths"] = list(set(assessment["writing_strengths"]))

        except Exception as e:
            assessment["error"] = str(e)

        return assessment

    def _generate_comprehensive_insights(self, semantic_analysis: Dict[str, Any],
                                       traditional_analysis: Dict[str, Any],
                                       integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合洞察"""
        insights = {
            "analysis_depth": "comprehensive",
            "multi_dimensional_assessment": {},
            "cross_validation_results": {},
            "actionable_recommendations": [],
            "unique_discoveries": []
        }

        try:
            # 多维度评估
            semantic_profile = semantic_analysis.get("final_profile", {})
            traditional_features = traditional_analysis.get("basic_features", {})

            if semantic_profile.get("success") and traditional_features.get("success"):
                semantic_scores = semantic_profile.get("style_scores", {})

                insights["multi_dimensional_assessment"] = {
                    "语义层面": {
                        "概念组织能力": semantic_scores.get("conceptual_organization", 3.0),
                        "创新联想能力": semantic_scores.get("creative_association", 3.0),
                        "情感表达力": semantic_scores.get("emotional_expression", 3.0)
                    },
                    "传统层面": {
                        "特征丰富度": len(traditional_features.get("feature_vector", [])),
                        "分析模块数": len(traditional_features.get("processing_summary", {}).get("analysis_modules_used", []))
                    }
                }

            # 交叉验证结果
            unified_assessment = integration_result.get("unified_assessment", {})
            insights["cross_validation_results"] = {
                "风格类型一致性": "高" if unified_assessment.get("confidence_level", 0) > 0.8 else "中等",
                "特征互补性": "强" if len(integration_result.get("complementary_insights", [])) > 3 else "弱"
            }

            # 可操作建议
            recommendations = []

            # 基于语义分析的建议
            semantic_summary = semantic_analysis.get("analysis_summary", {})
            semantic_chars = semantic_summary.get("semantic_characteristics", {})

            for char, score in semantic_chars.items():
                if score < 3.0:
                    recommendations.append(f"建议提升{char}（当前分数: {score:.1f}）")

            # 基于传统分析的建议
            if traditional_features.get("success"):
                recommendations.append("建议保持当前的文风特征一致性")

            insights["actionable_recommendations"] = recommendations

            # 独特发现
            unique_discoveries = []

            # 语义分析的独特发现
            if semantic_profile.get("success"):
                profile_summary = semantic_profile.get("profile_summary", {})
                uniqueness_score = profile_summary.get("uniqueness_score", 0.0)
                if uniqueness_score > 0.7:
                    unique_discoveries.append(f"文风独特性较高（独特性分数: {uniqueness_score:.2f}）")

            insights["unique_discoveries"] = unique_discoveries

        except Exception as e:
            insights["error"] = str(e)

        return insights

    def batch_process_documents(self, documents: List[Dict[str, str]],
                              processing_type: str = "extract") -> Dict[str, Any]:
        """
        批量处理文档
        
        Args:
            documents: 文档列表，每个文档包含 {"text": "...", "name": "..."}
            processing_type: 处理类型 ("extract", "compare", "align")
        """
        print(f"开始批量处理 {len(documents)} 个文档，处理类型: {processing_type}")
        
        result = {
            "batch_id": self._generate_processing_id(),
            "batch_time": datetime.now().isoformat(),
            "processing_type": processing_type,
            "total_documents": len(documents),
            "successful_processes": 0,
            "failed_processes": 0,
            "processing_results": [],
            "batch_summary": {}
        }
        
        try:
            for i, doc in enumerate(documents):
                print(f"处理文档 {i+1}/{len(documents)}: {doc.get('name', f'文档{i+1}')}")
                
                try:
                    if processing_type == "extract":
                        process_result = self.extract_comprehensive_style_features(
                            doc["text"], doc.get("name", f"文档{i+1}")
                        )
                    else:
                        # 其他处理类型的实现
                        process_result = {"error": f"Unsupported processing type: {processing_type}"}
                    
                    if process_result.get("success"):
                        result["successful_processes"] += 1
                    else:
                        result["failed_processes"] += 1
                    
                    process_result["batch_index"] = i
                    result["processing_results"].append(process_result)
                    
                except Exception as e:
                    result["failed_processes"] += 1
                    result["processing_results"].append({
                        "batch_index": i,
                        "document_name": doc.get("name", f"文档{i+1}"),
                        "success": False,
                        "error": str(e)
                    })
            
            # 生成批量摘要
            result["batch_summary"] = {
                "success_rate": result["successful_processes"] / result["total_documents"] if result["total_documents"] > 0 else 0,
                "processing_time": datetime.now().isoformat(),
                "average_processing_time": "未计算"  # 可以添加时间统计
            }
            
            print("批量处理完成!")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"批量处理失败: {str(e)}")
        
        return result
    
    def _generate_processing_id(self) -> str:
        """生成处理ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"style_proc_{timestamp}"
    
    def _generate_processing_summary(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成处理摘要"""
        summary = {
            "processing_success": processing_result.get("success", False),
            "features_extracted": 0,
            "analysis_modules_used": [],
            "key_characteristics": []
        }
        
        # 统计提取的特征数量
        if processing_result.get("basic_features", {}).get("success"):
            summary["features_extracted"] += len(processing_result["basic_features"].get("feature_vector", []))
            summary["analysis_modules_used"].append("基础特征提取")
        
        if processing_result.get("advanced_features"):
            summary["analysis_modules_used"].extend(["LLM综合分析", "修辞分析", "正式程度分析"])
        
        # 提取关键特征
        llm_features = processing_result.get("basic_features", {}).get("llm_features", {})
        if "overall_style_profile" in llm_features:
            profile = llm_features["overall_style_profile"]
            summary["key_characteristics"] = profile.get("dominant_characteristics", [])
        
        return summary
    
    def _generate_comparison_summary(self, comparison_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成比较摘要"""
        summary = {
            "comparison_success": comparison_result.get("success", False),
            "similarity_score": 0.0,
            "main_differences": [],
            "style_distance": "未知"
        }
        
        # 相似度分数
        similarity_analysis = comparison_result.get("similarity_analysis", {})
        if similarity_analysis.get("success"):
            summary["similarity_score"] = similarity_analysis.get("similarity_score", 0.0)
            
            # 风格距离分类
            score = summary["similarity_score"]
            if score >= 0.8:
                summary["style_distance"] = "非常相似"
            elif score >= 0.6:
                summary["style_distance"] = "较为相似"
            elif score >= 0.4:
                summary["style_distance"] = "中等差异"
            elif score >= 0.2:
                summary["style_distance"] = "较大差异"
            else:
                summary["style_distance"] = "显著差异"
        
        # 主要差异
        difference_analysis = comparison_result.get("difference_analysis", {})
        if difference_analysis.get("success"):
            parsed_comparison = difference_analysis.get("parsed_comparison", {})
            summary_info = parsed_comparison.get("summary", {})
            if "主要差异" in summary_info:
                summary["main_differences"] = [summary_info["主要差异"]]
        
        return summary
    
    def _record_processing_history(self, processing_result: Dict[str, Any]):
        """记录处理历史"""
        history_entry = {
            "processing_id": processing_result.get("processing_id"),
            "document_name": processing_result.get("document_name"),
            "processing_time": processing_result.get("processing_time"),
            "success": processing_result.get("success"),
            "text_length": processing_result.get("text_length"),
            "features_count": len(processing_result.get("basic_features", {}).get("feature_vector", []))
        }
        
        self.processing_history.append(history_entry)
        
        # 保持历史记录在合理范围内
        if len(self.processing_history) > 100:
            self.processing_history = self.processing_history[-100:]
    
    def get_processing_history(self) -> List[Dict[str, Any]]:
        """获取处理历史"""
        return self.processing_history.copy()
    
    def save_processing_result(self, processing_result: Dict[str, Any], filename: str = None) -> str:
        """保存处理结果"""
        if not filename:
            processing_id = processing_result.get("processing_id", "unknown")
            filename = f"comprehensive_style_result_{processing_id}.json"
        
        filepath = os.path.join(self.storage_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(processing_result, f, ensure_ascii=False, indent=2)
            return filepath
        except Exception as e:
            return f"保存失败: {str(e)}"
