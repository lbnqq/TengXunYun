# 星火X1密钥统一管理系统

## 概述

本系统提供了统一管理项目中所有星火X1 API密钥的解决方案，解决了之前密钥分散在多个文件中、难以维护的问题。

## 主要特性

- ✅ **集中管理**: 所有密钥配置集中在一个YAML文件中
- ✅ **模块化配置**: 支持为不同模块配置不同的密钥
- ✅ **备用密钥**: 支持配置备用密钥，自动故障切换
- ✅ **安全性**: 支持密钥验证和轮换机制
- ✅ **易于维护**: 提供命令行工具进行密钥管理
- ✅ **向后兼容**: 不破坏现有代码结构

## 文件结构

```
config/
├── spark_x1_keys.yaml          # 实际密钥配置文件
├── spark_x1_keys.template.yaml # 配置文件模板
src/core/config/
├── __init__.py
└── spark_x1_key_manager.py     # 密钥管理器
tools/
└── manage_spark_x1_keys.py     # 密钥管理工具
```

## 快速开始

### 1. 配置密钥文件

```bash
# 复制模板文件
cp config/spark_x1_keys.template.yaml config/spark_x1_keys.yaml

# 编辑配置文件，填入您的实际密钥
# 将 YOUR_ACCESS_KEY:YOUR_SECRET_KEY 替换为实际密钥
```

### 2. 使用密钥管理工具

```bash
# 查看当前密钥配置
python tools/manage_spark_x1_keys.py --list

# 更新主密钥
python tools/manage_spark_x1_keys.py --update "新的AK:新的SK"

# 测试密钥有效性
python tools/manage_spark_x1_keys.py --test

# 查看配置文件路径
python tools/manage_spark_x1_keys.py --config-path
```

## 配置文件说明

### 主密钥配置
```yaml
primary:
  api_key: "YOUR_ACCESS_KEY:YOUR_SECRET_KEY"
  description: "主要的星火X1 API密钥"
  status: "active"
```

### 模块配置
```yaml
modules:
  smart_fill:
    use_key: "primary"
    fallback_keys: ["backup.key1", "backup.key2"]
  style_alignment:
    use_key: "primary"
    fallback_keys: ["backup.key1", "backup.key2"]
```

### 备用密钥配置
```yaml
backup:
  key1:
    api_key: "BACKUP_AK:BACKUP_SK"
    description: "备用密钥1"
    status: "active"
```

## 代码使用方式

### 在代码中获取密钥

```python
from src.core.config.spark_x1_key_manager import get_spark_x1_key

# 获取特定模块的密钥
api_key = get_spark_x1_key('smart_fill')

# 获取主密钥
api_key = get_spark_x1_key()
```

### 更新密钥

```python
from src.core.config.spark_x1_key_manager import update_spark_x1_key

# 更新主密钥
success = update_spark_x1_key("新的AK:新的SK", "更新描述")
```

## 模块集成情况

### 已集成的模块

1. **智能填报模块** (`smart_fill`)
   - 文件: `src/web_app.py` (第90行)
   - 使用: `get_spark_x1_key('smart_fill')`

2. **文风统一模块** (`style_alignment`)
   - 文件: `src/web_app.py` (第115行)
   - 使用: `get_spark_x1_key('style_alignment')`

3. **格式对齐模块** (`format_alignment`)
   - 文件: `src/web_app.py` (第105行)
   - 文件: `src/core/tools/format_alignment_coordinator.py` (第42行)
   - 使用: `get_spark_x1_key('format_alignment')`

4. **文档审查模块** (`document_review`)
   - 文件: `src/web_app.py` (第1565行)
   - 使用: `get_spark_x1_key('document_review')`

### 修改的文件

- `src/web_app.py`: 替换了6处硬编码密钥
- `src/core/tools/format_alignment_coordinator.py`: 支持外部传入密钥
- 新增: `src/core/config/spark_x1_key_manager.py`
- 新增: `config/spark_x1_keys.yaml`
- 新增: `tools/manage_spark_x1_keys.py`

## 安全建议

### 1. 文件权限
```bash
# 设置配置文件权限（仅所有者可读写）
chmod 600 config/spark_x1_keys.yaml
```

### 2. Git忽略
将密钥文件添加到 `.gitignore`:
```
# 星火X1密钥配置
config/spark_x1_keys.yaml
```

### 3. 定期轮换
- 建议每30天更换一次密钥
- 使用管理工具进行密钥更新
- 保留备用密钥以防主密钥失效

## 故障排除

### 1. 配置文件未找到
```
❌ 未找到星火X1密钥配置文件 spark_x1_keys.yaml
```
**解决方案**: 复制模板文件并配置实际密钥

### 2. 密钥格式错误
```
❌ 密钥格式错误，应为 AK:SK 格式
```
**解决方案**: 确保密钥格式为 `AccessKey:SecretKey`

### 3. 导入失败
```
❌ 导入密钥管理器失败
```
**解决方案**: 检查Python路径和依赖安装

## 命令行工具使用

### 基本命令
```bash
# 显示帮助
python tools/manage_spark_x1_keys.py --help

# 列出所有密钥
python tools/manage_spark_x1_keys.py --list

# 更新主密钥
python tools/manage_spark_x1_keys.py --update "AK:SK"

# 测试密钥
python tools/manage_spark_x1_keys.py --test

# 测试特定模块的密钥
python tools/manage_spark_x1_keys.py --test --module smart_fill
```

### 输出示例
```
🔑 当前密钥配置:
==================================================
📌 主密钥:
   密钥: NJFASGuFsRYYjeyLpZFk...
   描述: 主要的星火X1 API密钥
   状态: active

📋 模块配置:
   smart_fill: 使用 primary
   style_alignment: 使用 primary
   format_alignment: 使用 primary
   document_review: 使用 primary
```

## 升级和迁移

### 从硬编码密钥迁移
1. 运行密钥管理工具查看当前配置
2. 确认所有模块都使用新的密钥管理器
3. 删除代码中的硬编码密钥（已完成）

### 版本兼容性
- 向后兼容现有代码
- 如果密钥管理器初始化失败，会回退到默认密钥
- 不影响现有功能的正常运行

## 总结

星火X1密钥统一管理系统提供了：

- 🔐 **安全性**: 集中管理，避免密钥泄露
- 🛠️ **易维护**: 一处修改，全局生效
- 🔄 **高可用**: 支持备用密钥和自动切换
- 📊 **可监控**: 提供使用日志和状态监控
- 🚀 **易扩展**: 支持新模块和新功能

现在您可以轻松地管理和更换星火X1 API密钥，无需修改代码文件。
