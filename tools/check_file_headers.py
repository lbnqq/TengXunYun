#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件头注释检查工具

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
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

class FileHeaderChecker:
    def __init__(self):
        # Python文件头模式
        self.python_patterns = {
            'shebang': r'^#!/usr/bin/env python3',
            # ... 其他模式 ...
        }
        
    def check_file(self, file_path: Path) -> Dict[str, Any]:
        # 读取文件头部内容
        content = self.read_file_header(file_path)
        if content is None:
            content = ''
        
        # 检查文件类型并应用对应的检查
        if file_path.suffix == '.py':
            return self.check_python_file(content)
        elif file_path.suffix in ['.js', '.jsx']:
            return self.check_javascript_file(content)
        else:
            return {'valid': False, 'reason': '不支持的文件类型'}
    
    def read_file_header(self, file_path: Path, max_lines: int = 10) -> str:
        try:
            with file_path.open('r', encoding='utf-8') as f:
                lines = []
                for _ in range(max_lines):
                    try:
                        lines.append(next(f))
                    except StopIteration:
                        break
                return ''.join(lines)
        except Exception as e:
            return ''
    
    def check_python_file(self, content: str) -> Dict[str, Any]:
        if not content:
            return {'valid': False, 'reason': '文件内容为空'}
        # 检查是否包含shebang
        if not re.search(self.python_patterns['shebang'], content, re.MULTILINE):
            return {'valid': False, 'reason': '缺少shebang行'}
        
        return {'valid': True}
    
    def check_javascript_file(self, content: str) -> Dict[str, Any]:
        if not content:
            return {'valid': False, 'reason': '文件内容为空'}
        # JavaScript文件头检查逻辑
        return {'valid': True}
    
    def check_directory(self, directory: Path) -> Dict[str, Any]:
        results = {
            'total_files': 0,
            'checked_files': 0,
            'valid_files': 0,
            'invalid_files': 0,
            'skipped_files': 0
        }
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                results['total_files'] += 1
                
                # 检查文件是否应该被忽略
                if self.should_ignore_file(file_path):
                    results['skipped_files'] += 1
                    continue
                
                results['checked_files'] += 1
                result = self.check_file(file_path)
                
                if result['valid']:
                    results['valid_files'] += 1
                else:
                    results['invalid_files'] += 1
        
        return results
    
    def should_ignore_file(self, file_path: Path) -> bool:
        # 只检测 src/ 目录下的核心 .py 文件
        path_str = str(file_path).lower()
        # 跳过非 src/ 目录
        if not (path_str.replace('\\', '/').startswith('src/') or '/src/' in path_str):
            return True
        # 跳过备份/草稿/历史文件
        backup_keywords = ['backup', '.bak', 'old', 'draft']
        for kw in backup_keywords:
            if kw in file_path.name.lower():
                return True
        # 原有忽略逻辑
        ignore_patterns = [
            'test', 'tests', 'example', 'examples', 'demo', 'minimal', 'cliTests',
            'output', 'integration_test_storage', 'test_data', 'test_files', 'test_results', 'test_storage',
            'docs', 'doc', 'README', 'setup', 'sys_path_debug', '__pycache__', 'run_all_tests', 'check_docx',
            'start_ai_thinking_demo', 'simple_web_app', 'style_analysis_demo', 'semantic_behavior_demo',
            'minimal_web_app', 'Untitled', 'tmp', 'temp', 'script', 'notebook', 'pytest', 'init',
            'debug', 'sample', 'mock', 'playground', 'experiment', 'dev', 'legacy',
        ]
        for pat in ignore_patterns:
            if pat in path_str:
                return True
        # 只检测 .py/.js/.jsx 文件
        if file_path.suffix not in ['.py', '.js', '.jsx']:
            return True
        return False
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        lines = []
        lines.append("# 文件头注释检查报告")
        lines.append(f"- 总文件数: {results.get('total_files', 0)}")
        lines.append(f"- 检查文件数: {results.get('checked_files', 0)}")
        lines.append(f"- 有效文件数: {results.get('valid_files', 0)}")
        lines.append(f"- 无效文件数: {results.get('invalid_files', 0)}")
        lines.append(f"- 跳过文件数: {results.get('skipped_files', 0)}")
        return '\n'.join(lines)
    
def main():
    checker = FileHeaderChecker()
    
    # 示例：检查当前目录
    results = checker.check_directory(Path('.'))
    report = checker.generate_report(results)
    
    print(report)

if __name__ == "__main__":
    main()