# 办公文档智能代理

一个基于多种AI大语言模型的智能文档处理系统，支持文档分析、内容填充、样式生成、虚拟审阅等功能。

## ⚠️ 重要项目须知

### 🔴 开发者必读

**每次开始工作前，必须完成以下步骤：**

1. **📖 阅读项目规范**:
   - 详细阅读 [`docs/项目开发规范.md`](docs/项目开发规范.md)
   - 了解代码规范、文档规范、工作流程规范

2. **🔍 项目状态检测**:

   ```bash
   python tools/project_status_checker.py
   ```

3. **🤖 AI协作规范**:
   - AI必须基于项目规范文档完成工作
   - 每次AI对话不超过20轮，避免上下文幻觉
   - 重要对话需要AI自己凝练上下文便于迁移

4. **📝 工作流程**:
   - 文档先行 → 状态检测 → 设计方案 → 代码实现 → 测试验证 → Git提交

### 🎯 AI工作要求

- **署名标记**: 所有AI生成代码必须包含署名信息
- **增量检测**: 基于时间戳进行变更检测
- **测试验证**: 工作完成后必须全面测试
- **规范遵守**: 严格按照项目开发规范执行

### 📋 快速检查清单

- [ ] 已阅读项目开发规范
- [ ] 已运行项目状态检测
- [ ] 了解当前项目状态
- [ ] 明确工作目标和范围
- [ ] 准备好测试验证方案

## 🌟 特性

- **多API支持**: 支持讯飞星火、七牛云、Together.ai、OpenRouter等多种AI服务
- **智能文档处理**: 自动分析文档内容、结构和场景
- **专业工具集**: 内容填充、样式生成、虚拟审阅、会议回顾等
- **Web界面**: 现代化的用户界面，支持拖拽上传
- **离线模式**: 支持模拟模式，无需API密钥即可体验

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd office-doc-agent

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

复制配置文件并填入您的API密钥：

```bash
cp config.env.example .env
```

编辑 `.env` 文件，配置您需要的API服务：

```env
# 讯飞星火API (必需)
XINGCHENG_API_KEY=your_xingcheng_api_key_here
XINGCHENG_API_SECRET=your_xingcheng_api_secret_here

# 七牛云 DeepSeek API (可选)
QINIU_API_KEY=your_qiniu_api_key_here

# Together.ai API (可选)
TOGETHER_API_KEY=your_together_api_key_here

# OpenRouter API (可选)
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 3. 启动应用

```bash
# 使用批处理脚本 (Windows)
start_web.bat

# 或直接运行
python src/web_app.py
```

访问 http://localhost:5000 开始使用。

## 📋 支持的API服务

### 1. 讯飞星火 (Xingcheng)
- **模型**: x1, x2, x3
- **特点**: 国内领先的大语言模型，中文处理能力强
- **配置**: 需要API Key和Secret

### 2. 七牛云 DeepSeek
- **模型**: deepseek-v3
- **特点**: 高性能中文大模型
- **配置**: 需要API Key

### 3. Together.ai
- **模型**: Mixtral-8x7B, Llama-2-70b-chat等
- **特点**: 开源模型托管服务
- **配置**: 需要API Key

### 4. OpenRouter
- **模型**: 多种开源模型
- **特点**: 统一的API接口访问多种模型
- **配置**: 需要API Key

### 5. 多API自动选择
- **功能**: 自动在可用API中选择最佳服务
- **特点**: 高可用性，自动故障转移

## 🛠️ 核心功能

### 文档分析
- 自动识别文档类型和场景
- 分析文档结构和关键信息
- 生成优化建议

### 内容填充
- 智能补充缺失内容
- 基于上下文生成相关内容
- 保持文档逻辑一致性

### 样式生成
- 生成专业样式模板
- 统一文档格式
- 提升文档美观度

### 虚拟审阅
- 模拟专业审阅流程
- 发现潜在问题
- 提供修改建议

### 会议回顾
- 处理会议相关文档
- 生成会议纪要
- 提取关键决策点

### 文档输出
- 支持多种格式导出
- 保持格式一致性
- 批量处理能力

## 📁 项目结构

```
office-doc-agent/
├── src/
│   ├── core/
│   │   ├── agent/           # 代理编排器
│   │   ├── guidance/        # 智能引导
│   │   ├── knowledge_base/  # 知识库
│   │   └── tools/          # 核心工具
│   ├── llm_clients/        # LLM客户端
│   │   ├── base_llm.py     # 基础LLM接口
│   │   ├── xingcheng_llm.py # 讯飞星火客户端
│   │   └── multi_llm.py    # 多API客户端
│   ├── utils/              # 工具函数
│   └── web_app.py          # Web应用
├── templates/              # HTML模板
├── static/                 # 静态资源
├── uploads/               # 上传文件目录
├── output/                # 输出文件目录
├── config.env.example     # 配置示例
├── requirements.txt       # 依赖列表
└── README.md             # 项目说明
```

## 🔧 API接口

### 文档上传处理
```http
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- file: 文档文件
- api_type: API类型 (xingcheng|multi|mock)
- model_name: 模型名称
```

### 健康检查
```http
GET /api/health
```

### 配置信息
```http
GET /api/config
```

### 可用模型
```http
GET /api/models
```

## 🎯 使用场景

1. **企业文档处理**: 批量处理公司文档，提升工作效率
2. **学术论文**: 智能分析论文结构，生成摘要和建议
3. **会议记录**: 自动生成会议纪要，提取关键信息
4. **报告生成**: 智能填充报告内容，生成专业格式
5. **内容审核**: 虚拟审阅，发现潜在问题

## 🔒 安全说明

- API密钥存储在本地 `.env` 文件中，不会上传到服务器
- 上传的文件在处理完成后自动删除
- 支持HTTPS部署，确保数据传输安全

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。

## 📄 许可证

MIT License

## 📞 支持

如有问题，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 使用前请确保您有相应API服务的有效密钥，并遵守各服务的使用条款。 