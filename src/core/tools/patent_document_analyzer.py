"""
专利申请书智能分析器
专门处理专利申请书等复杂文档表格的智能识别和填写
"""

import re
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class FieldType(Enum):
    """字段类型枚举"""
    TEXT = "text"                    # 普通文本
    TEXTAREA = "textarea"            # 多行文本
    SELECT = "select"                # 下拉选择
    DATE = "date"                    # 日期
    NUMBER = "number"                # 数字
    IMAGE = "image"                  # 图片
    TABLE = "table"                  # 表格
    SIGNATURE = "signature"          # 签名
    CHECKBOX = "checkbox"            # 复选框
    RADIO = "radio"                  # 单选按钮

class DocumentSection(Enum):
    """文档区块类型"""
    HEADER = "header"                # 文档头部
    BASIC_INFO = "basic_info"        # 基本信息
    INVENTOR_INFO = "inventor_info"  # 发明人信息
    ABSTRACT = "abstract"            # 摘要
    BACKGROUND = "background"        # 背景技术
    SUMMARY = "summary"              # 发明内容
    DRAWINGS = "drawings"            # 附图说明
    CLAIMS = "claims"                # 权利要求
    DESCRIPTION = "description"      # 具体实施方式
    APPENDIX = "appendix"            # 附录

@dataclass
class FieldConstraint:
    """字段约束条件"""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    required: bool = True
    options: List[str] = None
    file_types: List[str] = None  # 图片文件类型
    image_size: Tuple[int, int] = None  # 图片尺寸要求

@dataclass
class DocumentField:
    """文档字段定义"""
    field_id: str
    field_name: str
    field_type: FieldType
    section: DocumentSection
    position: Tuple[int, int]  # 行号，列号
    content: str
    constraints: FieldConstraint
    ai_fill_prompt: str  # AI填写提示词
    related_fields: List[str] = None  # 相关字段
    image_position: Optional[Dict[str, Any]] = None  # 图片位置信息

@dataclass
class DocumentStructure:
    """文档结构定义"""
    document_type: str
    title: str
    sections: List[DocumentSection]
    fields: List[DocumentField]
    total_objective: str  # 文档总体目标
    core_theme: str      # 核心主题
    logic_consistency: Dict[str, str]  # 逻辑一致性要求

