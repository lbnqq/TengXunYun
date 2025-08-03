# AI_Pytest7 智能文档助手 - 完整使用指南

## 📋 项目概述

**AI_Pytest7** 是一个基于AI的智能文档处理系统，专注于文档组装、文风检测和智能审批。该系统集成了多种AI模型，能够智能处理各种类型的文档，提供专业的文档处理服务。

### 🎯 核心定位
- **智能文档组装**：将分散内容智能组装成专业文档
- **文风检测与统一**：确保文档风格一致性和专业性  
- **智能审批与质量检查**：AI多角色评审，提供专业建议
- **格式标准化**：自动调整文档格式符合行业标准
- **质量保证**：多维度检查确保文档质量

### 🚀 主要特性
- ✅ **多模型支持**：集成星火X1、通义千问等主流AI模型
- ✅ **智能识别**：自动识别文档结构和待填写区域
- ✅ **多轮对话**：智能引导用户完成文档填写
- ✅ **格式保持**：保持原文档格式和结构
- ✅ **批量处理**：支持多个文档同时处理
- ✅ **质量检查**：AI辅助文档质量评估

---

## 🏗️ 项目结构

```
AI_Pytest7/
├── aiDoc/                          # 主项目目录
│   ├── 📄 README.md               # 项目说明文档
│   ├── 📄 README_USAGE.md         # 使用说明文档
│   ├── 📄 PROJECT_STATUS.md       # 项目状态文档
│   ├── 📄 requirements.txt        # Python依赖包列表
│   ├── 📄 run_app.py             # 应用启动脚本
│   ├── 📄 start.bat              # Windows启动脚本
│   ├── 📄 start.sh               # Linux/Mac启动脚本
│   │
│   ├── 📁 src/                   # 源代码目录
│   │   ├── 📄 web_app.py         # Flask Web应用主文件
│   │   ├── 📄 main.py            # 主程序入口
│   │   ├── 📄 doc_processor.py   # 文档处理模块
│   │   ├── 📄 layout_analyzer.py # 布局分析模块
│   │   ├── 📄 ocr_engine.py      # OCR引擎模块
│   │   ├── 📄 table_parser.py    # 表格解析模块
│   │   ├── 📄 utils.py           # 工具函数
│   │   ├── 📁 core/              # 核心功能模块
│   │   │   ├── 📁 agent/         # AI代理协调器
│   │   │   ├── 📁 analysis/      # 文档分析引擎
│   │   │   ├── 📁 tools/         # 核心工具集
│   │   │   ├── 📁 knowledge_base/ # 知识库
│   │   │   └── 📁 monitoring/    # 性能监控
│   │   ├── 📁 llm_clients/       # LLM客户端模块
│   │   └── 📁 uploads/           # 上传文件临时存储
│   │
│   ├── 📁 static/                # 静态资源目录
│   │   ├── 📁 css/               # CSS样式文件
│   │   ├── 📁 js/                # JavaScript脚本文件
│   │   └── 📄 favicon.ico        # 网站图标
│   │
│   ├── 📁 templates/             # HTML模板目录
│   │   ├── 📄 enhanced-frontend-complete.html # 主界面模板
│   │   ├── 📄 dashboard.html     # 仪表板模板
│   │   ├── 📄 demo.html          # 演示页面模板
│   │   └── 📄 smart_fill_demo.html # 智能填报演示模板
│   │
│   ├── 📁 config/                # 配置文件目录
│   │   └── 📄 config.yaml        # 主配置文件
│   │
│   ├── 📁 docs/                  # 文档目录
│   │   ├── 📄 UserGuide.md       # 用户指南
│   │   ├── 📄 DeveloperGuide.md  # 开发者指南
│   │   ├── 📄 APIReference.md    # API参考文档
│   │   └── 📄 AI编程项目终极实践手册.md # AI编程实践手册
│   │
│   ├── 📁 examples/              # 示例文件目录
│   │   ├── 📄 contract_template.txt # 合同模板示例
│   │   ├── 📄 patent_application_template.txt # 专利申请模板
│   │   └── 📄 writing_style_samples.md # 写作风格示例
│   │
│   ├── 📁 models/                # 模型文件目录
│   │   ├── 📁 hf_cache/          # Hugging Face缓存
│   │   └── 📁 paddleocr/         # PaddleOCR模型
│   │
│   ├── 📁 tools/                 # 开发工具目录
│   │   ├── 📄 automated_quality_check.py # 自动化质量检查
│   │   ├── 📄 code_template_generator.py # 代码模板生成器
│   │   └── 📄 project_status_checker.py # 项目状态检查器
│   │
│   ├── 📁 cliTests/              # CLI测试套件
│   │   ├── 📄 run_all_tests.py   # 运行所有测试
│   │   ├── 📄 test_format_alignment.py # 格式对齐测试
│   │   ├── 📄 test_style_alignment.py # 文风统一测试
│   │   ├── 📄 test_document_fill.py # 智能填报测试
│   │   ├── 📄 test_document_review.py # 文档评审测试
│   │   └── 📄 test_table_fill.py # 表格填充测试
│   │
│   ├── 📁 uploads/               # 文件上传目录
│   └── 📁 data/                  # 数据目录
│
├── 📁 src/                       # 源代码目录
└── 📁 新功能要求/                 # 新功能需求文档
```

