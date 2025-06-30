# 后端接口开发文档 (2025年6月26日)

## 📋 文档概述

本文档旨在系统梳理 Office-Doc-Agent 项目中已实现的所有后端API接口，为开发人员、测试人员及相关团队成员提供清晰的接口参考。本文档基于项目代码库中的实际实现，涵盖了API端点的功能、请求方法、路径、参数及主要用途，旨在方便接口调用、测试验证及后续维护工作。

本接口文档按照功能模块对API进行分类整理，包括文档处理、写作风格分析、数据库操作、性能监控、批量处理等主要模块。每个模块下详细列出相关API端点，并提供简要描述以帮助理解其作用。文档内容基于2025年6月26日的代码状态生成，未来如有接口变更，将更新相应版本。

**重要说明**：本文档同时包含后端接口定义和前端调用示例，确保前后端开发的一致性。

## 📅 文档信息

本接口文档的生成时间为2025年6月26日，基于项目代码库中截至该日期的最新实现。API信息通过对`src/web_app.py`及相关文件的分析提取，确保内容的准确性和完整性。本文档遵循《AI编程项目终极实践手册.md》中对技术文档结构和内容的要求，旨在为项目团队提供可靠的参考资料。

在梳理API接口的过程中，共识别出45个端点，覆盖了从基本健康检查到复杂文档处理的全方位功能。以下章节将按功能模块逐一展开详细说明，以便于开发人员快速定位所需接口。

## 🧠 智能意图识别API说明

系统支持用户上传文档后，自动分析文档内容和结构，智能识别用户意图（如：空表格/模板、内容完整、格式混乱、AIGC痕迹等），并在置信度高时自动推荐或引导用户进入最合适的下一步操作。该能力由`/api/document-fill/start`等接口自动触发，返回结构中包含推荐的处理类型、置信度、建议的下一步操作等信息。

## 🏗️ API分类与详细说明

API接口按照功能模块进行分类，以便于理解和使用。每个模块包含若干相关端点，涵盖了从基本页面访问到复杂业务逻辑处理的不同场景。以下是各模块的详细描述及接口清单。

### 页面访问接口

页面访问接口主要用于前端页面的渲染和访问，属于基础路由功能。这些接口通常不涉及复杂业务逻辑，主要负责页面内容的返回。

