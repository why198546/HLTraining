// 无限画布 JavaScript
console.log('=== Canvas Infinite.js 已加载 ===');

// 全局状态
let canvasState = {
    // 画布变换
    translateX: 0,
    translateY: 0,
    scale: 1,
    
    // 拖拽状态
    isDraggingCanvas: false,
    isDraggingImage: false,
    isResizing: false,
    dragStartX: 0,
    dragStartY: 0,
    dragImageId: null,
    
    // 缩放状态
    resizeImageId: null,
    resizeDirection: null,
    resizeStartX: 0,
    resizeStartY: 0,
    resizeStartWidth: 0,
    resizeStartHeight: 0,
    resizeStartImageX: 0,
    resizeStartImageY: 0,
    resizeAnimationFrame: null,
    
    // 图片数据
    images: [], // { id, url, prompt, x, y, width, height }
    selectedImages: [], // 选中的图片 ID 数组
    
    // 生成状态
    isGenerating: false,
    
    // 命令模式
    commandMode: false,
    currentCommand: null
};

// DOM 元素
const viewport = document.getElementById('canvasViewport');
const container = document.querySelector('.infinite-canvas-container');
const chatForm = document.getElementById('chatForm');
const promptInput = document.getElementById('promptInput');
const charCount = document.getElementById('charCount');
const btnSend = document.getElementById('btnSend');
const chatMessages = document.getElementById('chatMessages');
const commandMenu = document.getElementById('commandMenu');
const commandItems = document.querySelectorAll('.command-item');
const imageToolbar = document.getElementById('imageToolbar');
const zoomLevel = document.getElementById('zoomLevel');

// 控制按钮
const btnAutoArrangeAll = document.getElementById('btnAutoArrangeAll');
const btnAutoArrangeSelected = document.getElementById('btnAutoArrangeSelected');
const btnFitToScreen = document.getElementById('btnFitToScreen');
const btnMinimizeChat = document.getElementById('btnMinimizeChat');
const floatingChat = document.getElementById('floatingChat');
const floatingChatBtn = document.getElementById('floatingChatBtn');

// 模态框
const imageModal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const modalClose = document.getElementById('modalClose');

// 辅助线
const guideVertical = document.getElementById('guideVertical');
const guideHorizontal = document.getElementById('guideHorizontal');

// 对齐配置
const SNAP_THRESHOLD = 8; // 磁吸阈值（像素）

// 命令配置
const commands = [
    { name: '生成', mode: 'generate' },
    { name: '多图', mode: 'multi' },
    { name: '对话', mode: 'chat' },
    { name: '修改', mode: 'modify' }
];

let selectedCommandIndex = 0;

// ============ 初始化 ============

function init() {
    setupEventListeners();
    updateZoomDisplay();
    centerCanvas();
}

// ============ 事件监听器设置 ============

function setupEventListeners() {
    // 画布拖拽
    container.addEventListener('mousedown', handleCanvasMouseDown);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    
    // 缩放
    container.addEventListener('wheel', handleWheel, { passive: false });
    
    // 聊天表单
    chatForm.addEventListener('submit', handleChatSubmit);
    
    // 输入框
    promptInput.addEventListener('input', handleInput);
    promptInput.addEventListener('keydown', handleKeyDown);
    
    // 命令菜单
    commandItems.forEach(item => {
        item.addEventListener('click', () => selectCommand(item.dataset.command));
    });
    
    // 控制按钮
    btnAutoArrangeAll.addEventListener('click', () => autoArrangeImages(canvasState.images.map(img => img.id)));
    btnAutoArrangeSelected.addEventListener('click', () => autoArrangeImages(canvasState.selectedImages));
    btnFitToScreen.addEventListener('click', fitToScreen);
    btnMinimizeChat.addEventListener('click', toggleChat);
    floatingChatBtn.addEventListener('click', toggleChat);
    
    // 工具栏按钮
    imageToolbar.addEventListener('click', handleToolbarAction);
    
    // 模态框
    modalClose.addEventListener('click', () => imageModal.classList.remove('active'));
    imageModal.querySelector('.modal-backdrop').addEventListener('click', () => imageModal.classList.remove('active'));
    
    // 点击空白处取消选择
    document.addEventListener('click', handleDocumentClick);
    
    // 全局快捷键：按 / 打开命令菜单
    document.addEventListener('keydown', handleGlobalKeyDown);
}

// ============ 画布操作 ============

function handleCanvasMouseDown(e) {
    // 如果点击的是图片，不处理画布拖拽
    if (e.target.closest('.canvas-image-card')) return;
    
    canvasState.isDraggingCanvas = true;
    canvasState.dragStartX = e.clientX - canvasState.translateX;
    canvasState.dragStartY = e.clientY - canvasState.translateY;
    container.style.cursor = 'grabbing';
}

function handleMouseMove(e) {
    if (canvasState.isDraggingCanvas) {
        canvasState.translateX = e.clientX - canvasState.dragStartX;
        canvasState.translateY = e.clientY - canvasState.dragStartY;
        updateCanvasTransform();
    } else if (canvasState.isDraggingImage && canvasState.dragImageId) {
        const image = canvasState.images.find(img => img.id === canvasState.dragImageId);
        if (image) {
            image.x = (e.clientX - canvasState.dragStartX) / canvasState.scale;
            image.y = (e.clientY - canvasState.dragStartY) / canvasState.scale;
            
            // 应用拖拽对齐检测和磁吸
            applyDragSnapAlignment(image);
            
            updateImagePosition(image);
        }
    } else if (canvasState.isResizing && canvasState.resizeImageId) {
        handleResizeMove(e);
    }
}

