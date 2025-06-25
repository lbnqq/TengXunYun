#!/usr/bin/env python3
"""
文件头注释检查工具

检查Python和JavaScript文件是否包含符合项目规范的文件头注释。
确保所有代码文件都包含作者信息、创建时间、AI辅助标记等必要信息。

Author: AI Assistant (Claude)
Created: 2025-06-25
Last Modified: 2025-06-25
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

class FileHeaderChecker:
    """
    文件头注释检查器
    
    检查代码文件是否包含符合项目规范的文件头注释，
    包括作者信息、创建时间、AI辅助标记等。
    
    Author: AI Assistant (Claude)
    Date: 2025-06-25
    AI Assisted: 是
    """
    
    def __init__(self):
        """
        初始化文件头检查器
        
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        # Python文件头模式
        self.python_patterns = {
            'shebang': r'^#!/usr/bin/env python3',
            'docstring_start': r'^"""',
            'author': r'Author:\s*(.+)',
            'created': r'Created:\s*(\d{4}-\d{2}-\d{2})',
            'modified': r'Last Modified:\s*(\d{4}-\d{2}-\d{2})',
            'modified_by': r'Modified By:\s*(.+)',
            'ai_assisted': r'AI Assisted:\s*(是|否|Yes|No)',
            'version': r'Version:\s*(v?\d+\.\d+)',
            'license': r'License:\s*(.+)'
        }
        
        # JavaScript文件头模式
        self.js_patterns = {
            'comment_start': r'^/\*\*',
            'author': r'\*\s*@author\s+(.+)',
            'date': r'\*\s*@date\s+(\d{4}-\d{2}-\d{2})',
            'ai_assisted': r'\*\s*@ai_assisted\s+(是|否|Yes|No)',
            'version': r'\*\s*@version\s+(v?\d+\.\d+)',
            'license': r'\*\s*@license\s+(.+)'
        }
        
        # 必需字段
        self.required_fields = {
            'python': ['author', 'created', 'ai_assisted'],
            'javascript': ['author', 'date', 'ai_assisted']
        }
        
        # 忽略的文件和目录
        self.ignore_patterns = {
            '__pycache__', '.git', '.venv', 'venv', 'node_modules',
            '.pytest_cache', 'test_', '__init__.py'
        }
    
    def should_ignore(self, file_path: Path) -> bool:
        """
        检查是否应该忽略该文件
        
        Args:
            file_path (Path): 文件路径
            
        Returns:
            bool: 是否应该忽略
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        path_str = str(file_path)
        file_name = file_path.name
        
        # 检查忽略模式
        for pattern in self.ignore_patterns:
            if pattern in path_str or file_name.startswith(pattern):
                return True
        
        # 忽略测试文件和临时文件
        if file_name.startswith('test_') or file_name.endswith('.tmp'):
            return True
        
        return False
    
    def read_file_header(self, file_path: Path, max_lines: int = 30) -> str:
        """
        读取文件头部内容
        
        Args:
            file_path (Path): 文件路径
            max_lines (int): 最大读取行数
            
        Returns:
            str: 文件头部内容
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.rstrip())
                return '\n'.join(lines)
        except (UnicodeDecodeError, IOError):
            return ""
    
    def check_python_header(self, content: str) -> Dict[str, Any]:
        """
        检查Python文件头
        
        Args:
            content (str): 文件内容
            
        Returns:
            Dict[str, Any]: 检查结果
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        result = {
            'valid': True,
            'missing_fields': [],
            'found_fields': {},
            'errors': []
        }
        
        # 检查shebang
        if not re.search(self.python_patterns['shebang'], content, re.MULTILINE):
            result['errors'].append("缺少shebang行: #!/usr/bin/env python3")
        
        # 检查文档字符串开始
        if not re.search(self.python_patterns['docstring_start'], content, re.MULTILINE):
            result['errors'].append("缺少文档字符串开始标记")
            result['valid'] = False
            return result
        
        # 检查必需字段
        for field in self.required_fields['python']:
            pattern = self.python_patterns[field]
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                result['found_fields'][field] = match.group(1).strip()
            else:
                result['missing_fields'].append(field)
                result['valid'] = False
        
        # 检查可选字段
        optional_fields = ['modified', 'modified_by', 'version', 'license']
        for field in optional_fields:
            if field in self.python_patterns:
                pattern = self.python_patterns[field]
                match = re.search(pattern, content, re.MULTILINE)
                if match:
                    result['found_fields'][field] = match.group(1).strip()
        
        return result
    
    def check_javascript_header(self, content: str) -> Dict[str, Any]:
        """
        检查JavaScript文件头
        
        Args:
            content (str): 文件内容
            
        Returns:
            Dict[str, Any]: 检查结果
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        result = {
            'valid': True,
            'missing_fields': [],
            'found_fields': {},
            'errors': []
        }
        
        # 检查注释开始
        if not re.search(self.js_patterns['comment_start'], content, re.MULTILINE):
            result['errors'].append("缺少JSDoc注释开始标记: /**")
            result['valid'] = False
            return result
        
        # 检查必需字段
        for field in self.required_fields['javascript']:
            pattern = self.js_patterns[field]
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                result['found_fields'][field] = match.group(1).strip()
            else:
                result['missing_fields'].append(field)
                result['valid'] = False
        
        # 检查可选字段
        optional_fields = ['version', 'license']
        for field in optional_fields:
            if field in self.js_patterns:
                pattern = self.js_patterns[field]
                match = re.search(pattern, content, re.MULTILINE)
                if match:
                    result['found_fields'][field] = match.group(1).strip()
        
        return result
    
    def check_file(self, file_path: Path) -> Dict[str, Any]:
        """
        检查单个文件
        
        Args:
            file_path (Path): 文件路径
            
        Returns:
            Dict[str, Any]: 检查结果
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        if self.should_ignore(file_path):
            return {'skipped': True, 'reason': 'ignored'}
        
        content = self.read_file_header(file_path)
        if not content:
            return {'valid': False, 'errors': ['无法读取文件内容']}
        
        # 根据文件扩展名选择检查方法
        if file_path.suffix == '.py':
            return self.check_python_header(content)
        elif file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
            return self.check_javascript_header(content)
        else:
            return {'skipped': True, 'reason': 'unsupported file type'}
    
    def check_directory(self, directory: Path) -> Dict[str, Any]:
        """
        检查目录中的所有文件
        
        Args:
            directory (Path): 目录路径
            
        Returns:
            Dict[str, Any]: 检查结果汇总
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        results = {
            'total_files': 0,
            'checked_files': 0,
            'valid_files': 0,
            'invalid_files': 0,
            'skipped_files': 0,
            'file_results': {}
        }
        
        # 支持的文件扩展名
        supported_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx'}
        
        # 遍历目录
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in supported_extensions:
                results['total_files'] += 1
                
                # 检查文件
                file_result = self.check_file(file_path)
                results['file_results'][str(file_path)] = file_result
                
                if file_result.get('skipped'):
                    results['skipped_files'] += 1
                else:
                    results['checked_files'] += 1
                    if file_result.get('valid', False):
                        results['valid_files'] += 1
                    else:
                        results['invalid_files'] += 1
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        生成检查报告
        
        Args:
            results (Dict[str, Any]): 检查结果
            
        Returns:
            str: 格式化的报告
            
        Author: AI Assistant (Claude)
        Date: 2025-06-25
        AI Assisted: 是
        """
        report = f"""# 文件头注释检查报告

