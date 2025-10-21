// 创作会话版本管理
class CreationVersionManager {
    constructor() {
        this.currentSessionId = null;
        this.selectedVersions = {
            image: null,
            model: null
        };
        this.initializeUI();
    }

    // 初始化UI
    initializeUI() {
        this.createVersionPanels();
        this.bindEvents();
    }

    // 创建版本面板
    createVersionPanels() {
        const versionContainer = document.createElement('div');
        versionContainer.className = 'version-manager';
        versionContainer.innerHTML = `
            <div class="version-section">
                <h3>
                    <i class="fas fa-images"></i>
                    图片版本
                    <span class="version-count" id="image-version-count">0</span>
                </h3>
                <div class="version-grid" id="image-versions"></div>
                <button class="generate-more-btn" onclick="versionManager.generateMoreImages()">
                    <i class="fas fa-plus"></i>
                    生成更多图片版本
                </button>
            </div>

            <div class="version-section">
                <h3>
                    <i class="fas fa-cube"></i>
                    3D模型版本
                    <span class="version-count" id="model-version-count">0</span>
                </h3>
                <div class="version-grid" id="model-versions"></div>
                <button class="generate-more-btn" onclick="versionManager.generateMoreModels()" disabled>
                    <i class="fas fa-plus"></i>
                    生成更多3D版本
                </button>
            </div>

            <div class="version-actions">
                <button class="save-artwork-btn" onclick="versionManager.saveSelectedArtwork()" disabled>
                    <i class="fas fa-save"></i>
                    保存选中的作品
                </button>
            </div>
        `;

        // 插入到创作页面的合适位置
        const createContainer = document.querySelector('.create-container');
        if (createContainer) {
            createContainer.appendChild(versionContainer);
        }
    }

    // 绑定事件
    bindEvents() {
        // 页面加载时创建会话
        document.addEventListener('DOMContentLoaded', () => {
            this.createSession();
        });
    }

