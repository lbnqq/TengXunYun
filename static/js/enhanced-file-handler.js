/**
 * 增强版文件处理器
 * 功能：文件上传、验证、预处理、下载和二进制响应处理
 * 版本：2.0.0
 */

class EnhancedFileHandler {
    constructor() {
        this.supportedFormats = {
            document: ['.docx', '.doc', '.txt', '.rtf', '.pdf'],
            image: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            spreadsheet: ['.xlsx', '.xls', '.csv'],
            presentation: ['.pptx', '.ppt']
        };
        this.maxFileSize = 50 * 1024 * 1024; // 50MB
        this.uploadQueue = [];
        this.activeUploads = new Map();
        this.downloadCallbacks = new Map();
    }

    /**
     * 验证文件
     * @param {File} file - 文件对象
     * @param {string} expectedType - 期望的文件类型
     * @returns {Object} 验证结果
     */
    validateFile(file, expectedType = 'document') {
        const result = {
            isValid: true,
            errors: [],
            warnings: [],
            fileType: this.detectFileType(file),
            size: file.size,
            name: file.name
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

        // 检查文件名中的特殊字符
        const invalidChars = /[<>:"/\\|?*]/;
        if (invalidChars.test(file.name)) {
            result.warnings.push('文件名包含特殊字符，建议修改');
        }

        return result;
    }

    /**
     * 检测文件类型
     * @param {File} file - 文件对象
     * @returns {string} 文件类型
     */
    detectFileType(file) {
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        
        for (const [type, extensions] of Object.entries(this.supportedFormats)) {
            if (extensions.includes(extension)) {
                return type;
            }
        }
        
        return 'unknown';
    }

    /**
     * 预处理文件
     * @param {File} file - 文件对象
     * @returns {Promise<Object>} 预处理结果
     */
    async preprocessFile(file) {
        const result = {
            success: true,
            data: null,
            errors: [],
            metadata: {
                name: file.name,
                size: file.size,
                type: file.type,
                lastModified: file.lastModified,
                detectedType: this.detectFileType(file)
            }
        };

        try {
            // 根据文件类型进行不同的预处理
            switch (result.metadata.detectedType) {
                case 'document':
                    result.data = await this.preprocessDocument(file);
                    break;
                case 'image':
                    result.data = await this.preprocessImage(file);
                    break;
                case 'spreadsheet':
                    result.data = await this.preprocessSpreadsheet(file);
                    break;
                case 'presentation':
                    result.data = await this.preprocessPresentation(file);
                    break;
                default:
                    result.data = await this.preprocessGenericFile(file);
            }
        } catch (error) {
            result.success = false;
            result.errors.push(`文件预处理失败: ${error.message}`);
        }

        return result;
    }

    /**
     * 预处理文档文件
     * @param {File} file - 文件对象
     * @returns {Promise<Object>} 预处理结果
     */
    async preprocessDocument(file) {
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (extension === '.txt' || extension === '.rtf') {
            return await this.readTextFile(file);
        } else if (extension === '.docx' || extension === '.doc') {
            return await this.readWordDocument(file);
        } else if (extension === '.pdf') {
            return await this.readPDFDocument(file);
        }
        
        return { content: null, error: '不支持的文档格式' };
    }

    /**
     * 预处理图片文件
     * @param {File} file - 文件对象
     * @returns {Promise<Object>} 预处理结果
     */
    async preprocessImage(file) {
        return new Promise((resolve) => {
            const img = new Image();
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            img.onload = () => {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                
                const dataURL = canvas.toDataURL('image/jpeg', 0.8);
                resolve({
                    width: img.width,
                    height: img.height,
                    dataURL: dataURL,
                    format: 'jpeg'
                });
            };
            
            img.onerror = () => {
                resolve({ error: '图片加载失败' });
            };
            
            img.src = URL.createObjectURL(file);
        });
    }

    /**
     * 预处理电子表格文件
     * @param {File} file - 文件对象
     * @returns {Promise<Object>} 预处理结果
     */
    async preprocessSpreadsheet(file) {
        // 对于Excel文件，我们只能获取基本信息
        return {
            type: 'spreadsheet',
            sheets: '未知',
            size: file.size,
            format: file.name.split('.').pop().toLowerCase()
        };
    }

    /**
     * 预处理演示文件
     * @param {File} file - 文件对象
     * @returns {Promise<Object>} 预处理结果
     */
    async preprocessPresentation(file) {
        // 对于PPT文件，我们只能获取基本信息
        return {
            type: 'presentation',
            slides: '未知',
            size: file.size,
            format: file.name.split('.').pop().toLowerCase()
        };
    }

    /**
     * 预处理通用文件
     * @param {File} file - 文件对象
     * @returns {Promise<Object>} 预处理结果
     */
    async preprocessGenericFile(file) {
        return {
            type: 'generic',
            size: file.size,
            format: file.name.split('.').pop().toLowerCase()
        };
    }

    /**
     * 读取文本文件
     * @param {File} file - 文件对象
     * @returns {Promise<Object>} 读取结果
     */
    readTextFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                resolve({
                    content: e.target.result,
                    encoding: 'utf-8',
                    lines: e.target.result.split('\n').length
                });
            };
            reader.onerror = (e) => reject(new Error('文件读取失败'));
            reader.readAsText(file, 'utf-8');
        });
    }

    /**
     * 读取Word文档
     * @param {File} file - 文件对象
     * @returns {Promise<Object>} 读取结果
     */
    async readWordDocument(file) {
        // 对于Word文档，我们返回基本信息
        return {
            type: 'word',
            format: file.name.split('.').pop().toLowerCase(),
            size: file.size
        };
    }

    /**
     * 读取PDF文档
     * @param {File} file - 文件对象
     * @returns {Promise<Object>} 读取结果
     */
    async readPDFDocument(file) {
        // 对于PDF文档，我们返回基本信息
        return {
            type: 'pdf',
            format: 'pdf',
            size: file.size
        };
    }

    /**
     * 上传文件
     * @param {File} file - 文件对象
     * @param {string} endpoint - 上传端点
     * @param {Object} options - 上传选项
     * @returns {Promise<Object>} 上传结果
     */
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
                        const response = this.parseResponse(xhr);
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

    /**
     * 解析响应
     * @param {XMLHttpRequest} xhr - XHR对象
     * @returns {Object} 解析后的响应
     */
    parseResponse(xhr) {
        const contentType = xhr.getResponseHeader('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            return JSON.parse(xhr.responseText);
        } else if (contentType && contentType.includes('application/vnd.openxmlformats-officedocument.wordprocessingml.document')) {
            return {
                type: 'docx',
                blob: new Blob([xhr.response], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
            };
        } else if (contentType && contentType.includes('application/pdf')) {
            return {
                type: 'pdf',
                blob: new Blob([xhr.response], { type: 'application/pdf' })
            };
        } else {
            return {
                type: 'text',
                content: xhr.responseText
            };
        }
    }

    /**
     * 更新上传进度
     * @param {string} uploadId - 上传ID
     * @param {number} progress - 进度百分比
     */
    updateUploadProgress(uploadId, progress) {
        const callback = this.downloadCallbacks.get(uploadId);
        if (callback && callback.onProgress) {
            callback.onProgress(progress);
        }
    }

    /**
     * 下载文件
     * @param {string} endpoint - 下载端点
     * @param {Object} data - 请求数据
     * @param {string} filename - 文件名
     * @param {Object} options - 下载选项
     */
    async downloadFile(endpoint, data, filename, options = {}) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`下载失败: ${response.status} ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            let blob;

            if (contentType && contentType.includes('application/json')) {
                const jsonResponse = await response.json();
                if (jsonResponse.error) {
                    throw new Error(jsonResponse.error);
                }
                // 如果JSON响应包含文件数据
                if (jsonResponse.fileData) {
                    blob = new Blob([jsonResponse.fileData], { type: jsonResponse.fileType || 'application/octet-stream' });
                } else {
                    throw new Error('响应中没有文件数据');
                }
            } else {
                blob = await response.blob();
            }

            this.createDownloadLink(blob, filename);
            
        } catch (error) {
            console.error('下载失败:', error);
            throw error;
        }
    }

    /**
     * 创建下载链接
     * @param {Blob} blob - 文件blob
     * @param {string} filename - 文件名
     */
    createDownloadLink(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * 批量上传文件
     * @param {File[]} files - 文件数组
     * @param {string} endpoint - 上传端点
     * @param {Object} options - 上传选项
     * @returns {Promise<Object[]>} 上传结果数组
     */
    async batchUploadFiles(files, endpoint, options = {}) {
        const results = [];
        const totalFiles = files.length;
        
        for (let i = 0; i < totalFiles; i++) {
            try {
                const file = files[i];
                const result = await this.uploadFile(file, endpoint, options);
                results.push({
                    file: file.name,
                    success: true,
                    result: result
                });
            } catch (error) {
                results.push({
                    file: files[i].name,
                    success: false,
                    error: error.message
                });
            }
        }
        
        return results;
    }

    /**
     * 验证文件集合
     * @param {File[]} files - 文件数组
     * @param {string} expectedType - 期望的文件类型
     * @returns {Object} 验证结果
     */
    validateFileCollection(files, expectedType = 'document') {
        const results = {
            valid: [],
            invalid: [],
            total: files.length,
            totalSize: 0
        };

        files.forEach(file => {
            const validation = this.validateFile(file, expectedType);
            results.totalSize += file.size;
            
            if (validation.isValid) {
                results.valid.push({
                    file: file,
                    validation: validation
                });
            } else {
                results.invalid.push({
                    file: file,
                    validation: validation
                });
            }
        });

        return results;
    }

    /**
     * 获取文件预览
     * @param {File} file - 文件对象
     * @returns {Promise<string>} 预览URL
     */
    getFilePreview(file) {
        return new Promise((resolve, reject) => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => resolve(e.target.result);
                reader.onerror = (e) => reject(new Error('图片预览失败'));
                reader.readAsDataURL(file);
            } else {
                resolve(null);
            }
        });
    }

    /**
     * 压缩文件
     * @param {File} file - 文件对象
     * @param {number} quality - 压缩质量 (0-1)
     * @returns {Promise<Blob>} 压缩后的文件
     */
    async compressFile(file, quality = 0.8) {
        if (file.type.startsWith('image/')) {
            return new Promise((resolve) => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                const img = new Image();
                
                img.onload = () => {
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    
                    canvas.toBlob((blob) => {
                        resolve(blob);
                    }, file.type, quality);
                };
                
                img.src = URL.createObjectURL(file);
            });
        } else {
            return file;
        }
    }
}

// 创建全局文件处理器实例
const enhancedFileHandler = new EnhancedFileHandler();

// 导出全局实例
window.enhancedFileHandler = enhancedFileHandler; 