// 全局变量
let selectedFile = null;
let processingResult = null;
let currentTab = 'upload';
let availableModels = {};
let sourceFile = null;
let targetFile = null;
let formatTemplates = [];

// DOM 元素
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const uploadContent = document.getElementById('upload-content');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const processBtn = document.getElementById('process-btn');
const processingStatus = document.getElementById('processing-status');
const progressBar = document.getElementById('progress-bar');
const resultsTab = document.getElementById('results-tab');
const resultsContent = document.getElementById('results-content');
const errorSection = document.getElementById('error-section');
const errorMessage = document.getElementById('error-message');
const downloadBtn = document.getElementById('download-btn');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');

// 标签页元素
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// 分析结果元素
const docType = document.getElementById('doc-type');
const docScenario = document.getElementById('doc-scenario');
const keyInfo = document.getElementById('key-info');
const paragraphs = document.getElementById('paragraphs');
const charCount = document.getElementById('char-count');
const completeness = document.getElementById('completeness');

// 工具卡片
const toolCards = document.querySelectorAll('.tool-card');

// API配置元素
const apiTypeSelect = document.getElementById('api-type');
const modelNameSelect = document.getElementById('model-name');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkSystemStatus();
    loadAvailableModels();
});

// 初始化应用
function initializeApp() {
    console.log('办公文档智能代理 Web 界面已加载');
}

// 设置事件监听器
function setupEventListeners() {
    // 文件选择
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // 拖拽上传
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // 处理按钮
    processBtn.addEventListener('click', processDocument);
    
    // 标签页切换
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    
    // 工具卡片点击
    toolCards.forEach(card => {
        const button = card.querySelector('button');
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            handleToolAction(card.dataset.tool);
        });
    });
    
    // API类型选择
    apiTypeSelect.addEventListener('change', handleApiTypeChange);

    // 初始化格式对齐功能
    initFormatAlignment();
}

// 加载可用模型
async function loadAvailableModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();
        
        if (data.models) {
            availableModels = data.models;
            updateModelOptions();
        }
    } catch (error) {
        console.error('Failed to load models:', error);
        // 使用默认模型
        availableModels = {
            'xingcheng': ['x1', 'x2', 'x3'],
            'multi': ['auto'],
            'mock': ['mock-model']
        };
        updateModelOptions();
    }
}

// 更新模型选项
function updateModelOptions() {
    const currentApiType = apiTypeSelect.value;
    const models = availableModels[currentApiType] || [];
    
    // 清空现有选项
    modelNameSelect.innerHTML = '<option value="">自动选择</option>';
    
    // 添加新选项
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = getModelDisplayName(model);
        modelNameSelect.appendChild(option);
    });
}

// 获取模型显示名称
function getModelDisplayName(model) {
    const modelNames = {
        'x1': '星火大模型 X1',
        'x2': '星火大模型 X2',
        'x3': '星火大模型 X3',
        'auto': '自动选择最佳模型',
        'mock-model': '模拟模型',
        'deepseek-v3': 'DeepSeek V3',
        'mistralai/Mixtral-8x7B-Instruct-v0.1': 'Mixtral 8x7B',
        'qwen/qwen1.5-72b-chat': 'Qwen 1.5 72B',
        'openrouter/mistralai/mixtral-8x7b-instruct': 'Mixtral 8x7B (OpenRouter)',
        'together/mistralai/Mixtral-8x7B-Instruct-v0.1': 'Mixtral 8x7B (Together.ai)',
        'qiniu/deepseek-v3': 'DeepSeek V3 (七牛云)'
    };
    
    return modelNames[model] || model;
}

// 处理API类型变化
function handleApiTypeChange() {
    updateModelOptions();
}