function handleMouseUp() {
    // 移除resizing类
    if (canvasState.resizeImageId) {
        const card = viewport.querySelector(`[data-image-id="${canvasState.resizeImageId}"]`);
        if (card) {
            card.classList.remove('resizing');
        }
    }
    
    // 清理动画帧
    if (canvasState.resizeAnimationFrame) {
        cancelAnimationFrame(canvasState.resizeAnimationFrame);
        canvasState.resizeAnimationFrame = null;
    }
    
    // 隐藏辅助线
    hideAlignGuides();
    
    canvasState.isDraggingCanvas = false;
    canvasState.isDraggingImage = false;
    canvasState.isResizing = false;
    canvasState.resizeImageId = null;
    container.style.cursor = 'grab';
}

function handleWheel(e) {
    e.preventDefault();
    
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    const newScale = Math.max(0.1, Math.min(3, canvasState.scale * delta));
    
    // 计算鼠标位置
    const rect = container.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    // 调整平移以保持鼠标位置不变
    const scaleDiff = newScale - canvasState.scale;
    canvasState.translateX -= (mouseX - canvasState.translateX) * scaleDiff / canvasState.scale;
    canvasState.translateY -= (mouseY - canvasState.translateY) * scaleDiff / canvasState.scale;
    
    canvasState.scale = newScale;
    updateCanvasTransform();
    updateZoomDisplay();
}

function updateCanvasTransform() {
    viewport.style.transform = `translate(${canvasState.translateX}px, ${canvasState.translateY}px) scale(${canvasState.scale})`;
}

function updateZoomDisplay() {
    zoomLevel.textContent = Math.round(canvasState.scale * 100) + '%';
}

function centerCanvas() {
    const rect = container.getBoundingClientRect();
    canvasState.translateX = rect.width / 2;
    canvasState.translateY = rect.height / 2;
    updateCanvasTransform();
}

function fitToScreen() {
    if (canvasState.images.length === 0) {
        centerCanvas();
        canvasState.scale = 1;
        updateCanvasTransform();
        updateZoomDisplay();
        return;
    }
    
    // 计算所有图片的边界
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    canvasState.images.forEach(img => {
        minX = Math.min(minX, img.x);
        minY = Math.min(minY, img.y);
        maxX = Math.max(maxX, img.x + img.width);
        maxY = Math.max(maxY, img.y + img.height);
    });
    
    const contentWidth = maxX - minX;
    const contentHeight = maxY - minY;
    const rect = container.getBoundingClientRect();
    
    // 计算适合的缩放比例
    const scaleX = (rect.width * 0.9) / contentWidth;
    const scaleY = (rect.height * 0.9) / contentHeight;
    canvasState.scale = Math.min(scaleX, scaleY, 1);
    
    // 居中
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;
    canvasState.translateX = rect.width / 2 - centerX * canvasState.scale;
    canvasState.translateY = rect.height / 2 - centerY * canvasState.scale;
    
    updateCanvasTransform();
    updateZoomDisplay();
}

// ============ 图片操作 ============

function addImageToCanvas(imageData, customPosition = null) {
    const position = customPosition || calculateNextPosition();
    
    const image = {
        id: Date.now() + Math.random(),
        url: imageData.url,
        prompt: imageData.prompt,
        x: position.x,
        y: position.y,
        width: 300,
        height: 300
    };
    
    canvasState.images.push(image);
    renderImage(image);
    
    // 自动适应屏幕
    setTimeout(() => fitToScreen(), 100);
}

function calculateNextPosition() {
    if (canvasState.images.length === 0) {
        return { x: 0, y: 0 };
    }
    
    // 简单的网格排列
    const cols = Math.ceil(Math.sqrt(canvasState.images.length + 1));
    const row = Math.floor(canvasState.images.length / cols);
    const col = canvasState.images.length % cols;
    
    return {
        x: col * 350 - (cols * 350) / 2,
        y: row * 350
    };
}

function renderImage(image) {
    const card = document.createElement('div');
    card.className = 'canvas-image-card';
    card.dataset.imageId = image.id;
    card.style.left = image.x + 'px';
    card.style.top = image.y + 'px';
    card.style.width = image.width + 'px';
    
    card.innerHTML = `
        <img src="${image.url}" alt="${image.prompt}" draggable="false" title="${image.prompt}">
        <div class="resize-handle resize-tl"></div>
        <div class="resize-handle resize-tr"></div>
        <div class="resize-handle resize-bl"></div>
        <div class="resize-handle resize-br"></div>
    `;
    
    // 图片拖拽
    card.addEventListener('mousedown', (e) => {
        if (!e.target.classList.contains('resize-handle')) {
            handleImageMouseDown(e, image.id);
        }
    });
    
    // 图片点击选择
    card.addEventListener('click', (e) => {
        e.stopPropagation();
        if (!canvasState.isDraggingImage && !canvasState.isResizing) {
            toggleImageSelection(image.id, e.ctrlKey || e.metaKey);
        }
    });
    
    // 双击预览
    card.addEventListener('dblclick', (e) => {
        e.stopPropagation();
        if (!e.target.classList.contains('resize-handle')) {
            showImageModal(image.url);
        }
    });
    
    // 缩放角点事件
    const resizeHandles = card.querySelectorAll('.resize-handle');
    resizeHandles.forEach(handle => {
        handle.addEventListener('mousedown', (e) => handleResizeStart(e, image.id, handle.classList[1]));
    });
    
    viewport.appendChild(card);
}

function updateImagePosition(image) {
    const card = viewport.querySelector(`[data-image-id="${image.id}"]`);
    if (card) {
        // 使用transform提高性能，避免触发layout
        card.style.left = image.x + 'px';
        card.style.top = image.y + 'px';
        card.style.width = image.width + 'px';
        // 不设置height，让图片自适应
    }
}

