#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合方法检查器

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
import inspect
import importlib
import ast
from typing import Dict, Any, List, Set, Tuple
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

class ComprehensiveMethodChecker:
    def __init__(self, project_root=None, search_directories=None):
        self.project_root = Path(project_root) if project_root else Path(project_root or os.getcwd())
        self.search_directories = search_directories or ["src", "tools"]

    def scan_all_python_files(self) -> Dict[str, str]:
        python_files = {}
        for search_dir in self.search_directories:
            dir_path = self.project_root / search_dir
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    relative_path = py_file.relative_to(self.project_root)
                    python_files[str(relative_path)] = str(py_file)
        return python_files

    def extract_methods_from_file(self, file_path: str) -> Set[str]:
        # 示例方法体
        return set()

    def check_method_coverage(self) -> Dict[str, Dict[str, Any]]:
        api_endpoints = {}
        
        # 检查web_app.py中的API端点
        web_app_path = self.project_root / 'src' / 'web_app.py'
        if web_app_path.exists():
            try:
                with open(web_app_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找@app.route装饰器
                import re
                route_pattern = r'@app\.route\([\'"]([^\'"]+)[\'"][^)]*\)\s*\ndef\s+(\w+)'
                matches = re.findall(route_pattern, content)
                
                for route, function_name in matches:
                    if route not in api_endpoints:
                        api_endpoints[route] = []
                    api_endpoints[route].append(function_name)
            
            except Exception as e:
                logger.error(f"解析web_app.py失败: {e}")
        
        return api_endpoints
    
    def check_method_calls(self) -> Dict[str, List[str]]:
        print("🔍 开始全面深入扫描...")
        
        # 1. 方法覆盖率检查
        coverage_results = self.check_method_coverage()
        
        # 2. API端点检查
        api_endpoints = self.check_api_endpoints()
        
        # 3. 方法调用关系检查
        method_calls = self.check_method_calls()
        
        # 4. 生成报告
        report = ["# 全面深入方法实现检查报告\n"]
        
        # 方法覆盖率部分
        report.append("## 📊 方法实现覆盖率\n")
        for module_name, result in coverage_results.items():
            status = "✅" if result['coverage'] == 1.0 else "⚠️" if result['coverage'] >= 0.8 else "❌"
            report.append(f"### {module_name} 模块")
            report.append(f"{status} 实现覆盖率: {result['coverage']:.1%} ({result['total_implemented']}/{result['total_required']})")
            
            if result['implemented']:
                report.append(f"✅ 已实现方法: {', '.join(result['implemented'])}")
            
            if result['missing']:
                report.append(f"❌ 缺失方法: {', '.join(result['missing'])}")
            
            if result['found_locations']:
                report.append("📍 实现位置:")
                for location in result['found_locations']:
                    report.append(f"  - {location['file']}")
            
            report.append("")
        
        # API端点部分
        report.append("## 🌐 API端点实现\n")
        if api_endpoints:
            for route, functions in api_endpoints.items():
                report.append(f"### {route}")
                for func in functions:
                    report.append(f"  - {func}")
                report.append("")
        else:
            report.append("未找到API端点定义\n")
        
        # 方法调用关系部分
        report.append("## 🔗 关键方法调用关系\n")
        relevant_calls = {k: v for k, v in method_calls.items() 
                         if any(method in k for methods in self.required_methods.values() for method in methods)}
        
        if relevant_calls:
            for call, files in relevant_calls.items():
                report.append(f"### {call}")
                for file in files:
                    report.append(f"  - {file}")
                report.append("")
        else:
            report.append("未找到相关方法调用\n")
        
        # 问题总结
        report.append("## ⚠️ 问题总结\n")
        critical_issues = []
        for module_name, result in coverage_results.items():
            if result['coverage'] < 0.8:
                critical_issues.append(f"{module_name}: 实现覆盖率过低 ({result['coverage']:.1%})")
        
        if critical_issues:
            for issue in critical_issues:
                report.append(f"- {issue}")
        else:
            report.append("✅ 所有模块实现状态良好")
        
        return "\n".join(report)
    
    def save_detailed_report(self, output_file: str = "comprehensive_method_report.md"):
        checker = ComprehensiveMethodChecker()
        
        print("🚀 开始全面深入方法实现检查...")
        print("=" * 60)
        
        # 生成报告
        report = checker.generate_comprehensive_report()
        print(report)
        
        # 保存报告
        output_file = checker.save_detailed_report()
        
        # 检查严重问题
        coverage_results = checker.check_method_coverage()
        critical_issues = []
        
        for module_name, result in coverage_results.items():
            if result['coverage'] < 0.8:
                critical_issues.append(f"{module_name}: 实现覆盖率过低 ({result['coverage']:.1%})")
        
        if critical_issues:
            print("\n" + "=" * 60)
            print("⚠️ 发现严重问题:")
            for issue in critical_issues:
                print(f"  - {issue}")
            return 1
        else:
            print("\n" + "=" * 60)
            print("✅ 所有模块方法实现状态良好")
            return 0


if __name__ == "__main__":
    exit(main())