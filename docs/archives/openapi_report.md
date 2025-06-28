# API接口自动化文档

- 路径: `/`
  方法: GET
  说明: 系统主页入口，主流程所有页面和功能依赖此入口。

- 路径: `/demo`
  方法: GET
  说明: 系统演示与端到端测试专用页面，便于演示和自动化测试。

- 路径: `/examples/<filename>`
  方法: GET
  说明: 示例文件下载与演示专用接口，前端演示和测试依赖。

- 路径: `/debug_frontend.html`
  方法: GET
  说明: 前端调试专用页面，仅开发调试用途，非主流程用户功能。

- 路径: `/test_ai_features.html`
  方法: GET
  说明: AI能力演示与测试专用页面，便于AI功能端到端测试。

- 路径: `/api/upload`
  方法: 'POST'
  说明: 获取所有格式模板

- 路径: `/api/health`
  方法: GET
  说明: 获取特定格式模板

- 路径: `/api/config`
  方法: GET
  说明: 保存格式模板

- 路径: `/api/format-alignment`
  方法: 'POST'
  说明: 应用格式模板到文档

- 路径: `/api/format-templates`
  方法: 'GET'
  说明: 预览格式对齐后的文档

- 路径: `/api/format-templates/<template_id>`
  方法: 'GET'
  说明: Get available models for each API type.

- 路径: `/api/format-templates`
  方法: 'POST'
  说明: 响应文档填充问题

- 路径: `/api/format-templates/<template_id>/apply`
  方法: 'POST'
  说明: 获取文档填充状态

- 路径: `/api/format-alignment/preview/<session_id>`
  方法: GET
  说明: 获取文档填充结果

- 路径: `/api/models`
  方法: GET
  说明: 下载填充后的文档

- 路径: `/api/document-fill/start`
  方法: 'POST'
  说明: 添加补充材料

- 路径: `/api/document-fill/respond`
  方法: 'POST'
  说明: 分析文档写作风格

- 路径: `/api/document-fill/status`
  方法: 'GET'
  说明: 保存文风模板

- 路径: `/api/document-fill/result`
  方法: 'GET'
  说明: 获取所有文风模板

- 路径: `/api/document-fill/download`
  方法: 'GET'
  说明: 获取特定文风模板

- 路径: `/api/document-fill/add-material`
  方法: 'POST'
  说明: 设置文档填充的文风模板

- 路径: `/api/writing-style/analyze`
  方法: 'POST'
  说明: 预览文风变化

- 路径: `/api/writing-style/save-template`
  方法: 'POST'
  说明: 接受或拒绝单个文风变化

- 路径: `/api/writing-style/templates`
  方法: 'GET'
  说明: 批量接受或拒绝所有文风变化

- 路径: `/api/writing-style/templates/<template_id>`
  方法: 'GET'
  说明: 导出应用了文风变化的文档

- 路径: `/api/document-fill/set-style`
  方法: 'POST'
  说明: 自动匹配数据到文档字段

- 路径: `/api/style-alignment/preview`
  方法: 'POST'
  说明: 解决自动匹配中的冲突

- 路径: `/api/style-alignment/changes/<session_id>/<change_id>`
  方法: 'PATCH'
  说明: 开始文档审阅过程

- 路径: `/api/style-alignment/changes/<session_id>/batch`
  方法: 'PATCH'
  说明: 获取文档审阅建议

- 路径: `/api/style-alignment/export/<session_id>`
  方法: 'GET'
  说明: 接受或拒绝特定审阅建议

- 路径: `/api/document-fill/auto-match`
  方法: 'POST'
  说明: 批量接受或拒绝所有审阅建议

- 路径: `/api/document-fill/auto-match/conflicts/<session_id>`
  方法: 'PATCH'
  说明: 导出评审后的文档

- 路径: `/api/document-review/start`
  方法: 'POST'
  说明: 重命名模板

