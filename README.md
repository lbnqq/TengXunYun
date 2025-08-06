# aiDoc 智能文档处理系统

<div align="center">

![aiDoc Logo](static/favicon.ico)

**一个基于AI的智能文档处理系统，提供格式对齐、文风统一、智能填报和文档审查功能**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourusername/aiDoc.svg)](https://github.com/yourusername/aiDoc/stargazers)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [使用指南](#-使用指南) • [API文档](#-api文档) • [贡献指南](#-贡献指南)

</div>

## 🎯 项目简介

aiDoc 是一个智能文档处理系统，集成了讯飞星火X1大模型，为用户提供四大核心功能：

- **📄 格式对齐**：将不同格式的文档统一为标准格式
- **✍️ 文风统一**：让文档保持一致的写作风格  
- **📝 智能填报**：自动生成年度总结和个人简历
- **🔍 文档审查**：检查文档质量并提供改进建议

## ✨ 功能特性

### 🔧 核心功能
- **多格式支持**：支持 Word、PDF、TXT 等多种文档格式
- **AI驱动**：基于讯飞星火X1大模型的智能处理
- **实时处理**：快速响应，处理时间通常在30秒-2分钟内
- **用户友好**：简洁直观的Web界面，操作简单

### 🎨 界面特色
- **响应式设计**：支持桌面端和移动端
- **模块化布局**：四个功能模块独立运行
- **进度提示**：实时显示处理进度和状态
- **错误处理**：友好的中文错误提示

### 🔒 安全特性
- **数据保护**：用户上传文件不会被永久存储
- **超时控制**：防止长时间占用系统资源
- **输入验证**：严格的文件格式和大小限制
- **错误恢复**：完善的异常处理机制

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 现代浏览器（Chrome、Firefox、Edge等）
- 网络连接（调用AI服务需要）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/aiDoc.git
cd aiDoc
```

2. **创建虚拟环境**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置API密钥**
```bash
# 复制配置模板
cp config/spark_x1_keys.template.yaml config/spark_x1_keys.yaml
# 编辑配置文件，填入您的星火X1 API密钥
```

5. **启动应用**
```bash
python src/web_app.py
```

6. **访问应用**
打开浏览器访问：http://localhost:5000

## 📖 使用指南

### 格式对齐模块
1. 上传需要处理的文档
2. 选择目标格式模板
3. 点击"开始对齐"
4. 下载处理后的文档

### 文风统一模块
**预设风格模式**：
1. 选择目标风格（正式、友好、学术、商务）
2. 输入要处理的文本
3. 点击"开始处理"

**Few-Shot学习模式**：
1. 上传参考文档（风格样本）
2. 输入要处理的文本
3. 点击"开始处理"

### 智能填报模块
1. 选择文档类型（年度总结/个人简历）
2. 填写相关信息
3. 点击"开始生成"
4. 编辑和下载结果

### 文档审查模块
1. 选择审查模式（预设模板/自定义）
2. 输入要审查的文档内容
3. 点击"开始审查"
4. 查看详细的审查报告

## 🏗️ 项目结构

```
aiDoc/
├── src/                    # 后端源代码
│   ├── web_app.py         # Flask主应用
│   ├── core/              # 核心业务模块
│   └── llm_clients/       # AI客户端
├── templates/             # HTML模板
├── static/               # 静态资源
│   ├── css/              # 样式文件
│   └── js/               # JavaScript文件
├── config/               # 配置文件
├── examples/             # 示例和模板
├── docs/                 # 项目文档
├── 设计方案/              # 设计文档
└── requirements.txt      # Python依赖
```

## 📚 API文档

详细的API文档请参考：[docs/APIReference.md](docs/APIReference.md)

### 主要API端点
- `POST /api/format-alignment/process` - 格式对齐处理
- `POST /api/style-alignment/few-shot-transfer` - Few-Shot风格转换
- `POST /api/style-alignment/generate-with-style` - 预设风格生成
- `POST /api/document-review/analyze` - 文档审查分析

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发指南
- 遵循 PEP 8 代码规范
- 添加适当的注释和文档
- 确保所有测试通过
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [讯飞星火](https://xinghuo.xfyun.cn/) - 提供强大的AI能力
- [Flask](https://flask.palletsprojects.com/) - Web框架
- 所有贡献者和用户的支持

## 📞 联系我们

- 项目主页：https://github.com/yourusername/aiDoc
- 问题反馈：https://github.com/yourusername/aiDoc/issues
- 邮箱：your.email@example.com

---

<div align="center">

**如果这个项目对您有帮助，请给我们一个 ⭐ Star！**

Made with ❤️ by [Your Name](https://github.com/yourusername)

</div>
