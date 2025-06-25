"""
LLM深度文风分析器
利用大语言模型进行深度文风特征提取和分析
"""

import json
import re
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime


class LLMStylePromptTemplates:
    """LLM文风分析提示词模板"""
    
    @staticmethod
    def get_comprehensive_style_analysis_prompt(text: str) -> str:
        """综合文风分析提示词"""
        return f"""请对以下中文文本进行全面的文风分析，从多个维度进行评估：

文本内容：
{text[:800]}...

请按照以下格式进行分析，每个维度给出1-5分的评分和详细理由：

## 1. 词汇风格分析
评分：[1-5分]
特征描述：[描述词汇使用特点，如正式程度、专业术语、修辞手法等]
典型词汇：[列举3-5个代表性词汇]

## 2. 句式结构分析  
评分：[1-5分]
特征描述：[描述句子结构特点，如长短句搭配、复合句使用等]
典型句式：[举例1-2个代表性句子]

## 3. 语气情感分析
评分：[1-5分] 
特征描述：[描述语气和情感色彩，如客观/主观、正式/亲切等]
情感倾向：[积极/中性/消极]

## 4. 表达方式分析
评分：[1-5分]
特征描述：[描述表达习惯，如直接/委婉、具体/抽象等]
修辞手法：[列举使用的修辞手法]

## 5. 文本组织分析
评分：[1-5分]
特征描述：[描述逻辑结构和组织方式]
组织特点：[如总分结构、递进关系等]

## 6. 整体风格判断
主要风格类型：[从以下选择：正式公文、商务专业、学术研究、叙述描述、简洁实用、创意文学]
风格强度：[1-5分]
风格一致性：[1-5分]

## 7. 风格特色总结
核心特征：[用3-5个关键词概括]
适用场景：[说明适合的使用场景]
改进建议：[如有需要，提出1-2点改进建议]"""

    @staticmethod
    def get_style_comparison_prompt(text1: str, text2: str) -> str:
        """文风对比分析提示词"""
        return f"""请比较以下两段中文文本的写作风格，分析它们的相似性和差异性：

文本A：
{text1[:400]}...

文本B：
{text2[:400]}...

请按以下格式进行对比分析：

## 相似度评估
整体相似度：[1-5分，5分表示非常相似]
相似原因：[说明相似的具体方面]

## 差异分析
### 词汇使用差异
文本A特点：[描述A的词汇特色]
文本B特点：[描述B的词汇特色]
差异程度：[1-5分]

### 句式结构差异  
文本A特点：[描述A的句式特色]
文本B特点：[描述B的句式特色]
差异程度：[1-5分]

### 语气情感差异
文本A特点：[描述A的语气特色]
文本B特点：[描述B的语气特色]  
差异程度：[1-5分]

## 风格迁移建议
如要将文本B改写为文本A的风格，需要：
1. [具体建议1]
2. [具体建议2]
3. [具体建议3]

## 总结
主要差异：[概括最主要的1-2个差异]
风格距离：[1-5分，5分表示风格差异很大]"""

    @staticmethod
    def get_style_alignment_prompt(source_text: str, target_style_description: str, content_to_rewrite: str) -> str:
        """文风对齐重写提示词"""
        return f"""请根据参考文本的写作风格，重写给定内容，实现文风对齐。

## 参考文本（目标风格）：
{source_text[:600]}...

## 目标风格特征：
{target_style_description}

## 需要重写的内容：
{content_to_rewrite}

## 重写要求：
1. 保持原文的核心信息和逻辑结构
2. 调整词汇选择，使其符合目标风格
3. 调整句式结构，保持风格一致性
4. 调整语气和表达方式
5. 确保重写后的文本自然流畅

## 请提供：
### 重写结果：
[在此提供重写后的完整文本]

### 调整说明：
1. 词汇调整：[说明主要的词汇替换和调整]
2. 句式调整：[说明句子结构的主要变化]
3. 语气调整：[说明语气和表达方式的调整]
4. 其他调整：[其他重要的风格调整]

### 对齐效果评估：
风格匹配度：[1-5分]
内容保真度：[1-5分]
语言流畅度：[1-5分]"""

    @staticmethod
    def get_idiom_and_rhetoric_analysis_prompt(text: str) -> str:
        """成语和修辞分析提示词"""
        return f"""请分析以下中文文本中的成语使用和修辞手法：

文本内容：
{text[:600]}...

请按以下格式分析：

## 成语使用分析
识别的成语：[列出文中所有成语，如无则写"无"]
使用频率：[成语数量/总字数 × 1000‰]
使用恰当性：[1-5分，评估成语使用是否恰当]
成语风格：[如：文雅、通俗、古典等]

## 修辞手法分析
### 比喻
使用情况：[有/无]
具体例子：[如有，请举例]

### 排比
使用情况：[有/无]  
具体例子：[如有，请举例]

### 对偶
使用情况：[有/无]
具体例子：[如有，请举例]

### 设问/反问
使用情况：[有/无]
具体例子：[如有，请举例]

### 其他修辞手法
发现的手法：[列举其他修辞手法]
具体例子：[举例说明]

## 语言特色评估
修辞丰富度：[1-5分]
表达生动性：[1-5分]
文学色彩：[1-5分]
整体评价：[简要评价文本的修辞特色]"""

    @staticmethod
    def get_formality_analysis_prompt(text: str) -> str:
        """正式程度分析提示词"""
        return f"""请分析以下中文文本的正式程度和语域特征：

文本内容：
{text[:600]}...

请按以下格式分析：

## 正式程度评估
整体正式度：[1-5分，1=非常非正式，5=非常正式]
评估依据：[说明判断的主要依据]

## 语域特征分析
### 词汇层面
正式词汇：[列举正式词汇，如"根据、依据、鉴于"等]
非正式词汇：[列举非正式词汇，如"挺、蛮、超级"等]
专业术语：[列举专业术语]
口语化表达：[列举口语化表达]

### 句式层面
正式句式特征：[如被动句、长句、复合句等]
非正式句式特征：[如省略句、感叹句等]

### 语气层面
语气特点：[如客观、主观、命令、建议等]
人称使用：[第一人称/第二人称/第三人称的使用情况]

## 适用场景判断
最适合场景：[如：公文写作、学术论文、商务沟通、日常交流等]
不适合场景：[列举不太适合的使用场景]

## 调整建议
提高正式度：[如需要更正式，应如何调整]
降低正式度：[如需要更亲和，应如何调整]"""


