#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Prompt Generator - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""


import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class SmartPromptGenerator:
    """
    智能提示词生成器 - 为每个专家角色生成专业的评审提示词
    """
    
    def __init__(self):
        self.prompt_templates = self._init_prompt_templates()
        self.review_criteria = self._init_review_criteria()
        self.output_formats = self._init_output_formats()
    
    def _init_prompt_templates(self) -> Dict[str, str]:
        """初始化提示词模板"""
        return {
            "technical_reviewer": """
你是一位{role_name}，具有以下专业背景：
{background}

请从你的专业角度评审以下文档：

📋 文档信息：
- 文档类型：{document_type}
- 文档复杂度：{complexity_level}
- 目标受众：{target_audience}
- 评审重点：{review_focus}

🎯 你的专业评审重点：
{review_focus_areas}

📝 请以{tone_style}的风格进行评审，重点关注：
1. 技术准确性和可行性
2. 实现细节和架构设计
3. 性能和安全考虑
4. 技术标准和最佳实践
5. 潜在的技术风险

📄 文档内容：
{document_content}

📊 请提供详细的评审意见，包括：
- 主要技术问题识别
- 具体改进建议
- 技术风险评估
- 优先级排序（Critical/High/Medium/Low）
- 技术可行性评估

请确保评审意见专业、具体、可操作。
""",
            
            "business_analyst": """
你是一位{role_name}，具有以下专业背景：
{background}

请从商业分析角度评审以下文档：

📋 文档信息：
- 文档类型：{document_type}
- 业务复杂度：{complexity_level}
- 目标受众：{target_audience}
- 评审重点：{review_focus}

🎯 你的专业评审重点：
{review_focus_areas}

📝 请以{tone_style}的风格进行评审，重点关注：
1. 商业价值和市场定位
2. 目标用户需求匹配度
3. 竞争优势分析
4. 商业模式可行性
5. 商业风险评估

📄 文档内容：
{document_content}

📊 请提供详细的评审意见，包括：
- 主要商业问题识别
- 市场机会分析
- 商业策略建议
- 风险评估和缓解措施
- ROI和商业可行性评估

请确保评审意见具有商业洞察力和战略价值。
""",
            
            "legal_reviewer": """
你是一位{role_name}，具有以下专业背景：
{background}

请从法律合规角度评审以下文档：

📋 文档信息：
- 文档类型：{document_type}
- 法律复杂度：{complexity_level}
- 目标受众：{target_audience}
- 评审重点：{review_focus}

🎯 你的专业评审重点：
{review_focus_areas}

📝 请以{tone_style}的风格进行评审，重点关注：
1. 法律合规性检查
2. 合同条款完整性
3. 法律风险识别
4. 知识产权保护
5. 责任和义务明确性

📄 文档内容：
{document_content}

📊 请提供详细的评审意见，包括：
- 主要法律问题识别
- 合规性风险评估
- 法律条款完善建议
- 风险缓解措施
- 法律文件规范性检查

请确保评审意见严谨、准确、具有法律效力。
""",
            
            "qa_specialist": """
你是一位{role_name}，具有以下专业背景：
{background}

请从质量保证角度评审以下文档：

📋 文档信息：
- 文档类型：{document_type}
- 质量复杂度：{complexity_level}
- 目标受众：{target_audience}
- 评审重点：{review_focus}

🎯 你的专业评审重点：
{review_focus_areas}

📝 请以{tone_style}的风格进行评审，重点关注：
1. 内容准确性和完整性
2. 逻辑一致性和清晰度
3. 质量标准符合性
4. 可测试性和可验证性
5. 质量改进机会

📄 文档内容：
{document_content}

📊 请提供详细的评审意见，包括：
- 主要质量问题识别
- 准确性和完整性检查
- 质量改进建议
- 测试和验证建议
- 质量保证措施

请确保评审意见系统、全面、可验证。
""",
            
            "default": """
你是一位{role_name}，具有以下专业背景：
{background}

请从你的专业角度评审以下文档：

📋 文档信息：
- 文档类型：{document_type}
- 复杂度：{complexity_level}
- 目标受众：{target_audience}
- 评审重点：{review_focus}

🎯 你的专业评审重点：
{review_focus_areas}

📝 请以{tone_style}的风格进行评审，重点关注：
1. 专业准确性
2. 内容完整性
3. 逻辑严密性
4. 可操作性
5. 风险评估

📄 文档内容：
{document_content}

📊 请提供详细的评审意见，包括：
- 主要问题识别
- 改进建议
- 风险评估
- 优先级排序
- 专业建议

请确保评审意见专业、具体、有价值。
"""
        }
    
    def _init_review_criteria(self) -> Dict[str, List[str]]:
        """初始化评审标准"""
        return {
            "technical": [
                "技术可行性", "架构设计", "性能优化", "安全考虑", "可扩展性",
                "技术标准", "最佳实践", "实现细节", "技术风险", "维护性"
            ],
            "business": [
                "商业价值", "市场定位", "用户需求", "竞争优势", "商业模式",
                "收益分析", "成本效益", "风险评估", "战略 alignment", "可执行性"
            ],
            "legal": [
                "法律合规", "合同条款", "责任义务", "知识产权", "风险控制",
                "监管要求", "法律效力", "争议解决", "保密条款", "违约责任"
            ],
            "quality": [
                "准确性", "完整性", "一致性", "清晰度", "可测试性",
                "质量标准", "改进机会", "验证方法", "质量保证", "持续改进"
            ],
            "general": [
                "内容质量", "逻辑结构", "表达清晰", "目标明确", "可操作性",
                "风险评估", "改进建议", "优先级", "实施计划", "效果评估"
            ]
        }
    
    def _init_output_formats(self) -> Dict[str, str]:
        """初始化输出格式"""
        return {
            "structured": """
请按以下格式输出评审意见：

## 评审摘要
[总体评价和主要发现]

## 主要问题
### Critical（严重问题）
- [问题1描述]
- [问题2描述]

### High（重要问题）
- [问题1描述]
- [问题2描述]

### Medium（中等问题）
- [问题1描述]
- [问题2描述]

### Low（轻微问题）
- [问题1描述]
- [问题2描述]

## 改进建议
1. [具体建议1]
2. [具体建议2]
3. [具体建议3]

## 风险评估
- [风险1]: [风险等级] - [缓解措施]
- [风险2]: [风险等级] - [缓解措施]

## 优先级排序
1. [最高优先级问题]
2. [第二优先级问题]
3. [第三优先级问题]

## 总体评价
[总体评价和建议]
""",
            
            "simple": """
请按以下格式输出评审意见：

**评审摘要**: [总体评价]

**主要问题**:
- [问题1] (优先级: Critical/High/Medium/Low)
- [问题2] (优先级: Critical/High/Medium/Low)

**改进建议**:
- [建议1]
- [建议2]

**风险评估**: [主要风险点]

**总体评价**: [总结]
"""
        }
    
    def generate_role_prompt(self, role_profile: Dict[str, Any], 
                           document_content: str,
                           document_analysis: Dict[str, Any],
                           review_focus: Optional[str] = None,
                           output_format: str = "structured") -> str:
        """
        为特定角色生成专业的评审提示词
        
        Args:
            role_profile: 角色配置信息
            document_content: 文档内容
            document_analysis: 文档分析结果
            review_focus: 评审重点
            output_format: 输出格式
            
        Returns:
            str: 专业的评审提示词
        """
        try:
            # 1. 获取角色信息
            role_name = role_profile.get("role_name", "专业评审员")
            background = role_profile.get("background", "")
            review_focus_areas = role_profile.get("review_focus", [])
            tone_style = role_profile.get("tone_and_style", "专业、客观")
            
            # 2. 获取文档分析信息
            document_type = document_analysis.get("document_type", "通用文档")
            complexity_level = document_analysis.get("complexity_level", "medium")
            target_audience = document_analysis.get("target_audience", "通用用户")
            
            # 3. 确定评审重点
            if review_focus is None:
                review_focus = "综合评审"
            
            # 4. 选择提示词模板
            role_id = role_profile.get("role_id", "default")
            template = self.prompt_templates.get(role_id, self.prompt_templates["default"])
            
            # 5. 格式化提示词
            prompt = template.format(
                role_name=role_name,
                background=background,
                document_type=document_type,
                complexity_level=complexity_level,
                target_audience=target_audience,
                review_focus=review_focus,
                review_focus_areas=", ".join(review_focus_areas),
                tone_style=tone_style,
                document_content=document_content
            )
            
            # 6. 添加输出格式要求
            output_format_guide = self.output_formats.get(output_format, self.output_formats["structured"])
            prompt += f"\n\n{output_format_guide}"
            
            # 7. 添加时间戳和角色标识
            prompt += f"\n\n---\n评审时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n评审角色: {role_name}\n---"
            
            return prompt
            
        except Exception as e:
            print(f"❌ 生成角色提示词失败: {e}")
            # 返回基础提示词
            return self._generate_fallback_prompt(role_profile, document_content)
    
    def _generate_fallback_prompt(self, role_profile: Dict[str, Any], document_content: str) -> str:
        """生成回退提示词"""
        role_name = role_profile.get("role_name", "专业评审员")
        background = role_profile.get("background", "")
        
        return f"""
你是一位{role_name}，具有以下专业背景：
{background}

请评审以下文档并提供专业意见：

{document_content}

请提供：
1. 主要问题识别
2. 改进建议
3. 风险评估
4. 优先级排序

评审角色: {role_name}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def generate_multi_role_prompt(self, role_profiles: List[Dict[str, Any]],
                                 document_content: str,
                                 document_analysis: Dict[str, Any],
                                 review_focus: Optional[str] = None) -> Dict[str, str]:
        """
        为多个角色生成评审提示词
        
        Args:
            role_profiles: 角色配置列表
            document_content: 文档内容
            document_analysis: 文档分析结果
            review_focus: 评审重点
            
        Returns:
            Dict[str, str]: 角色ID到提示词的映射
        """
        prompts = {}
        
        for role_profile in role_profiles:
            role_id = role_profile.get("role_id", "unknown")
            prompt = self.generate_role_prompt(
                role_profile, document_content, document_analysis, review_focus or "综合评审"
            )
            prompts[role_id] = prompt
        
        return prompts
    
    def customize_prompt_for_document_type(self, base_prompt: str, 
                                         document_type: str,
                                         document_analysis: Dict[str, Any]) -> str:
        """
        根据文档类型定制提示词
        
        Args:
            base_prompt: 基础提示词
            document_type: 文档类型
            document_analysis: 文档分析结果
            
        Returns:
            str: 定制后的提示词
        """
        # 根据文档类型添加特定要求
        type_specific_requirements = {
            "technical_report": """
