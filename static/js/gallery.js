// 作品展示页面JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeGallery();
    createPlaceholderImages();
});

function initializeGallery() {
    // 设置筛选按钮事件
    setupFilterButtons();
    
    // 设置加载更多按钮
    setupLoadMoreButton();
    
    // 设置作品卡片交互
    setupArtworkInteractions();
}

function setupFilterButtons() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const artworkItems = document.querySelectorAll('.artwork-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 移除所有按钮的active类
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // 给当前按钮添加active类
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            
            // 筛选作品
            artworkItems.forEach(item => {
                if (filter === 'all' || item.getAttribute('data-category') === filter) {
                    item.style.display = 'block';
                    item.classList.add('fade-in');
                } else {
                    item.style.display = 'none';
                    item.classList.remove('fade-in');
                }
            });
        });
    });
}

function setupLoadMoreButton() {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    
    // 如果页面中没有加载更多按钮，则跳过设置
    if (!loadMoreBtn) {
        return;
    }
    
    loadMoreBtn.addEventListener('click', function() {
        // 模拟加载更多作品
        loadMoreArtworks();
    });
}

function loadMoreArtworks() {
    const galleryGrid = document.getElementById('galleryGrid');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    
    // 如果按钮不存在，则退出
    if (!loadMoreBtn || !galleryGrid) {
        return;
    }
    
    // 显示加载状态
    loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 正在加载...';
    loadMoreBtn.disabled = true;
    
    // 模拟网络延迟
    setTimeout(() => {
        // 创建新的作品项目
        const newArtworks = createSampleArtworks();
        
        newArtworks.forEach(artwork => {
            galleryGrid.appendChild(artwork);
        });
        
        // 恢复按钮状态
        loadMoreBtn.innerHTML = '<i class="fas fa-plus"></i> 加载更多作品';
        loadMoreBtn.disabled = false;
        
        // 添加动画效果
        const newItems = galleryGrid.querySelectorAll('.gallery-item:not(.loaded)');
        newItems.forEach((item, index) => {
            setTimeout(() => {
                item.classList.add('fade-in', 'loaded');
            }, index * 100);
        });
        
    }, 1500);
}

function createSampleArtworks() {
    const sampleData = [
        {
            category: 'animals',
            title: '快乐小狗',
            artist: '小丽',
            age: 9,
            date: '2024年3月11日',
            likes: 23,
            views: 67
        },
        {
            category: 'characters',
            title: '魔法师',
            artist: '小强',
            age: 12,
            date: '2024年3月10日',
            likes: 45,
            views: 112
        },
        {
            category: 'nature',
            title: '彩虹桥',
            artist: '小美',
            age: 11,
            date: '2024年3月9日',
            likes: 38,
            views: 95
        }
    ];
    
    return sampleData.map(data => createArtworkElement(data));
}

function createArtworkElement(data) {
    const galleryItem = document.createElement('div');
    galleryItem.className = 'gallery-item';
    galleryItem.setAttribute('data-category', data.category);
    
    galleryItem.innerHTML = `
        <div class="artwork-showcase">
            <div class="artwork-step">
                <h4>原始简笔画</h4>
                <div class="placeholder-img" data-text="简笔画"></div>
            </div>
            <div class="artwork-step">
                <h4>AI上色效果</h4>
                <div class="placeholder-img" data-text="上色图"></div>
            </div>
            <div class="artwork-step">
                <h4>手办风格</h4>
                <div class="placeholder-img" data-text="手办图"></div>
            </div>
        </div>
        <div class="artwork-info">
            <h3>${data.title}</h3>
            <p class="artist-info">
                <i class="fas fa-user-circle"></i>
                ${data.artist}，${data.age}岁
            </p>
            <p class="creation-date">
                <i class="fas fa-calendar"></i>
                ${data.date}
            </p>
            <div class="artwork-stats">
                <span class="likes">
                    <i class="fas fa-heart"></i>
                    ${data.likes}个赞
                </span>
                <span class="views">
                    <i class="fas fa-eye"></i>
                    ${data.views}次浏览
                </span>
            </div>
        </div>
    `;
    
    return galleryItem;
}