## 📊 检查统计
- **总文件数**: {results['total_files']}
- **检查文件数**: {results['checked_files']}
- **有效文件数**: {results['valid_files']}
- **无效文件数**: {results['invalid_files']}
- **跳过文件数**: {results['skipped_files']}

## 📋 检查结果
"""
        
        if results['invalid_files'] > 0:
            report += "\n### ❌ 无效文件\n"
            for file_path, result in results['file_results'].items():
                if not result.get('valid', True) and not result.get('skipped'):
                    report += f"\n**{file_path}**:\n"
                    
                    if result.get('missing_fields'):
                        report += f"- 缺少字段: {', '.join(result['missing_fields'])}\n"
                    
                    if result.get('errors'):
                        for error in result['errors']:
                            report += f"- 错误: {error}\n"
        
        if results['valid_files'] > 0:
            report += f"\n### ✅ 有效文件 ({results['valid_files']} 个)\n"
            report += "所有检查的文件都包含必需的文件头信息。\n"
        
        report += f"""
---
**检查工具**: 文件头注释检查器  
**检查时间**: {os.environ.get('USER', 'Unknown')} - {Path.cwd()}  
**生成时间**: 2025-06-25
"""
        
        return report

def main():
    """
    主函数
    
    Author: AI Assistant (Claude)
    Date: 2025-06-25
    AI Assisted: 是
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="文件头注释检查工具")
    parser.add_argument("paths", nargs="*", default=["."], help="要检查的文件或目录路径")
    parser.add_argument("--report", help="输出报告到文件")
    parser.add_argument("--strict", action="store_true", help="严格模式，任何错误都返回非零退出码")
    
    args = parser.parse_args()
    
    checker = FileHeaderChecker()
    all_results = {
        'total_files': 0,
        'checked_files': 0,
        'valid_files': 0,
        'invalid_files': 0,
        'skipped_files': 0,
        'file_results': {}
    }
    
    # 检查所有指定的路径
    for path_str in args.paths:
        path = Path(path_str)
        
        if path.is_file():
            # 检查单个文件
            result = checker.check_file(path)
            all_results['file_results'][str(path)] = result
            all_results['total_files'] += 1
            
            if result.get('skipped'):
                all_results['skipped_files'] += 1
            else:
                all_results['checked_files'] += 1
                if result.get('valid', False):
                    all_results['valid_files'] += 1
                else:
                    all_results['invalid_files'] += 1
        
        elif path.is_dir():
            # 检查目录
            dir_results = checker.check_directory(path)
            
            # 合并结果
            all_results['total_files'] += dir_results['total_files']
            all_results['checked_files'] += dir_results['checked_files']
            all_results['valid_files'] += dir_results['valid_files']
            all_results['invalid_files'] += dir_results['invalid_files']
            all_results['skipped_files'] += dir_results['skipped_files']
            all_results['file_results'].update(dir_results['file_results'])
    
    # 生成报告
    report = checker.generate_report(all_results)
    
    # 输出报告
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 报告已保存到: {args.report}")
    else:
        print(report)
    
    # 检查是否有错误
    if all_results['invalid_files'] > 0:
        print(f"\n❌ 发现 {all_results['invalid_files']} 个文件头注释不符合规范")
        if args.strict:
            sys.exit(1)
    else:
        print(f"\n✅ 所有 {all_results['checked_files']} 个文件的头注释都符合规范")

if __name__ == "__main__":
    main()