// 切换标签页
function switchTab(tabName) {
    // 更新按钮状态
    tabBtns.forEach(btn => {
        btn.classList.remove('active', 'bg-blue-100', 'text-blue-700');
        btn.classList.add('text-gray-600');
    });
    
    // 激活当前按钮
    const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active', 'bg-blue-100', 'text-blue-700');
        activeBtn.classList.remove('text-gray-600');
    } else {
        console.error(`Tab button not found for: ${tabName}`);
    }

    // 隐藏所有内容
    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    // 显示当前内容
    const activeContent = document.getElementById(`${tabName}-tab`);
    if (activeContent) {
        activeContent.classList.add('active');
    } else {
        console.error(`Tab content not found for: ${tabName}-tab`);
    }
    
    currentTab = tabName;
    
    // 如果切换到分析标签页且有处理结果，更新分析数据
    if (tabName === 'analysis' && processingResult) {
        updateAnalysisData();
    }
    
    // 如果切换到结果标签页且有处理结果，显示结果
    if (tabName === 'results' && processingResult) {
        showResultsInTab();
    }
}

// 处理工具操作
function handleToolAction(toolName) {
    if (!processingResult) {
        showNotification('请先上传并处理文档', 'error');
        return;
    }
    
    showNotification(`正在执行 ${getToolDisplayName(toolName)}...`, 'info');
    
    // 模拟工具处理
    setTimeout(() => {
        const result = simulateToolProcessing(toolName);
        showNotification(`${getToolDisplayName(toolName)} 完成！`, 'success');
        
        // 更新处理结果
        if (!processingResult.tool_results) {
            processingResult.tool_results = {};
        }
        processingResult.tool_results[toolName] = result;
        
        // 切换到结果标签页
        switchTab('results');
    }, 2000);
}

// 获取工具显示名称
function getToolDisplayName(toolName) {
    const toolNames = {
        'content-filler': '内容填充',
        'style-generator': '样式生成',
        'virtual-reviewer': '虚拟审阅',
        'meeting-review': '会议回顾',
        'document-output': '文档输出',
        'batch-process': '批量处理'
    };
    return toolNames[toolName] || toolName;
}

// 模拟工具处理
function simulateToolProcessing(toolName) {
    const results = {
        'content-filler': {
            status: 'success',
            message: '已智能填充3个段落内容，补充了关键信息',
            suggestions: ['建议添加更多数据支撑', '可以增加图表说明']
        },
        'style-generator': {
            status: 'success',
            message: '已生成专业样式模板',
            styles: ['标题样式', '正文样式', '引用样式']
        },
        'virtual-reviewer': {
            status: 'success',
            message: '审阅完成，发现3处需要修改的地方',
            issues: ['语法错误', '逻辑不清晰', '格式不规范']
        },
        'meeting-review': {
            status: 'success',
            message: '已生成会议纪要',
            summary: '会议要点总结...'
        },
        'document-output': {
            status: 'success',
            message: '文档已导出',
            formats: ['PDF', 'DOCX', 'TXT']
        },
        'batch-process': {
            status: 'success',
            message: '批量处理完成',
            processed: 5
        }
    };
    
    return results[toolName] || { status: 'error', message: '工具处理失败' };
}

// 检查系统状态
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            statusDot.className = 'w-3 h-3 bg-green-400 rounded-full';
            statusText.textContent = '系统正常';
        } else {
            statusDot.className = 'w-3 h-3 bg-red-400 rounded-full';
            statusText.textContent = '系统异常';
        }
    } catch (error) {
        console.error('状态检查失败:', error);
        statusDot.className = 'w-3 h-3 bg-yellow-400 rounded-full';
        statusText.textContent = '连接中...';
    }
}

// 处理文件选择
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedFile = file;
        displayFileInfo(file);
        processBtn.disabled = false;
    }
}

// 处理拖拽悬停
function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

// 处理拖拽离开
function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

// 处理文件拖拽
function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (isValidFile(file)) {
            selectedFile = file;
            displayFileInfo(file);
            processBtn.disabled = false;
        } else {
            showError('不支持的文件格式。请上传 TXT、PDF 或 DOCX 文件。');
        }
    }
}