---

## 🛠️ 环境要求

### 系统要求
- **操作系统**：Windows 10/11, Linux, macOS
- **Python版本**：3.8+ (推荐3.12)
- **内存**：8GB+ RAM
- **磁盘空间**：2GB+ 可用空间
- **网络**：稳定的互联网连接（用于AI模型调用）

### 依赖包
项目包含146个Python依赖包，主要包括：
- **Web框架**：Flask 3.1.1
- **AI模型**：transformers, torch, sentence-transformers
- **文档处理**：python-docx, PyPDF2, openpyxl
- **OCR引擎**：paddleocr, opencv-contrib-python
- **测试框架**：pytest, pytest-cov
- **其他工具**：requests, pandas, numpy等

---

## 🚀 快速安装

### 方法1：使用启动脚本（推荐）

#### Windows用户
```powershell
# 进入项目目录
cd aiDoc

# 运行启动脚本
start.bat
```

#### Linux/Mac用户
```bash
# 进入项目目录
cd aiDoc

# 给启动脚本执行权限
chmod +x start.sh

# 运行启动脚本
./start.sh
```

### 方法2：手动安装

#### 1. 克隆项目
```bash
git clone <repository-url>
cd AI_Pytest7/aiDoc
```

#### 2. 创建虚拟环境
```bash
# Windows
python -m venv venv_ci_test
venv_ci_test\Scripts\activate

# Linux/Mac
python3 -m venv venv_ci_test
source venv_ci_test/bin/activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 启动应用
```bash
python run_app.py
```

#### 5. 访问应用
打开浏览器访问：http://localhost:5000

---

## 📖 功能使用指南

### 1. 智能文档组装

#### 格式对齐功能
**功能描述**：将目标文档的格式调整为与参考文档一致

**使用步骤**：
1. 上传参考格式文档（标准格式）
2. 上传待处理文档（需要格式调整）
3. 系统自动分析并调整格式
4. 预览调整结果
5. 下载处理后的文档

**支持格式**：TXT, DOCX, PDF

#### 内容插入功能
**功能描述**：智能识别文档结构，将图表、图片等内容插入到最佳位置

**使用步骤**：
1. 上传文档模板
2. 上传外部内容（图表、图片等）
3. 系统自动分析并建议插入位置
4. 用户确认或调整
5. 系统进行智能组装

### 2. 文风检测与统一

#### 风格分析
**功能描述**：分析文档风格特征和语言模式

**使用步骤**：
1. 上传参考风格文档
2. 上传待调整文档
3. 系统分析风格特征
4. 应用风格到目标文档
5. 预览和导出结果

#### 一致性检查
**功能描述**：确保图表说明、标题等与文档风格一致

**特性**：
- 专业术语建议
- 语气调整
- 语言模式统一

### 3. 智能填报功能

#### 年度总结生成
**功能描述**：基于用户提供的信息自动生成年度总结

**使用步骤**：
1. 选择"年度总结"功能
2. 输入基本信息（姓名、部门、年度等）
3. 系统生成总结内容
4. 预览和调整
5. 下载最终文档

#### 简历生成
**功能描述**：根据求职目标岗位自动调整简历格式和内容重点

**特性**：
- 岗位匹配度分析
- 关键词优化建议
- 格式标准化处理
- 内容完整性检查

### 4. 智能审批与质量检查

#### 文档评审
**功能描述**：AI多角色评审，提供专业建议

**评审角色**：
- **HR专家**：评估简历的岗位匹配度和可读性
- **专业技术人员**：评估技术能力和项目经验描述
- **论文审稿人**：评估学术质量和创新性
- **律师**：审核法律合规性

**使用步骤**：
1. 上传待评审文档
2. 选择评审重点
3. 获取AI评审意见
4. 管理修改建议
5. 导出评审报告

#### 质量评估
**功能描述**：多维度检查确保文档质量

**检查项目**：
- 逻辑一致性验证
- 格式规范性检查
- 内容完整性检查
- 专业术语使用

---

## 🔧 配置说明

### 配置文件位置
```
aiDoc/config/config.yaml
```

### 主要配置项

#### OCR引擎配置
```yaml
ocr_engine:
  name: "paddleocr"
  use_gpu: false
  lang: "ch"
  ocr_model_dir: "models/paddleocr"
