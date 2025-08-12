/**
 * Enhanced-Frontend-Complete
 * 
 * @author AI Assistant (Claude)
 * @date 2025-01-28
 * @ai_assisted 是 - Claude 3.5 Sonnet
 * @version v1.0
 * @license MIT
 */


// ==================== 全局应用状态管理 ====================
class AppState {
    constructor() {
        this.currentSession = null;
        this.currentScene = 'format';
        this.uploadedFiles = new Map();
        this.processingStatus = new Map();
        this.errorHistory = [];
        this.userPreferences = {
            autoSave: true,
            showPreview: true,
            enableNotifications: true,
            language: 'zh-CN'
        };
        this.sessionHistory = [];
        this.currentStep = 1;
        this.maxSteps = 4;
    }

    createSession(sceneType) {
        const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.currentSession = {
            id: sessionId,
            type: sceneType,
            createdAt: new Date(),
            status: 'initialized',
            files: [],
            operations: [],
            results: {},
            currentStep: 1,
            completedSteps: []
        };
        this.sessionHistory.push(this.currentSession);
        return sessionId;
    }

    updateSession(sessionId, status, data = {}) {
        const session = this.sessionHistory.find(s => s.id === sessionId);
        if (session) {
            session.status = status;
            session.lastUpdated = new Date();
            Object.assign(session.results, data);
        }
    }

    addFileToSession(sessionId, file, fileType) {
        const session = this.sessionHistory.find(s => s.id === sessionId);
        if (session) {
            const fileInfo = {
                name: file.name,
                size: file.size,
                type: file.type,
                fileType: fileType,
                uploadedAt: new Date(),
                id: `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
            };
            session.files.push(fileInfo);
            this.uploadedFiles.set(fileInfo.id, file);
        }
    }

    logError(error, context) {
        this.errorHistory.push({
            timestamp: new Date(),
            message: error.message,
            stack: error.stack,
            context: context
        });
    }

    updateStep(step) {
        this.currentStep = step;
        if (this.currentSession) {
            this.currentSession.currentStep = step;
            if (!this.currentSession.completedSteps.includes(step - 1) && step > 1) {
                this.currentSession.completedSteps.push(step - 1);
            }
        }
    }

    getCurrentSessionId() {
        return this.currentSession ? this.currentSession.id : null;
    }
}

// ==================== 文件验证和预处理 ====================
class FileValidator {
    constructor() {
        this.supportedFormats = {
            document: ['.docx', '.doc', '.txt', '.rtf', '.pdf'],
            image: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            spreadsheet: ['.xlsx', '.xls', '.csv'],
            presentation: ['.pptx', '.ppt'],
            format_alignment: ['.txt'], // 格式对齐模块专用：只支持TXT
            document_review: ['.txt']   // 文档审查模块专用：只支持TXT
        };
        this.maxFileSize = 50 * 1024 * 1024; // 50MB
        this.minFileSize = 1; // 1 byte
    }

    validateFile(file, expectedType = 'document') {
        const result = {
            isValid: true,
            errors: [],
            warnings: [],
            fileType: this.detectFileType(file)
        };

        // 检查文件大小
        if (file.size > this.maxFileSize) {
            result.isValid = false;
            result.errors.push(`文件大小超过限制 (${this.maxFileSize / 1024 / 1024}MB)`);
        }

        if (file.size < this.minFileSize) {
            result.isValid = false;
            result.errors.push('文件为空或损坏');
        }

        // 检查文件格式
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        const supportedFormats = this.supportedFormats[expectedType] || this.supportedFormats.document;
        
        if (!supportedFormats.includes(extension)) {
            result.isValid = false;
            result.errors.push(`不支持的文件格式: ${extension}`);
        }

        // 检查文件名
        if (file.name.length > 255) {
            result.warnings.push('文件名过长，建议缩短');
        }

        // 检查文件名中的特殊字符
        const invalidChars = /[<>:"/\\|?*]/;
        if (invalidChars.test(file.name)) {
            result.warnings.push('文件名包含特殊字符，建议修改');
        }

        return result;
    }

    detectFileType(file) {
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        
        for (const [type, extensions] of Object.entries(this.supportedFormats)) {
            if (extensions.includes(extension)) {
                return type;
            }
        }
        return 'unknown';
    }

    async preprocessFile(file) {
        const result = {
            success: true,
            data: null,
            errors: []
        };

        try {
            // 读取文件内容
            const content = await this.readFileContent(file);
            result.data = {
                name: file.name,
                size: file.size,
                type: file.type,
                content: content,
                lastModified: file.lastModified,
                fileType: this.detectFileType(file)
            };
        } catch (error) {
            result.success = false;
            result.errors.push(`文件读取失败: ${error.message}`);
        }

        return result;
    }

    readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('文件读取失败'));
            
            // 根据文件类型选择读取方式
            if (file.type.startsWith('text/') || file.type === 'application/json') {
                reader.readAsText(file);
            } else {
                reader.readAsArrayBuffer(file);
            }
        });
    }
}

// ==================== 文件上传管理器 ====================
class FileUploadManager {
    constructor() {
        this.uploadQueue = [];
        this.activeUploads = new Map();
        this.uploadCallbacks = new Map();
        this.maxConcurrentUploads = 3;
    }

    async uploadFile(file, endpoint, options = {}) {
        const uploadId = `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const uploadConfig = {
            id: uploadId,
            file: file,
            endpoint: endpoint,
            options: {
                timeout: 30000,
                retries: 3,
                ...options
            },
            status: 'pending',
            progress: 0,
            startTime: Date.now()
        };

        this.uploadQueue.push(uploadConfig);
        this.processUploadQueue();
        
        return new Promise((resolve, reject) => {
            this.uploadCallbacks.set(uploadId, { resolve, reject });
        });
    }

    async processUploadQueue() {
        const activeUploads = Array.from(this.activeUploads.values());
        
        if (activeUploads.length >= this.maxConcurrentUploads) {
            return;
        }

        const pendingUpload = this.uploadQueue.shift();
        if (!pendingUpload) {
            return;
        }

        this.activeUploads.set(pendingUpload.id, pendingUpload);
        await this.executeUpload(pendingUpload);
    }

    async executeUpload(uploadConfig) {
        try {
            uploadConfig.status = 'uploading';
            
            const formData = new FormData();
            formData.append('file', uploadConfig.file);
            
            // 添加额外的表单数据
            if (uploadConfig.options.formData) {
                Object.entries(uploadConfig.options.formData).forEach(([key, value]) => {
                    formData.append(key, value);
                });
            }

            const xhr = new XMLHttpRequest();
            
            // 设置进度监听
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const progress = (e.loaded / e.total) * 100;
                    this.updateUploadProgress(uploadConfig.id, progress);
                }
            });

            // 设置响应处理
            xhr.addEventListener('load', () => {
                this.handleUploadResponse(uploadConfig.id, xhr);
            });

            xhr.addEventListener('error', () => {
                this.handleUploadError(uploadConfig.id, new Error('网络错误'));
            });

            xhr.addEventListener('timeout', () => {
                this.handleUploadError(uploadConfig.id, new Error('上传超时'));
            });

            // 发送请求
            xhr.open('POST', uploadConfig.endpoint);
            xhr.timeout = uploadConfig.options.timeout;
            
            // 设置请求头
            if (uploadConfig.options.headers) {
                Object.entries(uploadConfig.options.headers).forEach(([key, value]) => {
                    xhr.setRequestHeader(key, value);
                });
            }

            xhr.send(formData);

        } catch (error) {
            this.handleUploadError(uploadConfig.id, error);
        }
    }

    handleUploadResponse(uploadId, xhr) {
        const uploadConfig = this.activeUploads.get(uploadId);
        if (!uploadConfig) return;

        uploadConfig.status = 'completed';
        uploadConfig.progress = 100;

        const callback = this.uploadCallbacks.get(uploadId);
        if (callback) {
            try {
                // 检查响应类型
                const contentType = xhr.getResponseHeader('Content-Type');
                let responseData;

                if (contentType && contentType.includes('application/json')) {
                    responseData = JSON.parse(xhr.responseText);
                } else if (contentType && contentType.includes('application/vnd.openxmlformats-officedocument.wordprocessingml.document')) {
                    // 处理docx文件响应
                    responseData = {
                        type: 'document',
                        content: xhr.response,
                        filename: this.extractFilenameFromHeaders(xhr)
                    };
                } else {
                    // 处理其他二进制响应
                    responseData = {
                        type: 'binary',
                        content: xhr.response,
                        contentType: contentType
                    };
                }

                callback.resolve(responseData);
            } catch (error) {
                callback.reject(new Error('响应解析失败'));
            }
        }

        this.activeUploads.delete(uploadId);
        this.uploadCallbacks.delete(uploadId);
        this.processUploadQueue();
    }

    handleUploadError(uploadId, error) {
        const uploadConfig = this.activeUploads.get(uploadId);
        if (uploadConfig) {
            uploadConfig.status = 'error';
            uploadConfig.error = error.message;
        }

        const callback = this.uploadCallbacks.get(uploadId);
        if (callback) {
            callback.reject(error);
        }

        this.activeUploads.delete(uploadId);
        this.uploadCallbacks.delete(uploadId);
        this.processUploadQueue();
    }

    updateUploadProgress(uploadId, progress) {
        const uploadConfig = this.activeUploads.get(uploadId);
        if (uploadConfig) {
            uploadConfig.progress = progress;
        }
    }

    extractFilenameFromHeaders(xhr) {
        const contentDisposition = xhr.getResponseHeader('Content-Disposition');
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (filenameMatch && filenameMatch[1]) {
                return filenameMatch[1].replace(/['"]/g, '');
            }
        }
        return 'document.docx';
    }
}

// ==================== 错误处理器 ====================
class ErrorHandler {
    constructor() {
        this.errorTypes = {
            NETWORK: 'network',
            VALIDATION: 'validation',
            PROCESSING: 'processing',
            AUTHENTICATION: 'authentication',
            PERMISSION: 'permission',
            SYSTEM: 'system'
        };
        
        this.errorMessages = {
            [this.errorTypes.NETWORK]: {
                zh: '网络连接错误，请检查网络设置',
                en: 'Network connection error, please check network settings'
            },
            [this.errorTypes.VALIDATION]: {
                zh: '文件格式或内容验证失败',
                en: 'File format or content validation failed'
            },
            [this.errorTypes.PROCESSING]: {
                zh: '文档处理过程中出现错误',
                en: 'Error occurred during document processing'
            },
            [this.errorTypes.AUTHENTICATION]: {
                zh: '身份验证失败，请重新登录',
                en: 'Authentication failed, please login again'
            },
            [this.errorTypes.PERMISSION]: {
                zh: '权限不足，无法执行此操作',
                en: 'Insufficient permissions to perform this operation'
            },
            [this.errorTypes.SYSTEM]: {
                zh: '系统错误，请稍后重试',
                en: 'System error, please try again later'
            }
        };
    }

    handleError(error, context, options = {}) {
        const errorInfo = {
            originalError: error,
            context: context,
            timestamp: new Date(),
            type: this.categorizeError(error),
            userMessage: this.getUserFriendlyMessage(error, context),
            severity: options.severity || 'error'
        };

        // 记录错误
        console.error('Error occurred:', errorInfo);

        // 显示用户友好的错误消息
        this.showErrorMessage(errorInfo.userMessage, errorInfo.severity);

        // 发送错误通知
        if (options.notify !== false) {
            this.notifyUser(errorInfo);
        }

        return errorInfo;
    }

    categorizeError(error) {
        if (error.name === 'NetworkError' || error.message.includes('network')) {
            return this.errorTypes.NETWORK;
        }
        if (error.name === 'ValidationError' || error.message.includes('validation')) {
            return this.errorTypes.VALIDATION;
        }
        if (error.name === 'ProcessingError' || error.message.includes('processing')) {
            return this.errorTypes.PROCESSING;
        }
        if (error.name === 'AuthenticationError' || error.message.includes('auth')) {
            return this.errorTypes.AUTHENTICATION;
        }
        if (error.name === 'PermissionError' || error.message.includes('permission')) {
            return this.errorTypes.PERMISSION;
        }
        return this.errorTypes.SYSTEM;
    }

    getUserFriendlyMessage(error, context) {
        const errorType = this.categorizeError(error);

        // 优先使用错误对象中的消息
        if (error && error.message) {
            return error.message;
        }

        const baseMessage = this.errorMessages[errorType].zh;

        // 根据上下文添加具体信息
        if (context === 'file_upload') {
            return `${baseMessage} - 文件上传失败`;
        }
        if (context === 'document_processing') {
            return `${baseMessage} - 文档处理失败`;
        }
        if (context === 'api_request') {
            return `${baseMessage} - API请求失败`;
        }
        if (context === 'preset_style_generation') {
            return `${baseMessage} - 预设风格生成失败`;
        }
        if (context === 'few_shot_transfer') {
            return `${baseMessage} - Few-Shot风格迁移失败`;
        }
        if (context === 'validation') {
            return error.message || `${baseMessage} - 输入验证失败`;
        }
        if (context === 'api') {
            return error.message || `${baseMessage} - API调用失败`;
        }
        if (context === 'file_reading') {
            return error.message || `${baseMessage} - 文件读取失败`;
        }
        if (context === 'content_validation') {
            return error.message || `${baseMessage} - 内容验证失败`;
        }
        if (context === 'style_processing') {
            return error.message || `${baseMessage} - 风格处理失败`;
        }

        return baseMessage;
    }

    showErrorMessage(message, type = 'error') {
        this.createNotification(message, type);
    }

    createNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        // 添加到通知容器
        const container = document.querySelector('.notification-container') || this.createNotificationContainer();
        container.appendChild(notification);