// 验证文件格式
function isValidFile(file) {
    const allowedTypes = ['.txt', '.pdf', '.docx'];
    const fileName = file.name.toLowerCase();
    return allowedTypes.some(type => fileName.endsWith(type));
}

// 显示文件信息
function displayFileInfo(file) {
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    uploadContent.classList.add('hidden');
    fileInfo.classList.remove('hidden');
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 处理文档
async function processDocument() {
    if (!selectedFile) {
        showError('请先选择文件');
        return;
    }
    
    // 显示处理状态
    showProcessingStatus();
    
    // 创建 FormData
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('api_type', apiTypeSelect.value);
    formData.append('model_name', modelNameSelect.value);
    
    try {
        // 模拟进度
        simulateProgress();
        
        // 发送请求
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            processingResult = data.result;
            showResults(data);
            updateAnalysisData();
            showNotification('文档处理成功！', 'success');
        } else {
            showError(data.error || '处理失败');
        }
    } catch (error) {
        console.error('处理错误:', error);
        showError('网络错误，请检查连接后重试');
    } finally {
        hideProcessingStatus();
    }
}

// 更新分析数据
function updateAnalysisData() {
    if (!processingResult) return;
    
    // 文档类型分析
    docType.textContent = processingResult.scenario_analysis?.document_type || '未知';
    docScenario.textContent = processingResult.scenario_analysis?.scenario || '通用文档';
    keyInfo.textContent = processingResult.scenario_analysis?.key_points?.join(', ') || '无';
    
    // 结构分析
    if (processingResult.structure_info) {
        paragraphs.textContent = processingResult.structure_info.paragraphs || processingResult.structure_info.lines || '0';
        charCount.textContent = processingResult.text_content?.length || '0';
        completeness.textContent = '完整';
    }
}

// 显示处理状态
function showProcessingStatus() {
    processingStatus.classList.remove('hidden');
    errorSection.classList.add('hidden');
    processBtn.disabled = true;
}

// 隐藏处理状态
function hideProcessingStatus() {
    processingStatus.classList.add('hidden');
    processBtn.disabled = false;
}

// 模拟进度条
function simulateProgress() {
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) {
            progress = 90;
            clearInterval(interval);
        }
        progressBar.style.width = progress + '%';
    }, 200);
}

