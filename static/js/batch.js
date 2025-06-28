/**
 * 批量处理JavaScript
 */

class BatchProcessor {
    constructor() {
        this.selectedFiles = [];
        this.activeJobs = [];
        this.refreshInterval = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadActiveJobs();
        this.startAutoRefresh();
    }
    
    bindEvents() {
        // 文件选择
        const fileInput = document.getElementById('fileInput');
        const selectFilesBtn = document.getElementById('selectFilesBtn');
        const dropZone = document.getElementById('dropZone');
        
        selectFilesBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files);
            // 全局保存
            this.selectedFiles = Array.from(e.target.files);
        });
        
        // 拖拽上传
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            this.handleFileSelect(e.dataTransfer.files);
            // 全局保存
            this.selectedFiles = Array.from(e.dataTransfer.files);
        });
        
        // 开始批量处理
        document.getElementById('startBatchBtn').addEventListener('click', () => {
            this.startBatchProcessing();
        });
        
        // 刷新作业列表
        document.getElementById('refreshJobsBtn').addEventListener('click', () => {
            this.loadActiveJobs();
        });
        
        // 模态框关闭
        document.getElementById('closeModalBtn').addEventListener('click', () => {
            this.closeModal();
        });
        
        // 作业名称输入监听
        document.getElementById('jobName').addEventListener('input', () => {
            this.updateStartButton();
        });
    }
    
    handleFileSelect(files) {
        const fileArray = Array.from(files);
        
        // 过滤支持的文件类型
        const supportedTypes = ['.docx', '.pdf', '.txt', '.md'];
        const validFiles = fileArray.filter(file => {
            const extension = '.' + file.name.split('.').pop().toLowerCase();
            return supportedTypes.includes(extension);
        });
        
        if (validFiles.length !== fileArray.length) {
            this.showNotification('部分文件类型不支持，已自动过滤', 'warning');
        }
        
        // 添加到选中文件列表
        validFiles.forEach(file => {
            if (!this.selectedFiles.find(f => f.name === file.name)) {
                this.selectedFiles.push(file);
            }
        });
        
        this.updateFileList();
        this.updateStartButton();
    }
    
    updateFileList() {
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '';
        
        if (this.selectedFiles.length === 0) {
            return;
        }
        
        this.selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item flex items-center justify-between p-3 border border-gray-200 rounded-lg';
            
            fileItem.innerHTML = `
                <div class="flex items-center space-x-3">
                    <i class="fas fa-file-alt text-blue-600"></i>
                    <div>
                        <p class="text-sm font-medium text-gray-900">${file.name}</p>
                        <p class="text-xs text-gray-500">${this.formatFileSize(file.size)}</p>
                    </div>
                </div>
                <button class="text-red-600 hover:text-red-800" onclick="batchProcessor.removeFile(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            fileList.appendChild(fileItem);
        });
    }
    
    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.updateFileList();
        this.updateStartButton();
    }
    
    updateStartButton() {
        const startBtn = document.getElementById('startBatchBtn');
        const jobName = document.getElementById('jobName').value.trim();
        
        startBtn.disabled = this.selectedFiles.length === 0 || !jobName;
    }
    
    async startBatchProcessing() {
        const jobName = document.getElementById('jobName').value.trim();
        const operationType = document.getElementById('operationType').value;
        const parallelism = parseInt(document.getElementById('parallelism').value);
        const outputDir = document.getElementById('outputDir').value.trim();
        const overwriteFiles = document.getElementById('overwriteFiles').checked;
        
        if (this.selectedFiles.length === 0 || !jobName) {
            this.showNotification('请选择文件并输入作业名称', 'error');
            return;
        }
        
        this.showLoading(true);
        
        try {
            // 上传文件
            const uploadedFiles = await this.uploadFiles();
            
            // 创建批量处理作业
            const response = await fetch('/api/batch/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: jobName,
                    files: uploadedFiles,
                    processing_config: {
                        operation: operationType,
                        parallelism: parallelism,
                        output_dir: outputDir,
                        overwrite_files: overwriteFiles
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error('创建作业失败');
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('批量处理作业创建成功', 'success');
                
                // 启动作业
                await this.startJob(result.job_id);
                
                // 重置表单
                this.resetForm();
                
                // 刷新作业列表
                this.loadActiveJobs();
            } else {
                throw new Error(result.error || '创建作业失败');
            }
            
        } catch (error) {
            console.error('Error starting batch processing:', error);
            this.showNotification('启动批量处理失败: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async uploadFiles() {
        const uploadedFiles = [];

        for (const file of this.selectedFiles) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('batch_upload', 'true'); // 标记为批量上传

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('上传文件失败');
            }

            const result = await response.json();

            if (result.success) {
                uploadedFiles.push(result.file_path);
            } else {
                throw new Error(`上传文件 ${file.name} 失败: ${result.error}`);
            }
        }

        return uploadedFiles;
    }
    
    async startJob(jobId) {
        const response = await fetch(`/api/batch/start/${jobId}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('启动作业失败');
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || '启动作业失败');
        }
    }
    
    resetForm() {
        this.selectedFiles = [];
        document.getElementById('jobName').value = '';
        document.getElementById('operationType').value = 'document_parse';
        document.getElementById('parallelism').value = '3';
        document.getElementById('outputDir').value = 'output/batch_processing';
        document.getElementById('overwriteFiles').checked = false;
        
        this.updateFileList();
        this.updateStartButton();
    }
    
    async loadActiveJobs() {
        try {
            const response = await fetch('/api/batch/jobs');
            
            if (!response.ok) {
                throw new Error('加载作业列表失败');
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.activeJobs = result.jobs;
                this.updateJobsList();
            }
        } catch (error) {
            console.error('Error loading active jobs:', error);
        }
    }
    
    updateJobsList() {
        const jobsList = document.getElementById('jobsList');
        
        if (this.activeJobs.length === 0) {
            jobsList.innerHTML = `
                <div class="text-center text-gray-500 py-8">
                    <i class="fas fa-inbox text-4xl mb-4"></i>
                    <p>暂无批量处理作业</p>
                </div>
            `;
            return;
        }
        
        jobsList.innerHTML = '';
        
        this.activeJobs.forEach(job => {
            const jobCard = this.createJobCard(job);
            jobsList.appendChild(jobCard);
        });
    }
    
    createJobCard(job) {
        const card = document.createElement('div');
        card.className = 'job-card bg-gray-50 rounded-lg p-6 border border-gray-200';
        
        const progress = job.progress || {};
        const progressPercent = progress.total > 0 ? 
            (progress.processed / progress.total * 100).toFixed(1) : 0;
        
        const statusClass = `status-${job.status}`;
        const statusText = this.getStatusText(job.status);
        
        card.innerHTML = `
            <div class="flex justify-between items-start mb-4">
                <div>
                    <h3 class="text-lg font-semibold text-gray-900">${job.name}</h3>
                    <p class="text-sm text-gray-600">创建时间: ${new Date(job.created_at).toLocaleString()}</p>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="status-badge ${statusClass}">${statusText}</span>
                    <button class="text-blue-600 hover:text-blue-800" onclick="batchProcessor.showJobDetails('${job.id}')">
                        <i class="fas fa-info-circle"></i>
                    </button>
                    ${job.status === 'processing' ? 
                        `<button class="text-red-600 hover:text-red-800" onclick="batchProcessor.cancelJob('${job.id}')">
                            <i class="fas fa-stop-circle"></i>
                        </button>` : ''
                    }
                </div>
            </div>
            
            <div class="mb-4">
                <div class="flex justify-between text-sm text-gray-600 mb-2">
                    <span>进度: ${progress.processed || 0}/${progress.total || 0}</span>
                    <span>${progressPercent}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progressPercent}%"></div>
                </div>
            </div>
            
            <div class="grid grid-cols-3 gap-4 text-sm">
                <div class="text-center">
                    <div class="text-green-600 font-semibold">${progress.successful || 0}</div>
                    <div class="text-gray-500">成功</div>
                </div>
                <div class="text-center">
                    <div class="text-red-600 font-semibold">${progress.failed || 0}</div>
                    <div class="text-gray-500">失败</div>
                </div>
                <div class="text-center">
                    <div class="text-blue-600 font-semibold">${job.total_files || 0}</div>
                    <div class="text-gray-500">总计</div>
                </div>
            </div>
        `;
        
        return card;
    }
    
    getStatusText(status) {
        const statusMap = {
            'pending': '等待中',
            'processing': '处理中',
            'completed': '已完成',
            'failed': '失败',
            'cancelled': '已取消'
        };
        return statusMap[status] || status;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    showNotification(message, type = 'info') {
        // 简单的通知实现
        alert(message);
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }
    
    closeModal() {
        document.getElementById('jobDetailModal').style.display = 'none';
    }
    
    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.loadActiveJobs();
        }, 5000); // 每5秒刷新一次
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// 初始化批量处理器
let batchProcessor;
document.addEventListener('DOMContentLoaded', () => {
    batchProcessor = new BatchProcessor();
});