        // 自动移除通知
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);

        // 关闭按钮事件
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });
    }

    createNotificationContainer() {
        const container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
        return container;
    }

    getNotificationIcon(type) {
        const icons = {
            error: '❌',
            success: '✅',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    notifyUser(errorInfo) {
        // 可以在这里添加更多的通知方式，如声音、桌面通知等
        if (Notification.permission === 'granted') {
            new Notification('办公文档智能代理', {
                body: errorInfo.userMessage,
                icon: '/static/favicon.ico'
            });
        }
    }
}

// ==================== UI管理器 ====================
class UIManager {
    constructor() {
        this.currentScene = 'format';
        this.fileUploadAreas = new Map();
        this.progressBars = new Map();
        this.stepIndicators = new Map();
        this.modals = new Map();
    }

    initializeUI() {
        this.setupEventListeners();
        this.setupFileUploadAreas();
        this.setupProgressIndicators();
        this.setupStepNavigation();
        this.setupResponsiveDesign();
        this.setupNotifications();

        // AI文风统一界面将在切换到该场景时初始化
    }

    setupEventListeners() {
        // 导航事件
        document.querySelectorAll('.nav-item').forEach(item => {
            console.log('🔗 绑定导航事件:', item.getAttribute('data-scene'));
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const sceneId = item.getAttribute('data-scene');
                console.log('🎯 点击导航项:', sceneId);
                if (sceneId === 'dashboard') {
                    window.open('/dashboard', '_blank');
                    return;
                }
                this.switchScene(sceneId);
            });
        });

        // 按钮事件
        document.querySelectorAll('[data-action]').forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleButtonClick(e);
            });
        });

        // 表单提交事件
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        });

        // 模式切换事件 - 统一处理所有模块的模式切换
        this.setupModeSwitch();
    }

    setupModeSwitch() {
        // @AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: setup_mode_switch

        // 文风统一模块模式切换
        document.addEventListener('change', (e) => {
            if (e.target.name === 'style-mode') {
                console.log('🔄 文风统一模式切换（单选按钮）:', e.target.value);
                this.handleStyleModeSwitch(e.target.value);
            }
        });

        // 文风统一模块 - 点击整个模式选项卡片
        document.addEventListener('click', (e) => {
            const modeOption = e.target.closest('#scene-style .mode-option');
            if (modeOption) {
                const mode = modeOption.dataset.mode;
                console.log('📋 文风统一模式数据:', mode);

                // 获取当前模式（从单选按钮获取）
                const currentModeRadio = document.querySelector('#scene-style input[name="style-mode"]:checked');
                const currentMode = currentModeRadio ? currentModeRadio.value : null;
                console.log('📋 当前文风统一模式:', currentMode);

                const radioButton = modeOption.querySelector('input[type="radio"]');

                // 更新单选按钮状态
                if (radioButton) {
                    radioButton.checked = true;
                    console.log('✅ 单选按钮状态已更新');
                }

                // 总是执行模式切换和界面重置，确保界面状态正确
                console.log('🔄 通过点击卡片切换文风统一模式:', mode);
                this.handleStyleModeSwitch(mode);
            }
        });

        // 格式对齐模块的事件绑定已移至FormatAlignmentManager.bindEvents()中处理

        // 文档审查模块的模式切换已经在DocumentReviewManager中处理
    }

    handleStyleModeSwitch(mode) {
        // @AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: handle_style_mode_switch
        console.log('🔄 文风统一模式切换处理:', mode);

        // 重置界面状态 - 清理之前的处理结果
        this.resetStyleInterfaceState();

        const presetConfig = document.getElementById('style-preset-config');
        const fewShotConfig = document.getElementById('style-few-shot-config');

        // 添加平滑的显示/隐藏动画效果
        if (mode === 'preset') {
            // 显示预设配置，隐藏Few-Shot配置
            this.showBlockWithAnimation(presetConfig);
            this.hideBlockWithAnimation(fewShotConfig);
        } else if (mode === 'few-shot') {
            // 显示Few-Shot配置，隐藏预设配置
            this.showBlockWithAnimation(fewShotConfig);
            this.hideBlockWithAnimation(presetConfig);
        }

        // 更新模式选择的视觉状态
        this.updateStyleModeSelectionUI(mode);
    }

    resetStyleInterfaceState() {
        // @AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: reset_style_interface_state
        console.log('🔄 重置文风统一界面状态...');

        // 清理当前结果数据
        this.currentStyleResult = null;
        console.log('✅ 已清理结果数据');

        // 强制隐藏所有相关元素
        const elementsToHide = [
            'style-processing-area',
            'style-export-area',
            'style-completion-message'
        ];

        elementsToHide.forEach(elementId => {
            const element = document.getElementById(elementId);
            if (element) {
                element.style.display = 'none';
                element.style.visibility = 'hidden';
                element.classList.add('hidden');
                console.log(`✅ 已强制隐藏元素: ${elementId}`);
            } else {
                console.log(`⚠️ 未找到元素: ${elementId}`);
            }
        });

        // 清理进度条定时器
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
            console.log('✅ 已清理进度条定时器');
        }

        // 重置步骤导航到第一步
        this.navigateToStep(1);
        console.log('✅ 已重置步骤导航');

        // 额外检查：确保步骤指示器正确重置
        const stepItems = document.querySelectorAll('#scene-style .step-item');
        stepItems.forEach((item, index) => {
            item.classList.remove('active', 'completed');
            if (index === 0) {
                item.classList.add('active');
            }
        });
        console.log('✅ 已重置步骤指示器');

        console.log('✅ 文风统一界面状态重置完成');
    }

    updateStyleModeSelectionUI(mode) {
        // 更新文风统一模式选择的视觉状态和单选按钮状态
        console.log('🔄 更新文风统一模式选择UI:', mode);

        const modeOptions = document.querySelectorAll('#scene-style .mode-option');
        modeOptions.forEach(option => {
            const optionMode = option.dataset.mode;
            const radioButton = option.querySelector('input[type="radio"]');

            if (optionMode === mode) {
                // 选中状态
                option.classList.add('selected');
                if (radioButton) {
                    radioButton.checked = true;
                    console.log('✅ 设置文风统一单选按钮为选中:', optionMode);
                }
            } else {
                // 未选中状态
                option.classList.remove('selected');
                if (radioButton) {
                    radioButton.checked = false;
                    console.log('❌ 设置文风统一单选按钮为未选中:', optionMode);
                }
            }
        });
    }

    setupFileUploadAreas() {
        document.querySelectorAll('.file-upload-area').forEach(area => {
            const input = area.querySelector('input[type="file"]');
            if (input) {
                this.fileUploadAreas.set(area.id, { area, input });
                
                // 拖拽事件
                area.addEventListener('dragover', (e) => this.handleDragOver(e));
                area.addEventListener('dragleave', (e) => this.handleDragLeave(e));
                area.addEventListener('drop', (e) => this.handleFileDrop(e));
                
                // 点击事件
                area.addEventListener('click', (e) => this.handleUploadClick(e));
                
                // 文件选择事件
                input.addEventListener('change', (e) => this.handleFileSelect(e, area));
            }
        });
    }

    setupProgressIndicators() {
        document.querySelectorAll('.progress-bar').forEach(bar => {
            this.progressBars.set(bar.id, bar);
        });
    }

    setupStepNavigation() {
        document.querySelectorAll('.step-indicator').forEach(indicator => {
            this.stepIndicators.set(indicator.id, indicator);
        });
    }

    setupResponsiveDesign() {
        const mediaQuery = window.matchMedia('(max-width: 768px)');
        this.handleResponsiveChange(mediaQuery);
        mediaQuery.addListener(this.handleResponsiveChange.bind(this));
    }

    setupNotifications() {
        // 请求通知权限
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    switchScene(sceneId) {
        console.log('🔄 切换场景:', sceneId);

        // 隐藏所有场景
        document.querySelectorAll('.scene-section').forEach(scene => {
            scene.classList.add('hidden');
        });

        // 显示目标场景
        const targetScene = document.getElementById(`scene-${sceneId}`);
        console.log('🎯 目标场景元素:', targetScene);

        if (targetScene) {
            targetScene.classList.remove('hidden');
            this.currentScene = sceneId;
            console.log('✅ 场景切换成功:', sceneId);

            // 根据场景初始化相关功能
            if (sceneId === 'style') {
                this.initializeStyleScene();
            } else if (sceneId === 'format') {
                this.initializeFormatScene();
            } else if (sceneId === 'review') {
                this.initializeReviewScene();
            }
        } else {
            console.error('❌ 未找到目标场景:', `scene-${sceneId}`);
        }

        // 更新导航状态
        this.updateActiveNavItem(sceneId);

        // 重置步骤
        this.resetSteps();
    }

    async initializeStyleScene() {
        try {
            console.log('🎨 初始化文风统一场景...');

            // 加载预设风格
            await loadPresetStyles();

            // 初始化界面交互
            initializeStyleInterface();

            console.log('✅ 文风统一场景初始化完成');
        } catch (error) {
            console.error('❌ 文风统一场景初始化失败:', error);
            errorHandler.handleError(error, 'style_scene_initialization');
        }
    }

    async initializeFormatScene() {
        try {
            console.log('🎯 初始化格式对齐场景...');

            // 确保格式对齐管理器已初始化
            if (window.formatAlignmentManager) {
                // 重新初始化格式对齐管理器以确保事件绑定正常
                await formatAlignmentManager.initialize();
                console.log('✅ 格式对齐管理器重新初始化完成');
            } else {
                console.warn('⚠️ 格式对齐管理器未找到');
            }

            console.log('✅ 格式对齐场景初始化完成');
        } catch (error) {
            console.error('❌ 格式对齐场景初始化失败:', error);
            errorHandler.handleError(error, 'format_scene_initialization');
        }
    }

    async initializeReviewScene() {
        try {
            console.log('📋 初始化文档审查场景...');

            // 确保文档审查管理器已初始化
            if (window.documentReviewManager) {
                // 重新初始化文档审查管理器以确保事件绑定正常
                await documentReviewManager.initialize();
                console.log('✅ 文档审查管理器重新初始化完成');
            } else {
                console.warn('⚠️ 文档审查管理器未找到');
            }

            console.log('✅ 文档审查场景初始化完成');
        } catch (error) {
            console.error('❌ 文档审查场景初始化失败:', error);
            errorHandler.handleError(error, 'review_scene_initialization');
        }
    }

    updateActiveNavItem(sceneId) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-scene') === sceneId) {
                item.classList.add('active');
            }
        });
    }

    resetSteps() {
        document.querySelectorAll('.step-item').forEach((item, index) => {
            item.classList.remove('active', 'completed');
            if (index === 0) {
                item.classList.add('active');
            }
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
    }

    handleFileDrop(e) {
        e.preventDefault();
        const uploadArea = e.currentTarget;
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0], uploadArea);
        }
    }

    handleUploadClick(e) {
        const uploadArea = e.currentTarget;
        const input = uploadArea.querySelector('input[type="file"]');
        if (input) {
            input.click();
        }
    }

    handleFileSelect(e, uploadArea) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file, uploadArea);
        }
    }

    async handleButtonClick(e) {
        const button = e.currentTarget;
        const action = button.getAttribute('data-action');
        
        if (action) {
            await this.executeAction(action, button);
        }
    }

    handleFormSubmit(e) {
        e.preventDefault();
        const form = e.currentTarget;
        const action = form.getAttribute('data-action');
        
        if (action) {
            this.executeAction(action, form);
        }
    }

    async processFile(file, uploadArea) {
        try {
            // 验证文件
            const validator = new FileValidator();
            const validation = validator.validateFile(file);
            
            if (!validation.isValid) {
                errorHandler.handleError(
                    new Error(validation.errors.join(', ')),
                    'file_validation'
                );
                return;
            }

            // 预处理文件
            const preprocessing = await validator.preprocessFile(file);
            if (!preprocessing.success) {
                errorHandler.handleError(
                    new Error(preprocessing.errors.join(', ')),
                    'file_preprocessing'
                );
                return;
            }

            // 更新文件显示
            this.updateFileDisplay(uploadArea, file, preprocessing.data);

            // 显示成功消息
            errorHandler.createNotification('文件上传成功', 'success');

        } catch (error) {
            errorHandler.handleError(error, 'file_processing');
        }
    }

    updateFileDisplay(uploadArea, file, fileData) {
        // 移除现有的文件显示
        const existingDisplay = uploadArea.querySelector('.file-display');
        if (existingDisplay) {
            existingDisplay.remove();
        }

        // 创建新的文件显示
        const fileDisplay = this.createFileDisplay(file, fileData);
        uploadArea.appendChild(fileDisplay);

        // 更新上传区域状态
        uploadArea.classList.add('has-file');
    }

    createFileDisplay(file, fileData) {
        const display = document.createElement('div');
        display.className = 'file-display';
        display.innerHTML = `
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${this.formatFileSize(file.size)}</div>
                <div class="file-type">${fileData.fileType}</div>
            </div>
            <div class="file-actions">
                <button class="btn btn-small btn-preview-file" title="预览文件">👁️</button>
                <button class="btn btn-small btn-remove-file" title="移除文件">❌</button>
            </div>
        `;

        // 添加事件监听器
        const removeBtn = display.querySelector('.btn-remove-file');
        removeBtn.addEventListener('click', () => {
            display.remove();
            const uploadArea = display.closest('.file-upload-area');
            uploadArea.classList.remove('has-file');
        });

        return display;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showLoading(elementId, message = '处理中...') {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="loading">
                    <div class="loading-spinner"></div>
                    <div class="loading-message">${message}</div>
                </div>
            `;
        }
    }

    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            const loading = element.querySelector('.loading');
            if (loading) {
                loading.remove();
            }
        }
    }

    updateProgress(progress, message = '') {
        const progressBar = document.querySelector('.global-progress-bar');
        if (progressBar) {
            const fill = progressBar.querySelector('.progress-fill');
            const text = progressBar.querySelector('.progress-text');
            
            if (fill) {
                fill.style.width = `${progress}%`;
            }
            if (text && message) {
                text.textContent = message;
            }
        }
    }

    navigateToStep(step) {
        const stepItems = document.querySelectorAll('.step-item');
        stepItems.forEach((item, index) => {
            item.classList.remove('active', 'completed');
            if (index + 1 < step) {
                item.classList.add('completed');
            } else if (index + 1 === step) {
                item.classList.add('active');
            }
        });

        // 更新应用状态
        appState.updateStep(step);
    }

    async executeAction(action, element) {
        try {
            switch (action) {
                case 'format_alignment':
                    await this.handleFormatAlignment(element);
                    break;
                case 'style_alignment':
                    await this.handleStyleAlignment(element);
                    break;
                case 'document_fill':
                    await this.handleDocumentFill(element);
                    break;
                case 'document_review':
                    await this.handleDocumentReview(element);
                    break;
                case 'set_baseline':
                    await this.handleSetBaseline(element);
                    break;
                case 'save_format':
                    await this.handleSaveFormat(element);
                    break;
                case 'apply_style':
                    await this.handleApplyStyle(element);
                    break;
                case 'save_style':
                    await this.handleSaveStyle(element);
                    break;
                case 'start_review':
                    await this.handleStartReview(element);
                    break;
                case 'review_settings':
                    await this.handleReviewSettings(element);
                    break;
                case 'export_review_report':
                    await this.handleExportReviewReport(element);
                    break;
                case 'preview_result':
                    await this.handleFormatAlignmentPreview(element);
                    break;
                case 'export_result':
                    await this.handleFormatAlignmentExport(element);
                    break;
                case 'preview_review':
                    await this.handlePreviewReview(element);
                    break;
                case 'export_review':
                    await this.handleExportReview(element);
                    break;
                case 'auto_match_data':
                    await this.handleAutoMatchData(element);
                    break;
                case 'manual_match':
                    await this.handleManualMatch(element);
                    break;
                case 'export_filled_doc':
                    await this.handleExportFilledDoc(element);
                    break;
                case 'preview_fill':
                    await this.handlePreviewFill(element);
                    break;
                case 'export_fill':
                    await this.handleExportFill(element);
                    break;
                case 'preview_fill_result':
                    await this.handlePreviewFillResult(element);
                    break;
                case 'export_fill_result':
                    await this.handleExportFillResult(element);
                    break;
                case 'preview_style':
                    await this.handlePreviewStyle(element);
                    break;
                case 'export_style':
                    await this.handleExportStyle(element);
                    break;
                case 'export_review_pdf':
                    await this.handleExportReviewReport('pdf');
                    break;
                case 'export_review_word':
                    await this.handleExportReviewReport('word');
                    break;
                case 'export_review_html':
                    await this.handleExportReviewReport('html');
                    break;
                default:
                    console.warn(`未知操作: ${action}`);
            }
        } catch (error) {
            errorHandler.handleError(error, 'action_execution');
        }
    }

    async handleFormatAlignment(element) {
        // 防止重复提交
        if (this.isProcessing) {
            errorHandler.createNotification('正在处理中，请稍候...', 'info');
            return;
        }

        this.isProcessing = true;
        element.disabled = true;
        element.textContent = '处理中...';

        const sessionId = appState.createSession('format');
        this.navigateToStep(2);

        // 收集文件
        const files = this.collectFiles('format');
        if (files.length < 2) {
            errorHandler.handleError(new Error('请上传参考文件和目标文件'), 'validation');
            this.resetProcessingState(element);
            return;
        }

        try {
            // 读取文件内容
            const filesWithContent = await Promise.all(files.map(async (fileInfo) => {
                let content = '';

                if (fileInfo.file && fileInfo.file instanceof File) {
                    // 读取文件内容
                    content = await this.readFileContent(fileInfo.file);
                }

                return {
                    name: fileInfo.name,
                    size: fileInfo.size,
                    type: fileInfo.type,
                    content: content
                };
            }));

            console.log('📝 准备发送的文件数据:', filesWithContent);

            // 显示处理提示
            errorHandler.createNotification('正在处理文件，请稍候...', 'info');

            // 调用API，增加超时时间
            const result = await apiManager.request('/api/format-alignment', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: sessionId,
                    files: filesWithContent
                }),
                timeout: 90000  // 90秒超时
            });

            if (result.success) {
                this.navigateToStep(3);
                this.showResult(result.data);
                errorHandler.createNotification('格式对齐完成', 'success');
            } else {
                errorHandler.handleError(new Error(result.error || '格式对齐失败'), 'api');
            }
        } catch (error) {
            errorHandler.handleError(error, 'processing');
        } finally {
            this.resetProcessingState(element);
        }
    }

    resetProcessingState(element) {
        this.isProcessing = false;
        if (element) {
            element.disabled = false;
            element.textContent = '应用格式对齐';
        }
    }

    async handleFormatAlignmentPreview(element) {
        // 预览功能已取消，直接提示用户到导出处理结果中下载
        try {
            const taskId = this.getLatestFormatAlignmentTaskId();
            if (!taskId) {
                errorHandler.handleError(new Error('没有找到格式对齐任务，请先执行格式对齐'), 'validation');
                return;
            }

            console.log('🔍 格式对齐预览功能已取消，请到导出处理结果中下载');
            errorHandler.createNotification('预览功能已取消，请到下方"导出处理结果"中下载文件', 'info');
            // 滚动到导出处理结果部分
            const exportSection = document.getElementById('format-export-results');
            if (exportSection) {
                exportSection.scrollIntoView({ behavior: 'smooth' });
            }
        } catch (error) {
            errorHandler.handleError(error, 'preview');
        }
    }

    async handleFormatAlignmentExport(element) {
        try {
            // 获取最近的格式对齐任务ID
            const taskId = this.getLatestFormatAlignmentTaskId();
            if (!taskId) {
                errorHandler.handleError(new Error('没有找到格式对齐任务，请先执行格式对齐'), 'validation');
                return;
            }

            console.log('📥 导出格式对齐结果，任务ID:', taskId);
            this.showExportOptions(taskId);
        } catch (error) {
            errorHandler.handleError(error, 'export');
        }
    }

    getLatestFormatAlignmentTaskId() {
        // 从结果显示区域获取任务ID，或者从全局状态获取
        const resultContent = document.getElementById('format-preview-content');
        if (resultContent && resultContent.dataset.taskId) {
            return resultContent.dataset.taskId;
        }

        // 如果没有找到，返回null
        return null;
    }

    async readFileContent(file) {
        return new Promise((resolve, reject) => {
            // 对于DOCX等二进制文件，我们不在前端读取内容
            // 而是发送文件基本信息，让后端处理
            if (file.name.endsWith('.docx') ||
                file.name.endsWith('.doc') ||
                file.type.includes('officedocument') ||
                file.type.includes('msword')) {

                // 对于Office文档，返回文件信息而不是内容
                resolve(`[DOCX文件: ${file.name}, 大小: ${file.size} 字节]`);
                return;
            }

            // 对于文本文件，正常读取内容
            const reader = new FileReader();

            reader.onload = function(e) {
                resolve(e.target.result);
            };

            reader.onerror = function(e) {
                reject(new Error('文件读取失败'));
            };

            // 只对文本文件读取内容
            if (file.type.includes('text') || file.name.endsWith('.txt')) {
                reader.readAsText(file, 'UTF-8');
            } else {
                // 其他未知文件类型，尝试读取为文本
                reader.readAsText(file, 'UTF-8');
            }
        });
    }

    // ==================== AI文风统一功能 ====================

    async handleStyleAlignment(element) {
        // 新的文风统一处理入口 - 根据当前模式分发
        const selectedMode = document.querySelector('input[name="style-mode"]:checked')?.value;

        if (selectedMode === 'preset') {
            await this.handlePresetStyleGeneration(element);
        } else if (selectedMode === 'few-shot') {
            await this.handleFewShotTransfer(element);
        } else {
            errorHandler.handleError(new Error('请选择处理模式'), 'validation');
        }
    }

    async handlePresetStyleGeneration(element) {
        try {
            // 开始前清空上次结果并隐藏导出区，避免导出旧内容
            this.currentStyleResult = null;
            this.hideStyleExportSection();

            // 获取选中的风格
            const selectedStyle = document.querySelector('.style-card.selected');
            if (!selectedStyle) {
                errorHandler.handleError(new Error('请选择一种预设风格'), 'validation');
                return;
            }

            const styleId = selectedStyle.dataset.styleId;
            console.log('🎨 选中的风格ID:', styleId);

            // 获取内容
            const content = await this.getInputContent();
            if (!content) {
                errorHandler.handleError(new Error('请输入要处理的内容'), 'validation');
                return;
            }

            // 获取配置参数
            const action = document.getElementById('style-action')?.value || '重写';
            const temperature = parseFloat(document.getElementById('style-temperature')?.value || '0.7');
            const language = document.getElementById('style-language')?.value || 'auto';

            // 构建请求数据
            const requestData = {
                content: content,
                style_id: styleId,
                action: action,
                language: language,
                temperature: temperature
            };

            console.log('📤 发送请求数据:', requestData);

            // 开始新的处理时，先隐藏之前的导出结果
            this.hideStyleExportSection();

            // 显示进度
            this.showProcessingProgress();
            this.updateProcessingText('正在生成预设风格内容...');

            // 调用API
            const result = await apiManager.request('/api/style-alignment/generate-with-style', {
                method: 'POST',
                body: JSON.stringify(requestData),
                timeout: 120000  // 2分钟超时，预设风格生成可能需要较长时间
            });

            if (result.success) {
                // 验证生成的内容是否有效
                if (result.generated_content && result.generated_content.trim()) {
                    // 直接跳过预览，显示完成提示和导出选项
                    this.showStyleCompletionAndExport(result, content);
                    this.navigateToStep(4);
                } else {
                    this.hideProcessingProgress();
                    this.hideStyleExportSection();
                    this.hideStyleCompletionMessage();
                    errorHandler.handleError(new Error('生成的内容为空，请重试'), 'api');
                }
            } else {
                this.hideProcessingProgress();
                this.hideStyleExportSection();
                this.hideStyleCompletionMessage();
                errorHandler.handleError(new Error(result.error || '风格生成失败'), 'api');
            }

        } catch (error) {
            this.hideProcessingProgress();
            // 处理失败时也要隐藏导出结果和完成提示
            this.hideStyleExportSection();
            this.hideStyleCompletionMessage();

            console.error('❌ 预设风格生成失败:', error);

            // 根据错误类型提供更友好的错误信息
            let errorMessage = '预设风格生成失败';
            let context = 'preset_style_generation';

            if (error.name === 'AbortError' || error.message.includes('timeout') || error.message.includes('超时')) {
                errorMessage = '处理超时，技术文档风格生成需要较长时间，请稍后重试';
                context = 'network_timeout';
            } else if (error.message && error.message.includes('Read timed out')) {
                errorMessage = 'AI服务响应超时，请稍后重试或选择其他风格模板';
                context = 'api_timeout';
            } else if (error.message && error.message.includes('HTTPSConnectionPool')) {
                errorMessage = 'AI服务连接超时，请检查网络连接后重试';
                context = 'connection_timeout';
            } else if (error.message && error.message.includes('文件读取')) {
                errorMessage = '文件读取失败，请检查文件格式';
                context = 'file_reading';
            } else if (error.message && error.message.includes('内容')) {
                errorMessage = '输入内容验证失败，请检查输入内容';
                context = 'content_validation';
            } else if (error.message) {
                errorMessage = '预设风格生成失败: ' + error.message;
            }

            errorHandler.handleError(new Error(errorMessage), context);
        }
    }

    async handleFewShotTransfer(element) {
        try {
            // 获取参考文档
            const referenceFile = document.getElementById('upload-reference-doc').files[0];
            if (!referenceFile) {
                errorHandler.handleError(new Error('请上传参考文档'), 'validation');
                return;
            }

            // 验证文件格式 - 只允许TXT格式
            const fileExtension = '.' + referenceFile.name.split('.').pop().toLowerCase();
            if (fileExtension !== '.txt') {
                errorHandler.handleError(new Error('参考文档只支持TXT格式，请上传.txt文件'), 'validation');
                return;
            }

            // 验证文件MIME类型
            if (referenceFile.type && !referenceFile.type.startsWith('text/')) {
                errorHandler.handleError(new Error('文件类型不正确，请确保上传的是纯文本文件'), 'validation');
                return;
            }

            // 验证文件大小
            const maxSize = 10 * 1024 * 1024; // 10MB
            if (referenceFile.size > maxSize) {
                errorHandler.handleError(new Error('文件大小不能超过10MB'), 'validation');
                return;
            }

            if (referenceFile.size === 0) {
                errorHandler.handleError(new Error('文件为空，请选择有效的TXT文件'), 'validation');
                return;
            }

            // 获取内容
            const content = await this.getInputContent();
            if (!content) {
                errorHandler.handleError(new Error('请输入要处理的内容'), 'validation');
                return;
            }

            // 读取参考文档内容
            const referenceContent = await this.readFileContent(referenceFile);

            // 获取配置参数
            const targetDescription = document.getElementById('style-description')?.value || '';
            const temperature = parseFloat(document.getElementById('few-shot-temperature')?.value || '0.7');
            const language = document.getElementById('style-language')?.value || 'auto';

            // 开始新的处理时，先隐藏之前的导出结果
            this.hideStyleExportSection();

            // 显示进度
            this.showProcessingProgress();
            this.updateProcessingText('正在进行Few-Shot风格学习和转换...');

            // 调用API
            const result = await apiManager.request('/api/style-alignment/few-shot-transfer', {
                method: 'POST',
                body: JSON.stringify({
                    content: content,
                    reference_document: referenceContent,
                    target_description: targetDescription,
                    language: language,
                    temperature: temperature
                }),
                timeout: 120000  // 2分钟超时，文风转换可能需要较长时间
            });

            if (result.success) {
                // 直接跳过预览，显示完成提示和导出选项
                this.showStyleCompletionAndExport(result, content);
                this.navigateToStep(4);
            } else {
                this.hideProcessingProgress();
                errorHandler.handleError(new Error(result.error || 'Few-Shot风格迁移失败'), 'api');
            }

        } catch (error) {
            this.hideProcessingProgress();
            // 处理失败时也要隐藏导出结果和完成提示
            this.hideStyleExportSection();
            this.hideStyleCompletionMessage();

            console.error('❌ Few-Shot风格迁移失败:', error);

            // 根据错误类型提供更友好的错误信息
            let errorMessage = 'Few-Shot风格迁移失败';
            let context = 'few_shot_transfer';

            if (error.name === 'AbortError') {
                errorMessage = '请求超时，文风转换需要较长时间，请检查网络连接或稍后重试';
                context = 'network_timeout';
            } else if (error.message && error.message.includes('文件读取')) {
                errorMessage = '参考文档读取失败，请检查文件格式';
                context = 'file_reading';
            } else if (error.message && error.message.includes('内容')) {
                errorMessage = '输入内容验证失败，请检查输入内容';
                context = 'content_validation';
            } else if (error.message) {
                errorMessage = 'Few-Shot风格迁移失败: ' + error.message;
            }

            errorHandler.handleError(new Error(errorMessage), context);
        }
    }

    async getInputContent() {
        // @AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: fix_getInputContent
        // 获取用户输入的内容 - 使用更健壮的逻辑

        // 首先尝试从文本输入框获取内容
        const textInput = document.getElementById('style-content-text');
        if (textInput && textInput.value && textInput.value.trim()) {
            console.log('📝 从文本输入框获取内容:', textInput.value.trim().substring(0, 50) + '...');
            return textInput.value.trim();
        }

        // 然后检查文件上传
        const fileInput = document.getElementById('upload-content-file');
        if (fileInput && fileInput.files && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            try {
                console.log('📁 从文件获取内容:', file.name);
                const content = await this.readFileContent(file);
                return content;
            } catch (error) {
                throw new Error(`文件读取失败: ${error.message}`);
            }
        }

        // 如果都没有内容，检查当前激活的标签页来提供更具体的错误信息
        const activeTab = document.querySelector('.tab-button.active')?.dataset.tab;
        if (activeTab === 'file-upload') {
            throw new Error('请选择要上传的文件');
        } else {
            throw new Error('请在文本框中输入要处理的内容');
        }
    }

    async readFileContent(file) {
        // @AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: readFileContent
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = function(e) {
                try {
                    const content = e.target.result;

                    // 检查文件大小（限制为2MB）
                    if (content.length > 2 * 1024 * 1024) {
                        reject(new Error('文件过大，请选择小于2MB的文件'));
                        return;
                    }

                    // 检查内容是否为空
                    if (!content.trim()) {
                        reject(new Error('文件内容为空'));
                        return;
                    }

                    // 验证内容是否为纯文本（检查是否包含二进制字符）
                    if (typeof content !== 'string') {
                        reject(new Error('文件内容格式不正确，请确保是纯文本文件'));
                        return;
                    }

                    // 检查是否包含过多的控制字符（可能是二进制文件）
                    const controlCharCount = (content.match(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g) || []).length;
                    if (controlCharCount > content.length * 0.01) { // 如果控制字符超过1%，可能不是纯文本
                        reject(new Error('文件可能不是纯文本格式，请上传标准的TXT文件'));
                        return;
                    }

                    resolve(content.trim());
                } catch (error) {
                    reject(new Error(`文件解析失败: ${error.message}`));
                }
            };

            reader.onerror = function() {
                reject(new Error('文件读取失败，请检查文件是否损坏'));
            };

            // 根据文件类型选择读取方式
            const fileType = file.type.toLowerCase();
            const fileName = file.name.toLowerCase();

            if (fileType.includes('text') ||
                fileName.endsWith('.txt') ||
                fileName.endsWith('.md') ||
                fileName.endsWith('.rtf')) {
                // 文本文件直接读取
                reader.readAsText(file, 'UTF-8');
            } else if (fileName.endsWith('.docx') || fileName.endsWith('.doc')) {
                // Word文档需要特殊处理，这里先读取为文本
                // 注意：这只能读取纯文本，不能解析Word格式
                reader.readAsText(file, 'UTF-8');
            } else {
                // 其他文件类型尝试读取为文本
                reader.readAsText(file, 'UTF-8');
            }
        });
    }

    showProcessingProgress() {
        // 显示处理进度区域
        const processingArea = document.getElementById('style-processing-area');
        if (processingArea) {
            processingArea.style.display = 'block';
            processingArea.style.visibility = 'visible';
            processingArea.classList.remove('hidden');
            console.log('✅ 已显示处理进度区域');
        }

        // 重置进度
        this.updateStyleProgress(0, '开始处理...');

        // 模拟进度更新
        this.startProgressSimulation();
    }

    hideProcessingProgress() {
        const processingArea = document.getElementById('style-processing-area');
        if (processingArea) {
            processingArea.style.display = 'none';
        }
    }

    updateProcessingText(text) {
        const processingText = document.querySelector('#style-processing-area .processing-text');
        if (processingText) {
            processingText.textContent = text;
        }
    }

    updateStyleProgress(percent, message) {
        const progressFill = document.getElementById('style-progress-fill');
        const progressPercent = document.getElementById('style-progress-percent');
        const progressMessage = document.getElementById('style-progress-message');

        if (progressFill) {
            progressFill.style.width = `${percent}%`;
        }

        if (progressPercent) {
            progressPercent.textContent = `${percent}%`;
        }

        if (progressMessage) {
            progressMessage.textContent = message;
        }
    }

    async handleExportReviewReport(format) {
        // @AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: export_review_report
        try {
            // 检查是否有审查结果
            if (!documentReviewManager.currentReviewResult) {
                errorHandler.handleError(new Error('没有可导出的审查报告'), 'validation');
                return;
            }

            const reviewData = documentReviewManager.currentReviewResult;
            const content = reviewData.review_result;
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            const filename = `document_review_report_${timestamp}`;

            console.log(`📄 导出${format.toUpperCase()}格式审查报告...`);

            if (format === 'html') {
                // HTML导出 - 直接下载
                const htmlContent = this.generateReviewReportHTML(reviewData);
                this.downloadFile(htmlContent, `${filename}.html`, 'text/html');
                errorHandler.createNotification('HTML报告导出成功', 'success');
            } else if (format === 'pdf') {
                // PDF导出 - 通过后端API
                await this.exportReviewReportPDF(reviewData, filename);
            } else if (format === 'word') {
                // Word导出 - 通过后端API
                await this.exportReviewReportWord(reviewData, filename);
            } else {
                throw new Error(`不支持的导出格式: ${format}`);
            }

        } catch (error) {
            console.error('❌ 导出审查报告失败:', error);
            errorHandler.handleError(error, 'export');
        }
    }

    generateReviewReportHTML(reviewData) {
        const htmlContent = documentReviewManager.markdownToHtml(reviewData.review_result);
        const timestamp = new Date().toLocaleString('zh-CN');

        return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文档审查报告</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; margin: 40px; }
        .header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
        .title { font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px; }
        .meta { color: #666; font-size: 14px; }
        .content { margin-top: 20px; }
        h1, h2, h3 { color: #333; margin-top: 25px; margin-bottom: 15px; }
        h1 { font-size: 20px; } h2 { font-size: 18px; } h3 { font-size: 16px; }
        li { margin-bottom: 8px; }
        strong { color: #d73527; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">📋 AI文档审查报告</div>
        <div class="meta">
            <span>生成时间: ${timestamp}</span> |
            <span>文档长度: ${reviewData.document_length} 字符</span> |
            <span>处理时间: ${reviewData.processing_time?.toFixed(2)}秒</span>
            ${reviewData.chunks_count > 1 ? ` | <span>分块处理: ${reviewData.chunks_count} 个块</span>` : ''}
        </div>
    </div>
    <div class="content">
        ${htmlContent}
    </div>
    <div class="footer">
        <p>本报告由aiDoc AI文档审查系统生成 | 基于讯飞星火X1大模型</p>
    </div>
</body>
</html>`;
    }

    async exportReviewReportPDF(reviewData, filename) {
        // @AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: export_review_report_pdf
        try {
            console.log('📄 开始导出PDF格式审查报告...');

            // 调用后端API生成PDF
            const response = await fetch('/api/document-review/export-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    review_data: reviewData,
                    filename: filename
                })
            });

            if (response.ok) {
                // 获取PDF文件内容
                const blob = await response.blob();

                // 创建下载链接
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `${filename}.pdf`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);

                errorHandler.createNotification('PDF报告导出成功', 'success');
                console.log('✅ PDF导出完成');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'PDF导出失败');
            }
        } catch (error) {
            console.error('❌ PDF导出失败:', error);
            errorHandler.handleError(error, 'pdf_export');
        }
    }

    async exportReviewReportWord(reviewData, filename) {
        // @AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: export_review_report_word
        try {
            console.log('📝 开始导出Word格式审查报告...');

            // 调用后端API生成Word文档
            const response = await fetch('/api/document-review/export-word', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    review_data: reviewData,
                    filename: filename
                })
            });

            if (response.ok) {
                // 获取Word文件内容
                const blob = await response.blob();

                // 创建下载链接
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `${filename}.docx`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);

                errorHandler.createNotification('Word报告导出成功', 'success');
                console.log('✅ Word导出完成');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Word导出失败');
            }
        } catch (error) {
            console.error('❌ Word导出失败:', error);
            errorHandler.handleError(error, 'word_export');
        }
    }



    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    startProgressSimulation() {
        // 模拟进度更新
        let progress = 0;
        const messages = [
            '正在分析内容...',
            '调用AI模型...',
            '生成风格化文本...',
            '优化输出结果...',
            '完成处理'
        ];

        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress >= 90) {
                progress = 90;
                clearInterval(interval);
            }

            const messageIndex = Math.floor(progress / 20);
            const message = messages[messageIndex] || messages[messages.length - 1];

            this.updateStyleProgress(Math.floor(progress), message);
        }, 500);

        // 存储interval以便后续清理
        this.progressInterval = interval;
    }

    showStyleResult(result, originalContent) {
        // 保留原方法以防其他地方调用，但现在使用新的方法
        this.showStyleCompletionAndExport(result, originalContent);
    }

    showStyleCompletionAndExport(result, originalContent) {
        // 清理进度模拟
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }

        // 验证生成内容的有效性
        if (!result.generated_content || !result.generated_content.trim()) {
            console.error('❌ 生成的内容为空或无效');
            this.hideProcessingProgress();
            this.hideStyleExportSection();
            this.hideStyleCompletionMessage();
            errorHandler.handleError(new Error('生成的内容为空，请重试'), 'content_validation');
            return;
        }

        // 检查生成内容是否包含错误信息
        const generatedContent = result.generated_content.trim();
        if (generatedContent.includes('[错误]') || generatedContent.includes('API 请求失败') ||
            generatedContent.includes('超时') || generatedContent.length < 10) {
            console.error('❌ 生成的内容包含错误信息:', generatedContent);
            this.hideProcessingProgress();
            this.hideStyleExportSection();
            this.hideStyleCompletionMessage();
            errorHandler.handleError(new Error('AI生成失败，请重试'), 'content_validation');
            return;
        }

        // 完成进度
        this.updateStyleProgress(100, '处理完成');

        // 存储结果数据
        this.currentStyleResult = {
            original: originalContent,
            generated: result.generated_content,
            taskId: result.task_id,
            styleName: result.style_name,
            comparison: result.comparison,
            language: result.language
        };

        console.log('✅ 文风统一处理成功，生成内容长度:', generatedContent.length);

        // 延迟显示完成提示和导出选项
        setTimeout(() => {
            // 显示完成提示
            this.showStyleCompletionMessage();

            // 显示导出选项
            this.showStyleExportSection();

            errorHandler.createNotification('文风统一完成，请选择导出格式', 'success');
        }, 1000);
    }

    showStyleCompletionMessage() {
        // 显示文风统一完成提示
        const completionMessage = document.getElementById('style-completion-message');
        if (completionMessage) {
            completionMessage.style.display = 'block';
            completionMessage.style.visibility = 'visible';
            completionMessage.classList.remove('hidden');
            console.log('✅ 已显示完成提示消息');
        }
    }

    hideStyleCompletionMessage() {
        // 隐藏文风统一完成提示
        const completionMessage = document.getElementById('style-completion-message');
        if (completionMessage) {
            completionMessage.style.display = 'none';
        }
    }

    showStyleExportSection() {
        // 显示文风统一导出选项并初始化事件绑定
        const exportArea = document.getElementById('style-export-area');
        if (exportArea) {
            exportArea.style.display = 'block';
            exportArea.style.visibility = 'visible';
            exportArea.classList.remove('hidden');
            console.log('✅ 已显示导出选项区域');

            // 初始化导出按钮事件绑定
            this.initializeStyleExportButtons();
        }
    }

    initializeStyleExportButtons() {
        // 初始化文风统一导出按钮的事件绑定
        const confirmButton = document.getElementById('confirm-export');
        const backButton = document.getElementById('back-to-result');

        if (confirmButton) {
            // 移除之前的事件监听器，避免重复绑定
            confirmButton.onclick = null;
            confirmButton.onclick = () => {
                const selectedFormat = document.querySelector('input[name="export-format"]:checked')?.value;
                if (selectedFormat) {
                    // 调用原有的导出函数
                    performExport(selectedFormat);
                } else {
                    errorHandler.createNotification('请选择导出格式', 'warning');
                }
            };
        }

        if (backButton) {
            backButton.onclick = null;
            backButton.onclick = () => {
                // 返回按钮功能已取消，因为我们不再有预览界面
                errorHandler.createNotification('已完成处理，请选择导出格式', 'info');
            };
        }
    }



    hideStyleExportSection() {
        // 隐藏文风统一导出选项，避免显示上一次的结果
        const exportArea = document.getElementById('style-export-area');
        if (exportArea) {
            exportArea.style.display = 'none';
        }
    }

    async handleReferenceDocumentUpload(file) {
        if (!file) return;

        try {
            console.log('📄 上传参考文档:', file.name);

            // 验证文件格式 - 只允许TXT格式
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
            if (fileExtension !== '.txt') {
                errorHandler.createNotification('参考文档只支持TXT格式，请上传.txt文件', 'error');
                // 清空文件输入
                const input = document.getElementById('upload-reference-doc');
                if (input) input.value = '';
                return;
            }

            // 验证文件MIME类型
            if (file.type && !file.type.startsWith('text/')) {
                errorHandler.createNotification('文件类型不正确，请确保上传的是纯文本文件', 'error');
                // 清空文件输入
                const input = document.getElementById('upload-reference-doc');
                if (input) input.value = '';
                return;
            }

            // 验证文件大小
            const maxSize = 10 * 1024 * 1024; // 10MB
            if (file.size > maxSize) {
                errorHandler.createNotification('文件大小不能超过10MB', 'error');
                const input = document.getElementById('upload-reference-doc');
                if (input) input.value = '';
                return;
            }

            if (file.size === 0) {
                errorHandler.createNotification('文件为空，请选择有效的TXT文件', 'error');
                const input = document.getElementById('upload-reference-doc');
                if (input) input.value = '';
                return;
            }

            // 读取文件内容
            const content = await this.readFileContent(file);

            // 验证内容不为空
            if (!content.trim()) {
                errorHandler.createNotification('文件内容为空，请选择包含文本内容的TXT文件', 'error');
                const input = document.getElementById('upload-reference-doc');
                if (input) input.value = '';
                return;
            }

            // 存储参考文档信息
            this.uploadedReferenceDocument = {
                name: file.name,
                content: content,
                size: file.size
            };

            // 更新UI显示
            this.updateReferenceDocUploadStatus(file.name);

            errorHandler.createNotification('参考文档上传成功', 'success');
            console.log('✅ 参考文档上传成功');

        } catch (error) {
            console.error('❌ 参考文档上传失败:', error);
            errorHandler.createNotification('参考文档上传失败: ' + error.message, 'error');
            // 清空文件输入
            const input = document.getElementById('upload-reference-doc');
            if (input) input.value = '';
        }
    }

    updateReferenceDocUploadStatus(fileName) {
        // 更新上传区域的显示状态
        const uploadArea = document.getElementById('reference-doc-upload');
        if (uploadArea) {
            const uploadText = uploadArea.querySelector('.file-upload-text');
            const uploadHint = uploadArea.querySelector('.file-upload-hint');

            if (uploadText) {
                uploadText.textContent = `已上传: ${fileName}`;
                uploadText.style.color = '#10b981';
            }

            if (uploadHint) {
                uploadHint.textContent = '✅ TXT格式参考文档已就绪';
                uploadHint.style.color = '#10b981';
            }

            uploadArea.classList.add('file-uploaded');
        }
    }

    displayStyleComparison() {
        if (!this.currentStyleResult) return;

        // 显示原始内容
        const originalDisplay = document.getElementById('original-content-display');
        if (originalDisplay) {
            originalDisplay.textContent = this.currentStyleResult.original;
        }

        // 显示风格化内容
        const styledDisplay = document.getElementById('styled-content-display');
        if (styledDisplay) {
            styledDisplay.textContent = this.currentStyleResult.generated;
        }

        // 显示仅结果标签页内容
        const resultContent = document.getElementById('style-result-content');
        if (resultContent) {
            resultContent.innerHTML = `
                <div class="result-header">
                    <h3>风格化结果</h3>
                    <div class="result-meta">
                        <span>风格: ${this.currentStyleResult.styleName}</span>
                        <span>语言: ${this.currentStyleResult.language}</span>
                        <span>任务ID: ${this.currentStyleResult.taskId}</span>
                    </div>
                </div>
                <div class="result-content">
                    ${this.currentStyleResult.generated}
                </div>
            `;
        }

        // 显示分析报告
        const analysisContent = document.getElementById('style-analysis-content');
        if (analysisContent && this.currentStyleResult.comparison) {
            analysisContent.innerHTML = this.formatAnalysisReport(this.currentStyleResult.comparison);
        }
    }

    async handleDocumentFill(element) {
        const sessionId = appState.createSession('fill');
        this.navigateToStep(2);
        
        const files = this.collectFiles('fill');
        if (files.length === 0) {
            errorHandler.handleError(new Error('请上传文档模板'), 'validation');
            return;
        }

        const result = await apiManager.request('/api/document-fill/start', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                files: files
            })
        });

        if (result.success) {
            this.navigateToStep(3);
            this.showResult(result.data);
        }
    }

    async handleDocumentReview(element) {
        const sessionId = appState.createSession('review');
        this.navigateToStep(2);
        
        const files = this.collectFiles('review');
        if (files.length === 0) {
            errorHandler.handleError(new Error('请上传待审查文档'), 'validation');
            return;
        }

        const result = await apiManager.request('/api/document-review/start', {
            method: 'POST',
            body: JSON.stringify({
                session_id: sessionId,
                files: files
            })
        });

        if (result.success) {
            this.navigateToStep(3);
            this.showResult(result.data);
        }
    }

    async handlePreview(element) {
        this.navigateToStep(3);
        // 实现预览逻辑
    }

    async handleExport(element) {
        this.navigateToStep(4);
        // 实现导出逻辑
    }

    async handleSetBaseline(element) {
        const files = this.collectFiles('format');
        if (files.length === 0) {
            errorHandler.handleError(new Error('请先上传参考格式文件'), 'validation');
            return;
        }

        const result = await apiManager.request('/api/format-templates', {
            method: 'POST',
            body: JSON.stringify({
                name: '基准格式模板',
                content: files[0],
                type: 'baseline'
            })
        });

        if (result.success) {
            errorHandler.createNotification('基准格式设置成功', 'success');
        }
    }

    async handleSaveFormat(element) {
        const files = this.collectFiles('format');
        if (files.length === 0) {
            errorHandler.handleError(new Error('请先上传文件'), 'validation');
            return;
        }

        const templateName = prompt('请输入格式模板名称：');
        if (!templateName) return;

        const result = await apiManager.request('/api/format-templates', {
            method: 'POST',
            body: JSON.stringify({
                name: templateName,
                content: files[0],
                type: 'custom'
            })
        });

        if (result.success) {
            errorHandler.createNotification('格式模板保存成功', 'success');
        }
    }

    async handleApplyStyle(element) {
        const files = this.collectFiles('style');
        if (files.length < 2) {
            errorHandler.handleError(new Error('请上传参考文件和目标文件'), 'validation');
            return;
        }

        const result = await apiManager.request('/api/style-alignment/preview', {
            method: 'POST',
            body: JSON.stringify({
                reference_file: files[0],
                target_file: files[1]
            }),
            timeout: 60000  // 1分钟超时，预览功能
        });

        if (result.success) {
            this.navigateToStep(3);
            this.showResult(result.data);
        }
    }

    async handleSaveStyle(element) {
        const files = this.collectFiles('style');
        if (files.length === 0) {
            errorHandler.handleError(new Error('请先上传参考文风文件'), 'validation');
            return;
        }

        const templateName = prompt('请输入文风模板名称：');
        if (!templateName) return;

        const result = await apiManager.request('/api/writing-style/save-template', {
            method: 'POST',
            body: JSON.stringify({
                name: templateName,
                content: files[0]
            })
        });

        if (result.success) {
            errorHandler.createNotification('文风模板保存成功', 'success');
        }
    }

    async handleStartReview(element) {
        const files = this.collectFiles('review');
        if (files.length === 0) {
            errorHandler.handleError(new Error('请上传待审查文档'), 'validation');
            return;
        }

        const standard = document.getElementById('review-standard-select').value;
        const requirements = document.getElementById('review-requirements').value;

        const result = await apiManager.request('/api/document-review/start', {
            method: 'POST',
            body: JSON.stringify({
                document: files[0],
                standard: standard,
                requirements: requirements
            })
        });

        if (result.success) {
            this.navigateToStep(3);
            this.showResult(result.data);
        }
    }

    async handleReviewSettings(element) {
        // 显示审查设置对话框
        errorHandler.createNotification('审查设置功能开发中', 'info');
    }





    collectFiles(sceneType) {
        const files = [];
        
        // 从当前场景的所有文件输入框收集文件
        const fileInputs = document.querySelectorAll(`#scene-${sceneType} input[type="file"]`);
        
        fileInputs.forEach(input => {
            if (input.files && input.files.length > 0) {
                const file = input.files[0];
                files.push({
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    file: file
                });
            }
        });
        
        // 如果文件输入框没有文件，尝试从文件显示区域获取
        if (files.length === 0) {
            const uploadAreas = document.querySelectorAll(`#scene-${sceneType} .file-upload-area`);
            
            uploadAreas.forEach(area => {
                const fileDisplay = area.querySelector('.file-display');
                if (fileDisplay) {
                    const fileName = fileDisplay.querySelector('.file-name')?.textContent;
                    if (fileName) {
                        // 尝试从全局状态获取文件
                        const file = Array.from(appState.uploadedFiles.values())
                            .find(f => f.name === fileName);
                        if (file) {
                            files.push(file);
                        }
                    }
                }
            });
        }
        
        return files;
    }

    showResult(data) {
        const resultArea = document.querySelector(`#${this.currentScene}-result-area`);
        if (resultArea) {
            resultArea.style.display = 'block';
            const content = resultArea.querySelector(`#${this.currentScene}-preview-content`);
            if (content) {
                content.innerHTML = this.formatResult(data);

                // 如果是格式对齐结果，存储任务ID
                if (data && data.task_id && this.currentScene === 'format') {
                    content.dataset.taskId = data.task_id;
                    console.log('📝 存储格式对齐任务ID:', data.task_id);
                }
            }
        }
    }

    formatResult(data) {
        if (typeof data === 'string') {
            return `<pre>${data}</pre>`;
        }
        if (typeof data === 'object') {
            // 特殊处理格式对齐结果
            if (data.aligned_content) {
                return `
                    <div class="format-alignment-result">
                        <div class="result-header">
                            <h3>格式对齐结果</h3>
                            <div class="result-meta">
                                <span class="task-id">任务ID: ${data.task_id || 'N/A'}</span>
                                <span class="alignment-score">对齐分数: ${data.alignment_score || 'N/A'}</span>
                                <span class="status">状态: ${data.status || 'completed'}</span>
                            </div>
                        </div>
                        <div class="aligned-content">
                            <h4>格式化内容:</h4>
                            <div class="content-preview">${data.aligned_content.replace(/\n/g, '<br>')}</div>
                        </div>
                        <div class="suggestions">
                            <h4>处理建议:</h4>
                            <ul>
                                ${(data.suggestions || []).map(s => `<li>${s}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                `;
            }
            // 默认JSON显示
            return `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        }
        return `<div>${data}</div>`;
    }

    async handlePreviewResult(taskId) {
        try {
            console.log('🔍 预览结果，任务ID:', taskId);

            // 获取任务结果
            const result = await apiManager.request(`/api/format-alignment/result/${taskId}`, {
                method: 'GET'
            });

            if (result.code === 0) {
                // 创建预览模态框
                this.showPreviewModal(result.data);
            } else {
                errorHandler.handleError(new Error(result.message || '获取预览结果失败'), 'api');
            }
        } catch (error) {
            errorHandler.handleError(error, 'preview');
        }
    }

    async handleExportResult(taskId, format = 'txt') {
        try {
            console.log('📥 导出结果，任务ID:', taskId, '格式:', format);

            // 构建下载URL
            const downloadUrl = `/api/format-alignment/download/${taskId}?format=${format}`;

            // 创建下载链接
            const link = document.createElement('a');
            link.href = downloadUrl;

            // 根据格式设置文件名
            const extension = format === 'docx' ? 'docx' : 'txt';
            link.download = `formatted_document_${taskId}.${extension}`;

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            const formatName = format === 'docx' ? 'Word文档' : '文本文档';
            errorHandler.createNotification(`${formatName}导出成功`, 'success');
        } catch (error) {
            errorHandler.handleError(error, 'export');
        }
    }

    showExportOptions(taskId) {
        // 创建导出选项模态框
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content export-options-modal">
                <div class="modal-header">
                    <h3>选择导出格式</h3>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="export-options">
                        <div class="export-option" onclick="uiManager.handleExportResult('${taskId}', 'txt'); this.closest('.modal').remove();">
                            <div class="option-icon">📄</div>
                            <div class="option-info">
                                <h4>文本文档 (.txt)</h4>
                                <p>纯文本格式，兼容性最好</p>
                            </div>
                        </div>
                        <div class="export-option" onclick="uiManager.handleExportResult('${taskId}', 'docx'); this.closest('.modal').remove();">
                            <div class="option-icon">📝</div>
                            <div class="option-info">
                                <h4>Word文档 (.docx)</h4>
                                <p>Microsoft Word格式，支持丰富格式</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">取消</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    showPreviewModal(data) {
        // 创建预览模态框
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>格式对齐结果预览</h3>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="preview-content">
                        ${data.processing_log ? `<p><strong>处理日志:</strong> ${data.processing_log}</p>` : ''}
                        <div class="formatted-content">
                            <h4>格式化内容:</h4>
                            <pre>${data.formatted_content || '暂无内容'}</pre>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">关闭</button>
                    <button class="btn btn-primary" onclick="this.closest('.modal').remove(); uiManager.showExportOptions('${data.task_id}')">导出文档</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    handleResponsiveChange(mediaQuery) {
        if (mediaQuery.matches) {
            document.body.classList.add('mobile-view');
        } else {
            document.body.classList.remove('mobile-view');
        }
    }

    // 新增缺失的处理函数
    async handleAutoMatchData(element) {
        try {
            const sessionId = appState.getCurrentSessionId();
            if (!sessionId) {
                errorHandler.handleError(new Error('请先开始文档填报流程'), 'validation');
                return;
            }

            const result = await apiManager.request('/api/document-fill/auto-match', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            if (result.success) {
                this.navigateToStep(3);
                this.showResult(result.data);
                errorHandler.createNotification('数据自动匹配完成', 'success');
            }
        } catch (error) {
            errorHandler.handleError(error, 'auto_match_data');
        }
    }

    async handleManualMatch(element) {
        try {
            const sessionId = appState.getCurrentSessionId();
            if (!sessionId) {
                errorHandler.handleError(new Error('请先开始文档填报流程'), 'validation');
                return;
            }

            // 显示手动匹配界面
            this.showManualMatchInterface();
        } catch (error) {
            errorHandler.handleError(error, 'manual_match');
        }
    }

    async handleExportFilledDoc(element) {
        try {
            const sessionId = appState.getCurrentSessionId();
            if (!sessionId) {
                errorHandler.handleError(new Error('请先完成文档填报'), 'validation');
                return;
            }

            const result = await apiManager.request('/api/document-fill/export', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            if (result.success) {
                apiManager.downloadFile('/api/document-fill/download', result.data, 'filled_document.docx');
                errorHandler.createNotification('文档导出成功', 'success');
            }
        } catch (error) {
            errorHandler.handleError(error, 'export_filled_doc');
        }
    }

    async handlePreviewFill(element) {
        try {
            const sessionId = appState.getCurrentSessionId();
            if (!sessionId) {
                errorHandler.handleError(new Error('请先开始文档填报流程'), 'validation');
                return;
            }

            const result = await apiManager.request('/api/document-fill/preview', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            if (result.success) {
                this.navigateToStep(3);
                this.showResult(result.data);
            }
        } catch (error) {
            errorHandler.handleError(error, 'preview_fill');
        }
    }

    async handleExportFill(element) {
        try {
            const sessionId = appState.getCurrentSessionId();
            if (!sessionId) {
                errorHandler.handleError(new Error('请先完成文档填报'), 'validation');
                return;
            }

            const result = await apiManager.request('/api/document-fill/export', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            if (result.success) {
                apiManager.downloadFile('/api/document-fill/download', result.data, 'filled_document.docx');
                errorHandler.createNotification('文档导出成功', 'success');
            }
        } catch (error) {
            errorHandler.handleError(error, 'export_fill');
        }
    }

    async handlePreviewFillResult(element) {
        try {
            const sessionId = appState.getCurrentSessionId();
            if (!sessionId) {
                errorHandler.handleError(new Error('请先完成文档填报'), 'validation');
                return;
            }

            const result = await apiManager.request('/api/document-fill/preview-result', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            if (result.success) {
                this.showResult(result.data);
            }
        } catch (error) {
            errorHandler.handleError(error, 'preview_fill_result');
        }
    }

    async handleExportFillResult(element) {
        try {
            const sessionId = appState.getCurrentSessionId();
            if (!sessionId) {
                errorHandler.handleError(new Error('请先完成文档填报'), 'validation');
                return;
            }

            const result = await apiManager.request('/api/document-fill/export-result', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            if (result.success) {
                apiManager.downloadFile('/api/document-fill/download-result', result.data, 'fill_result.docx');
                errorHandler.createNotification('填报结果导出成功', 'success');
            }
        } catch (error) {
            errorHandler.handleError(error, 'export_fill_result');
        }
    }

    async handlePreviewStyle(element) {
        try {
            const sessionId = appState.getCurrentSessionId();
            if (!sessionId) {
                errorHandler.handleError(new Error('请先开始文风对齐流程'), 'validation');
                return;
            }

            const result = await apiManager.request('/api/writing-style/preview', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            if (result.success) {
                this.navigateToStep(3);
                this.showResult(result.data);
            }
        } catch (error) {
            errorHandler.handleError(error, 'preview_style');
        }
    }

    async handleExportStyle(element) {
        try {
            const sessionId = appState.getCurrentSessionId();
            if (!sessionId) {
                errorHandler.handleError(new Error('请先完成文风对齐'), 'validation');
                return;
            }

            const result = await apiManager.request('/api/writing-style/export', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            if (result.success) {
                apiManager.downloadFile('/api/writing-style/download', result.data, 'style_aligned_document.docx');
                errorHandler.createNotification('文风对齐文档导出成功', 'success');
            }
        } catch (error) {
            errorHandler.handleError(error, 'export_style');
        }
    }

    showManualMatchInterface() {
        // 创建手动匹配界面
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>手动数据匹配</h3>
                <div class="match-interface">
                    <div class="template-fields">
                        <h4>模板字段</h4>
                        <div id="template-fields-list"></div>
                    </div>
                    <div class="data-fields">
                        <h4>数据字段</h4>
                        <div id="data-fields-list"></div>
                    </div>
                </div>
                <div class="modal-actions">
                    <button class="btn btn-primary" onclick="uiManager.applyManualMatch()">应用匹配</button>
                    <button class="btn btn-secondary" onclick="uiManager.closeManualMatch()">取消</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    async applyManualMatch() {
        try {
            const sessionId = appState.getCurrentSessionId();
            const mappings = this.collectManualMappings();

            const result = await apiManager.request('/api/document-fill/manual-match', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: sessionId,
                    mappings: mappings
                })
            });

            if (result.success) {
                this.closeManualMatch();
                this.navigateToStep(3);
                this.showResult(result.data);
                errorHandler.createNotification('手动匹配应用成功', 'success');
            }
        } catch (error) {
            errorHandler.handleError(error, 'apply_manual_match');
        }
    }

    closeManualMatch() {
        const modal = document.querySelector('.modal');
        if (modal) {
            modal.remove();
        }
    }

    collectManualMappings() {
        // 收集手动匹配的映射关系
        const mappings = {};
        const mappingElements = document.querySelectorAll('.field-mapping');
        mappingElements.forEach(element => {
            const templateField = element.getAttribute('data-template-field');
            const dataField = element.querySelector('.data-field-select').value;
            if (templateField && dataField) {
                mappings[templateField] = dataField;
            }
        });
        return mappings;
    }

    // ==================== 通用动画方法 ====================
    // @AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: common_animation_methods

    showBlockWithAnimation(element) {
        if (!element) return;

        // 如果已经显示，直接返回
        if (element.style.display === 'block' && element.style.opacity === '1') return;

        // 设置初始状态
        element.style.display = 'block';
        element.style.opacity = '0';
        element.style.transform = 'translateY(-10px)';
        element.style.transition = 'opacity 0.3s ease, transform 0.3s ease';

        // 强制重绘
        element.offsetHeight;

        // 应用最终状态
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }

    hideBlockWithAnimation(element) {
        if (!element) return;

        // 如果已经隐藏，直接返回
        if (element.style.display === 'none') return;

        // 设置过渡效果
        element.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        element.style.opacity = '0';
        element.style.transform = 'translateY(-10px)';

        // 动画结束后隐藏元素
        setTimeout(() => {
            element.style.display = 'none';
        }, 300);
    }
}

// ==================== API管理器 ====================
class APIManager {
    constructor() {
        this.baseURL = '';
        this.timeout = 30000;
        this.retries = 3;
        this.retryDelay = 1000;
    }

    async request(endpoint, options = {}) {
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            timeout: this.timeout,
            ...options
        };

        let lastError;
        
        for (let attempt = 1; attempt <= this.retries; attempt++) {
            try {
                const response = await this.makeRequest(endpoint, config);
                return await this.handleResponse(response);
            } catch (error) {
                lastError = error;
                
                if (attempt < this.retries) {
                    await this.delay(this.retryDelay * attempt);
                }
            }
        }

        throw lastError;
    }

    async makeRequest(url, config) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), config.timeout);

        try {
            const response = await fetch(url, {
                method: config.method,
                headers: config.headers,
                body: config.body,
                signal: controller.signal
            });

            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }

    async handleResponse(response) {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const contentType = response.headers.get('Content-Type');
        
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else if (contentType && contentType.includes('application/vnd.openxmlformats-officedocument.wordprocessingml.document')) {
            // 处理docx文件响应
            const blob = await response.blob();
            const filename = this.extractFilenameFromHeaders(response);
            return {
                type: 'document',
                content: blob,
                filename: filename
            };
        } else {
            // 处理其他二进制响应
            const blob = await response.blob();
            return {
                type: 'binary',
                content: blob,
                contentType: contentType
            };
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async uploadFile(endpoint, file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        if (options.additionalData) {
            Object.entries(options.additionalData).forEach(([key, value]) => {
                formData.append(key, value);
            });
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData,
            headers: options.headers
        });

        return await this.handleResponse(response);
    }

    async downloadFile(endpoint, data, filename) {
        const response = await this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });

        if (response.type === 'document' || response.type === 'binary') {
            this.createDownloadLink(response.content, filename || response.filename);
        }
    }

    createDownloadLink(blob, filename) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
    }

    extractFilenameFromHeaders(response) {
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (filenameMatch && filenameMatch[1]) {
                return filenameMatch[1].replace(/['"]/g, '');
            }
        }
        return 'document.docx';
    }
}

// ==================== 全局实例 ====================
const appState = new AppState();
const fileValidator = new FileValidator();
const fileUploadManager = new FileUploadManager();
const errorHandler = new ErrorHandler();
const uiManager = new UIManager();
const apiManager = new APIManager();

// ==================== 应用初始化 ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 初始化办公文档智能代理前端...');
    
    // 设置页面标题
    document.title = "办公文档智能代理";
    
    // 初始化UI
    uiManager.initializeUI();

    // 初始化格式对齐管理器
    formatAlignmentManager.initialize();

    // 加载初始数据
    loadInitialData();

    console.log('✅ 前端初始化完成');
});

async function loadInitialData() {
    try {
        // 加载格式模板
        const formatTemplates = await apiManager.request('/api/format-templates');
        if (formatTemplates.success) {
            updateFormatSelect(formatTemplates.templates);
        }

        // 加载预设风格模板库
        await loadPresetStyles();

        // 加载文档历史
        const documentHistory = await apiManager.request('/api/documents/history');
        if (documentHistory.success) {
            updateHistoryTable(documentHistory.history);
        }

    } catch (error) {
        errorHandler.handleError(error, 'initial_data_loading');
    }
}

function updateFormatSelect(templates) {
    const select = document.getElementById('format-template-select');
    if (select && Array.isArray(templates)) {
        select.innerHTML = '<option value="">选择格式模板</option>';
        templates.forEach(template => {
            const option = document.createElement('option');
            option.value = template.id;
            option.textContent = template.name;
            select.appendChild(option);
        });
    }
}

function updateStyleSelect(templates) {
    const select = document.getElementById('style-template-select');
    if (select && Array.isArray(templates)) {
        select.innerHTML = '<option value="">选择文风模板</option>';
        templates.forEach(template => {
            const option = document.createElement('option');
            option.value = template.id;
            option.textContent = template.name;
            select.appendChild(option);
        });
    }
}

function updateHistoryTable(history) {
    const table = document.querySelector('#document-history-table tbody');
    if (table && Array.isArray(history)) {
        table.innerHTML = '';
        history.forEach(record => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${record.filename}</td>
                <td>${record.operation_type}</td>
                <td>${record.status}</td>
                <td>${new Date(record.created_at).toLocaleString()}</td>
                <td>
                    <button class="btn btn-small" onclick="reapplyOperation('${record.id}')">重新应用</button>
                </td>
            `;
            table.appendChild(row);
        });
    }
}

async function reapplyOperation(recordId) {
    try {
        const result = await apiManager.request(`/api/documents/history/${recordId}/reapply`, {
            method: 'POST'
        });
        
        if (result.success) {
            errorHandler.createNotification('操作重新应用成功', 'success');
        }
    } catch (error) {
        errorHandler.handleError(error, 'reapply_operation');
    }
}

// ==================== AI文风统一界面初始化 ====================

async function loadPresetStyles() {
    try {
        const result = await apiManager.request('/api/style-alignment/preset-styles', {
            timeout: 30000  // 30秒超时，加载预设风格
        });
        if (result.success) {
            displayPresetStyles(result.styles);
        }
    } catch (error) {
        console.error('加载预设风格失败:', error);
        // 显示错误占位符
        const container = document.getElementById('preset-styles-container');
        if (container) {
            container.innerHTML = '<div class="loading-placeholder">❌ 加载预设风格失败</div>';
        }
    }
}

function displayPresetStyles(styles) {
    const container = document.getElementById('preset-styles-container');
    if (!container) return;

    const styleIcons = {
        'academic': '🎓',
        'business': '💼',
        'humorous': '😄',
        'child_friendly': '🧸',
        'technical': '⚙️',
        'creative': '🎨'
    };

    container.innerHTML = '';

    Object.entries(styles).forEach(([styleId, styleInfo]) => {
        const styleCard = document.createElement('div');
        styleCard.className = 'style-card';
        styleCard.dataset.styleId = styleId;

        styleCard.innerHTML = `
            <div class="style-card-header">
                <div class="style-icon">${styleIcons[styleId] || '📝'}</div>
                <h3 class="style-name">${styleInfo.name}</h3>
            </div>
            <p class="style-description">${styleInfo.description}</p>
            <div class="style-examples">
                示例: ${styleInfo.examples ? styleInfo.examples[0] : '暂无示例'}
            </div>
        `;

        // 添加点击事件
        styleCard.addEventListener('click', () => {
            // 移除其他选中状态
            container.querySelectorAll('.style-card').forEach(card => {
                card.classList.remove('selected');
            });

            // 添加选中状态
            styleCard.classList.add('selected');
        });

        container.appendChild(styleCard);
    });
}

function initializeStyleInterface() {
    // 初始化模式选择器
    const modeOptions = document.querySelectorAll('.mode-option');
    modeOptions.forEach(option => {
        option.addEventListener('click', () => {
            const radio = option.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;

                // 更新UI显示
                modeOptions.forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');

                // 切换配置面板
                toggleConfigPanels(radio.value);
            }
        });
    });

    // 初始化标签页切换（排除文档审查模块，它有自己的处理）
    const tabButtons = document.querySelectorAll('.tab-button:not(#scene-review .tab-button)');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            switchTab(tabId);
        });
    });

    // 初始化温度滑块
    const temperatureSlider = document.getElementById('style-temperature');
    const temperatureValue = document.querySelector('.temperature-value');
    if (temperatureSlider && temperatureValue) {
        temperatureSlider.addEventListener('input', (e) => {
            temperatureValue.textContent = e.target.value;
        });
    }

    const fewShotSlider = document.getElementById('few-shot-temperature');
    const fewShotValue = document.querySelector('.few-shot-temperature-value');
    if (fewShotSlider && fewShotValue) {
        fewShotSlider.addEventListener('input', (e) => {
            fewShotValue.textContent = e.target.value;
        });
    }

    // 初始化字符计数器
    const contentTextarea = document.getElementById('style-content-text');
    const charCounter = document.getElementById('char-count');
    if (contentTextarea && charCounter) {
        contentTextarea.addEventListener('input', () => {
            const count = contentTextarea.value.length;
            charCounter.textContent = count;

            // 更新计数器样式
            charCounter.parentElement.classList.remove('warning', 'error');
            if (count > 1800) {
                charCounter.parentElement.classList.add('warning');
            }
            if (count > 2000) {
                charCounter.parentElement.classList.add('error');
            }
        });
    }

    // 初始化开始处理按钮
    const startButton = document.getElementById('start-style-processing');
    if (startButton) {
        startButton.addEventListener('click', () => {
            uiManager.handleStyleAlignment(startButton);
        });
    }

    // 初始化清空内容按钮
    const clearButton = document.getElementById('clear-content');
    if (clearButton) {
        clearButton.addEventListener('click', () => {
            if (confirm('确定要清空所有内容吗？')) {
                clearAllContent();
            }
        });
    }

    // 初始化结果操作按钮
    initializeResultButtons();
}

function toggleConfigPanels(mode) {
    const presetConfig = document.getElementById('style-preset-config');
    const fewShotConfig = document.getElementById('style-few-shot-config');

    if (mode === 'preset') {
        presetConfig.style.display = 'block';
        fewShotConfig.style.display = 'none';
    } else if (mode === 'few-shot') {
        presetConfig.style.display = 'none';
        fewShotConfig.style.display = 'block';
    }
}

function switchTab(tabId) {
    // 更新标签按钮状态（排除文档审查模块）
    document.querySelectorAll('.tab-button:not(#scene-review .tab-button)').forEach(btn => {
        btn.classList.remove('active');
    });
    const targetButton = document.querySelector(`[data-tab="${tabId}"]:not(#scene-review [data-tab="${tabId}"])`);
    if (targetButton) {
        targetButton.classList.add('active');
    }

    // 获取当前场景
    const currentScene = document.querySelector('.scene-section:not(.hidden)');
    const sceneId = currentScene?.id;

    // 只隐藏当前场景内的.tab-content（排除文档审查模块）
    if (currentScene) {
        currentScene.querySelectorAll('.tab-content:not(.review-tab-content)').forEach(content => {
            content.style.display = 'none';
        });
    }

    // 根据当前场景确定正确的标签页ID
    let targetId = `${tabId}-tab`;
    if (sceneId === 'scene-style') {
        targetId = `style-${tabId}-tab`;
    } else if (sceneId === 'scene-format') {
        targetId = `format-${tabId}-tab`;
    }

    const targetContent = document.getElementById(targetId);
    if (targetContent && !targetContent.closest('#scene-review')) {
        targetContent.style.display = 'block';
    }
}

function clearAllContent() {
    // 清空文本输入
    const textArea = document.getElementById('style-content-text');
    if (textArea) {
        textArea.value = '';
        textArea.dispatchEvent(new Event('input')); // 触发字符计数更新
    }

    // 清空文件上传
    const fileInput = document.getElementById('upload-content-file');
    if (fileInput) {
        fileInput.value = '';
    }

    // 清空参考文档
    const refInput = document.getElementById('upload-reference-doc');
    if (refInput) {
        refInput.value = '';
    }

    // 清空风格描述
    const descInput = document.getElementById('style-description');
    if (descInput) {
        descInput.value = '';
    }
}

function initializeResultButtons() {
    // 撤销按钮
    const undoButton = document.getElementById('undo-changes');
    if (undoButton) {
        undoButton.addEventListener('click', () => {
            // TODO: 实现撤销功能
            console.log('撤销功能待实现');
        });
    }

    // 重做按钮
    const redoButton = document.getElementById('redo-changes');
    if (redoButton) {
        redoButton.addEventListener('click', () => {
            // TODO: 实现重做功能
            console.log('重做功能待实现');
        });
    }

    // 重新生成按钮
    const regenerateButton = document.getElementById('regenerate-style');
    if (regenerateButton) {
        regenerateButton.addEventListener('click', () => {
            // 重新执行当前的风格处理
            const startButton = document.getElementById('start-style-processing');
            if (startButton) {
                uiManager.handleStyleAlignment(startButton);
            }
        });
    }

    // 预览按钮
    const previewButton = document.getElementById('preview-result');
    if (previewButton) {
        previewButton.addEventListener('click', () => {
            // TODO: 实现预览功能
            console.log('预览功能待实现');
        });
    }

    // 导出按钮
    const exportButton = document.getElementById('export-result');
    if (exportButton) {
        exportButton.addEventListener('click', () => {
            showExportOptions();
        });
    }
}

function showExportOptions() {
    const exportArea = document.getElementById('style-export-area');
    const resultArea = document.getElementById('style-result-area');

    if (exportArea && resultArea) {
        resultArea.style.display = 'none';
        exportArea.style.display = 'block';

        // 初始化导出按钮
        const confirmButton = document.getElementById('confirm-export');
        const backButton = document.getElementById('back-to-result');

        if (confirmButton) {
            confirmButton.onclick = () => {
                const selectedFormat = document.querySelector('input[name="export-format"]:checked')?.value;
                if (selectedFormat) {
                    performExport(selectedFormat);
                }
            };
        }

        if (backButton) {
            backButton.onclick = () => {
                exportArea.style.display = 'none';
                resultArea.style.display = 'block';
            };
        }
    }
}

async function performExport(format) {
    if (!uiManager.currentStyleResult) {
        errorHandler.handleError(new Error('没有可导出的结果'), 'validation');
        return;
    }

    const content = uiManager.currentStyleResult.generated;
    const filename = `style_result_${Date.now()}.${format}`;

    if (format === 'txt') {
        // 导出为TXT（本地处理）
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        apiManager.createDownloadLink(blob, filename);
        errorHandler.createNotification('TXT文件导出成功', 'success');
    } else {
        // 其他格式通过API导出
        try {
            // 显示加载状态
            errorHandler.createNotification(`正在导出${format.toUpperCase()}格式...`, 'info');

            // 获取当前任务ID
            const taskId = uiManager.currentStyleResult.taskId || uiManager.currentStyleResult.task_id;

            if (!taskId) {
                console.error('❌ 无法获取任务ID，当前结果:', uiManager.currentStyleResult);
                throw new Error('无法获取任务ID');
            }

            // 调用导出API
            const requestData = {
                task_id: taskId,
                format: format
            };

            const response = await fetch('/api/style-alignment/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (result.success) {
                // 创建下载链接
                const downloadUrl = result.download_url;
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = result.filename;
                link.style.display = 'none';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                errorHandler.createNotification(`${format.toUpperCase()}文件导出成功`, 'success');
            } else {
                throw new Error(result.error || '导出失败');
            }
        } catch (error) {
            console.error('导出失败:', error);
            errorHandler.createNotification(`${format.toUpperCase()}格式导出失败: ${error.message}`, 'error');
        }
    }
}

// ==================== 格式对齐增强管理器 ====================
class FormatAlignmentManager {
    constructor() {
        this.currentMode = 'preset'; // 'preset' or 'few-shot'
        this.selectedTemplate = null;
        this.uploadedDocument = null;
        this.uploadedTemplateDocument = null; // Few-Shot模式的模板文档
        this.currentTaskId = null;
        this.processingStep = 1;
        this.templates = [];
        this.presetTemplates = []; // 精选的6个预设模板
        this.isInitialized = false; // 初始化标志
        this.eventsBound = false; // 事件绑定标志
    }

    async initialize() {
        console.log('🎯 ===== 开始初始化格式对齐管理器 =====');
        console.log('🎯 initialize方法被调用');

        // 加载模板（每次都重新加载以确保最新数据）
        await this.loadFormatTemplates();

        // 只在第一次初始化时绑定事件
        if (!this.eventsBound) {
            console.log('🔗 准备绑定事件...');
            this.bindEvents();
            this.eventsBound = true;
            console.log('✅ 事件绑定完成');
        } else {
            console.log('⚠️ 事件已经绑定过，跳过绑定');
        }

        // 初始化界面
        this.initializeInterface();

        // 确保当前模式的界面状态正确
        this.handleModeSwitch(this.currentMode);

        this.isInitialized = true;
        console.log('✅ 格式对齐管理器初始化完成');
    }

    async loadFormatTemplates() {
        try {
            console.log('📚 加载格式模板...');
            const response = await apiManager.request('/api/format-alignment/templates', {
                method: 'GET'
            });

            if (response.success) {
                this.templates = response.templates;
                this.selectPresetTemplates();
                this.renderTemplateGallery();
                console.log(`✅ 加载了 ${this.templates.length} 个格式模板，精选了 ${this.presetTemplates.length} 个预设模板`);
            } else {
                console.error('❌ 加载格式模板失败:', response.error);
                errorHandler.createNotification('加载格式模板失败', 'error');
            }
        } catch (error) {
            console.error('❌ 加载格式模板异常:', error);
            errorHandler.createNotification('加载格式模板异常', 'error');
        }
    }

    selectPresetTemplates() {
        // 智能选择3个预设模板，基于名称和使用频率
        const priorityKeywords = ['测试', '通知', '报告', '管理', '公文', '论文', '规定', '文档'];
        const selected = [];

        // 首先选择包含优先关键词的模板
        for (const keyword of priorityKeywords) {
            const template = this.templates.find(t =>
                t.name.includes(keyword) && !selected.find(s => s.id === t.id)
            );
            if (template && selected.length < 3) {
                selected.push(template);
            }
        }

        // 如果不足3个，从剩余模板中选择
        if (selected.length < 3) {
            const remaining = this.templates.filter(t =>
                !selected.find(s => s.id === t.id)
            );

            // 按创建时间排序，选择较新的模板
            remaining.sort((a, b) => new Date(b.created_time) - new Date(a.created_time));

            // 确保选择足够的模板达到3个
            const needed = 3 - selected.length;
            for (let i = 0; i < Math.min(needed, remaining.length); i++) {
                selected.push(remaining[i]);
            }
        }

        // 确保最终有3个模板
        this.presetTemplates = selected.slice(0, 3);

        // 如果仍然不足3个，重复使用已有模板
        while (this.presetTemplates.length < 3 && this.templates.length > 0) {
            const randomTemplate = this.templates[Math.floor(Math.random() * this.templates.length)];
            if (!this.presetTemplates.find(t => t.id === randomTemplate.id)) {
                this.presetTemplates.push(randomTemplate);
            }
        }

        console.log('🎯 精选预设模板 (共' + this.presetTemplates.length + '个):', this.presetTemplates.map(t => t.name));
    }

    renderTemplateGallery() {
        const container = document.getElementById('preset-formats-container');
        if (!container) return;

        // 根据当前模式决定显示哪些模板
        const templatesToShow = this.currentMode === 'preset' ? this.presetTemplates : [];

        if (templatesToShow.length === 0) {
            container.innerHTML = '<div class="loading-placeholder">暂无格式模板</div>';
            return;
        }

        let html = '';
        let isFirst = true;

        // 定义模板图标映射
        const templateIcons = {
            '测试': '🧪',
            '通知': '📢',
            '报告': '📊',
            '管理': '📋',
            '公文': '📜',
            '论文': '🎓',
            '规定': '📏',
            '文档': '📄'
        };

        templatesToShow.forEach(template => {
            const isSelected = isFirst ? 'selected' : '';
            if (isFirst) {
                this.selectedTemplate = template.id;
                isFirst = false;
            }

            // 根据模板名称选择合适的图标
            let icon = '📄'; // 默认图标
            for (const [keyword, emoji] of Object.entries(templateIcons)) {
                if (template.name.includes(keyword)) {
                    icon = emoji;
                    break;
                }
            }

            // 生成简短的描述
            const shortName = template.name.length > 20 ?
                template.name.substring(0, 20) + '...' : template.name;

            const description = template.description ||
                `专业的${template.name.includes('测试') ? '测试' :
                template.name.includes('通知') ? '通知' :
                template.name.includes('报告') ? '报告' :
                template.name.includes('管理') ? '管理' :
                template.name.includes('公文') ? '公文' :
                template.name.includes('论文') ? '学术' : '文档'}格式模板`;

            html += `
                <div class="style-card ${isSelected}" data-template-id="${template.id}">
                    <div class="style-card-header">
                        <div class="style-icon">${icon}</div>
                        <h4 class="style-name">${shortName}</h4>
                    </div>
                    <div class="style-description">
                        ${description}
                    </div>
                    <div class="style-examples">
                        适用于：${template.name.includes('测试') ? '功能测试、系统验证' :
                        template.name.includes('通知') ? '公告发布、信息传达' :
                        template.name.includes('报告') ? '数据分析、工作汇报' :
                        template.name.includes('管理') ? '制度规范、流程管理' :
                        template.name.includes('公文') ? '正式文件、官方文档' :
                        template.name.includes('论文') ? '学术写作、研究报告' : '通用文档格式'}
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
        console.log(`✅ 渲染了 ${templatesToShow.length} 个格式模板`);
    }

    bindEvents() {
        // @AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: fix_mode_switch
        console.log('🔗 ===== 开始绑定格式对齐模块事件 =====');
        console.log('🔗 bindEvents方法被调用');

        // 保存this引用
        const self = this;

        // 测试DOM元素是否存在
        const formatScene = document.getElementById('scene-format');
        const modeOptions = document.querySelectorAll('#scene-format .mode-option');
        console.log('🔍 DOM检查 - 格式对齐场景:', formatScene);
        console.log('🔍 DOM检查 - 模式选项数量:', modeOptions.length);
        modeOptions.forEach((option, index) => {
            console.log(`🔍 模式选项 ${index}:`, option, '数据模式:', option.dataset.mode);
        });

        // 模式切换事件 - 支持单选按钮change事件（限制在格式对齐场景内）
        document.addEventListener('change', (e) => {
            if (e.target.name === 'format-mode' && e.target.closest('#scene-format')) {
                console.log('🔄 格式对齐模式切换事件触发:', e.target.value);
                self.handleModeSwitch(e.target.value);
            }
        });

        // 模式切换事件 - 支持点击模式选项容器（限制在格式对齐场景内）
        document.addEventListener('click', (e) => {
            // 只在格式对齐场景中处理
            const formatScene = document.getElementById('scene-format');
            if (!formatScene || !formatScene.contains(e.target)) {
                return; // 不在格式对齐场景中，直接返回
            }

            // 只处理模式选项的点击，忽略其他元素
            const modeOption = e.target.closest('#scene-format .mode-option');
            if (!modeOption || !modeOption.dataset.mode) {
                return; // 不是模式选项，直接返回
            }

            const mode = modeOption.dataset.mode;
            const radioButton = modeOption.querySelector('input[type="radio"]');

            // 检查是否需要切换模式（基于当前模式而不是单选按钮状态）
            if (mode !== self.currentMode) {
                // 更新单选按钮状态
                if (radioButton) {
                    radioButton.checked = true;
                }
                console.log('🔄 通过点击容器切换格式对齐模式:', mode);
                self.handleModeSwitch(mode);
            }
        });

        // 模板选择事件 - 支持新的样式类名
        document.addEventListener('click', (e) => {
            const templateCard = e.target.closest('.format-template-card') || e.target.closest('.style-card');
            if (templateCard) {
                self.handleTemplateSelection(templateCard);
            }
        });

        // 文档上传事件
        const uploadInput = document.getElementById('upload-format-document');
        if (uploadInput) {
            uploadInput.addEventListener('change', (e) => {
                self.handleDocumentUpload(e.target.files[0]);
            });
        }

        // Few-Shot模式模板文档上传事件
        const templateUploadInput = document.getElementById('upload-format-template');
        if (templateUploadInput) {
            templateUploadInput.addEventListener('change', (e) => {
                self.handleTemplateDocumentUpload(e.target.files[0]);
            });
        }

        // 文风统一模块 - Few-Shot参考文档上传事件
        const referenceDocInput = document.getElementById('upload-reference-doc');
        if (referenceDocInput) {
            referenceDocInput.addEventListener('change', (e) => {
                self.handleReferenceDocumentUpload(e.target.files[0]);
            });
        }

        // 标签页切换事件
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-button')) {
                this.handleTabSwitch(e.target);
            }
        });



        // 开始格式对齐按钮
        const startBtn = document.getElementById('start-format-alignment');
        if (startBtn) {
            startBtn.addEventListener('click', () => {
                this.startFormatAlignment();
            });
        }

        // 清空内容按钮 - 格式对齐模块专用
        const clearFormatBtn = document.getElementById('clear-format-content');
        if (clearFormatBtn) {
            console.log('✅ 找到清空内容按钮，正在绑定事件...');
            clearFormatBtn.addEventListener('click', () => {
                console.log('🖱️ 清空内容按钮被点击');
                if (confirm('确定要清空所有内容吗？')) {
                    console.log('✅ 用户确认清空内容');
                    this.clearFormatContent();
                } else {
                    console.log('❌ 用户取消清空操作');
                }
            });
        } else {
            console.log('❌ 未找到清空内容按钮元素: clear-format-content');
        }

        // 下载按钮
        const downloadBtn = document.getElementById('download-formatted-document');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                this.downloadFormattedDocument();
            });
        }

        // 移除格式对齐导出按钮事件绑定，因为已删除该按钮

        // 重新开始按钮
        const restartBtn = document.getElementById('restart-format-process');
        if (restartBtn) {
            restartBtn.addEventListener('click', () => {
                this.restartProcess();
            });
        }

        // 导出格式选择 - 只针对格式对齐模块
        document.addEventListener('click', (e) => {
            const formatScene = document.getElementById('scene-format');
            if (formatScene && formatScene.contains(e.target)) {
                const formatButton = e.target.closest('.format-buttons .btn');
                if (formatButton) {
                    this.handleFormatSelection(formatButton);
                }
            }
        });

        // Few-Shot温度滑块事件
        const fewShotSlider = document.getElementById('few-shot-format-strength');
        const fewShotValue = document.querySelector('.few-shot-temperature-value');
        if (fewShotSlider && fewShotValue) {
            fewShotSlider.addEventListener('input', (e) => {
                fewShotValue.textContent = e.target.value;
            });
        }
    }

    handleModeSwitch(mode) {
        console.log('🔄 格式对齐模式切换:', mode);
        console.log('🧹 开始清理模式切换时的文件上传状态...');

        // 清空之前的选择和状态
        this.selectedTemplate = null;
        this.uploadedDocument = null;
        this.uploadedTemplateDocument = null;
        this.currentTaskId = null;

        // 清空文件上传输入框的值
        const documentInput = document.getElementById('upload-format-document');
        if (documentInput) {
            documentInput.value = '';
        }

        const templateInput = document.getElementById('upload-format-template');
        if (templateInput) {
            templateInput.value = '';
        }

        // 完全重置文件上传区域的状态
        const uploadArea = document.getElementById('format-document-upload-area');
        if (uploadArea) {
            uploadArea.classList.remove('has-file');
            console.log('✅ 已移除待处理文档上传区域的has-file类');
            const uploadText = uploadArea.querySelector('.file-upload-text');
            if (uploadText) {
                uploadText.textContent = '点击或拖拽上传TXT待处理文档';
                uploadText.style.color = ''; // 重置颜色
                console.log('✅ 已重置待处理文档上传区域的显示文本');
            }
            const uploadHint = uploadArea.querySelector('.file-upload-hint');
            if (uploadHint) {
                uploadHint.textContent = '仅支持 .txt 格式';
                uploadHint.style.color = ''; // 重置颜色
            }
        }

        const templateUploadArea = document.getElementById('format-template-upload');
        if (templateUploadArea) {
            templateUploadArea.classList.remove('has-file');
            console.log('✅ 已移除格式模板上传区域的has-file类');
            const templateUploadText = templateUploadArea.querySelector('.file-upload-text');
            if (templateUploadText) {
                templateUploadText.textContent = '点击或拖拽上传TXT格式模板文档';
                templateUploadText.style.color = ''; // 重置颜色
                console.log('✅ 已重置格式模板上传区域的显示文本');
            }
            const templateUploadHint = templateUploadArea.querySelector('.file-upload-hint');
            if (templateUploadHint) {
                templateUploadHint.textContent = '仅支持 .txt 格式';
                templateUploadHint.style.color = ''; // 重置颜色
            }
        }

        console.log('✅ 模式切换时的文件上传状态清理完成');

        // 更新当前模式
        this.currentMode = mode;

        // 显示/隐藏相应的配置区域 - 添加平滑动画
        const presetConfig = document.getElementById('format-preset-config');
        const fewShotConfig = document.getElementById('format-few-shot-config');

        if (mode === 'preset') {
            // 显示预设配置，隐藏Few-Shot配置
            this.showBlockWithAnimation(presetConfig);
            this.hideBlockWithAnimation(fewShotConfig);
            this.renderTemplateGallery(); // 重新渲染预设模板
        } else if (mode === 'few-shot') {
            // 显示Few-Shot配置，隐藏预设配置
            this.showBlockWithAnimation(fewShotConfig);
            this.hideBlockWithAnimation(presetConfig);
        }

        // 更新模式选择的视觉状态
        this.updateModeSelectionUI(mode);

        // 禁用开始按钮，因为文件已被清空
        const startBtn = document.getElementById('start-format-alignment');
        if (startBtn) {
            startBtn.disabled = true;
        }

        // 重置步骤状态
        this.updateStepStatus(1, true);
        this.resetProcessingState();

        // 额外确保文件上传状态被完全清空
        setTimeout(() => {
            this.forceResetFileUploadState();
        }, 100); // 延迟100ms确保所有DOM操作完成

        console.log('✅ 格式对齐模式切换完成，已清空文件上传状态');
    }

    forceResetFileUploadState() {
        console.log('🔧 强制重置文件上传状态...');

        // 强制重置待处理文档上传区域
        const uploadArea = document.getElementById('format-document-upload-area');
        if (uploadArea) {
            uploadArea.classList.remove('has-file');
            const textElement = uploadArea.querySelector('.file-upload-text');
            const hintElement = uploadArea.querySelector('.file-upload-hint');

            if (textElement) {
                textElement.textContent = '点击或拖拽上传TXT待处理文档';
                textElement.style.color = '';
                textElement.style.fontWeight = '';
            }
            if (hintElement) {
                hintElement.textContent = '仅支持 .txt 格式';
                hintElement.style.color = '';
            }
            console.log('✅ 强制重置待处理文档上传区域');
        }

        // 强制重置模板文档上传区域
        const templateArea = document.getElementById('format-template-upload');
        if (templateArea) {
            templateArea.classList.remove('has-file');
            const textElement = templateArea.querySelector('.file-upload-text');
            const hintElement = templateArea.querySelector('.file-upload-hint');

            if (textElement) {
                textElement.textContent = '点击或拖拽上传TXT格式模板文档';
                textElement.style.color = '';
                textElement.style.fontWeight = '';
            }
            if (hintElement) {
                hintElement.textContent = '仅支持 .txt 格式';
                hintElement.style.color = '';
            }
            console.log('✅ 强制重置模板文档上传区域');
        }

        // 强制重置文件输入框 - 使用更彻底的方法
        const documentInput = document.getElementById('upload-format-document');
        const templateInput = document.getElementById('upload-format-template');

        if (documentInput) {
            // 彻底重置文件输入框
            const newDocumentInput = documentInput.cloneNode(true);
            documentInput.parentNode.replaceChild(newDocumentInput, documentInput);

            // 重新绑定事件
            const self = this;
            newDocumentInput.addEventListener('change', (e) => {
                self.handleDocumentUpload(e.target.files[0]);
            });
            console.log('✅ 彻底重置文档输入框并重新绑定事件');
        }

        if (templateInput) {
            // 彻底重置文件输入框
            const newTemplateInput = templateInput.cloneNode(true);
            templateInput.parentNode.replaceChild(newTemplateInput, templateInput);

            // 重新绑定事件
            const self = this;
            newTemplateInput.addEventListener('change', (e) => {
                self.handleTemplateDocumentUpload(e.target.files[0]);
            });
            console.log('✅ 彻底重置模板输入框并重新绑定事件');
        }

        // 强制重置内部状态
        this.uploadedDocument = null;
        this.uploadedTemplateDocument = null;
        console.log('✅ 强制重置内部文件状态');

        console.log('✅ 强制重置文件上传状态完成');
    }

    showBlockWithAnimation(element) {
        // 使用UIManager的通用动画方法
        if (window.uiManager) {
            uiManager.showBlockWithAnimation(element);
        } else {
            // 降级处理
            if (element) {
                element.style.display = 'block';
            }
        }
    }

    hideBlockWithAnimation(element) {
        // 使用UIManager的通用动画方法
        if (window.uiManager) {
            uiManager.hideBlockWithAnimation(element);
        } else {
            // 降级处理
            if (element) {
                element.style.display = 'none';
            }
        }
    }

    updateModeSelectionUI(mode) {
        // 更新格式对齐模式选择的视觉状态和单选按钮状态
        console.log('🔄 更新模式选择UI:', mode);

        const modeOptions = document.querySelectorAll('#scene-format .mode-option');
        modeOptions.forEach(option => {
            const optionMode = option.dataset.mode;
            const radioButton = option.querySelector('input[type="radio"]');

            if (optionMode === mode) {
                // 选中状态
                option.classList.add('selected');
                if (radioButton) {
                    radioButton.checked = true;
                    console.log('✅ 设置单选按钮为选中:', optionMode);
                }
            } else {
                // 未选中状态
                option.classList.remove('selected');
                if (radioButton) {
                    radioButton.checked = false;
                    console.log('❌ 设置单选按钮为未选中:', optionMode);
                }
            }
        });
    }

    handleTabSwitch(button) {
        // 移除格式对齐模块内的活动状态
        document.querySelectorAll('#scene-format .tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelectorAll('#scene-format .tab-content').forEach(content => {
            content.style.display = 'none';
        });

        // 激活当前标签
        button.classList.add('active');
        const tabId = 'format-' + button.dataset.tab + '-tab';
        const tabContent = document.getElementById(tabId);
        if (tabContent) {
            tabContent.style.display = 'block';
        }
    }

    async handleTemplateDocumentUpload(file) {
        if (!file) return;

        try {
            console.log('📄 上传格式模板文档:', file.name);

            // 验证文件 - 格式对齐模块只支持TXT格式
            const validation = fileValidator.validateFile(file, 'format_alignment');
            if (!validation.isValid) {
                errorHandler.handleError(new Error(validation.errors.join(', ')), 'file_validation');
                return;
            }

            // 读取文件内容
            const content = await this.readFileContent(file);
            this.uploadedTemplateDocument = {
                name: file.name,
                content: content,
                size: file.size
            };

            // 更新UI
            this.updateTemplateUploadStatus(file.name);
            this.checkFewShotReadyToProcess();

            console.log('✅ 格式模板文档上传成功');
        } catch (error) {
            console.error('❌ 格式模板文档上传失败:', error);
            errorHandler.createNotification('格式模板文档上传失败', 'error');
        }
    }

    updateTemplateUploadStatus(fileName) {
        const uploadArea = document.getElementById('format-template-upload');
        if (uploadArea) {
            uploadArea.classList.add('has-file');
            const textElement = uploadArea.querySelector('.file-upload-text');
            if (textElement) {
                textElement.textContent = `已选择: ${fileName}`;
            }
        }
    }

    checkFewShotReadyToProcess() {
        const startBtn = document.getElementById('start-format-alignment');
        if (startBtn && this.currentMode === 'few-shot' &&
            this.uploadedTemplateDocument && this.uploadedDocument) {
            startBtn.disabled = false;
            this.updateStepStatus(4, true);
        }
    }

    resetProcessingState() {
        // 重置文件上传状态
        const uploadAreas = document.querySelectorAll('.file-upload-area');
        uploadAreas.forEach(area => {
            area.classList.remove('has-file');
            const textElement = area.querySelector('.file-upload-text');
            if (textElement) {
                if (area.id === 'format-template-upload') {
                    textElement.textContent = '点击或拖拽上传TXT格式模板文档';
                } else {
                    textElement.textContent = '点击或拖拽上传TXT待处理文档';
                }
            }
            const hintElement = area.querySelector('.file-upload-hint');
            if (hintElement) {
                hintElement.textContent = '仅支持 .txt 格式';
            }
        });

        // 重置按钮状态
        const startBtn = document.getElementById('start-format-alignment');
        if (startBtn) {
            startBtn.disabled = true;
        }

        // 隐藏结果区域
        const comparisonBlock = document.getElementById('format-comparison-preview');
        const exportSection = document.getElementById('format-export-results');
        if (comparisonBlock) comparisonBlock.style.display = 'none';
        if (exportSection) exportSection.style.display = 'none';
    }

    handleTemplateSelection(card) {
        // 移除其他选中状态 - 支持两种CSS类名
        document.querySelectorAll('.format-template-card, .style-card').forEach(c => {
            c.classList.remove('selected');
        });

        // 设置当前选中
        card.classList.add('selected');
        this.selectedTemplate = card.dataset.templateId;

        console.log('✅ 选择格式模板:', this.selectedTemplate);
        this.updateStepStatus(2, true); // 更新为步骤2，因为现在是配置格式步骤
    }

    async handleDocumentUpload(file) {
        if (!file) return;

        try {
            console.log('📄 上传文档:', file.name);

            // 验证文件 - 格式对齐模块只支持TXT格式
            const validation = fileValidator.validateFile(file, 'format_alignment');
            if (!validation.isValid) {
                errorHandler.handleError(new Error(validation.errors.join(', ')), 'file_validation');
                return;
            }

            // 读取文件内容
            const content = await this.readFileContent(file);
            this.uploadedDocument = {
                name: file.name,
                content: content,
                size: file.size
            };

            // 更新UI
            this.updateUploadStatus(file.name);
            this.updateStepStatus(2, true);
            this.checkReadyToProcess();

            console.log('✅ 文档上传成功');
        } catch (error) {
            console.error('❌ 文档上传失败:', error);
            errorHandler.createNotification('文档上传失败', 'error');
        }
    }

    readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsText(file, 'UTF-8');
        });
    }



    updateUploadStatus(fileName) {
        const uploadArea = document.getElementById('format-document-upload-area');
        if (uploadArea) {
            uploadArea.classList.add('has-file');
            const textElement = uploadArea.querySelector('.file-upload-text');
            if (textElement) {
                textElement.textContent = `已选择: ${fileName}`;
            }
        }
    }

    checkReadyToProcess() {
        const startBtn = document.getElementById('start-format-alignment');
        if (!startBtn) return;

        let isReady = false;

        if (this.currentMode === 'preset') {
            // 预设模式：需要选择模板和上传文档
            isReady = this.selectedTemplate && this.uploadedDocument;
        } else if (this.currentMode === 'few-shot') {
            // Few-Shot模式：需要上传模板文档和待处理文档
            isReady = this.uploadedTemplateDocument && this.uploadedDocument;
        }

        startBtn.disabled = !isReady;

        if (isReady) {
            this.updateStepStatus(4, true);
        }
    }

    async startFormatAlignment() {
        // 检查不同模式的必要条件
        if (this.currentMode === 'preset' && (!this.selectedTemplate || !this.uploadedDocument)) {
            errorHandler.createNotification('请先选择模板和上传文档', 'warning');
            return;
        }

        if (this.currentMode === 'few-shot' && (!this.uploadedTemplateDocument || !this.uploadedDocument)) {
            errorHandler.createNotification('请先上传格式模板文档和待处理文档', 'warning');
            return;
        }

        try {
            console.log('🚀 开始格式对齐...');

            // 开始新的格式对齐时，先隐藏之前的导出结果和完成提示
            this.hideExportSection();

            // 隐藏步骤4的完成提示，因为要开始新的处理
            const previewBlock = document.getElementById('format-comparison-preview');
            if (previewBlock) {
                previewBlock.style.display = 'none';
            }

            this.updateStepStatus(4, true);
            this.showProgress();

            // 显示详细的进度提示
            this.updateProgressText('正在准备文件上传...');

            // 步骤1: 准备上传文件
            const uploadFormData = new FormData();
            const blob = new Blob([this.uploadedDocument.content], { type: 'text/plain' });
            uploadFormData.append('files', blob, this.uploadedDocument.name);

            // Few-Shot模式需要额外上传模板文档
            if (this.currentMode === 'few-shot' && this.uploadedTemplateDocument) {
                const templateBlob = new Blob([this.uploadedTemplateDocument.content], { type: 'text/plain' });
                uploadFormData.append('files', templateBlob, this.uploadedTemplateDocument.name);
            }

            // 使用AbortController来控制超时
            const uploadController = new AbortController();
            const uploadTimeoutId = setTimeout(() => uploadController.abort(), 60000); // 1分钟超时

            const uploadResponse = await fetch('/api/format-alignment/upload', {
                method: 'POST',
                body: uploadFormData,
                signal: uploadController.signal
            });

            clearTimeout(uploadTimeoutId);

            if (!uploadResponse.ok) {
                throw new Error('文件上传失败');
            }

            const uploadResult = await uploadResponse.json();
            if (uploadResult.code !== 0) {
                throw new Error(uploadResult.message || '文件上传失败');
            }

            const uploadId = uploadResult.data.upload_id;
            console.log('✅ 文件上传成功，upload_id:', uploadId);

            // 更新进度提示
            this.updateProgressText('正在进行格式对齐处理...');

            // 步骤2: 根据模式调用不同的处理API
            let formatInstruction = '';
            let processOptions = this.getFormatOptions();

            if (this.currentMode === 'preset') {
                formatInstruction = `使用模板ID: ${this.selectedTemplate} 进行格式对齐`;
                processOptions.template_id = this.selectedTemplate;
            } else {
                const formatDescription = document.getElementById('format-description')?.value || '';
                formatInstruction = `学习上传的格式模板文档的格式规范，并应用到待处理文档上。${formatDescription ? '格式要求：' + formatDescription : ''}`;
                processOptions.few_shot_mode = true;
                processOptions.template_document = this.uploadedTemplateDocument.name;
            }

            const processResponse = await apiManager.request('/api/format-alignment/process', {
                method: 'POST',
                body: JSON.stringify({
                    upload_id: uploadId,
                    format_instruction: formatInstruction,
                    options: processOptions
                }),
                timeout: 120000  // 2分钟超时，格式对齐可能需要较长时间
            });

            if (processResponse.code === 0) {
                this.currentTaskId = processResponse.data.task_id;
                // 直接跳过预览，显示导出选项
                this.updateStepStatus(4, true);
                this.showExportSection();
                // 隐藏对比预览容器
                const comparisonContainer = document.getElementById('format-comparison-container');
                if (comparisonContainer) {
                    comparisonContainer.style.display = 'none';
                }
                // 显示完成提示
                const previewBlock = document.getElementById('format-comparison-preview');
                if (previewBlock) {
                    previewBlock.style.display = 'block';
                }
                errorHandler.createNotification('格式对齐完成，请在导出处理结果中下载', 'success');
            } else {
                throw new Error(processResponse.message || '格式对齐失败');
            }

        } catch (error) {
            console.error('❌ 格式对齐失败:', error);

            // 重置步骤状态
            this.updateStepStatus(4, false);
            this.updateStepStatus(5, false);

            // 隐藏导出部分，因为处理失败了
            this.hideExportSection();

            // 隐藏步骤4的完成提示
            const previewBlock = document.getElementById('format-comparison-preview');
            if (previewBlock) {
                previewBlock.style.display = 'none';
            }

            // 根据错误类型提供更友好的错误信息
            let errorMessage = '格式对齐失败';
            if (error.name === 'AbortError') {
                errorMessage = '请求超时，请检查网络连接或稍后重试';
            } else if (error.message.includes('上传失败')) {
                errorMessage = '文件上传失败，请检查文件格式或网络连接';
            } else if (error.message) {
                errorMessage = '格式对齐失败: ' + error.message;
            }

            errorHandler.createNotification(errorMessage, 'error');
        } finally {
            this.hideProgress();
        }
    }

    getFormatOptions() {
        const baseOptions = {
            preserve_structure: document.getElementById('preserve-structure')?.checked || true,
            preserve_images: document.getElementById('preserve-images')?.checked || true,
            preserve_tables: document.getElementById('preserve-tables')?.checked || true
        };

        if (this.currentMode === 'preset') {
            return {
                ...baseOptions,
                action: document.getElementById('format-action')?.value || '格式对齐',
                strength: parseFloat(document.getElementById('format-strength')?.value || 0.7),
                language: document.getElementById('format-language')?.value || 'auto'
            };
        } else {
            return {
                ...baseOptions,
                strength: parseFloat(document.getElementById('few-shot-format-strength')?.value || 0.7),
                format_description: document.getElementById('format-description')?.value || ''
            };
        }
    }

    showProgress() {
        const progressContainer = document.getElementById('format-progress-container');
        const comparisonBlock = document.getElementById('format-comparison-preview');

        if (progressContainer && comparisonBlock) {
            comparisonBlock.style.display = 'block';
            progressContainer.style.display = 'block';

            // 模拟进度
            this.animateProgress();
        }
    }

    animateProgress() {
        const progressFill = document.getElementById('format-progress-fill');
        const progressText = document.getElementById('format-progress-text');

        if (!progressFill || !progressText) return;

        const steps = [
            { progress: 20, text: '正在分析文档结构...' },
            { progress: 40, text: '正在加载格式模板...' },
            { progress: 60, text: '正在应用格式规则...' },
            { progress: 80, text: '正在生成格式化文档...' },
            { progress: 100, text: '格式对齐完成！' }
        ];

        let currentStep = 0;
        const interval = setInterval(() => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                progressFill.style.width = step.progress + '%';
                progressText.textContent = step.text;
                currentStep++;
            } else {
                clearInterval(interval);
            }
        }, 800);
    }

    hideProgress() {
        const progressContainer = document.getElementById('format-progress-container');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
    }

    updateProgressText(text) {
        const progressText = document.querySelector('#format-progress-container .progress-text');
        if (progressText) {
            progressText.textContent = text;
        }
    }

    async showComparisonResult(data) {
        const comparisonContainer = document.getElementById('format-comparison-container');
        const originalPreview = document.getElementById('original-document-preview');
        const formattedPreview = document.getElementById('formatted-document-preview');

        if (comparisonContainer && originalPreview && formattedPreview) {
            // 显示原始文档
            originalPreview.innerHTML = this.formatDocumentContent(this.uploadedDocument.content);

            // 显示格式化后的文档
            formattedPreview.innerHTML = this.formatDocumentContent(data.aligned_content || data.formatted_content || '格式化内容生成中...');

            comparisonContainer.style.display = 'grid';
        }
    }

    formatDocumentContent(content) {
        // 简单的文档格式化显示
        return content
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>')
            .replace(/^<p><\/p>$/, '');
    }

    showExportSection() {
        // 显示原有的导出处理结果部分
        const exportSection = document.getElementById('format-export-results');
        if (exportSection) {
            exportSection.style.display = 'block';
        }

        const downloadBtn = document.getElementById('download-formatted-document');
        if (downloadBtn) {
            downloadBtn.disabled = false;
        }
    }

    hideExportSection() {
        // 隐藏导出处理结果部分，避免显示上一次的结果
        console.log('🔒 隐藏导出选项...');

        const exportSection = document.getElementById('format-export-results');
        if (exportSection) {
            exportSection.style.display = 'none';
            console.log('✅ 已隐藏导出结果区域');
        } else {
            console.log('⚠️ 未找到导出结果区域');
        }

        const downloadBtn = document.getElementById('download-formatted-document');
        if (downloadBtn) {
            downloadBtn.disabled = true;
            console.log('✅ 已禁用下载按钮');
        } else {
            console.log('⚠️ 未找到下载按钮');
        }
    }

    handleFormatSelection(button) {
        // 只处理格式对齐模块内的格式按钮
        const formatScene = document.getElementById('scene-format');
        if (!formatScene || !formatScene.contains(button)) {
            return;
        }

        // 移除格式对齐模块内其他按钮的选中状态
        formatScene.querySelectorAll('.format-buttons .btn').forEach(btn => {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline');
        });

        // 设置当前选中
        button.classList.remove('btn-outline');
        button.classList.add('btn-primary');

        this.selectedExportFormat = button.dataset.format;
        console.log('✅ 格式对齐模块选择导出格式:', this.selectedExportFormat);
    }

    async downloadFormattedDocument() {
        if (!this.currentTaskId) {
            errorHandler.createNotification('没有可下载的文档', 'warning');
            return;
        }

        try {
            const format = this.selectedExportFormat || 'txt';
            const downloadUrl = `/api/format-alignment/download/${this.currentTaskId}?format=${format}`;

            // 创建下载链接
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = `formatted_document_${this.currentTaskId}.${format}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            console.log('📥 开始下载格式化文档');
            errorHandler.createNotification('开始下载文档', 'success');
        } catch (error) {
            console.error('❌ 下载失败:', error);
            errorHandler.createNotification('下载失败', 'error');
        }
    }

    restartProcess() {
        // 重置状态
        this.selectedTemplate = null;
        this.uploadedDocument = null;
        this.currentTaskId = null;
        this.processingStep = 1;

        // 重置UI
        this.resetInterface();

        // 重新加载模板
        this.loadFormatTemplates();

        console.log('🔄 重新开始格式对齐流程');
    }

    resetInterface() {
        // 重置步骤状态
        document.querySelectorAll('.step-item').forEach((step, index) => {
            if (index === 0) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });

        // 重置模板选择 - 支持两种CSS类名
        document.querySelectorAll('.format-template-card, .style-card').forEach(card => {
            card.classList.remove('selected');
        });

        // 重置文件上传
        const uploadArea = document.getElementById('format-document-upload-area');
        if (uploadArea) {
            uploadArea.classList.remove('has-file');
            const textElement = uploadArea.querySelector('.file-upload-text');
            if (textElement) {
                textElement.textContent = '点击或拖拽上传TXT待处理文档';
            }
            const hintElement = uploadArea.querySelector('.file-upload-hint');
            if (hintElement) {
                hintElement.textContent = '仅支持 .txt 格式';
            }
        }

        // 重置按钮状态
        const startBtn = document.getElementById('start-format-alignment');
        if (startBtn) {
            startBtn.disabled = true;
        }

        // 隐藏结果区域
        const comparisonBlock = document.getElementById('format-comparison-preview');
        const exportSection = document.getElementById('format-export-results');
        if (comparisonBlock) comparisonBlock.style.display = 'none';
        if (exportSection) exportSection.style.display = 'none';
    }

    clearFormatContent() {
        // 清空格式对齐模块的所有内容和状态
        console.log('🗑️ ===== 开始执行清空格式对齐模块内容 =====');
        console.log('🗑️ clearFormatContent方法被调用');

        // 清空文件上传
        const documentInput = document.getElementById('upload-format-document');
        if (documentInput) {
            documentInput.value = '';
        }

        // 清空格式模板文档（Few-Shot模式）
        const templateInput = document.getElementById('upload-format-template');
        if (templateInput) {
            templateInput.value = '';
        }

        // 清空格式描述
        const descInput = document.getElementById('format-description');
        if (descInput) {
            descInput.value = '';
        }

        // 重置文件上传区域的显示文本
        const uploadText = document.querySelector('#format-document-upload-area .file-upload-text');
        if (uploadText) {
            uploadText.textContent = '点击或拖拽上传TXT待处理文档';
        }

        const templateUploadText = document.querySelector('#format-template-upload .file-upload-text');
        if (templateUploadText) {
            templateUploadText.textContent = '点击或拖拽上传TXT格式模板文档';
        }

        // 重置内部状态
        this.uploadedDocument = null;
        this.uploadedTemplateDocument = null;
        this.selectedTemplate = null;
        this.currentTaskId = null;

        // 强制隐藏所有处理进度和导出相关的元素
        console.log('🗑️ 开始隐藏处理进度和导出选项...');

        // 隐藏处理进度区域
        const comparisonBlock = document.getElementById('format-comparison-preview');
        if (comparisonBlock) {
            comparisonBlock.style.display = 'none';
            console.log('✅ 已隐藏处理进度区域');
        } else {
            console.log('⚠️ 未找到处理进度区域元素');
        }

        // 隐藏导出选项区域
        this.hideExportSection();

        // 确保导出结果区域也被隐藏
        const exportResultsBlock = document.getElementById('format-export-results');
        if (exportResultsBlock) {
            exportResultsBlock.style.display = 'none';
            console.log('✅ 已隐藏导出结果区域');
        } else {
            console.log('⚠️ 未找到导出结果区域元素');
        }

        // 强制隐藏所有可能的导出相关元素
        const allExportElements = [
            'format-export-results',
            'format-comparison-preview',
            'format-progress-container',
            'format-comparison-container'
        ];

        allExportElements.forEach(elementId => {
            const element = document.getElementById(elementId);
            if (element) {
                element.style.display = 'none';
                console.log(`✅ 已隐藏元素: ${elementId}`);
            }
        });

        // 重置步骤状态
        this.updateStepStatus(1, true);
        this.updateStepStatus(2, false);
        this.updateStepStatus(3, false);
        this.updateStepStatus(4, false);

        // 禁用开始按钮
        const startBtn = document.getElementById('start-format-alignment');
        if (startBtn) {
            startBtn.disabled = true;
        }

        // 重置模式选择到预设模式
        const presetRadio = document.getElementById('format-mode-preset');
        if (presetRadio) {
            presetRadio.checked = true;
            this.currentMode = 'preset';
            this.updateModeSelectionUI('preset');
        }

        // 显示预设配置，隐藏Few-Shot配置
        const presetConfig = document.getElementById('format-preset-config');
        const fewShotConfig = document.getElementById('format-few-shot-config');
        if (presetConfig) presetConfig.style.display = 'block';
        if (fewShotConfig) fewShotConfig.style.display = 'none';

        errorHandler.createNotification('内容已清空', 'success');
    }

    updateStepStatus(step, completed) {
        const stepItems = document.querySelectorAll('.step-item');
        stepItems.forEach((item, index) => {
            if (index + 1 <= step) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    initializeInterface() {
        // 初始化温度滑块
        const strengthSlider = document.getElementById('format-strength');
        const strengthValue = document.querySelector('.temperature-value');

        if (strengthSlider && strengthValue) {
            strengthSlider.addEventListener('input', (e) => {
                strengthValue.textContent = e.target.value;
            });
        }

        console.log('✅ 格式对齐界面初始化完成');
    }
}

// 创建格式对齐管理器实例
const formatAlignmentManager = new FormatAlignmentManager();

// 初始化格式对齐管理器
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOMContentLoaded事件触发，准备初始化格式对齐管理器...');
    if (formatAlignmentManager) {
        console.log('✅ 找到formatAlignmentManager实例');
        formatAlignmentManager.initialize();
    } else {
        console.log('❌ 未找到formatAlignmentManager实例');
    }
});

// ==================== 文档审查管理器 ====================
// @AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: document_review_manager

class DocumentReviewManager {
    constructor() {
        try {
            this.currentReviewResult = null;
            this.init();
        } catch (error) {
            console.error('❌ 文档审查管理器初始化失败:', error);
        }
    }

    init() {
        try {
            this.bindEvents();
            this.ensureInitialState();
            console.log('✅ 文档审查管理器初始化完成');
        } catch (error) {
            console.error('❌ 文档审查管理器初始化过程出错:', error);
        }
    }

    async initialize() {
        // 重新初始化方法，用于场景切换时调用
        console.log('🔄 重新初始化文档审查管理器...');
        this.ensureInitialState();
        console.log('✅ 文档审查管理器重新初始化完成');
    }

    ensureInitialState() {
        // 确保初始状态下进度条和结果区域完全隐藏
        const processingArea = document.getElementById('review-processing-area');
        const resultArea = document.getElementById('review-result-area');

        if (processingArea) {
            processingArea.classList.add('hidden');
            processingArea.style.display = 'none';
        }

        if (resultArea) {
            resultArea.classList.add('hidden');
            resultArea.style.display = 'none';
        }

        console.log('✅ 已确保初始状态：进度条和结果区域完全隐藏');
    }

    bindEvents() {
        // 保存this引用
        const self = this;

        // 开始审查按钮
        const startButton = document.getElementById('start-review-processing');
        if (startButton) {
            startButton.addEventListener('click', () => {
                this.handleDocumentReview(startButton);
            });
        }

        // 标签页切换
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-button') && e.target.closest('#scene-review')) {
                this.handleTabSwitch(e.target);
            }
        });

        // 重置按钮
        const resetButton = document.querySelector('[data-action="reset_review"]');
        if (resetButton) {
            resetButton.addEventListener('click', () => {
                console.log('🔄 重置文档审查');
                self.resetReview();
            });
        }

        // 文件上传验证 - 只支持TXT格式
        const fileInput = document.getElementById('upload-review-content-file');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
                    if (fileExtension !== '.txt') {
                        errorHandler.createNotification('文档审查只支持TXT格式文件', 'error');
                        e.target.value = '';
                        return;
                    }
                }
            });
        }
    }







    handleTabSwitch(button) {
        console.log('🔄 文档审查标签页切换:', button.dataset.tab);

        // 移除所有活动状态
        document.querySelectorAll('#scene-review .tab-button').forEach(btn => {
            btn.classList.remove('active');
            console.log('❌ 移除标签按钮活动状态:', btn.dataset.tab);
        });
        document.querySelectorAll('#scene-review .tab-pane').forEach(pane => {
            pane.classList.remove('active');
            console.log('❌ 移除标签页活动状态:', pane.id);
        });

        // 激活当前标签
        button.classList.add('active');
        const tabId = 'review-' + button.dataset.tab + '-tab';
        const tabContent = document.getElementById(tabId);
        console.log('🎯 目标标签页ID:', tabId);
        console.log('🎯 目标标签页元素:', tabContent);

        if (tabContent) {
            tabContent.classList.add('active');
            console.log('✅ 激活标签页:', tabId);

            // 调试：检查元素的实际样式
            const computedStyle = window.getComputedStyle(tabContent);
            console.log('🔍 标签页计算样式 display:', computedStyle.display);
            console.log('🔍 标签页计算样式 visibility:', computedStyle.visibility);
            console.log('🔍 标签页计算样式 opacity:', computedStyle.opacity);

            // 检查父元素的样式
            const parentElement = tabContent.parentElement;
            if (parentElement) {
                const parentStyle = window.getComputedStyle(parentElement);
                console.log('🔍 父元素类名:', parentElement.className);
                console.log('🔍 父元素计算样式 display:', parentStyle.display);
                console.log('🔍 父元素计算样式 visibility:', parentStyle.visibility);
            }
        } else {
            console.log('❌ 未找到目标标签页:', tabId);
        }
    }

    async handleDocumentReview(startButton) {
        try {
            // 获取内容
            const content = await this.getReviewContent();
            if (!content) {
                errorHandler.handleError(new Error('请输入要审查的内容'), 'validation');
                return;
            }

            // 显示进度 - 只有在点击开始审查按钮时才显示
            this.showProcessingProgress();

            // 调用API - 文档审查需要更长的超时时间
            const result = await apiManager.request('/api/document-review/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: content
                }),
                timeout: 120000  // 2分钟超时，因为文档审查可能需要较长时间
            });

            if (result.success) {
                this.displayReviewResult(result.data);
                console.log('✅ 文档审查完成');
            } else {
                throw new Error(result.error || '文档审查失败');
            }

        } catch (error) {
            this.hideProcessingProgress();
            let context = 'document_review';
            if (error.message && error.message.includes('内容')) {
                context = 'content_validation';
            }
            errorHandler.handleError(error, context);
        }
    }

    async getReviewContent() {
        console.log('🔍 开始获取审查内容...');

        // 优先从文本输入框获取内容
        const textInput = document.getElementById('review-content-text');
        console.log('📝 文本输入框元素:', textInput);
        console.log('📝 文本输入框值:', textInput?.value);
        console.log('📝 文本输入框是否可见:', textInput?.offsetParent !== null);

        if (textInput && textInput.value && textInput.value.trim()) {
            console.log('📝 从文本输入框获取审查内容');
            return textInput.value.trim();
        }

        // 然后检查文件上传
        const fileInput = document.getElementById('upload-review-content-file');
        console.log('📁 文件输入框元素:', fileInput);
        console.log('📁 文件输入框文件数量:', fileInput?.files?.length);
        console.log('📁 文件输入框是否可见:', fileInput?.offsetParent !== null);

        if (fileInput && fileInput.files && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            try {
                console.log('📁 从文件获取审查内容:', file.name);
                const content = await this.readFileContent(file);
                return content;
            } catch (error) {
                throw new Error(`文件读取失败: ${error.message}`);
            }
        }

        console.log('❌ 未找到任何审查内容');
        throw new Error('请在文本框中输入内容或上传文件');
    }

    async readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = function(e) {
                try {
                    const content = e.target.result;

                    if (content.length > 10 * 1024 * 1024) { // 10MB限制
                        reject(new Error('文件过大，请选择小于10MB的文件'));
                        return;
                    }

                    if (!content.trim()) {
                        reject(new Error('文件内容为空'));
                        return;
                    }

                    resolve(content.trim());
                } catch (error) {
                    reject(new Error(`文件解析失败: ${error.message}`));
                }
            };

            reader.onerror = function() {
                reject(new Error('文件读取失败，请检查文件是否损坏'));
            };

            reader.readAsText(file, 'UTF-8');
        });
    }

    showProcessingProgress() {
        const processingArea = document.getElementById('review-processing-area');
        const resultArea = document.getElementById('review-result-area');

        // 严格确保审查结果区域完全隐藏
        if (resultArea) {
            resultArea.classList.add('hidden');
            resultArea.style.display = 'none';
            console.log('✅ 已完全隐藏审查结果区域');
        }

        // 只有在点击开始审查按钮的瞬间才显示进度区域
        if (processingArea) {
            processingArea.classList.remove('hidden');
            processingArea.style.display = 'block';
            console.log('✅ 点击开始审查，立即显示进度区域');
        }

        // 重置进度条到初始状态
        const progressFill = document.getElementById('review-progress-fill');
        const progressText = document.getElementById('review-progress-text');

        if (progressFill) {
            progressFill.style.width = '0%';
            progressFill.style.transition = 'width 0.3s ease';
        }
        if (progressText) {
            progressText.textContent = '开始审查文档...';
        }

        // 模拟进度更新
        let progress = 0;
        const updateProgress = () => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;

            if (progressFill) {
                progressFill.style.width = progress + '%';
            }
            if (progressText) {
                if (progress < 30) {
                    progressText.textContent = '正在分析文档内容...';
                } else if (progress < 60) {
                    progressText.textContent = '正在执行智能审查...';
                } else {
                    progressText.textContent = '正在生成审查报告...';
                }
            }
        };

        const progressInterval = setInterval(updateProgress, 500);

        // 保存interval ID以便后续清除
        this.progressInterval = progressInterval;
    }

    hideProcessingProgress() {
        const processingArea = document.getElementById('review-processing-area');
        if (processingArea) {
            processingArea.classList.add('hidden');
            processingArea.style.display = 'none';
            console.log('✅ 已完全隐藏进度区域');
        }

        // 清除进度条定时器
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }

    displayReviewResult(data) {
        // 先完全隐藏进度区域
        this.hideProcessingProgress();

        // 只有当审查完全完成时才显示结果区域
        const resultArea = document.getElementById('review-result-area');
        const resultContent = document.getElementById('review-result-content');

        if (resultArea) {
            resultArea.classList.remove('hidden');
            resultArea.style.display = 'block';
            console.log('✅ 审查完全完成，显示结果区域');
        }

        if (resultContent) {
            // 将Markdown转换为HTML显示
            const htmlContent = this.markdownToHtml(data.review_result);
            resultContent.innerHTML = `
                <div class="review-result-header">
                    <h4>📋 审查报告</h4>
                    <div class="review-meta">
                        <span>文档长度: ${data.document_length} 字符</span>
                        <span>处理时间: ${data.processing_time?.toFixed(2)}秒</span>
                        ${data.chunks_count > 1 ? `<span>分块处理: ${data.chunks_count} 个块</span>` : ''}
                    </div>
                </div>
                <div class="review-result-content">
                    ${htmlContent}
                </div>
            `;
        }

        // 保存结果用于导出
        this.currentReviewResult = data;
        console.log('✅ 审查结果显示完成');
    }

    markdownToHtml(markdown) {
        // 简单的Markdown转HTML
        return markdown
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^\* (.*$)/gim, '<li>$1</li>')
            .replace(/^- (.*$)/gim, '<li>$1</li>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    resetReview() {
        // @AI-Generated: 2025-01-25, Confidence: 0.99, Model: Claude Sonnet 4, Prompt: reset_review
        console.log('🔄 开始重置文档审查...');

        // 清空文本输入框
        const textInput = document.getElementById('review-content-text');
        if (textInput) {
            textInput.value = '';
        }

        // 重置文件上传
        const fileInput = document.getElementById('upload-review-content-file');
        if (fileInput) {
            fileInput.value = '';
        }

        // 重置文件上传显示
        const uploadText = document.querySelector('#review-content-upload .file-upload-text');
        if (uploadText) {
            uploadText.textContent = '点击或拖拽上传文档文件';
        }

        // 完全隐藏进度区域
        const processingArea = document.getElementById('review-processing-area');
        if (processingArea) {
            processingArea.classList.add('hidden');
            processingArea.style.display = 'none';
        }

        // 完全隐藏结果区域
        const resultArea = document.getElementById('review-result-area');
        if (resultArea) {
            resultArea.classList.add('hidden');
            resultArea.style.display = 'none';
        }

        // 清空结果内容
        const resultContent = document.getElementById('review-result-content');
        if (resultContent) {
            resultContent.innerHTML = '';
        }

        // 清除进度条定时器
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }

        // 重置标签页到文本输入
        const textTab = document.querySelector('#scene-review [data-tab="text-input"]');
        if (textTab) {
            this.handleTabSwitch(textTab);
        }

        // 清空当前结果
        this.currentReviewResult = null;

        console.log('✅ 文档审查重置完成');
    }
}

// 创建文档审查管理器实例
const documentReviewManager = new DocumentReviewManager();

// ==================== 导出全局函数 ====================
window.appState = appState;
window.fileValidator = fileValidator;
window.fileUploadManager = fileUploadManager;
window.errorHandler = errorHandler;
window.uiManager = uiManager;
window.apiManager = apiManager;
window.reapplyOperation = reapplyOperation;
window.formatAlignmentManager = formatAlignmentManager;
window.documentReviewManager = documentReviewManager;