function setupArtworkInteractions() {
    // 支持多个页面的不同网格ID
    const galleryGrid = document.getElementById('galleryGrid') || 
                       document.getElementById('myArtworksGrid') ||
                       document.querySelector('.gallery-grid');
    
    if (!galleryGrid) {
        console.error('Gallery grid not found!');
        return;
    }
    
    // 使用事件委托处理作品卡片点击
    galleryGrid.addEventListener('click', function(e) {
        // 忽略来自导航栏的点击
        if (e.target.closest('.nav-menu') || e.target.closest('.nav-toggle') || e.target.closest('.navbar')) {
            console.log('🚫 Gallery: 忽略导航栏内的点击');
            return;
        }
        
        const artworkItem = e.target.closest('.artwork-item');
        if (artworkItem) {
            showArtworkModal(artworkItem);
        }
    });
    
    // 设置点赞功能
    galleryGrid.addEventListener('click', function(e) {
        // 忽略来自导航栏的点击
        if (e.target.closest('.nav-menu') || e.target.closest('.nav-toggle') || e.target.closest('.navbar')) {
            return;
        }
        
        if (e.target.closest('.likes')) {
            e.stopPropagation();
            handleLike(e.target.closest('.likes'));
        }
    });
}

function handleLike(likeElement) {
    const heartIcon = likeElement.querySelector('i');
    const likeText = likeElement.childNodes[2]; // 文本节点
    
    // 切换点赞状态
    if (heartIcon.classList.contains('fas')) {
        heartIcon.classList.remove('fas');
        heartIcon.classList.add('far');
        
        // 减少点赞数
        const currentLikes = parseInt(likeText.textContent.match(/\d+/)[0]);
        likeText.textContent = `${currentLikes - 1}个赞`;
    } else {
        heartIcon.classList.remove('far');
        heartIcon.classList.add('fas');
        
        // 增加点赞数
        const currentLikes = parseInt(likeText.textContent.match(/\d+/)[0]);
        likeText.textContent = `${currentLikes + 1}个赞`;
        
        // 添加点赞动画
        heartIcon.style.animation = 'heartbeat 0.6s ease';
        setTimeout(() => {
            heartIcon.style.animation = '';
        }, 600);
    }
}

function shareArtwork(galleryItem) {
    const title = galleryItem.querySelector('h3').textContent;
    const artist = galleryItem.querySelector('.artist-info').textContent.trim();
    
    if (navigator.share) {
        navigator.share({
            title: `AI创意工坊 - ${title}`,
            text: `看看${artist}创作的《${title}》！`,
            url: window.location.href
        });
    } else {
        // 复制链接到剪贴板
        navigator.clipboard.writeText(window.location.href).then(() => {
            showMessage('链接已复制到剪贴板！', 'success');
        });
    }
}

function downloadArtwork(galleryItem) {
    showMessage('下载功能开发中，敬请期待！', 'info');
}

