"""
语义空间行为算法引擎
整合所有语义分析组件，实现完整的语义空间行为算法
讯飞大模型作为语义分析助手和风格评估员
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from .semantic_unit_identifier import SemanticUnitIdentifier
from .semantic_space_mapper import SemanticSpaceMapper
from .semantic_behavior_analyzer import SemanticBehaviorAnalyzer
from .semantic_style_profiler import SemanticStyleProfiler


class SemanticSpaceBehaviorEngine:
    """语义空间行为算法引擎 - 主控制器"""
    
    def __init__(self, llm_client=None, storage_path: str = "src/core/knowledge_base/semantic_analysis"):
        """
        初始化语义空间行为算法引擎
        
        Args:
            llm_client: 讯飞大模型客户端
            storage_path: 存储路径
        """
        self.llm_client = llm_client
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # 初始化各个组件
        self.unit_identifier = SemanticUnitIdentifier(llm_client)
        self.space_mapper = SemanticSpaceMapper(
            cache_dir=os.path.join(storage_path, "vectors")
        )
        self.behavior_analyzer = SemanticBehaviorAnalyzer(llm_client)
        self.style_profiler = SemanticStyleProfiler(
            storage_path=os.path.join(storage_path, "profiles")
        )
        
        # 分析历史
        self.analysis_history = []
    
    def analyze_semantic_behavior(self, text: str, document_name: str = None,
                                analysis_depth: str = "comprehensive") -> Dict[str, Any]:
        """
        执行完整的语义空间行为分析
        
        Args:
            text: 输入文本
            document_name: 文档名称
            analysis_depth: 分析深度 ("basic", "standard", "comprehensive")
        
        Returns:
            完整的语义行为分析结果
        """
        analysis_id = self._generate_analysis_id()
        
        result = {
            "analysis_id": analysis_id,
            "document_name": document_name or "未命名文档",
            "analysis_time": datetime.now().isoformat(),
            "analysis_depth": analysis_depth,
            "text_length": len(text),
            "text_preview": text[:200] + "..." if len(text) > 200 else text,
            "stage_results": {},
            "final_profile": {},
            "analysis_summary": {},
            "success": False
        }
        
        try:
            print(f"🚀 开始语义空间行为分析: {document_name or '未命名文档'}")
            print(f"📊 分析深度: {analysis_depth}")
            
            # 阶段一：语义单元识别与表示
            stage1_result = self._stage1_semantic_unit_identification(text, analysis_depth)
            result["stage_results"]["stage1_identification"] = stage1_result
            
            if not stage1_result.get("success"):
                raise Exception("阶段一：语义单元识别失败")
            
            # 阶段二：语义空间映射
            stage2_result = self._stage2_semantic_space_mapping(stage1_result, analysis_depth)
            result["stage_results"]["stage2_mapping"] = stage2_result
            
            if not stage2_result.get("success"):
                raise Exception("阶段二：语义空间映射失败")
            
            # 阶段三：语义空间行为分析
            stage3_result = self._stage3_behavior_analysis(
                stage1_result, stage2_result, text, analysis_depth
            )
            result["stage_results"]["stage3_behavior"] = stage3_result
            
            # 阶段四：特征融合与风格画像构建
            stage4_result = self._stage4_profile_construction(
                result["stage_results"], document_name
            )
            result["stage_results"]["stage4_profiling"] = stage4_result
            result["final_profile"] = stage4_result.get("profile", {})
            
            # 生成分析摘要
            result["analysis_summary"] = self._generate_analysis_summary(result)
            result["success"] = True
            
            # 记录分析历史
            self._record_analysis_history(result)
            
            print("✅ 语义空间行为分析完成")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ 语义空间行为分析失败: {str(e)}")
        
        return result
    
    def _stage1_semantic_unit_identification(self, text: str, analysis_depth: str) -> Dict[str, Any]:
        """阶段一：语义单元识别与表示"""
        print("🔍 阶段一：语义单元识别与表示")
        
        stage_result = {
            "stage_name": "语义单元识别与表示",
            "start_time": datetime.now().isoformat(),
            "semantic_units": {},
            "unit_statistics": {},
            "success": False
        }
        
        try:
            # 1. 语义单元识别
            if analysis_depth == "comprehensive":
                identification_result = self.unit_identifier.identify_semantic_units(
                    text, "comprehensive"
                )
            elif analysis_depth == "standard":
                identification_result = self.unit_identifier.identify_semantic_units(
                    text, "concept"
                )
            else:  # basic
                identification_result = self.unit_identifier.identify_semantic_units(
                    text, "entity"
                )
            
            if identification_result.get("success"):
                stage_result["semantic_units"] = identification_result["semantic_units"]
                
                # 2. 统计信息
                unit_statistics = self.unit_identifier.get_semantic_unit_statistics(
                    identification_result["semantic_units"]
                )
                stage_result["unit_statistics"] = unit_statistics
                
                stage_result["success"] = True
                print("  ✅ 语义单元识别完成")
            else:
                stage_result["error"] = identification_result.get("error", "识别失败")
                print("  ❌ 语义单元识别失败")
        
        except Exception as e:
            stage_result["error"] = str(e)
            print(f"  ❌ 阶段一执行失败: {str(e)}")
        
        stage_result["end_time"] = datetime.now().isoformat()
        return stage_result
    
    def _stage2_semantic_space_mapping(self, stage1_result: Dict[str, Any], 
                                     analysis_depth: str) -> Dict[str, Any]:
        """阶段二：语义空间映射"""
        print("🗺️ 阶段二：语义空间映射")
        
        stage_result = {
            "stage_name": "语义空间映射",
            "start_time": datetime.now().isoformat(),
            "vector_result": {},
            "similarity_result": {},
            "cluster_result": {},
            "success": False
        }
        
        try:
            semantic_units = stage1_result.get("semantic_units", {})
            
            # 1. 向量编码
            vector_result = self.space_mapper.encode_semantic_units(semantic_units)
            stage_result["vector_result"] = vector_result
            
            if vector_result.get("success"):
                print("  ✅ 语义单元向量编码完成")
                
                # 2. 相似度计算
                if analysis_depth in ["standard", "comprehensive"]:
                    similarity_result = self.space_mapper.calculate_semantic_similarities(
                        vector_result, "cosine"
                    )
                    stage_result["similarity_result"] = similarity_result
                    
                    if similarity_result.get("success"):
                        print("  ✅ 语义相似度计算完成")
                
                # 3. 聚类分析
                if analysis_depth == "comprehensive":
                    cluster_result = self.space_mapper.find_semantic_clusters(vector_result)
                    stage_result["cluster_result"] = cluster_result
                    
                    if cluster_result.get("success"):
                        print("  ✅ 语义聚类分析完成")
                
                stage_result["success"] = True
            else:
                stage_result["error"] = vector_result.get("error", "向量编码失败")
                print("  ❌ 语义空间映射失败")
        
        except Exception as e:
            stage_result["error"] = str(e)
            print(f"  ❌ 阶段二执行失败: {str(e)}")
        
        stage_result["end_time"] = datetime.now().isoformat()
        return stage_result
    
    def _stage3_behavior_analysis(self, stage1_result: Dict[str, Any],
                                stage2_result: Dict[str, Any],
                                original_text: str,
                                analysis_depth: str) -> Dict[str, Any]:
        """阶段三：语义空间行为分析"""
        print("🧠 阶段三：语义空间行为分析")
        
        stage_result = {
            "stage_name": "语义空间行为分析",
            "start_time": datetime.now().isoformat(),
            "clustering_analysis": {},
            "distance_analysis": {},
            "novelty_assessment": {},
            "emotional_analysis": {},
            "success": False
        }
        
        try:
            vector_result = stage2_result.get("vector_result", {})
            similarity_result = stage2_result.get("similarity_result", {})
            cluster_result = stage2_result.get("cluster_result", {})
            semantic_units = stage1_result.get("semantic_units", {})
            
            # 1. 概念聚类分析
            if cluster_result.get("success") and analysis_depth == "comprehensive":
                clustering_analysis = self.behavior_analyzer.analyze_concept_clustering(
                    vector_result, cluster_result, original_text
                )
                stage_result["clustering_analysis"] = clustering_analysis
                
                if clustering_analysis.get("success"):
                    print("  ✅ 概念聚类行为分析完成")
            
            # 2. 语义距离模式分析
            if similarity_result.get("success") and analysis_depth in ["standard", "comprehensive"]:
                distance_analysis = self.behavior_analyzer.analyze_semantic_distance_patterns(
                    vector_result, similarity_result
                )
                stage_result["distance_analysis"] = distance_analysis
                
                if distance_analysis.get("success"):
                    print("  ✅ 语义距离模式分析完成")
            
            # 3. 联想创新度评估
            if (similarity_result.get("success") and 
                analysis_depth == "comprehensive" and 
                self.llm_client):
                
                novelty_assessment = self.behavior_analyzer.assess_associative_novelty(
                    vector_result, similarity_result, original_text
                )
                stage_result["novelty_assessment"] = novelty_assessment
                
                if novelty_assessment.get("success"):
                    print("  ✅ 联想创新度评估完成")
            
            # 4. 情感语义行为分析
            if semantic_units and analysis_depth in ["standard", "comprehensive"]:
                emotional_analysis = self.behavior_analyzer.analyze_emotional_semantic_behavior(
                    semantic_units, vector_result
                )
                stage_result["emotional_analysis"] = emotional_analysis
                
                if emotional_analysis.get("success"):
                    print("  ✅ 情感语义行为分析完成")
            
            stage_result["success"] = True
            print("  ✅ 语义空间行为分析完成")
        
        except Exception as e:
            stage_result["error"] = str(e)
            print(f"  ❌ 阶段三执行失败: {str(e)}")
        
        stage_result["end_time"] = datetime.now().isoformat()
        return stage_result
    
    def _stage4_profile_construction(self, stage_results: Dict[str, Any],
                                   document_name: str) -> Dict[str, Any]:
        """阶段四：特征融合与风格画像构建"""
        print("🎨 阶段四：特征融合与风格画像构建")
        
        stage_result = {
            "stage_name": "特征融合与风格画像构建",
            "start_time": datetime.now().isoformat(),
            "profile": {},
            "success": False
        }
        
        try:
            # 整合所有分析结果
            analysis_results = {
                "vector_result": stage_results.get("stage2_mapping", {}).get("vector_result", {}),
                "similarity_result": stage_results.get("stage2_mapping", {}).get("similarity_result", {}),
                "cluster_result": stage_results.get("stage2_mapping", {}).get("cluster_result", {}),
                "clustering_analysis": stage_results.get("stage3_behavior", {}).get("clustering_analysis", {}),
                "distance_analysis": stage_results.get("stage3_behavior", {}).get("distance_analysis", {}),
                "novelty_assessment": stage_results.get("stage3_behavior", {}).get("novelty_assessment", {}),
                "emotional_analysis": stage_results.get("stage3_behavior", {}).get("emotional_analysis", {})
            }
            
            # 构建语义风格画像
            profile = self.style_profiler.build_semantic_style_profile(
                analysis_results, document_name
            )
            stage_result["profile"] = profile
            
            if profile.get("success"):
                print("  ✅ 语义风格画像构建完成")
                stage_result["success"] = True
            else:
                stage_result["error"] = profile.get("error", "画像构建失败")
                print("  ❌ 语义风格画像构建失败")
        
        except Exception as e:
            stage_result["error"] = str(e)
            print(f"  ❌ 阶段四执行失败: {str(e)}")
        
        stage_result["end_time"] = datetime.now().isoformat()
        return stage_result
    
    def _generate_analysis_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析摘要"""
        summary = {
            "analysis_success": result.get("success", False),
            "stages_completed": 0,
            "total_processing_time": "unknown",
            "key_findings": [],
            "semantic_characteristics": {},
            "style_profile_summary": {}
        }
        
        try:
            # 统计完成的阶段
            stage_results = result.get("stage_results", {})
            completed_stages = sum(1 for stage in stage_results.values() if stage.get("success"))
            summary["stages_completed"] = completed_stages
            
            # 关键发现
            findings = []
            
            # 从语义单元识别中提取发现
            stage1 = stage_results.get("stage1_identification", {})
            if stage1.get("success"):
                unit_stats = stage1.get("unit_statistics", {})
                concept_count = unit_stats.get("concept_count", 0)
                if concept_count > 0:
                    findings.append(f"识别出 {concept_count} 个核心概念")
            
            # 从聚类分析中提取发现
            stage3 = stage_results.get("stage3_behavior", {})
            clustering_analysis = stage3.get("clustering_analysis", {})
            if clustering_analysis.get("success"):
                clustering_metrics = clustering_analysis.get("clustering_metrics", {})
                cluster_count = clustering_metrics.get("cluster_count", 0)
                if cluster_count > 0:
                    findings.append(f"发现 {cluster_count} 个概念聚类")
            
            # 从风格画像中提取发现
            final_profile = result.get("final_profile", {})
            if final_profile.get("success"):
                style_classification = final_profile.get("style_classification", {})
                primary_style = style_classification.get("primary_style", "")
                if primary_style:
                    findings.append(f"主要风格类型：{primary_style}")
            
            summary["key_findings"] = findings
            
            # 语义特征
            if final_profile.get("success"):
                style_scores = final_profile.get("style_scores", {})
                summary["semantic_characteristics"] = {
                    "概念组织能力": style_scores.get("conceptual_organization", 3.0),
                    "语义连贯性": style_scores.get("semantic_coherence", 3.0),
                    "创新联想能力": style_scores.get("creative_association", 3.0),
                    "情感表达力": style_scores.get("emotional_expression", 3.0)
                }
                
                # 风格画像摘要
                profile_summary = final_profile.get("profile_summary", {})
                summary["style_profile_summary"] = {
                    "风格类型": profile_summary.get("profile_type", "unknown"),
                    "关键优势": profile_summary.get("key_strengths", []),
                    "独特性分数": profile_summary.get("uniqueness_score", 0.0)
                }
        
        except Exception as e:
            summary["error"] = str(e)
        
        return summary
    
    def _generate_analysis_id(self) -> str:
        """生成分析ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"semantic_analysis_{timestamp}"
    
    def _record_analysis_history(self, result: Dict[str, Any]):
        """记录分析历史"""
        history_entry = {
            "analysis_id": result.get("analysis_id"),
            "document_name": result.get("document_name"),
            "analysis_time": result.get("analysis_time"),
            "success": result.get("success"),
            "text_length": result.get("text_length"),
            "analysis_depth": result.get("analysis_depth"),
            "stages_completed": result.get("analysis_summary", {}).get("stages_completed", 0)
        }
        
        self.analysis_history.append(history_entry)
        
        # 保持历史记录在合理范围内
        if len(self.analysis_history) > 50:
            self.analysis_history = self.analysis_history[-50:]
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """获取分析历史"""
        return self.analysis_history.copy()
    
    def save_analysis_result(self, result: Dict[str, Any], filename: str = None) -> str:
        """保存分析结果"""
        if not filename:
            analysis_id = result.get("analysis_id", "unknown")
            filename = f"semantic_analysis_{analysis_id}.json"
        
        filepath = os.path.join(self.storage_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            return filepath
        except Exception as e:
            return f"保存失败: {str(e)}"
    
    def compare_semantic_profiles(self, text1: str, text2: str,
                                doc1_name: str = None, doc2_name: str = None) -> Dict[str, Any]:
        """比较两个文本的语义风格画像"""
        comparison_result = {
            "comparison_id": self._generate_analysis_id(),
            "comparison_time": datetime.now().isoformat(),
            "document1_analysis": {},
            "document2_analysis": {},
            "profile_comparison": {},
            "success": False
        }
        
        try:
            print("🔄 开始语义风格画像比较...")
            
            # 分析第一个文档
            print("分析文档1...")
            analysis1 = self.analyze_semantic_behavior(text1, doc1_name or "文档1", "comprehensive")
            comparison_result["document1_analysis"] = analysis1
            
            # 分析第二个文档
            print("分析文档2...")
            analysis2 = self.analyze_semantic_behavior(text2, doc2_name or "文档2", "comprehensive")
            comparison_result["document2_analysis"] = analysis2
            
            # 比较风格画像
            if (analysis1.get("success") and analysis2.get("success") and
                analysis1.get("final_profile", {}).get("success") and
                analysis2.get("final_profile", {}).get("success")):
                
                profile1 = analysis1["final_profile"]
                profile2 = analysis2["final_profile"]
                
                profile_comparison = self.style_profiler.compare_profiles(profile1, profile2)
                comparison_result["profile_comparison"] = profile_comparison
                
                comparison_result["success"] = True
                print("✅ 语义风格画像比较完成")
            else:
                comparison_result["error"] = "文档分析失败，无法进行比较"
                print("❌ 语义风格画像比较失败")
        
        except Exception as e:
            comparison_result["error"] = str(e)
            print(f"❌ 语义风格画像比较失败: {str(e)}")
        
        return comparison_result
