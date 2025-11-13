// 统一的作品模态框功能
// 用于gallery页面和my_artworks页面的共享模态框组件

// 增加浏览次数(如果有artworkId的话)
async function incrementViewCount(artworkId) {
    if (!artworkId) return;
    
    try {
        const response = await fetch(`/increment-view/${artworkId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`作品 ${artworkId} 浏览次数已更新: ${result.view_count}`);
        }
    } catch (error) {
        console.error('更新浏览次数失败:', error);
    }
}

// 作品详情模态框功能
function showArtworkModal(element) {
    // 阻止事件冒泡，防止意外触发
    if (event) {
        event.stopPropagation();
    }
    
    if (!element) {
        console.error('Element is null or undefined');
        return;
    }
    
    console.log('showArtworkModal called, checking showImageModal function:', typeof showImageModal);
    
    const artworkData = {
        id: element.dataset.artworkId,
        title: element.dataset.artworkTitle,
        artist: element.dataset.artworkArtist,
        age: element.dataset.artworkAge,
        date: element.dataset.artworkDate,
        description: element.dataset.artworkDescription,
        originalImage: element.dataset.artworkOriginal,
        generatedImage: element.dataset.artworkGenerated,
        modelFile: element.dataset.artworkModel,
        likes: element.dataset.artworkLikes,
        views: element.dataset.artworkViews,
        sessionId: element.dataset.artworkSessionId,
        coloredVersions: JSON.parse(element.dataset.artworkColoredVersions || '[]'),
        adjustedVersions: JSON.parse(element.dataset.artworkAdjustedVersions || '[]')
    };
    
    // 增加浏览次数(仅对公开作品)
    if (artworkData.id) {
        incrementViewCount(artworkData.id);
    }
    
    console.log('Artwork versions:', {
        colored: artworkData.coloredVersions,
        adjusted: artworkData.adjustedVersions,
        sessionId: artworkData.sessionId
    });
    
    // 保存sessionId到modal元素
    const modal = document.getElementById('artworkModal');
    if (modal && artworkData.sessionId) {
        modal.dataset.sessionId = artworkData.sessionId;
    }
    
    // 设置模态框标题
    const modalTitle = document.getElementById('modalArtworkTitle');
    const editBtn = document.getElementById('editTitleBtn');
    
    if (modalTitle) {
        modalTitle.textContent = artworkData.title;
        modalTitle.dataset.artworkId = artworkData.id;
        
        // 只在"我的作品"页面显示编辑按钮
        const isMyArtworks = window.location.pathname.includes('my-artworks');
        if (editBtn && artworkData.id && isMyArtworks) {
            editBtn.style.display = 'inline-block';
            modalTitle.setAttribute('contenteditable', 'false');
            modalTitle.classList.remove('editing');
            editBtn.innerHTML = '<i class="fas fa-edit"></i>';
            editBtn.title = '编辑标题';
        } else if (editBtn) {
            editBtn.style.display = 'none';
        }
    }
    
    // 构建作品展示区域
    const showcase = document.getElementById('modalArtworkShowcase');
    if (!showcase) {
        console.error('Modal showcase element not found');
        return;
    }
    showcase.innerHTML = '';
    
    // 原始简笔画
    if (artworkData.originalImage && artworkData.originalImage.trim() !== '' && artworkData.originalImage !== 'null') {
        console.log('Adding original image with click handler:', artworkData.originalImage);
        const originalStep = document.createElement('div');
        originalStep.className = 'artwork-detail-step';
        originalStep.innerHTML = `
            <h4>原始简笔画</h4>
            <img src="${artworkData.originalImage}" alt="原始简笔画" 
                 style="cursor: pointer;" 
                 title="点击查看大图"
                 class="clickable-image"
                 onerror="this.parentElement.style.display='none'">
        `;
        showcase.appendChild(originalStep);
        
        // 为图片添加点击事件监听器
        const img = originalStep.querySelector('img');
        if (img) {
            img.addEventListener('click', function(e) {
                e.stopPropagation();
                console.log('Original image clicked, calling showImageModal');
                showImageModal(this.src, '原始简笔画');
            });
        }
    } else {
        console.log('No original image data available, value:', artworkData.originalImage);
        // 显示文字提示创作的说明
        const originalStep = document.createElement('div');
        originalStep.className = 'artwork-detail-step';
        originalStep.innerHTML = `
            <h4>创作方式</h4>
            <div class="text-creation-info">
                <i class="fas fa-keyboard"></i>
                <p>通过文字描述生成</p>
                <small>作者使用文字提示词直接创作，没有上传简笔画</small>
            </div>
        `;
        showcase.appendChild(originalStep);
    }
    
    // AI生成图片
    if (artworkData.generatedImage) {
        console.log('Adding generated image with click handler:', artworkData.generatedImage);
        const generatedStep = document.createElement('div');
        generatedStep.className = 'artwork-detail-step';
        
        // 检查是否在"我的作品"页面
        const isMyArtworks = window.location.pathname.includes('my-artworks');
        
        generatedStep.innerHTML = `
            <h4>AI生成效果</h4>
            <div class="image-with-actions">
                <img src="${artworkData.generatedImage}" alt="AI生成效果" 
                     style="cursor: pointer;" 
                     title="点击查看大图"
                     class="clickable-image"
                     onerror="this.parentElement.style.display='none'">
                ${isMyArtworks && artworkData.id ? `
                <div class="image-action-buttons">
                    <button class="image-action-btn" data-action="continue" title="基于此图调整后重新生成">
                        <i class="fas fa-paint-brush"></i>
                        <span>继续调整</span>
                    </button>
                    <button class="image-action-btn" data-action="generate-model" title="基于此图调整参数后生成3D模型">
                        <i class="fas fa-cube"></i>
                        <span>转3D模型</span>
                    </button>
                    <button class="image-action-btn" data-action="generate-video" title="基于此图调整参数后生成视频">
                        <i class="fas fa-video"></i>
                        <span>转视频</span>
                    </button>
                </div>
                ` : ''}
            </div>
        `;
        showcase.appendChild(generatedStep);
        
        // 为图片添加点击事件监听器
        const img = generatedStep.querySelector('img');
        if (img) {
            img.addEventListener('click', function(e) {
                e.stopPropagation();
                console.log('Generated image clicked, calling showImageModal');
                showImageModal(this.src, 'AI生成效果');
            });
        }
        
        // 为操作按钮添加事件监听器
        if (isMyArtworks && artworkData.id) {
            const actionButtons = generatedStep.querySelectorAll('.image-action-btn');
            actionButtons.forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const action = this.dataset.action;
                    handleImageAction(action, artworkData.id, artworkData.generatedImage);
                });
            });
        }
    } else {
        console.log('No generated image data available');
    }
    
    // 显示所有版本历史
    if (artworkData.sessionId && (artworkData.coloredVersions.length > 0 || artworkData.adjustedVersions.length > 0)) {
        const versionsStep = document.createElement('div');
        versionsStep.className = 'artwork-detail-step';
        
        let versionsHTML = '<h4><i class="fas fa-history"></i> 版本历史</h4><div class="version-gallery">';
        
        // 显示上色版本
        if (artworkData.coloredVersions.length > 0) {
            versionsHTML += '<div class="version-group"><h5>AI上色版本 (' + artworkData.coloredVersions.length + '个)</h5><div class="version-thumbs">';
            artworkData.coloredVersions.forEach((filename, index) => {
                const versionUrl = `/creation_sessions/${artworkData.sessionId}/${filename}`;
                versionsHTML += `
                    <div class="version-thumb" onclick="showImageModal('${versionUrl}', '上色版本 ${index + 1}')" title="点击查看大图">
                        <img src="${versionUrl}" alt="版本 ${index + 1}" onerror="this.parentElement.style.display='none'">
                        <span class="version-label">版本 ${index + 1}</span>
                    </div>
                `;
            });
            versionsHTML += '</div></div>';
        }
        
        // 显示调整版本
        if (artworkData.adjustedVersions.length > 0) {
            versionsHTML += '<div class="version-group"><h5>调整版本 (' + artworkData.adjustedVersions.length + '个)</h5><div class="version-thumbs">';
            artworkData.adjustedVersions.forEach((filename, index) => {
                const versionUrl = `/creation_sessions/${artworkData.sessionId}/${filename}`;
                versionsHTML += `
                    <div class="version-thumb" onclick="showImageModal('${versionUrl}', '调整版本 ${index + 1}')" title="点击查看大图">
                        <img src="${versionUrl}" alt="调整版本 ${index + 1}" onerror="this.parentElement.style.display='none'">
                        <span class="version-label">调整 ${index + 1}</span>
                    </div>
                `;
            });
            versionsHTML += '</div></div>';
        }
        
        versionsHTML += '</div>';
        versionsStep.innerHTML = versionsHTML;
        showcase.appendChild(versionsStep);
    }
    
    // 3D模型
    if (artworkData.modelFile) {
        const modelStep = document.createElement('div');
        modelStep.className = 'artwork-detail-step';
        modelStep.innerHTML = `
            <h4>3D模型</h4>
            <div class="model-preview-container">
                <div class="model-preview-thumb" onclick="showModelModal('${artworkData.modelFile}', '3D模型')">
                    <div class="model-thumbnail">
                        <i class="fas fa-cube"></i>
                        <span>点击查看3D模型</span>
                    </div>
                </div>
            </div>
        `;
        showcase.appendChild(modelStep);
    }
    
    // 设置作品信息
    const info = document.getElementById('modalArtworkInfo');
    if (!info) {
        console.error('Modal info element not found');
        return;
    }
    info.innerHTML = `
        <div class="modal-artwork-info">
            <p class="modal-artist-info">
                <i class="fas fa-user-circle"></i>
                <strong>${artworkData.artist}</strong>，${artworkData.age}岁
            </p>
            <p class="modal-creation-date">
                <i class="fas fa-calendar"></i>
                创作时间：${artworkData.date}
            </p>
            ${artworkData.description ? `
                <div class="modal-artwork-description">
                    <h4><i class="fas fa-comment"></i> 作品说明</h4>
                    <p>${artworkData.description}</p>
                </div>
            ` : ''}
            <div class="modal-artwork-stats">
                <span class="modal-likes" onclick="likeArtwork('${artworkData.id}')">
                    <i class="fas fa-heart"></i>
                    <span id="modal-likes-${artworkData.id}">${artworkData.likes}</span>个赞
                </span>
                <span class="modal-views">
                    <i class="fas fa-eye"></i>
                    ${artworkData.views}次浏览
                </span>
            </div>
        </div>
    `;
    
    // 显示模态框
    const modal = document.getElementById('artworkModal');
    if (!modal) {
        console.error('Artwork modal element not found');
        return;
    }
    
    // 禁止背景滚动
    document.body.style.overflow = 'hidden';
    
    modal.style.display = 'flex';
    
    // 添加显示类来触发CSS动画（使用setTimeout确保display生效后再添加类）
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

function closeArtworkModal() {
    const modal = document.getElementById('artworkModal');
    if (!modal) return;
    
    const content = modal.querySelector('.artwork-modal-content');
    
    // 移除显示类
    modal.classList.remove('show');
    
    // 添加关闭动画
    if (content) {
        content.style.transform = 'scale(0.9)';
        content.style.opacity = '0';
    }
    
    setTimeout(() => {
        modal.style.display = 'none';
        
        // 恢复背景滚动
        document.body.style.overflow = '';
        
        // 重置模态框状态
        if (content) {
            content.classList.remove('enlarged-mode');
            if (content.dataset.originalContent) {
                delete content.dataset.originalContent;
            }
            
            // 重置动画状态
            content.style.transform = '';
            content.style.opacity = '';
        }
        
        // 清除图片叠加层（如果存在）
        const imageOverlay = document.getElementById('imageOverlay');
        if (imageOverlay) {
            imageOverlay.remove();
        }
    }, 300);
}

// 在当前模态框上方叠加图片
function showImageModal(imageSrc, title) {
    console.log('showImageModal called with:', imageSrc, title);
    
    // 阻止事件冒泡
    if (window.event) {
        window.event.stopPropagation();
        window.event.preventDefault();
    }
    
    // 检查是否已经有图片叠加层，如果有就先移除
    const existingOverlay = document.getElementById('imageOverlay');
    if (existingOverlay) {
        console.log('Removing existing image overlay');
        existingOverlay.remove();
    }
    
    // 创建图片叠加层
    const imageOverlay = document.createElement('div');
    imageOverlay.id = 'imageOverlay';
    imageOverlay.className = 'image-overlay';
    
    console.log('Creating image overlay element');
    
    imageOverlay.innerHTML = `
        <div class="image-overlay-backdrop"></div>
        <div class="image-overlay-content">
            <img src="${imageSrc}" alt="${title}" class="overlay-image thumbnail-mode" 
                 data-mode="thumbnail">
        </div>
    `;
    
    // 添加到当前模态窗口内
    const artworkModal = document.getElementById('artworkModal');
    if (!artworkModal) {
        console.error('Artwork modal not found!');
        return;
    }
    
    console.log('Adding image overlay to artwork modal');
    artworkModal.appendChild(imageOverlay);
    
    // 显示叠加层 - 需要添加visible类来触发CSS动画
    imageOverlay.style.display = 'flex';
    // 延迟添加visible类以触发动画
    setTimeout(() => {
        imageOverlay.classList.add('visible');
    }, 10);
    console.log('Image overlay should now be visible');
    
    // 为图片添加事件监听
    const overlayImg = imageOverlay.querySelector('.overlay-image');
    if (overlayImg) {
        // 双击切换全屏
        overlayImg.addEventListener('dblclick', function(e) {
            e.stopPropagation();
            toggleImageMode(this);
        });
        
        // 单击切换模式
        overlayImg.addEventListener('click', function(e) {
            e.stopPropagation();
            handleImageClick(this);
        });
    }
    
    // 点击背景关闭叠加层
    const backdrop = imageOverlay.querySelector('.image-overlay-backdrop');
    if (backdrop) {
        backdrop.addEventListener('click', function(e) {
            e.stopPropagation();
            closeImageOverlay();
        });
    }
    
    // 也可以点击图片区域关闭
    imageOverlay.addEventListener('click', function(e) {
        console.log('Image overlay clicked:', e.target.className);
        // 如果点击的不是图片本身，就关闭叠加层
        if (e.target === imageOverlay || 
            e.target.classList.contains('image-overlay-backdrop') ||
            e.target.classList.contains('image-overlay-content')) {
            console.log('Closing image overlay');
            closeImageOverlay();
        }
    });
}

function handleImageClick(img) {
    // 单击切换图片模式
    if (img.dataset.mode === 'thumbnail') {
        img.dataset.mode = 'fullsize';
        img.classList.remove('thumbnail-mode');
        img.classList.add('fullsize-mode');
    } else {
        img.dataset.mode = 'thumbnail';
        img.classList.remove('fullsize-mode');
        img.classList.add('thumbnail-mode');
    }
}

function closeImageOverlay() {
    const imageOverlay = document.getElementById('imageOverlay');
    if (imageOverlay) {
        console.log('Closing image overlay with animation');
        // 移除visible类触发消失动画
        imageOverlay.classList.remove('visible');
        // 等待动画完成后移除元素
        setTimeout(() => {
            if (imageOverlay.parentNode) {
                imageOverlay.remove();
            }
        }, 300);
    }
}

// 关闭独立的图片模态框（artwork_modals.html中的imageModal）
function closeImageModal() {
    const imageModal = document.getElementById('imageModal');
    if (imageModal) {
        imageModal.style.display = 'none';
        // 清空图片
        const fullImage = document.getElementById('fullImage');
        if (fullImage) {
            fullImage.src = '';
        }
    }
}

function showModelModal(modelSrc, title) {
    if (event) {
        event.stopPropagation();
    }
    
    console.log('showModelModal called with:', modelSrc, title);
    
    // 等待DOM完全加载的函数
    const ensureDOMReady = (callback) => {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', callback);
        } else {
            callback();
        }
    };
    
    ensureDOMReady(() => {
        const modelOverlay = document.getElementById('modelOverlay');
        const modelTitle = document.getElementById('modelTitle');
        
        if (!modelOverlay) {
            console.error('Model overlay element not found');
            alert('3D模型查看器初始化失败：找不到模型容器');
            return;
        }
        
        // 设置标题（如果元素存在）
        if (modelTitle) {
            modelTitle.textContent = title;
            console.log('Model title set successfully');
        } else {
            console.warn('Model title element not found, continuing without title');
        }
        
        // 显示模型叠加层
        modelOverlay.style.display = 'flex';
        // 添加visible类来触发CSS动画
        setTimeout(() => {
            modelOverlay.classList.add('visible');
        }, 10);
        console.log('Model overlay displayed');
        
        // 获取模型容器
        const modelContainer = document.getElementById('modelContainer');
        if (!modelContainer) {
            console.error('Model container not found');
            return;
        }
        
        // 清空容器
        modelContainer.innerHTML = '';
        
        // 如果有ModelViewer3D类，使用它来初始化3D查看器
        if (typeof ModelViewer3D !== 'undefined') {
            console.log('Using ModelViewer3D class');
            try {
                // 创建ModelViewer3D实例
                const viewer = new ModelViewer3D(modelContainer, {
                    backgroundColor: 0x000000,
                    enableControls: true,
                    enableAutoRotate: false,
                    onModelLoaded: () => {
                        console.log('3D model loaded successfully');
                    },
                    onLoadError: (error) => {
                        console.error('3D model load error:', error);
                        modelContainer.innerHTML = `
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; text-align: center;">
                                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem; color: #ff6b6b;"></i>
                                <p>3D模型加载失败</p>
                                <p style="margin-top: 10px;"><a href="${modelSrc}" target="_blank" style="color: #4CAF50;">下载模型文件</a></p>
                            </div>
                        `;
                    }
                });
                
                // 加载模型
                viewer.loadModel(modelSrc);
                
            } catch (error) {
                console.error('Error creating ModelViewer3D:', error);
                // 降级到备用显示
                modelContainer.innerHTML = `
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; text-align: center;">
                        <i class="fas fa-cube" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                        <p>3D模型查看器初始化失败</p>
                        <p style="margin-top: 10px;"><a href="${modelSrc}" target="_blank" style="color: #4CAF50;">下载模型文件</a></p>
                    </div>
                `;
            }
        } else {
            console.log('ModelViewer3D class not found, using fallback');
            // 提供一个备用的显示方式
            modelContainer.innerHTML = `
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; text-align: center;">
                    <i class="fas fa-cube" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <p>3D模型查看器</p>
                    <p style="margin-top: 10px;"><a href="${modelSrc}" target="_blank" style="color: #4CAF50;">下载模型文件</a></p>
                </div>
            `;
            console.log('Fallback content added to model container');
        }
    });
}

function closeModelModal() {
    const modelOverlay = document.getElementById('modelOverlay');
    if (modelOverlay) {
        // 移除visible类触发消失动画
        modelOverlay.classList.remove('visible');
        // 等待动画完成后隐藏元素
        setTimeout(() => {
            modelOverlay.style.display = 'none';
        }, 300);
    }
    
    // 清理3D场景
    if (typeof cleanup3DScene === 'function') {
        cleanup3DScene();
    }
}

function toggleImageMode(img) {
    if (img.dataset.mode === 'thumbnail') {
        img.dataset.mode = 'fullsize';
        img.classList.remove('thumbnail-mode');
        img.classList.add('fullsize-mode');
    } else {
        img.dataset.mode = 'thumbnail';
        img.classList.remove('fullsize-mode');
        img.classList.add('thumbnail-mode');
    }
}

// 模态框事件监听器设置
document.addEventListener('DOMContentLoaded', function() {
    // 点击关闭按钮关闭模态框
    const closeBtn = document.querySelector('.artwork-modal-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            closeArtworkModal();
        });
    }
    
    // 点击模态框背景关闭模态框
    const modal = document.getElementById('artworkModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            // 只有点击模态框本身（不是内容区域）时才关闭
            if (e.target === modal || e.target.classList.contains('artwork-modal')) {
                e.preventDefault();
                e.stopPropagation();
                closeArtworkModal();
            }
        });
    }
    
    // ESC键关闭模态框
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // 优先关闭图片叠加层
            const imageOverlay = document.getElementById('imageOverlay');
            if (imageOverlay && imageOverlay.style.display !== 'none') {
                closeImageOverlay();
                return;
            }
            
            // 然后关闭模态框
            const modal = document.getElementById('artworkModal');
            if (modal && modal.style.display === 'flex') {
                closeArtworkModal();
            }
        }
    });
    
    // 标题编辑功能
    setupTitleEdit();
    
    // 右键菜单功能
    setupContextMenu();
});

// 标题编辑功能
function setupTitleEdit() {
    const editBtn = document.getElementById('editTitleBtn');
    const titleElement = document.getElementById('modalArtworkTitle');
    
    if (!editBtn || !titleElement) return;
    
    editBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        const isEditing = titleElement.getAttribute('contenteditable') === 'true';
        
        if (isEditing) {
            // 保存
            titleElement.setAttribute('contenteditable', 'false');
            titleElement.classList.remove('editing');
            editBtn.innerHTML = '<i class="fas fa-edit"></i>';
            editBtn.title = '编辑标题';
            
            // 保存到服务器
            saveTitleChange(titleElement.dataset.artworkId, titleElement.textContent.trim());
        } else {
            // 开始编辑
            titleElement.setAttribute('contenteditable', 'true');
            titleElement.classList.add('editing');
            titleElement.focus();
            editBtn.innerHTML = '<i class="fas fa-save"></i>';
            editBtn.title = '保存标题';
            
            // 选中文本
            const range = document.createRange();
            range.selectNodeContents(titleElement);
            const sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
        }
    });
    
    // 按Enter键保存
    titleElement.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            editBtn.click();
        }
    });
}

// 保存标题修改
async function saveTitleChange(artworkId, newTitle) {
    if (!artworkId || !newTitle) return;
    
    try {
        const response = await fetch(`/auth/artwork/${artworkId}/update-title`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title: newTitle })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('标题已更新');
            // 更新卡片上的标题
            const card = document.querySelector(`[data-artwork-id="${artworkId}"]`);
            if (card) {
                const cardTitle = card.querySelector('.artwork-title');
                if (cardTitle) {
                    cardTitle.textContent = newTitle;
                }
                card.dataset.artworkTitle = newTitle;
            }
        } else {
            alert('保存失败：' + (result.message || '未知错误'));
        }
    } catch (error) {
        console.error('保存标题失败:', error);
        alert('保存失败，请重试');
    }
}

// 图片操作处理函数
function handleImageAction(action, artworkId, imageUrl) {
    if (!artworkId) {
        alert('无法获取作品ID');
        return;
    }
    
    // 获取sessionId
    const titleElement = document.getElementById('modalArtworkTitle');
    const modal = document.getElementById('artworkModal');
    const sessionId = modal?.dataset.sessionId;
    
    // 构建URL参数
    let url = '/create?';
    const params = new URLSearchParams();
    
    params.append('reference', imageUrl);
    params.append('artwork_id', artworkId);
    
    if (sessionId) {
        params.append('session_id', sessionId);
    }
    
    switch (action) {
        case 'continue':
            // 继续创作 - 调整参数后重新生成
            params.append('mode', 'adjust');
            break;
        case 'generate-model':
            // 生成3D模型 - 先调整参数
            params.append('mode', 'model');
            params.append('target', '3d');
            break;
        case 'generate-video':
            // 生成视频 - 先调整参数
            params.append('mode', 'video');
            params.append('target', 'video');
            break;
    }
    
    window.location.href = url + params.toString();
}

// 右键菜单功能
let currentContextImage = null;

function setupContextMenu() {
    const contextMenu = document.getElementById('imageContextMenu');
    if (!contextMenu) return;
    
    // 隐藏菜单（点击页面其他地方）
    document.addEventListener('click', function() {
        contextMenu.style.display = 'none';
    });
    
    // 菜单项点击事件
    contextMenu.querySelectorAll('.context-menu-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.stopPropagation();
            const action = this.dataset.action;
            handleContextMenuAction(action, currentContextImage);
            contextMenu.style.display = 'none';
        });
    });
}

// 显示右键菜单
function showContextMenu(e, imageElement) {
    e.preventDefault();
    e.stopPropagation();
    
    const contextMenu = document.getElementById('imageContextMenu');
    if (!contextMenu) return;
    
    currentContextImage = imageElement;
    
    // 定位菜单
    contextMenu.style.display = 'block';
    contextMenu.style.left = e.pageX + 'px';
    contextMenu.style.top = e.pageY + 'px';
}

// 处理右键菜单操作
function handleContextMenuAction(action, imageElement) {
    if (!imageElement) return;
    
    const imageSrc = imageElement.src;
    const titleElement = document.getElementById('modalArtworkTitle');
    const artworkId = titleElement?.dataset.artworkId;
    
    switch (action) {
        case 'continue':
            // 跳转到创作页面，带上图片作为参考
            window.location.href = `/create?reference=${encodeURIComponent(imageSrc)}`;
            break;
            
        case 'generate-model':
            // 生成3D模型
            if (artworkId) {
                generateModel(artworkId, imageSrc);
            } else {
                alert('无法生成模型：缺少作品ID');
            }
            break;
            
        case 'generate-video':
            // 生成视频
            if (artworkId) {
                generateVideo(artworkId, imageSrc);
            } else {
                alert('无法生成视频：缺少作品ID');
            }
            break;
    }
}

// 生成3D模型
async function generateModel(artworkId, imageSrc) {
    if (!confirm('确定要为这张图片生成3D模型吗？此过程可能需要几分钟。')) {
        return;
    }
    
    try {
        const response = await fetch(`/auth/artwork/${artworkId}/generate-model`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image_url: imageSrc })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('3D模型生成已开始，完成后会自动显示');
            // 可以添加进度显示或轮询状态
        } else {
            alert('生成失败：' + (result.message || '未知错误'));
        }
    } catch (error) {
        console.error('生成3D模型失败:', error);
        alert('生成失败，请重试');
    }
}

// 生成视频
async function generateVideo(artworkId, imageSrc) {
    if (!confirm('确定要为这张图片生成视频吗？此过程可能需要几分钟。')) {
        return;
    }
    
    try {
        const response = await fetch(`/auth/artwork/${artworkId}/generate-video`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image_url: imageSrc })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('视频生成已开始，完成后会自动显示');
            // 可以添加进度显示或轮询状态
        } else {
            alert('生成失败：' + (result.message || '未知错误'));
        }
    } catch (error) {
        console.error('生成视频失败:', error);
        alert('生成失败，请重试');
    }
}