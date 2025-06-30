#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API使用与文档比对工具

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

API_PATTERN = re.compile(r'(/api/[\w\-/<>]+)')
PY_JS_DIRS = ['src', 'tests']
API_DOC_PATH = 'openapi_report.md'
REPORT_PATH = 'api_usage_diff_report.md'

# 提取代码中所有API路径及位置
api_usage = {}
for base in PY_JS_DIRS:
    for root, _, files in os.walk(base):
        for file in files:
            if file.endswith('.py') or file.endswith('.js'):
                with open(os.path.join(root, file), encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        for api in API_PATTERN.findall(line):
                            api_usage.setdefault(api, []).append(f'{os.path.join(root, file)}:{i}')

if not os.path.exists(API_DOC_PATH):
    print(f"API文档 {API_DOC_PATH} 不存在，跳过API接口文档一致性检查。")
    exit(0)

# 提取文档中所有API路径及说明
api_doc = {}
with open(API_DOC_PATH, 'r', encoding='utf-8') as f:
    last_path = None
    for line in f:
        if line.strip().startswith('- 路径:'):
            last_path = line.split('`')[1]
        if line.strip().startswith('说明:') and last_path:
            api_doc[last_path] = line.strip()[3:].strip()
            last_path = None

not_in_doc = set(api_usage) - set(api_doc)
not_in_code = set(api_doc) - set(api_usage)

with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('# API接口实现与文档差异详细报告\n\n')
    f.write('## 代码中出现但文档未覆盖的API\n')
    for api in sorted(not_in_doc):
        f.write(f'- {api}\n')
        for loc in api_usage[api]:
            f.write(f'    - 调用位置: {loc}\n')
        f.write('    - 建议: 补充接口文档或移除无效调用\n')
    f.write('\n## 文档中有但代码未实现的API\n')
    for api in sorted(not_in_code):
        f.write(f'- {api}\n')
        f.write(f'    - 文档说明: {api_doc[api]}\n')
        f.write('    - 建议: 实现该接口或清理文档冗余\n')

print(f'已生成 {REPORT_PATH}')