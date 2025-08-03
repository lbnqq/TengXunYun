# 智能文档助手 - 文档索引

## 📚 核心文档

### 🎯 用户文档
- **[README.md](README.md)** - 项目概览和快速开始
- **[使用指南 (USAGE_GUIDE.md)](USAGE_GUIDE.md)** - 详细的功能使用说明
- **[项目结构 (PROJECT_STRUCTURE.md)](PROJECT_STRUCTURE.md)** - 项目架构和目录结构

### 🔧 技术文档
- **[星火X1密钥管理 (SPARK_X1_KEY_MANAGEMENT.md)](SPARK_X1_KEY_MANAGEMENT.md)** - API密钥统一管理系统
- **[项目状态 (PROJECT_STATUS.md)](PROJECT_STATUS.md)** - 当前开发状态和功能完成情况

### 📖 详细文档 (docs目录)
- **[用户指南 (docs/UserGuide.md)](../docs/UserGuide.md)** - 完整的用户操作指南
- **[开发者指南 (docs/DeveloperGuide.md)](../docs/DeveloperGuide.md)** - 开发环境配置和代码规范
- **[API参考 (docs/APIReference.md)](../docs/APIReference.md)** - 完整的API接口文档
- **[AI编程实践手册 (docs/AI编程项目终极实践手册.md)](../docs/AI编程项目终极实践手册.md)** - 项目开发规范

## 🚀 快速导航

### 新用户开始
1. 阅读 [README.md](README.md) 了解项目概览
2. 按照安装步骤配置环境和API密钥
3. 参考 [使用指南](USAGE_GUIDE.md) 学习各模块功能
4. 查看 [项目结构](PROJECT_STRUCTURE.md) 了解代码组织

### 开发者
1. 阅读 [开发者指南](../docs/DeveloperGuide.md) 配置开发环境
2. 查看 [API参考](../docs/APIReference.md) 了解接口设计
3. 参考 [AI编程实践手册](../docs/AI编程项目终极实践手册.md) 遵循开发规范
4. 使用 [密钥管理工具](SPARK_X1_KEY_MANAGEMENT.md) 管理API密钥

### 系统管理员
1. 配置 [星火X1密钥](SPARK_X1_KEY_MANAGEMENT.md)
2. 查看 [项目状态](PROJECT_STATUS.md) 了解系统状态
3. 使用 `tools/manage_spark_x1_keys.py` 管理密钥
4. 运行 `cliTests/run_all_tests.py` 进行系统测试

## 🔍 功能模块文档

### 格式对齐模块
- **核心文件**: `src/core/tools/format_alignment_coordinator.py`
- **功能**: 智能文档格式统一
- **使用**: 参考 [使用指南 - 格式对齐](USAGE_GUIDE.md#格式对齐模块使用)

### 文风统一模块
- **核心文件**: `src/core/tools/style_alignment_coordinator.py`
- **功能**: 文档风格转换和统一
- **使用**: 参考 [使用指南 - 文风统一](USAGE_GUIDE.md#文风统一模块使用)

### 智能填报模块
- **核心文件**: `src/core/tools/simple_smart_fill_manager.py`
- **功能**: 自动生成简历、总结等文档
- **使用**: 参考 [使用指南 - 智能填报](USAGE_GUIDE.md#智能填报模块使用)

### 文档审查模块
- **核心文件**: `src/core/document_review_coordinator.py`
- **功能**: 多角色专业文档审查
- **使用**: 参考 [使用指南 - 文档审查](USAGE_GUIDE.md#文档审查模块使用)

## 🛠️ 工具和配置

### 配置文件
- **`config/spark_x1_keys.yaml`** - 星火X1 API密钥配置
- **`config/spark_x1_keys.template.yaml`** - 密钥配置模板
- **`config/config.yaml`** - 主配置文件

### 管理工具
- **`tools/manage_spark_x1_keys.py`** - 密钥管理命令行工具
- **`run_app.py`** - 应用启动脚本
- **`cliTests/run_all_tests.py`** - 测试套件

### 启动脚本
- **`start.bat`** - Windows启动脚本
- **`start.sh`** - Linux/Mac启动脚本

## 📋 测试文档

### CLI测试套件 (cliTests目录)
- **[测试说明 (cliTests/README.md)](../cliTests/README.md)** - 测试套件使用说明
- **[使用指南 (cliTests/USAGE.md)](../cliTests/USAGE.md)** - 测试执行指南
- **`run_all_tests.py`** - 运行所有测试
- **`test_*.py`** - 各模块功能测试

### 测试执行
```bash
cd cliTests
python run_all_tests.py
```

## 🔧 故障排除

### 常见问题
1. **API密钥配置问题** - 参考 [密钥管理文档](SPARK_X1_KEY_MANAGEMENT.md)
2. **模块初始化失败** - 检查依赖安装和Python版本
3. **文件上传问题** - 确认文件格式和大小限制
4. **导出功能异常** - 检查文件权限和磁盘空间

### 调试工具
```bash
# 检查密钥配置
python tools/manage_spark_x1_keys.py --list

# 测试密钥有效性
python tools/manage_spark_x1_keys.py --test

# 运行系统测试
cd cliTests && python run_all_tests.py
```

## 📞 支持信息

### 技术支持
- 查看控制台输出的错误信息
- 参考相关文档的故障排除部分
- 检查 [项目状态文档](PROJECT_STATUS.md) 了解已知问题

### 开发支持
- 遵循 [AI编程实践手册](../docs/AI编程项目终极实践手册.md) 的开发规范
- 使用项目提供的开发工具进行代码质量检查
- 参考 [API文档](../docs/APIReference.md) 进行接口开发

---

**注意**: 本文档索引会随着项目发展持续更新，请定期查看最新版本。
