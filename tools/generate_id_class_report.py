import os
import re

REPORT_PATH = 'id_class_report.md'
TEMPLATE_DIR = 'templates'

id_pattern = re.compile(r'id=["\']([\w\-]+)["\']')
class_pattern = re.compile(r'class=["\']([\w\-\s]+)["\']')

id_set = set()
class_set = set()

for root, _, files in os.walk(TEMPLATE_DIR):
    for file in files:
        if file.endswith('.html'):
            with open(os.path.join(root, file), encoding='utf-8') as f:
                content = f.read()
                id_set.update(id_pattern.findall(content))
                for cls in class_pattern.findall(content):
                    class_set.update(cls.split())

with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write('# 页面元素 id/class 对照表\n\n')
    f.write('## id 列表\n')
    for id_ in sorted(id_set):
        f.write(f'- {id_}\n')
    f.write('\n## class 列表\n')
    for cls in sorted(class_set):
        f.write(f'- {cls}\n')

print(f'已生成 {REPORT_PATH}') 