// 页面卸载时停止自动刷新
window.addEventListener('beforeunload', () => {
    if (batchProcessor) {
        batchProcessor.stopAutoRefresh();
    }
});

function readFileContentAsync(file, callback) {
    const reader = new FileReader();
    reader.onload = function(e) { callback(e.target.result); };
    reader.onerror = function() { showMessage('文件读取失败', 'error'); callback(null); };
    reader.readAsText(file);
}

async function processBatchFiles() {
    if (!this.selectedFiles || this.selectedFiles.length === 0) {
        showMessage('请先选择文件', 'error');
        return;
    }
    for (const file of this.selectedFiles) {
        await new Promise((resolve) => {
            readFileContentAsync(file, async (content) => {
                if (!content || content.trim() === '') {
                    showMessage('文件内容为空，跳过', 'warning');
                    resolve();
                    return;
                }
                // 举例：批量格式对齐
                try {
                    showLoading('正在格式对齐...');
                    const response = await fetch('/api/format-alignment', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ document_content: content, document_name: file.name })
                    });
                    const result = await response.json();
                    if (result.success) {
                        // 处理结果
                    } else {
                        showMessage(result.error || '格式对齐失败', 'error');
                    }
                } catch (err) {
                    showMessage('API调用失败: ' + err.message, 'error');
                } finally {
                    hideLoading();
                    resolve();
                }
            });
        });
    }
}
