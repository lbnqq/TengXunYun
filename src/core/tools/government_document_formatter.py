import re
import json
from typing import Dict, Any, List
from datetime import datetime

class GovernmentDocumentFormatterTool:
    """
    政府公文格式化工具
    根据《党政机关公文处理工作条例》等规范，对政府公文进行格式检查和优化
    """
    
    def __init__(self):
        self.tool_name = "政府公文格式化工具"
        self.description = "根据公文处理规范，检查和优化政府公文格式"
        
        # 公文种类定义
        self.document_types = {
            "决议": "适用于会议讨论通过的重大决策事项",
            "决定": "适用于对重要事项作出决策和部署",
            "命令（令）": "适用于公布行政法规和规章、宣布施行重大强制性措施、批准授予和晋升衔级、嘉奖有关单位和人员",
            "公报": "适用于公布重要决定或者重大事项",
            "公告": "适用于向国内外宣布重要事项或者法定事项",
            "通告": "适用于在一定范围内公布应当遵守或者周知的事项",
            "意见": "适用于对重要问题提出见解和处理办法",
            "通知": "适用于发布、传达要求下级机关执行和有关单位周知或者执行的事项，批转、转发公文",
            "通报": "适用于表彰先进、批评错误、传达重要精神和告知重要情况",
            "报告": "适用于向上级机关汇报工作、反映情况，回复上级机关的询问",
            "请示": "适用于向上级机关请求指示、批准",
            "批复": "适用于答复下级机关请示事项",
            "议案": "适用于各级人民政府按照法律程序向同级人民代表大会或者人民代表大会常务委员会提请审议事项",
            "函": "适用于不相隶属机关之间商洽工作、询问和答复问题、请求批准和答复审批事项",
            "纪要": "适用于记录会议主要情况和议定事项"
        }
        
        # 公文格式要素
        self.format_elements = {
            "标题": {"required": True, "position": "居中", "font": "方正小标宋简体", "size": "22磅"},
            "主送机关": {"required": True, "position": "左侧顶格", "punctuation": "："},
            "正文": {"required": True, "structure": ["开头", "主体", "结尾"]},
            "附件": {"required": False, "format": "附件：附件名称"},
            "发文机关署名": {"required": True, "position": "右下"},
            "成文日期": {"required": True, "format": "年月日", "position": "署名下方"},
            "印章": {"required": True, "position": "骑缝盖章"},
            "附注": {"required": False, "position": "左下角"}
        }
        
        # 常用公文用语
        self.official_phrases = {
            "开头用语": ["根据", "按照", "遵照", "依据", "为了", "为贯彻", "为落实"],
            "承转用语": ["现将", "特将", "兹将", "据此", "鉴于", "考虑到"],
            "结尾用语": ["特此通知", "特此报告", "特此请示", "特此批复", "特此函告", "特此纪要"],
            "表态用语": ["同意", "原则同意", "不同意", "批准", "不予批准", "予以支持"],
            "要求用语": ["要求", "希望", "请", "务必", "应当", "必须", "严禁", "不得"]
        }
    
    def execute(self, document_content: str, document_type: str = None) -> Dict[str, Any]:
        """
        执行政府公文格式化
        
        Args:
            document_content: 文档内容
            document_type: 公文类型（可选）
            
        Returns:
            格式化结果和建议
        """
        try:
            # 分析文档结构
            structure_analysis = self._analyze_document_structure(document_content)
            
            # 识别公文类型
            if not document_type:
                document_type = self._identify_document_type(document_content)
            
            # 格式检查
            format_check = self._check_format_compliance(document_content, structure_analysis)
            
            # 语言规范检查
            language_check = self._check_language_standards(document_content)
            
            # 生成优化建议
            optimization_suggestions = self._generate_optimization_suggestions(
                structure_analysis, format_check, language_check
            )
            
            # 生成格式化后的文档
            formatted_content = self._format_document(
                document_content, document_type, optimization_suggestions
            )
            
            return {
                "tool_name": self.tool_name,
                "document_type": document_type,
                "structure_analysis": structure_analysis,
                "format_check": format_check,
                "language_check": language_check,
                "optimization_suggestions": optimization_suggestions,
                "formatted_content": formatted_content,
                "compliance_score": self._calculate_compliance_score(format_check, language_check)
            }
            
        except Exception as e:
            return {"error": f"政府公文格式化失败: {str(e)}"}
    
    def _analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """分析文档结构"""
        structure = {
            "has_title": False,
            "has_main_recipient": False,
            "has_body": False,
            "has_signature": False,
            "has_date": False,
            "title": "",
            "main_recipient": "",
            "body_paragraphs": [],
            "signature": "",
            "date": ""
        }
        
        lines = content.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        if not lines:
            return structure
        
        # 识别标题（通常是第一行，包含"关于"、"通知"等关键词）
        first_line = lines[0]
        if any(keyword in first_line for keyword in ["关于", "通知", "决定", "意见", "公告", "通报", "报告", "请示", "批复", "函"]):
            structure["has_title"] = True
            structure["title"] = first_line
        
        # 识别主送机关（通常包含"："）
        for i, line in enumerate(lines[1:3], 1):  # 检查前几行
            if "：" in line and not line.endswith("："):
                structure["has_main_recipient"] = True
                structure["main_recipient"] = line
                break
        
        # 识别正文
        body_start = 1
        if structure["has_title"]:
            body_start += 1
        if structure["has_main_recipient"]:
            body_start += 1
            
        # 识别署名和日期（通常在最后几行）
        for line in reversed(lines[-5:]):
            # 日期格式检查
            if re.search(r'\d{4}年\d{1,2}月\d{1,2}日', line):
                structure["has_date"] = True
                structure["date"] = line
            # 署名检查（包含政府、委员会、办公室等）
            elif any(keyword in line for keyword in ["政府", "委员会", "办公室", "局", "厅", "部"]):
                structure["has_signature"] = True
                structure["signature"] = line
        
        # 提取正文段落
        body_end = len(lines)
        if structure["has_signature"]:
            body_end -= 1
        if structure["has_date"]:
            body_end -= 1
            
        structure["body_paragraphs"] = lines[body_start:body_end]
        structure["has_body"] = len(structure["body_paragraphs"]) > 0
        
        return structure
    
    def _identify_document_type(self, content: str) -> str:
        """识别公文类型"""
        content_lower = content.lower()
        
        # 根据标题关键词识别
        for doc_type in self.document_types.keys():
            if doc_type in content:
                return doc_type
        
        # 根据内容特征识别
        if "请示" in content or "恳请" in content:
            return "请示"
        elif "批复" in content or "同意" in content:
            return "批复"
        elif "通知" in content or "现将" in content:
            return "通知"
        elif "报告" in content or "汇报" in content:
            return "报告"
        elif "函" in content or "商洽" in content:
            return "函"
        else:
            return "通知"  # 默认类型
    
    def _check_format_compliance(self, content: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        """检查格式合规性"""
        compliance = {
            "title_format": {"compliant": structure["has_title"], "issues": []},
            "recipient_format": {"compliant": structure["has_main_recipient"], "issues": []},
            "body_format": {"compliant": structure["has_body"], "issues": []},
            "signature_format": {"compliant": structure["has_signature"], "issues": []},
            "date_format": {"compliant": structure["has_date"], "issues": []},
            "overall_issues": []
        }
        
        # 标题格式检查
        if not structure["has_title"]:
            compliance["title_format"]["issues"].append("缺少标题")
        elif structure["title"]:
            if not structure["title"].startswith("关于") and "通知" not in structure["title"]:
                compliance["title_format"]["issues"].append("标题格式不规范，建议以'关于'开头")
        
        # 主送机关格式检查
        if not structure["has_main_recipient"]:
            compliance["recipient_format"]["issues"].append("缺少主送机关")
        elif structure["main_recipient"] and not structure["main_recipient"].endswith("："):
            compliance["recipient_format"]["issues"].append("主送机关后应使用冒号")
        
        # 正文格式检查
        if not structure["has_body"]:
            compliance["body_format"]["issues"].append("缺少正文内容")
        
        # 署名格式检查
        if not structure["has_signature"]:
            compliance["signature_format"]["issues"].append("缺少发文机关署名")
        
        # 日期格式检查
        if not structure["has_date"]:
            compliance["date_format"]["issues"].append("缺少成文日期")
        elif structure["date"]:
            if not re.search(r'\d{4}年\d{1,2}月\d{1,2}日', structure["date"]):
                compliance["date_format"]["issues"].append("日期格式不规范，应为'年月日'格式")
        
        return compliance
    
    def _check_language_standards(self, content: str) -> Dict[str, Any]:
        """检查语言规范"""
        language_check = {
            "formal_language": {"score": 0, "issues": []},
            "official_phrases": {"score": 0, "suggestions": []},
            "grammar_check": {"score": 0, "issues": []},
            "terminology": {"score": 0, "suggestions": []}
        }
        
        # 检查是否使用正式语言
        informal_words = ["很", "非常", "特别", "比较", "还是", "可能", "大概", "应该"]
        formal_issues = []
        for word in informal_words:
            if word in content:
                formal_issues.append(f"建议避免使用非正式用词：'{word}'")
        
        language_check["formal_language"]["issues"] = formal_issues
        language_check["formal_language"]["score"] = max(0, 100 - len(formal_issues) * 10)
        
        # 检查公文用语使用情况
        phrase_suggestions = []
        if "现在" in content and "现将" not in content:
            phrase_suggestions.append("建议使用'现将'替代'现在'")
        if "这个" in content:
            phrase_suggestions.append("建议使用'该'替代'这个'")
        
        language_check["official_phrases"]["suggestions"] = phrase_suggestions
        language_check["official_phrases"]["score"] = max(0, 100 - len(phrase_suggestions) * 15)
        
        return language_check
    
    def _generate_optimization_suggestions(self, structure: Dict, format_check: Dict, language_check: Dict) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 结构优化建议
        if not structure["has_title"]:
            suggestions.append("添加规范的公文标题")
        if not structure["has_main_recipient"]:
            suggestions.append("添加主送机关")
        if not structure["has_signature"]:
            suggestions.append("添加发文机关署名")
        if not structure["has_date"]:
            suggestions.append("添加成文日期")
        
        # 格式优化建议
        for element, check in format_check.items():
            if isinstance(check, dict) and check.get("issues"):
                suggestions.extend(check["issues"])
        
        # 语言优化建议
        if language_check["formal_language"]["issues"]:
            suggestions.extend(language_check["formal_language"]["issues"])
        if language_check["official_phrases"]["suggestions"]:
            suggestions.extend(language_check["official_phrases"]["suggestions"])
        
        return suggestions
    
    def _format_document(self, content: str, doc_type: str, suggestions: List[str]) -> str:
        """格式化文档"""
        # 这里可以实现具体的格式化逻辑
        # 目前返回带有格式说明的内容
        
        formatted_lines = []
        formatted_lines.append(f"# {doc_type}")
        formatted_lines.append("")
        formatted_lines.append("## 格式化说明")
        formatted_lines.append("- 标题：居中，方正小标宋简体，22磅")
        formatted_lines.append("- 主送机关：左侧顶格，后加冒号")
        formatted_lines.append("- 正文：仿宋GB2312，3号字")
        formatted_lines.append("- 署名：右下角")
        formatted_lines.append("- 日期：署名下方，年月日格式")
        formatted_lines.append("")
        formatted_lines.append("## 原文内容")
        formatted_lines.append(content)
        
        if suggestions:
            formatted_lines.append("")
            formatted_lines.append("## 优化建议")
            for i, suggestion in enumerate(suggestions, 1):
                formatted_lines.append(f"{i}. {suggestion}")
        
        return "\n".join(formatted_lines)
    
    def _calculate_compliance_score(self, format_check: Dict, language_check: Dict) -> int:
        """计算合规性得分"""
        format_score = 0
        total_checks = 0
        
        for element, check in format_check.items():
            if isinstance(check, dict) and "compliant" in check:
                total_checks += 1
                if check["compliant"]:
                    format_score += 1
        
        format_percentage = (format_score / total_checks * 100) if total_checks > 0 else 0
        
        # 语言规范得分
        language_scores = []
        for check in language_check.values():
            if isinstance(check, dict) and "score" in check:
                language_scores.append(check["score"])
        
        language_percentage = sum(language_scores) / len(language_scores) if language_scores else 0
        
        # 综合得分
        overall_score = int((format_percentage * 0.6 + language_percentage * 0.4))
        
        return overall_score
