#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化质量检查工具

集成所有项目开发规范检查，确保代码质量和一致性。
包括文件头注释、API接口文档、页面元素一致性等检查。

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
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class AutomatedQualityChecker:
    """
    自动化质量检查器
    
    集成所有项目开发规范检查，确保代码质量和一致性。
    
    Author: AI Assistant (Claude)
    Date: 2025-01-28
    AI Assisted: 是
    """
    
    def __init__(self):
        """
        初始化质量检查器
        
        Author: AI Assistant (Claude)
        Date: 2025-01-28
        AI Assisted: 是
        """
        self.check_results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'summary': {
                'total_checks': 0,
                'passed_checks': 0,
                'failed_checks': 0,
                'warnings': 0
            },
            'recommendations': []
        }
    
    def check_file_headers(self) -> Dict[str, Any]:
        """
        检查文件头注释规范
        
        Returns:
            Dict[str, Any]: 检查结果
            
        Author: AI Assistant (Claude)
        Date: 2025-01-28
        AI Assisted: 是
        """
        print("🔍 检查文件头注释规范...")
        
        try:
            result = subprocess.run(
                [sys.executable, 'tools/check_file_headers.py'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                # 解析输出结果
                output = result.stdout
                if "所有文件头注释都符合规范" in output:
                    return {
                        'status': 'passed',
                        'message': '所有文件头注释都符合规范',
                        'details': output
                    }
                else:
                    return {
                        'status': 'failed',
                        'message': '发现文件头注释不规范',
                        'details': output
                    }
            else:
                return {
                    'status': 'error',
                    'message': f'检查工具运行失败: {result.stderr}',
                    'details': result.stderr
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'检查过程出错: {str(e)}',
                'details': str(e)
            }
    
    def check_api_documentation(self) -> Dict[str, Any]:
        """
        检查API接口文档一致性
        
        Returns:
            Dict[str, Any]: 检查结果
            
        Author: AI Assistant (Claude)
        Date: 2025-01-28
        AI Assisted: 是
        """
        print("🔍 检查API接口文档一致性...")
        
        try:
            # 检查API比对工具是否存在
            api_check_tool = Path('tools/compare_api_usage_with_doc.py')
            if not api_check_tool.exists():
                return {
                    'status': 'warning',
                    'message': 'API比对工具不存在，跳过检查',
                    'details': 'tools/compare_api_usage_with_doc.py 文件不存在'
                }
            
            result = subprocess.run(
                [sys.executable, 'tools/compare_api_usage_with_doc.py'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                return {
                    'status': 'passed',
                    'message': 'API接口文档检查通过',
                    'details': result.stdout
                }
            else:
                return {
                    'status': 'failed',
                    'message': 'API接口文档不一致',
                    'details': result.stderr
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'API检查过程出错: {str(e)}',
                'details': str(e)
            }
    
    def check_page_elements(self) -> Dict[str, Any]:
        """
        检查页面元素ID/Class一致性
        
        Returns:
            Dict[str, Any]: 检查结果
            
        Author: AI Assistant (Claude)
        Date: 2025-01-28
        AI Assisted: 是
        """
        print("🔍 检查页面元素ID/Class一致性...")
        
        try:
            # 生成ID/Class报告
            result = subprocess.run(
                [sys.executable, 'tools/generate_id_class_report.py'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                cwd=Path.cwd()
            )
            
            if result.returncode != 0:
                return {
                    'status': 'error',
                    'message': '生成ID/Class报告失败',
                    'details': result.stderr
                }
            
            # 检查ID使用一致性
            result = subprocess.run(
                [sys.executable, 'tools/compare_id_usage_with_report.py'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                return {
                    'status': 'passed',
                    'message': '页面元素ID/Class一致性检查通过',
                    'details': result.stdout
                }
            else:
                return {
                    'status': 'failed',
                    'message': '页面元素ID/Class使用不一致',
                    'details': result.stderr
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'页面元素检查过程出错: {str(e)}',
                'details': str(e)
            }
    
    def check_code_style(self) -> Dict[str, Any]:
        """
        检查代码风格规范
        
        Returns:
            Dict[str, Any]: 检查结果
            
        Author: AI Assistant (Claude)
        Date: 2025-01-28
        AI Assisted: 是
        """
        print("🔍 检查代码风格规范...")
        
        try:
            # 检查Python文件语法
            python_files = list(Path('src').rglob("*.py"))
            syntax_errors = []
            
            for file_path in python_files:
                try:
                    result = subprocess.run(
                        [sys.executable, '-m', 'py_compile', str(file_path)],
                        capture_output=True,
                        text=True,
                        encoding='utf-8'
                    )
                    if result.returncode != 0:
                        syntax_errors.append(f"{file_path}: {result.stderr}")
                except Exception as e:
                    syntax_errors.append(f"{file_path}: {str(e)}")
            
            if syntax_errors:
                return {
                    'status': 'failed',
                    'message': f'发现 {len(syntax_errors)} 个语法错误',
                    'details': '\n'.join(syntax_errors[:10])  # 只显示前10个错误
                }
            else:
                return {
                    'status': 'passed',
                    'message': '代码语法检查通过',
                    'details': f'检查了 {len(python_files)} 个Python文件'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'代码风格检查过程出错: {str(e)}',
                'details': str(e)
            }
    
    def check_documentation(self) -> Dict[str, Any]:
        """
        检查文档完整性
        
        Returns:
            Dict[str, Any]: 检查结果
            
        Author: AI Assistant (Claude)
        Date: 2025-01-28
        AI Assisted: 是
        """
        print("🔍 检查文档完整性...")
        
        try:
            required_docs = [
                'README.md'
            ]
            
            missing_docs = []
            for doc_path in required_docs:
                if not Path(doc_path).exists():
                    missing_docs.append(doc_path)
            
            if missing_docs:
                return {
                    'status': 'failed',
                    'message': f'缺少 {len(missing_docs)} 个必需文档',
                    'details': f'缺少文档: {", ".join(missing_docs)}'
                }
            else:
                return {
                    'status': 'passed',
                    'message': f'文档完整性检查通过',
                    'details': f'所有 {len(required_docs)} 个必需文档都存在'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'文档完整性检查过程出错: {str(e)}',
                'details': str(e)
            }
    
    def check_p0_p1_principles(self) -> Dict[str, Any]:
        """
        检查P0/P1原则（桩子、空函数、空类、Mock、可变全局变量等）
        Returns:
            Dict[str, Any]: 检查结果
        """
        print("🔍 检查P0/P1原则（桩子、空函数、空类、Mock、全局变量等）...")
        try:
            # 检查桩子函数/空函数/空类/Mock
            stub_result = subprocess.run(
                [sys.executable, 'tools/stub_function_detector.py', '--project-root', str(Path.cwd())],
                capture_output=True, text=True, cwd=Path.cwd()
            )
            stub_stdout = stub_result.stdout if stub_result.stdout is not None else ''
            stub_stderr = stub_result.stderr if stub_result.stderr is not None else ''
            stub_output = stub_stdout + '\n' + stub_stderr
            # 检查全局变量等
            detector_result = subprocess.run(
                [sys.executable, 'tools/stub_detector.py'],
                capture_output=True, text=True, cwd=Path.cwd()
            )
            detector_stdout = detector_result.stdout if detector_result.stdout is not None else ''
            detector_stderr = detector_result.stderr if detector_result.stderr is not None else ''
            detector_output = detector_stdout + '\n' + detector_stderr
            # 解析结果
            if 'CRITICAL' in stub_output or 'critical' in stub_output or '空函数' in detector_output or '空类' in detector_output or 'Mock' in detector_output or '全局变量' in detector_output:
                return {
                    'status': 'failed',
                    'message': '检测到P0/P1原则违规（桩子、空函数、空类、Mock、全局变量等）',
                    'details': stub_output + '\n' + detector_output
                }
            return {
                'status': 'passed',
                'message': 'P0/P1原则检查通过',
                'details': stub_output + '\n' + detector_output
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'P0/P1原则检查过程出错: {str(e)}',
                'details': str(e)
            }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """
        运行所有质量检查
        
        Returns:
            Dict[str, Any]: 检查结果汇总
            
        Author: AI Assistant (Claude)
        Date: 2025-01-28
        AI Assisted: 是
        """
        print("🚀 开始自动化质量检查...")
        
        # 定义所有检查项
        checks = {
            'file_headers': self.check_file_headers,
            'api_documentation': self.check_api_documentation,
            'page_elements': self.check_page_elements,
            'code_style': self.check_code_style,
            'documentation': self.check_documentation,
            'p0_p1_principles': self.check_p0_p1_principles
        }
        
        # 执行所有检查
        for check_name, check_func in checks.items():
            print(f"\n📋 执行检查: {check_name}")
            result = check_func()
            self.check_results['checks'][check_name] = result
            
            # 更新统计
            self.check_results['summary']['total_checks'] += 1
            if result['status'] == 'passed':
                self.check_results['summary']['passed_checks'] += 1
                print(f"✅ {result['message']}")
            elif result['status'] == 'failed':
                self.check_results['summary']['failed_checks'] += 1
                print(f"❌ {result['message']}")
            elif result['status'] == 'warning':
                self.check_results['summary']['warnings'] += 1
                print(f"⚠️ {result['message']}")
            else:
                self.check_results['summary']['failed_checks'] += 1
                print(f"💥 {result['message']}")
        
        # 生成建议
        self._generate_recommendations()
        
        return self.check_results
    
    def _generate_recommendations(self):
        """
        生成改进建议
        
        Author: AI Assistant (Claude)
        Date: 2025-01-28
        AI Assisted: 是
        """
        recommendations = []
        
        # 根据检查结果生成建议
        for check_name, result in self.check_results['checks'].items():
            if result['status'] == 'failed':
                if check_name == 'file_headers':
                    recommendations.append("运行 `python tools/fix_project_headers.py` 修复文件头注释")
                elif check_name == 'api_documentation':
                    recommendations.append("更新API接口文档，确保前后端一致性")
                elif check_name == 'page_elements':
                    recommendations.append("统一页面元素ID/Class命名规范")
                elif check_name == 'code_style':
                    recommendations.append("修复代码语法错误，确保代码质量")
                elif check_name == 'documentation':
                    recommendations.append("补充缺失的文档文件")
            elif result['status'] == 'warning':
                recommendations.append(f"完善 {check_name} 检查工具")
        
        # 添加通用建议
        if self.check_results['summary']['failed_checks'] > 0:
            recommendations.append("建议在CI/CD流程中集成自动化质量检查")
            recommendations.append("建立代码审查机制，确保规范执行")
        
        self.check_results['recommendations'] = recommendations
    
    def generate_report(self) -> str:
        """
        生成质量检查报告
        
        Returns:
            str: 格式化的报告
            
        Author: AI Assistant (Claude)
        Date: 2025-01-28
        AI Assisted: 是
        """
        summary = self.check_results['summary']
        
        report = f"""# 自动化质量检查报告

## 📊 检查概览
- **检查时间**: {self.check_results['timestamp']}
- **总检查项**: {summary['total_checks']}
- **通过检查**: {summary['passed_checks']}
- **失败检查**: {summary['failed_checks']}
- **警告检查**: {summary['warnings']}

## 📋 详细检查结果

"""
        
        # 检查结果详情
        for check_name, result in self.check_results['checks'].items():
            status_icon = {
                'passed': '✅',
                'failed': '❌',
                'warning': '⚠️',
                'error': '💥'
            }.get(result['status'], '❓')
            
            report += f"### {status_icon} {check_name.replace('_', ' ').title()}\n"
            report += f"**状态**: {result['status'].upper()}\n"
            report += f"**消息**: {result['message']}\n"
            if result.get('details'):
                report += f"**详情**: {result['details'][:200]}...\n" if len(result['details']) > 200 else f"**详情**: {result['details']}\n"
            report += "\n"
        
        # 改进建议
        if self.check_results['recommendations']:
            report += "## 🎯 改进建议\n\n"
            for i, recommendation in enumerate(self.check_results['recommendations'], 1):
                report += f"{i}. {recommendation}\n"
            report += "\n"
        
        # 总结
        if summary['failed_checks'] == 0:
            report += "## 🎉 检查总结\n\n✅ **所有质量检查都通过了！** 项目代码质量良好，符合开发规范。\n"
        else:
            report += f"## ⚠️ 检查总结\n\n❌ **发现 {summary['failed_checks']} 个问题需要修复**。请按照上述建议进行改进。\n"
        
        report += f"\n**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return report
    
    def save_report(self, output_file: str = "quality_check_report.md"):
        """
        保存检查报告
        
        Args:
            output_file (str): 输出文件名
            
        Author: AI Assistant (Claude)
        Date: 2025-01-28
        AI Assisted: 是
        """
        report = self.generate_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 质量检查报告已保存到: {output_file}")
        
        # 同时保存JSON格式的详细结果
        json_file = output_file.replace('.md', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.check_results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 详细结果已保存到: {json_file}")


def main():
    """
    主函数
    
    Author: AI Assistant (Claude)
    Date: 2025-01-28
    AI Assisted: 是
    """
    checker = AutomatedQualityChecker()
    
    # 运行所有检查
    results = checker.run_all_checks()
    
    # 生成报告
    report = checker.generate_report()
    print("\n" + "="*50)
    print(report)
    print("="*50)
    
    # 保存报告
    checker.save_report()
    
    # 返回退出码
    if results['summary']['failed_checks'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()