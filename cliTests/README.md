# CLI测试工具

本目录包含智能文档助手各业务功能的命令行测试脚本，用于验证后端API是否支持完整的业务流程。

## 测试目标

验证以下业务场景的贯通性：
1. **智能文档组装** - 格式对齐功能
2. **文风检测与统一** - 风格统一功能
3. **智能填报** - 文档模板填充功能
4. **智能审批与质量检查** - 文档评审功能
5. **表格填充** - 智能表格批量填充功能

## 文件结构

```
cliTests/
├── __init__.py                    # 包初始化文件
├── base_test_script.py           # 基础测试脚本类
├── test_format_alignment.py      # 格式对齐测试
├── test_style_alignment.py       # 文风统一测试
├── test_document_fill.py         # 智能填报测试
├── test_document_review.py       # 文档评审测试
├── test_table_fill.py            # 表格填充测试
├── run_all_tests.py              # 批量测试运行器
└── README.md                     # 本说明文档
```

## 使用方法

### 1. 单个测试

#### 格式对齐测试
```bash
python cliTests/test_format_alignment.py source.txt target.txt output.txt
```

#### 文风统一测试
```bash
python cliTests/test_style_alignment.py reference.txt target.txt output.txt
```

#### 智能填报测试
```bash
python cliTests/test_document_fill.py template.txt data.json output.txt
```

#### 文档评审测试
```bash
python cliTests/test_document_review.py document.txt output.txt --review-focus academic
```

#### 表格填充测试
```bash
python cliTests/test_table_fill.py table.json data.json output.json
```

### 2. 批量测试

运行所有业务功能测试：
```bash
python cliTests/run_all_tests.py
```

仅创建测试数据：
```bash
python cliTests/run_all_tests.py --create-data-only
```

### 3. 自定义API地址

```bash
python cliTests/run_all_tests.py --url http://your-api-server:5000
```

## 测试数据格式

### 格式对齐测试
- **source.txt**: 参考格式文档（标准格式）
- **target.txt**: 待处理文档（需要格式调整）

### 文风统一测试
- **reference.txt**: 参考风格文档（目标风格）
- **target.txt**: 待调整文档（需要风格统一）

### 智能填报测试
- **template.txt**: 文档模板（包含占位符）
- **data.json**: 填充数据（JSON格式）

### 文档评审测试
- **document.txt**: 待评审文档
- **--review-focus**: 评审重点（auto/academic/business/technical/legal）

### 表格填充测试
- **table.json**: 表格定义（包含列和数据）
- **data.json**: 填充数据（JSON格式）

## 输出文件

每个测试会生成以下文件：
- **输出文档**: 处理后的文档内容
- **测试报告**: `*_test_report.json` - 详细的测试结果
- **业务报告**: `*_report.json` - 业务处理结果

## 测试报告

### JSON报告格式
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

### HTML报告
批量测试会生成可视化的HTML报告，包含：
- 测试摘要
- 详细结果
- 错误信息
- 执行时间

## 问题诊断

### 常见问题

1. **API连接失败**
   - 检查API服务是否启动
   - 验证API地址是否正确
   - 确认网络连接正常

2. **文件读取失败**
   - 检查文件路径是否正确
   - 确认文件编码为UTF-8
   - 验证文件权限

3. **API响应错误**
   - 查看详细的错误信息
   - 检查API参数格式
   - 验证API接口实现

### 调试模式

使用 `--verbose` 参数启用详细输出：
```bash
python cliTests/test_format_alignment.py source.txt target.txt output.txt --verbose
```

## 业务贯通性验证

### 格式对齐流程
1. ✅ 读取源文档和目标文档
2. ✅ 调用格式对齐API
3. ✅ 获取对齐结果
4. ✅ 保存输出文档

### 文风统一流程
1. ✅ 分析参考文档风格
2. ✅ 应用风格到目标文档
3. ✅ 预览风格变化
4. ✅ 接受/拒绝变化
5. ✅ 导出统一风格文档

### 智能填报流程
1. ✅ 启动文档填报会话
2. ✅ 自动匹配数据到模板
3. ✅ 处理数据冲突
4. ✅ 完成文档填充
5. ✅ 导出填充结果

### 文档评审流程
1. ✅ 启动文档评审
2. ✅ 获取AI评审建议
3. ✅ 处理评审建议
4. ✅ 生成评审报告
5. ✅ 导出评审后文档

### 表格填充流程
1. ✅ 验证表格结构
2. ✅ 验证填充数据
3. ✅ 执行表格填充
4. ✅ 处理填充结果
5. ✅ 保存填充后表格

## 扩展测试

### 添加新的业务测试

1. 继承 `BaseTestScript` 类
2. 实现 `run_test` 方法
3. 定义业务流程图
4. 添加测试数据
5. 更新批量测试配置

### 自定义测试数据

修改 `run_all_tests.py` 中的 `create_test_data` 方法，添加新的测试数据生成逻辑。

## 注意事项

1. **API依赖**: 测试需要后端API服务正常运行
2. **数据格式**: 确保测试数据符合API要求
3. **超时设置**: 长时间运行的测试有5分钟超时限制
4. **错误处理**: 测试脚本包含完整的错误处理和恢复机制
5. **报告生成**: 所有测试都会生成详细的报告文件

## 贡献指南

1. 遵循现有的代码结构和命名规范
2. 添加适当的错误处理和日志记录
3. 确保测试的可重复性和稳定性
4. 更新文档和测试数据
5. 运行完整测试套件验证修改 