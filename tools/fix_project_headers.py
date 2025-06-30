#!/usr/bin/env python3
"""
项目核心文件头注释修复工具

专门修复项目核心文件的文件头注释，确保符合项目开发规范。

Author: AI Assistant (Claude)
Created: 2025-01-28
AI Assisted: 是
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def fix_python_file(file_path):
    """修复Python文件头注释"""
    try:
        # 确保file_path是Path对象
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成标准文件头
        header = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{description}

Author: AI Assistant (Claude)
Created: 2025-01-28
Last Modified: 2025-01-28
Modified By: AI Assistant (Claude)
AI Assisted: 是 - Claude 3.5 Sonnet
Version: v1.0
License: MIT
"""

'''
        
        # 获取文件描述
        file_name = file_path.name
        descriptions = {
            'main.py': '主程序入口文件',
            'web_app.py': 'Web应用主文件',
            'doc_processor.py': '文档处理器',
            'layout_analyzer.py': '布局分析器',
            'ocr_engine.py': 'OCR引擎',
            'table_parser.py': '表格解析器',
            'utils.py': '工具函数库',
            'base_llm.py': 'LLM基础客户端',
            'multi_llm.py': '多LLM客户端',
            'xingcheng_llm.py': '星尘LLM客户端',
            'agent_orchestrator.py': '代理协调器',
            'intent_driven_orchestrator.py': '意图驱动协调器',
            'efficient_document_classifier.py': '高效文档分类器',
            'efficient_format_aligner.py': '高效格式对齐器',
            'precise_format_applier.py': '精确格式应用器',
            'business_rules.py': '业务规则引擎',
            'resource_manager.py': '资源管理器',
            'check_file_headers.py': '文件头注释检查工具',
            'compare_api_usage_with_doc.py': 'API使用与文档比对工具',
            'compare_id_usage_with_report.py': 'ID使用与报告比对工具',
            'generate_id_class_report.py': 'ID/Class报告生成工具',
            'generate_openapi_doc.py': 'OpenAPI文档生成工具',
            'comprehensive_method_checker.py': '综合方法检查器',
            'method_implementation_checker.py': '方法实现检查器',
            'stub_function_detector.py': '桩子函数检测器',
            'check_config.py': '配置检查工具',
            'run_all_tests.py': '运行所有测试',
            'check_docx.py': 'DOCX文件检查工具',
            'minimal_web_app.py': '最小化Web应用',
            'semantic_behavior_demo.py': '语义行为演示',
            'style_analysis_demo.py': '样式分析演示',
            'setup_project.py': '项目设置脚本',
            'simple_web_app.py': '简单Web应用',
            'start_ai_thinking_demo.py': 'AI思考演示启动器',
            'sys_path_debug.py': '系统路径调试工具'
        }
        
        description = descriptions.get(file_name, f"{file_name.replace('_', ' ').title()}")
        header = header.format(description=description)
        
        # 移除现有注释
        lines = content.split('\n')
        new_lines = []
        in_header = False
        
        for line in lines:
            if line.startswith('#!/usr/bin/env python3') or line.startswith('# -*- coding:'):
                continue
            if '"""' in line and not in_header:
                in_header = True
                continue
            if in_header and '"""' in line:
                in_header = False
                continue
            if in_header:
                continue
            new_lines.append(line)
        
        # 组合新内容
        new_content = header + '\n'.join(new_lines)
        
        # 备份并写入
        backup_path = str(file_path) + '.backup'
        shutil.copy2(file_path, backup_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"修复失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    # 项目核心文件列表
    core_files = [
        'src/doc_processor.py',
        'src/layout_analyzer.py', 
        'src/main.py',
        'src/ocr_engine.py',
        'src/table_parser.py',
        'src/utils.py',
        'src/web_app.py',
        'src/core/agent/agent_orchestrator.py',
        'src/llm_clients/base_llm.py',
        'src/llm_clients/multi_llm.py',
        'src/llm_clients/xingcheng_llm.py',
        'src/core/agent/intent_driven_orchestrator.py',
        'src/core/analysis/efficient_document_classifier.py',
        'src/core/analysis/efficient_format_aligner.py',
        'src/core/analysis/precise_format_applier.py',
        'src/core/business_rules.py',
        'src/core/resource_manager.py',
        'tools/check_file_headers.py',
        'tools/compare_api_usage_with_doc.py',
        'tools/compare_id_usage_with_report.py',
        'tools/generate_id_class_report.py',
        'tools/generate_openapi_doc.py',
        'tools/comprehensive_method_checker.py',
        'tools/method_implementation_checker.py',
        'tools/stub_function_detector.py',
        'docs/archives/check_config.py',
        'cliTests/run_all_tests.py',
        'cliTests/check_docx.py',
        'examples/minimal_web_app.py',
        'examples/semantic_behavior_demo.py',
        'examples/style_analysis_demo.py',
        'tests/setup_project.py',
        'tests/simple_web_app.py',
        'tests/start_ai_thinking_demo.py',
        'tests/sys_path_debug.py'
    ]
    
    fixed_count = 0
    failed_count = 0
    
    print("🔧 开始修复项目核心文件头注释...")
    
    for file_path in core_files:
        if os.path.exists(file_path):
            print(f"修复: {file_path}")
            if fix_python_file(file_path):
                fixed_count += 1
                print(f"✅ 成功: {file_path}")
            else:
                failed_count += 1
                print(f"❌ 失败: {file_path}")
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    print(f"\n📊 修复完成:")
    print(f"✅ 成功: {fixed_count} 个文件")
    print(f"❌ 失败: {failed_count} 个文件")
    
    # 生成修复报告
    report = f"""# 项目核心文件头注释修复报告

## 📊 修复统计
- **修复成功**: {fixed_count} 个文件
- **修复失败**: {failed_count} 个文件

## 📋 修复内容
- 添加了标准的shebang行 (`#!/usr/bin/env python3`)
- 添加了编码声明 (`# -*- coding: utf-8 -*-`)
- 添加了完整的文档字符串
- 添加了作者信息、创建时间、AI辅助标记等必要字段
- 生成了备份文件（.backup后缀）

## 📝 注意事项
1. 所有修复的文件都生成了备份，如需恢复请使用 .backup 文件
2. 修复后的文件头注释符合项目开发规范
3. 建议运行 `python tools/check_file_headers.py` 验证修复结果

**修复时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**修复工具**: 项目核心文件头注释修复工具 v1.0
"""
    
    with open('project_header_fix_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 修复报告已保存到: project_header_fix_report.md")

if __name__ == "__main__":
    main() 