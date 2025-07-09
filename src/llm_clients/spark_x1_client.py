#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星火X1大模型客户端 - 智能填报模块专用

Author: AI Assistant (Claude)
Created: 2025-07-08
Last Modified: 2025-07-08
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0 - 集成星火X1 HTTP接口
License: MIT
"""

import os
import json
import logging
import requests
import re
import tempfile
from typing import Dict, Any, Optional, List
from datetime import datetime
from docx import Document

class SparkX1Client:
    """星火X1大模型HTTP客户端 - 专为智能填报设计"""
    
    def __init__(self, api_password: str = None):
        """
        初始化星火X1客户端
        
        Args:
            api_password: 星火X1的APIPassword (格式: AK:SK)
        """
        self.api_password = api_password or os.getenv('SPARK_X1_API_PASSWORD')
        if not self.api_password:
            raise ValueError("缺少星火X1 APIPassword配置")
        
        self.base_url = "https://spark-api-open.xf-yun.com/v2/chat/completions"
        self.model = "x1"
        self.logger = logging.getLogger(__name__)
        
        # 验证APIPassword格式
        if ':' not in self.api_password:
            raise ValueError("APIPassword格式错误，应为 AK:SK 格式")
    
    def _call_api(self, messages: List[Dict[str, str]], stream: bool = False, **kwargs) -> Dict[str, Any]:
        """
        调用星火X1 API
        
        Args:
            messages: 对话消息列表
            stream: 是否流式返回
            **kwargs: 其他参数
            
        Returns:
            API响应结果
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_password}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "user": kwargs.get("user", "smart_form_filler"),
                "messages": messages,
                "stream": stream,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4096)
            }
            
            self.logger.info(f"调用星火X1 API，消息数量: {len(messages)}")
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=kwargs.get("timeout", 180)
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    return result
                else:
                    raise Exception(f"API返回错误: {result.get('message', '未知错误')}")
            else:
                raise Exception(f"HTTP请求失败: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"星火X1 API调用失败: {e}")
            raise
    
    def generate_summary(self, work_content: str) -> Dict[str, Any]:
        """
        生成年度总结
        
        Args:
            work_content: 工作内容描述
            
        Returns:
            生成结果 {'success': bool, 'content': str, 'file_path': str, 'filename': str}
        """
        try:
            prompt = f"""
请根据以下工作内容，生成一份专业的年度工作总结，要求：

1. 总结格式要正式、专业
2. 内容要条理清晰，逻辑性强
3. 突出工作成果和个人成长
4. 字数控制在800-1200字之间
5. 包含工作回顾、主要成就、经验总结、不足反思、未来规划等部分

工作内容：
{work_content}

请直接输出年度总结内容，不需要额外的说明。
"""
            
            messages = [{"role": "user", "content": prompt}]
            result = self._call_api(messages, timeout=120)
            
            # 提取生成的内容
            content = result["choices"][0]["message"]["content"]
            
            # 生成Word文档
            doc_result = self._create_summary_document(content)
            
            return {
                "success": True,
                "content": content,
                "file_path": doc_result["file_path"],
                "filename": doc_result["filename"],
                "usage": result.get("usage", {})
            }
            
        except Exception as e:
            self.logger.error(f"生成年度总结失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "file_path": None,
                "filename": None
            }
    
    def generate_resume(self, personal_info: str) -> Dict[str, Any]:
        """
        生成个人简历
        
        Args:
            personal_info: 个人信息描述
            
        Returns:
            生成结果 {'success': bool, 'data': dict, 'file_path': str, 'filename': str}
        """
        try:
            prompt = f"""
请分析以下个人信息，提取关键信息并按JSON格式输出，用于填充简历模板：

个人信息：
{personal_info}

请严格按照以下JSON格式输出，如果某项信息缺失，请填写"暂无相关内容"：

{{
    "姓名": "提取的姓名",
    "电话": "提取的电话号码",
    "邮箱": "提取的邮箱地址",
    "个人陈述": "根据信息生成的个人陈述，突出优势和特点",
    "教育背景": [
        {{"学校": "学校名称", "专业": "专业名称", "学位": "学位", "时间": "时间段"}},
        {{"学校": "暂无相关内容", "专业": "暂无相关内容", "学位": "暂无相关内容", "时间": "暂无相关内容"}},
        {{"学校": "暂无相关内容", "专业": "暂无相关内容", "学位": "暂无相关内容", "时间": "暂无相关内容"}}
    ],
    "工作经验": [
        {{"公司": "公司名称", "职位": "职位名称", "时间": "时间段", "职责": "主要职责描述"}},
        {{"公司": "暂无相关内容", "职位": "暂无相关内容", "时间": "暂无相关内容", "职责": "暂无相关内容"}},
        {{"公司": "暂无相关内容", "职位": "暂无相关内容", "时间": "暂无相关内容", "职责": "暂无相关内容"}}
    ],
    "项目经验": [
        {{"名称": "项目名称", "角色": "担任角色", "时间": "时间段", "描述": "项目描述和成果"}},
        {{"名称": "暂无相关内容", "角色": "暂无相关内容", "时间": "暂无相关内容", "描述": "暂无相关内容"}},
        {{"名称": "暂无相关内容", "角色": "暂无相关内容", "时间": "暂无相关内容", "描述": "暂无相关内容"}}
    ],
    "专业技能": "整理后的技能列表，包括编程语言、框架、工具等"
}}

只输出JSON数据，不要包含任何其他文字说明。
"""
            
            messages = [{"role": "user", "content": prompt}]
            result = self._call_api(messages, timeout=180)
            
            # 提取生成的内容
            ai_response = result["choices"][0]["message"]["content"]
            
            # 解析JSON数据
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if not json_match:
                raise Exception("AI响应中未找到有效的JSON数据")
            
            json_str = json_match.group()
            resume_data = json.loads(json_str)
            
            # 生成Word文档
            doc_result = self._create_resume_document(resume_data)
            
            return {
                "success": True,
                "data": resume_data,
                "file_path": doc_result["file_path"],
                "filename": doc_result["filename"],
                "usage": result.get("usage", {})
            }
            
        except Exception as e:
            self.logger.error(f"生成简历失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "file_path": None,
                "filename": None
            }
    
    def _create_summary_document(self, content: str) -> Dict[str, str]:
        """创建年度总结Word文档"""
        try:
            doc = Document()

            # 添加标题
            title = doc.add_heading('年度工作总结', 0)
            title.alignment = 1  # 居中对齐

            # 添加日期
            date_para = doc.add_paragraph(f'日期：{datetime.now().strftime("%Y年%m月%d日")}')
            date_para.alignment = 2  # 右对齐

            # 添加内容
            doc.add_paragraph(content)

            # 保存文档
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"年度工作总结_{timestamp}.docx"

            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, filename)
            doc.save(file_path)

            return {
                "file_path": file_path,
                "filename": filename
            }

        except Exception as e:
            self.logger.error(f"创建年度总结文档失败: {e}")
            raise

    def _create_resume_document(self, resume_data: Dict[str, Any]) -> Dict[str, str]:
        """创建简历Word文档"""
        try:
            doc = Document()

            # 添加标题
            title = doc.add_heading('个人简历', 0)
            title.alignment = 1  # 居中对齐

            # 基本信息
            doc.add_heading('基本信息', level=1)
            basic_info = doc.add_paragraph()
            basic_info.add_run(f"姓名：{resume_data.get('姓名', '暂无')}\n")
            basic_info.add_run(f"电话：{resume_data.get('电话', '暂无')}\n")
            basic_info.add_run(f"邮箱：{resume_data.get('邮箱', '暂无')}")

            # 个人陈述
            if resume_data.get('个人陈述') and resume_data['个人陈述'] != '暂无相关内容':
                doc.add_heading('个人陈述', level=1)
                doc.add_paragraph(resume_data['个人陈述'])

            # 教育背景
            doc.add_heading('教育背景', level=1)
            education_list = resume_data.get('教育背景', [])
            for edu in education_list:
                if edu.get('学校') and edu['学校'] != '暂无相关内容':
                    edu_para = doc.add_paragraph()
                    edu_para.add_run(f"• {edu.get('时间', '')} - {edu.get('学校', '')}\n")
                    edu_para.add_run(f"  专业：{edu.get('专业', '')} | 学位：{edu.get('学位', '')}")

            # 工作经验
            doc.add_heading('工作经验', level=1)
            work_list = resume_data.get('工作经验', [])
            for work in work_list:
                if work.get('公司') and work['公司'] != '暂无相关内容':
                    work_para = doc.add_paragraph()
                    work_para.add_run(f"• {work.get('时间', '')} - {work.get('公司', '')}\n")
                    work_para.add_run(f"  职位：{work.get('职位', '')}\n")
                    work_para.add_run(f"  职责：{work.get('职责', '')}")

            # 项目经验
            doc.add_heading('项目经验', level=1)
            project_list = resume_data.get('项目经验', [])
            for project in project_list:
                if project.get('名称') and project['名称'] != '暂无相关内容':
                    proj_para = doc.add_paragraph()
                    proj_para.add_run(f"• {project.get('名称', '')} ({project.get('时间', '')})\n")
                    proj_para.add_run(f"  角色：{project.get('角色', '')}\n")
                    proj_para.add_run(f"  描述：{project.get('描述', '')}")

            # 专业技能
            if resume_data.get('专业技能') and resume_data['专业技能'] != '暂无相关内容':
                doc.add_heading('专业技能', level=1)
                doc.add_paragraph(resume_data['专业技能'])

            # 保存文档
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = resume_data.get('姓名', '未知')
            filename = f"个人简历_{name}_{timestamp}.docx"

            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, filename)
            doc.save(file_path)

            return {
                "file_path": file_path,
                "filename": filename
            }

        except Exception as e:
            self.logger.error(f"创建简历文档失败: {e}")
            raise

    def is_available(self) -> bool:
        """检查服务是否可用"""
        try:
            # 简单的健康检查
            test_messages = [{"role": "user", "content": "你好"}]
            result = self._call_api(test_messages, timeout=30)
            return result.get("code") == 0
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return False
