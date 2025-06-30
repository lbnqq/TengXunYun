/**
 * Enhanced-App
 * 
 * @author AI Assistant (Claude)
 * @date 2025-01-28
 * @ai_assisted 是 - Claude 3.5 Sonnet
 * @version v1.0
 * @license MIT
 */


// 全局应用状态管理
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
            enableNotifications: true
        };
        this.sessionHistory = [];
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
            results: {}
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
            session.files.push({
                name: file.name,
                size: file.size,
                type: file.type,
                fileType: fileType,
                uploadedAt: new Date(),
                id: `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
            });
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
}

// 文件验证和预处理管理器
class FileValidator {
    constructor() {
        this.supportedFormats = {
            document: ['.docx', '.doc', '.txt', '.rtf'],
            image: ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            pdf: ['.pdf']
        };
        this.maxFileSize = 50 * 1024 * 1024; // 50MB
    }

    validateFile(file, expectedType = 'document') {
        const result = {
            isValid: true,
            errors: [],
            warnings: []
        };

        // 检查文件大小
        if (file.size > this.maxFileSize) {
            result.isValid = false;
            result.errors.push(`文件大小超过限制 (${this.maxFileSize / 1024 / 1024}MB)`);
        }

        // 检查文件格式
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        const supportedFormats = this.supportedFormats[expectedType] || this.supportedFormats.document;
        
        if (!supportedFormats.includes(extension)) {
            result.isValid = false;
            result.errors.push(`不支持的文件格式: ${extension}`);
        }

        // 检查文件是否为空
        if (file.size === 0) {
            result.isValid = false;
            result.errors.push('文件为空');
        }

        // 检查文件名
        if (file.name.length > 255) {
            result.warnings.push('文件名过长，建议缩短');
        }

        return result;
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
                lastModified: file.lastModified
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
            reader.readAsText(file);
        });
    }
}

// 文件上传管理器
class FileUploadManager {
    constructor() {
        this.uploadQueue = [];
        this.activeUploads = new Map();
        this.uploadCallbacks = new Map();
    }

    async uploadFile(file, endpoint, options = {}) {
        const uploadId = `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        return new Promise((resolve, reject) => {
            const formData = new FormData();
            formData.append('file', file);
            
            // 添加额外参数
            if (options.extraData) {
                Object.keys(options.extraData).forEach(key => {
                    formData.append(key, options.extraData[key]);
                });
            }

            const xhr = new XMLHttpRequest();
            
            // 进度监听
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const progress = (e.loaded / e.total) * 100;
                    this.updateUploadProgress(uploadId, progress);
                }
            });

            // 完成监听
            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (error) {
                        reject(new Error('响应解析失败'));
                    }
                } else {
                    reject(new Error(`上传失败: ${xhr.status} ${xhr.statusText}`));
                }
            });

            // 错误监听
            xhr.addEventListener('error', () => {
                reject(new Error('网络错误'));
            });

            xhr.addEventListener('abort', () => {
                reject(new Error('上传被取消'));
            });

            xhr.open('POST', endpoint);
            xhr.send(formData);
        });
    }

    updateUploadProgress(uploadId, progress) {
        const callback = this.uploadCallbacks.get(uploadId);
        if (callback && callback.onProgress) {
            callback.onProgress(progress);
        }
    }
}

// 错误处理管理器
class ErrorHandler {
    constructor() {
        this.errorTypes = {
            NETWORK: 'network',
            VALIDATION: 'validation',
            PROCESSING: 'processing',
            PERMISSION: 'permission',
            UNKNOWN: 'unknown'
        };
    }

    handleError(error, context, options = {}) {
        const errorInfo = {
            type: this.categorizeError(error),
            message: error.message,
            context: context,
            timestamp: new Date(),
            userFriendly: this.getUserFriendlyMessage(error, context)
        };

        // 记录错误
        console.error('Error occurred:', errorInfo);

        // 显示用户友好的错误消息
        this.showErrorMessage(errorInfo.userFriendly, errorInfo.type);

        // 通知用户（如果启用）
        if (options.notifyUser !== false) {
            this.notifyUser(errorInfo);
        }

        return errorInfo;
    }

    categorizeError(error) {
        if (error.name === 'NetworkError' || error.message.includes('fetch')) {
            return this.errorTypes.NETWORK;
        } else if (error.message.includes('validation') || error.message.includes('format')) {
            return this.errorTypes.VALIDATION;
        } else if (error.message.includes('permission') || error.message.includes('access')) {
            return this.errorTypes.PERMISSION;
        } else if (error.message.includes('processing') || error.message.includes('server')) {
            return this.errorTypes.PROCESSING;
        } else {
            return this.errorTypes.UNKNOWN;
        }
    }

    getUserFriendlyMessage(error, context) {
        const errorType = this.categorizeError(error);
        
        switch (errorType) {
            case this.errorTypes.NETWORK:
                return '网络连接失败，请检查网络设置后重试';
            case this.errorTypes.VALIDATION:
                return '文件格式不正确，请检查文件类型和内容';
            case this.errorTypes.PERMISSION:
                return '权限不足，请检查文件访问权限';
            case this.errorTypes.PROCESSING:
                return '处理过程中出现错误，请稍后重试';
            default:
                return '操作失败，请稍后重试';
        }
    }