- **GET /**  
  功能：返回主页面内容，通常是项目的入口页面。  
  描述：这是用户访问应用时的默认页面，可能包含基本的导航和功能介绍。

- **GET /demo**  
  功能：返回演示页面。  
  描述：用于展示项目的基本功能或提供演示内容，适合新用户了解应用特性。

- **GET /dashboard**  
  功能：返回仪表盘页面。  
  描述：仪表盘页面通常用于展示项目运行状态、统计数据或关键指标。

- **GET /batch**  
  功能：返回批量处理页面。  
  描述：提供批量任务创建和管理的前端界面。

- **GET /debug_frontend.html**  
  功能：返回调试前端页面。  
  描述：用于开发和调试前端功能，可能包含测试工具或调试信息。

- **GET /test_ai_features.html**  
  功能：返回AI功能测试页面。  
  描述：专门用于测试AI相关功能的页面，可能包含交互式测试工具。

- **GET /examples/<filename>**  
  功能：下载示例文件。  
  描述：根据提供的文件名返回对应的示例文件，适用于用户获取模板或参考资料。

### 健康检查与配置接口

健康检查与配置接口用于监控应用状态和获取配置信息，确保系统正常运行。这些接口通常用于运维和调试。

- **GET /api/health**  
  功能：返回应用健康状态。  
  描述：用于检查应用是否正常运行，通常返回简单的状态信息。
  
  **前端调用示例**：
  ```javascript
  async function checkHealth() {
      try {
          const response = await fetch('/api/health');
          const result = await response.json();
          console.log('应用状态:', result);
          return result;
      } catch (error) {
          console.error('健康检查失败:', error);
          return null;
      }
  }
  ```

- **GET /api/performance/health**  
  功能：获取API健康状态（第一阶段新增）。  
  描述：返回系统各组件的详细健康状态，包括LLM客户端、数据库、文件系统、缓存系统、模板系统等。
  
  **响应格式**：
  ```json
  {
    "success": true,
    "data": {
      "endpoints": [],
      "overall_health": "healthy",
      "last_check": "2025-06-28T17:54:44.761579",
      "llm_client": {"status": "healthy"},
      "database": {"status": "healthy"},
      "file_system": {"status": "healthy"},
      "cache_system": {"status": "healthy"},
      "template_system": {"status": "healthy"}
    }
  }
  ```
  
  **前端调用示例**：
  ```javascript
  async function getApiHealth() {
      try {
          const response = await fetch('/api/performance/health');
          const result = await response.json();
          
          if (result.success) {
              const health = result.data;
              console.log('整体健康状态:', health.overall_health);
              console.log('数据库状态:', health.database.status);
              console.log('文件系统状态:', health.file_system.status);
              return health;
          } else {
              throw new Error(result.error || '健康检查失败');
          }
      } catch (error) {
          console.error('API健康检查失败:', error);
          return null;
      }
  }
  ```

- **GET /api/config**  
  功能：获取应用配置信息。  
  描述：返回当前应用的配置参数，可能包括功能开关或环境变量。
  
  **前端调用示例**：
  ```javascript
  async function getConfig() {
      try {
          const response = await fetch('/api/config');
          const config = await response.json();
          console.log('应用配置:', config);
          return config;
      } catch (error) {
          console.error('获取配置失败:', error);
          return null;
      }
  }
  ```

- **GET /api/models**  
  功能：获取可用模型列表。  
  描述：返回应用支持的AI模型或处理模型列表，供用户选择或配置。
  
  **前端调用示例**：
  ```javascript
  async function getAvailableModels() {
      try {
          const response = await fetch('/api/models');
          const models = await response.json();
          console.log('可用模型:', models);
          return models;
      } catch (error) {
          console.error('获取模型列表失败:', error);
          return [];
      }
  }
  ```

### 文档处理接口

文档处理接口是应用的核心功能模块，涵盖了文档上传、格式对齐、模板应用及文档填写等功能。这些接口支持复杂的业务逻辑处理。

- **POST /api/upload**  
  功能：上传文件。  
  描述：接收用户上传的文档文件，并进行初步处理或存储。上传后系统会自动分析文档内容和结构，判定用户意图（如智能填报、格式整理、内容补全、风格改写等），并在置信度高时自动推荐下一步操作。
  
  **前端调用示例**：
  ```javascript
  async function uploadFile(file) {
      try {
          showLoading('正在上传文件...');
          
          const formData = new FormData();
          formData.append('file', file);
          
          const response = await fetch('/api/upload', {
              method: 'POST',
              body: formData
          });
          
          if (!response.ok) {
              throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          
          const result = await response.json();
          
          if (result.success) {
              showMessage('文件上传成功！', 'success');
              return result;
          } else {
              throw new Error(result.error || '上传失败');
          }
          
      } catch (error) {
          showMessage(`上传失败: ${error.message}`, 'error');
          return null;
      } finally {
          hideLoading();
      }
  }
  ```

- **POST /api/format-alignment**  
  功能：执行格式对齐操作。  
  描述：根据指定规则或模板对上传的文档进行格式调整。

- **GET /api/format-templates**  
  功能：列出所有格式模板。  
  描述：返回可用的格式模板列表，供用户选择。

- **GET /api/format-templates/<template_id>**  
  功能：获取指定格式模板的详细信息。  
  描述：根据模板ID返回该模板的具体内容和配置。

- **POST /api/format-templates/<template_id>/apply**  
  功能：应用指定格式模板到文档。  
  描述：将选定的模板应用到目标文档上，执行格式化操作。

- **GET /api/templates/<template_id>**  
  功能：获取模板详细信息（第一阶段新增）。  
  描述：根据模板ID获取模板的详细信息，包括模板内容、格式规则、创建时间等。
  
  **响应格式**：
  ```json
  {
    "success": true,
    "template": {
      "template_id": "template_12345678_abcd1234",
      "template_name": "标准报告模板",
      "format_rules": {...},
      "created_at": "2025-06-28T17:54:44.761579",
      "updated_at": "2025-06-28T17:54:44.761579"
    }
  }
  ```
  
  **前端调用示例**：
  ```javascript
  async function getTemplateDetails(templateId) {
      try {
          const response = await fetch(`/api/templates/${templateId}`);
          const result = await response.json();
          
          if (result.success) {
              console.log('模板详情:', result.template);
              return result.template;
          } else {
              throw new Error(result.error || '获取模板失败');
          }
      } catch (error) {
          console.error('获取模板详情失败:', error);
          return null;
      }
  }
  ```

- **POST /api/templates/<template_id>/apply**  
  功能：应用模板到文档内容（第一阶段新增）。  
  描述：将指定模板应用到文档内容，返回格式化后的结果。
  
  **请求格式**：
  ```json
  {
    "content": "原始文档内容",
    "options": {
      "preserve_formatting": true,
      "apply_styles": true
    }
  }
  ```
  
  **响应格式**：
  ```json
  {
    "success": true,
    "result": {
      "formatted_content": "格式化后的内容",
      "applied_rules": ["规则1", "规则2"],
      "processing_time": 0.5
    }
  }
  ```
  
  **前端调用示例**：
  ```javascript
  async function applyTemplate(templateId, content, options = {}) {
      try {
          const response = await fetch(`/api/templates/${templateId}/apply`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  content: content,
                  options: options
              })
          });
          
          const result = await response.json();
          
          if (result.success) {
              console.log('模板应用成功:', result.result);
              return result.result;
          } else {
              throw new Error(result.error || '应用模板失败');
          }
      } catch (error) {
          console.error('应用模板失败:', error);
          return null;
      }
  }
  ```

- **DELETE /api/templates/<template_id>/delete**  
  功能：删除指定模板（第一阶段新增）。  
  描述：根据模板ID删除指定的模板文件和相关索引。
  
  **响应格式**：
  ```json
  {
    "success": true,
    "message": "模板删除成功",
    "deleted_template_id": "template_12345678_abcd1234"
  }
  ```
  
  **前端调用示例**：
  ```javascript
  async function deleteTemplate(templateId) {
      try {
          const response = await fetch(`/api/templates/${templateId}/delete`, {
              method: 'DELETE'
          });
          
          const result = await response.json();
          
          if (result.success) {
              console.log('模板删除成功:', result.message);
              return true;
          } else {
              throw new Error(result.error || '删除模板失败');
          }
      } catch (error) {
          console.error('删除模板失败:', error);
          return false;
      }
  }
  ```

- **GET /api/format-alignment/preview/<session_id>**  
  功能：预览格式化后的文档。  
  描述：根据会话ID返回格式化后的文档预览内容。

- **POST /api/document-fill/start**  
  功能：启动文档填写流程。  
  描述：初始化文档填写任务，自动分析文档类型、内容完整性、格式规范性等，返回结构中包含：
    - `detected_intent`：系统判定的用户意图类型
    - `confidence`：置信度分数
    - `recommended_action`：建议的下一步操作
    - `need_user_confirmation`：是否需要用户确认
  若置信度高，系统会自动引导用户进入推荐流程。
  
  **前端调用示例**：
  ```javascript
  async function startDocumentFill(documentContent, documentName) {
      try {
          showLoading('正在分析文档结构...');
          
          const response = await fetch('/api/document-fill/start', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  document_content: documentContent,
                  document_name: documentName
              })
          });
          
          const result = await response.json();
          
          if (result.error) {
              throw new Error(result.error);
          }
          
          // result.response: 首轮AI提问
          // result.current_question: 当前问题编号
          // result.total_questions: 总问题数
          
          return result;
          
      } catch (error) {
          showMessage(`文档分析失败: ${error.message}`, 'error');
          return null;
      } finally {
          hideLoading();
      }
  }
  ```

- **POST /api/document-fill/respond**  
  功能：响应文档填写过程中的问题。  
  描述：接收用户对填写问题的回答，并更新填写状态。
  
  **前端调用示例**：
  ```javascript
  async function respondToQuestion(userInput) {
      try {
          showLoading('AI正在思考...');
          
          const response = await fetch('/api/document-fill/respond', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  user_input: userInput
              })
          });
          
          const result = await response.json();
          
          if (result.error) {
              throw new Error(result.error);
          }
          
          // result.response: AI回复
          // result.current_question: 当前问题编号
          // result.total_questions: 总问题数
          // result.stage: 'completed' 表示填写完成
          
          if (result.stage === 'completed') {
              showMessage('文档填写完成！', 'success');
          }
          
          return result;
          
      } catch (error) {
          showMessage(`回复失败: ${error.message}`, 'error');
          return null;
      } finally {
          hideLoading();
      }
  }
  ```

- **GET /api/document-fill/status**  
  功能：获取文档填写任务的状态。  
  描述：返回当前填写任务的进度或状态信息。

- **GET /api/document-fill/result**  
  功能：获取文档填写结果。  
  描述：返回填写完成的文档内容或相关信息。
  
  **前端调用示例**：
  ```javascript
  async function getFillResult() {
      try {
          const response = await fetch('/api/document-fill/result');
          const result = await response.json();
          
          if (result.success) {
              // result.result.html_content: 填报后HTML
              // result.result.word_content: 填报后Word（如有）
              // result.result.fill_summary: 填充摘要
              return result.result;
          } else {
              throw new Error(result.error || '获取结果失败');
          }
          
      } catch (error) {
          showMessage(`获取结果失败: ${error.message}`, 'error');
          return null;
      }
  }
  ```

- **GET /api/document-fill/download**  
  功能：下载填写完成的文档。  
  描述：提供填写后的文档文件供用户下载。
  
  **前端调用示例**：
  ```javascript
  async function downloadFilledDocument() {
      try {
          const response = await fetch('/api/document-fill/download');
          
          if (response.ok) {
              const blob = await response.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = 'filled_document.html';
              document.body.appendChild(a);
              a.click();
              window.URL.revokeObjectURL(url);
              document.body.removeChild(a);
              
              showMessage('文档下载成功！', 'success');
          } else {
              throw new Error('下载失败');
          }
          
      } catch (error) {
          showMessage(`下载失败: ${error.message}`, 'error');
      }
  }
  ```

- **POST /api/document-fill/add-material**  
  功能：添加补充材料到文档填写任务。  
  描述：允许用户上传额外的参考资料或补充内容。
  
  **前端调用示例**：
  ```javascript
  async function addMaterial(materialName, materialContent) {
      try {
          const response = await fetch('/api/document-fill/add-material', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  material_name: materialName,
                  material_content: materialContent
              })
          });
          
          const result = await response.json();
          
          if (result.success) {
              showMessage('补充材料添加成功！', 'success');
              return result;
          } else {
              throw new Error(result.error || '添加失败');
          }
          
      } catch (error) {
          showMessage(`添加材料失败: ${error.message}`, 'error');
          return null;
      }
  }
  ```

- **POST /api/document-fill/set-style**  
  功能：设置文档填写任务的写作风格模板。  
  描述：为填写任务指定特定的写作风格或格式要求。
  
  **前端调用示例**：
  ```javascript
  async function setWritingStyle(templateId) {
      try {
          const response = await fetch('/api/document-fill/set-style', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  template_id: templateId
              })
          });
          
          const result = await response.json();
          
          if (result.success) {
              showMessage('写作风格设置成功！', 'success');
              return result;
          } else {
              throw new Error(result.error || '设置失败');
          }
          
      } catch (error) {
          showMessage(`设置风格失败: ${error.message}`, 'error');
          return null;
      }
  }
  ```

- **POST /api/table-fill**  
  功能：执行智能表格批量填充操作。  
  描述：处理上传文档中的一个或多个表格，根据提供的结构化数据智能填充表格内容。

  **请求格式**:
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

  **响应格式**:
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

  **前端调用示例 (Fetch API)**：
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
              console.log('表格填充成功:', result.filled_tables);
              return result.filled_tables;
          } else {
              throw new Error(result.error || '表格填充失败');
          }
          
      } catch (error) {
          console.error('表格填充失败:', error);
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
      {'姓名': '张三', '年龄': '25', '职位': '工程师'},
      {'姓名': '李四', '年龄': '30', '职位': '经理'}
  ];
  
  const filledTables = await fillTables(tables, fillData);
  ```

  **最佳实践**:
  1.  **数据验证**: 在发送请求前，前端应验证`tables`和`fill_data`的格式，确保它们是数组且结构正确。
  2.  **错误处理**: 实现完善的try-catch机制，向用户提供友好的错误提示（如网络错误、格式错误）。
  3.  **性能优化**: 对于大量数据（如超过1000行），建议分批调用API以保证性能。

  **常见问题 (FAQ)**:
  - **Q: 如何处理空表格？**  
    A: 空表格可以正常处理，只需确保`columns`和`data`字段存在即可（例如 `{"columns": [], "data": []}`）。
  - **Q: 填充数据的顺序重要吗？**  
    A: 填充数据按数组顺序处理，建议保持与表格行的对应关系以获得最佳匹配效果。
  - **Q: 如何处理列名不匹配的情况？**  
    A: 系统会自动跳过`fill_data`中在表格`columns`里不存在的列名，只填充匹配的字段。

### 写作风格分析接口

写作风格分析接口用于分析文档的写作风格，并支持风格模板的保存和应用。这些接口主要服务于内容生成和风格一致性需求。

- **POST /api/writing-style/analyze**  
  功能：分析文档的写作风格。  
  描述：对上传的文档进行风格分析，提取语言特征和表达习惯。
  
  **前端调用示例**：
  ```javascript
  async function analyzeWritingStyle(documentContent) {
      try {
          const response = await fetch('/api/writing-style/analyze', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  document_content: documentContent
              })
          });
          
          const result = await response.json();
          
          if (result.success) {
              console.log('风格分析结果:', result.style_features);
              return result.style_features;
          } else {
              throw new Error(result.error || '风格分析失败');
          }
          
      } catch (error) {
          console.error('风格分析失败:', error);
          return null;
      }
  }
  ```

- **GET /api/writing-style/templates**  
  功能：列出所有写作风格模板。  
  描述：返回用户保存的所有写作风格模板列表。
  
  **前端调用示例**：
  ```javascript
  async function getStyleTemplates() {
      try {
          const response = await fetch('/api/writing-style/templates');
          const result = await response.json();
          
          if (result.success) {
              console.log('风格模板列表:', result.templates);
              return result.templates;
          } else {
              throw new Error(result.error || '获取模板失败');
          }
          
      } catch (error) {
          console.error('获取风格模板失败:', error);
          return [];
      }
  }
  ```

- **POST /api/writing-style/save-template**  
  功能：保存写作风格模板。  
  描述：将分析得到的风格特征保存为可重复使用的模板。
  
  **前端调用示例**：
  ```javascript
  async function saveStyleTemplate(templateName, styleFeatures) {
      try {
          const response = await fetch('/api/writing-style/save-template', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  template_name: templateName,
                  style_features: styleFeatures
              })
          });
          
          const result = await response.json();
          
          if (result.success) {
              showMessage('风格模板保存成功！', 'success');
              return result.template_id;
          } else {
              throw new Error(result.error || '保存失败');
          }
          
      } catch (error) {
          showMessage(`保存模板失败: ${error.message}`, 'error');
          return null;
      }
  }
  ```

### 数据库操作接口

数据库操作接口用于管理应用数据，包括文档历史记录、个人模板和设置等。这些接口支持数据的持久化存储和查询。

- **GET /api/database/stats**  
  功能：获取数据库统计信息。  
  描述：返回数据库的使用情况和基本统计数据。
  
  **前端调用示例**：
  ```javascript
  async function getDatabaseStats() {
      try {
          const response = await fetch('/api/database/stats');
          const stats = await response.json();
          console.log('数据库统计:', stats);
          return stats;
      } catch (error) {
          console.error('获取数据库统计失败:', error);
          return null;
      }
  }
  ```

- **GET /api/documents/history**  
  功能：获取文档处理历史记录。  
  描述：返回用户处理过的文档列表及其处理状态。
  
  **前端调用示例**：
  ```javascript
  async function getDocumentHistory() {
      try {
          const response = await fetch('/api/documents/history');
          const history = await response.json();
          console.log('文档历史:', history);
          return history;
      } catch (error) {
          console.error('获取文档历史失败:', error);
          return [];
      }
  }
  ```

- **GET /api/templates/personal**  
  功能：获取用户的个人模板列表。  
  描述：返回用户创建或保存的个人模板集合。

- **GET /api/settings**  
  功能：获取应用设置。  
  描述：返回用户的应用设置或偏好配置。
  
  **前端调用示例**：
  ```javascript
  async function getSettings() {
      try {
          const response = await fetch('/api/settings');
          const settings = await response.json();
          console.log('应用设置:', settings);
          return settings;
      } catch (error) {
          console.error('获取设置失败:', error);
          return {};
      }
  }
  ```

- **POST /api/settings**  
  功能：更新应用设置。  
  描述：接收用户提交的新设置值并更新应用配置。
  
  **前端调用示例**：
  ```javascript
  async function updateSettings(newSettings) {
      try {
          const response = await fetch('/api/settings', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(newSettings)
          });
          
          const result = await response.json();
          
          if (result.success) {
              showMessage('设置更新成功！', 'success');
              return result;
          } else {
              throw new Error(result.error || '更新失败');
          }
          
      } catch (error) {
          showMessage(`更新设置失败: ${error.message}`, 'error');
          return null;
      }
  }
  ```

### 性能监控接口

性能监控接口用于跟踪和分析应用的运行性能，帮助识别瓶颈和优化方向。这些接口主要面向开发和运维人员。

- **GET /api/performance/stats**  
  功能：获取性能统计数据。  
  描述：返回应用的运行性能指标，如响应时间、资源使用等。
  
  **前端调用示例**：
  ```javascript
  async function getPerformanceStats() {
      try {
          const response = await fetch('/api/performance/stats');
          const stats = await response.json();
          console.log('性能统计:', stats);
          return stats;
      } catch (error) {
          console.error('获取性能统计失败:', error);
          return null;
      }
  }
  ```

- **GET /api/performance/operations**  
  功能：获取操作分解数据。  
  描述：返回各操作的性能分解数据，帮助定位耗时环节。

- **GET /api/performance/history**  
  功能：获取历史性能数据。  
  描述：返回一段时间内的性能指标变化记录。

- **POST /api/performance/export**  
  功能：导出性能数据。  
  描述：将性能数据导出为文件或特定格式，供进一步分析。

- **POST /api/test/cleanup**  
  功能：清理测试资源（第一阶段新增）。  
  描述：清理测试过程中产生的临时文件、缓存文件、上传文件等资源。
  
  **请求格式**：
  ```json
  {
    "test_session_id": "session_123456",
    "cleanup_type": "all"
  }
  ```
  
  **响应格式**：
  ```json
  {
    "success": true,
    "cleaned_items": {
      "temp_files": 5,
      "test_sessions": 2,
      "cache_files": 3,
      "upload_files": 1
    },
    "message": "清理完成"
  }
  ```
  
  **前端调用示例**：
  ```javascript
  async function cleanupTestResources(testSessionId = null, cleanupType = 'all') {
      try {
          const response = await fetch('/api/test/cleanup', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  test_session_id: testSessionId,
                  cleanup_type: cleanupType
              })
          });
          
          const result = await response.json();
          
          if (result.success) {
              console.log('清理完成:', result.cleaned_items);
              showMessage(`清理完成，共清理 ${result.cleaned_items.temp_files} 个临时文件`, 'success');
              return result.cleaned_items;
          } else {
              throw new Error(result.error || '清理失败');
          }
      } catch (error) {
          console.error('清理测试资源失败:', error);
          showMessage(`清理失败: ${error.message}`, 'error');
          return null;
      }
  }
  ```

### 批量处理接口

批量处理接口支持大规模文档处理任务的创建和管理，适用于处理多个文档或复杂工作流的用户需求。

- **POST /api/batch/create**  
  功能：创建批量处理任务。  
  描述：初始化一个新的批量处理任务，接收任务参数和文件列表。
  
  **前端调用示例**：
  ```javascript
  async function createBatchJob(jobParams) {
      try {
          const response = await fetch('/api/batch/create', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(jobParams)
          });
          
          const result = await response.json();
          
          if (result.success) {
              showMessage('批量任务创建成功！', 'success');
              return result.job_id;
          } else {
              throw new Error(result.error || '创建失败');
          }
          
      } catch (error) {
          showMessage(`创建批量任务失败: ${error.message}`, 'error');
          return null;
      }
  }
  ```

- **POST /api/batch/start/<job_id>**  
  功能：启动指定批量处理任务。  
  描述：根据任务ID启动批量处理流程，开始执行任务。

- **GET /api/batch/jobs**  
  功能：获取所有批量处理任务列表。  
  描述：返回用户创建的所有批量任务及其当前状态。
  
  **前端调用示例**：
  ```javascript
  async function getBatchJobs() {
      try {
          const response = await fetch('/api/batch/jobs');
          const jobs = await response.json();
          console.log('批量任务列表:', jobs);
          return jobs;
      } catch (error) {
          console.error('获取批量任务失败:', error);
          return [];
      }
  }
  ```

- **GET /api/batch/job/<job_id>**  
  功能：获取指定批量处理任务的状态。  
  描述：根据任务ID返回该任务的详细信息和进度。

- **POST /api/batch/cancel/<job_id>**  
  功能：取消指定批量处理任务。  
  描述：根据任务ID终止正在运行的批量任务。

## 🛠️ 前端开发工具函数

### 通用工具函数
```javascript
// 显示加载状态
function showLoading(message = '处理中...') {
    const loadingEl = document.getElementById('loading');
    if (loadingEl) {
        loadingEl.textContent = message;
        loadingEl.style.display = 'block';
    }
}

// 隐藏加载状态
function hideLoading() {
    const loadingEl = document.getElementById('loading');
    if (loadingEl) {
        loadingEl.style.display = 'none';
    }
}

// 显示消息
function showMessage(message, type = 'info') {
    const messageEl = document.getElementById('message');
    if (messageEl) {
        messageEl.textContent = message;
        messageEl.className = `message message-${type}`;
        messageEl.style.display = 'block';
        
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 3000);
    }
}

// 文件大小格式化
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 读取文件内容
function readFileContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsText(file);
    });
}
```

## 📖 使用指南与注意事项

在使用上述API接口时，建议遵循以下原则以确保高效和安全操作。首先，所有API调用应包含适当的身份验证信息，以防止未经授权的访问。其次，对于涉及文件上传或数据处理的接口（如`/api/upload`、`/api/document-fill/start`），建议限制文件大小和处理时间，以避免资源滥用。

此外，开发人员在调用API时应注意请求频率控制，特别是对于性能监控和健康检查接口，避免因频繁调用导致系统负载过高。对于批量处理任务，建议合理规划任务规模，确保任务执行期间系统资源充足。

### 前端开发最佳实践

1. **错误处理**：所有API调用都应包含try-catch错误处理
2. **加载状态**：长时间操作应显示加载状态
3. **用户反馈**：操作结果应及时反馈给用户
4. **参数验证**：前端应进行基本的参数验证
5. **文件处理**：文件上传前应检查格式和大小

### 接口调用流程示例

```javascript
// 完整的文档处理流程示例
async function processDocument(file) {
    try {
        // 1. 上传文件
        const uploadResult = await uploadFile(file);
        if (!uploadResult) return;
        
        // 2. 读取文件内容
        const content = await readFileContent(file);
        
        // 3. 启动文档填写
        const fillSession = await startDocumentFill(content, file.name);
        if (!fillSession) return;
        
        // 4. 显示首轮问题
        displayQuestion(fillSession.response);
        
        // 5. 设置问题回答处理
        setupQuestionResponse();
        
    } catch (error) {
        showMessage(`处理失败: ${error.message}`, 'error');
    }
}
```

如需更详细的参数说明或示例代码，可参考项目代码库中的测试文件（如`test_api_comprehensive.py`）或相关文档。未来版本的接口文档将进一步补充请求和响应示例，以便于开发人员快速上手。

## 📋 结论

本后端接口开发文档梳理了Office-Doc-Agent项目中已实现的45个API端点，覆盖了从页面访问到复杂文档处理的全方位功能。通过对API进行模块化分类，本文档为开发人员提供了清晰的接口参考，有助于接口调用、测试验证及后续功能扩展。

**本文档同时包含后端接口定义和前端调用示例，确保前后端开发的一致性。**

在未来的开发工作中，建议团队持续更新接口文档，确保其与代码实现保持同步。同时，针对部分高频使用接口（如文档上传和填写接口），可考虑开发更详细的使用教程或SDK，以提升开发效率和用户体验。

## 🔮 补充API设计建议

以下API设计建议基于前端设计和现有后端API的全面分析，填补了当前实现与前端需求之间的差距。这些建议遵循RESTful API设计的最佳实践，与现有`web_app.py`文件结构保持一致。

### 1. 文风统一预览与接受/拒绝

**目的**：允许用户预览应用于文档的文风变化，并逐个或批量接受或拒绝这些变化。

#### 预览文风变化
- **端点**：`/api/style-alignment/preview`
- **方法**：`POST`
- **参数**：
  - `document_content` (string)：要应用文风变化的文档内容
  - `document_name` (string)：文档名称
  - `style_template_id` (string)：要应用的文风模板ID
- **响应**：
  - `success` (boolean)：指示操作是否成功
  - `preview_data` (object)：包含带有高亮变化和建议的原始内容
    - `original_content` (string)：原始文档内容
    - `suggested_changes` (array)：包含ID、原始文本、建议文本和简要修改原因的变化列表
  - `session_id` (string)：用于后续操作的预览会话的唯一标识符

**前端调用示例**：
```javascript
async function previewStyleChanges(documentContent, documentName, styleTemplateId) {
    try {
        showLoading('正在生成文风预览...');
        
        const response = await fetch('/api/style-alignment/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                document_content: documentContent,
                document_name: documentName,
                style_template_id: styleTemplateId
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayStylePreview(result.preview_data);
            return result.session_id;
        } else {
            throw new Error(result.error || '预览生成失败');
        }
        
    } catch (error) {
        showMessage(`预览失败: ${error.message}`, 'error');
        return null;
    } finally {
        hideLoading();
    }
}
```

#### 接受/拒绝单个变化
- **端点**：`/api/style-alignment/changes/<session_id>/<change_id>`
- **方法**：`PATCH`
- **参数**：
  - `action` (string)：指示对特定变化的操作，值为"accept"或"reject"
- **响应**：
  - `success` (boolean)：指示操作是否成功
  - `change_id` (string)：被操作的变化ID
  - `action` (string)：执行的操作（"accept"或"reject"）
  - `updated_preview` (object)：可选地返回操作后的更新预览

#### 接受/拒绝所有变化
- **端点**：`/api/style-alignment/changes/<session_id>/batch`
- **方法**：`PATCH`
- **参数**：
  - `action` (string)：对所有变化应用的操作，值为"accept_all"或"reject_all"
- **响应**：
  - `success` (boolean)：指示操作是否成功
  - `action` (string)：执行的批量操作
  - `change_count` (integer)：受操作影响的变化数量

#### 导出文风调整后的文档
- **端点**：`/api/style-alignment/export/<session_id>`
- **方法**：`GET`
- **响应**：返回应用了所有接受的文风变化的文档作为可下载的DOCX文件

### 2. 智能填报的自动匹配数据

**目的**：在填报过程中启用数据到文档模板字段的自动匹配。

#### 自动匹配数据
- **端点**：`/api/document-fill/auto-match`
- **方法**：`POST`
- **参数**：
  - `session_id` (string)：活动文档填报会话的ID
  - `data_sources` (array)：要与文档字段匹配的数据源列表（文本或文件引用）
- **响应**：
  - `success` (boolean)：指示操作是否成功
  - `matched_fields` (object)：包含字段ID映射到匹配数据值的对象
  - `unmatched_fields` (array)：无法自动匹配的字段ID列表
  - `confidence_scores` (object)：每个匹配字段的置信度分数
  - `conflicts` (array)：多个数据源为同一字段提供值时的冲突列表

**前端调用示例**：
```javascript
async function autoMatchData(sessionId, dataSources) {
    try {
        showLoading('正在自动匹配数据...');
        
        const response = await fetch('/api/document-fill/auto-match', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                data_sources: dataSources
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayMatchedFields(result.matched_fields);
            if (result.conflicts.length > 0) {
                displayConflicts(result.conflicts);
            }
            return result;
        } else {
            throw new Error(result.error || '自动匹配失败');
        }
        
    } catch (error) {
        showMessage(`自动匹配失败: ${error.message}`, 'error');
        return null;
    } finally {
        hideLoading();
    }
}
```

#### 解决冲突
- **端点**：`/api/document-fill/auto-match/conflicts/<session_id>`
- **方法**：`PATCH`
- **参数**：
  - `resolutions` (object)：用户解决冲突的选择，将字段ID映射到所选值
- **响应**：
  - `success` (boolean)：指示操作是否成功
  - `resolved_fields` (object)：解决冲突的字段及其最终值

### 3. 文档审阅

**目的**：支持完整的文档审阅过程，包括发起审阅、获取建议、接受/拒绝建议以及导出审阅后的文档。

#### 开始审阅
- **端点**：`/api/document-review/start`
- **方法**：`POST`
- **参数**：
  - `document_content` (string)：要审阅的文档内容
  - `document_name` (string)：文档名称
  - `review_focus` (string)：审阅的重点（例如，"academic"、"business"、"auto"）
- **响应**：
  - `success` (boolean)：指示操作是否成功
  - `review_session_id` (string)：审阅会话的唯一标识符
  - `status` (string)：审阅过程的初始状态

**前端调用示例**：
```javascript
async function startDocumentReview(documentContent, documentName, reviewFocus) {
    try {
        showLoading('正在启动文档审阅...');
        
        const response = await fetch('/api/document-review/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                document_content: documentContent,
                document_name: documentName,
                review_focus: reviewFocus
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('文档审阅已启动', 'success');
            return result.review_session_id;
        } else {
            throw new Error(result.error || '审阅启动失败');
        }
        
    } catch (error) {
        showMessage(`审阅启动失败: ${error.message}`, 'error');
        return null;
    } finally {
        hideLoading();
    }
}
```

#### 获取审阅建议
- **端点**：`/api/document-review/suggestions/<review_session_id>`
- **方法**：`GET`
- **响应**：
  - `success` (boolean)：指示操作是否成功
  - `suggestions` (array)：按优先级排序的审阅建议列表

#### 接受/拒绝建议
- **端点**：`/api/document-review/suggestions/<review_session_id>/<suggestion_id>`
- **方法**：`PATCH`
- **参数**：
  - `action` (string)：指示对特定建议的操作，值为"accept"或"reject"

#### 接受/拒绝所有建议
- **端点**：`/api/document-review/suggestions/<review_session_id>/batch`
- **方法**：`PATCH`
- **参数**：
  - `action` (string)：对所有建议应用的操作，值为"accept_all"或"reject_all"

#### 导出审阅后的文档
- **端点**：`/api/document-review/export/<review_session_id>`
- **方法**：`GET`
- **响应**：返回应用了接受的建议的审阅文档作为可下载的DOCX文件

### 4. 模板管理（格式和文风）

**目的**：实现格式和文风模板的全面管理，包括重命名和删除。

#### 重命名模板
- **端点**：`/api/templates/<template_type>/<template_id>/rename`
- **方法**：`PATCH`
- **参数**：
  - `template_type` (string)：指定模板类型，值为"format"或"style"
  - `new_name` (string)：模板的新名称
- **响应**：
  - `success` (boolean)：指示操作是否成功
  - `template_id` (string)：重命名的模板ID
  - `new_name` (string)：模板更新后的名称

#### 删除模板确认
- **端点**：`/api/templates/<template_type>/<template_id>/confirm-delete`
- **方法**：`GET`
- **响应**：
  - `success` (boolean)：指示操作是否成功
  - `confirmation_message` (string)：提醒用户删除后果的消息
  - `confirmation_token` (string)：完成删除所需的临时令牌

#### 确认删除模板
- **端点**：`/api/templates/<template_type>/<template_id>`
- **方法**：`DELETE`
- **参数**：
  - `confirmation_token` (string)：从确认步骤收到的令牌，用于验证删除
- **响应**：
  - `success` (boolean)：指示操作是否成功
  - `template_id` (string)：删除的模板ID

### 5. 从历史记录中重新应用操作

**目的**：允许用户从文档处理历史记录中重新应用特定操作。

#### 重新应用操作
- **端点**：`/api/documents/history/<record_id>/reapply`
- **方法**：`POST`
- **参数**：
  - `record_id` (string)：要重新应用的历史记录ID
- **响应**：
  - `success` (boolean)：指示操作是否成功
  - `new_record_id` (string)：通过重新应用操作创建的新处理记录ID
  - `status` (string)：重新应用过程的状态
  - `message` (string, 可选)：如果原始文件缺失，则显示相应消息

#### 为重新应用上传文件
- **端点**：`/api/documents/history/<record_id>/upload`
- **方法**：`POST`
- **参数**：
  - `record_id` (string)：要为其上传文件的历史记录ID
  - `file` (file)：作为缺失原始文件替代品上传的文件
- **响应**：
  - `success` (boolean)：指示操作是否成功
  - `file_path` (string)：上传文件的路径
  - `message` (string)：确认消息

**前端调用示例**：
```javascript
async function reapplyHistoryOperation(recordId) {
    try {
        showLoading('正在重新应用操作...');
        
        const response = await fetch(`/api/documents/history/${recordId}/reapply`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('操作重新应用成功', 'success');
            return result.new_record_id;
        } else {
            if (result.message && result.message.includes('文件缺失')) {
                showMessage('原始文件缺失，请重新上传', 'warning');
                return null;
            }
            throw new Error(result.error || '重新应用失败');
        }
        
    } catch (error) {
        showMessage(`重新应用失败: ${error.message}`, 'error');
        return null;
    } finally {
        hideLoading();
    }
}
```

## 📋 结论

本后端接口开发文档梳理了Office-Doc-Agent项目中已实现的45个API端点，覆盖了从页面访问到复杂文档处理的全方位功能。通过对API进行模块化分类，本文档为开发人员提供了清晰的接口参考，有助于接口调用、测试验证及后续功能扩展。

**本文档同时包含后端接口定义和前端调用示例，确保前后端开发的一致性。**

在未来的开发工作中，建议团队持续更新接口文档，确保其与代码实现保持同步。同时，针对部分高频使用接口（如文档上传和填写接口），可考虑开发更详细的使用教程或SDK，以提升开发效率和用户体验。

---
**文档人**: AI Assistant (Claude)  
**文档时间**: 2025年6月26日  
**版本**: v3.0  
**状态检测**: 已完成 (2025-06-26 10:15:00)  
**审核状态**: 待审核