function createPlaceholderImages() {
    // 为占位图片添加样式和内容
    const style = document.createElement('style');
    style.textContent = `
        .placeholder-img {
            width: 100%;
            height: 150px;
            background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 14px;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
        }
        
        .placeholder-img::before {
            content: attr(data-text);
            position: absolute;
            z-index: 1;
        }
        
        .placeholder-img::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        @keyframes heartbeat {
            0% { transform: scale(1); }
            25% { transform: scale(1.2); color: #ff6b6b; }
            50% { transform: scale(1); }
            75% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .modal-content {
            background: white;
            border-radius: 15px;
            max-width: 800px;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid #eee;
        }
        
        .close-modal {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #666;
            transition: color 0.3s ease;
        }
        
        .close-modal:hover {
            color: #333;
        }
        
        .modal-body {
            padding: 20px;
        }
        
        .modal-showcase {
            margin-bottom: 20px;
        }
        
        .modal-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .action-btn {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 20px;
            cursor: pointer;
            transition: background 0.3s ease;
            font-size: 0.9rem;
        }
        
        .action-btn:hover {
            background: var(--primary-color-dark);
        }
        
        .action-btn i {
            margin-right: 5px;
        }
        
        .inspiration-section {
            background: white;
            padding: 4rem 0;
        }
        
        .inspiration-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        
        .inspiration-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .inspiration-card:hover {
            transform: translateY(-5px);
        }
        
        .inspiration-card i {
            font-size: 3rem;
            color: var(--primary-color);
            margin-bottom: 1rem;
        }
        
        .inspiration-card h3 {
            margin-bottom: 1rem;
            color: #333;
        }
        
        .inspiration-card p {
            color: #666;
            line-height: 1.6;
        }
        
        .gallery-hero {
            background: var(--page-gradient);
            color: white;
            padding: 6rem 0 4rem;
            text-align: center;
        }
        
        .gallery-title {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .gallery-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .gallery-content {
            background: white;
            padding: 4rem 0;
        }
        
        .gallery-filters {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 3rem;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            background: transparent;
            border: 2px solid var(--primary-color);
            color: var(--primary-color);
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .filter-btn:hover,
        .filter-btn.active {
            background: var(--primary-color);
            color: white;
        }
        
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .gallery-item {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .gallery-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        }
        
        .artwork-showcase {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            padding: 1rem;
        }
        
        .artwork-step h4 {
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            color: #666;
            text-align: center;
        }
        
        .artwork-info {
            padding: 1.5rem;
            border-top: 1px solid #e0e0e0;
        }
        
        .artwork-info h3 {
            margin-bottom: 1rem;
            color: #333;
            font-size: 1.3rem;
        }
        
        .artist-info,
        .creation-date {
            margin-bottom: 0.5rem;
            color: #666;
            font-size: 0.9rem;
        }
        
        .artist-info i,
        .creation-date i {
            margin-right: 0.5rem;
            color: var(--primary-color);
        }
        
        .artwork-stats {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .likes,
        .views {
            font-size: 0.9rem;
            color: #666;
            cursor: pointer;
            transition: color 0.3s ease;
        }
        
        .likes:hover {
            color: #ff6b6b;
        }
        
        .likes i,
        .views i {
            margin-right: 0.3rem;
        }
        
        .gallery-actions {
            text-align: center;
        }
        
        .load-more-btn {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1.1rem;
        }
        
        .load-more-btn:hover:not(:disabled) {
            background: var(--primary-color-dark);
            transform: translateY(-2px);
        }
        
        .load-more-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        .load-more-btn i {
            margin-right: 0.5rem;
        }
        
        @media (max-width: 768px) {
            .gallery-title {
                font-size: 2rem;
            }
            
            .gallery-grid {
                grid-template-columns: 1fr;
            }
            
            .artwork-showcase {
                grid-template-columns: 1fr;
            }
            
            .inspiration-grid {
                grid-template-columns: 1fr;
            }
            
            .modal-content {
                margin: 20px;
                max-width: calc(100vw - 40px);
            }
        }
    `;
    document.head.appendChild(style);
    
    // 为现有的占位图片添加默认文本
    const placeholderImages = document.querySelectorAll('img.placeholder-img');
    placeholderImages.forEach(img => {
        const div = document.createElement('div');
        div.className = 'placeholder-img';
        div.setAttribute('data-text', '示例图片');
        img.parentNode.replaceChild(div, img);
    });
}

function showMessage(message, type = 'info') {
    // 创建消息元素
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type}`;
    messageEl.textContent = message;
    
    // 添加样式
    messageEl.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'error' ? '#ff6b6b' : type === 'success' ? '#4CAF50' : 'var(--primary-color)'};
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(messageEl);
    
    // 3秒后自动移除
    setTimeout(() => {
        messageEl.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (document.body.contains(messageEl)) {
                document.body.removeChild(messageEl);
            }
        }, 300);
    }, 3000);
}

// 用户作品点赞功能
async function likeArtwork(artworkId) {
    try {
        const response = await fetch(`/vote-artwork/${artworkId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                vote_type: 'like'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 更新点赞数显示
            const modalLikesElement = document.getElementById(`modal-likes-${artworkId}`);
            if (modalLikesElement) {
                modalLikesElement.textContent = result.vote_count;
                
                // 添加点赞动画
                const heartIcon = modalLikesElement.closest('.modal-likes').querySelector('i');
                if (heartIcon) {
                    heartIcon.style.animation = 'heartBeat 0.6s ease';
                    setTimeout(() => {
                        heartIcon.style.animation = '';
                    }, 600);
                }
            }
            
            showMessage('点赞成功！', 'success');
        } else {
            showMessage(result.error || '点赞失败', 'error');
        }
    } catch (error) {
        console.error('点赞失败:', error);
        showMessage('点赞失败，请稍后重试', 'error');
    }
}

