// app.js - Smart Document Assistant Frontend Logic

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    // Ensure the page title is set immediately for tests
    document.title = "办公文档智能代理";
});

function initializeApp() {
    setupNavigation();
    setupFileUploads();
    setupActionButtons();
    setupManagementTabs();
    loadInitialData();
}

function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const sceneId = this.getAttribute('data-scene');
            switchScene(sceneId);
        });
    });
}

function switchScene(sceneId) {
    const scenes = document.querySelectorAll('.scene-section');
    scenes.forEach(scene => {
        scene.classList.add('hidden');
    });
    const activeScene = document.getElementById(`scene-${sceneId}`);
    if (activeScene) {
        activeScene.classList.remove('hidden');
        // Scroll to the top of the active scene to ensure visibility for tests
        activeScene.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    updateActiveNavItem(sceneId);
}

function updateActiveNavItem(sceneId) {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-scene') === sceneId) {
            item.classList.add('active');
        }
    });
}

function setupFileUploads() {
    // 参考格式文件
    const formatBaseInput = document.getElementById('upload-format-base');
    if (formatBaseInput) {
        formatBaseInput.addEventListener('change', function() {
            window.formatBaseFile = this.files && this.files.length > 0 ? this.files[0] : null;
        });
    }
    // 待处理文档
    const formatTargetInput = document.getElementById('upload-format-target');
    if (formatTargetInput) {
        formatTargetInput.addEventListener('change', function() {
            window.formatTargetFile = this.files && this.files.length > 0 ? this.files[0] : null;
        });
    }
    // 兼容原有input-file逻辑
    const fileInputs = document.querySelectorAll('.input-file');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileNameSpan = this.nextElementSibling;
            if (this.files.length > 0) {
                if (this.files.length > 1) {
                    fileNameSpan.textContent = `${this.files.length} files selected`;
                } else {
                    fileNameSpan.textContent = this.files[0].name;
                }
            } else {
                fileNameSpan.textContent = '';
            }
        });
    });
}

function setupActionButtons() {
    // Format Alignment
    document.querySelector('.btn-apply-format').addEventListener('click', applyFormat);
    document.querySelector('.btn-set-baseline').addEventListener('click', setFormatBaseline);
    document.querySelector('.btn-save-format').addEventListener('click', saveFormat);

    // Style Alignment
    document.querySelector('.btn-analyze-style').addEventListener('click', analyzeStyle);
    document.querySelector('.btn-apply-style').addEventListener('click', applyStyle);
    document.querySelector('.btn-accept-all-style').addEventListener('click', acceptAllStyleChanges);
    document.querySelector('.btn-reject-all-style').addEventListener('click', rejectAllStyleChanges);
    document.querySelector('.btn-export-styled-doc').addEventListener('click', exportStyledDocument);
    document.querySelector('.btn-save-style').addEventListener('click', saveStyle);

    // Intelligent Filling
    document.querySelector('.btn-auto-match-data').addEventListener('click', autoMatchData);
    document.querySelector('.btn-export-filled-doc').addEventListener('click', exportFilledDocument);

    // Document Review
    document.querySelector('.btn-start-review').addEventListener('click', startReview);
    document.querySelector('.btn-accept-all-issues').addEventListener('click', acceptAllIssues);
    document.querySelector('.btn-reject-all-issues').addEventListener('click', rejectAllIssues);
    document.querySelector('.btn-export-reviewed-doc').addEventListener('click', exportReviewedDocument);

    // Setup individual accept/reject buttons for review suggestions
    setupReviewSuggestionButtons();
}

function setupManagementTabs() {
    const tabButtons = document.querySelectorAll('.btn-tab');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            switchManagementTab(tabId);
        });
    });
}

function switchManagementTab(tabId) {
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    const activeTab = document.querySelector(`[data-tab-content="${tabId}"]`);
    if (activeTab) {
        activeTab.classList.add('active');
    }
    updateActiveTabButton(tabId);
}

function updateActiveTabButton(tabId) {
    const tabButtons = document.querySelectorAll('.btn-tab');
    tabButtons.forEach(button => {
        button.classList.remove('active');
        if (button.getAttribute('data-tab') === tabId) {
            button.classList.add('active');
        }
    });
}

function loadInitialData() {
    // Load format templates
    fetch('/api/format-templates')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success && Array.isArray(data.templates)) {
                updateFormatSelect(data.templates);
            } else {
                showFeedback('format', '格式模板数据异常');
            }
        })
        .catch(error => {
            console.error('Error loading format templates:', error);
            showFeedback('format', '加载格式模板失败，请稍后重试');
        });

    // Load style templates
    fetch('/api/writing-style/templates')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success && Array.isArray(data.templates)) {
                updateStyleSelect(data.templates);
            } else {
                showFeedback('style', '文风模板数据异常');
            }
        })
        .catch(error => {
            console.error('Error loading style templates:', error);
            showFeedback('style', '加载文风模板失败，请稍后重试');
        });

    // Load document history
    fetch('/api/documents/history')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success && Array.isArray(data.history)) {
                updateHistoryTable(data.history);
            } else {
                showFeedback('management', '文档历史数据异常');
            }
        })
        .catch(error => {
            console.error('Error loading document history:', error);
            showFeedback('management', '加载文档历史失败，请稍后重试');
        });
}

function updateFormatSelect(templates) {
    const select = document.getElementById('saved-format-select');
    select.innerHTML = '<option value="">-- 选择格式 --</option>';
    templates.forEach(template => {
        const option = document.createElement('option');
        option.value = template.id;
        option.textContent = template.name;
        select.appendChild(option);
    });
}

function updateStyleSelect(templates) {
    const select = document.getElementById('saved-style-select');
    select.innerHTML = '<option value="">-- 选择文风 --</option>';
    templates.forEach(template => {
        const option = document.createElement('option');
        option.value = template.id;
        option.textContent = template.name;
        select.appendChild(option);
    });
}

