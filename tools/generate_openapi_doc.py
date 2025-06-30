#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAPI文档生成工具

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""










import re

ROUTE_PATTERN = re.compile(r"@app\.route\(['\"](.*?)['\"](?:,\s*methods=\[(.*?)\])?\)")
DEF_PATTERN = re.compile(r"def (\w+)\(")