// 内联版本管理器 - 在创作流程中集成版本管理
class InlineVersionManager {
    constructor() {
        this.currentSessionId = null;
        this.selectedVersions = {
            image: null,
            model: null
        };
        this.currentStage = 1;
        this.stageDetectionTimeout = null;
        this.loadingVersions = false; // 防止重复加载
        this.init();
    }

    // 初始化
    async init() {
        await this.createSession();
        this.setupStageObservers();
    }

    // 设置阶段观察器
    setupStageObservers() {
        // 监听阶段变化
        const observer = new MutationObserver((mutations) => {
            // 避免版本面板变化触发循环
            const hasVersionPanelChanges = mutations.some(mutation => {
                return Array.from(mutation.addedNodes).some(node => 
                    node.nodeType === 1 && node.classList?.contains('inline-version-panel')
                );
            });
            
            if (!hasVersionPanelChanges) {
                this.detectCurrentStage();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class']
        });

        // 初始检测
        setTimeout(() => {
            this.detectCurrentStage();
        }, 1000);
    }

    // 检测当前阶段
    detectCurrentStage() {
        // 防抖：清除之前的定时器
        if (this.stageDetectionTimeout) {
            clearTimeout(this.stageDetectionTimeout);
        }
        
        this.stageDetectionTimeout = setTimeout(() => {
            const stages = [
                { id: 'generation-stage', num: 2 },
                { id: 'adjustment-stage', num: 3 },
                { id: 'model-stage', num: 4 }
            ];

            for (const stage of stages) {
                const element = document.getElementById(stage.id);
                if (element && element.style.display !== 'none') {
                    if (this.currentStage !== stage.num) {
                        this.currentStage = stage.num;
                        this.injectVersionPanelToStage(stage.id, stage.num);
                    }
                    break;
                }
            }
        }, 300); // 300ms防抖延迟
    }

    // 向指定阶段注入版本面板
    injectVersionPanelToStage(stageId, stageNum) {
        const stageElement = document.getElementById(stageId);
        if (!stageElement) return;

        // 在阶段2（生成阶段）不注入版本面板，因为我们使用缩略图网格
        if (stageNum === 2) {
            // 只加载版本数据，不创建面板
            this.loadVersionsForStage(stageNum);
            return;
        }

        // 移除已存在的版本面板
        const existingPanel = stageElement.querySelector('.inline-version-panel');
        if (existingPanel) {
            existingPanel.remove();
        }

        // 根据阶段创建相应的版本面板
        const versionPanel = this.createVersionPanelForStage(stageNum);
        if (versionPanel) {
            this.insertVersionPanel(stageElement, versionPanel, stageNum);
            this.loadVersionsForStage(stageNum);
        }
    }
    
    // 向指定容器注入版本面板内容（用于已有的versions-container）
    injectVersionPanelToContainer(containerId, stageNum) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // 在阶段2（生成阶段）不注入版本卡片，只使用缩略图网格
        if (stageNum === 2) {
            // 隐藏整个版本容器
            const versionsPanel = container.closest('.versions-panel-inline');
            if (versionsPanel) {
                versionsPanel.style.display = 'none';
            }
            // 只加载版本数据到缩略图
            this.loadVersionsForStage(stageNum);
            return;
        }
        
        // 隐藏占位符
        const placeholder = container.querySelector('.no-versions-placeholder');
        if (placeholder) {
            placeholder.style.display = 'none';
        }
        
        // 加载当前阶段的版本
        this.loadVersionsForStage(stageNum);
    }