    // 创建创作会话
    async createSession() {
        try {
            const response = await fetch('/create-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_agent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                })
            });

            const result = await response.json();
            if (result.success) {
                this.currentSessionId = result.session_id;
                console.log('✅ 创作会话已创建:', this.currentSessionId);
                this.updateSessionIdInForms();
            } else {
                throw new Error(result.error || '创建会话失败');
            }
        } catch (error) {
            console.error('❌ 创建会话失败:', error);
            showNotification('创建会话失败，请刷新页面重试', 'error');
        }
    }

    // 更新表单中的会话ID
    updateSessionIdInForms() {
        // 为所有生成表单添加会话ID
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

    // 刷新版本显示
    async refreshVersions() {
        if (!this.currentSessionId) return;

        try {
            const [imageVersions, modelVersions, selectedVersions] = await Promise.all([
                this.fetchVersions('image'),
                this.fetchVersions('model'),
                this.fetchSelectedVersions()
            ]);

            this.renderVersions('image', imageVersions);
            this.renderVersions('model', modelVersions);
            this.selectedVersions = selectedVersions;
            this.updateUI();
        } catch (error) {
            console.error('❌ 刷新版本失败:', error);
        }
    }

    // 获取版本列表
    async fetchVersions(type) {
        const response = await fetch(`/session/${this.currentSessionId}/versions?type=${type}`);
        const result = await response.json();
        return result.success ? result.versions : [];
    }

    // 获取选中的版本
    async fetchSelectedVersions() {
        const response = await fetch(`/session/${this.currentSessionId}/selected-versions`);
        const result = await response.json();
        return result.success ? result.selected : {};
    }

    // 渲染版本列表
    renderVersions(type, versions) {
        const container = document.getElementById(`${type}-versions`);
        const countElement = document.getElementById(`${type}-version-count`);
        
        if (!container || !countElement) return;

        countElement.textContent = versions.length;
        container.innerHTML = '';

        versions.forEach((version, index) => {
            const versionItem = this.createVersionItem(type, version, index + 1);
            container.appendChild(versionItem);
        });
    }

    // 创建版本项目
    createVersionItem(type, version, index) {
        const item = document.createElement('div');
        item.className = `version-item ${version.is_selected ? 'selected' : ''}`;
        item.dataset.versionId = version.version_id;

        const content = type === 'image' 
            ? `<img src="${version.url_path}" alt="版本 ${index}" loading="lazy">`
            : `<div class="model-preview">
                 <i class="fas fa-cube"></i>
                 <span>3D模型 v${index}</span>
               </div>`;

        item.innerHTML = `
            ${content}
            <div class="version-info">
                <div class="version-label">版本 ${index}</div>
                <div class="version-note">${version.metadata?.note || ''}</div>
                <div class="version-actions">
                    <button class="select-btn" onclick="versionManager.selectVersion('${version.version_id}')"
                            ${version.is_selected ? 'disabled' : ''}>
                        ${version.is_selected ? '已选中' : '选择'}
                    </button>
                    <button class="delete-btn" onclick="versionManager.deleteVersion('${version.version_id}')"
                            ${version.is_selected ? 'disabled' : ''}>
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;

        return item;
    }

    // 选择版本
    async selectVersion(versionId) {
        try {
            const response = await fetch(`/session/${this.currentSessionId}/select-version`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ version_id: versionId })
            });

            const result = await response.json();
            if (result.success) {
                showNotification(result.message, 'success');
                this.refreshVersions();
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('❌ 选择版本失败:', error);
            showNotification('选择版本失败', 'error');
        }
    }

    // 删除版本
    async deleteVersion(versionId) {
        if (!confirm('确定要删除这个版本吗？此操作不可撤销。')) return;

        try {
            const response = await fetch(`/session/${this.currentSessionId}/delete-version`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ version_id: versionId })
            });

            const result = await response.json();
            if (result.success) {
                showNotification(result.message, 'success');
                this.refreshVersions();
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('❌ 删除版本失败:', error);
            showNotification('删除版本失败', 'error');
        }
    }

    // 生成更多图片版本
    generateMoreImages() {
        // 触发图片生成，但带上版本备注
        const prompt = document.querySelector('input[name="prompt"]')?.value || '';
        if (!prompt.trim()) {
            showNotification('请先输入创作描述', 'warning');
            return;
        }

        const versionNote = prompt(`请为这个图片版本添加备注：`, `风格变化 ${new Date().getTime()}`);
        if (versionNote !== null) {
            // 在表单中添加版本备注
            const noteInput = document.createElement('input');
            noteInput.type = 'hidden';
            noteInput.name = 'version_note';
            noteInput.value = versionNote;
            
            const form = document.querySelector('form');
            form.appendChild(noteInput);
            
            // 触发生成
            generateImage();
        }
    }

    // 生成更多3D模型版本
    generateMoreModels() {
        if (!this.selectedVersions.image) {
            showNotification('请先选择一个图片版本', 'warning');
            return;
        }

        const versionNote = prompt('请为这个3D模型版本添加备注：', `模型变化 ${new Date().getTime()}`);
        if (versionNote !== null) {
            // 使用选中的图片生成3D模型
            this.generate3DFromSelected(versionNote);
        }
    }

    // 从选中图片生成3D模型
    async generate3DFromSelected(versionNote = '') {
        if (!this.selectedVersions.image) return;

        try {
            showLoading('正在生成3D模型...');

            const formData = new FormData();
            formData.append('image_path', this.selectedVersions.image.url_path);
            formData.append('session_id', this.currentSessionId);
            formData.append('version_note', versionNote);

            const response = await fetch('/generate-3d-model', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                showNotification('3D模型生成成功！', 'success');
                this.refreshVersions();
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('❌ 3D模型生成失败:', error);
            showNotification('3D模型生成失败', 'error');
        } finally {
            hideLoading();
        }
    }

    // 保存选中的作品
    async saveSelectedArtwork() {
        if (!this.selectedVersions.image) {
            showNotification('请先选择一个图片版本', 'warning');
            return;
        }

        // 显示保存对话框
        const saveModal = this.createSaveModal();
        document.body.appendChild(saveModal);
    }

    // 创建保存对话框
    createSaveModal() {
        const modal = document.createElement('div');
        modal.className = 'save-modal-overlay';
        modal.innerHTML = `
            <div class="save-modal">
                <h3>保存作品到作品集</h3>
                <form id="save-artwork-form">
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
                        <label>作品类别：</label>
                        <select name="category">
                            <option value="characters">人物角色</option>
                            <option value="animals">动物</option>
                            <option value="nature">自然风景</option>
                            <option value="objects">物品道具</option>
                            <option value="fantasy">奇幻幻想</option>
                            <option value="other">其他</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>作品描述：</label>
                        <textarea name="description" placeholder="描述一下你的创作灵感"></textarea>
                    </div>
                    <div class="modal-actions">
                        <button type="button" onclick="this.closest('.save-modal-overlay').remove()">取消</button>
                        <button type="submit">保存到作品集</button>
                    </div>
                </form>
            </div>
        `;

        // 绑定保存事件
        modal.querySelector('#save-artwork-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.submitSaveArtwork(modal, new FormData(e.target));
        });

        return modal;
    }

    // 提交保存作品
    async submitSaveArtwork(modal, formData) {
        try {
            showLoading('正在保存作品...');

            const data = {
                session_id: this.currentSessionId,
                title: formData.get('title'),
                artist_name: formData.get('artist_name'),
                artist_age: formData.get('artist_age'),
                category: formData.get('category'),
                description: formData.get('description')
            };

            const response = await fetch('/save-artwork', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (result.success) {
                showNotification('作品已成功保存到作品集！', 'success');
                modal.remove();
                
                // 提示用户查看作品集
                setTimeout(() => {
                    if (confirm('作品保存成功！是否前往作品集查看？')) {
                        window.location.href = '/gallery';
                    }
                }, 1000);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('❌ 保存作品失败:', error);
            showNotification('保存作品失败', 'error');
        } finally {
            hideLoading();
        }
    }

    // 更新UI状态
    updateUI() {
        const saveButton = document.querySelector('.save-artwork-btn');
        const generateModelButton = document.querySelector('.generate-more-btn[onclick*="generateMoreModels"]');
        
        if (saveButton) {
            saveButton.disabled = !this.selectedVersions.image;
        }
        
        if (generateModelButton) {
            generateModelButton.disabled = !this.selectedVersions.image;
        }
    }

    // 在生成完成后调用此方法
    onGenerationComplete() {
        this.refreshVersions();
    }
}

// 全局实例
window.versionManager = new CreationVersionManager();

// 辅助函数
function showNotification(message, type = 'info') {
    // 实现通知显示
    console.log(`${type.toUpperCase()}: ${message}`);
}

function showLoading(message) {
    // 实现加载提示
    console.log(`Loading: ${message}`);
}

function hideLoading() {
    // 隐藏加载提示
    console.log('Loading hidden');
}