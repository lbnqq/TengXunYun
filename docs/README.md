# 项目文档目录

## 📋 文档概览

本目录包含office-doc-agent项目的所有技术文档、规范文档和历史文档。

**最后更新**: 2025年6月25日  
**维护人**: AI Assistant (Claude)  
**文档总数**: 17个文件  

## 📚 文档分类

### 🔧 开发规范和指南
- **[项目开发规范.md](项目开发规范.md)** - 统一的项目开发规范，包括代码规范、文档规范、工作流程等
- **[OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)** - 项目优化功能总结，包含LLM效率、UI改进、批量处理等
- **[项目当前状态全貌.md](项目当前状态全貌.md)** - 完整的项目状态分析报告

### 📖 业务和使用文档
- **[business_processes.md](business_processes.md)** - 业务流程文档
- **[complex_document_fill_guide.md](complex_document_fill_guide.md)** - 复杂文档填充指南
- **[use_cases.md](use_cases.md)** - 使用案例文档

### 📊 临时报告 (reports/)
- **[git_commit_commands.md](reports/git_commit_commands.md)** - Git提交指令说明
- **[文件头检查报告.md](reports/文件头检查报告.md)** - 文件头注释检查结果
- **[项目状态增量检测报告.md](reports/项目状态增量检测报告.md)** - 项目状态检测报告
- **[文档整理分析报告.md](reports/文档整理分析报告.md)** - 文档整理方案分析
- **[文档整理后状态检测.md](reports/文档整理后状态检测.md)** - 文档整理后的状态检测

### 📦 历史文档归档 (archives/)
- **[重构概要设计.md](archives/重构概要设计.md)** - 历史重构设计文档
- **[重构目标todo.md](archives/重构目标todo.md)** - 历史重构任务清单
- **[重构624.MD](archives/重构624.MD)** - 6月24日重构记录
- **[项目实现情况分析报告.md](archives/项目实现情况分析报告.md)** - 历史实现分析
- **[Web应用工程可用性增强计划.md](archives/Web应用工程可用性增强计划.md)** - 历史增强计划
- **[README_UI_UPGRADE.md](archives/README_UI_UPGRADE.md)** - 历史UI升级说明

## 🔍 文档使用指南

### 新开发者入门
1. 首先阅读 **[项目开发规范.md](项目开发规范.md)** 了解开发规范
2. 查看 **[项目当前状态全貌.md](项目当前状态全貌.md)** 了解项目现状
3. 参考 **[OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)** 了解最新优化

### 业务人员参考
1. 查看 **[business_processes.md](business_processes.md)** 了解业务流程
2. 参考 **[use_cases.md](use_cases.md)** 了解使用场景
3. 使用 **[complex_document_fill_guide.md](complex_document_fill_guide.md)** 进行复杂操作

### 项目维护者
1. 定期查看 **reports/** 目录下的状态报告
2. 参考 **archives/** 目录了解历史决策
3. 更新相关文档并维护本索引

## 📋 文档维护规范

### 文档分类规则
- **根目录**: 核心规范和状态文档
- **reports/**: 临时生成的报告和检测结果
- **archives/**: 历史文档和已完成的设计文档

### 文档命名规范
- 使用中文名称，便于理解
- 包含创建日期或版本信息
- 临时文档添加时间戳

### 文档更新流程
1. 修改文档内容
2. 更新文档的"最后更新"时间
3. 更新本索引文件
4. 提交Git变更

## 🛠️ 相关工具

### 文档检查工具
```bash
# 检查文件头注释
python tools/check_file_headers.py docs/

# 项目状态检测
python tools/project_status_checker.py --output docs/reports/状态检测.md
```

### 文档生成工具
```bash
# 生成Markdown文档模板
python tools/code_template_generator.py markdown_doc "文档名" "文档描述" --output docs/新文档.md
```

## 📈 文档统计

- **总文档数**: 17个
- **开发规范**: 3个
- **业务文档**: 3个
- **临时报告**: 5个
- **历史归档**: 6个

## 🔗 相关链接

- [项目主页](../README.md)
- [开发工具](../tools/)
- [源代码](../src/)
- [测试文件](../tests/)

---

**文档索引维护**: AI Assistant (Claude)  
**创建时间**: 2025年6月25日  
**AI辅助**: 是 - Claude 3.5 Sonnet  
**状态**: 已完成文档整理