    // 为不同阶段创建版本面板
    createVersionPanelForStage(stageNum) {
        const panel = document.createElement('div');
        panel.className = 'inline-version-panel';

        if (stageNum === 2) {
            // 图片生成阶段
            panel.innerHTML = `
                <div class="version-header">
                    <h4><i class="fas fa-images"></i> 生成的图片版本 (<span id="image-count">0</span>)</h4>
                    <button class="more-versions-btn" onclick="inlineVersionManager.generateMoreImages()">
                        <i class="fas fa-magic"></i> 生成更多
                    </button>
                </div>
                <div class="version-gallery" id="image-version-gallery"></div>
                <div class="version-tip">
                    <i class="fas fa-lightbulb"></i> 点击选择你最喜欢的版本，然后继续到下一步
                </div>
            `;
        } else if (stageNum === 3) {
            // 图片调整阶段
            panel.innerHTML = `
                <div class="version-header">
                    <h4><i class="fas fa-edit"></i> 调整版本历史 (<span id="adjust-count">0</span>)</h4>
                    <button class="adjust-more-btn" onclick="inlineVersionManager.generateAdjustmentVersion()">
                        <i class="fas fa-tools"></i> 生成调整版本
                    </button>
                </div>
                <div class="version-gallery" id="adjust-version-gallery"></div>
                <div class="current-selection" id="current-image-selection">
                    <div class="selection-label">当前选中的图片：</div>
                    <div class="selected-image-preview"></div>
                </div>
            `;
        } else if (stageNum === 4) {
            // 3D模型生成阶段
            panel.innerHTML = `
                <div class="version-header">
                    <h4><i class="fas fa-cube"></i> 3D模型版本 (<span id="model-count">0</span>)</h4>
                    <button class="model-more-btn" onclick="inlineVersionManager.generateMore3DModels()" 
                            id="generate-more-models" disabled>
                        <i class="fas fa-cubes"></i> 生成更多
                    </button>
                </div>
                <div class="version-gallery model-gallery" id="model-version-gallery"></div>
                <div class="final-actions">
                    <button class="save-final-btn" onclick="inlineVersionManager.saveToGallery()" disabled>
                        <i class="fas fa-heart"></i> 保存到作品集
                    </button>
                </div>
            `;
        }

        return panel;
    }

    // 插入版本面板到合适位置
    insertVersionPanel(stageElement, panel, stageNum) {
        if (stageNum === 2) {
            // 在生成结果后插入
            const resultDiv = stageElement.querySelector('.generation-result') || 
                             stageElement.querySelector('#generated-image')?.parentElement;
            if (resultDiv) {
                resultDiv.after(panel);
            } else {
                stageElement.appendChild(panel);
            }
        } else if (stageNum === 3) {
            // 在调整控制之前插入
            const controls = stageElement.querySelector('.adjustment-controls');
            if (controls) {
                controls.before(panel);
            } else {
                stageElement.appendChild(panel);
            }
        } else if (stageNum === 4) {
            // 在3D查看器后插入
            const viewer = stageElement.querySelector('.model-viewer-container') ||
                          stageElement.querySelector('#model-viewer');
            if (viewer) {
                viewer.after(panel);
            } else {
                stageElement.appendChild(panel);
            }
        }
    }

    // 为指定阶段加载版本
    async loadVersionsForStage(stageNum) {
        if (!this.currentSessionId || this.loadingVersions) return;

        this.loadingVersions = true;
        try {
            if (stageNum === 2 || stageNum === 3) {
                await this.loadImageVersions();
            } else if (stageNum === 4) {
                await this.loadModelVersions();
                this.updateModelGenerationButton();
            }
            
            await this.loadSelectedVersions();
            this.updateUI();
        } catch (error) {
            console.error('❌ 加载版本失败:', error);
        } finally {
            this.loadingVersions = false;
        }
    }

    // 加载图片版本
    async loadImageVersions() {
        const versions = await this.fetchVersions('image');
        this.renderImageVersions(versions);
    }

    // 加载3D模型版本
    async loadModelVersions() {
        const versions = await this.fetchVersions('model');
        this.renderModelVersions(versions);
    }

    // 渲染图片版本
    renderImageVersions(versions) {
        const gallery = document.getElementById('image-version-gallery') || 
                       document.getElementById('adjust-version-gallery');
        
        // 如果gallery存在，渲染版本卡片
        if (gallery) {
            gallery.innerHTML = '';

            versions.forEach((version, index) => {
                const item = this.createImageVersionItem(version, index);
                gallery.appendChild(item);
            });

            // 更新计数
            const countElement = document.getElementById('image-count') || 
                               document.getElementById('adjust-count');
            if (countElement) {
                countElement.textContent = versions.length;
            }
        }
        
        // 总是更新缩略图网格（即使gallery不存在）
        this.updateThumbnailsGrid(versions);
    }
    