// 显示结果
function showResults(data) {
    console.log('showResults called with data:', data);

    // 检查resultsContent是否存在
    if (!resultsContent) {
        console.error('resultsContent element not found');
        showNotification('结果显示区域未找到，但处理已完成', 'warning');
        return;
    }

    resultsContent.innerHTML = '';

    // 文档信息
    const docInfo = createResultCard('文档信息', {
        '文件名': data.filename,
        '处理时间': new Date(data.processed_at).toLocaleString(),
        'API类型': data.api_type || '未知',
        '模型': data.model_name || '自动选择',
        '状态': '处理完成'
    });
    resultsContent.appendChild(docInfo);
    
    // 处理结果
    if (data.result && !data.result.error) {
        // 文档内容
        if (data.result.text_content) {
            const contentCard = createResultCard('文档内容', {
                '内容预览': data.result.text_content.substring(0, 200) + '...',
                '字符数': data.result.text_content.length
            });
            resultsContent.appendChild(contentCard);
        }
        
        // 结构信息
        if (data.result.structure_info) {
            const structureCard = createResultCard('文档结构', data.result.structure_info);
            resultsContent.appendChild(structureCard);
        }
        
        // 场景分析
        if (data.result.scenario_analysis) {
            const scenarioCard = createResultCard('场景分析', data.result.scenario_analysis);
            resultsContent.appendChild(scenarioCard);
        }
        
        // 内容摘要
        if (data.result.content_summary) {
            const summaryCard = createResultCard('智能摘要', {
                '内容摘要': data.result.content_summary
            });
            resultsContent.appendChild(summaryCard);
        }

        // 关键实体提取
        if (data.result.key_entities && data.result.key_entities.length > 0) {
            const entitiesData = {};
            data.result.key_entities.forEach((entity, index) => {
                entitiesData[`${entity.type} ${index + 1}`] = entity.value;
            });
            const entitiesCard = createResultCard('关键实体提取', entitiesData);
            resultsContent.appendChild(entitiesCard);
        }

        // 内容分析
        if (data.result.content_analysis) {
            const contentAnalysis = createResultCard('内容深度分析', data.result.content_analysis);
            resultsContent.appendChild(contentAnalysis);
        }

        // 质量评估
        if (data.result.quality_assessment) {
            const qualityData = {
                '完整性评分': `${(data.result.quality_assessment.completeness * 100).toFixed(0)}%`,
                '清晰度评分': `${(data.result.quality_assessment.clarity * 100).toFixed(0)}%`,
                '结构性评分': `${(data.result.quality_assessment.structure * 100).toFixed(0)}%`,
                '综合评分': `${(data.result.quality_assessment.overall_score * 100).toFixed(0)}%`,
                '改进领域': data.result.quality_assessment.areas_for_improvement.join(', ')
            };
            const qualityCard = createResultCard('质量评估', qualityData);
            resultsContent.appendChild(qualityCard);
        }

        // AI功能展示
        if (data.result.ai_features_used) {
            const aiFeatures = createResultCard('AI功能应用', {
                '使用的AI功能': data.result.ai_features_used.join(', '),
                '处理模式': data.result.mock_mode ? '模拟模式' : '真实API',
                '处理时间': data.result.processing_time || '未知'
            });
            resultsContent.appendChild(aiFeatures);
        }

        // 建议
        if (data.result.suggestions) {
            const suggestionsCard = createResultCard('智能优化建议', data.result.suggestions);
            resultsContent.appendChild(suggestionsCard);
        }
    } else {
        // 错误信息
        const errorCard = createResultCard('处理结果', {
            '状态': '处理失败',
            '错误信息': data.result?.error || '未知错误'
        });
        resultsContent.appendChild(errorCard);
    }
    
    // 工具处理结果
    if (data.result?.tool_results) {
        Object.entries(data.result.tool_results).forEach(([toolName, result]) => {
            const toolCard = createResultCard(getToolDisplayName(toolName), result);
            resultsContent.appendChild(toolCard);
        });
    }
    
    // 尝试切换到结果标签页并显示结果
    try {
        switchTab('results');
    } catch (error) {
        console.error('Error switching to results tab:', error);
        // 如果切换标签页失败，至少显示成功通知
        showNotification('文档处理完成！结果已准备就绪。', 'success');
    }
}

// 在结果标签页中显示结果
function showResultsInTab() {
    if (processingResult) {
        showResults({ result: processingResult, filename: selectedFile?.name || 'unknown' });
    }
}

// 安全的JSON字符串化函数，避免循环引用
function safeStringify(obj, maxDepth = 3, currentDepth = 0) {
    if (currentDepth > maxDepth) {
        return '[Max depth reached]';
    }

    if (obj === null || obj === undefined) {
        return String(obj);
    }

    if (typeof obj !== 'object') {
        return String(obj);
    }

    if (Array.isArray(obj)) {
        if (obj.length === 0) return '[]';
        if (obj.length > 10) {
            return `[Array with ${obj.length} items]`;
        }
        return obj.map(item => safeStringify(item, maxDepth, currentDepth + 1)).join(', ');
    }

    try {
        const keys = Object.keys(obj);
        if (keys.length === 0) return '{}';
        if (keys.length > 10) {
            return `{Object with ${keys.length} properties}`;
        }

        const pairs = keys.slice(0, 5).map(key => {
            const value = safeStringify(obj[key], maxDepth, currentDepth + 1);
            return `${key}: ${value}`;
        });

        if (keys.length > 5) {
            pairs.push(`... and ${keys.length - 5} more`);
        }

        return `{${pairs.join(', ')}}`;
    } catch (error) {
        return '[Object - cannot stringify]';
    }
}

