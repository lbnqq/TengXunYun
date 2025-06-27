import os

# 项目目录结构
DIRS = [
    'src/core/tools',
    'src/core/agent',
    'src/core/guidance',
    'src/core/knowledge_base',
    'src/utils',
    'tests',
    'config',
    'output',
    'src/llm_clients',
]

FILES = {
    'requirements.txt': '''flask
python-docx
PyPDF2
python-dotenv
# transformers
# openai
''',
    '.env': '''# .env file for office-doc-agent
XINGCHENG_API_KEY=YOUR_XINGCHENG_API_KEY
XINGCHENG_API_SECRET=YOUR_XINGCHENG_API_SECRET
LLM_MODEL_NAME=SparkMax
''',
    '.gitignore': '''# Python environment
venv/
*.pyc
__pycache__/
data/
''',
    'src/main.py': '# 主程序入口，后续可补充实现\n',
}

def make_dirs():
    for d in DIRS:
        os.makedirs(d, exist_ok=True)
    print('目录结构已创建')

def make_files():
    for path, content in FILES.items():
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    print('基础文件已生成')

def main():
    make_dirs()
    make_files()
    print('项目初始化完成！')

if __name__ == '__main__':
    main() 