// 增加浏览次数
async function incrementViewCount(artworkId) {
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

// 注意: 模态框功能已移至 artwork-modal.js 统一管理
// showArtworkModal, closeArtworkModal, showImageModal, showModelModal 等函数
// 都在 artwork-modal.js 中定义，两个页面共享同一套代码

// 3D模型控制函数
function rotateModel() {
    if (modelViewer) {
        console.log('开始旋转模型');
        modelViewer.rotateModel(2000); // 2秒旋转
    }
}

function resetView() {
    if (modelViewer) {
        console.log('重置视角');
        modelViewer.resetView();
        
        const modelInfo = document.getElementById('modelInfo');
        if (modelInfo) {
            modelInfo.textContent = '视角已重置';
            setTimeout(() => {
                modelInfo.textContent = '使用鼠标拖拽旋转，滚轮缩放';
            }, 2000);
        }
    }
}

function toggleWireframe() {
    if (modelViewer) {
        const isWireframe = modelViewer.toggleWireframe();
        console.log('切换线框模式:', isWireframe);
        
        // 更新按钮状态 - 使用事件目标
        const button = event.target;
        if (button) {
            if (isWireframe) {
                button.classList.add('wireframe-active');
                button.innerHTML = '<i class="fas fa-border-all"></i> 实体';
            } else {
                button.classList.remove('wireframe-active');
                button.innerHTML = '<i class="fas fa-border-none"></i> 线框';
            }
        }
        
        const modelInfo = document.getElementById('modelInfo');
        if (modelInfo) {
            modelInfo.textContent = isWireframe ? '已切换到线框模式' : '已切换到实体模式';
            setTimeout(() => {
                modelInfo.textContent = '使用鼠标拖拽旋转，滚轮缩放';
            }, 2000);
        }
    }
}

// 切换点云模式
function togglePointCloud() {
    if (modelViewer) {
        const hasPointCloud = modelViewer.togglePointCloud();
        console.log('切换点云模式:', hasPointCloud);
        
        // 更新按钮状态
        const button = event.target;
        if (button) {
            if (hasPointCloud) {
                button.classList.add('material-active');
                button.innerHTML = '<i class="fas fa-cube"></i> 实体';
            } else {
                button.classList.remove('material-active');
                button.innerHTML = '<i class="fas fa-braille"></i> 点云';
            }
        }
        
        const modelInfo = document.getElementById('modelInfo');
        if (modelInfo) {
            modelInfo.textContent = hasPointCloud ? '已切换到点云模式' : '已切换到实体模式';
            setTimeout(() => {
                modelInfo.textContent = '使用鼠标拖拽旋转，滚轮缩放';
            }, 2000);
        }
    }
}

// 切换材质类型
function switchMaterial(materialType) {
    if (modelViewer) {
        modelViewer.switchMaterial(materialType);
        console.log('切换材质类型:', materialType);
        
        // 更新按钮状态
        const allMaterialBtns = document.querySelectorAll('.controls-section:nth-child(2) .model-btn');
        allMaterialBtns.forEach(btn => btn.classList.remove('material-active'));
        
        if (event && event.target) {
            event.target.classList.add('material-active');
        }
        
        const modelInfo = document.getElementById('modelInfo');
        if (modelInfo) {
            const materialNames = {
                'original': '原始材质',
                'lambert': '朗伯材质',
                'phong': '冯氏材质',
                'standard': '标准材质'
            };
            modelInfo.textContent = `已切换到${materialNames[materialType] || '未知材质'}`;
            setTimeout(() => {
                modelInfo.textContent = '使用鼠标拖拽旋转，滚轮缩放';
            }, 2000);
        }
    }
}

// 切换背景显示
function toggleBackground() {
    if (modelViewer) {
        const hasBackground = modelViewer.toggleBackground();
        console.log('切换背景显示:', hasBackground);
        
        // 更新按钮状态
        const button = event.target;
        if (button) {
            if (hasBackground) {
                button.classList.add('material-active');
                button.innerHTML = '<i class="fas fa-eye-slash"></i> 隐藏';
            } else {
                button.classList.remove('material-active');
                button.innerHTML = '<i class="fas fa-image"></i> 背景';
            }
        }
        
        const modelInfo = document.getElementById('modelInfo');
        if (modelInfo) {
            modelInfo.textContent = hasBackground ? '背景已显示' : '背景已隐藏';
            setTimeout(() => {
                modelInfo.textContent = '使用鼠标拖拽旋转，滚轮缩放';
            }, 2000);
        }
    }
}

// 双击切换图片显示模式
function toggleImageMode(img) {
    event.stopPropagation();
    
    // 双击始终切换到1:1原始大小
    setImageMode(img, 'original');
}

// 设置图片显示模式
function setImageMode(img, mode) {
    const container = img.closest('.image-overlay-content');
    
    img.dataset.mode = mode;
    
    // 清除所有模式类
    img.classList.remove('thumbnail-mode', 'fit-mode', 'original-mode');
    
    if (mode === 'thumbnail') {
        // 缩略图模式
        img.classList.add('thumbnail-mode');
        if (container) container.classList.remove('scrollable');
    } else if (mode === 'fit') {
        // 适应窗口模式
        img.classList.add('fit-mode');
        if (container) container.classList.remove('scrollable');
    } else if (mode === 'original') {
        // 1:1 原始尺寸模式
        img.classList.add('original-mode');
        if (container) container.classList.add('scrollable');
    }
}

// 已移除 backToArtworkDetails 函数，现在使用 closeImageOverlay

// 点击模态框背景关闭
document.addEventListener('DOMContentLoaded', function() {
    const artworkModal = document.getElementById('artworkModal');
    if (artworkModal) {
        // 点击背景关闭
        artworkModal.addEventListener('click', function(event) {
            if (event.target === artworkModal) {
                closeArtworkModal();
            }
        });
        
        // 点击关闭按钮关闭
        const closeBtn = artworkModal.querySelector('.artwork-modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function(event) {
                event.stopPropagation();
                closeArtworkModal();
            });
        }
    }
    
    // ESC键关闭模态框
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const modal = document.getElementById('artworkModal');
            const modelOverlay = document.getElementById('modelOverlay');
            
            if (modal && modal.style.display !== 'none') {
                closeArtworkModal();
            } else if (modelOverlay && modelOverlay.classList.contains('visible')) {
                closeModelModal();
            }
        }
    });
});
// 切换Gallery 3D模型全屏
function toggleGalleryFullscreen() {
    const modelOverlay = document.getElementById('modelOverlay');
    if (!modelOverlay) {
        console.error('模型容器未找到');
        return;
    }
    
    const fullscreenBtn = document.getElementById('galleryFullscreenBtn');
    const icon = fullscreenBtn?.querySelector('i');
    
    if (!document.fullscreenElement) {
        // 进入全屏
        if (modelOverlay.requestFullscreen) {
            modelOverlay.requestFullscreen();
        } else if (modelOverlay.webkitRequestFullscreen) {
            modelOverlay.webkitRequestFullscreen();
        } else if (modelOverlay.msRequestFullscreen) {
            modelOverlay.msRequestFullscreen();
        }
        
        // 更新按钮
        if (icon) {
            icon.classList.remove('fa-expand');
            icon.classList.add('fa-compress');
        }
        if (fullscreenBtn) {
            fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i> 退出全屏';
        }
        
        // 调整模型查看器尺寸
        if (modelViewer) {
            setTimeout(() => {
                modelViewer.onWindowResize();
            }, 100);
        }
    } else {
        // 退出全屏
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
        
        // 更新按钮
        if (icon) {
            icon.classList.remove('fa-compress');
            icon.classList.add('fa-expand');
        }
        if (fullscreenBtn) {
            fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i> 全屏';
        }
        
        // 调整模型查看器尺寸
        if (modelViewer) {
            setTimeout(() => {
                modelViewer.onWindowResize();
            }, 100);
        }
    }
}

// 监听全屏状态变化
document.addEventListener('fullscreenchange', handleGalleryFullscreenChange);
document.addEventListener('webkitfullscreenchange', handleGalleryFullscreenChange);
document.addEventListener('mozfullscreenchange', handleGalleryFullscreenChange);
document.addEventListener('MSFullscreenChange', handleGalleryFullscreenChange);

function handleGalleryFullscreenChange() {
    const fullscreenBtn = document.getElementById('galleryFullscreenBtn');
    if (!fullscreenBtn) return;
    
    const icon = fullscreenBtn.querySelector('i');
    
    if (!document.fullscreenElement) {
        // 已退出全屏
        if (icon) {
            icon.classList.remove('fa-compress');
            icon.classList.add('fa-expand');
        }
        fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i> 全屏';
        
        // 调整模型查看器尺寸
        if (modelViewer) {
            setTimeout(() => {
                modelViewer.onWindowResize();
            }, 100);
        }
    }
}