function handleImageMouseDown(e, imageId) {
    e.stopPropagation();
    
    const image = canvasState.images.find(img => img.id === imageId);
    if (!image) return;
    
    canvasState.isDraggingImage = true;
    canvasState.dragImageId = imageId;
    
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    canvasState.dragStartX = e.clientX - image.x * canvasState.scale;
    canvasState.dragStartY = e.clientY - image.y * canvasState.scale;
    
    card.classList.add('dragging');
    
    document.addEventListener('mouseup', function onMouseUp() {
        card.classList.remove('dragging');
        document.removeEventListener('mouseup', onMouseUp);
    }, { once: true });
}

// ============ 图片缩放功能 ============

function handleResizeStart(e, imageId, direction) {
    e.stopPropagation();
    e.preventDefault();
    
    const image = canvasState.images.find(img => img.id === imageId);
    if (!image) return;
    
    canvasState.isResizing = true;
    canvasState.resizeImageId = imageId;
    canvasState.resizeDirection = direction;
    canvasState.resizeStartX = e.clientX;
    canvasState.resizeStartY = e.clientY;
    canvasState.resizeStartWidth = image.width;
    canvasState.resizeStartHeight = image.height;
    canvasState.resizeStartImageX = image.x;
    canvasState.resizeStartImageY = image.y;
    
    // 添加resizing类以禁用transition
    const card = viewport.querySelector(`[data-image-id="${imageId}"]`);
    if (card) {
        card.classList.add('resizing');
    }
}

function handleResizeMove(e) {
    const image = canvasState.images.find(img => img.id === canvasState.resizeImageId);
    if (!image) return;
    
    // 使用requestAnimationFrame优化性能
    if (canvasState.resizeAnimationFrame) {
        return; // 如果已经有待处理的帧，跳过
    }
    
    canvasState.resizeAnimationFrame = requestAnimationFrame(() => {
        canvasState.resizeAnimationFrame = null;
        
        const deltaX = (e.clientX - canvasState.resizeStartX) / canvasState.scale;
        const deltaY = (e.clientY - canvasState.resizeStartY) / canvasState.scale;
        
        const direction = canvasState.resizeDirection;
        const aspectRatio = canvasState.resizeStartWidth / canvasState.resizeStartHeight;
        
        if (direction === 'resize-br') {
            // 右下角：同时调整宽高，保持纵横比
            const newWidth = Math.max(50, canvasState.resizeStartWidth + deltaX);
            image.width = newWidth;
            image.height = newWidth / aspectRatio;
        } else if (direction === 'resize-bl') {
            // 左下角
            const newWidth = Math.max(50, canvasState.resizeStartWidth - deltaX);
            image.width = newWidth;
            image.height = newWidth / aspectRatio;
            image.x = canvasState.resizeStartImageX + (canvasState.resizeStartWidth - newWidth);
        } else if (direction === 'resize-tr') {
            // 右上角
            const newWidth = Math.max(50, canvasState.resizeStartWidth + deltaX);
            image.width = newWidth;
            image.height = newWidth / aspectRatio;
            image.y = canvasState.resizeStartImageY + (canvasState.resizeStartHeight - image.height);
        } else if (direction === 'resize-tl') {
            // 左上角
            const newWidth = Math.max(50, canvasState.resizeStartWidth - deltaX);
            image.width = newWidth;
            image.height = newWidth / aspectRatio;
            image.x = canvasState.resizeStartImageX + (canvasState.resizeStartWidth - newWidth);
            image.y = canvasState.resizeStartImageY + (canvasState.resizeStartHeight - image.height);
        }
        
        // 应用对齐检测和磁吸
        applySnapAlignment(image, direction, aspectRatio);
        
        updateImagePosition(image);
    });
}


function toggleImageSelection(imageId, multiSelect = false) {
    if (!multiSelect) {
        // 单选：清除其他选择
        canvasState.selectedImages = [imageId];
        document.querySelectorAll('.canvas-image-card.selected').forEach(card => {
            card.classList.remove('selected');
        });
    } else {
        // 多选
        const index = canvasState.selectedImages.indexOf(imageId);
        if (index > -1) {
            canvasState.selectedImages.splice(index, 1);
        } else {
            canvasState.selectedImages.push(imageId);
        }
    }
    
    // 更新选中样式
    const card = viewport.querySelector(`[data-image-id="${imageId}"]`);
    if (card) {
        card.classList.toggle('selected', canvasState.selectedImages.includes(imageId));
    }
    
    updateToolbar();
}

function updateToolbar() {
    if (canvasState.selectedImages.length > 0) {
        // 显示工具栏
        const firstImageId = canvasState.selectedImages[0];
        const card = viewport.querySelector(`[data-image-id="${firstImageId}"]`);
        if (card) {
            const rect = card.getBoundingClientRect();
            imageToolbar.style.display = 'flex';
            imageToolbar.style.left = rect.left + 'px';
            imageToolbar.style.top = (rect.top - 50) + 'px';
        }
        
        // 更新重排选中按钮
        btnAutoArrangeSelected.disabled = canvasState.selectedImages.length < 2;
    } else {
        imageToolbar.style.display = 'none';
        btnAutoArrangeSelected.disabled = true;
    }
}

function handleDocumentClick(e) {
    // 点击空白处取消选择
    if (!e.target.closest('.canvas-image-card') && !e.target.closest('.image-toolbar')) {
        canvasState.selectedImages = [];
        document.querySelectorAll('.canvas-image-card.selected').forEach(card => {
            card.classList.remove('selected');
        });
        updateToolbar();
    }
    
    // 关闭命令菜单
    if (!e.target.closest('#promptInput') && !e.target.closest('.command-menu')) {
        if (canvasState.commandMode) {
            cancelCommand();
        }
    }
}