- 路径: `/api/document-review/suggestions/<review_session_id>`
  方法: 'GET'
  说明: 确认删除模板

- 路径: `/api/document-review/suggestions/<review_session_id>/<suggestion_id>`
  方法: 'PATCH'
  说明: 删除模板

- 路径: `/api/document-review/suggestions/<review_session_id>/batch`
  方法: 'PATCH'
  说明: 重新应用历史操作

- 路径: `/api/document-review/export/<review_session_id>`
  方法: 'GET'
  说明: 为重新应用上传文件

- 路径: `/api/templates/<template_type>/<template_id>/rename`
  方法: 'PATCH'
  说明: 获取数据库统计信息

- 路径: `/api/templates/<template_type>/<template_id>/confirm-delete`
  方法: 'GET'
  说明: 获取文档处理历史

- 路径: `/api/templates/<template_type>/<template_id>`
  方法: 'DELETE'
  说明: 获取个人模板列表

- 路径: `/api/documents/history/<record_id>/reapply`
  方法: 'POST'
  说明: 获取应用设置

- 路径: `/api/documents/history/<record_id>/upload`
  方法: 'POST'
  说明: 更新应用设置

- 路径: `/api/database/stats`
  方法: 'GET'
  说明: 智能表格批量填充API
    请求参数:
      - tables: List[dict]，每个dict包含'columns'和'data'（二维数组）
      - fill_data: list of dict，每个 dict 对应一行数据，key 为表头
    返回:
      - 填充后的表格内容（json）

- 路径: `/api/documents/history`
  方法: 'GET'
  说明: 仪表板页面

- 路径: `/api/templates/personal`
  方法: 'GET'
  说明: 获取性能统计数据

- 路径: `/api/settings`
  方法: 'GET'
  说明: 获取API健康状态

- 路径: `/api/settings`
  方法: 'POST'
  说明: 获取操作类型分解统计

- 路径: `/api/table-fill`
  方法: 'POST'
  说明: 获取处理历史记录

- 路径: `/dashboard`
  方法: GET
  说明: 系统仪表板入口，性能监控、统计、历史记录等主流程依赖此接口。

- 路径: `/api/performance/stats`
  方法: GET
  说明: 批量处理页面

- 路径: `/api/performance/health`
  方法: GET
  说明: 创建批量处理作业

- 路径: `/api/performance/operations`
  方法: GET
  说明: 启动批量处理作业

- 路径: `/api/performance/history`
  方法: GET
  说明: 获取批量处理作业列表

- 路径: `/api/performance/export`
  方法: 'POST'
  说明: 获取批量处理作业状态

- 路径: `/batch`
  方法: GET
  说明: 批量处理主流程入口，批量文档处理、任务管理等核心功能依赖此接口。

- 路径: `/api/batch/create`
  方法: 'POST'
  说明: 注册批量处理器函数

- 路径: `/api/batch/start/<job_id>`
  方法: 'POST'
  说明: 文档解析处理器

- 路径: `/api/batch/jobs`
  方法: GET
  说明: 格式整理处理器

- 路径: `/api/batch/job/<job_id>`
  方法: GET
  说明: 内容生成处理器

- 路径: `/api/batch/cancel/<job_id>`
  方法: 'POST'
  说明: 风格转换处理器

- 路径: `/api/enhanced-document/analyze`
  方法: 'POST'
  说明: 获取AI填写建议API

- 路径: `/api/enhanced-document/fill`
  方法: 'POST'
  说明: 

- 路径: `/api/patent-document/analyze`
  方法: 'POST'
  说明: 

- 路径: `/api/image/process`
  方法: 'POST'
  说明: 

- 路径: `/api/image/batch-process`
  方法: 'POST'
  说明: 

- 路径: `/api/image/statistics`
  方法: 'GET'
  说明: 

- 路径: `/api/ai-fill-suggestions`
  方法: 'POST'
  说明: 

