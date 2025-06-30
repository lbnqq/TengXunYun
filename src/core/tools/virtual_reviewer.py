#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Virtual Reviewer - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from .base_tool import BaseTool

class EnhancedVirtualReviewerTool(BaseTool):

    def __init__(self, llm_client, knowledge_base: dict, **kwargs):
        super().__init__(**kwargs)
        self.llm_client = llm_client
        self.knowledge_base = knowledge_base

        # Enhanced review criteria templates
        self.review_criteria = {
            "technical": {
                "accuracy": "Technical accuracy and correctness",
                "feasibility": "Implementation feasibility",
                "completeness": "Technical completeness",
                "standards": "Adherence to technical standards",
                "security": "Security considerations",
                "performance": "Performance implications"
            },
            "business": {
                "alignment": "Business alignment and value",
                "feasibility": "Business feasibility",
                "risk": "Risk assessment",
                "roi": "Return on investment",
                "stakeholder": "Stakeholder impact",
                "timeline": "Timeline and milestones"
            },
            "editorial": {
                "clarity": "Clarity and readability",
                "structure": "Document structure and flow",
                "grammar": "Grammar and language usage",
                "consistency": "Consistency and style",
                "completeness": "Content completeness",
                "audience": "Audience appropriateness"
            },
            "legal": {
                "compliance": "Legal compliance",
                "risk": "Legal risk assessment",
                "contracts": "Contract implications",
                "intellectual_property": "IP considerations",
                "privacy": "Privacy and data protection",
                "liability": "Liability concerns"
            },
            "quality": {
                "standards": "Quality standards adherence",
                "testing": "Testing and validation",
                "documentation": "Documentation quality",
                "processes": "Process compliance",
                "metrics": "Quality metrics",
                "improvement": "Improvement opportunities"
            }
        }

        # Severity level definitions
        self.severity_levels = {
            "critical": {
                "description": "Must be addressed before proceeding",
                "priority": 1,
                "color": "red"
            },
            "high": {
                "description": "Should be addressed soon",
                "priority": 2,
                "color": "orange"
            },
            "medium": {
                "description": "Should be considered for improvement",
                "priority": 3,
                "color": "yellow"
            },
            "low": {
                "description": "Nice to have improvement",
                "priority": 4,
                "color": "green"
            },
            "info": {
                "description": "Informational comment",
                "priority": 5,
                "color": "blue"
            }
        }

    def execute(self, operation: str = "review_document", **kwargs) -> Dict[str, Any]:
        """
        执行虚拟评审操作

        Args:
            operation: Type of operation (review_document, multi_reviewer, generate_report)
            **kwargs: Operation-specific parameters
        """
        try:
            if operation == "review_document":
                return self.review_document(**kwargs)
            elif operation == "multi_reviewer":
                return self.multi_reviewer_session(**kwargs)
            elif operation == "generate_report":
                return self.generate_review_report(**kwargs)
            elif operation == "assess_quality":
                return self.assess_review_quality(**kwargs)
            else:
                return {"error": f"Unknown operation: {operation}"}
        except Exception as e:
            return {"error": f"Error in virtual review: {e}"}

    def assess_review_quality(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估评审质量
        
        Args:
            review_result: 评审结果
            
        Returns:
            Dict: 质量评估结果
        """
        try:
            comments = review_result.get("review_comments", {}).get("comments", [])
            
            # 计算质量指标
            total_comments = len(comments)
            critical_count = len([c for c in comments if c.get("priority") == "critical"])
            major_count = len([c for c in comments if c.get("priority") == "major"])
            minor_count = len([c for c in comments if c.get("priority") == "minor"])
            
            # 计算质量分数
            quality_score = 100.0
            if critical_count > 0:
                quality_score -= critical_count * 20
            if major_count > 0:
                quality_score -= major_count * 10
            if minor_count > 0:
                quality_score -= minor_count * 2
            
            quality_score = max(0.0, quality_score)
            
            return {
                "success": True,
                "quality_score": quality_score,
                "quality_level": self._get_quality_level(quality_score),
                "total_issues": total_comments,
                "critical_issues": critical_count,
                "major_issues": major_count,
                "minor_issues": minor_count,
                "assessment": self._get_quality_assessment(quality_score, total_comments)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"质量评估失败: {str(e)}"
            }
    
    def _get_quality_level(self, score: float) -> str:
        """获取质量等级"""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "fair"
        elif score >= 60:
            return "poor"
        else:
            return "critical"
    
    def _get_quality_assessment(self, score: float, total_issues: int) -> str:
        """获取质量评估描述"""
        if score >= 90:
            return "文档质量优秀，可以立即使用"
        elif score >= 80:
            return "文档质量良好，建议进行小幅修改"
        elif score >= 70:
            return "文档质量一般，需要中等程度的修改"
        elif score >= 60:
            return "文档质量较差，需要大量修改"
        else:
            return "文档质量严重不足，需要重新编写"

    def review_document(self, document_content: str, reviewer_role_name: str,
                       review_focus: Optional[str] = None, custom_criteria: Optional[List[str]] = None) -> Dict[str, Any]:
        """Enhanced document review with intelligent analysis."""

        if not document_content or not document_content.strip():
            return {"error": "No document content provided for review"}

        # Find reviewer profile
        reviewer_profile = self._get_reviewer_profile(reviewer_role_name)
        if not reviewer_profile:
            return {"error": f"Reviewer role '{reviewer_role_name}' not found in knowledge base."}

        # Analyze document characteristics
        doc_analysis = self._analyze_document_characteristics(document_content)

        # Determine review criteria based on reviewer role
        criteria = self._determine_review_criteria(reviewer_role_name, custom_criteria or [])

        # Generate review comments
        if self.llm_client:
            review_comments = self._generate_llm_review(
                document_content, reviewer_profile, review_focus or "General document quality", criteria, doc_analysis
            )
        else:
            review_comments = self._generate_rule_based_review(
                document_content, reviewer_profile, review_focus or "General document quality", criteria, doc_analysis
            )

        # Post-process and validate comments
        processed_comments = self._process_review_comments(review_comments)

        # Calculate review metrics
        review_metrics = self._calculate_review_metrics(processed_comments, doc_analysis)

        return {
            "success": True,
            "reviewer": reviewer_role_name,
            "reviewer_profile": reviewer_profile,
            "review_focus": review_focus or "General document quality",
            "review_criteria": criteria,
            "review_comments": {"comments": processed_comments},
            "document_analysis": doc_analysis,
            "review_metrics": review_metrics,
            "review_timestamp": datetime.now().isoformat(),
            "review_summary": self._generate_review_summary(processed_comments, reviewer_role_name)
        }

    def _get_reviewer_profile(self, reviewer_role_name: str) -> Optional[Dict[str, Any]]:
        """Get reviewer profile from knowledge base."""
        for role in self.knowledge_base.get('roles', []):
            if role.get('role_name') == reviewer_role_name:
                return role
        return None

    def _analyze_document_characteristics(self, content: str) -> Dict[str, Any]:
        """Analyze document characteristics for review context."""
        import re

        # Basic document analysis
        lines = content.split('\n')
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        sentences = re.split(r'[.!?]+', content)
        words = content.split()

        # Identify document sections
        headings = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('#') or line.isupper() or re.match(r'^\d+\.', line)):
                headings.append(line)

        # Identify technical terms
        technical_terms = len(re.findall(r'\b(algorithm|implementation|system|architecture|framework|methodology|analysis|optimization)\b', content, re.IGNORECASE))

        # Identify business terms
        business_terms = len(re.findall(r'\b(strategy|revenue|cost|profit|market|customer|stakeholder|ROI|budget)\b', content, re.IGNORECASE))

        return {
            "word_count": len(words),
            "paragraph_count": len(paragraphs),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "heading_count": len(headings),
            "headings": headings[:10],  # First 10 headings
            "avg_sentence_length": len(words) / max(len([s for s in sentences if s.strip()]), 1),
            "technical_density": technical_terms / max(len(words), 1) * 100,
            "business_density": business_terms / max(len(words), 1) * 100,
            "document_type": self._classify_document_type(content),
            "complexity_level": self._assess_complexity_level(content, words, sentences)
        }

    def _classify_document_type(self, content: str) -> str:
        """Classify document type based on content analysis."""
        content_lower = content.lower()

        # Technical document indicators
        if any(term in content_lower for term in ['algorithm', 'implementation', 'system', 'architecture', 'technical']):
            return "technical"

        # Business document indicators
        elif any(term in content_lower for term in ['strategy', 'business', 'market', 'revenue', 'proposal']):
            return "business"

        # Academic/research indicators
        elif any(term in content_lower for term in ['research', 'study', 'analysis', 'methodology', 'findings']):
            return "academic"

        # Legal document indicators
        elif any(term in content_lower for term in ['contract', 'agreement', 'legal', 'compliance', 'terms']):
            return "legal"

        # Policy/procedure indicators
        elif any(term in content_lower for term in ['policy', 'procedure', 'guidelines', 'standards', 'process']):
            return "policy"

        return "general"

    def _assess_complexity_level(self, content: str, words: List[str], sentences: List[str]) -> str:
        """Assess document complexity level."""
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        avg_sentence_length = len(words) / max(len([s for s in sentences if s.strip()]), 1)

        # Count complex words (more than 6 characters)
        complex_words = len([word for word in words if len(word) > 6])
        complex_word_ratio = complex_words / max(len(words), 1)

        if avg_sentence_length > 25 or complex_word_ratio > 0.3 or avg_word_length > 6:
            return "high"
        elif avg_sentence_length > 15 or complex_word_ratio > 0.2 or avg_word_length > 5:
            return "medium"
        else:
            return "low"

    def _determine_review_criteria(self, reviewer_role: str, custom_criteria: Optional[List[str]] = None) -> List[str]:
        """Determine review criteria based on reviewer role."""
        if custom_criteria:
            return custom_criteria

        # Map reviewer roles to criteria categories
        role_to_criteria = {
            "technical_reviewer": "technical",
            "business_analyst": "business",
            "editor": "editorial",
            "legal_counsel": "legal",
            "quality_assurance": "quality",
            "project_manager": "business",
            "architect": "technical",
            "product_manager": "business"
        }

        criteria_category = role_to_criteria.get(reviewer_role.lower(), "editorial")
        return list(self.review_criteria.get(criteria_category, {}).keys())

    def _generate_llm_review(self, content: str, reviewer_profile: Dict[str, Any],
                           review_focus: str, criteria: List[str], doc_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate review comments using LLM."""

        prompt = self._create_review_prompt(content, reviewer_profile, review_focus, criteria, doc_analysis)

        try:
            response = self.llm_client.generate(prompt)

            # Try to parse JSON response
            try:
                review_data = json.loads(response)
                if isinstance(review_data, dict) and "comments" in review_data:
                    return review_data["comments"]
                elif isinstance(review_data, list):
                    return review_data
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract structured information
                return self._extract_comments_from_text(response)

        except Exception as e:
            print(f"LLM review generation failed: {e}")

        # Fallback to rule-based review
        return self._generate_rule_based_review(content, reviewer_profile, review_focus, criteria, doc_analysis)

    def _generate_rule_based_review(self, content: str, reviewer_profile: Dict[str, Any],
                                  review_focus: str, criteria: List[str], doc_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate review comments using rule-based approach."""

        comments = []
        reviewer_role = reviewer_profile.get('role_name', 'Unknown Reviewer')

        # Document structure review
        if doc_analysis["heading_count"] == 0:
            comments.append({
                "severity": "medium",
                "comment": "Document lacks clear section headings. Consider adding structured headings to improve readability.",
                "area": "Document Structure",
                "category": "structure"
            })

        # Length and complexity review
        if doc_analysis["word_count"] < 100:
            comments.append({
                "severity": "high",
                "comment": "Document appears to be very brief. Consider adding more detailed content and explanations.",
                "area": "Content Completeness",
                "category": "completeness"
            })
        elif doc_analysis["word_count"] > 5000:
            comments.append({
                "severity": "medium",
                "comment": "Document is quite lengthy. Consider breaking it into smaller sections or providing an executive summary.",
                "area": "Document Length",
                "category": "structure"
            })

        # Sentence complexity review
        if doc_analysis["avg_sentence_length"] > 25:
            comments.append({
                "severity": "medium",
                "comment": "Average sentence length is high. Consider breaking complex sentences for better readability.",
                "area": "Readability",
                "category": "clarity"
            })

        # Role-specific reviews
        if "technical" in reviewer_role.lower():
            if doc_analysis["technical_density"] < 2:
                comments.append({
                    "severity": "medium",
                    "comment": "Document lacks sufficient technical detail for a technical review. Consider adding more specific technical information.",
                    "area": "Technical Content",
                    "category": "technical"
                })

            # Check for technical sections
            if not any(term in content.lower() for term in ['implementation', 'architecture', 'design', 'algorithm']):
                comments.append({
                    "severity": "high",
                    "comment": "Missing key technical sections such as implementation details or system architecture.",
                    "area": "Technical Completeness",
                    "category": "technical"
                })

        elif "business" in reviewer_role.lower():
            if doc_analysis["business_density"] < 1:
                comments.append({
                    "severity": "medium",
                    "comment": "Document lacks business context and value proposition. Consider adding business justification.",
                    "area": "Business Context",
                    "category": "business"
                })

            # Check for business sections
            if not any(term in content.lower() for term in ['cost', 'benefit', 'roi', 'timeline', 'resource']):
                comments.append({
                    "severity": "high",
                    "comment": "Missing key business considerations such as cost-benefit analysis or resource requirements.",
                    "area": "Business Analysis",
                    "category": "business"
                })

        elif "editor" in reviewer_role.lower() or "editorial" in reviewer_role.lower():
            # Grammar and style checks
            import re

            # Check for common issues
            if len(re.findall(r'\b(this|that|it)\b', content)) > doc_analysis["word_count"] * 0.05:
                comments.append({
                    "severity": "low",
                    "comment": "Frequent use of vague pronouns (this, that, it). Consider being more specific.",
                    "area": "Language Clarity",
                    "category": "editorial"
                })

            # Check for passive voice (simplified check)
            passive_indicators = len(re.findall(r'\b(was|were|been|being)\s+\w+ed\b', content))
            if passive_indicators > doc_analysis["sentence_count"] * 0.3:
                comments.append({
                    "severity": "low",
                    "comment": "Frequent use of passive voice detected. Consider using active voice for clearer communication.",
                    "area": "Writing Style",
                    "category": "editorial"
                })

        # Add positive feedback
        if doc_analysis["heading_count"] > 0:
            comments.append({
                "severity": "info",
                "comment": "Good use of section headings to structure the document.",
                "area": "Document Structure",
                "category": "positive"
            })

        if 500 <= doc_analysis["word_count"] <= 2000:
            comments.append({
                "severity": "info",
                "comment": "Document length is appropriate for the content type.",
                "area": "Content Length",
                "category": "positive"
            })

        return comments

    def _create_review_prompt(self, content: str, reviewer_profile: Dict[str, Any],
                            review_focus: str, criteria: List[str], doc_analysis: Dict[str, Any]) -> str:
        """Create a comprehensive review prompt for LLM."""

        role_name = reviewer_profile.get('role_name', 'Professional Reviewer')
        background = reviewer_profile.get('background', 'Professional with relevant expertise')

        prompt = f"""You are acting as a '{role_name}' conducting a professional document review.

REVIEWER PROFILE:
- Role: {role_name}
- Background: {background}
- Review Focus: {review_focus or 'General document quality and completeness'}

DOCUMENT ANALYSIS:
- Document Type: {doc_analysis.get('document_type', 'general')}
- Word Count: {doc_analysis.get('word_count', 0)}
- Complexity Level: {doc_analysis.get('complexity_level', 'medium')}
- Technical Density: {doc_analysis.get('technical_density', 0):.1f}%
- Business Density: {doc_analysis.get('business_density', 0):.1f}%

REVIEW CRITERIA:
Focus your review on these key areas:
{chr(10).join(f"- {criterion}" for criterion in criteria)}

DOCUMENT CONTENT:
---
{content[:2000]}{"..." if len(content) > 2000 else ""}
---

INSTRUCTIONS:
1. Provide a thorough professional review from your role's perspective
2. Focus on the specified criteria and review focus
3. Identify both strengths and areas for improvement
4. Provide specific, actionable feedback
5. Use appropriate severity levels: critical, high, medium, low, info

Return your review as a JSON object with this structure:
{{
    "comments": [
        {{
            "severity": "high|medium|low|critical|info",
            "comment": "Specific feedback comment",
            "area": "Document section or aspect",
            "category": "Type of feedback (technical, business, editorial, etc.)"
        }}
    ]
}}

Provide 3-8 meaningful comments covering different aspects of the document."""

        return prompt

    def _extract_comments_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract structured comments from unstructured text response."""
        comments = []

        # Try to find comment-like patterns
        import re

        # Look for severity indicators
        severity_patterns = [
            (r'critical[ly]?\s*:?\s*(.+?)(?=\n|$)', 'critical'),
            (r'high[ly]?\s*:?\s*(.+?)(?=\n|$)', 'high'),
            (r'medium\s*:?\s*(.+?)(?=\n|$)', 'medium'),
            (r'low\s*:?\s*(.+?)(?=\n|$)', 'low'),
            (r'info\s*:?\s*(.+?)(?=\n|$)', 'info')
        ]

        for pattern, severity in severity_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                comments.append({
                    "severity": severity,
                    "comment": match.strip(),
                    "area": "General",
                    "category": "extracted"
                })

        # If no structured comments found, create generic ones
        if not comments:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            for i, line in enumerate(lines[:5]):  # Take first 5 non-empty lines
                if len(line) > 20:  # Only meaningful lines
                    comments.append({
                        "severity": "medium",
                        "comment": line,
                        "area": "General",
                        "category": "extracted"
                    })

        return comments[:8]  # Limit to 8 comments

    def _process_review_comments(self, comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and validate review comments."""
        processed = []

        for comment in comments:
            # Ensure required fields
            processed_comment = {
                "severity": comment.get("severity", "medium"),
                "comment": comment.get("comment", "No comment provided"),
                "area": comment.get("area", "General"),
                "category": comment.get("category", "general"),
                "timestamp": datetime.now().isoformat()
            }

            # Validate severity
            if processed_comment["severity"] not in self.severity_levels:
                processed_comment["severity"] = "medium"

            # Add severity metadata
            processed_comment["severity_info"] = self.severity_levels[processed_comment["severity"]]

            processed.append(processed_comment)

        # Sort by severity priority
        processed.sort(key=lambda x: x["severity_info"]["priority"])

        return processed

    def _calculate_review_metrics(self, comments: List[Dict[str, Any]], doc_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate review metrics and statistics."""

        severity_counts = {}
        category_counts = {}

        for comment in comments:
            severity = comment.get("severity", "medium")
            category = comment.get("category", "general")

            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1

        # Calculate overall score (lower is better for issues)
        severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1, "info": 0}
        total_weight = sum(severity_weights.get(sev, 0) * count for sev, count in severity_counts.items())

        # Normalize score (0-100, where 100 is perfect)
        max_possible_weight = len(comments) * 10  # If all were critical
        quality_score = max(0, 100 - (total_weight / max(max_possible_weight, 1) * 100)) if comments else 100

        return {
            "total_comments": len(comments),
            "severity_distribution": severity_counts,
            "category_distribution": category_counts,
            "quality_score": round(quality_score, 1),
            "critical_issues": severity_counts.get("critical", 0),
            "high_priority_issues": severity_counts.get("high", 0),
            "improvement_opportunities": severity_counts.get("medium", 0) + severity_counts.get("low", 0),
            "positive_feedback": severity_counts.get("info", 0)
        }

    def _generate_review_summary(self, comments: List[Dict[str, Any]], reviewer_role: str) -> Dict[str, Any]:
        """Generate a comprehensive review summary."""
        if not comments:
            return {
                "overall_assessment": "No comments provided",
                "key_issues": [],
                "recommendations": [],
                "priority_level": "low"
            }

        # Count issues by priority
        critical_issues = [c for c in comments if c.get("priority") == "critical"]
        major_issues = [c for c in comments if c.get("priority") == "major"]
        minor_issues = [c for c in comments if c.get("priority") == "minor"]

        # Determine overall priority level
        if critical_issues:
            priority_level = "critical"
        elif major_issues:
            priority_level = "major"
        elif minor_issues:
            priority_level = "minor"
        else:
            priority_level = "low"

        # Generate key recommendations
        recommendations = []
        for comment in comments[:5]:  # Top 5 recommendations
            if comment.get("suggestion"):
                recommendations.append(comment["suggestion"])

        return {
            "overall_assessment": f"Document reviewed by {reviewer_role}",
            "total_issues": len(comments),
            "critical_issues": len(critical_issues),
            "major_issues": len(major_issues),
            "minor_issues": len(minor_issues),
            "key_issues": [c.get("issue", "") for c in comments[:3]],
            "recommendations": recommendations,
            "priority_level": priority_level,
            "reviewer_role": reviewer_role
        }

    def generate_review_report(self, document_content: str, reviewer_role_name: Optional[str] = None,
                             review_focus: Optional[str] = None, custom_criteria: Optional[List[str]] = None,
                             include_detailed_analysis: bool = True) -> Dict[str, Any]:
        """
        生成评审报告
        
        Args:
            document_content: 文档内容
            reviewer_role_name: 评审员角色名称
            review_focus: 评审重点
            custom_criteria: 自定义评审标准
            include_detailed_analysis: 是否包含详细分析
            
        Returns:
            Dict: 评审报告
        """
        try:
            # 1. 验证输入参数
            if not document_content or not document_content.strip():
                return {
                    "success": False,
                    "error": "文档内容为空"
                }
            
            # 2. 设置默认评审员角色
            if not reviewer_role_name:
                reviewer_role_name = "editor"
            
            # 3. 执行文档评审
            review_result = self.review_document(
                document_content=document_content,
                reviewer_role_name=reviewer_role_name,
                review_focus=review_focus or "General document quality",
                custom_criteria=custom_criteria or []
            )
            
            if not review_result.get("success"):
                return review_result
            
            # 4. 生成评审报告结构
            report = {
                "success": True,
                "report_id": f"review_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "document_info": {
                    "content_length": len(document_content),
                    "word_count": len(document_content.split()),
                    "review_focus": review_focus or "General document quality"
                },
                "reviewer_info": {
                    "role": reviewer_role_name,
                    "profile": review_result.get("reviewer_profile", {}),
                    "criteria_used": review_result.get("review_criteria", [])
                },
                "executive_summary": self._generate_executive_summary(review_result),
                "detailed_findings": self._generate_detailed_findings(review_result) if include_detailed_analysis else {},
                "recommendations": self._generate_recommendations(review_result),
                "quality_metrics": review_result.get("review_metrics", {}),
                "approval_status": self._determine_approval_status(review_result),
                "next_steps": self._generate_next_steps(review_result)
            }
            
            # 5. 添加详细分析（如果请求）
            if include_detailed_analysis:
                report["detailed_analysis"] = {
                    "document_characteristics": review_result.get("document_analysis", {}),
                    "style_analysis": self._analyze_writing_style(document_content),
                    "structure_analysis": self._analyze_document_structure(document_content),
                    "content_quality_analysis": self._analyze_content_quality(document_content)
                }
            
            print(f"✅ 评审报告已生成: {report['report_id']}")
            return report
            
        except Exception as e:
            return {
                "success": False,
                "error": f"生成评审报告失败: {str(e)}"
            }
    
    def _generate_executive_summary(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行摘要"""
        summary = review_result.get("review_summary", {})
        comments = review_result.get("review_comments", {}).get("comments", [])
        
        return {
            "overall_assessment": summary.get("overall_assessment", "文档评审完成"),
            "total_issues_found": summary.get("total_issues", 0),
            "critical_issues": summary.get("critical_issues", 0),
            "major_issues": summary.get("major_issues", 0),
            "minor_issues": summary.get("minor_issues", 0),
            "priority_level": summary.get("priority_level", "low"),
            "key_highlights": [c.get("issue", "") for c in comments[:3] if c.get("priority") in ["critical", "major"]],
            "overall_score": self._calculate_overall_score(comments)
        }
    
    def _generate_detailed_findings(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成详细发现"""
        comments = review_result.get("review_comments", {}).get("comments", [])
        
        # 按优先级分组
        findings = {
            "critical_issues": [],
            "major_issues": [],
            "minor_issues": [],
            "suggestions": []
        }
        
        for comment in comments:
            priority = comment.get("priority", "minor")
            if priority == "critical":
                findings["critical_issues"].append(comment)
            elif priority == "major":
                findings["major_issues"].append(comment)
            elif priority == "minor":
                findings["minor_issues"].append(comment)
            else:
                findings["suggestions"].append(comment)
        
        return findings
    
    def _generate_recommendations(self, review_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成建议列表"""
        comments = review_result.get("review_comments", {}).get("comments", [])
        recommendations = []
        
        for comment in comments:
            if comment.get("suggestion"):
                recommendations.append({
                    "priority": comment.get("priority", "minor"),
                    "category": comment.get("category", "general"),
                    "suggestion": comment.get("suggestion"),
                    "rationale": comment.get("rationale", ""),
                    "estimated_effort": self._estimate_effort(comment.get("priority", "minor"))
                })
        
        # 按优先级排序
        recommendations.sort(key=lambda x: {"critical": 3, "major": 2, "minor": 1}.get(x["priority"], 0), reverse=True)
        
        return recommendations
    
    def _determine_approval_status(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """确定审批状态"""
        summary = review_result.get("review_summary", {})
        critical_issues = summary.get("critical_issues", 0)
        major_issues = summary.get("major_issues", 0)
        
        if critical_issues > 0:
            status = "rejected"
            reason = f"存在 {critical_issues} 个关键问题需要解决"
        elif major_issues > 2:
            status = "conditional_approval"
            reason = f"存在 {major_issues} 个主要问题，建议修改后重新评审"
        elif major_issues > 0:
            status = "approved_with_revisions"
            reason = f"存在 {major_issues} 个主要问题，建议修改"
        else:
            status = "approved"
            reason = "文档质量良好，可以批准"
        
        return {
            "status": status,
            "reason": reason,
            "requires_action": status in ["rejected", "conditional_approval", "approved_with_revisions"],
            "next_review_required": status in ["rejected", "conditional_approval"]
        }
    
    def _generate_next_steps(self, review_result: Dict[str, Any]) -> List[str]:
        """生成后续步骤"""
        approval_status = self._determine_approval_status(review_result)
        steps = []
        
        if approval_status["status"] == "rejected":
            steps.extend([
                "解决所有关键问题",
                "重新提交文档进行评审",
                "考虑寻求专业帮助"
            ])
        elif approval_status["status"] == "conditional_approval":
            steps.extend([
                "解决主要问题",
                "进行必要的修改",
                "重新提交评审"
            ])
        elif approval_status["status"] == "approved_with_revisions":
            steps.extend([
                "根据建议进行修改",
                "考虑实施改进建议",
                "更新文档版本"
            ])
        else:  # approved
            steps.extend([
                "文档可以正式发布",
                "考虑实施优化建议",
                "记录评审结果"
            ])
        
        return steps
    
    def _calculate_overall_score(self, comments: List[Dict[str, Any]]) -> float:
        """计算总体评分"""
        if not comments:
            return 100.0
        
        total_score = 100.0
        deductions = {
            "critical": 20.0,
            "major": 10.0,
            "minor": 2.0
        }
        
        for comment in comments:
            priority = comment.get("priority", "minor")
            deduction = deductions.get(priority, 0)
            total_score -= deduction
        
        return max(0.0, total_score)
    
    def _estimate_effort(self, priority: str) -> str:
        """估算修改工作量"""
        effort_map = {
            "critical": "高工作量",
            "major": "中等工作量", 
            "minor": "低工作量"
        }
        return effort_map.get(priority, "未知")
    
    def _analyze_writing_style(self, content: str) -> Dict[str, Any]:
        """分析写作风格"""
        # 简化的风格分析
        sentences = content.split('.')
        words = content.split()
        
        return {
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "vocabulary_diversity": len(set(words)) / max(len(words), 1),
            "formal_tone": self._assess_formality(content),
            "readability_level": self._assess_readability(content)
        }
    
    def _analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """分析文档结构"""
        lines = content.split('\n')
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        return {
            "paragraph_count": len(paragraphs),
            "avg_paragraph_length": len(content) / max(len(paragraphs), 1),
            "has_headings": any(line.strip().startswith('#') for line in lines),
            "structure_consistency": "good"  # 简化评估
        }
    
    def _analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """分析内容质量"""
        return {
            "completeness": self._assess_completeness(content),
            "accuracy": "good",  # 简化评估
            "relevance": "good",  # 简化评估
            "clarity": self._assess_clarity(content)
        }
    
    def _assess_formality(self, content: str) -> str:
        """评估正式程度"""
        informal_words = ['我觉得', '挺好的', '应该可以', '用了']
        informal_count = sum(1 for word in informal_words if word in content)
        
        if informal_count > 5:
            return "informal"
        elif informal_count > 2:
            return "semi_formal"
        else:
            return "formal"
    
    def _assess_readability(self, content: str) -> str:
        """评估可读性"""
        sentences = content.split('.')
        avg_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        if avg_length > 25:
            return "complex"
        elif avg_length > 15:
            return "moderate"
        else:
            return "simple"
    
    def _assess_completeness(self, content: str) -> str:
        """评估完整性"""
        if len(content) < 100:
            return "incomplete"
        elif len(content) < 500:
            return "basic"
        else:
            return "complete"
    
    def _assess_clarity(self, content: str) -> str:
        """评估清晰度"""
        # 简化评估
        if len(content.split()) > 50:
            return "clear"
        else:
            return "needs_improvement"

    def multi_reviewer_session(self, document_content: str, reviewer_roles: List[str],
                             review_focus: Optional[str] = None) -> Dict[str, Any]:
        """Simulate a multi-reviewer session."""

        try:
            session_results = {
                "session_id": f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "document_analysis": self._analyze_document_characteristics(document_content),
                "reviewer_results": [],
                "consensus_analysis": {},
                "session_summary": {}
            }

            # Conduct individual reviews
            for role in reviewer_roles:
                review_result = self.review_document(document_content, role, review_focus)
                if review_result.get("success"):
                    session_results["reviewer_results"].append(review_result)

            # Analyze consensus and conflicts
            session_results["consensus_analysis"] = self._analyze_reviewer_consensus(
                session_results["reviewer_results"]
            )

            # Generate session summary
            session_results["session_summary"] = self._generate_session_summary(
                session_results["reviewer_results"], session_results["consensus_analysis"]
            )

            return {
                "success": True,
                "session_results": session_results
            }

        except Exception as e:
            return {"error": f"Error in multi-reviewer session: {e}"}

    def _analyze_reviewer_consensus(self, reviewer_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze consensus and conflicts between reviewers."""

        all_comments = []
        reviewer_scores = {}
        common_areas = {}

        for result in reviewer_results:
            reviewer = result.get("reviewer", "Unknown")
            comments = result.get("review_comments", {}).get("comments", [])
            metrics = result.get("review_metrics", {})

            all_comments.extend(comments)
            reviewer_scores[reviewer] = metrics.get("quality_score", 0)

            # Track common areas of concern
            for comment in comments:
                area = comment.get("area", "General")
                if area not in common_areas:
                    common_areas[area] = []
                common_areas[area].append({
                    "reviewer": reviewer,
                    "severity": comment.get("severity"),
                    "comment": comment.get("comment")
                })

        # Find consensus areas (mentioned by multiple reviewers)
        consensus_areas = {area: comments for area, comments in common_areas.items() if len(comments) > 1}

        # Calculate overall consensus score
        scores = list(reviewer_scores.values())
        consensus_score = 100 - (max(scores) - min(scores)) if len(scores) > 1 else 100

        return {
            "total_comments": len(all_comments),
            "reviewer_scores": reviewer_scores,
            "consensus_areas": consensus_areas,
            "consensus_score": round(consensus_score, 1),
            "agreement_level": "High" if consensus_score > 80 else "Medium" if consensus_score > 60 else "Low"
        }

    def _generate_session_summary(self, reviewer_results: List[Dict[str, Any]],
                                consensus_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of multi-reviewer session."""

        # Aggregate all critical and high issues
        critical_issues = []
        high_issues = []

        for result in reviewer_results:
            comments = result.get("review_comments", {}).get("comments", [])
            for comment in comments:
                if comment.get("severity") == "critical":
                    critical_issues.append({
                        "reviewer": result.get("reviewer"),
                        "area": comment.get("area"),
                        "comment": comment.get("comment")
                    })
                elif comment.get("severity") == "high":
                    high_issues.append({
                        "reviewer": result.get("reviewer"),
                        "area": comment.get("area"),
                        "comment": comment.get("comment")
                    })

        # Generate recommendations
        recommendations = []
        if critical_issues:
            recommendations.append("Address all critical issues identified by reviewers")
        if high_issues:
            recommendations.append("Prioritize high-severity issues for next revision")
        if consensus_analysis.get("consensus_score", 0) < 70:
            recommendations.append("Seek clarification on conflicting reviewer feedback")
        recommendations.append("Schedule follow-up review after addressing major issues")

        return {
            "participating_reviewers": [r.get("reviewer") for r in reviewer_results],
            "critical_issues_count": len(critical_issues),
            "high_issues_count": len(high_issues),
            "consensus_level": consensus_analysis.get("agreement_level", "Unknown"),
            "overall_recommendation": "Approve with revisions" if not critical_issues else "Major revisions required",
            "next_steps": recommendations,
            "session_timestamp": datetime.now().isoformat()
        }


# Backward compatibility wrapper
class VirtualReviewerTool(EnhancedVirtualReviewerTool):
    """Backward compatibility wrapper for the enhanced virtual reviewer."""

    def execute(self, document_content: str, reviewer_role_name: str, review_focus: str = None) -> dict:
        """Backward compatible execute method."""
        result = self.review_document(document_content, reviewer_role_name, review_focus)

        if result.get("success"):
            return {
                "reviewer": result["reviewer"],
                "review_comments": result["review_comments"]
            }
        else:
            return result