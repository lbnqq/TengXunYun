#!/usr/bin/env python3
"""
桩子函数检测器
功能：检测项目中的桩子函数、示例函数、mock示例等未完整实现的方法

Author: AI Assistant (Claude)
Date: 2025-06-27
AI Assisted: 是
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
    """桩子函数信息"""
    file_path: str
    line_number: int
    function_name: str
    class_name: str = ""
    stub_type: str = ""  # pass, return_none, return_empty, not_implemented, todo, fixme, mock
    description: str = ""
    severity: str = "medium"  # low, medium, high, critical
    context: str = ""


class StubFunctionDetector:
    """桩子函数检测器"""
    
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
        """检测所有桩子函数"""
        print("🔍 开始检测桩子函数...")
        
        python_files = self._find_python_files()
        print(f"📁 找到 {len(python_files)} 个Python文件")
        
        for file_path in python_files:
            self._analyze_file(file_path)
        
        print(f"✅ 检测完成，发现 {len(self.stub_functions)} 个桩子函数")
        return self.stub_functions
    
    def _find_python_files(self) -> List[Path]:
        """查找所有Python文件"""
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
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                print(f"⚠️  语法错误，跳过文件: {file_path}")
                return
            
            # 分析函数定义
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self._analyze_function(node, file_path, content)
                elif isinstance(node, ast.AsyncFunctionDef):
                    self._analyze_function(node, file_path, content)
        
        except Exception as e:
            print(f"❌ 分析文件失败 {file_path}: {e}")
    
    def _analyze_function(self, func_node, file_path: Path, content: str):
        """分析单个函数"""
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
        """获取函数所属的类名"""
        lines = content.split('\n')
        
        # 向上查找类定义
        for i in range(func_node.lineno - 2, -1, -1):
            line = lines[i].strip()
            if line.startswith('class '):
                # 提取类名
                match = re.match(r'class\s+(\w+)', line)
                if match:
                    return match.group(1)
            elif line and not line.startswith('#'):
                break
        
        return ""
    
    def _check_stub_function(self, func_node, func_body: str, file_path: Path, 
                           function_name: str, class_name: str) -> StubFunctionInfo:
        """检查是否是桩子函数"""
        # 获取函数体代码行（排除注释和空行）
        body_lines = []
        for line in func_body.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('"""'):
                body_lines.append(stripped)
        
        # 如果函数体为空或只有很少的代码行，可能是桩子函数
        if len(body_lines) <= 3:
            for stub_type, pattern in self.stub_patterns.items():
                if re.search(pattern, func_body, re.IGNORECASE):
                    return self._create_stub_info(
                        file_path, func_node.lineno, function_name, class_name,
                        stub_type, func_body
                    )
        
        # 检查是否有TODO/FIXME注释
        if re.search(r'#\s*(TODO|FIXME)', func_body, re.IGNORECASE):
            return self._create_stub_info(
                file_path, func_node.lineno, function_name, class_name,
                "todo_fixme", func_body
            )
        
        # 检查是否只有简单的返回语句
        if self._is_simple_return_only(body_lines):
            return self._create_stub_info(
                file_path, func_node.lineno, function_name, class_name,
                "simple_return", func_body
            )
        
        return None
    
    def _is_simple_return_only(self, body_lines: List[str]) -> bool:
        """检查是否只有简单的返回语句"""
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
        """创建桩子函数信息"""
        # 确定严重程度
        severity_map = {
            "pass": "high",
            "return_none": "medium",
            "return_empty_dict": "medium",
            "return_empty_list": "medium",
            "not_implemented": "critical",
            "todo": "medium",
            "fixme": "high",
            "mock": "low",
            "placeholder": "medium",
            "example": "low",
            "demo": "low",
            "temp": "high",
            "dummy": "medium",
            "todo_fixme": "high",
            "simple_return": "medium"
        }
        
        severity = severity_map.get(stub_type, "medium")
        
        # 生成描述
        description_map = {
            "pass": "空函数体，需要实现具体逻辑",
            "return_none": "只返回None，需要实现返回值",
            "return_empty_dict": "只返回空字典，需要填充数据",
            "return_empty_list": "只返回空列表，需要填充数据",
            "not_implemented": "明确标记为未实现",
            "todo": "标记为待办事项",
            "fixme": "标记为需要修复",
            "mock": "模拟/测试函数",
            "placeholder": "占位符函数",
            "example": "示例函数",
            "demo": "演示函数",
            "temp": "临时函数",
            "dummy": "虚拟函数",
            "todo_fixme": "包含TODO或FIXME注释",
            "simple_return": "只有简单返回语句"
        }
        
        description = description_map.get(stub_type, "未知类型的桩子函数")
        
        return StubFunctionInfo(
            file_path=str(file_path.relative_to(self.project_root)),
            line_number=line_number,
            function_name=function_name,
            class_name=class_name,
            stub_type=stub_type,
            description=description,
            severity=severity,
            context=func_body[:200] + "..." if len(func_body) > 200 else func_body
        )
    
    def generate_report(self, output_file: str = None) -> str:
        """生成检测报告"""
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
        """导出JSON格式的检测结果"""
        data = {
            "detection_time": datetime.now().isoformat(),
            "total_files": len(self._find_python_files()),
            "total_stubs": len(self.stub_functions),
            "stub_functions": [asdict(stub) for stub in self.stub_functions]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 JSON结果已保存到: {output_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="检测项目中的桩子函数")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--output", help="输出报告文件")
    parser.add_argument("--json", help="输出JSON文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 创建检测器
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
        report = detector.generate_report()
        print(report)
    
    # 导出JSON
    if args.json:
        detector.export_json(args.json)
    
    # 返回退出码
    critical_count = len([s for s in stubs if s.severity == 'critical'])
    high_count = len([s for s in stubs if s.severity == 'high'])
    
    if critical_count > 0:
        print(f"❌ 发现 {critical_count} 个严重级别的桩子函数")
        exit(1)
    elif high_count > 0:
        print(f"⚠️  发现 {high_count} 个高级别的桩子函数")
        exit(2)
    else:
        print("✅ 未发现严重或高级别的桩子函数")
        exit(0)


if __name__ == "__main__":
    main() 