function updateHistoryTable(history) {
    const tbody = document.querySelector('.history-table tbody');
    tbody.innerHTML = '';
    history.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.type || 'N/A'}</td>
            <td>${record.content || 'N/A'}</td>
            <td>${record.time || 'N/A'}</td>
            <td>${record.status || 'N/A'}</td>
            <td><button class="btn btn-small btn-reapply" data-id="${record.id || ''}">重试</button></td>
        `;
        tbody.appendChild(row);
    });
    setupReapplyButtons();
}

function setupReapplyButtons() {
    const reapplyButtons = document.querySelectorAll('.btn-reapply');
    reapplyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const recordId = this.getAttribute('data-id');
            reapplyOperation(recordId);
        });
    });
}

function reapplyOperation(recordId) {
    fetch(`/api/documents/history/${recordId}/reapply`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('操作已重新应用，新记录ID: ' + data.new_record_id);
            loadInitialData(); // Refresh history
        } else if (data.status === 'file_missing') {
            alert(data.message);
            // Trigger file upload for reapplication
            triggerFileUploadForReapply(recordId);
        } else {
            alert('重新应用操作失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => console.error('Error reapplying operation:', error));
}

function triggerFileUploadForReapply(recordId) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.txt,.docx,.pdf';
    input.onchange = function(event) {
        const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);
            fetch(`/api/documents/history/${recordId}/upload`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    reapplyOperation(recordId); // Retry reapplication after upload
                } else {
                    alert('文件上传失败: ' + (data.error || '未知错误'));
                }
            })
            .catch(error => console.error('Error uploading file for reapply:', error));
        }
    };
    input.click();
}

async function applyFormat() {
    const sessionId = 'current_session'; // 可根据实际逻辑获取
    const dataSources = await collectDataSources();
    fetch('/api/format-alignment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, data_sources: dataSources })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showFeedback('format', '格式统一成功');
        } else {
            showFeedback('format', '格式统一失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        showFeedback('format', '格式统一失败: ' + error.message);
        console.error('Error applying format:', error);
    });
}

function setFormatBaseline() {
    const formatFileElement = document.getElementById('format-file-input');
    if (formatFileElement && formatFileElement.files && formatFileElement.files.length > 0) {
        const formatFile = formatFileElement.files[0];
        const formData = new FormData();
        formData.append('file', formatFile);

        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success) {
                showFeedback('format', '参考格式已设置为: ' + formatFile.name);
            } else {
                showFeedback('format', '设置参考格式失败: ' + (data && data.error ? data.error : '未知错误'));
            }
        })
        .catch(error => {
            showFeedback('format', '设置参考格式失败: ' + error.message);
            console.error('Error setting format baseline:', error);
        });
    } else {
        // 没有文件时的处理逻辑（可选）
    }
}

function saveFormat() {
    const formatNameElement = document.getElementById('save-format-name');
    if (!formatNameElement || !formatNameElement.value) {
        showFeedback('format', '请输入新格式名称');
        return;
    }

    const formatName = formatNameElement.value;
    const formatFileElement = document.getElementById('upload-format-base');
    if (!formatFileElement || formatFileElement.files.length === 0) {
        showFeedback('format', '请上传参考格式文件以保存');
        return;
    }

    const formatFile = formatFileElement.files[0];
    const formData = new FormData();
    formData.append('file', formatFile);
    formData.append('name', formatName);

    fetch('/api/format-templates', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showFeedback('format', '格式已保存: ' + formatName);
            loadInitialData(); // Refresh format templates
        } else {
            showFeedback('format', '保存格式失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        showFeedback('format', '保存格式失败: ' + error.message);
        console.error('Error saving format:', error);
    });
}

function analyzeStyle() {
    const styleFileElement = document.getElementById('upload-style-ref');
    if (!styleFileElement || styleFileElement.files.length === 0) {
        showFeedback('style', '请上传参考文风文档');
        return;
    }

    const styleFile = styleFileElement.files[0];
    const formData = new FormData();
    formData.append('file', styleFile);

    fetch('/api/writing-style/analyze', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success === false || data.error) {
            showFeedback('style', '文风分析失败: ' + (data.error || '未知错误'));
        } else {
            showFeedback('style', '文风分析完成');
        }
    })
    .catch(error => {
        showFeedback('style', '文风分析失败: ' + error.message);
        console.error('Error analyzing style:', error);
    });
}

async function applyStyle() {
    const sessionId = 'current_session';
    const dataSources = await collectDataSources();
    fetch('/api/style-alignment/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, data_sources: dataSources })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success === false || data.error) {
            showFeedback('style', '操作失败: ' + (data.error || '未知错误'));
        } else {
            showFeedback('style', '操作成功');
        }
    })
    .catch(error => {
        showFeedback('style', '操作失败: ' + error.message);
        console.error('Error applying style:', error);
    });
}

function displayStylePreview(previewData, sessionId) {
    const previewBlock = document.querySelector('.result-preview-block');
    const previewArea = previewBlock.querySelector('.document-preview-placeholder');
    previewArea.innerHTML = '';

    // Display original content with highlighted changes
    let content = previewData.original_content || '';
    previewData.suggested_changes.forEach(change => {
        const original = change.original_text || '';
        const suggested = change.suggested_text || '';
        const reason = change.reason || 'No reason provided';
        const changeId = change.id || '';
        content = content.replace(original, `<span class="highlighted-change" data-change-id="${changeId}" title="${reason}">${suggested}</span>`);
    });
    previewArea.innerHTML = content;

    // Setup action buttons for individual changes
    const changes = previewData.suggested_changes || [];
    changes.forEach(change => {
        const changeId = change.id || '';
        const original = change.original_text || '';
        const suggested = change.suggested_text || '';
        const reason = change.reason || 'No reason provided';
        const suggestionItem = document.createElement('div');
        suggestionItem.className = 'suggestion-item';
        suggestionItem.setAttribute('data-issue-id', changeId);
        suggestionItem.innerHTML = `
            <div class="suggestion-header">
                <strong>建议:</strong> ${reason} <span class="suggestion-type">(文风)</span>
                <button class="btn-toggle-details">▼</button>
            </div>
            <div class="suggestion-details">
                <p>原: "${original}" -> 改为: "${suggested}"</p>
                <div class="suggestion-actions">
                    <button class="btn btn-small btn-accept-issue" data-id="${changeId}">接受</button>
                    <button class="btn btn-small btn-reject-issue" data-id="${changeId}">拒绝</button>
                </div>
            </div>
        `;
        previewArea.appendChild(suggestionItem);
    });

    // Store session ID for later use
    previewBlock.setAttribute('data-session-id', sessionId);
    previewBlock.classList.remove('hidden');

    // Setup buttons for individual accept/reject
    setupStyleChangeButtons();
}

function setupStyleChangeButtons() {
    const acceptButtons = document.querySelectorAll('.btn-accept-issue');
    const rejectButtons = document.querySelectorAll('.btn-reject-issue');

    acceptButtons.forEach(button => {
        button.addEventListener('click', function() {
            const changeId = this.getAttribute('data-id');
            const sessionId = document.querySelector('.result-preview-block').getAttribute('data-session-id');
            handleStyleChange(sessionId, changeId, 'accept');
        });
    });

    rejectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const changeId = this.getAttribute('data-id');
            const sessionId = document.querySelector('.result-preview-block').getAttribute('data-session-id');
            handleStyleChange(sessionId, changeId, 'reject');
        });
    });
}

function handleStyleChange(sessionId, changeId, action) {
    if (!sessionId || sessionId === 'null') {
        showFeedback('style', '无效的会话ID，无法处理文风变化');
        return;
    }

    fetch(`/api/style-alignment/changes/${sessionId}/${changeId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: action })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showFeedback('style', `文风变化已${action === 'accept' ? '接受' : '拒绝'}`);
            // Update preview if provided
            if (data.updated_preview) {
                displayStylePreview(data.updated_preview, sessionId);
            }
        } else {
            showFeedback('style', `处理文风变化失败: ${data.error || '未知错误'}`);
        }
    })
    .catch(error => {
        showFeedback('style', `处理文风变化失败: ${error.message}`);
        console.error('Error handling style change:', error);
    });
}

function acceptAllStyleChanges() {
    const previewBlock = document.querySelector('.result-preview-block');
    if (!previewBlock) {
        showFeedback('style', '页面元素未找到，无法处理文风变化');
        return;
    }
    const sessionId = previewBlock.getAttribute('data-session-id');
    if (!sessionId || sessionId === 'null') {
        showFeedback('style', '无效的会话ID，无法处理文风变化');
        return;
    }

    fetch(`/api/style-alignment/changes/${sessionId}/batch`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: 'accept_all' })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showFeedback('style', '所有文风变化已接受');
        } else {
            showFeedback('style', '接受所有文风变化失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        showFeedback('style', '接受所有文风变化失败: ' + error.message);
        console.error('Error accepting all style changes:', error);
    });
}

function rejectAllStyleChanges() {
    const previewBlock = document.querySelector('.result-preview-block');
    if (!previewBlock) {
        showFeedback('style', '页面元素未找到，无法处理文风变化');
        return;
    }
    const sessionId = previewBlock.getAttribute('data-session-id');
    if (!sessionId || sessionId === 'null') {
        showFeedback('style', '无效的会话ID，无法处理文风变化');
        return;
    }

    fetch(`/api/style-alignment/changes/${sessionId}/batch`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: 'reject_all' })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showFeedback('style', '所有文风变化已拒绝');
        } else {
            showFeedback('style', '拒绝所有文风变化失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        showFeedback('style', '拒绝所有文风变化失败: ' + error.message);
        console.error('Error rejecting all style changes:', error);
    });
}