    showErrorMessage(message, type) {
        const notification = this.createNotification(message, 'error');
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    createNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        return notification;
    }

    getNotificationIcon(type) {
        switch (type) {
            case 'error': return '❌';
            case 'success': return '✅';
            case 'warning': return '⚠️';
            case 'info': return 'ℹ️';
            default: return '💬';
        }
    }

    notifyUser(errorInfo) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('文档处理错误', {
                body: errorInfo.userFriendly,
                icon: '/static/favicon.ico'
            });
        }
    }
}

// 用户界面管理器
class UIManager {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.loadingStates = new Map();
    }

    initializeUI() {
        this.setupEventListeners();
        this.setupFileUploadAreas();
        this.setupProgressIndicators();
        this.setupStepNavigation();
        this.setupResponsiveDesign();
    }

    setupEventListeners() {
        // 文件上传监听
        document.querySelectorAll('.file-upload-area').forEach(area => {
            area.addEventListener('dragover', this.handleDragOver.bind(this));
            area.addEventListener('dragleave', this.handleDragLeave.bind(this));
            area.addEventListener('drop', this.handleFileDrop.bind(this));
            area.addEventListener('click', this.handleUploadClick.bind(this));
        });

        // 按钮点击监听
        document.querySelectorAll('.btn-primary, .btn-secondary, .btn-success').forEach(btn => {
            btn.addEventListener('click', this.handleButtonClick.bind(this));
        });

        // 表单提交监听
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        });
    }

    setupFileUploadAreas() {
        document.querySelectorAll('.file-upload-area').forEach(area => {
            const input = area.querySelector('input[type="file"]');
            if (input) {
                input.addEventListener('change', (e) => {
                    this.handleFileSelect(e, area);
                });
            }
        });
    }

    setupProgressIndicators() {
        // 创建全局进度条
        const progressBar = document.createElement('div');
        progressBar.id = 'global-progress';
        progressBar.className = 'global-progress-bar';
        progressBar.innerHTML = `
            <div class="progress-fill"></div>
            <div class="progress-text">0%</div>
        `;
        document.body.appendChild(progressBar);
    }

    setupStepNavigation() {
        const stepIndicators = document.querySelectorAll('.step-indicator .step-item');
        stepIndicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                this.navigateToStep(index + 1);
            });
        });
    }

    setupResponsiveDesign() {
        const mediaQuery = window.matchMedia('(max-width: 768px)');
        this.handleResponsiveChange(mediaQuery);
        mediaQuery.addListener(this.handleResponsiveChange.bind(this));
    }

    handleResponsiveChange(mediaQuery) {
        if (mediaQuery.matches) {
            document.body.classList.add('mobile-view');
        } else {
            document.body.classList.remove('mobile-view');
        }
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
        e.currentTarget.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        const uploadArea = e.currentTarget;
        
        files.forEach(file => {
            this.processFile(file, uploadArea);
        });
    }

    handleUploadClick(e) {
        const input = e.currentTarget.querySelector('input[type="file"]');
        if (input) {
            input.click();
        }
    }

    handleFileSelect(e, uploadArea) {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            this.processFile(file, uploadArea);
        });
    }

    handleButtonClick(e) {
        const button = e.currentTarget;
        const action = button.getAttribute('data-action');
        
        if (action) {
            this.executeAction(action, button);
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
            const validation = fileValidator.validateFile(file);
            if (!validation.isValid) {
                errorHandler.handleError(new Error(validation.errors.join(', ')), 'file_validation');
                return;
            }

            // 预处理文件
            const preprocessing = await fileValidator.preprocessFile(file);
            if (!preprocessing.success) {
                errorHandler.handleError(new Error(preprocessing.errors.join(', ')), 'file_preprocessing');
                return;
            }

            // 更新UI显示
            this.updateFileDisplay(uploadArea, file, preprocessing.data);
            
            // 存储文件信息
            const fileId = `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            appState.uploadedFiles.set(fileId, {
                file: file,
                data: preprocessing.data,
                uploadArea: uploadArea
            });

        } catch (error) {
            errorHandler.handleError(error, 'file_processing');
        }
    }

    updateFileDisplay(uploadArea, file, fileData) {
        const displayArea = uploadArea.querySelector('.file-display') || this.createFileDisplay(uploadArea);
        
        displayArea.innerHTML = `
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${this.formatFileSize(file.size)}</div>
                <div class="file-type">${file.type || '未知类型'}</div>
            </div>
            <div class="file-actions">
                <button class="btn-remove-file" onclick="uiManager.removeFile('${file.name}')">删除</button>
                <button class="btn-preview-file" onclick="uiManager.previewFile('${file.name}')">预览</button>
            </div>
        `;
        
        uploadArea.classList.add('has-file');
    }

    createFileDisplay(uploadArea) {
        const displayArea = document.createElement('div');
        displayArea.className = 'file-display';
        uploadArea.appendChild(displayArea);
        return displayArea;
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
            element.classList.add('loading');
            element.innerHTML = `
                <div class="loading-spinner"></div>
                <div class="loading-message">${message}</div>
            `;
            this.loadingStates.set(elementId, true);
        }
    }

    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element && this.loadingStates.get(elementId)) {
            element.classList.remove('loading');
            this.loadingStates.delete(elementId);
        }
    }

    updateProgress(progress, message = '') {
        const progressBar = document.getElementById('global-progress');
        if (progressBar) {
            const fill = progressBar.querySelector('.progress-fill');
            const text = progressBar.querySelector('.progress-text');
            
            fill.style.width = `${progress}%`;
            text.textContent = message || `${Math.round(progress)}%`;
            
            if (progress >= 100) {
                setTimeout(() => {
                    progressBar.style.display = 'none';
                }, 1000);
            } else {
                progressBar.style.display = 'block';
            }
        }
    }

    navigateToStep(step) {
        if (step >= 1 && step <= this.totalSteps) {
            this.currentStep = step;
            this.updateStepIndicators();
            this.showStepContent(step);
        }
    }

    updateStepIndicators() {
        const indicators = document.querySelectorAll('.step-indicator .step-item');
        indicators.forEach((indicator, index) => {
            const stepNumber = index + 1;
            indicator.classList.remove('active', 'completed');
            
            if (stepNumber === this.currentStep) {
                indicator.classList.add('active');
            } else if (stepNumber < this.currentStep) {
                indicator.classList.add('completed');
            }
        });
    }

    showStepContent(step) {
        const stepContents = document.querySelectorAll('.step-content');
        stepContents.forEach((content, index) => {
            const stepNumber = index + 1;
            if (stepNumber === step) {
                content.classList.remove('hidden');
            } else {
                content.classList.add('hidden');
            }
        });
    }

    async executeAction(action, element) {
        try {
            this.showLoading(element.id || 'action-area', '执行中...');
            
            switch (action) {
                case 'upload_file':
                    await this.handleFileUpload(element);
                    break;
                case 'process_document':
                    await this.handleDocumentProcessing(element);
                    break;
                case 'export_result':
                    await this.handleExport(element);
                    break;
                case 'preview_result':
                    await this.handlePreview(element);
                    break;
                default:
                    console.warn(`未知操作: ${action}`);
            }
        } catch (error) {
            errorHandler.handleError(error, `action_${action}`);
        } finally {
            this.hideLoading(element.id || 'action-area');
        }
    }

    async handleFileUpload(element) {
        // 实现文件上传逻辑
        console.log('处理文件上传');
    }

    async handleDocumentProcessing(element) {
        // 实现文档处理逻辑
        console.log('处理文档');
    }

    async handleExport(element) {
        // 实现导出逻辑
        console.log('处理导出');
    }

    async handlePreview(element) {
        // 实现预览逻辑
        console.log('处理预览');
    }
}

// API通信管理器
class APIManager {
    constructor() {
        this.baseURL = '/api';
        this.timeout = 30000; // 30秒超时
        this.retryAttempts = 3;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
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
        
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const response = await this.makeRequest(url, config);
                return await this.handleResponse(response);
            } catch (error) {
                lastError = error;
                if (attempt < this.retryAttempts) {
                    await this.delay(1000 * attempt); // 指数退避
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
                ...config,
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

        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else if (contentType && contentType.includes('application/vnd.openxmlformats-officedocument.wordprocessingml.document')) {
            return await response.blob();
        } else {
            return await response.text();
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async uploadFile(endpoint, file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        if (options.extraData) {
            Object.keys(options.extraData).forEach(key => {
                formData.append(key, options.extraData[key]);
            });
        }

        return this.request(endpoint, {
            method: 'POST',
            body: formData,
            headers: {} // 不设置Content-Type，让浏览器自动设置
        });
    }

    async downloadFile(endpoint, data, filename) {
        try {
            const response = await this.request(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response instanceof Blob) {
                this.createDownloadLink(response, filename);
            } else {
                throw new Error('响应不是文件类型');
            }
        } catch (error) {
            errorHandler.handleError(error, 'file_download');
        }
    }

    createDownloadLink(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// 全局实例
const appState = new AppState();
const fileValidator = new FileValidator();
const fileUploadManager = new FileUploadManager();
const errorHandler = new ErrorHandler();
const uiManager = new UIManager();
const apiManager = new APIManager();

// 应用初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('初始化增强版办公文档智能代理前端应用...');
    
    // 初始化UI
    uiManager.initializeUI();
    
    // 设置页面标题
    document.title = "办公文档智能代理 - 增强版";
    
    // 请求通知权限
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    console.log('应用初始化完成');
});

// 导出全局实例供其他模块使用
window.appState = appState;
window.fileValidator = fileValidator;
window.fileUploadManager = fileUploadManager;
window.errorHandler = errorHandler;
window.uiManager = uiManager;
window.apiManager = apiManager; 