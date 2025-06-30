#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桩类、桩函数检测工具

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
from typing import List, Dict, Any
from pathlib import Path


class StubDetector:
    """
    桩类、桩函数检测器
    
    功能：
    - 检测空类定义（pass语句）
    - 检测空函数定义（pass语句）
    - 检测TODO标记
    - 检测NotImplementedError
    - 检测硬编码模拟数据
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        
    def scan_project(self) -> Dict[str, Any]:
        """
        扫描整个项目
        
        Returns:
            Dict[str, Any]: 检测结果
        """
        print("🔍 开始扫描项目中的桩类、桩函数...")
        
        # 扫描Python文件
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            self._scan_file(file_path)
        
        # 生成报告
        report = self._generate_report()
        
        print(f"✅ 扫描完成，发现 {len(self.issues)} 个问题")
        return report
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        file_str = str(file_path)
        
        # 检查是否在venv目录中
        if "venv" in file_str or "site-packages" in file_str:
            return True
            
        skip_patterns = [
            "__pycache__/",
            ".git/",
            "node_modules/",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "dist-packages/",
            "lib/python",
            "Scripts/",
            "backup_",
            "temp/",
            "cache/"
        ]
        
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _scan_file(self, file_path: Path):
        """扫描单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                # 语法错误，跳过
                return
            
            # 检测各种问题
            self._detect_empty_classes(tree, file_path, content)
            self._detect_empty_functions(tree, file_path, content)
            self._detect_todo_comments(file_path, content)
            self._detect_not_implemented(file_path, content)
            self._detect_mock_data(file_path, content)
            
        except Exception as e:
            print(f"⚠️ 扫描文件 {file_path} 时出错: {e}")
    
    def _detect_empty_classes(self, tree: ast.AST, file_path: Path, content: str):
        """检测空类定义"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查类体是否只有pass语句
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    self.issues.append({
                        'type': 'empty_class',
                        'file': str(file_path),
                        'line': node.lineno,
                        'name': node.name,
                        'description': f'空类定义: {node.name}',
                        'severity': 'high'
                    })
    
    def _detect_empty_functions(self, tree: ast.AST, file_path: Path, content: str):
        """检测空函数定义"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数体是否只有pass语句
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    self.issues.append({
                        'type': 'empty_function',
                        'file': str(file_path),
                        'line': node.lineno,
                        'name': node.name,
                        'description': f'空函数定义: {node.name}',
                        'severity': 'high'
                    })
    
    def _detect_todo_comments(self, file_path: Path, content: str):
        """检测TODO标记"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(r'#\s*TODO', line, re.IGNORECASE):
                self.issues.append({
                    'type': 'todo_comment',
                    'file': str(file_path),
                    'line': i,
                    'content': line.strip(),
                    'description': f'TODO标记: {line.strip()}',
                    'severity': 'medium'
                })
    
    def _detect_not_implemented(self, file_path: Path, content: str):
        """检测NotImplementedError"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'NotImplementedError' in line:
                self.issues.append({
                    'type': 'not_implemented',
                    'file': str(file_path),
                    'line': i,
                    'content': line.strip(),
                    'description': f'NotImplementedError: {line.strip()}',
                    'severity': 'high'
                })
    
    def _detect_mock_data(self, file_path: Path, content: str):
        """检测硬编码模拟数据"""
        mock_patterns = [
            r'return\s*\{[^}]*"name"\s*:\s*"[^"]*"[^}]*\}',  # 返回包含name的字典
            r'return\s*\{[^}]*"张三"[^}]*\}',  # 包含"张三"的返回
            r'return\s*\{[^}]*"李四"[^}]*\}',  # 包含"李四"的返回
            r'return\s*\{[^}]*"test"[^}]*\}',  # 包含"test"的返回
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern in mock_patterns:
                if re.search(pattern, line):
                    self.issues.append({
                        'type': 'mock_data',
                        'file': str(file_path),
                        'line': i,
                        'content': line.strip(),
                        'description': f'硬编码模拟数据: {line.strip()}',
                        'severity': 'medium'
                    })
                    break
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成检测报告"""
        report = {
            'summary': {
                'total_issues': len(self.issues),
                'high_severity': len([i for i in self.issues if i['severity'] == 'high']),
                'medium_severity': len([i for i in self.issues if i['severity'] == 'medium']),
                'low_severity': len([i for i in self.issues if i['severity'] == 'low'])
            },
            'issues_by_type': {},
            'issues': self.issues
        }
        
        # 按类型分组
        for issue in self.issues:
            issue_type = issue['type']
            if issue_type not in report['issues_by_type']:
                report['issues_by_type'][issue_type] = []
            report['issues_by_type'][issue_type].append(issue)
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """打印检测报告"""
        print("\n" + "="*60)
        print("🔍 桩类、桩函数检测报告")
        print("="*60)
        
        summary = report['summary']
        print(f"📊 总问题数: {summary['total_issues']}")
        print(f"🔴 高严重性: {summary['high_severity']}")
        print(f"🟡 中严重性: {summary['medium_severity']}")
        print(f"🟢 低严重性: {summary['low_severity']}")
        
        if summary['total_issues'] == 0:
            print("✅ 未发现桩类、桩函数问题！")
            return
        
        print("\n📋 详细问题列表:")
        print("-"*60)
        
        for issue in report['issues']:
            severity_icon = "🔴" if issue['severity'] == 'high' else "🟡" if issue['severity'] == 'medium' else "🟢"
            print(f"{severity_icon} {issue['file']}:{issue['line']}")
            print(f"   类型: {issue['type']}")
            print(f"   描述: {issue['description']}")
            if 'content' in issue:
                print(f"   内容: {issue['content']}")
            print()
        
        print("💡 建议:")
        print("1. 立即修复高严重性问题")
        print("2. 为TODO标记制定实现计划")
        print("3. 替换硬编码模拟数据为真实实现")
        print("4. 建立代码审查机制防止问题再次出现")


def main():
    """主函数"""
    detector = StubDetector()
    report = detector.scan_project()
    detector.print_report(report)
    
    # 保存报告到文件
    with open('stub_detection_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存到: stub_detection_report.json")
    
    # 如果有高严重性问题，返回非零退出码
    if report['summary']['high_severity'] > 0:
        print("❌ 发现高严重性问题，请立即修复！")
        exit(1)
    else:
        print("✅ 检测通过！")


if __name__ == "__main__":
    main() 