function exportStyledDocument() {
    const previewBlock = document.querySelector('.result-preview-block');
    if (!previewBlock) {
        showFeedback('style', '页面元素未找到，无法导出文档');
        return;
    }
    const sessionId = previewBlock.getAttribute('data-session-id');
    if (!sessionId || sessionId === 'null') {
        showFeedback('style', '无效的会话ID，无法导出文档');
        return;
    }
    window.location.href = `/api/style-alignment/export/${sessionId}`;
}

function saveStyle() {
    const styleNameElement = document.getElementById('save-style-name');
    if (!styleNameElement || !styleNameElement.value) {
        showFeedback('style', '请输入新文风名称');
        return;
    }

    const styleName = styleNameElement.value;
    const styleFileElement = document.getElementById('upload-style-ref');
    if (!styleFileElement || styleFileElement.files.length === 0) {
        showFeedback('style', '请上传参考文风文件以保存');
        return;
    }

    const styleFile = styleFileElement.files[0];
    const formData = new FormData();
    formData.append('file', styleFile);
    formData.append('name', styleName);

    fetch('/api/writing-style/save-template', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showFeedback('style', '文风已保存: ' + styleName);
            loadInitialData(); // Refresh style templates
        } else {
            showFeedback('style', '保存文风失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        showFeedback('style', '保存文风失败: ' + error.message);
        console.error('Error saving style:', error);
    });
}

async function collectDataSources() {
    const dataSources = [];
    // 1. 文本数据（主文本域）
    const textDataElement = document.getElementById('fill-text-data');
    const textData = textDataElement ? textDataElement.value.trim() : '';
    if (textData) {
        dataSources.push({ type: 'text', name: 'fill-text-data', content: textData });
    }
    // 2. 所有 input.input-text, textarea.input-textarea
    document.querySelectorAll('.input-text, .input-textarea').forEach(el => {
        if (el.value && el.value.trim()) {
            dataSources.push({ type: 'text', name: el.id || el.name || '', content: el.value.trim() });
        }
    });
    // 3. 用户在预览区填写的字段（如 .field-input）
    document.querySelectorAll('.field-input').forEach(el => {
        if (el.value && el.value.trim()) {
            dataSources.push({ type: 'text', name: el.getAttribute('data-field') || el.id || '', content: el.value.trim() });
        }
    });
    // 4. AI生成内容（如 .field-value）
    document.querySelectorAll('.field-value').forEach(el => {
        if (el.textContent && el.textContent.trim()) {
            dataSources.push({ type: 'ai_suggestion', name: el.getAttribute('data-field') || '', content: el.textContent.trim() });
        }
    });
    // 5. 图片文件（image/*）
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    for (const input of imageInputs) {
        if (input.files && input.files.length > 0) {
            for (const file of input.files) {
                const base64 = await fileToBase64(file);
                dataSources.push({
                    type: 'file',
                    name: file.name,
                    content: base64,
                    mime: file.type
                });
            }
        }
    }
    return dataSources;
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// autoMatchData 需 await collectDataSources
async function autoMatchData() {
    const sessionId = 'current_session'; // TODO: 替换为实际 session id 获取逻辑
    const dataSources = await collectDataSources();
    fetch('/api/document-fill/auto-match', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: sessionId,
            data_sources: dataSources
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showFeedback('fill', '数据自动匹配成功');
            displayFillPreview(data.matched_fields, data.unmatched_fields, data.conflicts, data.confidence_scores);
        } else {
            showFeedback('fill', '数据自动匹配失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        showFeedback('fill', '数据自动匹配失败: ' + error.message);
        console.error('Error auto-matching data:', error);
    });
}

function displayFillPreview(matchedFields, unmatchedFields, conflicts, confidenceScores) {
    const previewArea = document.querySelector('.fill-preview');
    previewArea.innerHTML = '';

    // Display matched fields
    for (const [fieldId, value] of Object.entries(matchedFields)) {
        const confidence = confidenceScores[fieldId] || 0;
        const fieldElement = document.createElement('p');
        fieldElement.innerHTML = `${fieldId}: <span class="field-value matched" data-field="${fieldId}" title="Confidence: ${confidence.toFixed(2)}">${value}</span>`;
        previewArea.appendChild(fieldElement);
    }

    // Display unmatched fields
    unmatchedFields.forEach(fieldId => {
        const fieldElement = document.createElement('p');
        fieldElement.innerHTML = `${fieldId}: <input type="text" class="field-input" placeholder="待填写" data-field="${fieldId}">`;
        previewArea.appendChild(fieldElement);
    });

    // Display conflicts for user resolution
    conflicts.forEach(conflict => {
        const fieldId = conflict.field_id;
        const options = conflict.options;
        const conflictElement = document.createElement('p');
        let optionsHtml = options.map(opt => `<option value="${opt.value}" title="Confidence: ${opt.confidence.toFixed(2)}">${opt.value} (from ${opt.source})</option>`).join('');
        conflictElement.innerHTML = `${fieldId}: <select class="field-select" data-field="${fieldId}"><option value="">-- 选择值 --</option>${optionsHtml}</select>`;
        previewArea.appendChild(conflictElement);
    });

    // Update progress info
    const totalFields = Object.keys(matchedFields).length + unmatchedFields.length + conflicts.length;
    const filledFields = Object.keys(matchedFields).length;
    document.querySelector('.fill-progress-info').textContent = `已填报 ${filledFields}/${totalFields} 个字段`;
}

function exportFilledDocument() {
    fetch('/api/document-fill/download', {
        method: 'GET'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'filled_document.html';
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        showFeedback('fill', '导出填充文档失败: ' + error.message);
        console.error('Error exporting filled document:', error);
    });
}

async function startReview() {
    const sessionId = 'current_session';
    const dataSources = await collectDataSources();
    fetch('/api/document-review/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, data_sources: dataSources })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showFeedback('review', '文档审阅已启动');
            pollReviewSuggestions(data.review_session_id);
        } else {
            showFeedback('review', '启动文档审阅失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        showFeedback('review', '启动文档审阅失败: ' + error.message);
        console.error('Error starting review:', error);
    });
}

function pollReviewSuggestions(sessionId) {
    if (!sessionId || sessionId === 'null') {
        showFeedback('review', '无效的会话ID，无法获取审阅建议');
        return;
    }

    const interval = setInterval(() => {
        fetch(`/api/document-review/suggestions/${sessionId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success && data.suggestions.length > 0) {
                clearInterval(interval);
                displayReviewSuggestions(data.suggestions, sessionId);
            }
        })
        .catch(error => {
            console.error('Error polling review suggestions:', error);
            showFeedback('review', '获取审阅建议失败: ' + error.message);
            clearInterval(interval);
        });
    }, 3000);
}

function displayReviewSuggestions(suggestions, sessionId) {
    const reviewBlock = document.querySelector('.review-results-block');
    const previewArea = reviewBlock.querySelector('.review-preview');
    const sidebar = reviewBlock.querySelector('.sidebar-suggestions');
    previewArea.innerHTML = '';
    sidebar.innerHTML = '<h4 class="sidebar-title">审阅建议</h4>';

    // Display document content with issue markers
    let content = suggestions[0].original_content || '';
    suggestions.forEach(suggestion => {
        const original = suggestion.original_text || '';
        const issueId = suggestion.suggestion_id || '';
        const reason = suggestion.reason || 'No reason provided';
        content = content.replace(original, `<p class="issue-marker" data-issue-id="${issueId}" title="${reason}">${original}</p>`);
    });
    previewArea.innerHTML = content;

    // Display suggestions in sidebar
    suggestions.forEach(suggestion => {
        const issueId = suggestion.suggestion_id || '';
        const original = suggestion.original_text || '';
        const suggested = suggestion.suggested_text || '';
        const reason = suggestion.reason || 'No reason provided';
        const type = suggestion.type || 'N/A';
        const suggestionItem = document.createElement('div');
        suggestionItem.className = 'suggestion-item';
        suggestionItem.setAttribute('data-issue-id', issueId);
        suggestionItem.innerHTML = `
            <div class="suggestion-header">
                <strong>建议:</strong> ${reason} <span class="suggestion-type">(${type})</span>
                <button class="btn-toggle-details">▼</button>
            </div>
            <div class="suggestion-details">
                <p>原: "${original}" -> 改为: "${suggested}"</p>
                <div class="suggestion-actions">
                    <button class="btn btn-small btn-accept-issue" data-id="${issueId}">接受</button>
                    <button class="btn btn-small btn-reject-issue" data-id="${issueId}">拒绝</button>
                </div>
            </div>
        `;
        sidebar.appendChild(suggestionItem);
    });

    // Store session ID for later use
    reviewBlock.setAttribute('data-session-id', sessionId);
    reviewBlock.classList.remove('hidden');

    // Setup buttons for individual accept/reject
    setupReviewSuggestionButtons();
}

function setupReviewSuggestionButtons() {
    const acceptButtons = document.querySelectorAll('.btn-accept-issue');
    const rejectButtons = document.querySelectorAll('.btn-reject-issue');

    acceptButtons.forEach(button => {
        button.addEventListener('click', function() {
            const suggestionId = this.getAttribute('data-id');
            const sessionId = document.querySelector('.review-results-block').getAttribute('data-session-id');
            handleReviewSuggestion(sessionId, suggestionId, 'accept');
        });
    });

    rejectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const suggestionId = this.getAttribute('data-id');
            const sessionId = document.querySelector('.review-results-block').getAttribute('data-session-id');
            handleReviewSuggestion(sessionId, suggestionId, 'reject');
        });
    });
}

function handleReviewSuggestion(sessionId, suggestionId, action) {
    if (!sessionId || sessionId === 'null') {
        showFeedback('review', '无效的会话ID，无法处理审阅建议');
        return;
    }

    fetch(`/api/document-review/suggestions/${sessionId}/${suggestionId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: action })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showFeedback('review', `审阅建议已${action === 'accept' ? '接受' : '拒绝'}`);
        } else {
            showFeedback('review', `处理审阅建议失败: ${data.error || '未知错误'}`);
        }
    })
    .catch(error => {
        showFeedback('review', `处理审阅建议失败: ${error.message}`);
        console.error('Error handling review suggestion:', error);
    });
}

