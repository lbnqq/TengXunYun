import json
import os
from typing import Dict, Any, List, Optional
from .complex_document_filler import ComplexDocumentFiller
from .writing_style_analyzer import WritingStyleAnalyzer

class DocumentFillCoordinator:
    """
    文档填充协调器
    管理复杂文档填充的多轮对话流程
    """
    
    def __init__(self, llm_client=None):
        self.tool_name = "文档填充协调器"
        self.description = "协调复杂文档填充的多轮对话流程"
        self.llm_client = llm_client
        self.document_filler = ComplexDocumentFiller(llm_client)
        self.style_analyzer = WritingStyleAnalyzer()
        
        # 会话状态
        self.session_state = {
            "current_document": None,
            "analysis_result": None,
            "questions": [],
            "current_question_index": 0,
            "user_answers": {},
            "conversation_history": [],
            "fill_stage": "initial",  # initial, analyzing, questioning, filling, completed
            "supplementary_materials": {},  # 用户上传的补充材料
            "writing_style_template": None,  # 选择的文风模板
            "content_generation_prompt": self._get_content_generation_prompt()
        }
    
    def start_document_fill(self, document_content: str, document_name: str = None) -> Dict[str, Any]:
        """
        开始文档填充流程
        
        Args:
            document_content: 文档内容
            document_name: 文档名称
            
        Returns:
            初始分析结果和第一个问题
        """
        try:
            # 重置会话状态
            self._reset_session()
            
            # 保存文档信息
            self.session_state["current_document"] = {
                "content": document_content,
                "name": document_name or "未命名文档"
            }
            self.session_state["fill_stage"] = "analyzing"
            
            # 分析文档结构
            analysis_result = self.document_filler.analyze_document_structure(
                document_content, document_name
            )
            
            if "error" in analysis_result:
                return analysis_result
            
            self.session_state["analysis_result"] = analysis_result
            
            # 生成填写问题
            questions = self.document_filler.generate_fill_questions(analysis_result)
            self.session_state["questions"] = questions
            self.session_state["fill_stage"] = "questioning"
            
            # 生成初始响应
            response = self._generate_initial_response(analysis_result, questions)
            
            return response
            
        except Exception as e:
            return {"error": f"文档填充初始化失败: {str(e)}"}
    
    def process_user_response(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户回复
        
        Args:
            user_input: 用户输入
            
        Returns:
            处理结果和下一步指引
        """
        try:
            # 记录对话历史
            self.session_state["conversation_history"].append({
                "type": "user",
                "content": user_input,
                "timestamp": self._get_timestamp()
            })

            # 检查是否是特殊指令
            if self._is_special_command(user_input):
                return self._handle_special_command(user_input)
            
            current_stage = self.session_state["fill_stage"]
            
            if current_stage == "questioning":
                return self._handle_questioning_stage(user_input)
            elif current_stage == "filling":
                return self._handle_filling_stage(user_input)
            elif current_stage == "completed":
                return self._handle_completed_stage(user_input)
            else:
                return {"error": "无效的填充阶段"}
                
        except Exception as e:
            return {"error": f"处理用户回复失败: {str(e)}"}
    
    def _handle_questioning_stage(self, user_input: str) -> Dict[str, Any]:
        """处理问答阶段"""
        current_index = self.session_state["current_question_index"]
        questions = self.session_state["questions"]
        
        if current_index >= len(questions):
            # 所有问题已回答，开始填充
            return self._start_filling_process()
        
        current_question = questions[current_index]
        
        # 解析用户答案
        parsed_answer = self._parse_user_answer(user_input, current_question)
        
        if parsed_answer.get("valid"):
            # 保存答案
            self._save_answer(current_question, parsed_answer["data"])
            
            # 移动到下一个问题
            self.session_state["current_question_index"] += 1
            
            if self.session_state["current_question_index"] >= len(questions):
                # 所有问题已回答
                return self._start_filling_process()
            else:
                # 提出下一个问题
                return self._ask_next_question()
        else:
            # 答案无效，重新询问
            return self._request_clarification(current_question, parsed_answer.get("error"))
    
    def _handle_filling_stage(self, user_input: str) -> Dict[str, Any]:
        """处理填充阶段"""
        # 在填充阶段，用户可能要求修改某些信息
        if "修改" in user_input or "更改" in user_input:
            return self._handle_modification_request(user_input)
        elif "确认" in user_input or "完成" in user_input:
            return self._finalize_document()
        else:
            return {
                "response": "文档填充已完成，您可以：\n1. 说'确认'完成填充\n2. 说'修改XXX'来修改特定信息\n3. 下载填充后的文档",
                "stage": "filling",
                "actions": ["confirm", "modify", "download"]
            }
    
    def _handle_completed_stage(self, user_input: str) -> Dict[str, Any]:
        """处理完成阶段"""
        if "重新" in user_input or "再次" in user_input:
            return self._restart_process()
        else:
            return {
                "response": "文档填充已完成！您可以下载填充后的文档，或者上传新文档重新开始。",
                "stage": "completed",
                "actions": ["download", "restart"]
            }
    
    def _generate_initial_response(self, analysis_result: Dict[str, Any], questions: List[Dict]) -> Dict[str, Any]:
        """生成初始响应"""
        total_fields = analysis_result.get("total_fields", 0)
        confidence = analysis_result.get("confidence_score", 0.0)
        doc_type = analysis_result.get("structure_info", {}).get("document_type", "未知")
        
        response_text = f"""
📄 文档分析完成！

**文档信息：**
- 文档类型：{doc_type}
- 识别到 {total_fields} 个待填写字段
- 分析置信度：{confidence:.1%}

**需要填写的信息类别：**
"""
        
        for i, question in enumerate(questions, 1):
            response_text += f"{i}. {question['category']}\n"
        
        response_text += f"\n我将逐步引导您填写这些信息。让我们从第一个开始：\n\n"
        
        # 添加第一个问题
        if questions:
            first_question = questions[0]
            response_text += self._format_question(first_question)
        
        return {
            "response": response_text,
            "stage": "questioning",
            "analysis_result": analysis_result,
            "total_questions": len(questions),
            "current_question": 1,
            "progress": 0
        }
    
    def _format_question(self, question: Dict[str, Any]) -> str:
        """格式化问题"""
        question_text = f"**{question['category']}**\n"
        question_text += f"{question['question_text']}\n\n"
        
        if question.get("required_info"):
            question_text += "需要提供的信息：\n"
            for info in question["required_info"]:
                question_text += f"- {info}\n"
        
        if question.get("examples"):
            question_text += f"\n示例：{', '.join(question['examples'])}\n"
        
        question_text += "\n请提供相关信息："
        
        return question_text
    
    def _parse_user_answer(self, user_input: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """解析用户答案"""
        category = question["category"]
        input_type = question.get("input_type", "text")
        
        # 基本验证
        if not user_input.strip():
            return {"valid": False, "error": "请提供有效的信息"}
        
        # 根据类别进行特定验证
        if category == "个人信息":
            return self._validate_personal_info(user_input, question)
        elif category == "日期时间":
            return self._validate_datetime_info(user_input)
        elif category == "金额数字":
            return self._validate_amount_info(user_input)
        elif category == "机构信息":
            return self._validate_organization_info(user_input)
        elif category == "描述文本":
            return self._validate_description_info(user_input)
        elif category == "表格数据":
            return self._validate_table_data(user_input, question)
        else:
            return {"valid": True, "data": {"raw_input": user_input}}
    
    def _validate_personal_info(self, user_input: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """验证个人信息"""
        # 尝试从用户输入中提取结构化信息
        info_data = {}
        
        # 简单的信息提取逻辑
        lines = user_input.strip().split('\n')
        for line in lines:
            line = line.strip()
            if '：' in line or ':' in line:
                key, value = line.split('：' if '：' in line else ':', 1)
                info_data[key.strip()] = value.strip()
            elif line:
                # 如果没有明确的键值对，尝试智能识别
                if len(line) <= 10 and not any(char.isdigit() for char in line):
                    info_data["姓名"] = line
                elif line.isdigit() and len(line) <= 3:
                    info_data["年龄"] = line
                elif len(line) == 18 and line.isdigit():
                    info_data["身份证号"] = line
                elif '@' in line:
                    info_data["邮箱"] = line
                elif line.startswith('1') and len(line) == 11:
                    info_data["电话"] = line
        
        if not info_data:
            return {"valid": False, "error": "请提供清晰的个人信息，建议使用'姓名：张三'的格式"}
        
        return {"valid": True, "data": info_data}
    
    def _validate_datetime_info(self, user_input: str) -> Dict[str, Any]:
        """验证日期时间信息"""
        import re
        
        # 检查日期格式
        date_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}/\d{1,2}/\d{4}'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, user_input):
                return {"valid": True, "data": {"date": user_input.strip()}}
        
        return {"valid": False, "error": "请提供正确的日期格式，如：2024年1月15日"}
    
    def _validate_amount_info(self, user_input: str) -> Dict[str, Any]:
        """验证金额数字信息"""
        import re
        
        # 提取数字
        numbers = re.findall(r'\d+\.?\d*', user_input)
        if numbers:
            return {"valid": True, "data": {"amount": user_input.strip(), "number": numbers[0]}}
        
        return {"valid": False, "error": "请提供具体的数值信息"}
    
    def _validate_organization_info(self, user_input: str) -> Dict[str, Any]:
        """验证机构信息"""
        if len(user_input.strip()) < 2:
            return {"valid": False, "error": "请提供完整的机构名称"}
        
        return {"valid": True, "data": {"organization": user_input.strip()}}
    
    def _validate_description_info(self, user_input: str) -> Dict[str, Any]:
        """验证描述信息"""
        if len(user_input.strip()) < 5:
            return {"valid": False, "error": "请提供更详细的描述信息"}
        
        return {"valid": True, "data": {"description": user_input.strip()}}
    
    def _validate_table_data(self, user_input: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """验证表格数据"""
        # 简单的表格数据验证
        return {"valid": True, "data": {"table_data": user_input.strip()}}
    
    def _save_answer(self, question: Dict[str, Any], answer_data: Dict[str, Any]):
        """保存答案"""
        question_id = question["question_id"]
        self.session_state["user_answers"][question_id] = answer_data
        
        # 标记问题为已回答
        for q in self.session_state["questions"]:
            if q["question_id"] == question_id:
                q["answered"] = True
                q["answer"] = answer_data
                break
    
    def _ask_next_question(self) -> Dict[str, Any]:
        """提出下一个问题"""
        current_index = self.session_state["current_question_index"]
        questions = self.session_state["questions"]
        
        if current_index < len(questions):
            next_question = questions[current_index]
            progress = (current_index / len(questions)) * 100
            
            response_text = f"✅ 信息已保存！\n\n"
            response_text += f"进度：{current_index}/{len(questions)} ({progress:.0f}%)\n\n"
            response_text += self._format_question(next_question)
            
            return {
                "response": response_text,
                "stage": "questioning",
                "current_question": current_index + 1,
                "total_questions": len(questions),
                "progress": progress
            }
        
        return self._start_filling_process()
    
    def _request_clarification(self, question: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """请求澄清"""
        response_text = f"❌ {error_message}\n\n"
        response_text += "让我们重新来：\n\n"
        response_text += self._format_question(question)
        
        return {
            "response": response_text,
            "stage": "questioning",
            "need_clarification": True
        }
    
    def _start_filling_process(self) -> Dict[str, Any]:
        """开始填充过程"""
        self.session_state["fill_stage"] = "filling"
        
        # 准备填充数据
        fill_data = self._prepare_fill_data()
        
        # 执行文档填充
        analysis_result = self.session_state["analysis_result"]
        fill_result = self.document_filler.fill_document(analysis_result, fill_data)
        
        if "error" in fill_result:
            return fill_result
        
        self.session_state["fill_result"] = fill_result
        
        response_text = "🎉 所有信息收集完成！正在填充文档...\n\n"
        response_text += "**填充摘要：**\n"
        
        summary = fill_result.get("fill_summary", {})
        response_text += f"- 总字段数：{summary.get('total_fields', 0)}\n"
        response_text += f"- 已填充：{summary.get('filled_fields', 0)}\n"
        response_text += f"- 完成度：{summary.get('completion_rate', 0):.1f}%\n\n"
        
        response_text += "文档填充完成！您可以：\n"
        response_text += "1. 说'确认'完成填充\n"
        response_text += "2. 说'修改XXX'来修改特定信息\n"
        response_text += "3. 直接下载填充后的文档"
        
        return {
            "response": response_text,
            "stage": "filling",
            "fill_result": fill_result,
            "actions": ["confirm", "modify", "download"]
        }
    
    def _prepare_fill_data(self) -> Dict[str, Any]:
        """准备填充数据"""
        fill_data = {"original_content": self.session_state["current_document"]["content"]}
        
        # 转换用户答案为填充格式
        for question_id, answer_data in self.session_state["user_answers"].items():
            # 找到对应的问题
            question = next((q for q in self.session_state["questions"] if q["question_id"] == question_id), None)
            if question:
                # 根据问题类型处理答案
                if "fields" in question:
                    for field_id in question["fields"]:
                        fill_data[field_id] = answer_data
                elif "table_id" in question:
                    fill_data[question["table_id"]] = answer_data
        
        return fill_data
    
    def _handle_modification_request(self, user_input: str) -> Dict[str, Any]:
        """处理修改请求"""
        # 简单的修改处理逻辑
        return {
            "response": "请告诉我您想修改哪个具体信息，我会重新询问相关问题。",
            "stage": "filling",
            "modification_requested": True
        }
    
    def _finalize_document(self) -> Dict[str, Any]:
        """完成文档填充"""
        self.session_state["fill_stage"] = "completed"
        
        fill_result = self.session_state.get("fill_result", {})
        
        return {
            "response": "🎉 文档填充已完成！您可以下载填充后的文档。",
            "stage": "completed",
            "final_result": fill_result,
            "download_ready": True
        }
    
    def _restart_process(self) -> Dict[str, Any]:
        """重新开始流程"""
        self._reset_session()
        return {
            "response": "已重置填充流程。请上传新的文档开始填充。",
            "stage": "initial"
        }
    
    def _reset_session(self):
        """重置会话状态"""
        self.session_state = {
            "current_document": None,
            "analysis_result": None,
            "questions": [],
            "current_question_index": 0,
            "user_answers": {},
            "conversation_history": [],
            "fill_stage": "initial"
        }
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

    def _get_content_generation_prompt(self) -> str:
        """获取内容生成的系统提示词"""
        return """
你是一个专业的文档内容生成助手。在生成任何内容时，请严格遵循以下要求：

【写作风格要求】
1. 长短句结合：避免连续使用长句或短句，保持节奏感
2. 减少被动句式：优先使用主动语态，让表达更直接有力
3. 自然流畅：避免机械化表达，让内容读起来像人类撰写
4. 简洁明了：去除冗余词汇，每个词都有其存在价值

【去AIGC痕迹】
- 避免使用"首先、其次、最后"等机械化过渡词
- 不要使用"值得注意的是"、"需要强调的是"等AI常用表达
- 减少使用"进行"、"实施"、"开展"等动词
- 避免过度使用"的"字结构
- 不要出现"综上所述"、"总而言之"等总结性套话

【内容质量】
- 信息准确：确保所有事实和数据的准确性
- 逻辑清晰：内容结构合理，前后呼应
- 针对性强：根据具体场景和用户需求定制内容
- 专业度适中：既要专业又要通俗易懂

【特殊要求】
- 如果用户提供了文风参考，严格按照参考文风的语言习惯、句式结构、用词偏好进行内容生成
- 保持与用户身份和角色相符的语言风格
- 根据文档类型调整正式程度和专业术语使用

请在生成内容时将这些要求内化，让输出内容自然、专业、符合人类写作习惯。
"""

    def add_supplementary_material(self, material_name: str, material_content: str) -> Dict[str, Any]:
        """添加补充材料"""
        self.session_state["supplementary_materials"][material_name] = {
            "content": material_content,
            "added_time": self._get_timestamp(),
            "type": self._detect_material_type(material_content)
        }

        return {
            "success": True,
            "message": f"已添加补充材料: {material_name}",
            "total_materials": len(self.session_state["supplementary_materials"])
        }

    def _detect_material_type(self, content: str) -> str:
        """检测补充材料类型"""
        content_lower = content.lower()

        if any(keyword in content_lower for keyword in ["简历", "履历", "个人信息", "工作经历"]):
            return "个人简历"
        elif any(keyword in content_lower for keyword in ["合同", "协议", "条款"]):
            return "合同文档"
        elif any(keyword in content_lower for keyword in ["报告", "总结", "分析"]):
            return "报告文档"
        elif any(keyword in content_lower for keyword in ["证书", "证明", "资质"]):
            return "证明材料"
        else:
            return "参考文档"

    def set_writing_style_template(self, template_id: str) -> Dict[str, Any]:
        """设置文风模板"""
        # 这里需要从文风模板存储中加载
        # 暂时返回成功状态
        self.session_state["writing_style_template"] = template_id

        return {
            "success": True,
            "message": f"已设置文风模板: {template_id}",
            "template_id": template_id
        }

    def _is_special_command(self, user_input: str) -> bool:
        """检查是否是特殊指令"""
        special_keywords = [
            "上传补充材料", "添加参考文档", "设置文风", "选择文风模板",
            "查看文风模板", "分析文风", "润色", "优化文风"
        ]
        return any(keyword in user_input for keyword in special_keywords)

    def _handle_special_command(self, user_input: str) -> Dict[str, Any]:
        """处理特殊指令"""
        if "上传补充材料" in user_input or "添加参考文档" in user_input:
            return {
                "response": "请上传您的补充材料。支持的材料类型包括：\n- 个人简历（提供个人信息参考）\n- 工作证明（提供工作经历参考）\n- 项目文档（提供项目经验参考）\n- 其他相关文档\n\n上传后我会自动分析并在填写时参考这些材料。",
                "stage": self.session_state["fill_stage"],
                "action_required": "upload_material"
            }

        elif "设置文风" in user_input or "选择文风模板" in user_input:
            templates = self.style_analyzer.list_style_templates()
            if not templates:
                return {
                    "response": "当前没有保存的文风模板。您可以：\n1. 上传一份您喜欢的范文，我来分析其文风特征\n2. 继续使用默认的文风生成内容",
                    "stage": self.session_state["fill_stage"],
                    "action_required": "upload_style_reference"
                }
            else:
                template_list = "\n".join([f"- {t['name']} ({t['style_name']})" for t in templates])
                return {
                    "response": f"找到以下文风模板：\n{template_list}\n\n请告诉我您想使用哪个模板，或者上传新的范文来创建文风模板。",
                    "stage": self.session_state["fill_stage"],
                    "available_templates": templates,
                    "action_required": "select_style_template"
                }

        elif "查看文风模板" in user_input:
            return self._show_style_templates()

        elif "分析文风" in user_input:
            return {
                "response": "请上传您希望分析文风的范文，我会分析其写作特征并生成相应的文风模板。",
                "stage": self.session_state["fill_stage"],
                "action_required": "upload_style_reference"
            }

        else:
            return {
                "response": "我理解您的需求。请具体说明您想要什么帮助，或者继续回答当前的填写问题。",
                "stage": self.session_state["fill_stage"]
            }

    def _show_style_templates(self) -> Dict[str, Any]:
        """显示文风模板"""
        templates = self.style_analyzer.list_style_templates()

        if not templates:
            return {
                "response": "当前没有保存的文风模板。您可以上传范文来创建文风模板。",
                "stage": self.session_state["fill_stage"]
            }

        response_text = f"找到 {len(templates)} 个文风模板：\n\n"

        for template in templates:
            response_text += f"**{template['name']}**\n"
            response_text += f"- 文风类型：{template['style_name']}\n"
            response_text += f"- 置信度：{template['confidence_score']:.1%}\n"
            response_text += f"- 创建时间：{template['created_time'][:10]}\n\n"

        response_text += "您可以说'使用XXX模板'来选择特定的文风模板。"

        return {
            "response": response_text,
            "stage": self.session_state["fill_stage"],
            "available_templates": templates
        }

    def analyze_and_save_writing_style(self, reference_content: str, reference_name: str) -> Dict[str, Any]:
        """分析并保存文风模板"""
        try:
            # 分析文风
            analysis_result = self.style_analyzer.analyze_writing_style(reference_content, reference_name)

            if "error" in analysis_result:
                return analysis_result

            # 保存文风模板
            save_result = self.style_analyzer.save_style_template(analysis_result)

            if "error" in save_result:
                return save_result

            return {
                "success": True,
                "message": f"已分析并保存文风模板：{reference_name}",
                "template_id": analysis_result["template_id"],
                "style_type": analysis_result["style_type"],
                "style_name": self.style_analyzer.style_types.get(analysis_result["style_type"], {}).get("name", "未知风格"),
                "confidence_score": analysis_result["confidence_score"],
                "style_prompt": analysis_result["style_prompt"]
            }

        except Exception as e:
            return {"error": f"文风分析失败: {str(e)}"}

    def apply_writing_style_to_content(self, content: str, template_id: str = None) -> str:
        """将文风应用到内容生成"""
        if not template_id:
            template_id = self.session_state.get("writing_style_template")

        if not template_id:
            # 使用默认的内容生成提示词
            return self.session_state["content_generation_prompt"] + "\n\n" + content

        # 加载文风模板
        template_data = self.style_analyzer.load_style_template(template_id)

        if "error" in template_data:
            # 如果模板加载失败，使用默认提示词
            return self.session_state["content_generation_prompt"] + "\n\n" + content

        # 组合文风提示词和内容生成提示词
        style_prompt = template_data.get("style_prompt", "")
        base_prompt = self.session_state["content_generation_prompt"]

        combined_prompt = f"{base_prompt}\n\n{style_prompt}\n\n请根据以上要求生成内容：\n{content}"

        return combined_prompt
    
    def get_session_status(self) -> Dict[str, Any]:
        """获取会话状态"""
        return {
            "stage": self.session_state["fill_stage"],
            "document_name": self.session_state.get("current_document", {}).get("name"),
            "total_questions": len(self.session_state["questions"]),
            "answered_questions": self.session_state["current_question_index"],
            "progress": (self.session_state["current_question_index"] / len(self.session_state["questions"]) * 100) if self.session_state["questions"] else 0
        }
    
    def get_fill_result(self) -> Dict[str, Any]:
        """获取填充结果"""
        return self.session_state.get("fill_result", {})
    
    def auto_match_data(self, session_id: str, data_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        自动匹配数据到文档字段
        
        Args:
            session_id: 会话ID
            data_sources: 数据源列表
            
        Returns:
            匹配结果
        """
        try:
            if not self.session_state.get("analysis_result"):
                return {"error": "文档尚未分析，请先上传文档"}
            
            analysis_result = self.session_state["analysis_result"]
            fill_fields = analysis_result.get("fill_fields", [])
            
            # 提取所有数据源的内容
            all_data = {}
            for source in data_sources:
                source_type = source.get("type", "")
                source_name = source.get("name", "")
                source_content = source.get("content", "")
                
                if source_type == "text":
                    # 解析文本数据
                    text_data = self._parse_text_data(source_content)
                    all_data.update(text_data)
                elif source_type == "file":
                    # 解析文件数据
                    file_data = self._parse_file_data(source_content, source_name)
                    all_data.update(file_data)
                elif source_type == "user_input":
                    # 用户输入数据
                    all_data[source_name] = source_content
            
            # 执行字段匹配
            matched_fields = {}
            unmatched_fields = []
            confidence_scores = {}
            conflicts = []
            
            for field in fill_fields:
                field_id = field["field_id"]
                field_category = field["category"]
                field_meaning = field.get("inferred_meaning", "")
                
                # 尝试匹配字段
                match_result = self._match_field_to_data(field, all_data)
                
                if match_result["matched"]:
                    if match_result["confidence"] > 0.7:  # 高置信度直接匹配
                        matched_fields[field_id] = match_result["value"]
                        confidence_scores[field_id] = match_result["confidence"]
                    else:
                        # 低置信度或有冲突
                        conflicts.append({
                            "field_id": field_id,
                            "field_name": field_meaning or field_id,
                            "options": [{
                                "value": match_result["value"],
                                "source": match_result["source"],
                                "confidence": match_result["confidence"]
                            }]
                        })
                else:
                    unmatched_fields.append(field_id)
            
            return {
                "success": True,
                "matched_fields": matched_fields,
                "unmatched_fields": unmatched_fields,
                "confidence_scores": confidence_scores,
                "conflicts": conflicts,
                "total_fields": len(fill_fields),
                "matched_count": len(matched_fields),
                "unmatched_count": len(unmatched_fields),
                "conflict_count": len(conflicts)
            }
            
        except Exception as e:
            return {"error": f"自动匹配数据失败: {str(e)}"}
    
    def resolve_conflicts(self, session_id: str, resolutions: Dict[str, str]) -> Dict[str, Any]:
        """
        解决自动匹配中的冲突
        
        Args:
            session_id: 会话ID
            resolutions: 冲突解决方案
            
        Returns:
            解决结果
        """
        try:
            resolved_fields = {}
            
            for field_id, selected_value in resolutions.items():
                resolved_fields[field_id] = selected_value
                
                # 更新会话状态中的用户答案
                self.session_state["user_answers"][field_id] = selected_value
            
            return {
                "success": True,
                "resolved_fields": resolved_fields,
                "total_resolved": len(resolved_fields)
            }
            
        except Exception as e:
            return {"error": f"解决冲突失败: {str(e)}"}
    
    def _parse_text_data(self, text_content: str) -> Dict[str, str]:
        """解析文本数据"""
        data = {}
        lines = text_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if '：' in line or ':' in line:
                key, value = line.split('：' if '：' in line else ':', 1)
                data[key.strip()] = value.strip()
            elif line and len(line) < 50:  # 短行可能是字段值
                # 尝试智能识别字段类型
                if len(line) <= 10 and not any(char.isdigit() for char in line):
                    data["姓名"] = line
                elif line.isdigit() and len(line) <= 3:
                    data["年龄"] = line
                elif len(line) == 18 and line.isdigit():
                    data["身份证号"] = line
                elif '@' in line:
                    data["邮箱"] = line
                elif line.startswith('1') and len(line) == 11:
                    data["电话"] = line
        
        return data
    
    def _parse_file_data(self, file_content: str, file_name: str) -> Dict[str, str]:
        """解析文件数据"""
        data = {}
        
        # 根据文件名推断数据类型
        file_lower = file_name.lower()
        
        if any(keyword in file_lower for keyword in ['简历', '履历', 'cv']):
            # 简历文件解析
            data.update(self._parse_resume_data(file_content))
        elif any(keyword in file_lower for keyword in ['合同', '协议']):
            # 合同文件解析
            data.update(self._parse_contract_data(file_content))
        else:
            # 通用文件解析
            data.update(self._parse_text_data(file_content))
        
        return data
    
    def _parse_resume_data(self, content: str) -> Dict[str, str]:
        """解析简历数据"""
        data = {}
        
        # 简单的简历信息提取
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if '姓名' in line and '：' in line:
                data["姓名"] = line.split('：', 1)[1].strip()
            elif '电话' in line and '：' in line:
                data["电话"] = line.split('：', 1)[1].strip()
            elif '邮箱' in line and '：' in line:
                data["邮箱"] = line.split('：', 1)[1].strip()
            elif '地址' in line and '：' in line:
                data["地址"] = line.split('：', 1)[1].strip()
        
        return data
    
    def _parse_contract_data(self, content: str) -> Dict[str, str]:
        """解析合同数据"""
        data = {}
        
        # 简单的合同信息提取
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if '甲方' in line and '：' in line:
                data["甲方"] = line.split('：', 1)[1].strip()
            elif '乙方' in line and '：' in line:
                data["乙方"] = line.split('：', 1)[1].strip()
            elif '金额' in line and '：' in line:
                data["金额"] = line.split('：', 1)[1].strip()
            elif '日期' in line and '：' in line:
                data["日期"] = line.split('：', 1)[1].strip()
        
        return data
    
    def _match_field_to_data(self, field: Dict[str, Any], all_data: Dict[str, str]) -> Dict[str, Any]:
        """匹配字段到数据"""
        field_meaning = field.get("inferred_meaning", "")
        field_category = field["category"]
        field_type = field["field_type"]
        
        best_match = None
        best_confidence = 0.0
        best_source = ""
        
        # 基于字段含义匹配
        if field_meaning:
            for key, value in all_data.items():
                confidence = self._calculate_field_confidence(field_meaning, key, value, field_category)
                if confidence > best_confidence:
                    best_match = value
                    best_confidence = confidence
                    best_source = key
        
        # 基于字段类型匹配
        if not best_match or best_confidence < 0.5:
            for key, value in all_data.items():
                confidence = self._calculate_type_confidence(field_type, field_category, key, value)
                if confidence > best_confidence:
                    best_match = value
                    best_confidence = confidence
                    best_source = key
        
        return {
            "matched": best_match is not None and best_confidence > 0.3,
            "value": best_match or "",
            "confidence": best_confidence,
            "source": best_source
        }
    
    def _calculate_field_confidence(self, field_meaning: str, data_key: str, data_value: str, field_category: str) -> float:
        """计算字段匹配置信度"""
        confidence = 0.0
        
        # 精确匹配
        if field_meaning.lower() == data_key.lower():
            confidence += 0.8
        elif field_meaning in data_key or data_key in field_meaning:
            confidence += 0.6
        
        # 类别匹配
        if field_category == "个人信息" and any(keyword in data_key for keyword in ["姓名", "电话", "邮箱", "地址"]):
            confidence += 0.3
        elif field_category == "日期时间" and any(keyword in data_key for keyword in ["日期", "时间", "年", "月", "日"]):
            confidence += 0.3
        elif field_category == "金额数字" and any(keyword in data_key for keyword in ["金额", "数量", "价格", "费用"]):
            confidence += 0.3
        
        # 值格式匹配
        if field_category == "日期时间" and any(char in data_value for char in ["年", "月", "日", "-", "/"]):
            confidence += 0.2
        elif field_category == "金额数字" and any(char in data_value for char in ["元", "万", "千", ".", ","]):
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def _calculate_type_confidence(self, field_type: str, field_category: str, data_key: str, data_value: str) -> float:
        """计算类型匹配置信度"""
        confidence = 0.0
        
        # 基于字段类型匹配
        if field_type == "personal_info":
            if any(keyword in data_key for keyword in ["姓名", "电话", "邮箱", "地址", "身份证"]):
                confidence += 0.5
        elif field_type == "datetime_info":
            if any(keyword in data_key for keyword in ["日期", "时间", "年", "月", "日"]):
                confidence += 0.5
        elif field_type == "amount_info":
            if any(keyword in data_key for keyword in ["金额", "数量", "价格", "费用"]):
                confidence += 0.5
        
        # 基于值格式匹配
        if field_type == "datetime_info" and any(char in data_value for char in ["年", "月", "日", "-", "/"]):
            confidence += 0.3
        elif field_type == "amount_info" and any(char in data_value for char in ["元", "万", "千", ".", ","]):
            confidence += 0.3
        
        return min(1.0, confidence)
