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
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 移除所有按钮的active类
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // 给当前按钮添加active类
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            
            // 筛选作品
            galleryItems.forEach(item => {
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
    
    loadMoreBtn.addEventListener('click', function() {
        // 模拟加载更多作品
        loadMoreArtworks();
    });
}

function loadMoreArtworks() {
    const galleryGrid = document.getElementById('galleryGrid');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    
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
    const galleryGrid = document.getElementById('galleryGrid');
    
    // 使用事件委托处理作品卡片点击
    galleryGrid.addEventListener('click', function(e) {
        const galleryItem = e.target.closest('.gallery-item');
        if (galleryItem) {
            showArtworkModal(galleryItem);
        }
    });
    
    // 设置点赞功能
    galleryGrid.addEventListener('click', function(e) {
        if (e.target.closest('.likes')) {
            e.stopPropagation();
            handleLike(e.target.closest('.likes'));
        }
    });
}

function showArtworkModal(galleryItem) {
    // 创建模态框
    const modal = document.createElement('div');
    modal.className = 'artwork-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>${galleryItem.querySelector('h3').textContent}</h2>
                <button class="close-modal">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="modal-showcase">
                    ${galleryItem.querySelector('.artwork-showcase').innerHTML}
                </div>
                <div class="modal-info">
                    ${galleryItem.querySelector('.artwork-info').innerHTML}
                    <div class="modal-actions">
                        <button class="action-btn share-btn">
                            <i class="fas fa-share"></i>
                            分享作品
                        </button>
                        <button class="action-btn download-btn">
                            <i class="fas fa-download"></i>
                            下载图片
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 添加模态框样式
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(modal);
    
    // 触发动画
    setTimeout(() => {
        modal.style.opacity = '1';
    }, 10);
    
    // 设置关闭事件
    modal.querySelector('.close-modal').addEventListener('click', () => {
        closeModal(modal);
    });
    
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal(modal);
        }
    });
    
    // 设置操作按钮事件
    modal.querySelector('.share-btn').addEventListener('click', () => {
        shareArtwork(galleryItem);
    });
    
    modal.querySelector('.download-btn').addEventListener('click', () => {
        downloadArtwork(galleryItem);
    });
}

