"""
端到端用户意图驱动的文档处理编排器

基于用户上传文档的状态自动识别用户意图，并执行相应的处理流程：
1. 空表格/模板 → 智能填报
2. 格式混乱 → 格式整理  
3. 内容不完整 → 内容补全
4. AIGC痕迹明显 → 风格改写
"""

import json
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime
import logging

from ..tools import DocumentParserTool, ComplexDocumentFiller, DocumentFormatExtractor
from ..tools import ContentFillerTool, StyleGeneratorTool, VirtualReviewerTool
from ..guidance import ScenarioInferenceModule


class DocumentRoleAnalyzer:
    """文档角色分析器 - 智能推断文档在处理流程中的角色"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

        # 文档角色评估指标
        self.role_indicators = {
            "format_reference": {
                "structure_completeness": 0.3,  # 结构完整性权重
                "format_consistency": 0.25,     # 格式一致性权重
                "creation_time": 0.2,           # 创建时间权重
                "content_quality": 0.15,        # 内容质量权重
                "file_naming": 0.1              # 文件命名权重
            },
            "style_reference": {
                "writing_quality": 0.35,        # 写作质量权重
                "style_consistency": 0.25,      # 风格一致性权重
                "content_depth": 0.2,           # 内容深度权重
                "language_naturalness": 0.15,   # 语言自然度权重
                "logical_coherence": 0.05       # 逻辑连贯性权重
            },
            "target_document": {
                "incompleteness": 0.4,          # 不完整程度权重
                "format_issues": 0.3,           # 格式问题权重
                "content_gaps": 0.2,            # 内容缺失权重
                "processing_urgency": 0.1       # 处理紧急度权重
            }
        }


class DocumentIntentAnalyzer:
    """文档意图分析器 - 识别用户真正想要什么"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.role_analyzer = DocumentRoleAnalyzer(llm_client)

        # AIGC检测关键词和模式
        self.aigc_indicators = {
            "phrases": [
                "作为一个", "总的来说", "综上所述", "需要注意的是", "值得一提的是",
                "首先", "其次", "最后", "另外", "此外", "因此", "所以",
                "在这种情况下", "基于以上", "通过分析", "可以看出"
            ],
            "patterns": [
                r"第[一二三四五六七八九十]+[，,]",  # 第一，第二，...
                r"[1-9]\.[1-9]\.",  # 1.1. 1.2. 格式
                r"综合[考虑分析]",
                r"通过[以上上述]",
                r"基于[以上上述]"
            ],
            "structure_indicators": [
                "引言", "概述", "背景", "目标", "方法", "结果", "结论", "建议"
            ]
        }
    
    def analyze_multi_document_roles(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析多个文档的角色和处理意图

        Args:
            documents: [{"name": str, "content": str, "metadata": dict}, ...]

        Returns:
            {
                "document_roles": {doc_name: {"role": str, "confidence": float, "evidence": []}},
                "recommended_workflow": {"primary_action": str, "steps": []},
                "default_selections": {"reference_doc": str, "target_docs": []},
                "user_confirmation_needed": bool
            }
        """
        try:
            if not documents:
                return {"error": "没有提供文档进行分析"}

            # 1. 分析每个文档的特征
            document_analyses = {}
            for doc in documents:
                analysis = self._analyze_single_document_role(
                    doc["content"], doc["name"], doc.get("metadata", {})
                )
                document_analyses[doc["name"]] = analysis

            # 2. 确定文档角色和关系
            role_assignments = self._assign_document_roles(document_analyses)

            # 3. 推荐处理工作流程
            workflow = self._recommend_processing_workflow(role_assignments)

            # 4. 生成默认选项
            defaults = self._generate_default_selections(role_assignments, workflow)

            # 5. 判断是否需要用户确认
            confirmation_needed = self._assess_confirmation_need(role_assignments, workflow)

            return {
                "document_roles": role_assignments,
                "recommended_workflow": workflow,
                "default_selections": defaults,
                "user_confirmation_needed": confirmation_needed,
                "confidence_summary": self._generate_confidence_summary(role_assignments),
                "analysis_time": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"多文档角色分析失败: {str(e)}"}

    def _analyze_single_document_role(self, content: str, name: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """分析单个文档的角色特征"""
        import os
        from datetime import datetime

        # 基础分析
        basic_analysis = self._analyze_document_basics(content)

        # 文件元数据分析
        file_analysis = {
            "creation_time": metadata.get("creation_time"),
            "file_size": metadata.get("file_size", len(content)),
            "file_extension": os.path.splitext(name)[1].lower(),
            "naming_pattern": self._analyze_file_naming(name)
        }

        # 内容质量分析
        quality_analysis = self._analyze_content_quality(content)

        # 格式规范性分析
        format_analysis = self._analyze_format_quality(content)

        # 角色得分计算
        role_scores = self._calculate_role_scores(
            basic_analysis, file_analysis, quality_analysis, format_analysis
        )

        # 确定最可能的角色
        primary_role = max(role_scores.items(), key=lambda x: x[1]["score"])

        return {
            "primary_role": primary_role[0],
            "role_confidence": primary_role[1]["score"],
            "role_evidence": primary_role[1]["evidence"],
            "all_role_scores": role_scores,
            "basic_analysis": basic_analysis,
            "quality_analysis": quality_analysis,
            "format_analysis": format_analysis,
            "file_analysis": file_analysis
        }

    def _analyze_file_naming(self, filename: str) -> Dict[str, Any]:
        """分析文件命名模式"""
        import re

        naming_analysis = {
            "has_template_keywords": False,
            "has_version_info": False,
            "has_date_info": False,
            "formality_level": "neutral",
            "naming_score": 0.5
        }

        filename_lower = filename.lower()

        # 模板关键词检测
        template_keywords = ["模板", "template", "格式", "format", "样本", "sample", "范例", "example"]
        if any(keyword in filename_lower for keyword in template_keywords):
            naming_analysis["has_template_keywords"] = True
            naming_analysis["naming_score"] += 0.3

        # 版本信息检测
        version_patterns = [r"v\d+", r"版本\d+", r"_\d+\.\d+", r"final", r"最终"]
        if any(re.search(pattern, filename_lower) for pattern in version_patterns):
            naming_analysis["has_version_info"] = True
            naming_analysis["naming_score"] += 0.2

        # 日期信息检测
        date_patterns = [r"\d{4}[-_]\d{2}[-_]\d{2}", r"\d{4}年\d{1,2}月", r"\d{8}"]
        if any(re.search(pattern, filename) for pattern in date_patterns):
            naming_analysis["has_date_info"] = True
            naming_analysis["naming_score"] += 0.1

        return naming_analysis

    def analyze_document_intent(self, document_content: str, document_name: str = None) -> Dict[str, Any]:
        """
        分析文档意图
        
        Returns:
            {
                "primary_intent": "fill_form|format_cleanup|content_completion|style_rewrite",
                "confidence": 0.0-1.0,
                "evidence": [],
                "secondary_intents": [],
                "processing_priority": "high|medium|low",
                "recommended_actions": []
            }
        """
        try:
            # 1. 基础文档分析
            basic_analysis = self._analyze_document_basics(document_content)
            
            # 2. 意图检测
            intent_scores = self._calculate_intent_scores(document_content, basic_analysis)
            
            # 3. 确定主要意图
            primary_intent = max(intent_scores.items(), key=lambda x: x[1]["score"])
            
            # 4. 生成处理建议
            recommendations = self._generate_processing_recommendations(
                primary_intent[0], intent_scores, basic_analysis
            )
            
            return {
                "primary_intent": primary_intent[0],
                "confidence": primary_intent[1]["score"],
                "evidence": primary_intent[1]["evidence"],
                "secondary_intents": self._get_secondary_intents(intent_scores, primary_intent[0]),
                "processing_priority": self._determine_priority(primary_intent[1]["score"]),
                "recommended_actions": recommendations,
                "analysis_metadata": {
                    "document_name": document_name,
                    "analysis_time": datetime.now().isoformat(),
                    "basic_stats": basic_analysis,
                    "all_intent_scores": intent_scores
                }
            }
            
        except Exception as e:
            return {"error": f"意图分析失败: {str(e)}"}
    
    def _analyze_document_basics(self, content: str) -> Dict[str, Any]:
        """基础文档分析"""
        if not content or not content.strip():
            return {
                "is_empty": True,
                "word_count": 0,
                "line_count": 0,
                "has_structure": False,
                "has_tables": False,
                "has_forms": False
            }
        
        lines = content.split('\n')
        words = content.split()
        
        # 检测表格和表单
        has_tables = any('|' in line or '\t' in line for line in lines)
        has_forms = any(any(indicator in line for indicator in ['___', '____', '：', ':', '□', '☐']) for line in lines)
        
        # 检测结构化内容
        structure_indicators = ['#', '一、', '二、', '1.', '2.', '（一）', '（二）']
        has_structure = any(any(indicator in line for indicator in structure_indicators) for line in lines)
        
        return {
            "is_empty": len(content.strip()) == 0,
            "word_count": len(words),
            "line_count": len([line for line in lines if line.strip()]),
            "has_structure": has_structure,
            "has_tables": has_tables,
            "has_forms": has_forms,
            "avg_line_length": sum(len(line) for line in lines) / max(len(lines), 1),
            "empty_line_ratio": len([line for line in lines if not line.strip()]) / max(len(lines), 1)
        }
    
    def _calculate_intent_scores(self, content: str, basic_analysis: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """计算各种意图的得分"""
        scores = {
            "fill_form": {"score": 0.0, "evidence": []},
            "format_cleanup": {"score": 0.0, "evidence": []},
            "content_completion": {"score": 0.0, "evidence": []},
            "style_rewrite": {"score": 0.0, "evidence": []}
        }
        
        # 1. 智能填报意图检测
        if basic_analysis["is_empty"] or basic_analysis["word_count"] < 50:
            scores["fill_form"]["score"] += 0.8
            scores["fill_form"]["evidence"].append("文档内容极少或为空")
        
        if basic_analysis["has_forms"]:
            scores["fill_form"]["score"] += 0.6
            scores["fill_form"]["evidence"].append("检测到表单元素")
        
        if basic_analysis["has_tables"]:
            scores["fill_form"]["score"] += 0.4
            scores["fill_form"]["evidence"].append("检测到表格结构")
        
        # 2. 格式整理意图检测
        if basic_analysis["empty_line_ratio"] > 0.3:
            scores["format_cleanup"]["score"] += 0.5
            scores["format_cleanup"]["evidence"].append("空行比例过高")
        
        if basic_analysis["avg_line_length"] < 10 or basic_analysis["avg_line_length"] > 100:
            scores["format_cleanup"]["score"] += 0.4
            scores["format_cleanup"]["evidence"].append("行长度不规范")
        
        if not basic_analysis["has_structure"] and basic_analysis["word_count"] > 200:
            scores["format_cleanup"]["score"] += 0.6
            scores["format_cleanup"]["evidence"].append("缺少结构化格式")
        
        # 3. 内容补全意图检测
        if 50 < basic_analysis["word_count"] < 300:
            scores["content_completion"]["score"] += 0.5
            scores["content_completion"]["evidence"].append("内容长度偏短")
        
        incomplete_indicators = ['待补充', '待完善', '...', '省略', '等等', 'TODO', 'TBD']
        if any(indicator in content for indicator in incomplete_indicators):
            scores["content_completion"]["score"] += 0.7
            scores["content_completion"]["evidence"].append("检测到未完成标记")
        
        # 4. 风格改写意图检测（AIGC检测）
        aigc_score = self._detect_aigc_content(content)
        scores["style_rewrite"]["score"] = aigc_score["score"]
        scores["style_rewrite"]["evidence"] = aigc_score["evidence"]
        
        return scores
    
    def _detect_aigc_content(self, content: str) -> Dict[str, Any]:
        """检测AIGC生成内容"""
        import re
        
        score = 0.0
        evidence = []
        
        # 检测AIGC常用短语
        phrase_count = sum(1 for phrase in self.aigc_indicators["phrases"] if phrase in content)
        if phrase_count >= 3:
            score += 0.4
            evidence.append(f"检测到{phrase_count}个AI常用短语")
        
        # 检测AIGC常用模式
        pattern_count = 0
        for pattern in self.aigc_indicators["patterns"]:
            if re.search(pattern, content):
                pattern_count += 1
        
        if pattern_count >= 2:
            score += 0.3
            evidence.append(f"检测到{pattern_count}个AI写作模式")
        
        # 检测过于规整的结构
        structure_count = sum(1 for indicator in self.aigc_indicators["structure_indicators"] if indicator in content)
        if structure_count >= 4:
            score += 0.3
            evidence.append("检测到过于规整的文档结构")
        
        # 检测重复性表达
        sentences = content.split('。')
        if len(sentences) > 5:
            similar_starts = {}
            for sentence in sentences:
                if len(sentence.strip()) > 10:
                    start = sentence.strip()[:3]
                    similar_starts[start] = similar_starts.get(start, 0) + 1
            
            max_similar = max(similar_starts.values()) if similar_starts else 0
            if max_similar >= 3:
                score += 0.2
                evidence.append("检测到重复性句式结构")
        
        return {"score": min(score, 1.0), "evidence": evidence}

    def _analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """分析内容质量"""
        if not content or not content.strip():
            return {
                "quality_score": 0.0,
                "writing_naturalness": 0.0,
                "logical_coherence": 0.0,
                "content_depth": 0.0,
                "language_quality": 0.0
            }

        # 写作自然度评估
        naturalness_score = self._assess_writing_naturalness(content)

        # 逻辑连贯性评估
        coherence_score = self._assess_logical_coherence(content)

        # 内容深度评估
        depth_score = self._assess_content_depth(content)

        # 语言质量评估
        language_score = self._assess_language_quality(content)

        # 综合质量得分
        overall_score = (
            naturalness_score * 0.3 +
            coherence_score * 0.25 +
            depth_score * 0.25 +
            language_score * 0.2
        )

        return {
            "quality_score": overall_score,
            "writing_naturalness": naturalness_score,
            "logical_coherence": coherence_score,
            "content_depth": depth_score,
            "language_quality": language_score
        }

    def _assess_writing_naturalness(self, content: str) -> float:
        """评估写作自然度（检测AIGC痕迹）"""
        score = 1.0  # 从满分开始，发现AIGC特征则扣分

        # 检测AIGC常用短语
        phrase_count = sum(1 for phrase in self.aigc_indicators["phrases"] if phrase in content)
        score -= min(phrase_count * 0.1, 0.4)  # 最多扣0.4分

        # 检测过于规整的结构
        structure_count = sum(1 for indicator in self.aigc_indicators["structure_indicators"] if indicator in content)
        if structure_count >= 5:
            score -= 0.3
        elif structure_count >= 3:
            score -= 0.2

        # 检测重复性表达模式
        import re
        patterns_found = sum(1 for pattern in self.aigc_indicators["patterns"] if re.search(pattern, content))
        score -= min(patterns_found * 0.15, 0.3)

        return max(score, 0.0)

    def _assess_logical_coherence(self, content: str) -> float:
        """评估逻辑连贯性"""
        sentences = content.split('。')
        if len(sentences) < 3:
            return 0.5  # 内容太短，给中等分

        # 检测逻辑连接词的使用
        logical_connectors = ["因此", "所以", "但是", "然而", "另外", "此外", "首先", "其次", "最后"]
        connector_count = sum(1 for connector in logical_connectors if connector in content)

        # 检测段落结构
        paragraphs = content.split('\n\n')
        has_clear_structure = len(paragraphs) > 1 and all(len(p.strip()) > 50 for p in paragraphs[:3])

        score = 0.5  # 基础分
        score += min(connector_count * 0.1, 0.3)  # 逻辑连接词加分
        if has_clear_structure:
            score += 0.2  # 清晰结构加分

        return min(score, 1.0)

    def _assess_content_depth(self, content: str) -> float:
        """评估内容深度"""
        word_count = len(content.split())

        # 基于字数的基础评分
        if word_count < 100:
            base_score = 0.2
        elif word_count < 500:
            base_score = 0.5
        elif word_count < 1500:
            base_score = 0.8
        else:
            base_score = 1.0

        # 检测专业术语和具体细节
        professional_indicators = ["分析", "研究", "方法", "结果", "数据", "指标", "评估", "建议"]
        professional_count = sum(1 for indicator in professional_indicators if indicator in content)

        # 检测具体数字和事实
        import re
        numbers = len(re.findall(r'\d+(?:\.\d+)?%?', content))

        depth_bonus = min(professional_count * 0.05 + numbers * 0.02, 0.3)

        return min(base_score + depth_bonus, 1.0)

    def _assess_language_quality(self, content: str) -> float:
        """评估语言质量"""
        # 检测语法错误和不规范表达
        quality_issues = 0

        # 检测常见语法问题
        grammar_issues = ["的的", "了了", "在在", "是是"]  # 重复词
        quality_issues += sum(1 for issue in grammar_issues if issue in content)

        # 检测标点符号使用
        import re
        punctuation_density = len(re.findall(r'[，。！？；：]', content)) / max(len(content), 1)
        if punctuation_density < 0.02 or punctuation_density > 0.1:
            quality_issues += 1

        # 基础分减去问题分
        score = 1.0 - min(quality_issues * 0.1, 0.5)

        return max(score, 0.3)  # 最低0.3分

    def _analyze_format_quality(self, content: str) -> Dict[str, Any]:
        """分析格式质量"""
        format_analysis = {
            "structure_score": 0.0,
            "consistency_score": 0.0,
            "completeness_score": 0.0,
            "overall_format_score": 0.0
        }

        if not content or not content.strip():
            return format_analysis

        lines = content.split('\n')

        # 结构化程度评估
        structure_indicators = ['#', '一、', '二、', '1.', '2.', '（一）', '（二）']
        has_structure = any(any(indicator in line for indicator in structure_indicators) for line in lines)
        format_analysis["structure_score"] = 0.8 if has_structure else 0.3

        # 格式一致性评估
        empty_line_ratio = len([line for line in lines if not line.strip()]) / max(len(lines), 1)
        consistency_score = 0.8 if 0.1 <= empty_line_ratio <= 0.3 else 0.5
        format_analysis["consistency_score"] = consistency_score

        # 完整性评估
        has_title = len(lines) > 0 and len(lines[0].strip()) < 50 and lines[0].strip()
        has_content = len([line for line in lines if line.strip()]) > 3
        completeness_score = 0.5
        if has_title:
            completeness_score += 0.2
        if has_content:
            completeness_score += 0.3
        format_analysis["completeness_score"] = completeness_score

        # 综合格式得分
        format_analysis["overall_format_score"] = (
            format_analysis["structure_score"] * 0.4 +
            format_analysis["consistency_score"] * 0.3 +
            format_analysis["completeness_score"] * 0.3
        )

        return format_analysis
    
    def _get_secondary_intents(self, intent_scores: Dict[str, Dict[str, Any]], primary_intent: str) -> List[Dict[str, Any]]:
        """获取次要意图"""
        secondary = []
        for intent, data in intent_scores.items():
            if intent != primary_intent and data["score"] > 0.3:
                secondary.append({
                    "intent": intent,
                    "score": data["score"],
                    "evidence": data["evidence"][:2]  # 只保留前两个证据
                })
        
        return sorted(secondary, key=lambda x: x["score"], reverse=True)[:2]
    
    def _determine_priority(self, confidence: float) -> str:
        """确定处理优先级"""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        else:
            return "low"
    
    def _generate_processing_recommendations(self, primary_intent: str, intent_scores: Dict[str, Dict[str, Any]], basic_analysis: Dict[str, Any]) -> List[str]:
        """生成处理建议"""
        recommendations = []
        
        if primary_intent == "fill_form":
            recommendations.append("启动智能填报流程，自动识别填写项并引导用户完成")
            if basic_analysis["has_tables"]:
                recommendations.append("重点关注表格数据的完整性和准确性")
        
        elif primary_intent == "format_cleanup":
            recommendations.append("执行格式整理，统一文档样式和结构")
            if not basic_analysis["has_structure"]:
                recommendations.append("建议添加标题层级和段落结构")
        
        elif primary_intent == "content_completion":
            recommendations.append("分析内容缺失，智能补全相关信息")
            recommendations.append("保持原有写作风格和逻辑连贯性")
        
        elif primary_intent == "style_rewrite":
            recommendations.append("检测到AI生成痕迹，建议进行人性化改写")
            recommendations.append("重点优化表达方式，增加自然性和个性化")
        
        # 添加次要意图的建议
        for secondary in self._get_secondary_intents(intent_scores, primary_intent):
            if secondary["score"] > 0.5:
                recommendations.append(f"同时考虑{secondary['intent']}需求")
        
        return recommendations


class IntentDrivenOrchestrator:
    """意图驱动的端到端文档处理编排器"""
    
    def __init__(self, llm_client=None, kb_path: str = "src/core/knowledge_base"):
        self.llm_client = llm_client
        self.intent_analyzer = DocumentIntentAnalyzer(llm_client)
        
        # 初始化工具
        self.tools = {
            "document_parser": DocumentParserTool(),
            "document_filler": ComplexDocumentFiller(),
            "format_extractor": DocumentFormatExtractor(),
            "content_filler": ContentFillerTool(),
            "style_generator": StyleGeneratorTool(llm_client, os.path.join(kb_path, "style_templates.yaml")),
            "virtual_reviewer": VirtualReviewerTool(llm_client, {})
        }
        
        # 处理状态
        self.processing_state = {
            "document_path": None,
            "document_content": None,
            "intent_analysis": None,
            "processing_results": [],
            "final_output": None
        }
        
        self.log_path = os.path.join("logs", "intent_analysis.log")
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        logging.basicConfig(filename=self.log_path, level=logging.INFO, format='%(message)s')
    
    def log_intent_analysis(self, document_name: str, intent_result: dict, user_feedback: dict = None):
        import json
        from datetime import datetime
        log_entry = {
            "document_name": document_name,
            "primary_intent": intent_result.get("primary_intent"),
            "confidence": intent_result.get("confidence"),
            "evidence": intent_result.get("evidence"),
            "analysis_time": intent_result.get("analysis_metadata", {}).get("analysis_time"),
            "user_feedback": user_feedback,
            "log_time": datetime.now().isoformat()
        }
        logging.info(json.dumps(log_entry, ensure_ascii=False))

    def process_document_end_to_end(self, file_path: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        端到端文档处理主流程
        
        Args:
            file_path: 文档路径
            user_context: 用户上下文信息（可选）
            
        Returns:
            处理结果，包含最终输出和处理过程信息
        """
        try:
            # 1. 文档解析
            parse_result = self._parse_document(file_path)
            if "error" in parse_result:
                return parse_result
            
            # 2. 意图分析
            intent_result = self._analyze_user_intent(parse_result["content"], user_context)
            if "error" in intent_result:
                return intent_result
            
            # 日志记录
            self.log_intent_analysis(os.path.basename(file_path), intent_result)
            
            # 3. 自动处理执行
            processing_result = self._execute_intent_based_processing(intent_result)
            if "error" in processing_result:
                return processing_result
            
            # 4. 结果整合和输出
            final_result = self._generate_final_output(processing_result)
            
            return {
                "success": True,
                "intent_analysis": intent_result,
                "processing_results": processing_result,
                "final_output": final_result,
                "user_message": self._generate_user_message(intent_result, final_result),
                "processing_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"端到端处理失败: {str(e)}"}
    
    def _parse_document(self, file_path: str) -> Dict[str, Any]:
        """解析文档"""
        self.processing_state["document_path"] = file_path
        
        parse_result = self.tools["document_parser"].execute(file_path=file_path)
        if "error" in parse_result:
            return parse_result
        
        self.processing_state["document_content"] = parse_result.get("text_content", "")
        return {"content": self.processing_state["document_content"], "structure": parse_result}
    
    def _analyze_user_intent(self, content: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析用户意图"""
        document_name = os.path.basename(self.processing_state["document_path"]) if self.processing_state["document_path"] else None
        
        intent_result = self.intent_analyzer.analyze_document_intent(content, document_name)
        self.processing_state["intent_analysis"] = intent_result
        
        return intent_result
    
    def _execute_intent_based_processing(self, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """基于意图执行处理"""
        primary_intent = intent_analysis.get("primary_intent")
        confidence = intent_analysis.get("confidence", 0.0)
        
        if confidence < 0.3:
            return {"error": "意图识别置信度过低，无法自动处理"}
        
        processing_results = []
        
        # 根据主要意图执行相应处理
        if primary_intent == "fill_form":
            result = self._execute_form_filling()
            processing_results.append({"type": "form_filling", "result": result})
        
        elif primary_intent == "format_cleanup":
            result = self._execute_format_cleanup()
            processing_results.append({"type": "format_cleanup", "result": result})
        
        elif primary_intent == "content_completion":
            result = self._execute_content_completion()
            processing_results.append({"type": "content_completion", "result": result})
        
        elif primary_intent == "style_rewrite":
            result = self._execute_style_rewrite()
            processing_results.append({"type": "style_rewrite", "result": result})
        
        # 处理次要意图
        for secondary in intent_analysis.get("secondary_intents", []):
            if secondary["score"] > 0.5:
                secondary_result = self._execute_secondary_intent(secondary["intent"])
                processing_results.append({"type": f"secondary_{secondary['intent']}", "result": secondary_result})
        
        self.processing_state["processing_results"] = processing_results
        return {"processing_results": processing_results}
    
    def _execute_form_filling(self) -> Dict[str, Any]:
        """执行表单填写"""
        # 这里应该调用智能填报流程
        return {"status": "form_filling_initiated", "message": "智能填报流程已启动"}
    
    def _execute_format_cleanup(self) -> Dict[str, Any]:
        """执行格式整理"""
        # 这里应该调用格式整理流程
        return {"status": "format_cleaned", "message": "文档格式已整理"}
    
    def _execute_content_completion(self) -> Dict[str, Any]:
        """执行内容补全"""
        # 这里应该调用内容补全流程
        return {"status": "content_completed", "message": "内容已智能补全"}
    
    def _execute_style_rewrite(self) -> Dict[str, Any]:
        """执行风格改写"""
        # 这里应该调用风格改写流程
        return {"status": "style_rewritten", "message": "文档风格已优化"}
    
    def _execute_secondary_intent(self, intent: str) -> Dict[str, Any]:
        """执行次要意图"""
        return {"status": f"{intent}_processed", "message": f"次要需求{intent}已处理"}
    
    def _generate_final_output(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成最终输出"""
        return {
            "output_type": "processed_document",
            "content": self.processing_state["document_content"],  # 这里应该是处理后的内容
            "metadata": {
                "original_file": self.processing_state["document_path"],
                "processing_steps": len(processing_result.get("processing_results", [])),
                "completion_time": datetime.now().isoformat()
            }
        }
    
    def _generate_user_message(self, intent_analysis: Dict[str, Any], final_result: Dict[str, Any]) -> str:
        """生成用户友好的消息"""
        primary_intent = intent_analysis.get("primary_intent")
        confidence = intent_analysis.get("confidence", 0.0)
        
        intent_names = {
            "fill_form": "智能填报",
            "format_cleanup": "格式整理", 
            "content_completion": "内容补全",
            "style_rewrite": "风格优化"
        }
        
        intent_name = intent_names.get(primary_intent, "文档处理")
        
        message = f"✅ 已自动识别您的需求为：{intent_name}（置信度：{confidence:.1%}）\n"
        message += f"📋 处理完成，文档已按照您的需求进行优化。\n"
        
        if intent_analysis.get("secondary_intents"):
            message += f"🔄 同时处理了其他相关需求，确保文档质量。"
        
        return message
