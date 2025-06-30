#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桩子函数检测器

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""











import os
import re
import ast
import json
import inspect
from typing import Dict, List, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class StubFunctionInfo:
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.stub_functions = []
        self.stub_patterns = {
            "pass": r"^\s*pass\s*$",
            "return_none": r"^\s*return\s+None\s*$",
            "return_empty_dict": r"^\s*return\s+\{\}\s*$",
            "return_empty_list": r"^\s*return\s+\[\]\s*$",
            "return_empty_string": r"^\s*return\s+['\"]\s*['\"]\s*$",
            "not_implemented": r"raise\s+NotImplementedError",
            "todo": r"#\s*TODO",
            "fixme": r"#\s*FIXME",
            "mock": r"mock|Mock|MOCK",
            "placeholder": r"placeholder|Placeholder|PLACEHOLDER",
            "example": r"example|Example|EXAMPLE",
            "demo": r"demo|Demo|DEMO",
            "temp": r"temp|Temp|TEMP",
            "dummy": r"dummy|Dummy|DUMMY"
        }
        
        # 排除的目录和文件
        self.exclude_patterns = [
            r"__pycache__",
            r"\.git",
            r"\.venv",
            r"venv",
            r"node_modules",
            r"\.pytest_cache",
            r"\.coverage",
            r"\.tox",
            r"build",
            r"dist",
            r"\.egg-info",
            r"tests/test_.*\.py$",  # 测试文件中的mock是正常的
            r"cliTests/.*\.py$",    # CLI测试文件
            r"examples/.*\.py$"     # 示例文件
        ]
    
    def detect_stub_functions(self) -> List[StubFunctionInfo]:
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # 排除不需要的目录
            dirs[:] = [d for d in dirs if not any(re.match(pattern, d) for pattern in self.exclude_patterns)]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    # 排除不需要的文件
                    if not any(re.match(pattern, str(file_path)) for pattern in self.exclude_patterns):
                        python_files.append(file_path)
        
        return python_files
    
    def _analyze_file(self, file_path: Path):
        # 获取函数信息
        function_name = func_node.name
        class_name = self._get_class_name(func_node, content)
        
        # 获取函数体
        func_lines = content.split('\n')[func_node.lineno-1:func_node.end_lineno]
        func_body = '\n'.join(func_lines)
        
        # 检查是否是桩子函数
        stub_info = self._check_stub_function(func_node, func_body, file_path, function_name, class_name)
        if stub_info:
            self.stub_functions.append(stub_info)
    
    def _get_class_name(self, func_node, content: str) -> str:
        # 获取函数体代码行（排除注释和空行）
        body_lines = []
        for line in func_body.split('\n'):
            stripped = line.strip()
        if len(body_lines) == 0:
            return True
        
        # 检查是否只有return语句
        simple_returns = [
            r'^\s*return\s*$',
            r'^\s*return\s+None\s*$',
            r'^\s*return\s+\{\}\s*$',
            r'^\s*return\s+\[\]\s*$',
            r'^\s*return\s+["\']\s*["\']\s*$',
            r'^\s*return\s+True\s*$',
            r'^\s*return\s+False\s*$',
            r'^\s*return\s+0\s*$',
            r'^\s*return\s+""\s*$'
        ]
        
        for line in body_lines:
            if not any(re.match(pattern, line) for pattern in simple_returns):
                return False
        
        return True
    
    def _create_stub_info(self, file_path: Path, line_number: int, function_name: str,
                         class_name: str, stub_type: str, func_body: str) -> StubFunctionInfo:
        if not self.stub_functions:
            return "✅ 未发现桩子函数"
        
        # 按严重程度分组
        severity_groups = {}
        for stub in self.stub_functions:
            if stub.severity not in severity_groups:
                severity_groups[stub.severity] = []
            severity_groups[stub.severity].append(stub)
        
        # 生成报告
        report_lines = [
            "# 桩子函数检测报告",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"检测文件数: {len(self._find_python_files())}",
            f"发现桩子函数数: {len(self.stub_functions)}",
            "",
            "## 统计摘要",
            f"- 严重 (Critical): {len(severity_groups.get('critical', []))}",
            f"- 高 (High): {len(severity_groups.get('high', []))}",
            f"- 中 (Medium): {len(severity_groups.get('medium', []))}",
            f"- 低 (Low): {len(severity_groups.get('low', []))}",
            ""
        ]
        
        # 按严重程度详细列出
        severity_order = ['critical', 'high', 'medium', 'low']
        for severity in severity_order:
            if severity in severity_groups:
                report_lines.extend([
                    f"## {severity.upper()} 级别桩子函数",
                    ""
                ])
                
                for stub in severity_groups[severity]:
                    report_lines.extend([
                        f"### {stub.function_name}",
                        f"- **文件**: `{stub.file_path}:{stub.line_number}`",
                        f"- **类型**: {stub.stub_type}",
                        f"- **描述**: {stub.description}",
                    ])
                    
                    if stub.class_name:
                        report_lines.append(f"- **类**: {stub.class_name}")
                    
                    report_lines.extend([
                        f"- **代码**:",
                        "```python",
                        stub.context,
                        "```",
                        ""
                    ])
        
        report = "\n".join(report_lines)
        
        # 保存到文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 报告已保存到: {output_file}")
        
        return report
    
    def export_json(self, output_file: str) -> None:
        pass

# ========== 主程序入口 ==========
import argparse

parser = argparse.ArgumentParser(description="检测项目中的桩子函数")
parser.add_argument("--project-root", default=".", help="项目根目录")
parser.add_argument("--output", help="输出报告文件")
parser.add_argument("--json", help="输出JSON文件")
parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

args = parser.parse_args()

# 创建检测器
if __name__ == "__main__":
    detector = StubFunctionDetector(args.project_root)
    # 执行检测
    stubs = detector.detect_stub_functions()
    # 输出结果
    if args.verbose:
        print(f"\n发现 {len(stubs)} 个桩子函数:")
        for stub in stubs:
            print(f"  {stub.severity.upper()}: {stub.file_path}:{stub.line_number} - {stub.function_name} ({stub.stub_type})")
    # 生成报告
    if args.output:
        report = detector.generate_report(args.output)
        print(report)
    else:
        report = detector.generate_report(None)
        print(report)
    # 导出JSON
    if args.json:
        detector.export_json(args.json)