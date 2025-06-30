#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: main.py
Description: 主程序入口文件
Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary modules from our project
from core.agent.agent_orchestrator import AgentOrchestrator
from llm_clients.xingcheng_llm import XingchengLLMClient

# Load environment variables from .env file
load_dotenv()

def main():
    pass

if __name__ == "__main__":
    main()