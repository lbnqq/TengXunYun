import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from .base_tool import BaseTool

class EnhancedVirtualReviewerTool(BaseTool):
    """
    Enhanced virtual reviewer with comprehensive review capabilities.
    Features:
    - Multi-perspective review simulation
    - Intelligent comment generation
    - Review quality assessment
    - Collaborative review simulation
    - Customizable review criteria
    - Review report generation
    """

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
        Execute virtual review operation.

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

    def review_document(self, document_content: str, reviewer_role_name: str,
                       review_focus: str = None, custom_criteria: List[str] = None) -> Dict[str, Any]:
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
        criteria = self._determine_review_criteria(reviewer_role_name, custom_criteria)

        # Generate review comments
        if self.llm_client:
            review_comments = self._generate_llm_review(
                document_content, reviewer_profile, review_focus, criteria, doc_analysis
            )
        else:
            review_comments = self._generate_rule_based_review(
                document_content, reviewer_profile, review_focus, criteria, doc_analysis
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

    def _determine_review_criteria(self, reviewer_role: str, custom_criteria: List[str] = None) -> List[str]:
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
        """Generate a summary of the review."""

        if not comments:
            return {
                "overall_assessment": "No specific issues identified",
                "key_strengths": ["Document reviewed without major concerns"],
                "priority_actions": [],
                "recommendations": ["Continue with current approach"]
            }

        # Categorize comments
        critical_issues = [c for c in comments if c.get("severity") == "critical"]
        high_issues = [c for c in comments if c.get("severity") == "high"]
        positive_feedback = [c for c in comments if c.get("severity") == "info"]

        # Generate assessment
        if critical_issues:
            assessment = "Critical issues identified that must be addressed"
        elif high_issues:
            assessment = "High priority issues require attention"
        elif len(comments) > 5:
            assessment = "Multiple improvement opportunities identified"
        else:
            assessment = "Generally good with minor improvements needed"

        # Extract key strengths
        strengths = [c["comment"] for c in positive_feedback]
        if not strengths:
            strengths = ["Document structure is clear", "Content is relevant to the topic"]

        # Priority actions
        priority_actions = []
        for comment in critical_issues + high_issues:
            priority_actions.append(f"{comment['area']}: {comment['comment']}")

        # Recommendations
        recommendations = []
        if critical_issues:
            recommendations.append("Address all critical issues before proceeding")
        if high_issues:
            recommendations.append("Prioritize high-severity improvements")
        recommendations.append("Consider implementing suggested improvements")
        recommendations.append("Schedule follow-up review after revisions")

        return {
            "overall_assessment": assessment,
            "key_strengths": strengths[:3],  # Top 3 strengths
            "priority_actions": priority_actions[:5],  # Top 5 actions
            "recommendations": recommendations
        }

    def multi_reviewer_session(self, document_content: str, reviewer_roles: List[str],
                             review_focus: str = None) -> Dict[str, Any]:
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