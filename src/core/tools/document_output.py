#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Output - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""

from .base_tool import BaseTool

class DocumentOutputTool(BaseTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self, content: str, output_path: str, file_format: str = "txt") -> dict:
        try:
            full_path = f"{output_path}.{file_format}"
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "message": f"Content saved to {full_path}"}
        except Exception as e:
            return {"error": f"Failed to save content to {output_path}.{file_format}: {e}"} 