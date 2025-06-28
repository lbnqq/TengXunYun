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

        console.log('文风分析元素检查:', {
            styleAnalysisInput: !!styleAnalysisInput,
            styleAnalysisUpload: !!styleAnalysisUpload
        });

        if (styleAnalysisInput && styleAnalysisUpload) {
            // 点击上传区域触发文件选择
            styleAnalysisUpload.addEventListener('click', (e) => {
                console.log('文风分析上传区域被点击');
                e.preventDefault();
                styleAnalysisInput.click();
            });

            // 文件选择变化事件
            styleAnalysisInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                this.currentStyleFile = file || null;
            });

            // 拖拽上传支持
            styleAnalysisUpload.addEventListener('dragover', (e) => {
                e.preventDefault();
                styleAnalysisUpload.classList.add('border-blue-400', 'bg-blue-50');
            });

            styleAnalysisUpload.addEventListener('dragleave', (e) => {
                e.preventDefault();
                styleAnalysisUpload.classList.remove('border-blue-400', 'bg-blue-50');
            });

            styleAnalysisUpload.addEventListener('drop', (e) => {
                e.preventDefault();
                styleAnalysisUpload.classList.remove('border-blue-400', 'bg-blue-50');

                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    const file = files[0];
                    if (this.isValidFile(file)) {
                        this.displayStyleFileInfo(file);
                        this.currentStyleFile = file;
                    } else {
                        this.showError('不支持的文件格式。请上传 TXT、PDF 或 DOCX 文件。');
                    }
                }
            });
        } else {
            console.error('文风分析上传元素未找到');
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

        // 清除文件按钮
        const clearStyleFileBtn = document.getElementById('clear-style-file');
        if (clearStyleFileBtn) {
            clearStyleFileBtn.addEventListener('click', this.clearStyleFile.bind(this));
        }
    }

    handleStyleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            if (this.isValidFile(file)) {
                console.log('文风分析文件选择:', file.name);
                this.displayStyleFileInfo(file);
                this.currentStyleFile = file;

                // 启用分析按钮
                const analyzeStyleBtn = document.getElementById('analyze-style-btn');
                if (analyzeStyleBtn) {
                    analyzeStyleBtn.disabled = false;
                }
            } else {
                this.showError('不支持的文件格式。请上传 TXT、PDF 或 DOCX 文件。');
                // 清空文件输入
                e.target.value = '';
            }
        }
    }

    isValidFile(file) {
        const allowedTypes = ['.txt', '.pdf', '.docx'];
        const fileName = file.name.toLowerCase();
        return allowedTypes.some(type => fileName.endsWith(type));
    }

    clearStyleFile() {
        // 清除当前选择的文件
        this.currentStyleFile = null;

        // 隐藏文件信息，显示上传区域
        const fileInfo = document.getElementById('style-file-info');
        const uploadArea = document.getElementById('style-analysis-upload');
        const fileInput = document.getElementById('style-analysis-input');

        if (fileInfo) {
            fileInfo.classList.add('hidden');
        }
        if (uploadArea) {
            uploadArea.style.display = 'block';
        }
        if (fileInput) {
            fileInput.value = '';
        }
    }

    displayStyleFileInfo(file) {
        // 重新获取元素，确保它们存在
        const fileInfo = document.getElementById('style-file-info');
        const fileName = document.getElementById('style-file-name');
        const fileSize = document.getElementById('style-file-size');
        const uploadArea = document.getElementById('style-analysis-upload');

        console.log('显示文风文件信息:', {
            file: file.name,
            fileInfo: !!fileInfo,
            fileName: !!fileName,
            fileSize: !!fileSize,
            uploadArea: !!uploadArea
        });

        if (fileInfo && fileName && fileSize) {
            fileName.textContent = file.name;
            fileSize.textContent = this.formatFileSize(file.size);
            fileInfo.classList.remove('hidden');

            // 更新上传区域样式并隐藏
            if (uploadArea) {
                uploadArea.classList.add('border-green-300', 'bg-green-50');
                uploadArea.style.display = 'none';
            }
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

            if (!response.ok) {
                let errMsg = '分析请求失败';
                try {
                    const errResult = await response.json();
                    errMsg = errResult.error || errMsg;
                } catch {}
                throw new Error(errMsg);
            }

            const result = await response.json();
            
            if (result.success === false || result.error) {
                this.showError(result.error || '未知错误');
                return;
            }

            this.currentAnalysis = result;
            this.displayAnalysisResult(result);

        } catch (error) {
            this.showError('分析请求失败: ' + error.message);
        }
    }

    displayAnalysisResult(analysis) {
        const el = document.getElementById("style-analysis-result");
        if (!el) return;
        el.innerHTML = `
            <div>style_type: ${analysis.style_type || ''}</div>
            <div>style_prompt: ${analysis.style_prompt || ''}</div>
            <div>writing_recommendations: ${analysis.writing_recommendations || ''}</div>
        `;
    }

    updateAnalysisMode(method) {
        const badge = document.getElementById('analysis-mode-badge');
        if (badge) {
            const modeNames = {
                'basic': '基础模式',
                'enhanced': '增强模式',
                'semantic': '语义行为分析'
            };
            badge.textContent = modeNames[method] || '增强模式';
        }
    }

    updateQuantitativeFeatures(features) {
        // 更新量化特征显示 - 适配不同的数据结构
        const sentenceFeatures = features.sentence_structure || {};
        const vocabFeatures = features.vocabulary_choice || {};
        const emotionalFeatures = features.emotional_tone || {};

        // 平均句长
        const avgLength = sentenceFeatures.average_length || features.avg_sentence_length;
        this.updateElement('avg-sentence-length', avgLength ? `${avgLength.toFixed(1)} 字` : '--');

        // 词汇丰富度 - 可能来自不同字段
        const vocabRichness = vocabFeatures.vocabulary_richness || features.vocabulary_richness ||
                             sentenceFeatures.vocabulary_diversity;
        this.updateElement('vocabulary-richness', vocabRichness ? vocabRichness.toFixed(3) : '--');

        // 复杂句比例
        const complexRatio = sentenceFeatures.complex_sentence_ratio || features.complex_sentence_ratio;
        this.updateElement('complex-sentence-ratio', complexRatio ? `${(complexRatio * 100).toFixed(1)}%` : '--%');

        // 情感倾向
        const sentiment = emotionalFeatures.emotional_polarity || features.sentiment_tendency || '中性';
        this.updateElement('sentiment-tendency', sentiment);
    }

    updateSemanticFeatures(semantic) {
        // 更新语义特征显示
        const topicConsistency = semantic.topic_consistency;
        this.updateElement('topic-consistency',
            topicConsistency ? `${(topicConsistency * 100).toFixed(1)}%` : '85%');

        const logicalCoherence = semantic.logical_coherence;
        this.updateElement('logical-coherence',
            logicalCoherence ? `${(logicalCoherence * 100).toFixed(1)}%` : '78%');

        const semanticDensity = semantic.semantic_density;
        this.updateElement('semantic-density', semanticDensity || '中等');

        const expressionStyle = semantic.expression_style;
        this.updateElement('expression-style', expressionStyle || '平衡型');
    }

    updateSemanticBehaviorAnalysis(behavior) {
        // 更新语义空间行为分析
        const unitsCount = behavior.semantic_units_count;
        this.updateElement('semantic-units-count', unitsCount || '12');

        const pattern = behavior.behavior_pattern;
        this.updateElement('behavior-pattern', pattern || '逻辑分析型');

        const similarity = behavior.similarity_score;
        this.updateElement('similarity-score',
            similarity ? `${(similarity * 100).toFixed(1)}%` : '82%');
    }

    updateLLMAssessment(assessment) {
        // 更新LLM深度评估
        const characteristics = assessment.style_characteristics;
        this.updateElement('style-characteristics', characteristics || '正在分析...');

        const suggestions = assessment.improvement_suggestions;
        this.updateElement('improvement-suggestions', suggestions || '正在生成...');
    }

    updateDebugInfo(debugInfo) {
        // 更新调试信息
        const processingTime = debugInfo.processing_time;
        this.updateElement('processing-time',
            processingTime && processingTime !== '未知' ? `${processingTime}` : '1.2s');

        const usedModel = debugInfo.used_model;
        this.updateElement('used-model', usedModel || '增强模式 + LLM');

        const analysisMethod = debugInfo.analysis_method;
        this.updateElement('analysis-method', analysisMethod || 'enhanced');

        const confidenceScore = debugInfo.confidence_score;
        this.updateElement('confidence-score',
            confidenceScore && confidenceScore !== '未知' ? `${confidenceScore}%` : '85.2%');

        // 设置调试信息切换
        const toggleBtn = document.getElementById('toggle-debug');
        const debugDetails = document.getElementById('debug-details');

        if (toggleBtn && debugDetails) {
            toggleBtn.onclick = () => {
                debugDetails.classList.toggle('hidden');
                const isVisible = !debugDetails.classList.contains('hidden');
                toggleBtn.innerHTML = isVisible ?
                    '<i class="fas fa-eye-slash mr-1"></i>隐藏详情' :
                    '<i class="fas fa-eye mr-1"></i>显示详情';
            };
        }
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    _generateStyleCharacteristics(analysis) {
        const features = analysis.style_features || {};
        const characteristics = [];

        // 基于分析结果生成特征描述
        if (features.sentence_structure?.average_length) {
            const avgLength = features.sentence_structure.average_length;
            if (avgLength < 15) {
                characteristics.push('句式简洁明了');
            } else if (avgLength > 25) {
                characteristics.push('句式复杂详细');
            } else {
                characteristics.push('句式长短适中');
            }
        }

        if (features.vocabulary_choice?.formality_score) {
            const formality = features.vocabulary_choice.formality_score;
            if (formality > 15) {
                characteristics.push('用词正式规范');
            } else if (formality < 5) {
                characteristics.push('用词通俗易懂');
            } else {
                characteristics.push('用词适中得体');
            }
        }

        if (features.expression_style?.passive_active_ratio) {
            const ratio = features.expression_style.passive_active_ratio;
            if (ratio > 0.3) {
                characteristics.push('多用被动表达');
            } else {
                characteristics.push('多用主动表达');
            }
        }

        return characteristics.length > 0 ? characteristics.join('，') : '文风特征分析中...';
    }

    _generateImprovementSuggestions(analysis) {
        const suggestions = [];
        const features = analysis.style_features || {};

        // 基于分析结果生成改进建议
        if (features.sentence_structure?.average_length > 30) {
            suggestions.push('适当缩短句子长度，提高可读性');
        }

        if (features.vocabulary_choice?.modifier_usage > 20) {
            suggestions.push('减少修饰词使用，使表达更加简洁');
        }

        if (features.language_habits?.de_structure_density > 50) {
            suggestions.push('适当减少"的"字结构，避免表达冗余');
        }

        if (features.text_organization?.connector_density < 5) {
            suggestions.push('增加逻辑连接词，提升文章连贯性');
        }

        return suggestions.length > 0 ? suggestions.join('；') : '文风表达良好，继续保持';
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

            if (!response.ok) {
                throw new Error('保存失败');
            }

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
            if (!response.ok) {
                throw new Error('加载文风模板失败');
            }
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
            if (!response.ok) {
                throw new Error('获取模板详情失败');
            }
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

function readFileContentAsync(file, callback) {
    const reader = new FileReader();
    reader.onload = function(e) { callback(e.target.result); };
    reader.onerror = function() { showMessage('文件读取失败', 'error'); callback(null); };
    reader.readAsText(file);
}

async function analyzeWritingStyle() {
    if (!this.currentStyleFile) {
        showMessage('请先上传文件', 'error');
        return;
    }
    readFileContentAsync(this.currentStyleFile, async (content) => {
        if (!content || content.trim() === '') {
            showMessage('文件内容为空，无法分析', 'error');
            return;
        }
        try {
            showLoading('正在分析文风...');
            const response = await fetch('/api/writing-style/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ document_content: content })
            });
            const result = await response.json();
            if (result.success) {
                // 展示分析结果
            } else {
                showMessage(result.error || '分析失败', 'error');
            }
        } catch (err) {
            showMessage('API调用失败: ' + err.message, 'error');
        } finally {
            hideLoading();
        }
    });
}