function handleGlobalKeyDown(e) {
    // 如果已经在输入框中，不处理
    if (e.target === promptInput) return;
    
    // 如果在其他输入元素中，不处理
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    // 按下 / 键打开命令菜单
    if (e.key === '/') {
        e.preventDefault();
        promptInput.focus();
        promptInput.value = '/';
        // 触发input事件以显示命令菜单
        promptInput.dispatchEvent(new Event('input'));
    }
}

// ============ 自动排列 ============

function autoArrangeImages(imageIds) {
    if (imageIds.length === 0) return;
    
    const images = canvasState.images.filter(img => imageIds.includes(img.id));
    const cols = Math.ceil(Math.sqrt(images.length));
    const spacing = 50;
    
    images.forEach((image, index) => {
        const row = Math.floor(index / cols);
        const col = index % cols;
        
        image.x = col * (image.width + spacing) - (cols * (image.width + spacing)) / 2;
        image.y = row * (image.height + spacing);
        
        updateImagePosition(image);
    });
    
    // 自动适应屏幕
    setTimeout(() => fitToScreen(), 100);
}

// ============ 工具栏操作 ============

async function handleToolbarAction(e) {
    const btn = e.target.closest('.toolbar-btn');
    if (!btn) return;
    
    const action = btn.dataset.action;
    const imageId = canvasState.selectedImages[0];
    const image = canvasState.images.find(img => img.id === imageId);
    if (!image) return;
    
    switch (action) {
        case 'upscale':
            addMessage('assistant', '高清放大功能开发中...');
            break;
        case 'regenerate':
            regenerateImage(image);
            break;
        case 'modify':
            promptInput.value = '';
            promptInput.placeholder = '✨ 告诉我如何修改这张图片...';
            canvasState.currentCommand = 'modify';
            promptInput.focus();
            addMessage('assistant', '✅ 已选中图片，请告诉我如何修改！\n\n💡 示例：\n• "换成夜晚场景"\n• "改成水彩风格"\n• "加上一只小鸟"');
            break;
        case 'download':
            downloadImage(image);
            break;
        case 'delete':
            deleteImage(imageId);
            break;
    }
}

async function regenerateImage(image) {
    addMessage('assistant', '正在重新生成图片...');
    await generateImage(image.prompt, image.id);
}

function downloadImage(image) {
    const a = document.createElement('a');
    a.href = image.url;
    a.download = `generated_${Date.now()}.png`;
    a.click();
}

function deleteImage(imageId) {
    const index = canvasState.images.findIndex(img => img.id === imageId);
    if (index > -1) {
        canvasState.images.splice(index, 1);
        const card = viewport.querySelector(`[data-image-id="${imageId}"]`);
        if (card) card.remove();
        
        canvasState.selectedImages = canvasState.selectedImages.filter(id => id !== imageId);
        updateToolbar();
    }
}

// ============ 聊天功能 ============

function handleInput() {
    const value = promptInput.value;
    charCount.textContent = value.length;
    
    // 命令菜单
    if (value === '/' || value.startsWith('/ ')) {
        showCommandMenu();
    } else if (value.startsWith('/')) {
        const query = value.substring(1);
        
        // 检测连续输入 /，用于快速切换命令
        if (query === '/' && canvasState.commandMode) {
            // 切换到下一个命令
            const visibleItems = Array.from(commandItems).filter(item => item.style.display !== 'none');
            selectedCommandIndex = (selectedCommandIndex + 1) % visibleItems.length;
            updateCommandSelection(visibleItems);
            // 清空输入框，保持命令菜单打开
            promptInput.value = '/';
            return;
        }
        
        filterCommands(query.toLowerCase());
    } else {
        if (canvasState.commandMode) {
            hideCommandMenu();
        }
    }
}

function handleKeyDown(e) {
    // 检测按下 / 键用于快速切换命令（不在命令模式下时让其正常输入）
    if (e.key === '/' && canvasState.commandMode && promptInput.value === '/') {
        e.preventDefault();
        const visibleItems = Array.from(commandItems).filter(item => item.style.display !== 'none');
        selectedCommandIndex = (selectedCommandIndex + 1) % visibleItems.length;
        updateCommandSelection(visibleItems);
        return;
    }
    
    if (!canvasState.commandMode) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
        return;
    }
    
    const visibleItems = Array.from(commandItems).filter(item => item.style.display !== 'none');
    
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedCommandIndex = (selectedCommandIndex + 1) % visibleItems.length;
        updateCommandSelection(visibleItems);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedCommandIndex = (selectedCommandIndex - 1 + visibleItems.length) % visibleItems.length;
        updateCommandSelection(visibleItems);
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (visibleItems[selectedCommandIndex]) {
            selectCommand(visibleItems[selectedCommandIndex].dataset.command);
        }
    } else if (e.key === 'Escape') {
        e.preventDefault();
        cancelCommand();
    }
}

