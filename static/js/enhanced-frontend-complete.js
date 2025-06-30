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
            presentation: ['.pptx', '.ppt']
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
    }

    setupEventListeners() {
        // 导航事件
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const sceneId = item.getAttribute('data-scene');
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
        // 隐藏所有场景
        document.querySelectorAll('.scene-section').forEach(scene => {
            scene.classList.add('hidden');
        });

        // 显示目标场景
        const targetScene = document.getElementById(`scene-${sceneId}`);
        if (targetScene) {
            targetScene.classList.remove('hidden');
            this.currentScene = sceneId;
        }

        // 更新导航状态
        this.updateActiveNavItem(sceneId);
        
        // 重置步骤
        this.resetSteps();
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
                    await this.handlePreview(element);
                    break;
                case 'export_result':
                    await this.handleExport(element);
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
                default:
                    console.warn(`未知操作: ${action}`);
            }
        } catch (error) {
            errorHandler.handleError(error, 'action_execution');
        }
    }

    async handleFormatAlignment(element) {
        const sessionId = appState.createSession('format');
        this.navigateToStep(2);
        
        // 收集文件
        const files = this.collectFiles('format');
        if (files.length < 2) {
            errorHandler.handleError(new Error('请上传参考文件和目标文件'), 'validation');
            return;
        }

        // 调用API
        const result = await apiManager.request('/api/format-alignment', {
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

    async handleStyleAlignment(element) {
        const sessionId = appState.createSession('style');
        this.navigateToStep(2);
        
        const files = this.collectFiles('style');
        if (files.length < 2) {
            errorHandler.handleError(new Error('请上传参考文件和目标文件'), 'validation');
            return;
        }

        const result = await apiManager.request('/api/writing-style/analyze', {
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
            })
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

    async handleExportReviewReport(element) {
        // 实现导出审查报告逻辑
        errorHandler.createNotification('导出审查报告功能开发中', 'info');
    }

    async handlePreviewReview(element) {
        this.navigateToStep(3);
        // 实现预览审查结果逻辑
    }

    async handleExportReview(element) {
        this.navigateToStep(4);
        // 实现导出审查报告逻辑
        try {
            const result = await apiManager.request('/api/document-review/export', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: appState.getCurrentSessionId()
                })
            });

            if (result.success) {
                apiManager.downloadFile('/api/document-review/download', result.data, 'review_report.docx');
            }
        } catch (error) {
            errorHandler.handleError(error, 'export_review');
        }
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
            }
        }
    }

    formatResult(data) {
        if (typeof data === 'string') {
            return `<pre>${data}</pre>`;
        }
        if (typeof data === 'object') {
            return `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        }
        return `<div>${data}</div>`;
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

        // 加载文风模板
        const styleTemplates = await apiManager.request('/api/writing-style/templates');
        if (styleTemplates.success) {
            updateStyleSelect(styleTemplates.templates);
        }

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

// ==================== 导出全局函数 ====================
window.appState = appState;
window.fileValidator = fileValidator;
window.fileUploadManager = fileUploadManager;
window.errorHandler = errorHandler;
window.uiManager = uiManager;
window.apiManager = apiManager;
window.reapplyOperation = reapplyOperation; 