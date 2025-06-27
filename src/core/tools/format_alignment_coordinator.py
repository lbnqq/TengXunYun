import os
import json
from typing import Dict, Any, List, Tuple, Optional
from .document_format_extractor import DocumentFormatExtractor

class FormatAlignmentCoordinator:
    """
    文档格式对齐协调器
    处理用户的自然语言格式对齐请求，协调多个文档的格式处理
    """
    
    def __init__(self, llm_client=None):
        self.tool_name = "文档格式对齐协调器"
        self.description = "智能处理文档格式对齐请求，支持自然语言交互"
        self.llm_client = llm_client
        self.format_extractor = DocumentFormatExtractor()
        
        # 用户会话状态
        self.session_state = {
            "uploaded_documents": {},  # 存储上传的文档
            "format_templates": {},    # 存储提取的格式模板
            "current_operation": None  # 当前操作状态
        }
    
    def process_user_request(self, user_input: str, uploaded_files: Dict[str, str] = None) -> Dict[str, Any]:
        """
        处理用户的格式对齐请求
        
        Args:
            user_input: 用户输入的自然语言请求
            uploaded_files: 上传的文件 {文件名: 文件内容}
            
        Returns:
            处理结果
        """
        try:
            # 更新会话状态中的文档
            if uploaded_files:
                self.session_state["uploaded_documents"].update(uploaded_files)
            
            # 分析用户意图
            intent_analysis = self._analyze_user_intent(user_input)
            
            # 根据意图执行相应操作
            if intent_analysis["intent"] == "format_alignment":
                return self._handle_format_alignment(intent_analysis, user_input)
            elif intent_analysis["intent"] == "save_template":
                return self._handle_save_template(intent_analysis, user_input)
            elif intent_analysis["intent"] == "list_templates":
                return self._handle_list_templates()
            elif intent_analysis["intent"] == "use_template":
                return self._handle_use_template(intent_analysis, user_input)
            else:
                return self._handle_general_query(user_input)
                
        except Exception as e:
            return {"error": f"处理请求失败: {str(e)}"}
    
    def _analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """分析用户意图"""
        intent_analysis = {
            "intent": "general",
            "confidence": 0.0,
            "entities": {},
            "parameters": {}
        }
        
        user_input_lower = user_input.lower()
        
        # 格式对齐意图识别
        alignment_keywords = ["格式对齐", "格式一致", "格式统一", "对齐格式", "保持格式", "格式相同"]
        if any(keyword in user_input for keyword in alignment_keywords):
            intent_analysis["intent"] = "format_alignment"
            intent_analysis["confidence"] = 0.9
            
            # 提取文档引用
            doc_refs = self._extract_document_references(user_input)
            intent_analysis["entities"]["documents"] = doc_refs
        
        # 保存模板意图识别
        save_keywords = ["保存格式", "保存模板", "记住格式", "存储格式"]
        if any(keyword in user_input for keyword in save_keywords):
            intent_analysis["intent"] = "save_template"
            intent_analysis["confidence"] = 0.8
        
        # 列出模板意图识别
        list_keywords = ["查看模板", "显示模板", "有哪些格式", "模板列表"]
        if any(keyword in user_input for keyword in list_keywords):
            intent_analysis["intent"] = "list_templates"
            intent_analysis["confidence"] = 0.8
        
        # 使用模板意图识别
        use_keywords = ["使用格式", "应用模板", "按照格式"]
        if any(keyword in user_input for keyword in use_keywords):
            intent_analysis["intent"] = "use_template"
            intent_analysis["confidence"] = 0.8
        
        return intent_analysis
    
    def _extract_document_references(self, user_input: str) -> Dict[str, str]:
        """从用户输入中提取文档引用"""
        doc_refs = {"source": None, "target": None}
        
        # 常见的文档引用模式
        patterns = [
            r"文档(\d+|[一二三四五六七八九十]+)",
            r"第(\d+|[一二三四五六七八九十]+)个文档",
            r"(\w+\.(?:txt|doc|docx|pdf))",
        ]
        
        import re
        
        # 查找文档引用
        found_docs = []
        for pattern in patterns:
            matches = re.findall(pattern, user_input)
            found_docs.extend(matches)
        
        # 分析对齐关系
        if "与" in user_input and "对齐" in user_input:
            # 例如："文档1与文档2格式对齐"
            parts = user_input.split("与")
            if len(parts) >= 2:
                # 第一部分通常是源文档
                for doc_name in self.session_state["uploaded_documents"].keys():
                    if doc_name in parts[0] or any(ref in parts[0] for ref in found_docs):
                        doc_refs["source"] = doc_name
                        break
                
                # 第二部分通常是目标文档
                for doc_name in self.session_state["uploaded_documents"].keys():
                    if doc_name in parts[1] or any(ref in parts[1] for ref in found_docs):
                        doc_refs["target"] = doc_name
                        break
        
        # 如果没有明确指定，尝试从上传的文档中推断
        uploaded_docs = list(self.session_state["uploaded_documents"].keys())
        if len(uploaded_docs) >= 2 and not doc_refs["source"]:
            doc_refs["source"] = uploaded_docs[0]
            doc_refs["target"] = uploaded_docs[1]
        
        return doc_refs
    
    def _handle_format_alignment(self, intent_analysis: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """处理格式对齐请求"""
        doc_refs = intent_analysis["entities"].get("documents", {})
        source_doc = doc_refs.get("source")
        target_doc = doc_refs.get("target")
        
        if not source_doc or not target_doc:
            return {
                "response": "请明确指定要对齐的两个文档。例如：'让文档1的格式与文档2对齐'",
                "suggestions": [
                    "上传两个文档",
                    "明确指定源文档和目标文档",
                    "使用类似'文档A与文档B格式对齐'的表达"
                ]
            }
        
        if source_doc not in self.session_state["uploaded_documents"]:
            return {"error": f"找不到源文档: {source_doc}"}
        
        if target_doc not in self.session_state["uploaded_documents"]:
            return {"error": f"找不到目标文档: {target_doc}"}
        
        try:
            # 提取目标文档的格式
            target_content = self.session_state["uploaded_documents"][target_doc]
            format_data = self.format_extractor.extract_format_from_document(target_content, target_doc)
            
            if "error" in format_data:
                return format_data
            
            # 保存格式模板
            save_result = self.format_extractor.save_format_template(format_data)
            if "error" in save_result:
                return save_result
            
            # 应用格式到源文档
            source_content = self.session_state["uploaded_documents"][source_doc]
            alignment_result = self.format_extractor.align_document_format(
                source_content, format_data["template_id"]
            )
            
            if "error" in alignment_result:
                return alignment_result
            
            return {
                "success": True,
                "response": f"已成功将 {source_doc} 的格式对齐到 {target_doc}",
                "source_document": source_doc,
                "target_document": target_doc,
                "template_id": format_data["template_id"],
                "template_name": f"规范格式：{target_doc}",
                "aligned_content": alignment_result["aligned_content"],
                "html_output": alignment_result["html_output"],
                "format_prompt": format_data["format_prompt"],
                "actions": [
                    {
                        "type": "download",
                        "label": "下载对齐后的文档",
                        "data": alignment_result["html_output"]
                    },
                    {
                        "type": "save_template",
                        "label": f"规范格式：{target_doc}",
                        "template_id": format_data["template_id"]
                    }
                ]
            }
            
        except Exception as e:
            return {"error": f"格式对齐处理失败: {str(e)}"}
    
    def _handle_save_template(self, intent_analysis: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """处理保存模板请求"""
        # 实现保存模板逻辑
        return {
            "response": "格式模板保存功能",
            "message": "请指定要保存为模板的文档"
        }
    
    def _handle_list_templates(self) -> Dict[str, Any]:
        """处理列出模板请求"""
        templates = self.format_extractor.list_format_templates()
        
        if not templates:
            return {
                "response": "当前没有保存的格式模板",
                "suggestions": ["上传文档并进行格式对齐以创建模板"]
            }
        
        template_list = []
        for template in templates:
            template_list.append({
                "id": template["template_id"],
                "name": template["name"],
                "description": template["description"],
                "created_time": template["created_time"]
            })
        
        return {
            "response": f"找到 {len(templates)} 个格式模板",
            "templates": template_list,
            "actions": [
                {
                    "type": "use_template",
                    "label": template["description"],
                    "template_id": template["template_id"]
                } for template in templates
            ]
        }
    
    def _handle_use_template(self, intent_analysis: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """处理使用模板请求"""
        # 实现使用模板逻辑
        return {
            "response": "使用格式模板功能",
            "message": "请选择要使用的模板和要应用的文档"
        }
    
    def _handle_general_query(self, user_input: str) -> Dict[str, Any]:
        """处理一般查询"""
        return {
            "response": "我可以帮您进行文档格式对齐。请上传两个文档，然后说'让文档1与文档2格式对齐'",
            "capabilities": [
                "文档格式对齐",
                "格式模板保存和复用",
                "HTML格式输出",
                "Word文档下载"
            ],
            "examples": [
                "让文档1与文档2格式对齐",
                "保存文档2的格式为模板",
                "查看所有格式模板",
                "使用已保存的格式模板"
            ]
        }
    
    def get_session_info(self) -> Dict[str, Any]:
        """获取当前会话信息"""
        return {
            "uploaded_documents": list(self.session_state["uploaded_documents"].keys()),
            "available_templates": len(self.format_extractor.list_format_templates()),
            "current_operation": self.session_state["current_operation"]
        }
    
    def clear_session(self):
        """清除会话状态"""
        self.session_state = {
            "uploaded_documents": {},
            "format_templates": {},
            "current_operation": None
        }
    
    def add_document(self, document_name: str, document_content: str) -> Dict[str, Any]:
        """添加文档到会话"""
        self.session_state["uploaded_documents"][document_name] = document_content
        
        return {
            "success": True,
            "message": f"已添加文档: {document_name}",
            "total_documents": len(self.session_state["uploaded_documents"])
        }
    
    def remove_document(self, document_name: str) -> Dict[str, Any]:
        """从会话中移除文档"""
        if document_name in self.session_state["uploaded_documents"]:
            del self.session_state["uploaded_documents"][document_name]
            return {
                "success": True,
                "message": f"已移除文档: {document_name}"
            }
        else:
            return {
                "error": f"文档不存在: {document_name}"
            }
    
    def use_saved_template(self, template_id: str, document_name: str) -> Dict[str, Any]:
        """使用已保存的模板"""
        if document_name not in self.session_state["uploaded_documents"]:
            return {"error": f"文档不存在: {document_name}"}
        
        document_content = self.session_state["uploaded_documents"][document_name]
        
        # 应用模板
        result = self.format_extractor.align_document_format(document_content, template_id)
        
        if "error" in result:
            return result
        
        # 加载模板信息
        template_data = self.format_extractor.load_format_template(template_id)
        
        return {
            "success": True,
            "response": f"已将 {document_name} 应用格式模板",
            "template_used": template_data.get("document_name", "未知模板"),
            "aligned_content": result["aligned_content"],
            "html_output": result["html_output"],
            "actions": [
                {
                    "type": "download",
                    "label": "下载格式化文档",
                    "data": result["html_output"]
                }
            ]
        }
    
    def align_documents_format(self, source_doc: str, target_doc: str) -> dict:
        """
        直接对齐两个已上传文档的格式，兼容测试用例
        """
        intent_analysis = {
            "intent": "format_alignment",
            "entities": {"documents": {"source": source_doc, "target": target_doc}}
        }
        return self._handle_format_alignment(intent_analysis, "")
