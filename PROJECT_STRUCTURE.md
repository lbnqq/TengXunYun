# aiDoc 项目结构说明

## 📁 项目目录结构

```
aiDoc/
├── 📄 README.md                    # 项目说明文档
├── 📄 README_USAGE.md              # 使用说明文档
├── 📄 PROJECT_STATUS.md            # 项目状态文档
├── 📄 SOLUTION_SUMMARY.md          # 解决方案总结
├── 📄 requirements.txt             # Python依赖包列表
├── 📄 run_app.py                   # 应用启动脚本
├── 📄 start.bat                    # Windows启动脚本
├── 📄 start.sh                     # Linux/Mac启动脚本
│
├── 📁 src/                         # 源代码目录
│   ├── 📄 web_app.py              # Flask Web应用主文件
│   ├── 📄 main.py                 # 主程序入口
│   ├── 📄 doc_processor.py        # 文档处理模块
│   ├── 📄 layout_analyzer.py      # 布局分析模块
│   ├── 📄 ocr_engine.py           # OCR引擎模块
│   ├── 📄 table_parser.py         # 表格解析模块
│   ├── 📄 utils.py                # 工具函数
│   ├── 📁 core/                   # 核心功能模块
│   ├── 📁 llm_clients/            # LLM客户端模块
│   └── 📁 uploads/                # 上传文件临时存储
│
├── 📁 static/                      # 静态资源目录
│   ├── 📁 css/                    # CSS样式文件
│   ├── 📁 js/                     # JavaScript脚本文件
│   └── 📄 favicon.ico             # 网站图标
│
├── 📁 templates/                   # HTML模板目录
│   ├── 📄 enhanced-frontend-complete.html  # 主界面模板
│   ├── 📄 dashboard.html          # 仪表板模板
│   ├── 📄 demo.html               # 演示页面模板
│   └── 📄 smart_fill_demo.html    # 智能填报演示模板
│
├── 📁 config/                      # 配置文件目录
│   └── 📄 config.yaml             # 主配置文件
│
├── 📁 docs/                        # 文档目录
│   ├── 📄 UserGuide.md            # 用户指南
│   ├── 📄 DeveloperGuide.md       # 开发者指南
│   ├── 📄 APIReference.md         # API参考文档
│   └── 📄 AI编程项目终极实践手册.md # AI编程实践手册
│
├── 📁 examples/                    # 示例文件目录
│   ├── 📄 contract_template.txt   # 合同模板示例
│   ├── 📄 patent_application_template.txt # 专利申请模板
│   └── 📄 writing_style_samples.md # 写作风格示例
│
├── 📁 models/                      # 模型文件目录
│   ├── 📁 hf_cache/               # Hugging Face缓存
│   └── 📁 paddleocr/              # PaddleOCR模型
│
├── 📁 tools/                       # 开发工具目录
│   ├── 📄 automated_quality_check.py # 自动化质量检查
│   ├── 📄 code_template_generator.py # 代码模板生成器
│   └── 📄 project_status_checker.py  # 项目状态检查器
│
├── 📁 cliTests/                    # CLI测试套件
│   ├── 📄 run_all_tests.py        # 运行所有测试
│   ├── 📄 test_format_alignment.py # 格式对齐测试
│   └── 📄 test_document_fill.py   # 文档填报测试
│
├── 📁 uploads/                     # 文件上传目录
│   └── 📁 images/                 # 图片上传目录
│
└── 📁 data/                        # 数据目录
```

## 🚀 核心功能模块

### 1. 智能填报模块
- **位置**: `src/core/tools/integrated_smart_fill_manager.py`
- **功能**: 年度总结生成、简历填报
- **LLM**: 集成星火X1大模型

### 2. 格式对齐模块
- **位置**: `src/core/tools/format_alignment_coordinator.py`
- **功能**: 文档格式智能对齐
- **LLM**: 使用星火X1进行格式化处理
- **特性**: 支持多轮对话、TXT/DOCX导出

### 3. 文风对齐模块
- **位置**: `src/core/tools/`
- **功能**: 文档风格统一处理

### 4. 文档审查模块
- **位置**: `src/core/tools/`
- **功能**: 智能文档审查和建议

### 5. 表格填报模块
- **位置**: `src/core/tools/`
- **功能**: 智能表格数据填充

## 🔧 启动方式

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
./start.sh
```

### Python直接启动
```bash
python run_app.py
```

## 📝 开发说明

- **主要技术栈**: Flask, Python, JavaScript, HTML/CSS
- **LLM集成**: 星火X1大模型
- **前端框架**: 原生JavaScript + 现代CSS
- **文件处理**: 支持DOCX, TXT, PDF等格式
- **部署方式**: 本地部署，Web界面访问

## 🧪 测试

项目包含完整的CLI测试套件，位于 `cliTests/` 目录：

```bash
cd cliTests
python run_all_tests.py
```

## 📚 文档

详细文档请参考 `docs/` 目录中的相关文件：
- 用户使用指南
- 开发者文档
- API参考手册

---

**注意**: 本项目已清理所有临时测试文件，保持项目结构整洁。如需进行开发测试，请使用 `cliTests/` 目录中的正式测试套件。
