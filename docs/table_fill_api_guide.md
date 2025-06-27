# 表格填充API使用指南

## 概述

表格填充API (`/api/table-fill`) 提供智能表格批量填充功能，支持将结构化数据填充到表格中。本文档详细说明了API的使用方法、参数格式和最佳实践。

## API端点

```
POST /api/table-fill
Content-Type: application/json
```

## 请求格式

### 基本结构

```json
{
  "tables": [
    {
      "columns": ["列名1", "列名2", "列名3"],
      "data": [
        ["行1列1", "行1列2", "行1列3"],
        ["行2列1", "行2列2", "行2列3"]
      ]
    }
  ],
  "fill_data": [
    {"列名1": "填充值1", "列名2": "填充值2"},
    {"列名1": "填充值3", "列名2": "填充值4"}
  ]
}
```

### 参数说明

#### `tables` (必需)
- **类型**: `Array<Object>`
- **描述**: 要填充的表格数组，每个表格包含列定义和数据

**表格对象结构**:
- `columns` (必需): `Array<String>` - 表格列名数组
- `data` (必需): `Array<Array>` - 表格数据二维数组

#### `fill_data` (必需)
- **类型**: `Array<Object>`
- **描述**: 填充数据数组，每个对象代表一行数据
- **格式**: 键为列名，值为对应的填充内容

## 响应格式

### 成功响应

```json
{
  "success": true,
  "filled_tables": [
    {
      "columns": ["列名1", "列名2", "列名3"],
      "data": [
        ["填充后值1", "填充后值2", "填充后值3"],
        ["填充后值4", "填充后值5", "填充后值6"]
      ]
    }
  ]
}
```

### 错误响应

```json
{
  "success": false,
  "error": "错误描述信息"
}
```

## 使用示例

### 示例1: 基本表格填充

**请求**:
```json
{
  "tables": [
    {
      "columns": ["姓名", "年龄", "职位"],
      "data": [
        ["张三", "", ""],
        ["李四", "", ""]
      ]
    }
  ],
  "fill_data": [
    {"姓名": "张三", "年龄": "25", "职位": "工程师"},
    {"姓名": "李四", "年龄": "30", "职位": "经理"}
  ]
}
```

**响应**:
```json
{
  "success": true,
  "filled_tables": [
    {
      "columns": ["姓名", "年龄", "职位"],
      "data": [
        ["张三", "25", "工程师"],
        ["李四", "30", "经理"]
      ]
    }
  ]
}
```

### 示例2: 多表格填充

**请求**:
```json
{
  "tables": [
    {
      "columns": ["产品名称", "价格"],
      "data": [["笔记本", ""], ["鼠标", ""]]
    },
    {
      "columns": ["员工", "部门"],
      "data": [["", "技术部"], ["", "市场部"]]
    }
  ],
  "fill_data": [
    {"产品名称": "笔记本", "价格": "5000", "员工": "张三", "部门": "技术部"},
    {"产品名称": "鼠标", "价格": "100", "员工": "李四", "部门": "市场部"}
  ]
}
```

### 示例3: 部分填充

```json
{
  "tables": [
    {
      "columns": ["项目", "状态", "负责人"],
      "data": [
        ["项目A", "进行中", ""],
        ["项目B", "", "李四"]
      ]
    }
  ],
  "fill_data": [
    {"项目": "项目A", "负责人": "张三"},
    {"项目": "项目B", "状态": "已完成"}
  ]
}
```

## 前端集成示例

### JavaScript/Fetch

```javascript
async function fillTables(tables, fillData) {
  try {
    const response = await fetch('/api/table-fill', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tables: tables,
        fill_data: fillData
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('填充成功:', result.filled_tables);
      return result.filled_tables;
    } else {
      console.error('填充失败:', result.error);
      throw new Error(result.error);
    }
  } catch (error) {
    console.error('API调用失败:', error);
    throw error;
  }
}

// 使用示例
const tables = [
  {
    columns: ['姓名', '年龄', '职位'],
    data: [['张三', '', ''], ['李四', '', '']]
  }
];

const fillData = [
  {姓名: '张三', 年龄: '25', 职位: '工程师'},
  {姓名: '李四', 年龄: '30', 职位: '经理'}
];

fillTables(tables, fillData)
  .then(filledTables => {
    // 处理填充后的表格
    console.log(filledTables);
  })
  .catch(error => {
    // 处理错误
    console.error(error);
  });
```

### jQuery

```javascript
function fillTablesWithJQuery(tables, fillData) {
  return $.ajax({
    url: '/api/table-fill',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
      tables: tables,
      fill_data: fillData
    })
  }).done(function(result) {
    if (result.success) {
      console.log('填充成功:', result.filled_tables);
      return result.filled_tables;
    } else {
      console.error('填充失败:', result.error);
      throw new Error(result.error);
    }
  }).fail(function(xhr, status, error) {
    console.error('API调用失败:', error);
    throw error;
  });
}
```

## 数据类型支持

API支持以下数据类型：

- **字符串**: `"文本内容"`
- **数字**: `42`, `3.14`
- **布尔值**: `true`, `false`
- **日期**: `"2024-01-01"` (字符串格式)
- **空值**: `""`, `null`

## 最佳实践

### 1. 数据验证
在发送请求前验证数据格式：

```javascript
function validateTableData(tables, fillData) {
  // 检查tables格式
  if (!Array.isArray(tables)) {
    throw new Error('tables必须是数组');
  }
  
  tables.forEach((table, index) => {
    if (!table.columns || !Array.isArray(table.columns)) {
      throw new Error(`表格${index + 1}缺少columns字段`);
    }
    if (!table.data || !Array.isArray(table.data)) {
      throw new Error(`表格${index + 1}缺少data字段`);
    }
  });
  
  // 检查fillData格式
  if (!Array.isArray(fillData)) {
    throw new Error('fill_data必须是数组');
  }
}
```

### 2. 错误处理
实现完善的错误处理机制：

```javascript
async function robustFillTables(tables, fillData) {
  try {
    // 数据验证
    validateTableData(tables, fillData);
    
    // API调用
    const result = await fillTables(tables, fillData);
    return result;
    
  } catch (error) {
    // 记录错误
    console.error('表格填充失败:', error);
    
    // 用户友好的错误提示
    if (error.message.includes('网络')) {
      alert('网络连接失败，请检查网络后重试');
    } else if (error.message.includes('格式')) {
      alert('数据格式错误，请检查输入数据');
    } else {
      alert('填充失败，请联系技术支持');
    }
    
    throw error;
  }
}
```

### 3. 性能优化
- 对于大量数据，考虑分批处理
- 使用适当的超时设置
- 实现重试机制

## 常见问题

### Q: 如何处理空表格？
A: 空表格可以正常处理，只需确保columns和data字段存在即可：
```json
{
  "columns": [],
  "data": []
}
```

### Q: 填充数据的顺序重要吗？
A: 填充数据按数组顺序处理，建议保持与表格行的对应关系。

### Q: 如何处理列名不匹配的情况？
A: 系统会自动跳过不匹配的列名，只填充匹配的字段。

### Q: 支持的最大表格大小是多少？
A: 建议单次请求不超过1000行数据，以确保最佳性能。

## 技术支持

如有问题，请联系技术支持或查看项目文档。
