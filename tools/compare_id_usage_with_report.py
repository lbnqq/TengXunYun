#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ID使用与报告比对工具

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

ID_PATTERN = re.compile(r'getElementById\(["\']([\w\-]+)["\']\)|By\.ID,\s*["\']([\w\-]+)["\']|querySelector\(["\']#([\w\-]+)["\']\)')
CODE_DIRS = ['src', 'static/js', 'tests']
ID_REPORT_PATH = 'id_class_report.md'
REPORT_PATH = 'id_usage_diff_report.md'

# 提取代码中所有id及位置
id_usage = {}
for base in CODE_DIRS:
    for root, _, files in os.walk(base):
        for file in files:
            if file.endswith('.py') or file.endswith('.js'):
                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        for m in ID_PATTERN.findall(line):
                            for id_ in m:
                                if id_:
                                    id_usage.setdefault(id_, []).append(f'{os.path.join(root, file)}:{i}')

# 提取对照表中所有id
id_report = set()
with open(ID_REPORT_PATH, 'r', encoding='utf-8') as f:
    in_id = False
    for line in f:
        if line.strip() == '## id 列表':
            in_id = True
            continue
        if line.strip().startswith('## class 列表'):
            break
        if in_id and line.strip().startswith('- '):
            id_report.add(line.strip()[2:])

not_in_report = set(id_usage) - id_report
not_in_code = id_report - set(id_usage)

with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('# 页面元素id实现与对照表差异详细报告\n\n')
    f.write('## 代码中用到但页面未覆盖的id\n')
    for id_ in sorted(not_in_report):
        f.write(f'- {id_}\n')
        for loc in id_usage[id_]:
            f.write(f'    - 调用位置: {loc}\n')
        f.write('    - 建议: 补充页面元素或移除无效调用\n')
    f.write('\n## 页面有但代码未用到的id\n')
    for id_ in sorted(not_in_code):
        f.write(f'- {id_}\n')
        f.write('    - 建议: 清理冗余页面元素或补充相关逻辑\n')

print(f'已生成 {REPORT_PATH}')