async function handleChatSubmit(e) {
    e.preventDefault();
    
    if (canvasState.isGenerating) return;
    
    const prompt = promptInput.value.trim();
    if (!prompt) return;
    
    // 确定意图
    let forcedIntent = canvasState.currentCommand;
    
    // 多图模式特殊处理
    if (forcedIntent === 'multi') {
        await handleMultiGenerationMode(prompt);
        return;
    }
    
    // 修改模式特殊处理
    if (forcedIntent === 'modify') {
        if (canvasState.selectedImages.length === 0) {
            addMessage('assistant', '⚠️ 请先选中一张图片再进行修改。');
            canvasState.currentCommand = null;
            promptInput.placeholder = '输入 / 查看命令，或直接描述你的需求...';
            return;
        }
        addMessage('user', prompt);
        promptInput.value = '';
        charCount.textContent = '0';
        canvasState.currentCommand = null;
        promptInput.placeholder = '输入 / 查看命令，或直接描述你的需求...';
        await modifyImage(canvasState.selectedImages[0], prompt);
        return;
    }
    
    addMessage('user', prompt);
    promptInput.value = '';
    charCount.textContent = '0';
    
    // 重置命令
    canvasState.currentCommand = null;
    promptInput.placeholder = '输入 / 查看命令，或直接描述你的需求...';
    
    canvasState.isGenerating = true;
    btnSend.disabled = true;
    
    const loadingMsg = addMessage('assistant', '思考中...', true);
    
    try {
        // 调用对话API
        const response = await fetch('/api/canvas/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt,
                selectedImageIndex: canvasState.selectedImages.length > 0 ? 0 : null,
                hasImages: canvasState.images.length > 0,
                forcedIntent
            })
        });
        
        const data = await response.json();
        loadingMsg.remove();
        
        if (!data.success) {
            addMessage('assistant', `❌ 错误：${data.error}`);
            return;
        }
        
        if (data.intent === 'multi_generate') {
            // 多图生成模式
            addMessage('assistant', data.response);
            await generateMultipleImages(data.tasks);
        } else if (data.intent === 'generate') {
            await generateImage(data.refined_prompt || prompt);
        } else if (data.intent === 'modify' && canvasState.selectedImages.length > 0) {
            await modifyImage(canvasState.selectedImages[0], data.refined_prompt || prompt);
        } else {
            addMessage('assistant', data.response);
        }
    } catch (error) {
        loadingMsg.remove();
        addMessage('assistant', `❌ 网络错误：${error.message}`);
    } finally {
        canvasState.isGenerating = false;
        btnSend.disabled = false;
    }
}

async function generateImage(prompt, replaceImageId = null) {
    addMessage('assistant', '正在生成图片...');
    
    try {
        const response = await fetch('/api/canvas/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            addMessage('assistant', `❌ 生成失败：${data.error}`);
            return;
        }
        
        if (replaceImageId) {
            // 替换现有图片
            const image = canvasState.images.find(img => img.id === replaceImageId);
            if (image) {
                image.url = data.image_url;
                image.prompt = prompt;
                const card = viewport.querySelector(`[data-image-id="${replaceImageId}"]`);
                if (card) {
                    card.querySelector('img').src = data.image_url;
                    card.querySelector('img').alt = prompt;
                    card.querySelector('img').title = prompt;
                }
            }
        } else {
            // 新增图片
            addImageToCanvas({
                url: data.image_url,
                prompt: prompt
            });
        }
        
        addMessage('assistant', '✅ 图片已生成！');
    } catch (error) {
        addMessage('assistant', `❌ 生成失败：${error.message}`);
    }
}

async function generateMultipleImages(tasks) {
    const total = tasks.length;
    let successCount = 0;
    let failCount = 0;
    
    // 创建进度消息
    const progressMsg = addMessage('assistant', `正在生成第 1/${total} 张...`);
    
    for (let i = 0; i < tasks.length; i++) {
        const task = tasks[i];
        const currentNum = i + 1;
        
        // 更新进度
        progressMsg.querySelector('.message-content').innerHTML = 
            `🎨 正在生成第 ${currentNum}/${total} 张：${task.prompt}`;
        
        try {
            const response = await fetch('/api/canvas/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: task.prompt })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // 计算画布位置：横向排列，间隔一些距离
                const spacing = 50;
                const imageWidth = 300;
                
                addImageToCanvas({
                    url: data.image_url,
                    prompt: task.prompt
                }, {
                    x: 50 + (imageWidth + spacing) * i,
                    y: 50
                });
                
                successCount++;
            } else {
                failCount++;
                console.error(`生成第${currentNum}张失败:`, data.error);
            }
            
            // 稍微延迟，避免请求过快
            if (i < tasks.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 500));
            }
        } catch (error) {
            failCount++;
            console.error(`生成第${currentNum}张出错:`, error);
        }
    }
    
    // 显示最终结果
    progressMsg.querySelector('.message-content').innerHTML = 
        `✅ 批量生成完成！成功 ${successCount} 张${failCount > 0 ? `，失败 ${failCount} 张` : ''}`;
}

async function handleMultiGenerationMode(prompt) {
    addMessage('user', prompt);
    promptInput.value = '';
    charCount.textContent = '0';
    
    // 重置命令
    canvasState.currentCommand = null;
    promptInput.placeholder = '输入 / 查看命令，或直接描述你的需求...';
    
    canvasState.isGenerating = true;
    btnSend.disabled = true;
    
    try {
        // 智能解析多图请求
        const parseResult = parseMultiGenerationPrompt(prompt);
        
        if (parseResult.count === 0 || parseResult.count === 1) {
            // 没有明确的数量，给出提示
            addMessage('assistant', '请告诉我要生成多少张图片。\n\n📝 示例格式：\n• "生成3张可爱的小猫"\n• "画5个不同风格的风景"\n• "创作二张中国风建筑"\n\n或者直接输入：\n• "3张 熊猫"\n• "5个 樱花"\n• "二张 山水画"');
            return;
        }
        
        if (parseResult.count > 10) {
            addMessage('assistant', '⚠️ 单次最多生成10张图片，已自动调整为10张。');
            parseResult.count = 10;
        }
        
        // 显示确认信息
        addMessage('assistant', `好的！我将为你生成 ${parseResult.count} 张"${parseResult.description}"的图片。`);
        
        // 创建任务列表
        const tasks = Array.from({ length: parseResult.count }, (_, i) => ({
            prompt: parseResult.description,
            index: i + 1
        }));
        
        // 执行批量生成
        await generateMultipleImages(tasks);
        
    } catch (error) {
        addMessage('assistant', `❌ 生成失败：${error.message}`);
    } finally {
        canvasState.isGenerating = false;
        btnSend.disabled = false;
    }
}