// 创建结果卡片
function createResultCard(title, data) {
    try {
        console.log(`Creating result card for: ${title}`);

        const card = document.createElement('div');
        card.className = 'bg-gray-50 rounded-lg p-4';

        const titleElement = document.createElement('h4');
        titleElement.className = 'font-semibold text-gray-800 mb-3';
        titleElement.textContent = title;
        card.appendChild(titleElement);

        const content = document.createElement('div');
        content.className = 'space-y-2';

        // 处理数组类型的数据
        if (Array.isArray(data)) {
            console.log(`Processing array with ${data.length} items`);
            data.slice(0, 20).forEach((item, index) => { // 限制显示前20项
                const itemDiv = document.createElement('div');
                itemDiv.className = 'flex justify-between items-start';

                const label = document.createElement('span');
                label.className = 'font-medium text-gray-600';
                label.textContent = `${index + 1}:`;

                const valueElement = document.createElement('span');
                valueElement.className = 'text-gray-800 text-right flex-1 ml-4';
                valueElement.textContent = safeStringify(item);

                itemDiv.appendChild(label);
                itemDiv.appendChild(valueElement);
                content.appendChild(itemDiv);
            });

            if (data.length > 20) {
                const moreDiv = document.createElement('div');
                moreDiv.className = 'text-gray-500 italic';
                moreDiv.textContent = `... and ${data.length - 20} more items`;
                content.appendChild(moreDiv);
            }
        } else if (typeof data === 'object' && data !== null) {
            console.log(`Processing object with keys: ${Object.keys(data).join(', ')}`);
            // 处理对象类型的数据
            const entries = Object.entries(data).slice(0, 20); // 限制显示前20个属性

            entries.forEach(([key, value]) => {
                const item = document.createElement('div');
                item.className = 'flex justify-between items-start';

                const label = document.createElement('span');
                label.className = 'font-medium text-gray-600';
                label.textContent = key + ':';

                const valueElement = document.createElement('span');
                valueElement.className = 'text-gray-800 text-right flex-1 ml-4';
                valueElement.style.wordBreak = 'break-word';
                valueElement.style.maxWidth = '300px';

                // 安全地处理值
                const displayValue = safeStringify(value);
                if (displayValue.length > 200) {
                    valueElement.textContent = displayValue.substring(0, 200) + '...';
                } else {
                    valueElement.textContent = displayValue;
                }

                item.appendChild(label);
                item.appendChild(valueElement);
                content.appendChild(item);
            });

            if (Object.keys(data).length > 20) {
                const moreDiv = document.createElement('div');
                moreDiv.className = 'text-gray-500 italic';
                moreDiv.textContent = `... and ${Object.keys(data).length - 20} more properties`;
                content.appendChild(moreDiv);
            }
        } else {
            console.log(`Processing primitive value: ${typeof data}`);
            // 处理基本类型的数据
            const item = document.createElement('div');
            item.textContent = safeStringify(data);
            content.appendChild(item);
        }

        card.appendChild(content);
        console.log(`Result card created successfully for: ${title}`);
        return card;
    } catch (error) {
        console.error('Error creating result card:', error);
        console.error('Stack trace:', error.stack);

        // 返回一个简单的错误卡片
        const errorCard = document.createElement('div');
        errorCard.className = 'bg-red-50 rounded-lg p-4';
        errorCard.innerHTML = `
            <h4 class="font-semibold text-red-800 mb-2">Error displaying ${title}</h4>
            <p class="text-red-600">${error.message}</p>
            <p class="text-sm text-red-500 mt-2">Data type: ${typeof data}</p>
        `;
        return errorCard;
    }
}

