/**
 * Document-Fill
 * 
 * @author AI Assistant (Claude)
 * @date 2025-01-28
 * @ai_assisted 是 - Claude 3.5 Sonnet
 * @version v1.0
 * @license MIT
 */


class DocumentFillManager {
    constructor() {
        this.currentSession = null;
        this.uploadedMaterials = [];
        this.selectedStyleTemplate = null;
        this.conversationHistory = [];
        this.fillProgress = { current: 0, total: 0 };
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // 文档上传
        const fillFileInput = document.getElementById('fill-file-input');
        const fillUploadArea = document.getElementById('fill-upload-area');

        console.log('Initializing document fill listeners...');
        console.log('fillFileInput:', fillFileInput);
        console.log('fillUploadArea:', fillUploadArea);

        fillUploadArea = document.getElementById('fill-upload-area');
        if (fillUploadArea) {
             fillUploadArea.className = 'upload-area rounded-lg p-8 text-center cursor-pointer border-2 border-dashed border-gray-300';
           }

        if (fillFileInput && fillUploadArea) {
            fillUploadArea.addEventListener('click', () => {
                console.log('Upload area clicked');
                fillFileInput.click();
            });
            fillUploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
            fillUploadArea.addEventListener('drop', this.handleFileDrop.bind(this));
            fillFileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                this.currentFile = file || null;
            });
            console.log('Event listeners added successfully');
        } else {
            console.error('Failed to find upload elements');
        }

        // 开始分析按钮
        const startFillBtn = document.getElementById('start-fill-btn');
        if (startFillBtn) {
            startFillBtn.addEventListener('click', this.startDocumentAnalysis.bind(this));
        }

        // 补充材料上传
        const materialFileInput = document.getElementById('material-file-input');
        const materialUploadArea = document.getElementById('material-upload-area');
        
        if (materialFileInput && materialUploadArea) {
            materialUploadArea.addEventListener('click', () => materialFileInput.click());
            materialFileInput.addEventListener('change', (e) => {
                const files = Array.from(e.target.files);
                files.forEach(file => this.uploadedMaterials.push(file));
            });
        }

        // 继续按钮
        const continueWithoutMaterials = document.getElementById('continue-without-materials');
        const continueWithMaterials = document.getElementById('continue-with-materials');
        
        if (continueWithoutMaterials) {
            continueWithoutMaterials.addEventListener('click', () => this.showWritingStyleSection());
        }
        if (continueWithMaterials) {
            continueWithMaterials.addEventListener('click', () => this.showWritingStyleSection());
        }

        // 文风设置
        const skipStyleSetting = document.getElementById('skip-style-setting');
        const startConversation = document.getElementById('start-conversation');
        
        if (skipStyleSetting) {
            skipStyleSetting.addEventListener('click', () => this.startConversation());
        }
        if (startConversation) {
            startConversation.addEventListener('click', () => this.startConversation());
        }

        // 对话功能
        const sendMessage = document.getElementById('send-message');
        const userInput = document.getElementById('user-input');
        
        if (sendMessage) {
            sendMessage.addEventListener('click', this.sendUserMessage.bind(this));
        }
        if (userInput) {
            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendUserMessage();
                }
            });
        }

        // 下载和重新开始
        const downloadBtn = document.getElementById('download-filled-doc');
        const restartBtn = document.getElementById('restart-fill');
        
        if (downloadBtn) {
            downloadBtn.addEventListener('click', this.downloadFilledDocument.bind(this));
        }
        if (restartBtn) {
            restartBtn.addEventListener('click', this.restartFillProcess.bind(this));
        }
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleFileDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }

    processFile(file) {
        // 显示文件信息
        const fileInfo = document.getElementById('fill-file-info');
        const fileName = document.getElementById('fill-file-name');
        const fileSize = document.getElementById('fill-file-size');
        
        if (fileInfo && fileName && fileSize) {
            fileName.textContent = file.name;
            fileSize.textContent = this.formatFileSize(file.size);
            fileInfo.classList.remove('hidden');
        }

        // 隐藏上传区域
        const uploadArea = document.getElementById('fill-upload-area');
        if (uploadArea) {
            uploadArea.style.display = 'none';
        }

        this.currentFile = file;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function readFileContentAsync(file, callback) {
        const reader = new FileReader();
        reader.onload = function(e) { callback(e.target.result); };
        reader.onerror = function() { showMessage('文件读取失败', 'error'); callback(null); };
        reader.readAsText(file);
    }

    async function startDocumentFill() {
        if (!this.currentFile) {
            showMessage('请先上传主文档', 'error');
            return;
        }
        readFileContentAsync(this.currentFile, async (content) => {
            if (!content || content.trim() === '') {
                showMessage('主文档内容为空', 'error');
                return;
            }
            try {
                showLoading('正在分析文档结构...');
                const response = await fetch('/api/document-fill/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ document_content: content, document_name: this.currentFile.name })
                });
                const result = await response.json();
                if (result.error) {
                    showMessage(result.error, 'error');
                } else {
                    // 处理AI提问等
                }
            } catch (err) {
                showMessage('API调用失败: ' + err.message, 'error');
            } finally {
                hideLoading();
            }
        });
    }

    showSupplementaryMaterialsSection() {
        const section = document.getElementById('supplementary-materials-section');
        if (section) {
            section.classList.remove('hidden');
            section.scrollIntoView({ behavior: 'smooth' });
        }
    }

    handleMaterialUpload(e) {
        const files = Array.from(e.target.files);
        files.forEach(file => this.addMaterial(file));
    }

    async addMaterial(file) {
        const materialsList = document.getElementById('materials-list');
        if (!materialsList) return;

        const materialItem = document.createElement('div');
        materialItem.className = 'material-item flex items-center justify-between p-3 bg-gray-50 rounded-lg border';
        
        const content = await this.readFileContent(file);
        
        materialItem.innerHTML = `
            <div class="flex items-center space-x-3">
                <i class="fas fa-file-alt text-blue-500"></i>
                <div>
                    <p class="font-medium text-gray-800">${file.name}</p>
                    <p class="text-sm text-gray-600">${this.formatFileSize(file.size)}</p>
                </div>
            </div>
            <button class="text-red-500 hover:text-red-700" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        materialsList.appendChild(materialItem);
        
        // 添加到材料列表
        this.uploadedMaterials.push({
            name: file.name,
            content: content,
            size: file.size
        });

        // 启用继续按钮
        const continueBtn = document.getElementById('continue-with-materials');
        if (continueBtn) {
            continueBtn.disabled = false;
        }

        // 上传到服务器
        try {
            await fetch('/api/document-fill/add-material', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    material_name: file.name,
                    material_content: content
                })
            });
        } catch (error) {
            console.error('上传补充材料失败:', error);
        }
    }

    showWritingStyleSection() {
        const section = document.getElementById('writing-style-section');
        if (section) {
            section.classList.remove('hidden');
            section.scrollIntoView({ behavior: 'smooth' });
        }
        
        // 加载文风模板列表
        this.loadStyleTemplates();
    }

    async loadStyleTemplates() {
        try {
            const response = await fetch('/api/writing-style/templates');
            const result = await response.json();
            
            if (result.success) {
                this.displayStyleTemplates(result.templates);
            }
        } catch (error) {
            console.error('加载文风模板失败:', error);
        }
    }

    displayStyleTemplates(templates) {
        const templatesList = document.getElementById('style-templates-list');
        if (!templatesList) return;

        templatesList.innerHTML = '';

        if (templates.length === 0) {
            templatesList.innerHTML = '<p class="text-gray-500 text-sm">暂无保存的文风模板</p>';
            return;
        }

        templates.forEach(template => {
            const templateItem = document.createElement('div');
            templateItem.className = 'style-template-item p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer';
            templateItem.innerHTML = `
                <div class="flex items-center justify-between">
                    <div>
                        <p class="font-medium text-gray-800">${template.name}</p>
                        <p class="text-sm text-gray-600">${template.style_name}</p>
                    </div>
                    <div class="text-right">
                        <p class="text-sm text-blue-600">${(template.confidence_score * 100).toFixed(1)}%</p>
                        <p class="text-xs text-gray-500">${template.created_time ? template.created_time.split('T')[0] : ''}</p>
                    </div>
                </div>
            `;
            
            templateItem.addEventListener('click', () => {
                // 移除其他选中状态
                document.querySelectorAll('.style-template-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                // 添加选中状态
                templateItem.classList.add('selected');
                this.selectedStyleTemplate = template.template_id;
            });
            
            templatesList.appendChild(templateItem);
        });
    }

    async startConversation() {
        // 设置文风模板
        if (this.selectedStyleTemplate) {
            try {
                await fetch('/api/document-fill/set-style', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        template_id: this.selectedStyleTemplate
                    })
                });
            } catch (error) {
                console.error('设置文风模板失败:', error);
            }
        }

        // 显示AI思考提示
        this.showAIThinkingMessage('🤖 AI助手正在准备对话...');

        // 显示对话区域
        const section = document.getElementById('conversation-section');
        if (section) {
            section.classList.remove('hidden');
            section.scrollIntoView({ behavior: 'smooth' });
        }

        // 显示初始消息
        if (this.currentSession && this.currentSession.response) {
            this.hideAIThinkingMessage();
            this.addMessageToHistory('assistant', this.currentSession.response);
            this.updateProgress(this.currentSession.current_question || 1, this.currentSession.total_questions || 1);
        }
    }

    // 显示AI思考提示
    showAIThinkingMessage(message = '🧠 文思泉涌中...') {
        let aiThinkingContainer = document.getElementById('ai-thinking-container');
        if (!aiThinkingContainer) {
            aiThinkingContainer = document.createElement('div');
            aiThinkingContainer.id = 'ai-thinking-container';
            aiThinkingContainer.className = 'ai-thinking-overlay';
            document.body.appendChild(aiThinkingContainer);
        }

        const thinkingMessages = [
            "🧠 文思泉涌中，正在为您精心撰写...",
            "✨ 灵感迸发中，让AI为您妙笔生花...",
            "🎨 创意流淌中，正在雕琢完美内容...",
            "🌟 智慧汇聚中，为您呈现专业佳作...",
            "💫 才思敏捷中，正在谱写精彩篇章...",
            "🎯 匠心独运中，为您打造精品内容...",
            "🌈 妙笔生花中，正在创作专业文档...",
            "🚀 思维飞扬中，为您呈现完美答卷..."
        ];

        const randomMessage = thinkingMessages[Math.floor(Math.random() * thinkingMessages.length)];

        aiThinkingContainer.innerHTML = `
            <div class="ai-thinking-content">
                <div class="ai-thinking-icon">
                    <div class="thinking-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
                <div class="ai-thinking-text">
                    <h3>🤖 AI智能写作助手</h3>
                    <p>${randomMessage}</p>
                    <div class="ai-thinking-progress">
                        <div class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                        <span class="progress-text">正在生成中...</span>
                    </div>
                </div>
            </div>
        `;

        aiThinkingContainer.style.display = 'flex';
        this.startProgressAnimation();
        this.startMessageRotation(aiThinkingContainer, thinkingMessages);
    }

    // 隐藏AI思考提示
    hideAIThinkingMessage() {
        const aiThinkingContainer = document.getElementById('ai-thinking-container');
        if (aiThinkingContainer) {
            aiThinkingContainer.style.display = 'none';
        }
    }

    // 启动进度条动画
    startProgressAnimation() {
        const progressFill = document.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = '0%';
            progressFill.style.transition = 'width 0.5s ease-in-out';
            
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15 + 5;
                if (progress >= 90) {
                    progress = 90;
                    clearInterval(interval);
                }
                progressFill.style.width = progress + '%';
            }, 800);
        }
    }

    // 启动消息轮换
    startMessageRotation(container, messages) {
        let currentIndex = 0;
        const messageElement = container.querySelector('.ai-thinking-text p');
        
        const interval = setInterval(() => {
            currentIndex = (currentIndex + 1) % messages.length;
            messageElement.style.opacity = '0';
            
            setTimeout(() => {
                messageElement.textContent = messages[currentIndex];
                messageElement.style.opacity = '1';
            }, 300);
        }, 3000);
        
        container.dataset.messageInterval = interval;
    }

    addMessageToHistory(sender, message) {
        const history = document.getElementById('conversation-history');
        if (!history) return;

        // 如果是第一条消息，清空占位符
        const placeholder = history.querySelector('.text-center');
        if (placeholder) {
            placeholder.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message-bubble p-3 mb-3 ${sender === 'user' ? 'message-user' : 'message-assistant'}`;
        
        const messageContent = document.createElement('div');
        messageContent.innerHTML = this.formatMessage(message);
        messageDiv.appendChild(messageContent);

        if (sender === 'assistant') {
            const avatar = document.createElement('div');
            avatar.className = 'flex items-center mb-2';
            avatar.innerHTML = '<i class="fas fa-robot text-blue-500 mr-2"></i><span class="text-sm font-medium text-gray-600">AI助手</span>';
            messageDiv.insertBefore(avatar, messageContent);
        }

        history.appendChild(messageDiv);
        history.scrollTop = history.scrollHeight;
    }

    formatMessage(message) {
        // 简单的消息格式化
        return message.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    async sendUserMessage() {
        const userInput = document.getElementById('user-input');
        const message = userInput.value.trim();
        
        if (!message) return;
        
        // 添加用户消息到历史记录
        this.addMessageToHistory('user', message);
        
        // 清空输入框
        userInput.value = '';
        
        // 显示AI思考提示
        this.showAIThinkingMessage('🤖 AI正在思考您的回复...');
        
        try {
            const response = await fetch('/api/document-fill/respond', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_input: message
                })
            });
            
            const result = await response.json();
            
            // 隐藏AI思考提示
            this.hideAIThinkingMessage();
            
            if (result.error) {
                this.addMessageToHistory('assistant', `❌ 错误: ${result.error}`);
                return;
            }
            
            // 添加AI回复到历史记录
            this.addMessageToHistory('assistant', result.response);
            
            // 更新进度
            if (result.current_question && result.total_questions) {
                this.updateProgress(result.current_question, result.total_questions);
            }
            
            // 如果填充完成，显示结果
            if (result.stage === 'completed') {
                this.showFillResult(result);
            }
            
        } catch (error) {
            this.hideAIThinkingMessage();
            console.error('发送消息失败:', error);
            this.addMessageToHistory('assistant', '❌ 网络错误，请重试');
        }
    }

    updateProgress(current, total) {
        const progressText = document.getElementById('progress-text');
        const progressBar = document.getElementById('fill-progress-bar');
        
        if (progressText) {
            progressText.textContent = `${current}/${total}`;
        }
        
        if (progressBar) {
            const percentage = (current / total) * 100;
            progressBar.style.width = `${percentage}%`;
        }
    }

    async showFillResult(result) {
        // 隐藏对话区域
        const conversationSection = document.getElementById('conversation-section');
        if (conversationSection) {
            conversationSection.classList.add('hidden');
        }

        // 显示结果区域
        const resultSection = document.getElementById('fill-result-section');
        if (resultSection) {
            resultSection.classList.remove('hidden');
            resultSection.scrollIntoView({ behavior: 'smooth' });
        }

        // 获取填充结果
        try {
            const response = await fetch('/api/document-fill/result');
            const fillResult = await response.json();
            
            if (fillResult.success) {
                this.displayFillResult(fillResult.result);
            }
        } catch (error) {
            console.error('获取填充结果失败:', error);
        }
    }

    displayFillResult(result) {
        const resultContent = document.getElementById('fill-result-content');
        if (!resultContent) return;

        const summary = result.fill_summary || {};
        
        resultContent.innerHTML = `
            <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <h6 class="font-semibold text-green-800 mb-2">填充完成！</h6>
                <div class="grid md:grid-cols-3 gap-4 text-sm">
                    <div>
                        <span class="text-green-600">总字段数：</span>
                        <span class="font-medium">${summary.total_fields || 0}</span>
                    </div>
                    <div>
                        <span class="text-green-600">已填充：</span>
                        <span class="font-medium">${summary.filled_fields || 0}</span>
                    </div>
                    <div>
                        <span class="text-green-600">完成度：</span>
                        <span class="font-medium">${(summary.completion_rate || 0).toFixed(1)}%</span>
                    </div>
                </div>
            </div>
            <div class="bg-gray-50 rounded-lg p-4">
                <h6 class="font-semibold text-gray-800 mb-2">文档预览</h6>
                <div class="bg-white border rounded p-4 max-h-64 overflow-y-auto">
                    ${result.html_content ? result.html_content.substring(0, 500) + '...' : '文档内容生成中...'}
                </div>
            </div>
        `;
    }

    async downloadFilledDocument() {
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
            } else {
                this.showError('下载失败');
            }
        } catch (error) {
            this.showError('下载失败: ' + error.message);
        }
    }

    restartFillProcess() {
        // 重置状态
        this.currentSession = null;
        this.uploadedMaterials = [];
        this.selectedStyleTemplate = null;
        this.conversationHistory = [];
        this.fillProgress = { current: 0, total: 0 };

        // 隐藏所有区域
        const sections = [
            'supplementary-materials-section',
            'writing-style-section', 
            'conversation-section',
            'fill-result-section'
        ];
        
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                section.classList.add('hidden');
            }
        });

        // 重置文件上传区域
        const uploadArea = document.getElementById('fill-upload-area');
        const fileInfo = document.getElementById('fill-file-info');
        
        if (uploadArea) {
            uploadArea.style.display = 'block';
        }
        if (fileInfo) {
            fileInfo.classList.add('hidden');
        }

        // 清空文件输入
        const fileInput = document.getElementById('fill-file-input');
        if (fileInput) {
            fileInput.value = '';
        }

        this.currentFile = null;
    }

    showLoading(message = '处理中...') {
        // 实现加载状态显示
        console.log('Loading:', message);
    }

    hideLoading() {
        // 实现隐藏加载状态
        console.log('Loading hidden');
    }

    showError(message) {
        // 实现错误消息显示
        alert('错误: ' + message);
    }
}

// 初始化文档填充管理器
document.addEventListener('DOMContentLoaded', () => {
    window.documentFillManager = new DocumentFillManager();
});