function acceptAllIssues() {
    const reviewBlock = document.querySelector('.review-results-block');
    if (!reviewBlock) {
        showFeedback('review', '页面元素未找到，无法处理审阅建议');
        return;
    }
    const sessionId = reviewBlock.getAttribute('data-session-id');
    if (!sessionId || sessionId === 'null') {
        showFeedback('review', '无效的会话ID，无法处理审阅建议');
        return;
    }

    fetch(`/api/document-review/suggestions/${sessionId}/batch`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: 'accept_all' })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showFeedback('review', '所有审阅建议已接受');
        } else {
            showFeedback('review', '接受所有审阅建议失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        showFeedback('review', '接受所有审阅建议失败: ' + error.message);
        console.error('Error accepting all issues:', error);
    });
}

function rejectAllIssues() {
    const reviewBlock = document.querySelector('.review-results-block');
    if (!reviewBlock) {
        showFeedback('review', '页面元素未找到，无法处理审阅建议');
        return;
    }
    const sessionId = reviewBlock.getAttribute('data-session-id');
    if (!sessionId || sessionId === 'null') {
        showFeedback('review', '无效的会话ID，无法处理审阅建议');
        return;
    }

    fetch(`/api/document-review/suggestions/${sessionId}/batch`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: 'reject_all' })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showFeedback('review', '所有审阅建议已拒绝');
        } else {
            showFeedback('review', '拒绝所有审阅建议失败: ' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        showFeedback('review', '拒绝所有审阅建议失败: ' + error.message);
        console.error('Error rejecting all issues:', error);
    });
}

function exportReviewedDocument() {
    const reviewBlock = document.querySelector('.review-results-block');
    if (!reviewBlock) {
        showFeedback('review', '页面元素未找到，无法导出文档');
        return;
    }
    const sessionId = reviewBlock.getAttribute('data-session-id');
    if (!sessionId || sessionId === 'null') {
        showFeedback('review', '无效的会话ID，无法导出文档');
        return;
    }
    fetch(`/api/document-review/export/${sessionId}`, {
        method: 'GET'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'reviewed_document.docx';
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        showFeedback('review', '导出审阅文档失败: ' + error.message);
        console.error('Error exporting reviewed document:', error);
    });
}

function showFeedback(scene, message) {
    const feedbackElement = document.querySelector(`#scene-${scene} .feedback-message`);
    if (feedbackElement) {
        feedbackElement.textContent = message;
        feedbackElement.style.display = 'block';
        setTimeout(() => {
            feedbackElement.style.display = 'none';
        }, 3000);
    }
}

// 智能文档分析
async function enhancedDocumentAnalysis() {
    try {
        const documentContent = document.getElementById('document-content').value;
        const documentName = document.getElementById('document-name').value || '智能文档';
        
        if (!documentContent.trim()) {
            showMessage('请先输入文档内容', 'error');
            return;
        }
        
        showLoading('正在分析文档结构...');
        
        const response = await fetch('/api/enhanced-document/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                document_content: documentContent,
                document_name: documentName
            })
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.error) {
            showMessage(result.error, 'error');
            return;
        }
        
        // 显示分析结果
        displayEnhancedAnalysisResult(result);
        
    } catch (error) {
        hideLoading();
        showMessage(`文档分析失败: ${error.message}`, 'error');
    }
}