class AdvancedLLMStyleAnalyzer:
    """高级LLM文风分析器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.templates = LLMStylePromptTemplates()
        
    def comprehensive_style_analysis(self, text: str) -> Dict[str, Any]:
        """综合文风分析"""
        if not self.llm_client:
            return {"error": "LLM client not available"}
        
        try:
            prompt = self.templates.get_comprehensive_style_analysis_prompt(text)
            response = self.llm_client.generate(prompt)
            
            # 解析LLM响应
            parsed_result = self._parse_comprehensive_analysis(response)
            
            return {
                "analysis_type": "comprehensive_style",
                "analysis_time": datetime.now().isoformat(),
                "text_length": len(text),
                "raw_response": response,
                "parsed_analysis": parsed_result,
                "success": True
            }
            
        except Exception as e:
            return {
                "analysis_type": "comprehensive_style",
                "analysis_time": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def compare_styles(self, text1: str, text2: str) -> Dict[str, Any]:
        """对比两个文本的风格"""
        if not self.llm_client:
            return {"error": "LLM client not available"}
        
        try:
            prompt = self.templates.get_style_comparison_prompt(text1, text2)
            response = self.llm_client.generate(prompt)
            
            parsed_result = self._parse_comparison_analysis(response)
            
            return {
                "analysis_type": "style_comparison",
                "analysis_time": datetime.now().isoformat(),
                "text1_length": len(text1),
                "text2_length": len(text2),
                "raw_response": response,
                "parsed_comparison": parsed_result,
                "success": True
            }
            
        except Exception as e:
            return {
                "analysis_type": "style_comparison",
                "analysis_time": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def analyze_idioms_and_rhetoric(self, text: str) -> Dict[str, Any]:
        """分析成语和修辞手法"""
        if not self.llm_client:
            return {"error": "LLM client not available"}
        
        try:
            prompt = self.templates.get_idiom_and_rhetoric_analysis_prompt(text)
            response = self.llm_client.generate(prompt)
            
            parsed_result = self._parse_rhetoric_analysis(response)
            
            return {
                "analysis_type": "idioms_and_rhetoric",
                "analysis_time": datetime.now().isoformat(),
                "text_length": len(text),
                "raw_response": response,
                "parsed_analysis": parsed_result,
                "success": True
            }
            
        except Exception as e:
            return {
                "analysis_type": "idioms_and_rhetoric",
                "analysis_time": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def analyze_formality(self, text: str) -> Dict[str, Any]:
        """分析正式程度"""
        if not self.llm_client:
            return {"error": "LLM client not available"}
        
        try:
            prompt = self.templates.get_formality_analysis_prompt(text)
            response = self.llm_client.generate(prompt)
            
            parsed_result = self._parse_formality_analysis(response)
            
            return {
                "analysis_type": "formality_analysis",
                "analysis_time": datetime.now().isoformat(),
                "text_length": len(text),
                "raw_response": response,
                "parsed_analysis": parsed_result,
                "success": True
            }
            
        except Exception as e:
            return {
                "analysis_type": "formality_analysis",
                "analysis_time": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def _parse_comprehensive_analysis(self, response: str) -> Dict[str, Any]:
        """解析综合分析结果"""
        result = {
            "vocabulary_analysis": {},
            "sentence_structure": {},
            "tone_emotion": {},
            "expression_style": {},
            "text_organization": {},
            "overall_style": {},
            "style_summary": {}
        }
        
        try:
            # 使用正则表达式提取各部分信息
            sections = response.split('##')
            
            for section in sections:
                if '词汇风格分析' in section:
                    result["vocabulary_analysis"] = self._extract_section_info(section)
                elif '句式结构分析' in section:
                    result["sentence_structure"] = self._extract_section_info(section)
                elif '语气情感分析' in section:
                    result["tone_emotion"] = self._extract_section_info(section)
                elif '表达方式分析' in section:
                    result["expression_style"] = self._extract_section_info(section)
                elif '文本组织分析' in section:
                    result["text_organization"] = self._extract_section_info(section)
                elif '整体风格判断' in section:
                    result["overall_style"] = self._extract_section_info(section)
                elif '风格特色总结' in section:
                    result["style_summary"] = self._extract_section_info(section)
        
        except Exception as e:
            result["parsing_error"] = str(e)
        
        return result
    
    def _parse_comparison_analysis(self, response: str) -> Dict[str, Any]:
        """解析对比分析结果"""
        result = {
            "similarity_assessment": {},
            "difference_analysis": {},
            "style_transfer_suggestions": {},
            "summary": {}
        }
        
        try:
            sections = response.split('##')
            
            for section in sections:
                if '相似度评估' in section:
                    result["similarity_assessment"] = self._extract_section_info(section)
                elif '差异分析' in section:
                    result["difference_analysis"] = self._extract_section_info(section)
                elif '风格迁移建议' in section:
                    result["style_transfer_suggestions"] = self._extract_section_info(section)
                elif '总结' in section:
                    result["summary"] = self._extract_section_info(section)
        
        except Exception as e:
            result["parsing_error"] = str(e)
        
        return result
    
    def _parse_rhetoric_analysis(self, response: str) -> Dict[str, Any]:
        """解析修辞分析结果"""
        result = {
            "idiom_analysis": {},
            "rhetoric_analysis": {},
            "language_features": {}
        }
        
        try:
            sections = response.split('##')
            
            for section in sections:
                if '成语使用分析' in section:
                    result["idiom_analysis"] = self._extract_section_info(section)
                elif '修辞手法分析' in section:
                    result["rhetoric_analysis"] = self._extract_section_info(section)
                elif '语言特色评估' in section:
                    result["language_features"] = self._extract_section_info(section)
        
        except Exception as e:
            result["parsing_error"] = str(e)
        
        return result
    
    def _parse_formality_analysis(self, response: str) -> Dict[str, Any]:
        """解析正式程度分析结果"""
        result = {
            "formality_assessment": {},
            "linguistic_features": {},
            "scenario_judgment": {},
            "adjustment_suggestions": {}
        }
        
        try:
            sections = response.split('##')
            
            for section in sections:
                if '正式程度评估' in section:
                    result["formality_assessment"] = self._extract_section_info(section)
                elif '语域特征分析' in section:
                    result["linguistic_features"] = self._extract_section_info(section)
                elif '适用场景判断' in section:
                    result["scenario_judgment"] = self._extract_section_info(section)
                elif '调整建议' in section:
                    result["adjustment_suggestions"] = self._extract_section_info(section)
        
        except Exception as e:
            result["parsing_error"] = str(e)
        
        return result
    
    def _extract_section_info(self, section: str) -> Dict[str, Any]:
        """从文本段落中提取结构化信息"""
        info = {"raw_text": section.strip()}
        
        # 提取评分
        score_match = re.search(r'评分：\s*(\d+)', section)
        if score_match:
            info["score"] = int(score_match.group(1))
        
        # 提取特征描述
        desc_match = re.search(r'特征描述：\s*([^\n]+)', section)
        if desc_match:
            info["description"] = desc_match.group(1).strip()
        
        # 提取其他关键信息
        lines = section.split('\n')
        for line in lines:
            if '：' in line:
                key, value = line.split('：', 1)
                key = key.strip().replace('### ', '').replace('## ', '')
                value = value.strip()
                if key and value:
                    info[key] = value
        
        return info