    // 更新右侧缩略图网格
    updateThumbnailsGrid(versions) {
        const thumbnailsGrid = document.querySelector('.thumbnails-grid');
        if (!thumbnailsGrid) {
            console.warn('⚠️ 未找到 .thumbnails-grid 元素');
            return;
        }
        
        let thumbnailSlots = thumbnailsGrid.querySelectorAll('.thumbnail-slot');
        
        // 如果槽位不存在，创建6个槽位
        if (thumbnailSlots.length === 0) {
            thumbnailsGrid.innerHTML = '';
            for (let i = 0; i < 6; i++) {
                const slot = document.createElement('div');
                slot.className = 'thumbnail-slot';
                thumbnailsGrid.appendChild(slot);
            }
            thumbnailSlots = thumbnailsGrid.querySelectorAll('.thumbnail-slot');
        }
        
        // 更新每个缩略图槽位（前5个显示版本，第6个显示"生成更多"按钮）
        thumbnailSlots.forEach((slot, index) => {
            // 清空现有内容
            slot.innerHTML = '';
            
            if (index < 5 && index < versions.length) {
                // 前5个槽位：如果有对应的版本，显示缩略图
                const version = versions[index];
                const isSelected = version.is_selected;
                
                slot.className = `thumbnail-slot ${isSelected ? 'selected' : ''}`;
                slot.onclick = () => this.selectVersion(version.version_id);
                
                slot.innerHTML = `
                    <img src="${version.url_path}" alt="版本 ${index + 1}" loading="lazy">
                    ${isSelected ? '<div class="selected-indicator"><i class="fas fa-check"></i></div>' : ''}
                    <div class="thumbnail-number">版本 ${index + 1}</div>
                `;
            } else if (index === 5) {
                // 第6个槽位：显示"生成更多"按钮
                slot.className = 'thumbnail-slot generate-more-btn';
                slot.onclick = () => this.generateMore();
                slot.innerHTML = `
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; color: #667eea; font-size: 14px; font-weight: 500;">
                        <i class="fas fa-plus-circle" style="font-size: 24px; margin-bottom: 5px;"></i>
                        <span>生成更多</span>
                    </div>
                `;
            } else if (index < 5) {
                // 前5个槽位的占位符
                slot.className = 'thumbnail-slot';
                slot.onclick = null;
                slot.innerHTML = `<div class="thumbnail-placeholder">${index + 1}</div>`;
            }
        });
    }

    // 渲染3D模型版本
    renderModelVersions(versions) {
        const gallery = document.getElementById('model-version-gallery');
        if (!gallery) return;

        gallery.innerHTML = '';

        versions.forEach((version, index) => {
            const item = this.createModelVersionItem(version, index);
            gallery.appendChild(item);
        });

        // 更新计数
        const countElement = document.getElementById('model-count');
        if (countElement) {
            countElement.textContent = versions.length;
        }
    }

    // 创建图片版本项
    createImageVersionItem(version, index) {
        const item = document.createElement('div');
        item.className = `version-item ${version.is_selected ? 'selected' : ''}`;
        item.onclick = () => this.selectVersion(version.version_id);

        item.innerHTML = `
            <div class="version-image">
                <img src="${version.url_path}" alt="版本 ${index + 1}" loading="lazy">
                ${version.is_selected ? '<div class="selected-badge">已选中</div>' : ''}
            </div>
            <div class="version-info">
                <div class="version-number">版本 ${index + 1}</div>
                ${version.metadata?.note ? `<div class="version-note">${version.metadata.note}</div>` : ''}
            </div>
        `;

        return item;
    }

    // 创建3D模型版本项
    createModelVersionItem(version, index) {
        const item = document.createElement('div');
        item.className = `version-item model-item ${version.is_selected ? 'selected' : ''}`;
        item.onclick = () => this.selectVersion(version.version_id);

        item.innerHTML = `
            <div class="model-preview">
                <i class="fas fa-cube"></i>
                <div class="model-info">
                    <div class="model-name">模型 ${index + 1}</div>
                    ${version.is_selected ? '<div class="selected-badge">已选中</div>' : ''}
                </div>
            </div>
            <button class="view-3d-btn" onclick="event.stopPropagation(); inlineVersionManager.view3DModel('${version.url_path}')">
                <i class="fas fa-eye"></i> 预览
            </button>
        `;

        return item;
    }

    // 创建会话
    async createSession() {
        try {
            const response = await fetch('/create-session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_agent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.currentSessionId = result.session_id;
                this.updateFormSessionIds();
            } else {
                console.error('❌ 创建会话失败:', result.error);
                alert('创建会话失败，请刷新页面重试');
            }
        } catch (error) {
            console.error('❌ 创建会话网络错误:', error);
            alert('网络错误，请检查连接后重试');
        }
    }