```

#### 布局分析配置
```yaml
layout_analyzer:
  hf_model_id: "uer/layoutlmv3-base-finetuned-table-detection-v2"
  model_type: "hf"
  detection_threshold: 0.3
```

#### 意图置信度阈值
```yaml
intent_confidence_thresholds:
  fill_form: 0.8
  format_cleanup: 0.7
  content_completion: 0.6
  style_rewrite: 0.5
```

### AI模型配置

#### 星火X1配置
```python
spark_x1_config = {
    'api_password': 'your-api-password'
}
```

#### 通义千问配置
```python
qianwen_config = {
    'api_key': 'your-api-key'
}
```

---

## 🧪 测试指南

### 运行测试

#### 1. 基础功能测试
```bash
cd aiDoc
python -m pytest tests/ -v
```

#### 2. CLI测试套件
```bash
cd aiDoc/cliTests
python run_all_tests.py
```

#### 3. 单个功能测试
```bash
# 格式对齐测试
python cliTests/test_format_alignment.py source.txt target.txt output.txt

# 文风统一测试
python cliTests/test_style_alignment.py reference.txt target.txt output.txt

# 智能填报测试
python cliTests/test_document_fill.py template.txt data.json output.txt

# 文档评审测试
python cliTests/test_document_review.py document.txt output.txt --review-focus academic
```

### 测试报告

#### JSON报告格式
```json
{
  "test_name": "测试名称",
  "success": true,
  "duration": 2.5,
  "api_calls": [
    {
      "endpoint": "/api/xxx",
      "method": "POST",
      "success": true,
      "response_time": 1.2
    }
  ],
  "errors": [],
  "warnings": []
}
```

#### HTML报告
批量测试会生成可视化的HTML报告，包含：
- 测试摘要
- 详细结果
- 错误信息
- 执行时间

---

## 📊 性能指标

### 处理能力
- **文档大小**：支持最大50MB文档
- **并发处理**：支持10+并发用户
- **响应时间**：平均2-5秒处理时间
- **准确率**：格式对齐95%+，文风检测90%+

### 系统资源
- **CPU使用率**：平均30-50%
- **内存使用**：2-4GB
- **磁盘空间**：根据文档数量动态增长

---

## 🔍 故障排除

### 常见问题

#### 1. 应用启动失败
**症状**：运行 `python run_app.py` 后出现错误

**解决方案**：
```bash
# 检查Python版本
python --version

# 检查依赖安装
pip list

# 重新安装依赖
pip install -r requirements.txt --upgrade
```

#### 2. AI模型连接失败
**症状**：智能功能无法使用

**解决方案**：
```bash
# 检查网络连接
ping api.xfyun.cn

# 检查API配置
cat config/config.yaml

# 测试API连接
python -c "from llm_clients.spark_x1_client import SparkX1Client; client = SparkX1Client('your-api-password'); print(client.is_available())"
```

#### 3. 文件上传失败
**症状**：无法上传文件或文件处理失败

**解决方案**：
```bash
# 检查上传目录权限
ls -la uploads/

# 检查文件格式
file your_document.txt

