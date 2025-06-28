/**
 * 增强版UI管理器
 * 功能：用户界面交互、文件上传、状态显示、进度管理
 * 版本：2.0.0
 */

class UIManager {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.loadingStates = new Map();
        this.fileUploadAreas = new Map();
        this.progressCallbacks = new Map();
    }

    /**
     * 初始化用户界面
     */
    initializeUI() {
        this.setupEventListeners();
        this.setupFileUploadAreas();
        this.setupProgressIndicators();
        this.setupStepNavigation();
        this.setupResponsiveDesign();
        this.setupGlobalProgressBar();
        this.setupNotificationSystem();
    }

    /**
     * 设置事件监听器
     */
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

    /**
     * 设置文件上传区域
     */
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

    /**
     * 设置进度指示器
     */
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

    /**
     * 设置步骤导航
     */
    setupStepNavigation() {
        const stepIndicators = document.querySelectorAll('.step-indicator .step-item');
        stepIndicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                this.navigateToStep(index + 1);
            });
        });
    }

    /**
     * 设置响应式设计
     */
    setupResponsiveDesign() {
        const mediaQuery = window.matchMedia('(max-width: 768px)');
        this.handleResponsiveChange(mediaQuery);
        mediaQuery.addListener(this.handleResponsiveChange.bind(this));
    }

    /**
     * 设置全局进度条
     */
    setupGlobalProgressBar() {
        this.createGlobalProgressBar();
    }

    /**
     * 设置通知系统
     */
    setupNotificationSystem() {
        // 创建通知容器
        const notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
    }

    /**
     * 创建全局进度条
     */
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

    /**
     * 处理响应式变化
     * @param {MediaQueryList} mediaQuery - 媒体查询对象
     */
    handleResponsiveChange(mediaQuery) {
        if (mediaQuery.matches) {
            document.body.classList.add('mobile-view');
        } else {
            document.body.classList.remove('mobile-view');
        }
    }

    /**
     * 处理拖拽悬停
     * @param {DragEvent} e - 拖拽事件
     */
    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    /**
     * 处理拖拽离开
     * @param {DragEvent} e - 拖拽事件
     */
    handleDragLeave(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
    }

    /**
     * 处理文件拖放
     * @param {DragEvent} e - 拖拽事件
     */
    handleFileDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        const uploadArea = e.currentTarget;
        
        files.forEach(file => {
            this.processFile(file, uploadArea);
        });
    }

    /**
     * 处理上传点击
     * @param {Event} e - 点击事件
     */
    handleUploadClick(e) {
        const input = e.currentTarget.querySelector('input[type="file"]');
        if (input) {
            input.click();
        }
    }

    /**
     * 处理文件选择
     * @param {Event} e - 文件选择事件
     * @param {HTMLElement} uploadArea - 上传区域
     */
    handleFileSelect(e, uploadArea) {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            this.processFile(file, uploadArea);
        });
    }

    /**
     * 处理按钮点击
     * @param {Event} e - 点击事件
     */
    handleButtonClick(e) {
        const button = e.currentTarget;
        const action = button.getAttribute('data-action');
        
        if (action) {
            this.executeAction(action, button);
        }
    }

    /**
     * 处理表单提交
     * @param {Event} e - 表单提交事件
     */
    handleFormSubmit(e) {
        e.preventDefault();
        const form = e.currentTarget;
        const action = form.getAttribute('data-action');
        
        if (action) {
            this.executeAction(action, form);
        }
    }

    /**
     * 处理场景切换
     * @param {Event} e - 点击事件
     */
    handleSceneSwitch(e) {
        e.preventDefault();
        const sceneId = e.currentTarget.getAttribute('data-scene');
        if (sceneId) {
            this.switchScene(sceneId);
        }
    }

    /**
     * 处理文件
     * @param {File} file - 文件对象
     * @param {HTMLElement} uploadArea - 上传区域
     */
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

    /**
     * 更新文件显示
     * @param {HTMLElement} uploadArea - 上传区域
     * @param {File} file - 文件对象
     * @param {Object} fileData - 文件数据
     */
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

    /**
     * 创建文件显示区域
     * @param {HTMLElement} uploadArea - 上传区域
     * @returns {HTMLElement} 文件显示区域
     */
    createFileDisplay(uploadArea) {
        const displayArea = document.createElement('div');
        displayArea.className = 'file-display';
        uploadArea.appendChild(displayArea);
        return displayArea;
    }

    /**
     * 格式化文件大小
     * @param {number} bytes - 字节数
     * @returns {string} 格式化的大小
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * 显示加载状态
     * @param {string} elementId - 元素ID
     * @param {string} message - 加载消息
     */
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

    /**
     * 隐藏加载状态
     * @param {string} elementId - 元素ID
     */
    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element && this.loadingStates.get(elementId)) {
            element.classList.remove('loading');
            this.loadingStates.delete(elementId);
        }
    }

    /**
     * 更新进度
     * @param {number} progress - 进度百分比
     * @param {string} message - 进度消息
     */
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

    /**
     * 导航到指定步骤
     * @param {number} step - 步骤号
     */
    navigateToStep(step) {
        if (step >= 1 && step <= this.totalSteps) {
            this.currentStep = step;
            this.updateStepIndicators();
            this.showStepContent(step);
        }
    }

    /**
     * 更新步骤指示器
     */
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

    /**
     * 显示步骤内容
     * @param {number} step - 步骤号
     */
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

    /**
     * 切换场景
     * @param {string} sceneId - 场景ID
     */
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

    /**
     * 更新活动导航项
     * @param {string} sceneId - 场景ID
     */
    updateActiveNavItem(sceneId) {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-scene') === sceneId) {
                item.classList.add('active');
            }
        });
    }

    /**
     * 执行操作
     * @param {string} action - 操作名称
     * @param {HTMLElement} element - 触发元素
     */
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

    /**
     * 处理文件上传
     * @param {HTMLElement} element - 触发元素
     */
    async handleFileUpload(element) {
        console.log('处理文件上传');
        // 实现文件上传逻辑
    }

    /**
     * 处理文档处理
     * @param {HTMLElement} element - 触发元素
     */
    async handleDocumentProcessing(element) {
        console.log('处理文档');
        // 实现文档处理逻辑
    }

    /**
     * 处理导出
     * @param {HTMLElement} element - 触发元素
     */
    async handleExport(element) {
        console.log('处理导出');
        // 实现导出逻辑
    }

    /**
     * 处理预览
     * @param {HTMLElement} element - 触发元素
     */
    async handlePreview(element) {
        console.log('处理预览');
        // 实现预览逻辑
    }

    /**
     * 处理格式对齐
     * @param {HTMLElement} element - 触发元素
     */
    async handleFormatAlignment(element) {
        console.log('处理格式对齐');
        // 实现格式对齐逻辑
    }

    /**
     * 处理文风对齐
     * @param {HTMLElement} element - 触发元素
     */
    async handleStyleAlignment(element) {
        console.log('处理文风对齐');
        // 实现文风对齐逻辑
    }

    /**
     * 处理文档填报
     * @param {HTMLElement} element - 触发元素
     */
    async handleDocumentFill(element) {
        console.log('处理文档填报');
        // 实现文档填报逻辑
    }

    /**
     * 处理文档审查
     * @param {HTMLElement} element - 触发元素
     */
    async handleDocumentReview(element) {
        console.log('处理文档审查');
        // 实现文档审查逻辑
    }

    /**
     * 显示通知
     * @param {string} message - 消息内容
     * @param {string} type - 消息类型
     * @param {number} duration - 显示时长（毫秒）
     */
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

    /**
     * 获取通知图标
     * @param {string} type - 通知类型
     * @returns {string} 图标HTML
     */
    getNotificationIcon(type) {
        switch (type) {
            case 'error': return '❌';
            case 'success': return '✅';
            case 'warning': return '⚠️';
            case 'info': return 'ℹ️';
            default: return '💬';
        }
    }

    /**
     * 删除文件
     * @param {string} fileName - 文件名
     */
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

    /**
     * 预览文件
     * @param {string} fileName - 文件名
     */
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

    /**
     * 显示文件预览
     * @param {Object} fileInfo - 文件信息
     */
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

    /**
     * 格式化文件预览
     * @param {Object} fileInfo - 文件信息
     * @returns {string} 预览HTML
     */
    formatFilePreview(fileInfo) {
        if (fileInfo.data && fileInfo.data.content) {
            return `<pre>${fileInfo.data.content}</pre>`;
        } else {
            return `<p>文件大小: ${this.formatFileSize(fileInfo.file.size)}</p>
                    <p>文件类型: ${fileInfo.file.type || '未知'}</p>`;
        }
    }

    /**
     * 更新文件显示（删除后）
     * @param {string} fileName - 文件名
     */
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