function parseMultiGenerationPrompt(prompt) {
    // 解析多图生成提示词
    const patterns = [
        // "生成3张xxx" 或 "画5个yyy"
        { regex: /^(?:生成|画|创作|做)?\s*(\d+|[一二三四五六七八九十]+)\s*(?:张|个|幅)\s*(.+)$/i, countIndex: 1, descIndex: 2 },
        // "xxx 3张" 或 "yyy 5个"
        { regex: /^(.+?)\s+(\d+|[一二三四五六七八九十]+)\s*(?:张|个|幅)$/i, countIndex: 2, descIndex: 1 },
        // "3张 xxx"
        { regex: /^(\d+|[一二三四五六七八九十]+)\s*(?:张|个|幅)\s+(.+)$/i, countIndex: 1, descIndex: 2 }
    ];
    
    // 中文数字转换
    const chineseNums = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
    };
    
    for (const pattern of patterns) {
        const match = prompt.match(pattern.regex);
        if (match) {
            let countStr = match[pattern.countIndex];
            const description = match[pattern.descIndex].trim();
            
            // 转换数量
            let count = chineseNums[countStr] || parseInt(countStr);
            
            if (count && description) {
                return { count, description };
            }
        }
    }
    
    // 如果没有匹配到明确的格式，返回0
    return { count: 0, description: prompt };
}

async function modifyImage(imageId, modifyPrompt) {
    const image = canvasState.images.find(img => img.id === imageId);
    if (!image) return;
    
    addMessage('assistant', '正在修改图片...');
    
    try {
        const response = await fetch('/api/canvas/modify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image_url: image.url,
                instruction: modifyPrompt,  // 修正参数名：modify_prompt → instruction
                original_prompt: image.prompt
            })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            addMessage('assistant', `❌ 修改失败：${data.error}`);
            return;
        }
        
        image.url = data.image_url;
        image.prompt = data.new_prompt || image.prompt;
        
        const card = viewport.querySelector(`[data-image-id="${imageId}"]`);
        if (card) {
            card.querySelector('img').src = data.image_url;
            card.querySelector('img').alt = image.prompt;
            card.querySelector('img').title = image.prompt;
        }
        
        addMessage('assistant', '✅ 图片已修改！');
    } catch (error) {
        addMessage('assistant', `❌ 修改失败：${error.message}`);
    }
}

function addMessage(role, content, isLoading = false) {
    const msg = document.createElement('div');
    msg.className = `message ${role}`;
    msg.innerHTML = `
        <div class="message-content">
            ${isLoading ? '<span class="loading-spinner"></span>' : content}
        </div>
    `;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msg;
}

// ============ 命令菜单 ============

function showCommandMenu() {
    canvasState.commandMode = true;
    commandMenu.classList.add('active');
    selectedCommandIndex = 0;
    commandItems.forEach(item => item.style.display = 'flex');
    updateCommandSelection(Array.from(commandItems));
}

function hideCommandMenu() {
    canvasState.commandMode = false;
    commandMenu.classList.remove('active');
}

function cancelCommand() {
    hideCommandMenu();
    canvasState.currentCommand = null;
    promptInput.placeholder = '输入 / 查看命令，或直接描述你的需求...';
}

function filterCommands(query) {
    canvasState.commandMode = true;
    commandMenu.classList.add('active');
    let visibleCount = 0;
    
    commandItems.forEach(item => {
        const commandName = item.dataset.command.toLowerCase();
        if (commandName.includes(query)) {
            item.style.display = 'flex';
            visibleCount++;
        } else {
            item.style.display = 'none';
        }
    });
    
    if (visibleCount === 0) {
        hideCommandMenu();
    } else {
        selectedCommandIndex = 0;
        const visibleItems = Array.from(commandItems).filter(item => item.style.display !== 'none');
        updateCommandSelection(visibleItems);
    }
}

function updateCommandSelection(visibleItems) {
    commandItems.forEach(item => item.classList.remove('selected'));
    if (visibleItems[selectedCommandIndex]) {
        visibleItems[selectedCommandIndex].classList.add('selected');
        visibleItems[selectedCommandIndex].scrollIntoView({ block: 'nearest' });
    }
}

function selectCommand(commandName) {
    const command = commands.find(c => c.name === commandName);
    if (!command) return;
    
    canvasState.currentCommand = command.mode;
    promptInput.value = '';
    
    if (command.mode === 'generate') {
        promptInput.placeholder = '🎨 生成模式：描述你想要的图片...';
        addMessage('assistant', '已切换到生成模式。告诉我你想生成什么图片吧！');
    } else if (command.mode === 'multi') {
        promptInput.placeholder = '🖼️ 多图模式：输入"3张 熊猫"或"生成5个风景"...';
        addMessage('assistant', '已切换到多图模式。\n\n📝 输入格式示例：\n• "3张 可爱的小猫"\n• "生成5个风景画"\n• "画二张中国风建筑"\n\n💡 提示：最多可生成10张图片');
    } else if (command.mode === 'chat') {
        promptInput.placeholder = '💬 对话模式：问我任何问题...';
        addMessage('assistant', '已切换到对话模式。有什么想了解的吗？');
    } else if (command.mode === 'modify') {
        if (canvasState.selectedImages.length === 0) {
            promptInput.placeholder = '✨ 修改模式：请先选择图片';
            addMessage('assistant', '修改模式需要先选中一张图片。请点击画布中的图片。');
        } else {
            promptInput.placeholder = '✨ 修改模式：告诉我如何修改选中的图片...';
            addMessage('assistant', '已切换到修改模式。告诉我要如何修改选中的图片！');
        }
    }
    
    hideCommandMenu();
    promptInput.focus();
}

// ============ 对齐和磁吸功能 ============