特别注意：
- 技术方案的可行性和创新性
- 实验设计和数据分析的严谨性
- 技术风险评估和缓解措施
- 与现有技术的对比分析
""",
            "business_proposal": """
特别注意：
- 商业模式的可行性和创新性
- 市场分析和竞争策略
- 财务预测和风险评估
- 执行计划和里程碑
""",
            "legal_document": """
特别注意：
- 法律条款的完整性和准确性
- 权利义务的明确性
- 风险控制和责任界定
- 争议解决机制
""",
            "government_document": """
特别注意：
- 政策依据和法规符合性
- 程序合法性和可操作性
- 责任分工和监督机制
- 实施效果和社会影响
""",
            "academic_paper": """
特别注意：
- 研究方法的科学性
- 文献综述的完整性
- 数据分析和结论的可靠性
- 学术规范和引用准确性
"""
        }
        
        # 添加文档类型特定要求
        if document_type in type_specific_requirements:
            base_prompt += type_specific_requirements[document_type]
        
        return base_prompt
    
    def add_context_information(self, prompt: str, context_info: Dict[str, Any]) -> str:
        """
        添加上下文信息到提示词
        
        Args:
            prompt: 原始提示词
            context_info: 上下文信息
            
        Returns:
            str: 增强后的提示词
        """
        context_section = "\n\n📚 上下文信息:\n"
        
        for key, value in context_info.items():
            if value:
                context_section += f"- {key}: {value}\n"
        
        # 在文档内容前插入上下文信息
        if "📄 文档内容：" in prompt:
            prompt = prompt.replace("📄 文档内容：", context_section + "📄 文档内容：")
        else:
            prompt += context_section
        
        return prompt 