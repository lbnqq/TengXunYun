import re
import json
import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import hashlib

class ComplexDocumentFiller:
    """
    复杂文档智能填充工具
    识别文档中的待填写区域，通过多轮对话获取信息，智能填充文档
    """
    
    def __init__(self, llm_client=None):
        self.tool_name = "复杂文档智能填充工具"
        self.description = "智能识别文档待填写区域，引导用户提供信息，自动填充复杂文档"
        self.llm_client = llm_client
        
        # 常见待填写字段模式
        self.fill_patterns = {
            # 基本信息类
            "personal_info": {
                "patterns": [
                    r"姓名[：:]\s*[_\s]*", r"姓\s*名[：:]\s*[_\s]*",
                    r"性别[：:]\s*[_\s]*", r"年龄[：:]\s*[_\s]*",
                    r"身份证号[：:]\s*[_\s]*", r"电话[：:]\s*[_\s]*",
                    r"手机[：:]\s*[_\s]*", r"邮箱[：:]\s*[_\s]*",
                    r"地址[：:]\s*[_\s]*", r"住址[：:]\s*[_\s]*"
                ],
                "category": "个人信息",
                "required_info": ["姓名", "性别", "年龄", "身份证号", "联系方式", "地址"]
            },
            
            # 时间日期类
            "datetime_info": {
                "patterns": [
                    r"日期[：:]\s*[_\s]*", r"时间[：:]\s*[_\s]*",
                    r"\d{4}年\s*月\s*日", r"年\s*月\s*日",
                    r"申请日期[：:]\s*[_\s]*", r"填表日期[：:]\s*[_\s]*"
                ],
                "category": "日期时间",
                "required_info": ["具体日期"]
            },
            
            # 金额数字类
            "amount_info": {
                "patterns": [
                    r"金额[：:]\s*[_\s]*", r"数量[：:]\s*[_\s]*",
                    r"价格[：:]\s*[_\s]*", r"费用[：:]\s*[_\s]*",
                    r"工资[：:]\s*[_\s]*", r"收入[：:]\s*[_\s]*"
                ],
                "category": "金额数字",
                "required_info": ["具体数值", "单位"]
            },
            
            # 公司机构类
            "organization_info": {
                "patterns": [
                    r"公司[：:]\s*[_\s]*", r"单位[：:]\s*[_\s]*",
                    r"机构[：:]\s*[_\s]*", r"部门[：:]\s*[_\s]*",
                    r"工作单位[：:]\s*[_\s]*", r"所在单位[：:]\s*[_\s]*"
                ],
                "category": "机构信息",
                "required_info": ["机构名称", "地址", "联系方式"]
            },
            
            # 描述文本类
            "description_info": {
                "patterns": [
                    r"说明[：:]\s*[_\s]*", r"描述[：:]\s*[_\s]*",
                    r"备注[：:]\s*[_\s]*", r"详情[：:]\s*[_\s]*",
                    r"原因[：:]\s*[_\s]*", r"情况[：:]\s*[_\s]*"
                ],
                "category": "描述文本",
                "required_info": ["详细描述"]
            }
        }
        
        # 表格识别模式
        self.table_patterns = {
            "header_indicators": ["序号", "项目", "名称", "数量", "金额", "备注", "说明"],
            "empty_cell_patterns": [r"^\s*$", r"^[_\s]+$", r"^\.+$", r"^\-+$"]
        }
    
    def analyze_document_structure(self, document_content: str, document_name: str = None) -> Dict[str, Any]:
        """
        分析文档结构，识别待填写区域
        
        Args:
            document_content: 文档内容
            document_name: 文档名称
            
        Returns:
            文档结构分析结果
        """
        try:
            analysis_result = {
                "document_name": document_name or "未命名文档",
                "total_fields": 0,
                "fill_fields": [],
                "tables": [],
                "structure_info": {},
                "confidence_score": 0.0,
                "analysis_time": datetime.now().isoformat()
            }
            
            # 识别待填写字段
            fill_fields = self._identify_fill_fields(document_content)
            analysis_result["fill_fields"] = fill_fields
            analysis_result["total_fields"] = len(fill_fields)
            
            # 识别表格结构
            tables = self._identify_tables(document_content)
            analysis_result["tables"] = tables
            
            # 分析文档结构
            structure_info = self._analyze_structure(document_content)
            analysis_result["structure_info"] = structure_info
            
            # 计算置信度
            confidence = self._calculate_confidence(fill_fields, tables, structure_info)
            analysis_result["confidence_score"] = confidence
            
            return analysis_result
            
        except Exception as e:
            return {"error": f"文档结构分析失败: {str(e)}"}
    
    def _identify_fill_fields(self, content: str) -> List[Dict[str, Any]]:
        """识别待填写字段"""
        fill_fields = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 检查每种字段类型
            for field_type, field_info in self.fill_patterns.items():
                for pattern in field_info["patterns"]:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        field = {
                            "field_id": f"field_{len(fill_fields) + 1}",
                            "field_type": field_type,
                            "category": field_info["category"],
                            "line_number": line_num + 1,
                            "line_content": line,
                            "match_text": match.group(),
                            "position": match.span(),
                            "context": self._extract_context(lines, line_num),
                            "required_info": field_info["required_info"],
                            "confidence": 0.8,
                            "filled": False,
                            "value": None
                        }
                        
                        # 尝试从上下文推断字段含义
                        field["inferred_meaning"] = self._infer_field_meaning(field)
                        
                        fill_fields.append(field)
        
        return fill_fields
    
    def _identify_tables(self, content: str) -> List[Dict[str, Any]]:
        """识别表格结构"""
        tables = []
        lines = content.split('\n')
        
        # 简单的表格识别逻辑
        current_table = None
        table_id = 0
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            
            # 检查是否是表格标题行
            if self._is_table_header(line):
                if current_table:
                    tables.append(current_table)
                
                table_id += 1
                current_table = {
                    "table_id": f"table_{table_id}",
                    "start_line": line_num + 1,
                    "header": line,
                    "columns": self._parse_table_columns(line),
                    "rows": [],
                    "empty_cells": [],
                    "fill_required": False
                }
            
            # 检查是否是表格数据行
            elif current_table and self._is_table_row(line):
                row_data = self._parse_table_row(line, current_table["columns"])
                current_table["rows"].append({
                    "row_number": len(current_table["rows"]) + 1,
                    "line_number": line_num + 1,
                    "data": row_data,
                    "empty_cells": [i for i, cell in enumerate(row_data) if self._is_empty_cell(cell)]
                })
                
                # 检查是否需要填写
                if any(self._is_empty_cell(cell) for cell in row_data):
                    current_table["fill_required"] = True
            
            # 表格结束
            elif current_table and line == "":
                tables.append(current_table)
                current_table = None
        
        # 添加最后一个表格
        if current_table:
            tables.append(current_table)
        
        return tables
    
    def _is_table_header(self, line: str) -> bool:
        """判断是否是表格标题行"""
        indicators = self.table_patterns["header_indicators"]
        return any(indicator in line for indicator in indicators)
    
    def _is_table_row(self, line: str) -> bool:
        """判断是否是表格数据行"""
        # 简单判断：包含分隔符或多个字段
        separators = ["|", "\t", "  ", "：", ":"]
        return any(sep in line for sep in separators) and len(line.split()) > 1
    
    def _parse_table_columns(self, header_line: str) -> List[str]:
        """解析表格列名"""
        # 简单的列名解析
        separators = ["|", "\t", "  "]
        for sep in separators:
            if sep in header_line:
                return [col.strip() for col in header_line.split(sep) if col.strip()]
        
        # 如果没有明显分隔符，按空格分割
        return [col.strip() for col in header_line.split() if col.strip()]
    
    def _parse_table_row(self, row_line: str, columns: List[str]) -> List[str]:
        """解析表格行数据"""
        separators = ["|", "\t"]
        for sep in separators:
            if sep in row_line:
                cells = [cell.strip() for cell in row_line.split(sep)]
                # 确保单元格数量与列数匹配
                while len(cells) < len(columns):
                    cells.append("")
                return cells[:len(columns)]
        
        # 按空格分割，但要考虑列数
        words = row_line.split()
        if len(words) >= len(columns):
            return words[:len(columns)]
        else:
            cells = words + [""] * (len(columns) - len(words))
            return cells
    
    def _is_empty_cell(self, cell: str) -> bool:
        """判断单元格是否为空"""
        if not cell or cell.isspace():
            return True
        
        for pattern in self.table_patterns["empty_cell_patterns"]:
            if re.match(pattern, cell):
                return True
        
        return False
    
    def _extract_context(self, lines: List[str], line_num: int, context_size: int = 2) -> Dict[str, str]:
        """提取字段上下文"""
        start = max(0, line_num - context_size)
        end = min(len(lines), line_num + context_size + 1)
        
        return {
            "before": "\n".join(lines[start:line_num]),
            "current": lines[line_num],
            "after": "\n".join(lines[line_num + 1:end])
        }
    
    def _infer_field_meaning(self, field: Dict[str, Any]) -> str:
        """推断字段含义"""
        context = field["context"]["current"]
        field_type = field["field_type"]
        
        # 基于上下文和字段类型推断含义
        if field_type == "personal_info":
            if "姓名" in context:
                return "请填写完整姓名"
            elif "性别" in context:
                return "请选择性别（男/女）"
            elif "年龄" in context:
                return "请填写年龄（数字）"
            elif "身份证" in context:
                return "请填写18位身份证号码"
            elif "电话" in context or "手机" in context:
                return "请填写联系电话"
            elif "邮箱" in context:
                return "请填写电子邮箱地址"
            elif "地址" in context or "住址" in context:
                return "请填写详细地址"
        
        elif field_type == "datetime_info":
            return "请填写日期（格式：YYYY年MM月DD日）"
        
        elif field_type == "amount_info":
            return "请填写具体数值和单位"
        
        elif field_type == "organization_info":
            return "请填写机构或公司名称"
        
        elif field_type == "description_info":
            return "请填写详细描述或说明"
        
        return "请填写相关信息"
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """分析文档整体结构"""
        lines = content.split('\n')
        
        return {
            "total_lines": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "has_title": self._has_title(lines),
            "has_signature": self._has_signature(lines),
            "has_date": self._has_date(content),
            "document_type": self._infer_document_type(content)
        }
    
    def _has_title(self, lines: List[str]) -> bool:
        """检查是否有标题"""
        if not lines:
            return False
        
        first_line = lines[0].strip()
        # 简单判断：第一行较短且不包含冒号
        return len(first_line) < 50 and "：" not in first_line and ":" not in first_line
    
    def _has_signature(self, lines: List[str]) -> bool:
        """检查是否有签名"""
        if len(lines) < 2:
            return False
        
        last_lines = lines[-3:]
        signature_indicators = ["签名", "署名", "申请人", "负责人", "日期"]
        
        return any(indicator in line for line in last_lines for indicator in signature_indicators)
    
    def _has_date(self, content: str) -> bool:
        """检查是否包含日期"""
        date_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}/\d{1,2}/\d{4}'
        ]
        
        return any(re.search(pattern, content) for pattern in date_patterns)
    
    def _infer_document_type(self, content: str) -> str:
        """推断文档类型"""
        type_indicators = {
            "申请表": ["申请", "申请表", "申请书"],
            "合同": ["合同", "协议", "甲方", "乙方"],
            "报告": ["报告", "汇报", "总结"],
            "通知": ["通知", "公告", "通告"],
            "表单": ["表单", "登记", "填写"],
            "简历": ["简历", "个人信息", "工作经历", "教育背景"]
        }
        
        for doc_type, indicators in type_indicators.items():
            if any(indicator in content for indicator in indicators):
                return doc_type
        
        return "通用文档"
    
    def _calculate_confidence(self, fill_fields: List[Dict], tables: List[Dict], structure_info: Dict) -> float:
        """计算分析置信度"""
        confidence = 0.0
        
        # 基于识别到的字段数量
        if fill_fields:
            confidence += min(len(fill_fields) * 0.1, 0.4)
        
        # 基于表格识别
        if tables:
            confidence += min(len(tables) * 0.15, 0.3)
        
        # 基于文档结构完整性
        structure_score = sum([
            structure_info.get("has_title", False),
            structure_info.get("has_signature", False),
            structure_info.get("has_date", False)
        ]) / 3
        confidence += structure_score * 0.3
        
        return min(confidence, 1.0)
    
    def generate_fill_questions(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据分析结果生成填写问题
        
        Args:
            analysis_result: 文档分析结果
            
        Returns:
            问题列表
        """
        questions = []
        
        # 按类别组织字段
        fields_by_category = {}
        for field in analysis_result.get("fill_fields", []):
            category = field["category"]
            if category not in fields_by_category:
                fields_by_category[category] = []
            fields_by_category[category].append(field)
        
        # 为每个类别生成问题
        question_id = 1
        for category, fields in fields_by_category.items():
            question = {
                "question_id": f"q_{question_id}",
                "category": category,
                "question_text": self._generate_category_question(category, fields),
                "fields": [field["field_id"] for field in fields],
                "required_info": list(set(info for field in fields for info in field["required_info"])),
                "input_type": self._determine_input_type(category),
                "validation_rules": self._get_validation_rules(category),
                "examples": self._get_examples(category),
                "answered": False,
                "answer": None
            }
            questions.append(question)
            question_id += 1
        
        # 为表格生成问题
        for table in analysis_result.get("tables", []):
            if table.get("fill_required"):
                question = {
                    "question_id": f"q_{question_id}",
                    "category": "表格数据",
                    "question_text": f"请填写表格\"{table.get('header', '未命名表格')}\"中的空白单元格",
                    "table_id": table["table_id"],
                    "table_info": table,
                    "input_type": "table",
                    "answered": False,
                    "answer": None
                }
                questions.append(question)
                question_id += 1
        
        return questions
    
    def _generate_category_question(self, category: str, fields: List[Dict]) -> str:
        """为字段类别生成问题"""
        question_templates = {
            "个人信息": f"请提供您的个人信息，我发现文档中需要填写{len(fields)}个个人信息字段",
            "日期时间": f"请提供相关的日期信息，文档中有{len(fields)}个日期字段需要填写",
            "金额数字": f"请提供相关的数值信息，文档中有{len(fields)}个数值字段需要填写",
            "机构信息": f"请提供机构或公司相关信息，文档中有{len(fields)}个机构字段需要填写",
            "描述文本": f"请提供相关的描述或说明，文档中有{len(fields)}个描述字段需要填写"
        }
        
        return question_templates.get(category, f"请提供{category}相关信息")
    
    def _determine_input_type(self, category: str) -> str:
        """确定输入类型"""
        input_types = {
            "个人信息": "form",
            "日期时间": "date",
            "金额数字": "number",
            "机构信息": "text",
            "描述文本": "textarea"
        }
        
        return input_types.get(category, "text")
    
    def _get_validation_rules(self, category: str) -> Dict[str, Any]:
        """获取验证规则"""
        validation_rules = {
            "个人信息": {
                "姓名": {"required": True, "min_length": 2, "max_length": 10},
                "身份证号": {"required": True, "pattern": r"^\d{18}$"},
                "电话": {"required": True, "pattern": r"^1[3-9]\d{9}$"},
                "邮箱": {"pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}
            },
            "日期时间": {
                "format": "YYYY年MM月DD日",
                "required": True
            },
            "金额数字": {
                "type": "number",
                "min": 0,
                "required": True
            }
        }
        
        return validation_rules.get(category, {})
    
    def _get_examples(self, category: str) -> List[str]:
        """获取示例"""
        examples = {
            "个人信息": ["张三", "男", "25", "北京市朝阳区xxx街道xxx号"],
            "日期时间": ["2024年1月15日", "2024-01-15"],
            "金额数字": ["1000元", "50万", "3.5%"],
            "机构信息": ["北京科技有限公司", "清华大学", "国家发改委"],
            "描述文本": ["详细说明项目背景和目标", "列举主要工作内容"]
        }
        
        return examples.get(category, [])
    
    def fill_document(self, analysis_result: Dict[str, Any], user_answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据用户答案填充文档
        
        Args:
            analysis_result: 文档分析结果
            user_answers: 用户提供的答案
            
        Returns:
            填充结果
        """
        try:
            # 获取原始文档内容（这里需要从分析结果中获取）
            original_content = user_answers.get("original_content", "")
            
            # 创建填充后的内容
            filled_content = original_content
            
            # 填充字段
            for field in analysis_result.get("fill_fields", []):
                field_id = field["field_id"]
                if field_id in user_answers:
                    filled_content = self._fill_field(filled_content, field, user_answers[field_id])
            
            # 填充表格
            for table in analysis_result.get("tables", []):
                table_id = table["table_id"]
                if table_id in user_answers:
                    filled_content = self._fill_table(filled_content, table, user_answers[table_id])
            
            # 生成HTML格式
            html_content = self._generate_html_output(filled_content, analysis_result)
            
            return {
                "success": True,
                "filled_content": filled_content,
                "html_content": html_content,
                "fill_summary": self._generate_fill_summary(analysis_result, user_answers),
                "download_ready": True
            }
            
        except Exception as e:
            return {"error": f"文档填充失败: {str(e)}"}
    
    def _fill_field(self, content: str, field: Dict[str, Any], value: str) -> str:
        """填充单个字段"""
        # 简单的字段替换逻辑
        match_text = field["match_text"]
        
        # 在匹配文本后添加值
        if match_text in content:
            replacement = match_text + value
            content = content.replace(match_text, replacement, 1)
        
        return content
    
    def _fill_table(self, content: str, table: Dict[str, Any], table_data: Dict[str, Any]) -> str:
        """填充表格"""
        # 这里需要更复杂的表格填充逻辑
        # 暂时返回原内容
        return content
    
    def _generate_html_output(self, content: str, analysis_result: Dict[str, Any]) -> str:
        """生成HTML格式输出"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{analysis_result.get('document_name', '填充文档')}</title>
            <style>
                body {{ font-family: 'SimSun', serif; line-height: 1.6; margin: 40px; }}
                .document-title {{ text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 30px; }}
                .content {{ white-space: pre-wrap; }}
                .filled-field {{ background-color: #e8f5e8; padding: 2px 4px; border-radius: 3px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
                th {{ background-color: #f0f0f0; }}
            </style>
        </head>
        <body>
            <div class="document-title">{analysis_result.get('document_name', '填充文档')}</div>
            <div class="content">{self._convert_to_html(content)}</div>
            <script>
                function downloadAsWord() {{
                    const content = document.body.innerHTML;
                    const blob = new Blob([content], {{type: 'application/msword'}});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'filled_document.doc';
                    a.click();
                    URL.revokeObjectURL(url);
                }}
            </script>
            <button onclick="downloadAsWord()" style="margin-top: 20px; padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">下载Word文档</button>
        </body>
        </html>
        """
        
        return html_template
    
    def _convert_to_html(self, content: str) -> str:
        """将文本内容转换为HTML"""
        # 简单的文本到HTML转换
        html_content = content.replace('\n', '<br>')
        return html_content
    
    def _generate_fill_summary(self, analysis_result: Dict[str, Any], user_answers: Dict[str, Any]) -> Dict[str, Any]:
        """生成填充摘要"""
        total_fields = len(analysis_result.get("fill_fields", []))
        filled_fields = len([k for k in user_answers.keys() if k.startswith("field_")])
        
        return {
            "total_fields": total_fields,
            "filled_fields": filled_fields,
            "completion_rate": (filled_fields / total_fields * 100) if total_fields > 0 else 0,
            "document_type": analysis_result.get("structure_info", {}).get("document_type", "未知"),
            "confidence_score": analysis_result.get("confidence_score", 0.0)
        }
