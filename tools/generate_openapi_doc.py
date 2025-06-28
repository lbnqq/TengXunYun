import re

ROUTE_PATTERN = re.compile(r"@app\.route\(['\"](.*?)['\"](?:,\s*methods=\[(.*?)\])?\)")
DEF_PATTERN = re.compile(r"def (\w+)\(")
DOCSTRING_PATTERN = re.compile(r'"""(.*?)"""', re.DOTALL)

api_list = []
with open('src/web_app.py', encoding='utf-8') as f:
    content = f.read()
    routes = list(ROUTE_PATTERN.finditer(content))
    defs = list(DEF_PATTERN.finditer(content))
    docstrings = list(DOCSTRING_PATTERN.finditer(content))

    for i, route in enumerate(routes):
        path = route.group(1)
        methods = route.group(2) or 'GET'
        # 查找下一个 def
        def_idx = next((j for j, d in enumerate(defs) if d.start() > route.end()), None)
        doc = ''
        if def_idx is not None and def_idx < len(docstrings):
            doc = docstrings[def_idx].group(1).strip()
        api_list.append({'path': path, 'methods': methods, 'doc': doc})

with open('openapi_report.md', 'w', encoding='utf-8') as f:
    f.write('# API接口自动化文档\n\n')
    for api in api_list:
        f.write(f"- 路径: `{api['path']}`\n  方法: {api['methods']}\n  说明: {api['doc']}\n\n")

print('已生成 openapi_report.md') 