class PatentDocumentAnalyzer:
    """专利申请书智能分析器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.tool_name = "专利申请书智能分析器"
        self.description = "智能识别专利申请书结构，分析字段类型和填写要求"
        
        # 专利申请书字段模式
        self.patent_field_patterns = {
            # 基本信息字段
            "patent_name": {
                "patterns": [
                    r"发明名称[：:]\s*[_\s]*",
                    r"专利名称[：:]\s*[_\s]*",
                    r"申请名称[：:]\s*[_\s]*"
                ],
                "field_type": FieldType.TEXT,
                "section": DocumentSection.BASIC_INFO,
                "constraints": FieldConstraint(max_length=100, required=True),
                "ai_fill_prompt": "根据发明内容和技术方案，生成简洁准确的发明名称"
            },
            
            "application_number": {
                "patterns": [
                    r"申请号[：:]\s*[_\s]*",
                    r"专利号[：:]\s*[_\s]*"
                ],
                "field_type": FieldType.TEXT,
                "section": DocumentSection.BASIC_INFO,
                "constraints": FieldConstraint(pattern=r"^\d{13}$", required=False),
                "ai_fill_prompt": "生成标准格式的专利申请号"
            },
            
            "application_date": {
                "patterns": [
                    r"申请日[：:]\s*[_\s]*",
                    r"申请日期[：:]\s*[_\s]*",
                    r"提交日期[：:]\s*[_\s]*"
                ],
                "field_type": FieldType.DATE,
                "section": DocumentSection.BASIC_INFO,
                "constraints": FieldConstraint(required=True),
                "ai_fill_prompt": "填写当前申请日期"
            },
            
            "inventor_name": {
                "patterns": [
                    r"发明人[：:]\s*[_\s]*",
                    r"申请人[：:]\s*[_\s]*"
                ],
                "field_type": FieldType.TEXT,
                "section": DocumentSection.INVENTOR_INFO,
                "constraints": FieldConstraint(max_length=50, required=True),
                "ai_fill_prompt": "填写发明人姓名"
            },
            
            "technical_field": {
                "patterns": [
                    r"技术领域[：:]\s*[_\s]*",
                    r"所属领域[：:]\s*[_\s]*"
                ],
                "field_type": FieldType.SELECT,
                "section": DocumentSection.BASIC_INFO,
                "constraints": FieldConstraint(
                    options=["机械", "电子", "化学", "生物", "计算机", "通信", "材料", "其他"],
                    required=True
                ),
                "ai_fill_prompt": "根据发明内容选择最合适的技术领域"
            },
            
            # 摘要和背景
            "abstract": {
                "patterns": [
                    r"摘要[：:]\s*[_\s]*",
                    r"发明摘要[：:]\s*[_\s]*"
                ],
                "field_type": FieldType.TEXTAREA,
                "section": DocumentSection.ABSTRACT,
                "constraints": FieldConstraint(min_length=100, max_length=500, required=True),
                "ai_fill_prompt": "根据技术方案生成简洁的技术摘要，突出创新点"
            },
            
            "background": {
                "patterns": [
                    r"背景技术[：:]\s*[_\s]*",
                    r"现有技术[：:]\s*[_\s]*"
                ],
                "field_type": FieldType.TEXTAREA,
                "section": DocumentSection.BACKGROUND,
                "constraints": FieldConstraint(min_length=200, max_length=1000, required=True),
                "ai_fill_prompt": "分析现有技术存在的问题和不足，为发明提供背景"
            },
            
            # 图片相关字段
            "drawing_description": {
                "patterns": [
                    r"附图说明[：:]\s*[_\s]*",
                    r"图片说明[：:]\s*[_\s]*"
                ],
                "field_type": FieldType.TEXTAREA,
                "section": DocumentSection.DRAWINGS,
                "constraints": FieldConstraint(min_length=50, max_length=300, required=False),
                "ai_fill_prompt": "描述附图的内容和编号"
            },
            
            "drawing_files": {
                "patterns": [
                    r"附图[：:]\s*[_\s]*",
                    r"图片[：:]\s*[_\s]*",
                    r"示意图[：:]\s*[_\s]*"
                ],
                "field_type": FieldType.IMAGE,
                "section": DocumentSection.DRAWINGS,
                "constraints": FieldConstraint(
                    file_types=["jpg", "jpeg", "png", "gif"],
                    image_size=(800, 600),
                    required=False
                ),
                "ai_fill_prompt": "上传技术方案的示意图或结构图"
            }
        }
        
        # 文档区块识别模式
        self.section_patterns = {
            DocumentSection.HEADER: [
                r"^.*专利.*申请.*书.*$",
                r"^.*发明.*申请.*书.*$"
            ],
            DocumentSection.BASIC_INFO: [
                r"^.*基本.*信息.*$",
                r"^.*申请.*信息.*$"
            ],
            DocumentSection.ABSTRACT: [
                r"^.*摘要.*$",
                r"^.*发明.*摘要.*$"
            ],
            DocumentSection.BACKGROUND: [
                r"^.*背景.*技术.*$",
                r"^.*现有.*技术.*$"
            ],
            DocumentSection.CLAIMS: [
                r"^.*权利.*要求.*$",
                r"^.*保护.*范围.*$"
            ],
            DocumentSection.DESCRIPTION: [
                r"^.*具体.*实施.*方式.*$",
                r"^.*详细.*说明.*$"
            ]
        }
    
    def analyze_patent_document(self, document_content: str, document_name: str = None) -> Dict[str, Any]:
        """
        分析专利申请书结构
        
        Args:
            document_content: 文档内容
            document_name: 文档名称
            
        Returns:
            分析结果
        """
        try:
            analysis_result = {
                "document_type": "patent_application",
                "document_name": document_name or "专利申请书",
                "analysis_time": datetime.now().isoformat(),
                "total_objective": "",
                "core_theme": "",
                "sections": [],
                "fields": [],
                "image_positions": [],
                "logic_consistency": {},
                "confidence_score": 0.0
            }
            
            # 1. 识别文档总体目标和核心主题
            objective_analysis = self._analyze_document_objective(document_content)
            analysis_result["total_objective"] = objective_analysis["objective"]
            analysis_result["core_theme"] = objective_analysis["theme"]
            
            # 2. 识别文档区块
            sections = self._identify_document_sections(document_content)
            analysis_result["sections"] = sections
            
            # 3. 识别字段
            fields = self._identify_patent_fields(document_content)
            analysis_result["fields"] = fields
            
            # 4. 识别图片位置
            image_positions = self._identify_image_positions(document_content)
            analysis_result["image_positions"] = image_positions
            
            # 5. 分析逻辑一致性
            logic_consistency = self._analyze_logic_consistency(fields, sections)
            analysis_result["logic_consistency"] = logic_consistency
            
            # 6. 计算置信度
            confidence = self._calculate_patent_confidence(fields, sections, image_positions)
            analysis_result["confidence_score"] = confidence
            
            return analysis_result
            
        except Exception as e:
            return {"error": f"专利文档分析失败: {str(e)}"}
    
    def _analyze_document_objective(self, content: str) -> Dict[str, str]:
        """分析文档总体目标和核心主题"""
        try:
            if self.llm_client:
                prompt = f"""
                分析以下专利申请书的内容，识别：
                1. 文档的总体目标（申请什么类型的专利，解决什么问题）
                2. 核心主题（技术方案的核心创新点）
                
                文档内容：
                {content[:2000]}...
                
                请以JSON格式返回：
                {{
                    "objective": "总体目标描述",
                    "theme": "核心主题描述"
                }}
                """
                
                response = self.llm_client.generate(prompt)
                try:
                    result = json.loads(response)
                    return result
                except:
                    pass
            
            # 备用分析逻辑
            objective = "申请发明专利，保护技术创新"
            theme = "技术方案创新"
            
            # 简单关键词分析
            if "发明" in content:
                objective = "申请发明专利，保护发明创造"
            if "实用新型" in content:
                objective = "申请实用新型专利，保护技术改进"
            if "外观设计" in content:
                objective = "申请外观设计专利，保护产品外观"
            
            return {
                "objective": objective,
                "theme": theme
            }
            
        except Exception as e:
            return {
                "objective": "申请专利保护技术创新",
                "theme": "技术方案创新"
            }
    
    def _identify_document_sections(self, content: str) -> List[Dict[str, Any]]:
        """识别文档区块"""
        sections = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            for section_type, patterns in self.section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        sections.append({
                            "section_type": section_type.value,
                            "section_name": line,
                            "line_number": line_num + 1,
                            "content_start": line_num + 1,
                            "content_end": None
                        })
                        break
        
        # 确定每个区块的内容范围
        for i, section in enumerate(sections):
            if i < len(sections) - 1:
                section["content_end"] = sections[i + 1]["line_number"] - 1
            else:
                section["content_end"] = len(lines)
        
        return sections
    
    def _identify_patent_fields(self, content: str) -> List[Dict[str, Any]]:
        """识别专利申请书字段"""
        fields = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            for field_key, field_info in self.patent_field_patterns.items():
                for pattern in field_info["patterns"]:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        field = {
                            "field_id": field_key,
                            "field_name": self._extract_field_name(match.group()),
                            "field_type": field_info["field_type"].value,
                            "section": field_info["section"].value,
                            "line_number": line_num + 1,
                            "line_content": line,
                            "match_text": match.group(),
                            "position": match.span(),
                            "constraints": self._serialize_constraints(field_info["constraints"]),
                            "ai_fill_prompt": field_info["ai_fill_prompt"],
                            "related_fields": [],
                            "image_position": None
                        }
                        
                        # 如果是图片字段，设置图片位置信息
                        if field_info["field_type"] == FieldType.IMAGE:
                            field["image_position"] = self._get_image_position_info(line_num, lines)
                        
                        fields.append(field)
                        break
        
        return fields
    
    def _identify_image_positions(self, content: str) -> List[Dict[str, Any]]:
        """识别图片位置"""
        image_positions = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 识别图片占位符
            image_patterns = [
                r"\[图片\d*\]",
                r"\[附图\d*\]",
                r"\[示意图\d*\]",
                r"图\d+",
                r"附图\d+"
            ]
            
            for pattern in image_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    image_positions.append({
                        "position_id": f"img_{len(image_positions) + 1}",
                        "line_number": line_num + 1,
                        "placeholder_text": match.group(),
                        "suggested_size": (400, 300),
                        "description": self._extract_image_description(line),
                        "field_relation": self._find_related_field(line_num, lines)
                    })
        
        return image_positions
    
    def _analyze_logic_consistency(self, fields: List[Dict], sections: List[Dict]) -> Dict[str, str]:
        """分析逻辑一致性"""
        consistency_rules = {
            "basic_info_completeness": "基本信息必须包含发明名称、申请人、申请日期",
            "abstract_background_relation": "摘要内容应与背景技术部分呼应",
            "drawing_claim_consistency": "附图说明应与权利要求书一致",
            "technical_field_accuracy": "技术领域应与发明内容匹配",
            "inventor_application_relation": "发明人信息应与申请人信息一致"
        }
        
        return consistency_rules
    
    def _calculate_patent_confidence(self, fields: List[Dict], sections: List[Dict], 
                                   image_positions: List[Dict]) -> float:
        """计算专利文档分析置信度"""
        confidence = 0.0
        
        # 字段识别置信度
        if fields:
            field_confidence = min(len(fields) / 10.0, 1.0)  # 最多10个字段
            confidence += field_confidence * 0.4
        
        # 区块识别置信度
        if sections:
            section_confidence = min(len(sections) / 6.0, 1.0)  # 最多6个区块
            confidence += section_confidence * 0.3
        
        # 图片位置识别置信度
        if image_positions:
            image_confidence = min(len(image_positions) / 5.0, 1.0)  # 最多5个图片
            confidence += image_confidence * 0.2
        
        # 文档完整性置信度
        completeness_confidence = 0.1
        confidence += completeness_confidence
        
        return min(1.0, confidence)
    
    def _extract_field_name(self, match_text: str) -> str:
        """提取字段名称"""
        # 移除冒号和空白字符
        field_name = re.sub(r'[：:]\s*$', '', match_text)
        return field_name.strip()
    
    def _serialize_constraints(self, constraints: FieldConstraint) -> Dict[str, Any]:
        """序列化约束条件"""
        return {
            "min_length": constraints.min_length,
            "max_length": constraints.max_length,
            "pattern": constraints.pattern,
            "required": constraints.required,
            "options": constraints.options,
            "file_types": constraints.file_types,
            "image_size": constraints.image_size
        }
    
    def _get_image_position_info(self, line_num: int, lines: List[str]) -> Dict[str, Any]:
        """获取图片位置信息"""
        return {
            "line_number": line_num + 1,
            "suggested_size": (400, 300),
            "description": "技术方案示意图",
            "file_types": ["jpg", "jpeg", "png", "gif"]
        }
    
    def _extract_image_description(self, line: str) -> str:
        """提取图片描述"""
        # 简单的图片描述提取
        if "图" in line:
            return "技术方案示意图"
        elif "附图" in line:
            return "专利附图"
        else:
            return "相关图片"
    
    def _find_related_field(self, line_num: int, lines: List[str]) -> str:
        """查找相关字段"""
        # 向上查找最近的字段
        for i in range(line_num - 1, max(0, line_num - 5), -1):
            line = lines[i].strip()
            if any(keyword in line for keyword in ["附图", "图片", "示意图"]):
                return f"field_{i}"
        return ""
    
    def generate_ai_fill_suggestions(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成AI填写建议"""
        try:
            suggestions = {
                "document_objective": analysis_result.get("total_objective", ""),
                "core_theme": analysis_result.get("core_theme", ""),
                "field_suggestions": {},
                "image_suggestions": {},
                "consistency_checks": []
            }
            
            fields = analysis_result.get("fields", [])
            for field in fields:
                field_id = field["field_id"]
                ai_prompt = field.get("ai_fill_prompt", "")
                
                if self.llm_client and ai_prompt:
                    # 使用LLM生成填写建议
                    enhanced_prompt = f"""
                    基于以下专利申请书分析结果，为字段"{field['field_name']}"生成填写建议：
                    
                    文档目标：{analysis_result.get('total_objective', '')}
                    核心主题：{analysis_result.get('core_theme', '')}
                    字段类型：{field['field_type']}
                    填写要求：{ai_prompt}
                    
                    请提供具体的填写建议和示例。
                    """
                    
                    try:
                        suggestion = self.llm_client.generate(enhanced_prompt)
                        suggestions["field_suggestions"][field_id] = suggestion
                    except:
                        suggestions["field_suggestions"][field_id] = ai_prompt
            
            return suggestions
            
        except Exception as e:
            return {"error": f"生成AI填写建议失败: {str(e)}"} 