/**
 * Enhanced-Ui
 * 
 * @author AI Assistant (Claude)
 * @date 2025-01-28
 * @ai_assisted 是 - Claude 3.5 Sonnet
 * @version v1.0
 * @license MIT
 */


class UIManager {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.loadingStates = new Map();
        this.fileUploadAreas = new Map();
        this.progressCallbacks = new Map();
    }

    initializeUI() {
        this.setupEventListeners();
        this.setupFileUploadAreas();
        this.setupProgressIndicators();
        this.setupStepNavigation();
        this.setupResponsiveDesign();
        this.setupGlobalProgressBar();
        this.setupNotificationSystem();
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
        document.querySelectorAll('.btn-primary, .btn-secondary, .btn-success, .btn-danger').forEach(btn => {
            btn.addEventListener('click', this.handleButtonClick.bind(this));
        });

        // 表单提交监听
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        });

        // 场景切换监听
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', this.handleSceneSwitch.bind(this));
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
            
            // 存储上传区域信息
            this.fileUploadAreas.set(area.id || area.className, area);
        });
    }

    setupProgressIndicators() {
        // 创建全局进度条
        this.createGlobalProgressBar();
        
        // 设置步骤指示器
        const stepIndicators = document.querySelectorAll('.step-indicator .step-item');
        stepIndicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                this.navigateToStep(index + 1);
            });
        });
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

    setupGlobalProgressBar() {
        this.createGlobalProgressBar();
    }

    setupNotificationSystem() {
        // 创建通知容器
        const notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
    }

    createGlobalProgressBar() {
        const progressBar = document.createElement('div');
        progressBar.id = 'global-progress';
        progressBar.className = 'global-progress-bar';
        progressBar.style.display = 'none';
        progressBar.innerHTML = `
            <div class="progress-fill"></div>
            <div class="progress-text">0%</div>
        `;
        document.body.appendChild(progressBar);
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

    handleSceneSwitch(e) {
        e.preventDefault();
        const sceneId = e.currentTarget.getAttribute('data-scene');
        if (sceneId) {
            this.switchScene(sceneId);
        }
    }

    async processFile(file, uploadArea) {
        try {
            // 验证文件
            const validation = window.fileValidator.validateFile(file);
            if (!validation.isValid) {
                window.errorHandler.handleError(new Error(validation.errors.join(', ')), 'file_validation');
                return;
            }

            // 预处理文件
            const preprocessing = await window.fileValidator.preprocessFile(file);
            if (!preprocessing.success) {
                window.errorHandler.handleError(new Error(preprocessing.errors.join(', ')), 'file_preprocessing');
                return;
            }

            // 更新UI显示
            this.updateFileDisplay(uploadArea, file, preprocessing.data);
            
            // 存储文件信息
            const fileId = `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            window.appState.uploadedFiles.set(fileId, {
                file: file,
                data: preprocessing.data,
                uploadArea: uploadArea
            });

            // 显示成功消息
            this.showNotification('文件上传成功', 'success');

        } catch (error) {
            window.errorHandler.handleError(error, 'file_processing');
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

    switchScene(sceneId) {
        const scenes = document.querySelectorAll('.scene-section');
        scenes.forEach(scene => {
            scene.classList.add('hidden');
        });
        
        const activeScene = document.getElementById(`scene-${sceneId}`);
        if (activeScene) {
            activeScene.classList.remove('hidden');
            activeScene.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        this.updateActiveNavItem(sceneId);
        window.appState.currentScene = sceneId;
    }

    updateActiveNavItem(sceneId) {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-scene') === sceneId) {
                item.classList.add('active');
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
                default:
                    console.warn(`未知操作: ${action}`);
            }
        } catch (error) {
            window.errorHandler.handleError(error, `action_${action}`);
        } finally {
            this.hideLoading(element.id || 'action-area');
        }
    }

    async handleFileUpload(element) {
        console.log('处理文件上传');
        // 实现文件上传逻辑
    }

    async handleDocumentProcessing(element) {
        console.log('处理文档');
        // 实现文档处理逻辑
    }

    async handleExport(element) {
        console.log('处理导出');
        // 实现导出逻辑
    }

    async handlePreview(element) {
        console.log('处理预览');
        // 实现预览逻辑
    }

    async handleFormatAlignment(element) {
        console.log('处理格式对齐');
        // 实现格式对齐逻辑
    }

    async handleStyleAlignment(element) {
        console.log('处理文风对齐');
        // 实现文风对齐逻辑
    }

    async handleDocumentFill(element) {
        console.log('处理文档填报');
        // 实现文档填报逻辑
    }

    async handleDocumentReview(element) {
        console.log('处理文档审查');
        // 实现文档审查逻辑
    }

    showNotification(message, type = 'info', duration = 5000) {
        const container = document.getElementById('notification-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        container.appendChild(notification);

        // 自动移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, duration);
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

    removeFile(fileName) {
        // 从状态中移除文件
        for (const [fileId, fileInfo] of window.appState.uploadedFiles.entries()) {
            if (fileInfo.file.name === fileName) {
                window.appState.uploadedFiles.delete(fileId);
                break;
            }
        }

        // 更新UI
        this.updateFileDisplayAfterRemoval(fileName);
        this.showNotification('文件已删除', 'success');
    }

    previewFile(fileName) {
        // 查找文件信息
        let fileInfo = null;
        for (const [fileId, info] of window.appState.uploadedFiles.entries()) {
            if (info.file.name === fileName) {
                fileInfo = info;
                break;
            }
        }

        if (fileInfo) {
            this.showFilePreview(fileInfo);
        } else {
            this.showNotification('文件未找到', 'error');
        }
    }

    showFilePreview(fileInfo) {
        const modal = document.createElement('div');
        modal.className = 'file-preview-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>文件预览: ${fileInfo.file.name}</h3>
                    <button class="modal-close" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="file-preview-content">
                        ${this.formatFilePreview(fileInfo)}
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    formatFilePreview(fileInfo) {
        if (fileInfo.data && fileInfo.data.content) {
            return `<pre>${fileInfo.data.content}</pre>`;
        } else {
            return `<p>文件大小: ${this.formatFileSize(fileInfo.file.size)}</p>
                    <p>文件类型: ${fileInfo.file.type || '未知'}</p>`;
        }
    }

    updateFileDisplayAfterRemoval(fileName) {
        // 查找并清除对应的文件显示
        document.querySelectorAll('.file-display').forEach(display => {
            const fileNameElement = display.querySelector('.file-name');
            if (fileNameElement && fileNameElement.textContent === fileName) {
                const uploadArea = display.closest('.file-upload-area');
                if (uploadArea) {
                    uploadArea.classList.remove('has-file');
                    display.remove();
                }
            }
        });
    }
}

// 创建全局UI管理器实例
const uiManager = new UIManager();

// 页面加载完成后初始化UI
document.addEventListener('DOMContentLoaded', function() {
    uiManager.initializeUI();
});

// 导出全局实例
window.uiManager = uiManager; 