// 显示增强的分析结果
function displayEnhancedAnalysisResult(analysisResult) {
    const resultContainer = document.getElementById('analysis-result');
    if (!resultContainer) return;
    
    const documentType = analysisResult.document_type || 'general';
    const confidence = (analysisResult.confidence_score * 100).toFixed(1);
    const fieldCount = analysisResult.fields?.length || 0;
    const imageCount = analysisResult.image_count || 0;
    const detectedIntent = analysisResult.detected_intent || documentType;
    const recommendedAction = analysisResult.recommended_action || '';
    const intentOptions = [
        { value: 'empty_form', label: '空白表格/模板' },
        { value: 'complete_good', label: '内容完整优质' },
        { value: 'messy_format', label: '格式混乱' },
        { value: 'incomplete', label: '内容不完整' },
        { value: 'aigc_heavy', label: 'AIGC痕迹明显' },
        { value: 'general', label: '普通文档' }
    ];
    const intentLabels = {
        'empty_form': '检测到这是空白表格/模板，是否进入智能填报？',
        'complete_good': '检测到这是内容完整优质的文档，可作为参考模板。',
        'messy_format': '检测到文档格式较为混乱，建议进行格式整理。',
        'incomplete': '检测到文档内容不完整，建议补全内容。',
        'aigc_heavy': '检测到存在明显AIGC痕迹，建议进行风格改写。',
        'general': '检测到为普通文档，可继续后续操作。'
    };
    let html = `
        <div class="analysis-summary">
            <h3>📋 文档分析结果</h3>
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="label">文档类型:</span>
                    <span class="value">${getDocumentTypeName(documentType)}</span>
                </div>
                <div class="summary-item">
                    <span class="label">识别置信度:</span>
                    <span class="value">${confidence}%</span>
                </div>
                <div class="summary-item">
                    <span class="label">识别字段数:</span>
                    <span class="value">${fieldCount}</span>
                </div>
                <div class="summary-item">
                    <span class="label">图片位置数:</span>
                    <span class="value">${imageCount}</span>
                </div>
            </div>
        </div>
    `;
    
    // 文档目标信息
    if (analysisResult.total_objective) {
        html += `
            <div class="document-objective">
                <h4>🎯 文档目标</h4>
                <p>${analysisResult.total_objective}</p>
            </div>
        `;
    }
    
    // 核心主题
    if (analysisResult.core_theme) {
        html += `
            <div class="core-theme">
                <h4>💡 核心主题</h4>
                <p>${analysisResult.core_theme}</p>
            </div>
        `;
    }
    
    // 字段列表
    if (analysisResult.fields && analysisResult.fields.length > 0) {
        html += `
            <div class="fields-section">
                <h4>📝 识别字段</h4>
                <div class="fields-grid">
        `;
        
        analysisResult.fields.forEach(field => {
            const fieldType = getFieldTypeName(field.field_type);
            const section = getSectionName(field.section);
            
            html += `
                <div class="field-item">
                    <div class="field-header">
                        <span class="field-name">${field.field_name}</span>
                        <span class="field-type">${fieldType}</span>
                    </div>
                    <div class="field-details">
                        <span class="field-section">区块: ${section}</span>
                        <span class="field-line">行号: ${field.line_number}</span>
                    </div>
                    <div class="field-constraints">
                        ${generateConstraintsHTML(field.constraints)}
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    // 图片位置信息
    if (analysisResult.image_positions && analysisResult.image_positions.length > 0) {
        html += `
            <div class="images-section">
                <h4>🖼️ 图片位置</h4>
                <div class="images-grid">
        `;
        
        analysisResult.image_positions.forEach((img, index) => {
            html += `
                <div class="image-item">
                    <div class="image-header">
                        <span class="image-id">图片${index + 1}</span>
                        <span class="image-line">行号: ${img.line_number}</span>
                    </div>
                    <div class="image-details">
                        <span class="image-placeholder">${img.placeholder_text}</span>
                        <span class="image-description">${img.description}</span>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    // AI填写建议
    if (analysisResult.ai_suggestions) {
        html += `
            <div class="ai-suggestions">
                <h4>🤖 AI填写建议</h4>
                <div class="suggestions-content">
                    <p><strong>文档目标:</strong> ${analysisResult.ai_suggestions.document_objective}</p>
                    <p><strong>核心主题:</strong> ${analysisResult.ai_suggestions.core_theme}</p>
                </div>
            </div>
        `;
    }
    
    // 智能填充按钮
    html += `
        <div class="action-buttons">
            <button onclick="startIntelligentFill()" class="btn btn-primary">
                🚀 开始智能填充
            </button>
            <button onclick="getAIFillSuggestions()" class="btn btn-secondary">
                💡 获取AI建议
            </button>
        </div>
    `;
    
    resultContainer.innerHTML = html;
    resultContainer.style.display = 'block';
    
    // 保存分析结果到全局变量
    window.currentAnalysisResult = analysisResult;

    // === 新增：弹出意图判定结果模态框 ===
    showIntentModal({
        detectedIntent,
        confidence,
        recommendedAction,
        intentOptions,
        intentLabels,
        onIntentChange: (newIntent) => {
            // 更新推荐操作和引导文案
            const newAction = getRecommendedActionByIntent(newIntent);
            updateIntentModal(newIntent, newAction, intentLabels[newIntent]);
        }
    });

    // 新增反馈区
    let feedbackHtml = `
      <div style="margin-top:16px;">
        <label>判定是否准确：</label>
        <select id="intent-feedback-select">
          <option value="accurate">准确</option>
          <option value="inaccurate">不准确</option>
        </select>
        <span id="intent-correct-select-area" style="display:none;">
          <label style="margin-left:8px;">纠正为：</label>
          <select id="intent-correct-select">
            <option value="contract_template">合同模板</option>
            <option value="paper_draft">论文草稿</option>
            <option value="aigc_incomplete">AIGC+内容不全</option>
            <option value="empty_form">空白表格/模板</option>
            <option value="complete_good">内容完整优质</option>
            <option value="messy_format">格式混乱</option>
            <option value="content_incomplete">内容不完整</option>
            <option value="aigc_heavy">AIGC痕迹明显</option>
          </select>
        </span>
        <button id="submit-intent-feedback" style="margin-left:12px;">提交反馈</button>
      </div>
    `;
    document.getElementById('modal-content').innerHTML += feedbackHtml;
    // 交互逻辑
    document.getElementById('intent-feedback-select').addEventListener('change', function() {
      if (this.value === 'inaccurate') {
        document.getElementById('intent-correct-select-area').style.display = '';
      } else {
        document.getElementById('intent-correct-select-area').style.display = 'none';
      }
    });
    document.getElementById('submit-intent-feedback').addEventListener('click', function() {
      const feedback = document.getElementById('intent-feedback-select').value;
      const corrected = feedback === 'inaccurate' ? document.getElementById('intent-correct-select').value : null;
      const payload = {
        document_name: analysisResult.analysis_metadata?.document_name || '',
        original_intent: analysisResult.detected_intent || analysisResult.document_type,
        user_feedback: feedback,
        corrected_intent: corrected,
        feedback_time: new Date().toISOString()
      };
      fetch('/api/intent-feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).then(r => r.json()).then(res => {
        alert(res.message || '反馈已提交');
      });
    });
}

// 智能填充文档
async function startIntelligentFill() {
    try {
        if (!window.currentAnalysisResult) {
            showMessage('请先进行文档分析', 'error');
            return;
        }
        
        // 显示文思泉涌的友好提示
        showAIThinkingMessage();
        
        // 收集用户数据
        const userData = collectUserData();
        
        // 收集图片文件
        const imageFiles = collectImageFiles();
        
        const response = await fetch('/api/enhanced-document/fill', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                analysis_result: window.currentAnalysisResult,
                user_data: userData,
                image_files: imageFiles
            })
        });
        
        const result = await response.json();
        hideAIThinkingMessage();
        
        if (result.error) {
            showMessage(result.error, 'error');
            return;
        }
        
        // 显示填充结果
        displayFillResult(result);
        
    } catch (error) {
        hideAIThinkingMessage();
        showMessage(`智能填充失败: ${error.message}`, 'error');
    }
}

// 显示AI思考中的友好提示
function showAIThinkingMessage() {
    // 创建或获取AI思考提示容器
    let aiThinkingContainer = document.getElementById('ai-thinking-container');
    if (!aiThinkingContainer) {
        aiThinkingContainer = document.createElement('div');
        aiThinkingContainer.id = 'ai-thinking-container';
        aiThinkingContainer.className = 'ai-thinking-overlay';
        document.body.appendChild(aiThinkingContainer);
    }
    
    // 生成随机的文思泉涌提示语
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
    
    // 启动进度条动画
    startProgressAnimation();
    
    // 启动消息轮换
    startMessageRotation(aiThinkingContainer, thinkingMessages);
}

