#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面深入的方法实现检查工具
扫描整个项目代码库，验证所有模块的实现状态
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
    """全面深入的方法实现检查器"""
    
    def __init__(self):
        self.project_root = Path(project_root)
        self.required_methods = {
            'style_alignment': [
                'generate_style_preview',
                'save_style_template', 
                'export_styled_document',
                'analyze_writing_style',
                'apply_style_changes',
                'handle_style_change',
                'handle_batch_style_changes'
            ],
            'document_fill': [
                'generate_fill_preview',
                'apply_fill_changes',
                'export_filled_document',
                'analyze_template_structure',
                'match_data_to_template',
                'intelligent_fill_document'
            ],
            'format_alignment': [
                'analyze_format_differences',
                'generate_alignment_preview',
                'apply_format_changes',
                'export_aligned_document',
                'compare_document_formats',
                'align_documents_format'
            ],
            'document_review': [
                'generate_review_report',
                'apply_review_suggestions',
                'export_reviewed_document',
                'analyze_document_quality',
                'generate_approval_recommendations',
                'execute'
            ]
        }
        
        # 扩展搜索范围
        self.search_directories = [
            'src/core/tools',
            'src/core/analysis', 
            'src/core/agent',
            'src/core/database',
            'src/core/guidance',
            'src/core/knowledge_base',
            'src/core/monitoring',
            'src/llm_clients',
            'src'
        ]
        
        self.found_methods = {}
        self.missing_methods = {}
        self.method_locations = {}
        
    def scan_all_python_files(self) -> Dict[str, str]:
        """扫描所有Python文件"""
        python_files = {}
        
        for search_dir in self.search_directories:
            dir_path = self.project_root / search_dir
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    relative_path = py_file.relative_to(self.project_root)
                    python_files[str(relative_path)] = str(py_file)
        
        return python_files
    
    def extract_methods_from_file(self, file_path: str) -> Set[str]:
        """从文件中提取所有方法名"""
        methods = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用AST解析
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    methods.add(node.name)
                elif isinstance(node, ast.AsyncFunctionDef):
                    methods.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    for class_node in ast.walk(node):
                        if isinstance(class_node, ast.FunctionDef):
                            methods.add(class_node.name)
                        elif isinstance(class_node, ast.AsyncFunctionDef):
                            methods.add(class_node.name)
        
        except Exception as e:
            logger.warning(f"解析文件失败 {file_path}: {e}")
        
        return methods
    
    def find_method_implementations(self) -> Dict[str, List[Dict[str, str]]]:
        """查找所有方法的实现位置"""
        python_files = self.scan_all_python_files()
        all_methods = {}
        
        for module_name, file_path in python_files.items():
            methods = self.extract_methods_from_file(file_path)
            
            for method_name in methods:
                if method_name not in all_methods:
                    all_methods[method_name] = []
                all_methods[method_name].append({
                    'file': module_name,
                    'path': file_path
                })
        
        return all_methods
    
    def check_method_coverage(self) -> Dict[str, Dict[str, Any]]:
        """检查方法覆盖率"""
        all_methods = self.find_method_implementations()
        results = {}
        
        for module_name, required_methods in self.required_methods.items():
            implemented = []
            missing = []
            found_locations = []
            
            for method_name in required_methods:
                if method_name in all_methods:
                    implemented.append(method_name)
                    found_locations.extend(all_methods[method_name])
                else:
                    missing.append(method_name)
            
            coverage = len(implemented) / len(required_methods) if required_methods else 1.0
            
            results[module_name] = {
                'implemented': implemented,
                'missing': missing,
                'found_locations': found_locations,
                'coverage': coverage,
                'total_required': len(required_methods),
                'total_implemented': len(implemented)
            }
        
        return results
    
    def check_api_endpoints(self) -> Dict[str, List[str]]:
        """检查API端点实现"""
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
        """检查方法调用关系"""
        method_calls = {}
        python_files = self.scan_all_python_files()
        
        for module_name, file_path in python_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找方法调用
                import re
                call_pattern = r'(\w+)\.(\w+)\('
                matches = re.findall(call_pattern, content)
                
                for obj_name, method_name in matches:
                    key = f"{obj_name}.{method_name}"
                    if key not in method_calls:
                        method_calls[key] = []
                    method_calls[key].append(module_name)
            
            except Exception as e:
                logger.warning(f"检查方法调用失败 {file_path}: {e}")
        
        return method_calls
    
    def generate_comprehensive_report(self) -> str:
        """生成全面报告"""
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
        """保存详细报告"""
        report_content = self.generate_comprehensive_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"详细报告已保存到: {output_file}")
        return output_file


def main():
    """主函数"""
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