function applySnapAlignment(currentImage, resizeDirection = null, aspectRatio = null) {
    // 获取其他图片（排除当前正在缩放的图片）
    const otherImages = canvasState.images.filter(img => img.id !== currentImage.id);
    
    if (otherImages.length === 0) {
        hideAlignGuides();
        return;
    }
    
    // 当前图片的边界
    const current = {
        left: currentImage.x,
        right: currentImage.x + currentImage.width,
        top: currentImage.y,
        bottom: currentImage.y + currentImage.height,
        centerX: currentImage.x + currentImage.width / 2,
        centerY: currentImage.y + currentImage.height / 2,
        width: currentImage.width,
        height: currentImage.height
    };
    
    // 收集所有可能的对齐点
    let alignments = {
        x: [],
        y: []
    };
    
    // 遍历所有其他图片，收集对齐信息
    for (const other of otherImages) {
        const target = {
            left: other.x,
            right: other.x + other.width,
            top: other.y,
            bottom: other.y + other.height,
            centerX: other.x + other.width / 2,
            centerY: other.y + other.height / 2
        };
        
        // 收集X轴对齐点
        if (Math.abs(current.left - target.left) < SNAP_THRESHOLD) {
            alignments.x.push({ type: 'left-left', value: target.left, distance: Math.abs(current.left - target.left) });
        }
        if (Math.abs(current.right - target.right) < SNAP_THRESHOLD) {
            alignments.x.push({ type: 'right-right', value: target.right, distance: Math.abs(current.right - target.right) });
        }
        if (Math.abs(current.left - target.right) < SNAP_THRESHOLD) {
            alignments.x.push({ type: 'left-right', value: target.right, distance: Math.abs(current.left - target.right) });
        }
        if (Math.abs(current.right - target.left) < SNAP_THRESHOLD) {
            alignments.x.push({ type: 'right-left', value: target.left, distance: Math.abs(current.right - target.left) });
        }
        if (Math.abs(current.centerX - target.centerX) < SNAP_THRESHOLD) {
            alignments.x.push({ type: 'center-center', value: target.centerX, distance: Math.abs(current.centerX - target.centerX) });
        }
        
        // 收集Y轴对齐点
        if (Math.abs(current.top - target.top) < SNAP_THRESHOLD) {
            alignments.y.push({ type: 'top-top', value: target.top, distance: Math.abs(current.top - target.top) });
        }
        if (Math.abs(current.bottom - target.bottom) < SNAP_THRESHOLD) {
            alignments.y.push({ type: 'bottom-bottom', value: target.bottom, distance: Math.abs(current.bottom - target.bottom) });
        }
        if (Math.abs(current.top - target.bottom) < SNAP_THRESHOLD) {
            alignments.y.push({ type: 'top-bottom', value: target.bottom, distance: Math.abs(current.top - target.bottom) });
        }
        if (Math.abs(current.bottom - target.top) < SNAP_THRESHOLD) {
            alignments.y.push({ type: 'bottom-top', value: target.top, distance: Math.abs(current.bottom - target.top) });
        }
        if (Math.abs(current.centerY - target.centerY) < SNAP_THRESHOLD) {
            alignments.y.push({ type: 'center-center', value: target.centerY, distance: Math.abs(current.centerY - target.centerY) });
        }
    }
    
    // 按距离排序，选择最近的对齐点
    alignments.x.sort((a, b) => a.distance - b.distance);
    alignments.y.sort((a, b) => a.distance - b.distance);
    
    let guideX = null;
    let guideY = null;
    
    // 应用X轴对齐
    if (alignments.x.length > 0) {
        const align = alignments.x[0];
        guideX = align.value;
        
        if (resizeDirection) {
            // 缩放模式
            applyResizeAlignmentX(currentImage, align, resizeDirection, aspectRatio, current);
        }
    }
    
    // 应用Y轴对齐
    if (alignments.y.length > 0) {
        const align = alignments.y[0];
        guideY = align.value;
        
        if (resizeDirection) {
            // 缩放模式
            applyResizeAlignmentY(currentImage, align, resizeDirection, aspectRatio, current);
        }
    }
    
    // 显示辅助线
    if (guideX !== null) {
        showVerticalGuide(guideX);
    } else {
        guideVertical.style.display = 'none';
    }
    
    if (guideY !== null) {
        showHorizontalGuide(guideY);
    } else {
        guideHorizontal.style.display = 'none';
    }
}

// X轴缩放对齐
function applyResizeAlignmentX(image, align, direction, aspectRatio, originalBounds) {
    switch (align.type) {
        case 'left-left':
            if (direction === 'resize-bl' || direction === 'resize-tl') {
                image.x = align.value;
                image.width = originalBounds.right - align.value;
            }
            break;
        case 'right-right':
            if (direction === 'resize-br' || direction === 'resize-tr') {
                image.width = align.value - image.x;
                if (aspectRatio) {
                    const newHeight = image.width / aspectRatio;
                    if (direction === 'resize-tr') {
                        image.y = originalBounds.bottom - newHeight;
                    }
                    image.height = newHeight;
                }
            }
            break;
        case 'left-right':
            if (direction === 'resize-bl' || direction === 'resize-tl') {
                image.x = align.value;
                image.width = originalBounds.right - align.value;
            }
            break;
        case 'right-left':
            if (direction === 'resize-br' || direction === 'resize-tr') {
                image.width = align.value - image.x;
                if (aspectRatio) {
                    const newHeight = image.width / aspectRatio;
                    if (direction === 'resize-tr') {
                        image.y = originalBounds.bottom - newHeight;
                    }
                    image.height = newHeight;
                }
            }
            break;
        case 'center-center':
            const halfWidth = image.width / 2;
            image.x = align.value - halfWidth;
            break;
    }
}