// 隐藏AI思考提示
function hideAIThinkingMessage() {
    const aiThinkingContainer = document.getElementById('ai-thinking-container');
    if (aiThinkingContainer) {
        aiThinkingContainer.style.display = 'none';
    }
}

// 启动进度条动画
function startProgressAnimation() {
    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
        progressFill.style.width = '0%';
        progressFill.style.transition = 'width 0.5s ease-in-out';
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15 + 5; // 随机进度增长
            if (progress >= 90) {
                progress = 90; // 最多到90%，等待实际完成
                clearInterval(interval);
            }
            progressFill.style.width = progress + '%';
        }, 800);
    }
}

// 启动消息轮换
function startMessageRotation(container, messages) {
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
    
    // 保存interval ID以便清理
    container.dataset.messageInterval = interval;
}

// 获取AI填写建议
async function getAIFillSuggestions() {
    try {
        if (!window.currentAnalysisResult) {
            showMessage('请先进行文档分析', 'error');
            return;
        }
        
        // 显示AI思考提示
        showAIThinkingMessage();
        
        const response = await fetch('/api/ai-fill-suggestions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                analysis_result: window.currentAnalysisResult
            })
        });
        
        const result = await response.json();
        hideAIThinkingMessage();
        
        if (result.error) {
            showMessage(result.error, 'error');
            return;
        }
        
        // 显示AI建议
        displayAISuggestions(result);
        
    } catch (error) {
        hideAIThinkingMessage();
        showMessage(`获取AI建议失败: ${error.message}`, 'error');
    }
}

// 显示AI建议
function displayAISuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('ai-suggestions');
    if (!suggestionsContainer) return;
    
    let html = `
        <div class="ai-suggestions-panel">
            <h3>🤖 AI填写建议</h3>
            <div class="suggestions-content">
    `;
    
    if (suggestions.field_suggestions) {
        html += `<h4>字段填写建议:</h4>`;
        Object.entries(suggestions.field_suggestions).forEach(([fieldId, suggestion]) => {
            html += `
                <div class="suggestion-item">
                    <strong>${fieldId}:</strong>
                    <p>${suggestion}</p>
                </div>
            `;
        });
    }
    
    if (suggestions.consistency_checks) {
        html += `<h4>一致性检查:</h4>`;
        suggestions.consistency_checks.forEach(check => {
            html += `<p>• ${check}</p>`;
        });
    }
    
    html += `
            </div>
        </div>
    `;
    
    suggestionsContainer.innerHTML = html;
    suggestionsContainer.style.display = 'block';
}