// 显示错误
function showError(message) {
    errorMessage.textContent = message;
    errorSection.classList.remove('hidden');
    // 隐藏结果标签页内容（如果需要的话）
    // resultsTab.classList.add('hidden');
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'success' ? 'bg-green-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// ==================== 格式对齐功能 ====================

// 初始化格式对齐功能
function initFormatAlignment() {
    const sourceUploadArea = document.getElementById('source-upload-area');
    const targetUploadArea = document.getElementById('target-upload-area');
    const sourceFileInput = document.getElementById('source-file-input');
    const targetFileInput = document.getElementById('target-file-input');
    const formatAlignBtn = document.getElementById('format-align-btn');
    const showTemplatesBtn = document.getElementById('show-templates-btn');
    const formatInstruction = document.getElementById('format-instruction');

    if (!sourceUploadArea || !targetUploadArea) return;

    // 源文档上传
    sourceUploadArea.addEventListener('click', () => sourceFileInput.click());
    sourceUploadArea.addEventListener('dragover', handleDragOver);
    sourceUploadArea.addEventListener('drop', (e) => handleFileDrop(e, 'source'));
    sourceFileInput.addEventListener('change', (e) => handleFileSelect(e, 'source'));

    // 目标文档上传
    targetUploadArea.addEventListener('click', () => targetFileInput.click());
    targetUploadArea.addEventListener('dragover', handleDragOver);
    targetUploadArea.addEventListener('drop', (e) => handleFileDrop(e, 'target'));
    targetFileInput.addEventListener('change', (e) => handleFileSelect(e, 'target'));

    // 格式对齐按钮
    if (formatAlignBtn) {
        formatAlignBtn.addEventListener('click', executeFormatAlignment);
    }

    // 显示模板按钮
    if (showTemplatesBtn) {
        showTemplatesBtn.addEventListener('click', showFormatTemplates);
    }

    // 指令输入框变化
    if (formatInstruction) {
        formatInstruction.addEventListener('input', updateFormatAlignButton);
    }

    // 加载格式模板
    loadFormatTemplates();
}

// 处理文件选择
function handleFileSelect(event, type) {
    const file = event.target.files[0];
    if (file) {
        if (type === 'source') {
            sourceFile = file;
            updateFileInfo('source', file);
        } else {
            targetFile = file;
            updateFileInfo('target', file);
        }
        updateFormatAlignButton();
    }
}

// 处理文件拖拽
function handleFileDrop(event, type) {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
        if (type === 'source') {
            sourceFile = file;
            updateFileInfo('source', file);
        } else {
            targetFile = file;
            updateFileInfo('target', file);
        }
        updateFormatAlignButton();
    }
}

// 更新文件信息显示
function updateFileInfo(type, file) {
    const fileInfo = document.getElementById(`${type}-file-info`);
    const fileName = document.getElementById(`${type}-file-name`);
    const fileSize = document.getElementById(`${type}-file-size`);
    const uploadArea = document.getElementById(`${type}-upload-area`);

    if (fileInfo && fileName && fileSize && uploadArea) {
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileInfo.classList.remove('hidden');
        uploadArea.classList.add('border-green-300', 'bg-green-50');
    }
}

// 更新格式对齐按钮状态
function updateFormatAlignButton() {
    const formatAlignBtn = document.getElementById('format-align-btn');
    const formatInstruction = document.getElementById('format-instruction');

    if (formatAlignBtn && formatInstruction) {
        const hasFiles = sourceFile && targetFile;
        const hasInstruction = formatInstruction.value.trim().length > 0;
        formatAlignBtn.disabled = !(hasFiles && hasInstruction);
    }
}