// Y轴缩放对齐
function applyResizeAlignmentY(image, align, direction, aspectRatio, originalBounds) {
    switch (align.type) {
        case 'top-top':
            if (direction === 'resize-tl' || direction === 'resize-tr') {
                image.y = align.value;
                image.height = originalBounds.bottom - align.value;
            }
            break;
        case 'bottom-bottom':
            // 关键优化：底部对齐时，先设置高度，再根据纵横比计算宽度
            if (direction === 'resize-bl' || direction === 'resize-br') {
                image.height = align.value - image.y;
                if (aspectRatio) {
                    const newWidth = image.height * aspectRatio;
                    if (direction === 'resize-bl') {
                        image.x = originalBounds.right - newWidth;
                    }
                    image.width = newWidth;
                }
            }
            break;
        case 'top-bottom':
            if (direction === 'resize-tl' || direction === 'resize-tr') {
                image.y = align.value;
                image.height = originalBounds.bottom - align.value;
            }
            break;
        case 'bottom-top':
            if (direction === 'resize-bl' || direction === 'resize-br') {
                image.height = align.value - image.y;
                if (aspectRatio) {
                    const newWidth = image.height * aspectRatio;
                    if (direction === 'resize-bl') {
                        image.x = originalBounds.right - newWidth;
                    }
                    image.width = newWidth;
                }
            }
            break;
        case 'center-center':
            const halfHeight = image.height / 2;
            image.y = align.value - halfHeight;
            break;
    }
}

function applyDragSnapAlignment(currentImage) {
    // 获取其他图片（排除当前正在拖拽的图片）
    const otherImages = canvasState.images.filter(img => img.id !== currentImage.id);
    
    if (otherImages.length === 0) {
        hideAlignGuides();
        return;
    }
    
    // 当前图片的边界
    const current = {
        left: currentImage.x,
        right: currentImage.x + currentImage.width,
        top: currentImage.y,
        bottom: currentImage.y + currentImage.height,
        centerX: currentImage.x + currentImage.width / 2,
        centerY: currentImage.y + currentImage.height / 2
    };
    
    let snappedX = false;
    let snappedY = false;
    let guideX = null;
    let guideY = null;
    
    // 检测对齐（拖拽时只调整位置，不改变大小）
    for (const other of otherImages) {
        const target = {
            left: other.x,
            right: other.x + other.width,
            top: other.y,
            bottom: other.y + other.height,
            centerX: other.x + other.width / 2,
            centerY: other.y + other.height / 2
        };
        
        // 垂直对齐检测（左、右、中心）
        if (!snappedX) {
            // 左对左
            if (Math.abs(current.left - target.left) < SNAP_THRESHOLD) {
                currentImage.x = target.left;
                guideX = target.left;
                snappedX = true;
            }
            // 右对右
            else if (Math.abs(current.right - target.right) < SNAP_THRESHOLD) {
                currentImage.x = target.right - currentImage.width;
                guideX = target.right;
                snappedX = true;
            }
            // 左对右
            else if (Math.abs(current.left - target.right) < SNAP_THRESHOLD) {
                currentImage.x = target.right;
                guideX = target.right;
                snappedX = true;
            }
            // 右对左
            else if (Math.abs(current.right - target.left) < SNAP_THRESHOLD) {
                currentImage.x = target.left - currentImage.width;
                guideX = target.left;
                snappedX = true;
            }
            // 中心对中心
            else if (Math.abs(current.centerX - target.centerX) < SNAP_THRESHOLD) {
                currentImage.x = target.centerX - currentImage.width / 2;
                guideX = target.centerX;
                snappedX = true;
            }
        }
        
        // 水平对齐检测（上、下、中心）
        if (!snappedY) {
            // 上对上
            if (Math.abs(current.top - target.top) < SNAP_THRESHOLD) {
                currentImage.y = target.top;
                guideY = target.top;
                snappedY = true;
            }
            // 下对下
            else if (Math.abs(current.bottom - target.bottom) < SNAP_THRESHOLD) {
                currentImage.y = target.bottom - currentImage.height;
                guideY = target.bottom;
                snappedY = true;
            }
            // 上对下
            else if (Math.abs(current.top - target.bottom) < SNAP_THRESHOLD) {
                currentImage.y = target.bottom;
                guideY = target.bottom;
                snappedY = true;
            }
            // 下对上
            else if (Math.abs(current.bottom - target.top) < SNAP_THRESHOLD) {
                currentImage.y = target.top - currentImage.height;
                guideY = target.top;
                snappedY = true;
            }
            // 中心对中心
            else if (Math.abs(current.centerY - target.centerY) < SNAP_THRESHOLD) {
                currentImage.y = target.centerY - currentImage.height / 2;
                guideY = target.centerY;
                snappedY = true;
            }
        }
        
        // 如果两个方向都已对齐，提前退出
        if (snappedX && snappedY) break;
    }
    
    // 显示或隐藏辅助线
    if (guideX !== null) {
        showVerticalGuide(guideX);
    } else {
        guideVertical.style.display = 'none';
    }
    
    if (guideY !== null) {
        showHorizontalGuide(guideY);
    } else {
        guideHorizontal.style.display = 'none';
    }
}

function showVerticalGuide(x) {
    guideVertical.style.left = x + 'px';
    guideVertical.style.display = 'block';
}

function showHorizontalGuide(y) {
    guideHorizontal.style.top = y + 'px';
    guideHorizontal.style.display = 'block';
}

function hideAlignGuides() {
    guideVertical.style.display = 'none';
    guideHorizontal.style.display = 'none';
}

// ============ 其他功能 ============

function toggleChat() {
    const isMinimized = floatingChat.classList.toggle('minimized');
    floatingChatBtn.style.display = isMinimized ? 'block' : 'none';
}

function showImageModal(url) {
    modalImage.src = url;
    imageModal.classList.add('active');
}

// ============ 启动 ============

init();