    // 更新表单中的会话ID
    updateFormSessionIds() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            let sessionInput = form.querySelector('input[name="session_id"]');
            if (!sessionInput) {
                sessionInput = document.createElement('input');
                sessionInput.type = 'hidden';
                sessionInput.name = 'session_id';
                form.appendChild(sessionInput);
            }
            sessionInput.value = this.currentSessionId;
        });
    }

    // 获取版本列表
    async fetchVersions(type) {
        const response = await fetch(`/session/${this.currentSessionId}/versions?type=${type}`);
        const result = await response.json();
        return result.success ? result.versions : [];
    }

    // 加载选中的版本
    async loadSelectedVersions() {
        const response = await fetch(`/session/${this.currentSessionId}/selected-versions`);
        const result = await response.json();
        if (result.success) {
            this.selectedVersions = result.selected;
        }
    }

    // 选择版本
    async selectVersion(versionId) {
        try {
            const response = await fetch(`/session/${this.currentSessionId}/select-version`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ version_id: versionId })
            });

            const result = await response.json();
            if (result.success) {
                await this.loadSelectedVersions();
                this.updateUI();
                this.updateMainDisplay();
            }
        } catch (error) {
            console.error('❌ 选择版本失败:', error);
        }
    }

    // 更新UI
    updateUI() {
        // 重新渲染当前阶段的版本
        this.loadVersionsForStage(this.currentStage);
        
        // 更新按钮状态
        this.updateButtonStates();
    }

    // 更新主显示区域
    updateMainDisplay() {
        if (this.selectedVersions.image) {
            // 更新主图片显示
            const imageElements = [
                'generated-image',
                'current-image', 
                'final-image',
                'adjustment-image'
            ];
            
            imageElements.forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    element.src = this.selectedVersions.image.url_path;
                    element.style.display = 'block';
                }
            });

            // 更新当前选择预览
            this.updateCurrentSelectionPreview();
        }
    }

    // 更新当前选择预览
    updateCurrentSelectionPreview() {
        const preview = document.querySelector('.selected-image-preview');
        if (preview && this.selectedVersions.image) {
            preview.innerHTML = `
                <img src="${this.selectedVersions.image.url_path}" alt="当前选中">
                <div class="selection-info">
                    <div class="selection-name">当前选中版本</div>
                </div>
            `;
        }
    }

    // 更新按钮状态
    updateButtonStates() {
        // 3D模型生成按钮
        const modelBtn = document.getElementById('generate-more-models');
        if (modelBtn) {
            modelBtn.disabled = !this.selectedVersions.image;
        }

        // 保存按钮
        const saveBtn = document.querySelector('.save-final-btn');
        if (saveBtn) {
            saveBtn.disabled = !this.selectedVersions.image;
        }
    }

    // 更新3D模型生成按钮
    updateModelGenerationButton() {
        const btn = document.getElementById('generate-more-models');
        if (btn) {
            btn.disabled = !this.selectedVersions.image;
            btn.title = this.selectedVersions.image ? 
                '点击生成更多3D模型版本' : 
                '请先选择一个图片版本';
        }
    }

    // 生成更多图片
    generateMoreImages() {
        if (typeof generateImage === 'function') {
            generateImage();
        } else {
            const form = document.querySelector('form[action="/generate-image"]');
            if (form) {
                form.submit();
            }
        }
    }

    // 生成调整版本
    generateAdjustmentVersion() {
        if (!this.selectedVersions.image) {
            alert('请先选择一个图片版本');
            return;
        }

        if (typeof adjustImage === 'function') {
            adjustImage();
        } else {
            const form = document.querySelector('form[action="/adjust-image"]');
            if (form) {
                form.submit();
            }
        }
    }

    // 生成更多3D模型
    generateMore3DModels() {
        if (!this.selectedVersions.image) {
            alert('请先选择一个图片版本');
            return;
        }

        if (typeof generate3DModel === 'function') {
            generate3DModel();
        } else {
            const form = document.querySelector('form[action="/generate-3d-model"]');
            if (form) {
                form.submit();
            }
        }
    }

    // 查看3D模型
    view3DModel(modelUrl) {
        if (typeof load3DModel === 'function') {
            load3DModel(modelUrl);
        } else {
            // 在主3D查看器中显示
            const viewer = document.getElementById('model-viewer');
            if (viewer) {
                viewer.src = modelUrl;
            }
        }
    }

    // 保存到作品集
    saveToGallery() {
        if (!this.selectedVersions.image) {
            alert('请先选择一个图片版本');
            return;
        }

        if (!this.currentSessionId) {
            console.error('❌ 会话ID不存在:', this.currentSessionId);
            alert('会话未正确创建，请刷新页面重试');
            return;
        }

        // 显示保存对话框
        this.showSaveDialog();
    }

    // 显示保存对话框
    showSaveDialog() {
        // 再次确认会话ID
        if (!this.currentSessionId) {
            console.error('❌ 创建保存对话框时会话ID为空');
            alert('会话ID丢失，请刷新页面重试');
            return;
        }

        const modal = document.createElement('div');
        modal.className = 'save-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>保存到作品集</h3>
                <form id="save-form">
                    <input type="hidden" name="session_id" value="${this.currentSessionId}">
                    <div class="form-group">
                        <label>作品标题：</label>
                        <input type="text" name="title" required placeholder="给你的作品起个名字">
                    </div>
                    <div class="form-group">
                        <label>创作者姓名：</label>
                        <input type="text" name="artist_name" required placeholder="你的名字">
                    </div>
                    <div class="form-group">
                        <label>年龄：</label>
                        <input type="number" name="artist_age" min="6" max="18" value="10" required>
                    </div>
                    <div class="form-group">
                        <label>作品描述：</label>
                        <textarea name="description" placeholder="描述一下你的创作"></textarea>
                    </div>
                    <div class="modal-actions">
                        <button type="button" onclick="this.closest('.save-modal').remove()">取消</button>
                        <button type="submit">保存</button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);

        // 绑定提交事件
        modal.querySelector('#save-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.submitSaveForm(modal, new FormData(e.target));
        });
    }

    // 提交保存表单
    async submitSaveForm(modal, formData) {
        try {
            const sessionId = formData.get('session_id');
            
            if (!sessionId) {
                alert('会话ID缺失，请刷新页面重试');
                return;
            }

            const data = {
                session_id: sessionId,
                title: formData.get('title'),
                artist_name: formData.get('artist_name'),
                artist_age: formData.get('artist_age'),
                description: formData.get('description')
            };

            const response = await fetch('/save-artwork', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (result.success) {
                modal.remove();
                alert('作品保存成功！');
                
                if (confirm('是否前往作品集查看？')) {
                    window.location.href = '/gallery';
                }
            } else {
                alert('保存失败：' + result.error);
            }
        } catch (error) {
            console.error('❌ 保存失败:', error);
            alert('保存失败，请重试');
        }
    }

    // 生成完成后的回调
    onGenerationComplete() {
        setTimeout(async () => {
            await this.loadVersionsForStage(this.currentStage);
            // 自动选择并显示最新生成的版本
            await this.autoSelectLatestVersion();
        }, 1000);
    }
    
    // 自动选择最新版本
    async autoSelectLatestVersion() {
        try {
            const versions = await this.fetchVersions('image');
            if (versions && versions.length > 0) {
                // 获取最新版本（通常是第一个）
                const latestVersion = versions[0];
                
                // 更新主图片显示
                const imageElements = [
                    'generated-image',
                    'current-image', 
                    'final-image',
                    'adjustment-image'
                ];
                
                imageElements.forEach(id => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.src = latestVersion.url_path;
                        element.style.display = 'block';
                    }
                });
                
                // 更新全局变量（如果存在）
                if (window.generatedImageUrl !== undefined) {
                    window.generatedImageUrl = latestVersion.url_path;
                }
            }
        } catch (error) {
            console.error('❌ 自动选择最新版本失败:', error);
        }
    }
    
    // 生成更多版本
    generateMore() {
        // 检查是否在生成阶段且有必要的参数
        if (this.currentStage !== 2) {
            console.warn('⚠️ 当前不在生成阶段');
            return;
        }
        
        // 直接调用生成函数，不需要重新上传
        if (typeof generateImage === 'function') {
            generateImage();
        } else {
            console.error('❌ generateImage 函数未定义');
        }
    }

    // 兼容性方法：显示指定阶段的版本
    showVersionsForStage(stageNumber) {
        const stageIds = {
            1: 'input-stage',
            2: 'generation-stage', 
            3: 'adjustment-stage',
            4: 'model-stage'
        };
        const stageId = stageIds[stageNumber];
        if (stageId) {
            this.injectVersionPanelToStage(stageId, stageNumber);
        }
    }
}

// 全局实例
window.inlineVersionManager = new InlineVersionManager();