function closeModal(modal) {
    modal.style.opacity = '0';
    setTimeout(() => {
        document.body.removeChild(modal);
    }, 300);
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
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 20px;
            cursor: pointer;
            transition: background 0.3s ease;
            font-size: 0.9rem;
        }
        
        .action-btn:hover {
            background: #5a6fd8;
        }
        
        .action-btn i {
            margin-right: 5px;
        }
        
        .inspiration-section {
            background: #f8f9ff;
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
            color: #667eea;
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            border: 2px solid #667eea;
            color: #667eea;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .filter-btn:hover,
        .filter-btn.active {
            background: #667eea;
            color: white;
        }
        
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .gallery-item {
            background: #f8f9ff;
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
            color: #667eea;
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
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1.1rem;
        }
        
        .load-more-btn:hover:not(:disabled) {
            background: #5a6fd8;
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
        background: ${type === 'error' ? '#ff6b6b' : type === 'success' ? '#4CAF50' : '#667eea'};
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
        const response = await fetch(`/like-artwork/${artworkId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 更新点赞数显示
            const likesElement = document.getElementById(`likes-${artworkId}`);
            if (likesElement) {
                likesElement.textContent = result.likes;
                
                // 添加点赞动画
                const heartIcon = likesElement.parentElement.querySelector('i');
                heartIcon.style.animation = 'heartBeat 0.6s ease';
                setTimeout(() => {
                    heartIcon.style.animation = '';
                }, 600);
                
                // 添加点赞样式
                likesElement.parentElement.classList.add('liked');
                setTimeout(() => {
                    likesElement.parentElement.classList.remove('liked');
                }, 600);
            }
            
            showMessage('点赞成功！', 'success');
        } else {
            showMessage('点赞失败，请稍后重试', 'error');
        }
        
    } catch (error) {
        console.error('点赞失败:', error);
        showMessage('点赞失败，请稍后重试', 'error');
    }
}

// 作品详情模态框功能
function showArtworkModal(element) {
    // 阻止事件冒泡，防止意外触发
    event.stopPropagation();
    
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
        views: element.dataset.artworkViews
    };
    
    // 设置模态框标题
    document.getElementById('modalArtworkTitle').textContent = artworkData.title;
    
    // 构建作品展示区域
    const showcase = document.getElementById('modalArtworkShowcase');
    showcase.innerHTML = '';
    
    // 原始简笔画
    if (artworkData.originalImage && artworkData.originalImage.trim() !== '' && artworkData.originalImage !== 'null') {
        const originalStep = document.createElement('div');
        originalStep.className = 'artwork-detail-step';
        originalStep.innerHTML = `
            <h4>原始简笔画</h4>
            <img src="/static/${artworkData.originalImage}" alt="原始简笔画" 
                 onclick="showImageModal(this.src, '原始简笔画')" 
                 style="cursor: pointer;" 
                 title="点击查看大图"
                 onerror="this.parentElement.style.display='none'">
        `;
        showcase.appendChild(originalStep);
    } else {
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
        const generatedStep = document.createElement('div');
        generatedStep.className = 'artwork-detail-step';
        generatedStep.innerHTML = `
            <h4>AI生成效果</h4>
            <img src="/static/${artworkData.generatedImage}" alt="AI生成效果" 
                 onclick="showImageModal(this.src, 'AI生成效果')" 
                 style="cursor: pointer;" 
                 title="点击查看大图"
                 onerror="this.parentElement.style.display='none'">
        `;
        showcase.appendChild(generatedStep);
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
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden'; // 防止背景滚动
    
    // 添加动画效果
    setTimeout(() => {
        modal.querySelector('.artwork-modal-content').style.transform = 'scale(1)';
        modal.querySelector('.artwork-modal-content').style.opacity = '1';
    }, 10);
}

function closeArtworkModal() {
    const modal = document.getElementById('artworkModal');
    const content = modal.querySelector('.artwork-modal-content');
    
    // 添加关闭动画
    content.style.transform = 'scale(0.9)';
    content.style.opacity = '0';
    
    setTimeout(() => {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // 恢复背景滚动
        
        // 重置模态框状态
        content.classList.remove('enlarged-mode');
        if (content.dataset.originalContent) {
            delete content.dataset.originalContent;
        }
        
        // 重置动画状态
        content.style.transform = 'scale(0.9)';
        content.style.opacity = '0';
    }, 300);
}

// 在当前模态框上方叠加图片
function showImageModal(imageSrc, title) {
    event.stopPropagation();
    
    // 创建图片叠加层
    const imageOverlay = document.createElement('div');
    imageOverlay.id = 'imageOverlay';
    imageOverlay.className = 'image-overlay';
    
    imageOverlay.innerHTML = `
        <div class="image-overlay-backdrop"></div>
        <div class="image-overlay-content">
            <img src="${imageSrc}" alt="${title}" class="overlay-image thumbnail-mode" 
                 ondblclick="toggleImageMode(this)" 
                 onclick="handleImageClick(this)"
                 data-mode="thumbnail">
        </div>
    `;
    
    // 添加到当前模态窗口内
    const artworkModal = document.getElementById('artworkModal');
    artworkModal.appendChild(imageOverlay);
    
    // 点击背景关闭叠加层
    imageOverlay.addEventListener('click', function(e) {
        // 如果点击的不是图片本身，就关闭叠加层
        if (e.target === imageOverlay || 
            e.target.classList.contains('image-overlay-backdrop') ||
            e.target.classList.contains('image-overlay-content')) {
            closeImageOverlay();
        }
    });
    
    // 显示动画
    setTimeout(() => {
        imageOverlay.classList.add('visible');
    }, 10);
}

// 处理图片点击事件
function handleImageClick(img) {
    event.stopPropagation();
    
    const currentMode = img.dataset.mode;
    
    // 单击逻辑：缩略图 → 窗口，窗口 → 缩略图，原始 → 缩略图
    if (currentMode === 'thumbnail') {
        setImageMode(img, 'fit');
    } else {
        setImageMode(img, 'thumbnail');
    }
}

// 关闭图片叠加层
function closeImageOverlay() {
    const imageOverlay = document.getElementById('imageOverlay');
    if (imageOverlay) {
        imageOverlay.classList.remove('visible');
        setTimeout(() => {
            imageOverlay.remove();
        }, 300);
    }
}

// 显示3D模型模态框
function showModelModal(modelSrc, title) {
    event.stopPropagation();
    
    const modelOverlay = document.getElementById('modelOverlay');
    const modelTitle = document.getElementById('modelTitle');
    const modelPlaceholder = modelOverlay.querySelector('.model-placeholder');
    
    if (modelOverlay && modelTitle) {
        modelTitle.textContent = title;
        
        // 更新模型信息
        const modelDescription = modelPlaceholder.querySelector('p');
        const modelInfo = modelPlaceholder.querySelector('.model-info');
        
        if (modelDescription) {
            modelDescription.textContent = `正在加载模型: ${modelSrc.split('/').pop()}`;
        }
        
        if (modelInfo) {
            modelInfo.textContent = `模型文件: ${modelSrc}`;
        }
        
        // 添加旋转动画
        const modelIcon = modelPlaceholder.querySelector('i');
        if (modelIcon) {
            modelIcon.style.animation = 'rotate 2s linear infinite';
        }
        
        modelOverlay.classList.add('visible');
        
        // 模拟加载过程
        setTimeout(() => {
            if (modelDescription) {
                modelDescription.textContent = `模型已加载: ${modelSrc.split('/').pop()}`;
            }
            if (modelIcon) {
                modelIcon.style.animation = 'none';
            }
        }, 2000);
        
        console.log('加载3D模型:', modelSrc);
    }
}

// 关闭3D模型叠加层
function closeModelOverlay() {
    const modelOverlay = document.getElementById('modelOverlay');
    if (modelOverlay) {
        modelOverlay.classList.remove('visible');
    }
}

// 3D模型控制函数
function rotateModel() {
    const modelIcon = document.querySelector('#modelOverlay .fas.fa-cube');
    const modelDescription = document.querySelector('#modelOverlay .model-placeholder p');
    
    if (modelIcon) {
        modelIcon.style.animation = 'rotate 1s linear 1';
        setTimeout(() => {
            modelIcon.style.animation = 'none';
        }, 1000);
    }
    
    if (modelDescription) {
        modelDescription.textContent = '模型正在旋转...';
        setTimeout(() => {
            modelDescription.textContent = '旋转完成';
        }, 1000);
    }
    
    console.log('旋转模型');
}

function resetView() {
    const modelDescription = document.querySelector('#modelOverlay .model-placeholder p');
    
    if (modelDescription) {
        modelDescription.textContent = '视角已重置到默认位置';
        setTimeout(() => {
            modelDescription.textContent = '模型已加载完成';
        }, 2000);
    }
    
    console.log('重置视角');
}

function toggleWireframe() {
    const wireframeBtn = document.querySelector('#modelOverlay .model-btn:nth-child(3)');
    const modelDescription = document.querySelector('#modelOverlay .model-placeholder p');
    
    if (wireframeBtn) {
        const isWireframe = wireframeBtn.classList.contains('wireframe-active');
        
        if (isWireframe) {
            wireframeBtn.classList.remove('wireframe-active');
            wireframeBtn.innerHTML = '<i class="fas fa-border-none"></i> 线框';
            if (modelDescription) {
                modelDescription.textContent = '已切换到实体模式';
            }
        } else {
            wireframeBtn.classList.add('wireframe-active');
            wireframeBtn.innerHTML = '<i class="fas fa-border-all"></i> 实体';
            if (modelDescription) {
                modelDescription.textContent = '已切换到线框模式';
            }
        }
        
        setTimeout(() => {
            if (modelDescription) {
                modelDescription.textContent = '模型已加载完成';
            }
        }, 2000);
    }
    
    console.log('切换线框模式');
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
        artworkModal.addEventListener('click', function(event) {
            if (event.target === artworkModal) {
                closeArtworkModal();
            }
        });
    }
});