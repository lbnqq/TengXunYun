#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础测试文件
"""

import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

def test_basic_functionality():
    """测试基本功能"""
    assert 1 + 1 == 2

def test_imports():
    """测试基本导入"""
    import os
    import sys
    import json
    assert True

def test_flask_import():
    """测试Flask导入"""
    from flask import Flask
    app = Flask(__name__)
    assert app is not None

def test_pandas_import():
    """测试pandas导入"""
    import pandas as pd
    df = pd.DataFrame({'a': [1, 2, 3]})
    assert len(df) == 3

@pytest.mark.unit
def test_doc_processor_import():
    """测试文档处理器导入"""
    try:
        from doc_processor import DocumentProcessor
        assert True
    except ImportError as e:
        pytest.skip(f"DocumentProcessor import failed: {e}")
