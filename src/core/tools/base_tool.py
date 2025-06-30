#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Tool - 核心模块

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""

from abc import ABC, abstractmethod

class BaseTool(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def __str__(self):
        return self.__class__.__name__ 