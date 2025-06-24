/**
 * 文风分析与对齐功能的JavaScript模块
 */

class WritingStyleManager {
    constructor() {
        this.currentAnalysis = null;
        this.styleTemplates = [];
        
        this.initializeEventListeners();
        this.loadStyleTemplates();
    }

    initializeEventListeners() {
        // 文风分析文件上传
        const styleAnalysisInput = document.getElementById('style-analysis-input');
        const styleAnalysisUpload = document.getElementById('style-analysis-upload');
        
        if (styleAnalysisInput && styleAnalysisUpload) {
            styleAnalysisUpload.addEventListener('click', () => styleAnalysisInput.click());
            styleAnalysisInput.addEventListener('change', this.handleStyleFileSelect.bind(this));
        }

        // 分析按钮
        const analyzeStyleBtn = document.getElementById('analyze-style-btn');
        const analyzeTextBtn = document.getElementById('analyze-text-btn');
        
        if (analyzeStyleBtn) {
            analyzeStyleBtn.addEventListener('click', this.analyzeStyleFromFile.bind(this));
        }
        if (analyzeTextBtn) {
            analyzeTextBtn.addEventListener('click', this.analyzeStyleFromText.bind(this));
        }

        // 保存和测试按钮
        const saveTemplateBtn = document.getElementById('save-style-template');
        const testGenerationBtn = document.getElementById('test-style-generation');
        
        if (saveTemplateBtn) {
            saveTemplateBtn.addEventListener('click', this.saveStyleTemplate.bind(this));
        }
        if (testGenerationBtn) {
            testGenerationBtn.addEventListener('click', this.testStyleGeneration.bind(this));
        }

        // 刷新模板列表
        const refreshTemplatesBtn = document.getElementById('refresh-templates');
        if (refreshTemplatesBtn) {
            refreshTemplatesBtn.addEventListener('click', this.loadStyleTemplates.bind(this));
        }
    }

    handleStyleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.displayStyleFileInfo(file);
            this.currentStyleFile = file;
        }
    }

    displayStyleFileInfo(file) {
        const fileInfo = document.getElementById('style-file-info');
        const fileName = document.getElementById('style-file-name');
        const fileSize = document.getElementById('style-file-size');
        
        if (fileInfo && fileName && fileSize) {
            fileName.textContent = file.name;
            fileSize.textContent = this.formatFileSize(file.size);
            fileInfo.classList.remove('hidden');
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async analyzeStyleFromFile() {
        if (!this.currentStyleFile) {
            this.showError('请先选择文件');
            return;
        }

        this.showLoading('正在分析文风特征...');

        try {
            const content = await this.readFileContent(this.currentStyleFile);
            await this.performStyleAnalysis(content, this.currentStyleFile.name);
        } catch (error) {
            this.showError('文件读取失败: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    async analyzeStyleFromText() {
        const textInput = document.getElementById('style-text-input');
        if (!textInput || !textInput.value.trim()) {
            this.showError('请输入要分析的文本');
            return;
        }

        this.showLoading('正在分析文风特征...');

        try {
            await this.performStyleAnalysis(textInput.value.trim(), '文本输入');
        } catch (error) {
            this.showError('分析失败: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    async performStyleAnalysis(content, documentName) {
        try {
            const response = await fetch('/api/writing-style/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    document_content: content,
                    document_name: documentName
                })
            });

            const result = await response.json();
            
            if (result.error) {
                this.showError(result.error);
                return;
            }

            this.currentAnalysis = result;
            this.displayAnalysisResult(result);

        } catch (error) {
            this.showError('分析请求失败: ' + error.message);
        }
    }

    displayAnalysisResult(analysis) {
        const resultSection = document.getElementById('style-analysis-result');
        const resultContent = document.getElementById('style-analysis-content');
        
        if (!resultSection || !resultContent) return;

        // 显示结果区域
        resultSection.classList.remove('hidden');
        resultSection.scrollIntoView({ behavior: 'smooth' });

        // 构建分析结果HTML
        const features = analysis.style_features || {};
        const styleType = analysis.style_type || 'unknown';
        const confidence = analysis.confidence_score || 0;

        resultContent.innerHTML = `
            <div class="grid md:grid-cols-2 gap-6">
                <div class="space-y-4">
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <h6 class="font-semibold text-blue-800 mb-2">基本信息</h6>
                        <div class="space-y-2 text-sm">
                            <div class="flex justify-between">
                                <span class="text-blue-600">文档名称：</span>
                                <span class="font-medium">${analysis.document_name}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-blue-600">识别文风：</span>
                                <span class="font-medium">${this.getStyleTypeName(styleType)}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-blue-600">置信度：</span>
                                <span class="font-medium">${(confidence * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    </div>

                    <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                        <h6 class="font-semibold text-green-800 mb-2">句式结构</h6>
                        <div class="space-y-2 text-sm">
                            ${this.renderFeatureItem('平均句长', features.sentence_structure?.average_length, '字')}
                            ${this.renderFeatureItem('长短句比例', features.sentence_structure?.long_short_ratio, '', true)}
                            ${this.renderFeatureItem('复合句比例', features.sentence_structure?.complex_ratio, '', true)}
                        </div>
                    </div>

                    <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
                        <h6 class="font-semibold text-purple-800 mb-2">词汇选择</h6>
                        <div class="space-y-2 text-sm">
                            ${this.renderFeatureItem('正式程度', features.vocabulary_choice?.formality_score)}
                            ${this.renderFeatureItem('专业术语密度', features.vocabulary_choice?.technical_density)}
                            ${this.renderFeatureItem('修饰词使用', features.vocabulary_choice?.modifier_usage)}
                        </div>
                    </div>
                </div>

                <div class="space-y-4">
                    <div class="bg-orange-50 border border-orange-200 rounded-lg p-4">
                        <h6 class="font-semibold text-orange-800 mb-2">表达方式</h6>
                        <div class="space-y-2 text-sm">
                            ${this.renderFeatureItem('被动/主动比例', features.expression_style?.passive_active_ratio)}
                            ${this.renderFeatureItem('语气强度', features.expression_style?.tone_strength)}
                        </div>
                    </div>

                    <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <h6 class="font-semibold text-gray-800 mb-2">文本组织</h6>
                        <div class="space-y-2 text-sm">
                            ${this.renderFeatureItem('段落数量', features.text_organization?.paragraph_count)}
                            ${this.renderFeatureItem('连接词密度', features.text_organization?.connector_density)}
                            ${this.renderFeatureItem('总结性表达', features.text_organization?.summary_usage)}
                        </div>
                    </div>

                    <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <h6 class="font-semibold text-yellow-800 mb-2">语言习惯</h6>
                        <div class="space-y-2 text-sm">
                            ${this.renderFeatureItem('口语化程度', features.language_habits?.colloquial_level)}
                            ${this.renderFeatureItem('书面语规范', features.language_habits?.formal_structure_usage)}
                            ${this.renderFeatureItem('"的"字结构密度', features.language_habits?.de_structure_density)}
                        </div>
                    </div>
                </div>
            </div>

            <div class="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h6 class="font-semibold text-gray-800 mb-2">生成的文风提示词</h6>
                <div class="bg-white border rounded p-3 text-sm max-h-32 overflow-y-auto">
                    <pre class="whitespace-pre-wrap text-gray-700">${analysis.style_prompt || '暂无提示词'}</pre>
                </div>
            </div>
        `;
    }

    renderFeatureItem(label, value, unit = '', isPercentage = false) {
        if (value === undefined || value === null) {
            return `
                <div class="flex justify-between">
                    <span class="text-gray-600">${label}：</span>
                    <span class="text-gray-400">-</span>
                </div>
            `;
        }

        let displayValue = value;
        if (isPercentage) {
            displayValue = (value * 100).toFixed(1) + '%';
        } else if (unit) {
            displayValue = value + unit;
        } else if (typeof value === 'number') {
            displayValue = value.toFixed(2);
        }

        return `
            <div class="flex justify-between">
                <span class="text-gray-600">${label}：</span>
                <span class="font-medium">${displayValue}</span>
            </div>
        `;
    }

    getStyleTypeName(styleType) {
        const styleNames = {
            'formal_official': '正式公文风格',
            'business_professional': '商务专业风格',
            'academic_research': '学术研究风格',
            'narrative_descriptive': '叙述描述风格',
            'concise_practical': '简洁实用风格'
        };
        return styleNames[styleType] || '未知风格';
    }

    async saveStyleTemplate() {
        if (!this.currentAnalysis) {
            this.showError('请先进行文风分析');
            return;
        }

        const templateName = prompt('请输入模板名称:', this.currentAnalysis.document_name);
        if (!templateName) return;

        this.showLoading('正在保存文风模板...');

        try {
            const response = await fetch('/api/writing-style/save-template', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    reference_content: this.getCurrentAnalysisContent(),
                    reference_name: templateName
                })
            });

            const result = await response.json();
            
            if (result.error) {
                this.showError(result.error);
                return;
            }

            this.showSuccess('文风模板保存成功！');
            this.loadStyleTemplates(); // 刷新模板列表

        } catch (error) {
            this.showError('保存失败: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    getCurrentAnalysisContent() {
        // 获取当前分析的原始内容
        const textInput = document.getElementById('style-text-input');
        if (textInput && textInput.value.trim()) {
            return textInput.value.trim();
        }
        
        // 如果是文件上传，需要重新读取文件内容
        // 这里简化处理，实际应该保存原始内容
        return '文风分析内容';
    }

    async testStyleGeneration() {
        if (!this.currentAnalysis) {
            this.showError('请先进行文风分析');
            return;
        }

        const testText = prompt('请输入要测试的内容:', '请生成一份工作总结');
        if (!testText) return;

        this.showLoading('正在测试文风生成...');

        try {
            // 这里应该调用文风应用API
            // 暂时显示模拟结果
            setTimeout(() => {
                alert('文风测试功能开发中...');
                this.hideLoading();
            }, 1000);

        } catch (error) {
            this.showError('测试失败: ' + error.message);
            this.hideLoading();
        }
    }

    async loadStyleTemplates() {
        try {
            const response = await fetch('/api/writing-style/templates');
            const result = await response.json();
            
            if (result.success) {
                this.styleTemplates = result.templates;
                this.displayStyleTemplatesManagement(result.templates);
            }
        } catch (error) {
            console.error('加载文风模板失败:', error);
        }
    }

    displayStyleTemplatesManagement(templates) {
        const managementSection = document.getElementById('style-templates-management');
        if (!managementSection) return;

        managementSection.innerHTML = '';

        if (templates.length === 0) {
            managementSection.innerHTML = `
                <div class="text-center text-gray-500 py-8">
                    <i class="fas fa-bookmark text-3xl mb-2"></i>
                    <p>暂无保存的文风模板</p>
                    <p class="text-sm">上传范文进行分析后可保存为模板</p>
                </div>
            `;
            return;
        }

        templates.forEach(template => {
            const templateCard = document.createElement('div');
            templateCard.className = 'bg-gray-50 border border-gray-200 rounded-lg p-4 hover:bg-gray-100 transition-colors';
            
            templateCard.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <h6 class="font-semibold text-gray-800">${template.name}</h6>
                        <p class="text-sm text-gray-600">${template.style_name}</p>
                        <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            <span>置信度: ${(template.confidence_score * 100).toFixed(1)}%</span>
                            <span>创建时间: ${template.created_time.split('T')[0]}</span>
                        </div>
                    </div>
                    <div class="flex space-x-2">
                        <button class="text-blue-500 hover:text-blue-700 p-2" onclick="writingStyleManager.viewTemplate('${template.template_id}')" title="查看详情">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="text-green-500 hover:text-green-700 p-2" onclick="writingStyleManager.useTemplate('${template.template_id}')" title="使用模板">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="text-red-500 hover:text-red-700 p-2" onclick="writingStyleManager.deleteTemplate('${template.template_id}')" title="删除模板">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
            
            managementSection.appendChild(templateCard);
        });
    }

    async viewTemplate(templateId) {
        try {
            const response = await fetch(`/api/writing-style/templates/${templateId}`);
            const result = await response.json();
            
            if (result.success) {
                this.displayTemplateDetails(result.template);
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('获取模板详情失败: ' + error.message);
        }
    }

    displayTemplateDetails(template) {
        // 创建模态框显示模板详情
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-2xl max-h-96 overflow-y-auto">
                <div class="flex justify-between items-center mb-4">
                    <h5 class="text-lg font-semibold">文风模板详情</h5>
                    <button class="text-gray-500 hover:text-gray-700" onclick="this.closest('.fixed').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="space-y-4">
                    <div>
                        <strong>模板名称：</strong>${template.document_name}
                    </div>
                    <div>
                        <strong>文风类型：</strong>${this.getStyleTypeName(template.style_type)}
                    </div>
                    <div>
                        <strong>置信度：</strong>${(template.confidence_score * 100).toFixed(1)}%
                    </div>
                    <div>
                        <strong>文风提示词：</strong>
                        <pre class="bg-gray-100 p-3 rounded text-sm mt-2 whitespace-pre-wrap">${template.style_prompt}</pre>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    async useTemplate(templateId) {
        // 在文档填充中使用此模板
        if (window.documentFillManager) {
            window.documentFillManager.selectedStyleTemplate = templateId;
            this.showSuccess('文风模板已选择，可在文档填充中使用');
        } else {
            this.showSuccess('文风模板已选择');
        }
    }

    async deleteTemplate(templateId) {
        if (!confirm('确定要删除这个文风模板吗？')) return;

        try {
            // 这里应该调用删除API
            // 暂时只是从列表中移除
            this.showSuccess('删除功能开发中...');
        } catch (error) {
            this.showError('删除失败: ' + error.message);
        }
    }

    async readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    showLoading(message = '处理中...') {
        console.log('Loading:', message);
        // 可以添加实际的加载UI
    }

    hideLoading() {
        console.log('Loading hidden');
    }

    showError(message) {
        alert('错误: ' + message);
    }

    showSuccess(message) {
        alert('成功: ' + message);
    }
}

// 初始化文风管理器
document.addEventListener('DOMContentLoaded', () => {
    window.writingStyleManager = new WritingStyleManager();
});