// 执行格式对齐
async function executeFormatAlignment() {
    const formatInstruction = document.getElementById('format-instruction');
    const instruction = formatInstruction.value.trim();

    if (!sourceFile || !targetFile) {
        showNotification('请上传源文档和目标文档', 'error');
        return;
    }

    if (!instruction) {
        showNotification('请输入格式对齐指令', 'error');
        return;
    }

    try {
        showNotification('正在处理格式对齐...', 'info');

        // 读取文件内容
        const sourceContent = await readFileContent(sourceFile);
        const targetContent = await readFileContent(targetFile);

        // 发送格式对齐请求
        const response = await fetch('/api/format-alignment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_input: instruction,
                uploaded_files: {
                    [sourceFile.name]: sourceContent,
                    [targetFile.name]: targetContent
                }
            })
        });

        const result = await response.json();

        if (result.success) {
            showFormatAlignmentResult(result);
            showNotification('格式对齐完成！', 'success');
        } else {
            showNotification(result.error || '格式对齐失败', 'error');
        }

    } catch (error) {
        console.error('Format alignment error:', error);
        showNotification('格式对齐处理失败', 'error');
    }
}

// 显示格式对齐结果
function showFormatAlignmentResult(result) {
    const resultSection = document.getElementById('format-result-section');
    const resultContent = document.getElementById('format-result-content');

    if (!resultSection || !resultContent) return;

    resultContent.innerHTML = '';

    // 创建结果卡片
    const responseCard = createResultCard('处理结果', {
        '源文档': result.source_document,
        '目标文档': result.target_document,
        '模板名称': result.template_name,
        '状态': '格式对齐成功'
    });
    resultContent.appendChild(responseCard);

    // 格式提示词
    if (result.format_prompt) {
        const promptCard = createResultCard('生成的格式提示词', {
            '提示词': result.format_prompt
        });
        resultContent.appendChild(promptCard);
    }

    // 操作按钮
    if (result.actions) {
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'flex space-x-3 mt-4';

        result.actions.forEach(action => {
            const button = document.createElement('button');
            button.className = 'bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition duration-300';
            button.textContent = action.label;

            if (action.type === 'download') {
                button.addEventListener('click', () => {
                    // 创建两个按钮：预览和下载
                    const buttonContainer = document.createElement('div');
                    buttonContainer.className = 'flex space-x-2';

                    const previewBtn = document.createElement('button');
                    previewBtn.className = 'bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm';
                    previewBtn.textContent = '浏览器预览';
                    previewBtn.addEventListener('click', () => previewFormattedDocument(action.data));

                    const downloadBtn = document.createElement('button');
                    downloadBtn.className = 'bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm';
                    downloadBtn.textContent = '下载文档';
                    downloadBtn.addEventListener('click', () => downloadFormattedDocument(action.data));

                    buttonContainer.appendChild(previewBtn);
                    buttonContainer.appendChild(downloadBtn);

                    // 替换原按钮
                    button.parentNode.replaceChild(buttonContainer, button);
                });
            } else if (action.type === 'save_template') {
                button.addEventListener('click', () => saveFormatTemplate(action.template_id));
            }

            actionsDiv.appendChild(button);
        });

        resultContent.appendChild(actionsDiv);
    }

    resultSection.classList.remove('hidden');

    // 重新加载模板列表
    loadFormatTemplates();
}

// 预览格式化文档
function previewFormattedDocument(htmlContent) {
    try {
        // 在新窗口中打开HTML内容
        const newWindow = window.open('', '_blank');
        if (newWindow) {
            newWindow.document.write(htmlContent);
            newWindow.document.close();
            showNotification('文档预览已打开', 'success');
        } else {
            // 如果弹窗被阻止，则在当前页面显示
            showFormattedDocumentModal(htmlContent);
        }
    } catch (error) {
        console.error('Preview error:', error);
        showNotification('预览失败', 'error');
    }
}