// 显示填充结果
function displayFillResult(fillResult) {
    const resultContainer = document.getElementById('fill-result');
    if (!resultContainer) return;
    
    let html = `
        <div class="fill-result-panel">
            <h3>✅ 文档填充完成</h3>
    `;
    
    // 质量评估
    if (fillResult.quality_assessment) {
        const quality = fillResult.quality_assessment;
        html += `
            <div class="quality-assessment">
                <h4>📊 质量评估</h4>
                <div class="quality-grid">
                    <div class="quality-item">
                        <span class="label">总体评分:</span>
                        <span class="value">${quality.overall_score.toFixed(1)}/100</span>
                    </div>
                    <div class="quality-item">
                        <span class="label">完成度:</span>
                        <span class="value">${quality.completion_rate.toFixed(1)}%</span>
                    </div>
                    <div class="quality-item">
                        <span class="label">类型匹配度:</span>
                        <span class="value">${quality.type_match_rate.toFixed(1)}%</span>
                    </div>
                    <div class="quality-item">
                        <span class="label">约束满足度:</span>
                        <span class="value">${quality.constraint_satisfaction_rate.toFixed(1)}%</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    // 填充内容预览
    if (fillResult.filled_content) {
        html += `
            <div class="content-preview">
                <h4>📄 填充内容预览</h4>
                <div class="preview-content">
                    <pre>${fillResult.filled_content}</pre>
                </div>
            </div>
        `;
    }
    
    // 操作按钮
    html += `
        <div class="action-buttons">
            <button onclick="downloadFilledDocument()" class="btn btn-success">
                📥 下载文档
            </button>
            <button onclick="previewHTMLDocument()" class="btn btn-info">
                👁️ 预览HTML
            </button>
        </div>
    `;
    
    html += `</div>`;
    
    resultContainer.innerHTML = html;
    resultContainer.style.display = 'block';
    
    // 保存填充结果
    window.currentFillResult = fillResult;
}

// 收集用户数据
function collectUserData() {
    const userData = {};
    
    // 收集表单字段
    const formFields = document.querySelectorAll('input[type="text"], input[type="email"], textarea, select');
    formFields.forEach(field => {
        if (field.value.trim()) {
            userData[field.name || field.id] = field.value.trim();
        }
    });
    
    // 收集预览区域的用户填写内容
    const previewFields = document.querySelectorAll('.preview-field');
    previewFields.forEach(field => {
        const fieldId = field.getAttribute('data-field-id');
        const fieldValue = field.textContent.trim();
        if (fieldValue && fieldId) {
            userData[fieldId] = fieldValue;
        }
    });
    
    return userData;
}

// 收集图片文件
function collectImageFiles() {
    const imageFiles = [];
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        if (input.files && input.files.length > 0) {
            Array.from(input.files).forEach(file => {
                if (file.type.startsWith('image/')) {
                    // 这里需要将文件转换为base64
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        imageFiles.push({
                            name: file.name,
                            data: e.target.result,
                            type: file.type,
                            size: file.size
                        });
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    });
    
    return imageFiles;
}

// 下载填充后的文档
function downloadFilledDocument() {
    if (!window.currentFillResult) {
        showMessage('没有可下载的文档', 'error');
        return;
    }
    
    const result = window.currentFillResult;
    
    if (result.html_content) {
        // 下载HTML文档
        const blob = new Blob([result.html_content], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'filled_document.html';
        a.click();
        URL.revokeObjectURL(url);
    } else if (result.filled_content) {
        // 下载文本文档
        const blob = new Blob([result.filled_content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'filled_document.txt';
        a.click();
        URL.revokeObjectURL(url);
    }
}

// 预览HTML文档
function previewHTMLDocument() {
    if (!window.currentFillResult || !window.currentFillResult.html_content) {
        showMessage('没有HTML预览内容', 'error');
        return;
    }
    
    const htmlContent = window.currentFillResult.html_content;
    const newWindow = window.open('', '_blank');
    newWindow.document.write(htmlContent);
    newWindow.document.close();
}

// 获取文档类型名称
function getDocumentTypeName(documentType) {
    const typeNames = {
        'patent': '专利文档',
        'project': '项目文档',
        'contract': '合同文档',
        'report': '报告文档',
        'general': '通用文档',
        'style_preview': '文风预览',
        'style_export': '文风导出',
        'review_export': '评审导出'
    };
    
    return typeNames[documentType] || '未知类型';
}

function getFieldTypeName(type) {
    const typeNames = {
        'text': '文本',
        'textarea': '多行文本',
        'select': '下拉选择',
        'date': '日期',
        'number': '数字',
        'image': '图片',
        'table': '表格',
        'signature': '签名',
        'checkbox': '复选框',
        'radio': '单选按钮'
    };
    return typeNames[type] || type;
}

function getSectionName(section) {
    const sectionNames = {
        'header': '文档头部',
        'basic_info': '基本信息',
        'inventor_info': '发明人信息',
        'abstract': '摘要',
        'background': '背景技术',
        'summary': '发明内容',
        'drawings': '附图说明',
        'claims': '权利要求',
        'description': '具体实施方式',
        'appendix': '附录'
    };
    return sectionNames[section] || section;
}

function generateConstraintsHTML(constraints) {
    if (!constraints) return '';
    
    let html = '<div class="constraints">';
    
    if (constraints.required) {
        html += '<span class="constraint required">必填</span>';
    }
    
    if (constraints.min_length) {
        html += `<span class="constraint">最小长度: ${constraints.min_length}</span>`;
    }
    
    if (constraints.max_length) {
        html += `<span class="constraint">最大长度: ${constraints.max_length}</span>`;
    }
    
    if (constraints.options) {
        html += `<span class="constraint">选项: ${constraints.options.join(', ')}</span>`;
    }
    
    html += '</div>';
    return html;
}

// 图片处理功能
async function processImage(imageData, imageName, targetPosition) {
    try {
        const response = await fetch('/api/image/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image_data: imageData,
                image_name: imageName,
                target_position: targetPosition
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            showMessage(result.error, 'error');
            return null;
        }
        
        return result;
        
    } catch (error) {
        showMessage(`图片处理失败: ${error.message}`, 'error');
        return null;
    }
}

// 批量处理图片
async function batchProcessImages(imageList, documentContent) {
    try {
        const response = await fetch('/api/image/batch-process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image_list: imageList,
                document_content: documentContent
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            showMessage(result.error, 'error');
            return null;
        }
        
        return result;
        
    } catch (error) {
        showMessage(`批量图片处理失败: ${error.message}`, 'error');
        return null;
    }
}

// 获取图片统计信息
async function getImageStatistics() {
    try {
        const response = await fetch('/api/image/statistics');
        const result = await response.json();
        
        if (result.error) {
            showMessage(result.error, 'error');
            return null;
        }
        
        return result;
        
    } catch (error) {
        showMessage(`获取统计信息失败: ${error.message}`, 'error');
        return null;
    }
}

// 生成SVG图像
async function generateSVGImage(documentType, contentDescription, svgSize = [400, 300]) {
    try {
        const response = await fetch('/api/svg/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                document_type: documentType,
                content_description: contentDescription,
                svg_size: svgSize
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            showMessage(result.error, 'error');
            return null;
        }
        
        return result;
        
    } catch (error) {
        showMessage(`SVG生成失败: ${error.message}`, 'error');
        return null;
    }
}

// 将SVG插入到文档
async function insertSVGToDocument(documentContent, svgInfo, targetPosition, mode = 'preview') {
    try {
        const response = await fetch('/api/svg/insert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                document_content: documentContent,
                svg_info: svgInfo,
                target_position: targetPosition,
                mode: mode
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            showMessage(result.error, 'error');
            return documentContent;
        }
        
        return result.updated_content;
        
    } catch (error) {
        showMessage(`SVG插入失败: ${error.message}`, 'error');
        return documentContent;
    }
}

// 预览时生成并插入SVG
async function previewWithSVG(documentContent, documentType = 'general') {
    try {
        showLoading('正在生成预览SVG...');
        
        // 生成SVG
        const svgResult = await generateSVGImage(
            documentType,
            '文档预览示意图',
            [400, 300]
        );
        
        if (!svgResult) {
            hideLoading();
            return documentContent;
        }
        
        // 插入SVG到文档（预览模式）
        const targetPosition = {
            line_number: 1,
            document_type: documentType,
            suggested_size: [400, 300]
        };
        
        const updatedContent = await insertSVGToDocument(
            documentContent,
            svgResult,
            targetPosition,
            'preview'
        );
        
        hideLoading();
        return updatedContent;
        
    } catch (error) {
        hideLoading();
        showMessage(`预览SVG生成失败: ${error.message}`, 'error');
        return documentContent;
    }
}

// 导出时生成并插入SVG
async function exportWithSVG(documentContent, documentType = 'general') {
    try {
        showLoading('正在生成导出SVG...');
        
        // 生成SVG
        const svgResult = await generateSVGImage(
            documentType,
            '文档导出示意图',
            [400, 300]
        );
        
        if (!svgResult) {
            hideLoading();
            return documentContent;
        }
        
        // 插入SVG到文档（下载模式）
        const targetPosition = {
            line_number: 1,
            document_type: documentType,
            suggested_size: [400, 300]
        };
        
        const updatedContent = await insertSVGToDocument(
            documentContent,
            svgResult,
            targetPosition,
            'download'
        );
        
        hideLoading();
        return updatedContent;
        
    } catch (error) {
        hideLoading();
        showMessage(`导出SVG生成失败: ${error.message}`, 'error');
        return documentContent;
    }
}

// 增强的预览功能（集成SVG）
async function enhancedPreview() {
    try {
        const documentContent = document.getElementById('document-content').value;
        const documentName = document.getElementById('document-name').value || '智能文档';
        
        if (!documentContent.trim()) {
            showMessage('请先输入文档内容', 'error');
            return;
        }
        
        showLoading('正在生成增强预览...');
        
        // 1. 分析文档类型
        const documentType = getDocumentTypeFromContent(documentContent, documentName);
        
        // 2. 生成带SVG的预览内容
        const previewContent = await previewWithSVG(documentContent, documentType);
        
        // 3. 显示预览
        displayEnhancedPreview(previewContent, documentType);
        
        hideLoading();
        
    } catch (error) {
        hideLoading();
        showMessage(`增强预览失败: ${error.message}`, 'error');
    }
}

// 增强的导出功能（集成SVG）
async function enhancedExport() {
    try {
        const documentContent = document.getElementById('document-content').value;
        const documentName = document.getElementById('document-name').value || '智能文档';
        
        if (!documentContent.trim()) {
            showMessage('请先输入文档内容', 'error');
            return;
        }
        
        showLoading('正在生成增强导出...');
        
        // 1. 分析文档类型
        const documentType = getDocumentTypeFromContent(documentContent, documentName);
        
        // 2. 生成带SVG的导出内容
        const exportContent = await exportWithSVG(documentContent, documentType);
        
        // 3. 下载文档
        downloadDocument(exportContent, documentName, documentType);
        
        hideLoading();
        
    } catch (error) {
        hideLoading();
        showMessage(`增强导出失败: ${error.message}`, 'error');
    }
}

// 显示增强预览
function displayEnhancedPreview(content, documentType) {
    const previewContainer = document.getElementById('preview-container');
    if (!previewContainer) return;
    
    const documentTypeName = getDocumentTypeName(documentType);
    
    let html = `
        <div class="enhanced-preview">
            <h3>🎨 增强预览 - ${documentTypeName}</h3>
            <div class="preview-content">
                ${content}
            </div>
            <div class="preview-actions">
                <button onclick="enhancedExport()" class="btn btn-success">
                    📥 导出文档
                </button>
                <button onclick="regenerateSVG()" class="btn btn-secondary">
                    🔄 重新生成SVG
                </button>
            </div>
        </div>
    `;
    
    previewContainer.innerHTML = html;
    previewContainer.style.display = 'block';
}

// 重新生成SVG
async function regenerateSVG() {
    try {
        const documentContent = document.getElementById('document-content').value;
        const documentType = getDocumentTypeFromContent(documentContent);
        
        showLoading('正在重新生成SVG...');
        
        // 生成新的SVG
        const svgResult = await generateSVGImage(
            documentType,
            '重新生成的文档示意图',
            [400, 300]
        );
        
        if (svgResult) {
            // 更新预览
            const targetPosition = {
                line_number: 1,
                document_type: documentType,
                suggested_size: [400, 300]
            };
            
            const updatedContent = await insertSVGToDocument(
                documentContent,
                svgResult,
                targetPosition,
                'preview'
            );
            
            displayEnhancedPreview(updatedContent, documentType);
        }
        
        hideLoading();
        
    } catch (error) {
        hideLoading();
        showMessage(`重新生成SVG失败: ${error.message}`, 'error');
    }
}

// 下载文档
function downloadDocument(content, documentName, documentType) {
    const blob = new Blob([content], { type: 'text/html; charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${documentName}_with_svg.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showMessage('文档导出成功！', 'success');
}

// 从内容判断文档类型
function getDocumentTypeFromContent(content, documentName = '') {
    const patentPatterns = [
        /专利.*申请.*书/, /发明.*申请.*书/, /实用新型.*申请.*书/, /外观设计.*申请.*书/
    ];
    const projectPatterns = [
        /项目.*申请.*表/, /课题.*申请.*书/, /基金.*申请.*书/
    ];
    const contractPatterns = [
        /合同.*书/, /协议.*书/, /意向.*书/
    ];
    const reportPatterns = [
        /报告.*书/, /总结.*报告/, /分析.*报告/
    ];
    
    const allText = content + ' ' + documentName;
    
    if (patentPatterns.some(pattern => pattern.test(allText))) {
        return 'patent';
    } else if (projectPatterns.some(pattern => pattern.test(allText))) {
        return 'project';
    } else if (contractPatterns.some(pattern => pattern.test(allText))) {
        return 'contract';
    } else if (reportPatterns.some(pattern => pattern.test(allText))) {
        return 'report';
    } else {
        return 'general';
    }
}

// 在现有的预览和导出函数中集成SVG功能
// 修改现有的previewDocument函数
async function previewDocument() {
    try {
        const documentContent = document.getElementById('document-content').value;
        
        if (!documentContent.trim()) {
            showMessage('请先输入文档内容', 'error');
            return;
        }
        
        // 使用增强预览功能
        await enhancedPreview();
        
    } catch (error) {
        showMessage(`预览失败: ${error.message}`, 'error');
    }
}

// 修改现有的exportDocument函数
async function exportDocument() {
    try {
        const documentContent = document.getElementById('document-content').value;
        
        if (!documentContent.trim()) {
            showMessage('请先输入文档内容', 'error');
            return;
        }
        
        // 使用增强导出功能
        await enhancedExport();
        
    } catch (error) {
        showMessage(`导出失败: ${error.message}`, 'error');
    }
}

// 显式展示意图判定结果的模态框
function showIntentModal({ detectedIntent, confidence, recommendedAction, intentOptions, intentLabels, onIntentChange }) {
    // 移除已存在的模态框
    const oldModal = document.getElementById('intent-modal');
    if (oldModal) oldModal.remove();
    // 构建模态框
    const modal = document.createElement('div');
    modal.id = 'intent-modal';
    modal.className = 'fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-lg w-full shadow-lg">
            <div class="flex justify-between items-center mb-4">
                <h4 class="text-lg font-semibold">系统意图判定结果</h4>
                <button class="text-gray-500 hover:text-gray-700" onclick="document.getElementById('intent-modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="mb-3">
                <strong>判定意图类型：</strong>
                <select id="intent-type-select" class="border rounded px-2 py-1">
                    ${intentOptions.map(opt => `<option value="${opt.value}" ${opt.value === detectedIntent ? 'selected' : ''}>${opt.label}</option>`).join('')}
                </select>
            </div>
            <div class="mb-3">
                <strong>置信度：</strong> <span id="intent-confidence">${confidence}%</span>
            </div>
            <div class="mb-3">
                <strong>推荐操作：</strong> <span id="intent-recommend">${getRecommendedActionByIntent(detectedIntent)}</span>
            </div>
            <div class="mb-3" id="intent-guide-text">
                ${intentLabels[detectedIntent]}
            </div>
            <div class="flex justify-end gap-2 mt-4">
                <button class="btn btn-primary" onclick="document.getElementById('intent-modal').remove()">确认</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    // 监听手动切换
    const select = modal.querySelector('#intent-type-select');
    select.addEventListener('change', function() {
        const newIntent = this.value;
        if (onIntentChange) onIntentChange(newIntent);
    });
}

// 根据意图类型返回推荐操作
function getRecommendedActionByIntent(intent) {
    switch (intent) {
        case 'empty_form': return '进入智能填报';
        case 'complete_good': return '作为参考模板';
        case 'messy_format': return '格式整理';
        case 'incomplete': return '内容补全';
        case 'aigc_heavy': return '风格改写';
        default: return '继续后续操作';
    }
}
// 更新模态框内容
function updateIntentModal(newIntent, newAction, guideText) {
    document.getElementById('intent-recommend').textContent = newAction;
    document.getElementById('intent-guide-text').textContent = guideText;
}

function showMessage(message, type = 'info') {
    // 简单弹窗提示，可根据type定制样式
    alert((type === 'error' ? '❌ ' : type === 'success' ? '✅ ' : '') + message);
}

function hideLoading() {
    // 预留loading隐藏逻辑，如有全局loading可在此关闭
    // 当前为占位实现
}

// 修复格式统一相关操作的文件获取逻辑
function getFormatFile() {
    if (window.formatBaseFile) return window.formatBaseFile;
    showMessage('请先上传参考格式文件', 'error');
    return null;
}

function getTargetFile() {
    if (window.formatTargetFile) return window.formatTargetFile;
    showMessage('请先上传待处理文档', 'error');
    return null;
}

async function previewDocument() {
    const formatFile = getFormatFile();
    const targetFile = getTargetFile();
    if (!formatFile || !targetFile) return;
    // ...原有预览逻辑...
}

async function exportDocument() {
    const formatFile = getFormatFile();
    const targetFile = getTargetFile();
    if (!formatFile || !targetFile) return;
    // ...原有导出逻辑...
}

async function enhancedPreview() {
    const formatFile = getFormatFile();
    const targetFile = getTargetFile();
    if (!formatFile || !targetFile) return;
    // ...原有增强预览逻辑...
}

async function enhancedExport() {
    const formatFile = getFormatFile();
    const targetFile = getTargetFile();
    if (!formatFile || !targetFile) return;
    // ...原有增强导出逻辑...
}

async function regenerateSVG() {
    const targetFile = getTargetFile();
    if (!targetFile) return;
    // ...原有SVG生成逻辑...
}

// 全局通用：读取文件内容并回调
function readFileContentAsync(file, callback) {
    const reader = new FileReader();
    reader.onload = function(e) {
        callback(e.target.result);
    };
    reader.onerror = function() {
        showMessage('文件读取失败', 'error');
        callback(null);
    };
    reader.readAsText(file);
}

// 以文风分析为例，所有API调用都要这样处理
async function analyzeWritingStyle() {
    if (!window.currentStyleFile) {
        showMessage('请先上传文件', 'error');
        return;
    }
    readFileContentAsync(window.currentStyleFile, async function(content) {
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
                displayStyleResult(result.style_features);
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

// 以格式统一TAB为例，所有API调用点都要这样处理
async function handleFormatAlignment() {
    if (!window.formatTargetFile) {
        showMessage('请先上传待处理文档', 'error');
        return;
    }
    readFileContentAsync(window.formatTargetFile, async function(content) {
        if (!content || content.trim() === '') {
            showMessage('文档内容为空', 'error');
            return;
        }
        try {
            showLoading('正在格式对齐...');
            const response = await fetch('/api/format-alignment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ document_content: content, document_name: window.formatTargetFile.name })
            });
            const result = await response.json();
            if (result.success) {
                // 处理对齐结果
            } else {
                showMessage(result.error || '格式对齐失败', 'error');
            }
        } catch (err) {
            showMessage('API调用失败: ' + err.message, 'error');
        } finally {
            hideLoading();
        }
    });
}