# 检查文件编码
file -i your_document.txt
```

#### 4. 测试失败
**症状**：运行测试时出现错误

**解决方案**：
```bash
# 运行详细测试
python -m pytest tests/ -v --tb=long

# 检查测试数据
ls -la cliTests/test_data/

# 重新创建测试数据
python cliTests/run_all_tests.py --create-data-only
```

### 日志查看

#### 应用日志
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

#### 测试日志
```bash
# 查看测试日志
tail -f cliTests/test_results/test.log
```

---

## 📚 API参考

### 核心API端点

#### 文档处理
- `POST /api/upload` - 文件上传
- `POST /api/format-alignment` - 格式对齐
- `POST /api/style-alignment` - 文风统一
- `POST /api/document-fill` - 智能填报
- `POST /api/document-review` - 文档评审

#### 智能填报
- `POST /api/smart-fill/generate-summary` - 生成年度总结
- `POST /api/smart-fill/generate-resume` - 生成简历
- `GET /api/smart-fill/status` - 获取系统状态

#### 预览和导出
- `GET /api/format-alignment/preview/<session_id>` - 预览格式对齐结果
- `GET /api/style-alignment/export/<session_id>` - 导出文风调整文档
- `GET /api/document-review/export/<review_session_id>` - 导出评审文档

### API响应格式

#### 成功响应
```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "status": "processing",
    "message": "任务已提交"
  }
}
```

#### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": "详细错误信息"
  }
}
```

---

## 🔄 开发指南

### 环境设置

#### 1. 克隆项目
```bash
git clone <repository-url>
cd AI_Pytest7/aiDoc
```

#### 2. 创建虚拟环境
```bash
python -m venv venv_dev
source venv_dev/bin/activate  # Linux/Mac
# 或
venv_dev\Scripts\activate     # Windows
```

#### 3. 安装开发依赖
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果有开发依赖
```

#### 4. 配置开发环境
```bash
# 复制配置文件
cp config/config.yaml.example config/config.yaml

# 编辑配置文件
nano config/config.yaml
```

### 代码规范

#### Python代码规范
- 遵循PEP 8规范
- 使用类型注解
- 添加适当的注释
- 编写单元测试

#### 提交规范
```bash
# 代码格式化
black src/
isort src/

# 代码检查
flake8 src/
mypy src/

# 运行测试
pytest tests/ -v
```

### 添加新功能

#### 1. 创建新模块
```bash
# 在src/core/tools/下创建新文件
touch src/core/tools/new_feature.py
```

#### 2. 实现功能
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新功能模块

Author: Your Name
Created: 2025-01-01
Version: v1.0
License: MIT
"""

class NewFeature:
    def __init__(self, config=None):
        self.config = config or {}
    
    def process(self, input_data):
        # 实现功能逻辑
        pass
```

#### 3. 添加API端点
```python
@app.route('/api/new-feature', methods=['POST'])
def new_feature():
    try:
        data = request.get_json()
        result = new_feature_processor.process(data)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

#### 4. 编写测试
```python
def test_new_feature():
    # 准备测试数据
    test_data = {...}
    
    # 调用功能
    result = new_feature_processor.process(test_data)
    
    # 验证结果
    assert result['success'] == True
```

---

## 📞 技术支持

### 获取帮助

#### 1. 查看文档
- 用户指南：`docs/UserGuide.md`
- 开发者指南：`docs/DeveloperGuide.md`
- API参考：`docs/APIReference.md`

#### 2. 运行诊断
```bash
# 系统状态检查
python tools/project_status_checker.py

# 质量检查
python tools/automated_quality_check.py
```

#### 3. 查看日志
```bash
# 应用日志
tail -f logs/app.log

# 错误日志
tail -f logs/error.log
```

### 报告问题

#### 问题报告模板
```
**问题描述**：
[详细描述遇到的问题]

**重现步骤**：
1. [步骤1]
2. [步骤2]
3. [步骤3]

**预期结果**：
[描述期望的结果]

**实际结果**：
[描述实际发生的结果]

**环境信息**：
- 操作系统：
- Python版本：
- 项目版本：
- 错误日志：
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🎉 致谢

感谢所有为项目做出贡献的开发者和用户！

---

**AI_Pytest7 智能文档助手** - 让文档处理更智能，让工作效率更高效！ ��

*最后更新：2025年1月28日* 