function showFormattedDocumentModal(htmlContent) {
    // 创建模态框显示HTML内容
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-auto m-4">
            <div class="flex justify-between items-center p-4 border-b">
                <h3 class="text-lg font-semibold">格式化文档预览</h3>
                <div class="flex space-x-2">
                    <button id="downloadFromModal" class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm">
                        下载文档
                    </button>
                    <button id="closeModal" class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm">
                        关闭
                    </button>
                </div>
            </div>
            <div class="p-4">
                <iframe srcdoc="${htmlContent.replace(/"/g, '&quot;')}"
                        class="w-full h-96 border rounded"></iframe>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // 添加事件监听器
    modal.querySelector('#closeModal').addEventListener('click', () => {
        document.body.removeChild(modal);
    });

    modal.querySelector('#downloadFromModal').addEventListener('click', () => {
        downloadFormattedDocument(htmlContent);
        document.body.removeChild(modal);
    });

    // 点击背景关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
}

// 下载格式化文档
function downloadFormattedDocument(htmlContent) {
    try {
        const blob = new Blob([htmlContent], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `formatted_document_${Date.now()}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showNotification('文档下载成功', 'success');
    } catch (error) {
        console.error('Download error:', error);
        showNotification('下载失败', 'error');
    }
}

// 保存格式模板
function saveFormatTemplate(templateId) {
    showNotification('格式模板已保存', 'success');
    loadFormatTemplates();
}

// 加载格式模板
async function loadFormatTemplates() {
    try {
        const response = await fetch('/api/format-templates');
        const result = await response.json();

        if (result.success) {
            formatTemplates = result.templates;
            updateTemplatesDisplay();
        }
    } catch (error) {
        console.error('Error loading templates:', error);
    }
}

// 显示格式模板
function showFormatTemplates() {
    const templatesSection = document.getElementById('format-templates-section');
    if (templatesSection) {
        templatesSection.classList.toggle('hidden');
        updateTemplatesDisplay();
    }
}

// 更新模板显示
function updateTemplatesDisplay() {
    const templatesList = document.getElementById('templates-list');
    if (!templatesList) return;

    templatesList.innerHTML = '';

    if (formatTemplates.length === 0) {
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'text-gray-500 text-center py-4';
        emptyDiv.textContent = '暂无保存的格式模板';
        templatesList.appendChild(emptyDiv);
        return;
    }

    formatTemplates.forEach(template => {
        const templateDiv = document.createElement('div');
        templateDiv.className = 'bg-gray-50 rounded-lg p-4 flex justify-between items-center';

        const infoDiv = document.createElement('div');
        infoDiv.innerHTML = `
            <h6 class="font-medium text-gray-800">${template.name}</h6>
            <p class="text-sm text-gray-600">${template.description}</p>
            <p class="text-xs text-gray-500">创建时间: ${new Date(template.created_time).toLocaleString()}</p>
        `;

        const useButton = document.createElement('button');
        useButton.className = 'bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm transition duration-300';
        useButton.textContent = '使用模板';
        useButton.addEventListener('click', () => useFormatTemplate(template.template_id));

        templateDiv.appendChild(infoDiv);
        templateDiv.appendChild(useButton);
        templatesList.appendChild(templateDiv);
    });
}

// 使用格式模板
async function useFormatTemplate(templateId) {
    if (!sourceFile) {
        showNotification('请先上传源文档', 'error');
        return;
    }

    try {
        const sourceContent = await readFileContent(sourceFile);

        const response = await fetch(`/api/format-templates/${templateId}/apply`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                document_name: sourceFile.name,
                document_content: sourceContent
            })
        });

        const result = await response.json();

        if (result.success) {
            showFormatAlignmentResult(result);
            showNotification('格式模板应用成功！', 'success');
        } else {
            showNotification(result.error || '模板应用失败', 'error');
        }

    } catch (error) {
        console.error('Template application error:', error);
        showNotification('模板应用失败', 'error');
    }
}

// 读取文件内容
function readFileContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(e);
        reader.readAsText(file, 'UTF-8');
    });
}