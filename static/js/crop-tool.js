/**
 * crop-tool.js - 图片裁剪工具模块
 * 功能：自动识别纸张边界、手动绘制边界、应用裁剪、图片旋转
 */

// 图片旋转状态（0, 90, 180, 270）
let imageRotation = 0;

/**
 * 显示裁剪工具提示和选项
 * 改为在预览头部显示一个小的裁剪按钮，而不是覆盖整个预览区域
 */
function showCropToolHint() {
    const previewContainer = document.getElementById('uploaded-image-preview');
    if (!previewContainer) return;
    
    // 移除旧的按钮（如果存在）
    removeCropToolHint();
    
    // 找到preview-header
    const header = previewContainer.querySelector('.preview-header');
    if (!header) return;
    
    // 创建小的裁剪按钮
    const cropBtn = document.createElement('button');
    cropBtn.id = 'crop-tool-hint';
    cropBtn.innerHTML = '✂️ 裁剪';
    cropBtn.style.cssText = `
        background: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-size: 12px;
        cursor: pointer;
        font-weight: bold;
        margin-left: auto;
        transition: background 0.2s;
    `;
    
    // 鼠标悬停效果
    cropBtn.onmouseover = function() {
        this.style.background = '#45a049';
    };
    cropBtn.onmouseout = function() {
        this.style.background = '#4CAF50';
    };
    
    // 创建下拉菜单
    const menuDiv = document.createElement('div');
    menuDiv.style.cssText = `
        position: absolute;
        top: 100%;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        z-index: 100;
        min-width: 120px;
        display: none;
    `;
    menuDiv.innerHTML = `
        <div style="padding: 8px;">
            <button onclick="showCropTool('auto')" style="display: block; width: 100%; padding: 8px; border: none; background: none; text-align: left; cursor: pointer; border-radius: 4px; font-size: 12px;">🤖 自动识别</button>
            <button onclick="showCropTool('manual')" style="display: block; width: 100%; padding: 8px; border: none; background: none; text-align: left; cursor: pointer; border-radius: 4px; font-size: 12px; margin-top: 4px;">✏️ 手动绘制</button>
        </div>
    `;
    
    // 按钮点击显示/隐藏菜单
    cropBtn.onclick = function(e) {
        e.stopPropagation();
        menuDiv.style.display = menuDiv.style.display === 'none' ? 'block' : 'none';
    };
    
    // 点击页面其他地方隐藏菜单
    document.addEventListener('click', function() {
        menuDiv.style.display = 'none';
    });
    
    // 将菜单放在header中
    header.appendChild(menuDiv);
    
    // 使header变为相对定位，以便菜单相对于它定位
    header.style.position = 'relative';
    
    // 将按钮添加到header末尾
    header.appendChild(cropBtn);
}

/**
 * 移除裁剪工具提示
 */
function removeCropToolHint() {
    const hint = document.getElementById('crop-tool-hint');
    if (hint) {
        hint.remove();
    }
}

/**
 * 显示裁剪工具（自动识别或手动绘制）
 */
function showCropTool(mode) {
    const previewImg = document.getElementById('uploaded-image');
    if (!previewImg) {
        showToast('请先上传图片', 'warning');
        return;
    }
    
    removeCropToolHint();
    
    if (mode === 'auto') {
        // 自动识别纸张边界
        showToast('正在分析图片边界...', 'info');
        detectAndDrawPaperBorder(previewImg);
    } else if (mode === 'manual') {
        // 手动绘制边界
        showToast('点击图片的四个角来绘制边界框', 'info');
        initializeManualCropMode(previewImg);
    }
}

/**
 * 自动检测并绘制纸张边界
 */
// 存储当前的拖拽状态
let currentDragCorner = null;

function detectAndDrawPaperBorder(imgElement) {
    const previewContainer = document.getElementById('uploaded-image-preview');
    if (!previewContainer) return;
    
    // 移除之前的SVG覆盖层（如果存在）
    const existingSvg = previewContainer.querySelector('svg');
    if (existingSvg) {
        existingSvg.remove();
    }
    
    // 获取原始图片的尺寸
    const imgWidth = imgElement.naturalWidth;
    const imgHeight = imgElement.naturalHeight;
    
    // 创建一个临时canvas来检测边界
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = imgWidth;
    tempCanvas.height = imgHeight;
    tempCtx.drawImage(imgElement, 0, 0);
    
    // 检测纸张边界
    const border = detectPaperBoundary(tempCtx, imgWidth, imgHeight);
    
    // 转换为四个角点（支持透视变形）
    const corners = [
        { x: border.left, y: border.top, id: 'tl' },      // 左上
        { x: border.right, y: border.top, id: 'tr' },     // 右上
        { x: border.right, y: border.bottom, id: 'br' },  // 右下
        { x: border.left, y: border.bottom, id: 'bl' }    // 左下
    ];
    
    // 绘制四边形裁剪框
    drawQuadCropOverlay(imgElement, corners);
}

/**
 * 绘制四边形裁剪覆盖层
 */
function drawQuadCropOverlay(imgElement, corners) {
    const previewContainer = document.getElementById('uploaded-image-preview');
    if (!previewContainer) return;
    
    const imgWidth = imgElement.naturalWidth;
    const imgHeight = imgElement.naturalHeight;
    
    // 创建SVG覆盖层
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', `0 0 ${imgWidth} ${imgHeight}`);
    svg.setAttribute('id', 'crop-svg-overlay');
    svg.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        cursor: crosshair;
        pointer-events: none;
    `;
    
    // 绘制半透明遮挡层
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const mask = document.createElementNS('http://www.w3.org/2000/svg', 'mask');
    mask.setAttribute('id', 'cropMask');
    
    const maskRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    maskRect.setAttribute('width', imgWidth);
    maskRect.setAttribute('height', imgHeight);
    maskRect.setAttribute('fill', 'white');
    mask.appendChild(maskRect);
    
    const maskPoly = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    maskPoly.setAttribute('id', 'cropMaskPoly');
    const points = corners.map(c => `${c.x},${c.y}`).join(' ');
    maskPoly.setAttribute('points', points);
    maskPoly.setAttribute('fill', 'black');
    mask.appendChild(maskPoly);
    
    defs.appendChild(mask);
    svg.appendChild(defs);
    
    // 遮挡层
    const overlay = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    overlay.setAttribute('width', imgWidth);
    overlay.setAttribute('height', imgHeight);
    overlay.setAttribute('fill', 'rgba(0,0,0,0.4)');
    overlay.setAttribute('mask', 'url(#cropMask)');
    overlay.style.pointerEvents = 'none';
    svg.appendChild(overlay);
    
    // 绘制四边形边界
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('id', 'cropPolygon');
    polygon.setAttribute('points', points);
    polygon.setAttribute('fill', 'none');
    polygon.setAttribute('stroke', '#FF8C00');
    polygon.setAttribute('stroke-width', '3');
    polygon.style.pointerEvents = 'none';
    svg.appendChild(polygon);
    
    // 添加四个可拖拽的角点
    const cornerSize = 20;
    corners.forEach(corner => {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('class', 'corner-handle');
        group.setAttribute('data-corner', corner.id);
        group.style.cursor = 'move';
        
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', corner.x);
        circle.setAttribute('cy', corner.y);
        circle.setAttribute('r', cornerSize / 2);
        circle.setAttribute('fill', '#FF8C00');
        circle.setAttribute('stroke', 'white');
        circle.setAttribute('stroke-width', '3');
        circle.style.pointerEvents = 'auto';
        circle.style.touchAction = 'none'; // 禁用浏览器默认触摸行为
        
        group.appendChild(circle);
        
        // 鼠标事件
        group.onmousedown = (e) => startQuadCornerDrag(e, corner.id, svg, corners, imgWidth, imgHeight);
        
        // 触摸事件
        group.ontouchstart = (e) => startQuadCornerDrag(e, corner.id, svg, corners, imgWidth, imgHeight);
        
        svg.appendChild(group);
    });
    
    previewContainer.style.position = 'relative';
    previewContainer.appendChild(svg);
    
    // 显示裁剪确认按钮
    showCropConfirmButtons(corners);
    
    showToast('📍 已识别纸张边界（拖拽四个角来调整透视）', 'success');
}

/**
 * 开始拖拽角点（四边形版本，支持鼠标和触摸）
 */
function startQuadCornerDrag(e, cornerId, svg, corners, imgWidth, imgHeight) {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('🎯 开始拖拽角点:', cornerId, 'imgSize:', imgWidth, 'x', imgHeight);
    
    // 找到当前拖拽的角点
    const corner = corners.find(c => c.id === cornerId);
    if (!corner) {
        console.error('❌ 未找到角点:', cornerId);
        return;
    }
    
    console.log('📍 初始角点位置:', corner.x, corner.y);
    
    const previewImg = document.getElementById('uploaded-image');
    if (!previewImg) {
        console.error('❌ 未找到uploaded-image元素');
        return;
    }
    
    const imgRect = previewImg.getBoundingClientRect();
    const scaleX = imgWidth / imgRect.width;
    const scaleY = imgHeight / imgRect.height;
    
    console.log('📐 缩放比例 scaleX:', scaleX.toFixed(2), 'scaleY:', scaleY.toFixed(2));
    console.log('📏 图片显示尺寸:', imgRect.width, 'x', imgRect.height);
    console.log('📏 图片真实尺寸:', imgWidth, 'x', imgHeight);
    
    // 获取SVG相对于视口的位置
    const svgRect = svg.getBoundingClientRect();
    console.log('🎨 SVG位置:', 'left:', svgRect.left, 'top:', svgRect.top);
    
    let moveCount = 0; // 用于减少日志输出
    
    // 统一处理函数：处理鼠标或触摸事件
    function handleMove(clientX, clientY) {
        // 计算在SVG坐标系中的位置
        const mouseXInSvg = (clientX - svgRect.left) * scaleX;
        const mouseYInSvg = (clientY - svgRect.top) * scaleY;
        
        // 每10次移动才输出一次日志
        if (moveCount++ % 10 === 0) {
            console.log('🖱️  位置:', clientX, clientY, '→ SVG坐标:', mouseXInSvg.toFixed(0), mouseYInSvg.toFixed(0));
        }
        
        // 直接更新角点位置（限制在图片范围内）
        corner.x = Math.max(0, Math.min(imgWidth, mouseXInSvg));
        corner.y = Math.max(0, Math.min(imgHeight, mouseYInSvg));
        
        // 更新显示
        updateQuadCropDisplay(svg, corners);
    }
    
    // 鼠标移动处理
    function onMouseMove(moveEvent) {
        handleMove(moveEvent.clientX, moveEvent.clientY);
    }
    
    // 触摸移动处理
    function onTouchMove(touchEvent) {
        touchEvent.preventDefault();
        if (touchEvent.touches.length > 0) {
            const touch = touchEvent.touches[0];
            handleMove(touch.clientX, touch.clientY);
        }
    }
    
    // 鼠标释放
    function onMouseUp() {
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
        document.removeEventListener('touchmove', onTouchMove);
        document.removeEventListener('touchend', onTouchEnd);
        document.removeEventListener('touchcancel', onTouchEnd);
    }
    
    // 触摸结束
    function onTouchEnd() {
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
        document.removeEventListener('touchmove', onTouchMove);
        document.removeEventListener('touchend', onTouchEnd);
        document.removeEventListener('touchcancel', onTouchEnd);
    }
    
    // 同时监听鼠标和触摸事件
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
    document.addEventListener('touchmove', onTouchMove, { passive: false });
    document.addEventListener('touchend', onTouchEnd);
    document.addEventListener('touchcancel', onTouchEnd);
}

/**
 * 更新四边形裁剪框的显示
 */
function updateQuadCropDisplay(svg, corners) {
    const points = corners.map(c => `${c.x},${c.y}`).join(' ');
    
    // 更新多边形
    const polygon = svg.querySelector('#cropPolygon');
    if (polygon) {
        polygon.setAttribute('points', points);
    }
    
    // 更新mask
    const maskPoly = svg.querySelector('#cropMaskPoly');
    if (maskPoly) {
        maskPoly.setAttribute('points', points);
    }
    
    // 更新角点位置
    corners.forEach(corner => {
        const handle = svg.querySelector(`[data-corner="${corner.id}"] circle`);
        if (handle) {
            handle.setAttribute('cx', corner.x);
            handle.setAttribute('cy', corner.y);
        }
    });
}

/**
 * 开始拖拽角点（旧版本，保留兼容）
 */
function startCornerDrag(e, cornerId, svg, border, imgWidth, imgHeight) {
    e.preventDefault();
    e.stopPropagation();
    currentDragCorner = cornerId;
    
    // 保存初始边界状态
    const initialBorder = {
        left: border.left,
        right: border.right,
        top: border.top,
        bottom: border.bottom
    };
    
    const startClientX = e.clientX;
    const startClientY = e.clientY;
    
    const previewImg = document.getElementById('uploaded-image');
    if (!previewImg) return;
    
    const imgRect = previewImg.getBoundingClientRect();
    const scaleX = imgWidth / imgRect.width;
    const scaleY = imgHeight / imgRect.height;
    
    function onMouseMove(moveEvent) {
        // 计算从起始点的偏移量（在图片坐标系中）
        const deltaX = (moveEvent.clientX - startClientX) * scaleX;
        const deltaY = (moveEvent.clientY - startClientY) * scaleY;
        
        // 更新对应角的坐标（从初始位置计算）
        switch (cornerId) {
            case 'tl':
                border.left = Math.max(0, Math.min(initialBorder.right - 20, initialBorder.left + deltaX));
                border.top = Math.max(0, Math.min(initialBorder.bottom - 20, initialBorder.top + deltaY));
                break;
            case 'tr':
                border.right = Math.min(imgWidth, Math.max(initialBorder.left + 20, initialBorder.right + deltaX));
                border.top = Math.max(0, Math.min(initialBorder.bottom - 20, initialBorder.top + deltaY));
                break;
            case 'bl':
                border.left = Math.max(0, Math.min(initialBorder.right - 20, initialBorder.left + deltaX));
                border.bottom = Math.min(imgHeight, Math.max(initialBorder.top + 20, initialBorder.bottom + deltaY));
                break;
            case 'br':
                border.right = Math.min(imgWidth, Math.max(initialBorder.left + 20, initialBorder.right + deltaX));
                border.bottom = Math.min(imgHeight, Math.max(initialBorder.top + 20, initialBorder.bottom + deltaY));
                break;
        }
        
        // 更新SVG中的rect和角标记
        updateCropRectDisplay(svg, border);
    }
    
    function onMouseUp() {
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
        currentDragCorner = null;
    }
    
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
}

/**
 * 更新裁剪框的显示
 */
function updateCropRectDisplay(svg, border) {
    const rect = svg.querySelector('#cropRect');
    if (rect) {
        rect.setAttribute('x', border.left);
        rect.setAttribute('y', border.top);
        rect.setAttribute('width', Math.max(10, border.right - border.left));
        rect.setAttribute('height', Math.max(10, border.bottom - border.top));
    }
    
    // 更新角标记位置
    const corners = [
        { x: border.left, y: border.top, id: 'tl' },
        { x: border.right, y: border.top, id: 'tr' },
        { x: border.left, y: border.bottom, id: 'bl' },
        { x: border.right, y: border.bottom, id: 'br' }
    ];
    
    corners.forEach(corner => {
        const handle = svg.querySelector(`[data-corner="${corner.id}"] rect`);
        if (handle) {
            const cornerSize = 16;
            handle.setAttribute('x', corner.x - cornerSize / 2);
            handle.setAttribute('y', corner.y - cornerSize / 2);
        }
    });
    
    // 更新mask
    const maskRect2 = svg.querySelector('mask rect:last-of-type');
    if (maskRect2) {
        maskRect2.setAttribute('x', border.left);
        maskRect2.setAttribute('y', border.top);
        maskRect2.setAttribute('width', border.right - border.left);
        maskRect2.setAttribute('height', border.bottom - border.top);
    }
}

/**
 * 显示裁剪确认按钮
 */
function showCropConfirmButtons(cornersOrBorder) {
    // 移除旧的按钮（如果存在）
    removeCropConfirmButtons();
    
    const previewContainer = document.getElementById('uploaded-image-preview');
    if (!previewContainer) return;
    
    const btnContainer = document.createElement('div');
    btnContainer.id = 'crop-confirm-buttons';
    btnContainer.style.cssText = `
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(255, 255, 255, 0.95);
        padding: 8px;
        display: flex;
        gap: 8px;
        border-radius: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 100;
        pointer-events: auto;
    `;
    
    // 通用按钮样式
    const baseStyle = `
        width: 40px;
        height: 40px;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        font-size: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        pointer-events: auto;
    `;
    
    const greenStyle = `${baseStyle} background: #4CAF50; color: white;`;
    const orangeStyle = `${baseStyle} background: #FF9800; color: white;`;
    const redStyle = `${baseStyle} background: #f44336; color: white;`;
    
    // 将corners存储到全局，供按钮调用
    window.currentCropCorners = cornersOrBorder;
    
    btnContainer.innerHTML = `
        <button id="btn-rotate-ccw" 
                title="逆时针旋转"
                onmouseover="this.style.transform='scale(1.1)'" 
                onmouseout="this.style.transform='scale(1)'"
                style="${greenStyle}">
            ↺
        </button>
        <button id="btn-rotate-cw" 
                title="顺时针旋转"
                onmouseover="this.style.transform='scale(1.1)'" 
                onmouseout="this.style.transform='scale(1)'"
                style="${greenStyle}">
            ↻
        </button>
        <button id="btn-rotate-reset" 
                title="重置旋转"
                onmouseover="this.style.transform='scale(1.1)'" 
                onmouseout="this.style.transform='scale(1)'"
                style="${orangeStyle}">
            ⟲
        </button>
        <button id="btn-crop-apply" 
                title="应用裁剪"
                onmouseover="this.style.transform='scale(1.1)'" 
                onmouseout="this.style.transform='scale(1)'"
                style="${greenStyle}">
            ✓
        </button>
        <button id="btn-crop-cancel" 
                title="取消"
                onmouseover="this.style.transform='scale(1.1)'" 
                onmouseout="this.style.transform='scale(1)'"
                style="${redStyle}">
            ✕
        </button>
    `;
    
    previewContainer.appendChild(btnContainer);
    
    console.log('🔘 按钮已添加到DOM, currentCropCorners:', window.currentCropCorners);
    
    // 添加事件监听器
    const btnRotateCcw = document.getElementById('btn-rotate-ccw');
    const btnRotateCw = document.getElementById('btn-rotate-cw');
    const btnRotateReset = document.getElementById('btn-rotate-reset');
    const btnCropApply = document.getElementById('btn-crop-apply');
    const btnCropCancel = document.getElementById('btn-crop-cancel');
    
    console.log('🔍 按钮元素查找结果:', {
        'btn-rotate-ccw': !!btnRotateCcw,
        'btn-rotate-cw': !!btnRotateCw,
        'btn-rotate-reset': !!btnRotateReset,
        'btn-crop-apply': !!btnCropApply,
        'btn-crop-cancel': !!btnCropCancel
    });
    
    if (btnRotateCcw) {
        btnRotateCcw.addEventListener('click', () => {
            console.log('🔄 点击逆时针旋转按钮');
            rotateImageCounterClockwise();
        });
    }
    
    if (btnRotateCw) {
        btnRotateCw.addEventListener('click', () => {
            console.log('🔄 点击顺时针旋转按钮');
            rotateImageClockwise();
        });
    }
    
    if (btnRotateReset) {
        btnRotateReset.addEventListener('click', () => {
            console.log('🔄 点击重置旋转按钮');
            resetImageRotation();
        });
    }
    
    if (btnCropApply) {
        btnCropApply.addEventListener('click', () => {
            console.log('✅ 点击应用裁剪按钮, corners:', window.currentCropCorners);
            applyCropBoundary(window.currentCropCorners);
        });
    }
    
    if (btnCropCancel) {
        btnCropCancel.addEventListener('click', () => {
            console.log('❌ 点击取消按钮');
            cancelCrop();
        });
    }
}

/**
 * 移除裁剪确认按钮
 */
function removeCropConfirmButtons() {
    const btnContainer = document.getElementById('crop-confirm-buttons');
    if (btnContainer) {
        btnContainer.remove();
    }
}

/**
 * 应用裁剪
 */
function applyCropBoundary(cornersOrBorder) {
    console.log('🎬 applyCropBoundary 被调用, 参数:', cornersOrBorder);
    
    const previewImg = document.getElementById('uploaded-image');
    if (!previewImg || !previewImg.src) {
        console.error('❌ 没有图片可裁剪');
        showToast('没有图片可裁剪', 'error');
        return;
    }
    
    console.log('✅ 图片元素存在:', previewImg.src);
    
    // 判断是corners还是border格式
    let corners;
    if (Array.isArray(cornersOrBorder)) {
        corners = cornersOrBorder;
    } else {
        // 转换border为corners
        corners = [
            { x: cornersOrBorder.left, y: cornersOrBorder.top, id: 'tl' },
            { x: cornersOrBorder.right, y: cornersOrBorder.top, id: 'tr' },
            { x: cornersOrBorder.right, y: cornersOrBorder.bottom, id: 'br' },
            { x: cornersOrBorder.left, y: cornersOrBorder.bottom, id: 'bl' }
        ];
    }
    
    showToast('正在裁剪图片...', 'info');
    
    // 获取当前图片的session_id
    const sessionId = window.currentSessionId || '';
    
    // 准备裁剪数据
    const cropData = {
        corners: corners.map(c => ({ x: Math.round(c.x), y: Math.round(c.y), id: c.id })),
        width: previewImg.naturalWidth,
        height: previewImg.naturalHeight
    };
    
    // 发送到后端进行裁剪
    fetch('/api/crop_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: sessionId,
            image_src: previewImg.src,
            crop_data: cropData
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('📦 服务器响应:', data);
        
        if (data.success) {
            console.log('✅ 裁剪成功，新图片URL:', data.cropped_image_url);
            
            // 更新预览图片
            previewImg.src = data.cropped_image_url + '?t=' + Date.now();
            
            // 更新图片加载完成后重新分析宽高比
            previewImg.onload = function() {
                console.log('🖼️ 裁剪后图片已加载，尺寸:', this.naturalWidth, 'x', this.naturalHeight);
                
                // 如果存在分析函数，调用它
                if (typeof analyzeImageAndUpdateAspectRatio === 'function') {
                    analyzeImageAndUpdateAspectRatio(previewImg);
                }
            };
            
            // 清除裁剪UI
            cancelCrop();
            
            showToast('✅ 裁剪成功', 'success');
        } else {
            console.error('❌ 裁剪失败:', data.error);
            showToast('裁剪失败: ' + (data.error || '未知错误'), 'error');
        }
    })
    .catch(error => {
        console.error('裁剪错误:', error);
        showToast('裁剪失败，请重试', 'error');
    });
}

/**
 * 取消裁剪
 */
function cancelCrop() {
    const previewContainer = document.getElementById('uploaded-image-preview');
    if (previewContainer) {
        const svg = previewContainer.querySelector('#crop-svg-overlay');
        if (svg) svg.remove();
    }
    removeCropConfirmButtons();
    showCropToolHint();
    showToast('已取消裁剪', 'info');
}

/**
 * 初始化手动裁剪模式
 */
function initializeManualCropMode(imgElement) {
    const previewContainer = document.getElementById('uploaded-image-preview');
    if (!previewContainer) return;
    
    // 移除之前的SVG覆盖层（如果存在）
    const existingSvg = previewContainer.querySelector('svg');
    if (existingSvg) {
        existingSvg.remove();
    }
    
    // 隐藏其他UI元素
    const cropButtons = previewContainer.querySelector('.crop-confirm-buttons');
    if (cropButtons) cropButtons.style.display = 'none';
    
    const imgWidth = imgElement.naturalWidth;
    const imgHeight = imgElement.naturalHeight;
    
    // 存储四个角点
    let corners = [];
    
    // 创建SVG覆盖层
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', `0 0 ${imgWidth} ${imgHeight}`);
    svg.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        cursor: crosshair;
    `;
    
    // 获取图片相对于容器的scale
    const imgRect = imgElement.getBoundingClientRect();
    const containerRect = previewContainer.getBoundingClientRect();
    const scaleX = imgWidth / imgRect.width;
    const scaleY = imgHeight / imgRect.height;
    
    // 处理点击事件
    svg.addEventListener('click', (e) => {
        if (corners.length >= 4) return;
        
        const svgRect = svg.getBoundingClientRect();
        const x = (e.clientX - svgRect.left) * scaleX;
        const y = (e.clientY - svgRect.top) * scaleY;
        
        corners.push({ x, y });
        
        // 绘制已选择的角点
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', x);
        circle.setAttribute('cy', y);
        circle.setAttribute('r', '8');
        circle.setAttribute('fill', '#FF8C00');
        circle.setAttribute('stroke', 'white');
        circle.setAttribute('stroke-width', '2');
        svg.appendChild(circle);
        
        // 如果有之前的点，连接起来
        if (corners.length > 1) {
            const prevCorner = corners[corners.length - 2];
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', prevCorner.x);
            line.setAttribute('y1', prevCorner.y);
            line.setAttribute('x2', x);
            line.setAttribute('y2', y);
            line.setAttribute('stroke', '#FF8C00');
            line.setAttribute('stroke-width', '2');
            svg.appendChild(line);
        }
        
        // 显示提示
        showToast(`点击了第 ${corners.length} 个角 ${['（左上）', '（右上）', '（右下）', '（左下）'][corners.length - 1]}`, 'info');
        
        // 当选了四个点后，计算边界框
        if (corners.length === 4) {
            setTimeout(() => {
                computeAndDrawBorder();
            }, 300);
        }
    });
    
    previewContainer.style.position = 'relative';
    previewContainer.appendChild(svg);
    
    showToast('🖱️ 请在图片上点击4个角（按顺序：左上 → 右上 → 右下 → 左下）', 'info');
    
    /**
     * 根据4个点计算边界框
     */
    function computeAndDrawBorder() {
        // 计算边界框
        const xs = corners.map(c => c.x);
        const ys = corners.map(c => c.y);
        
        const border = {
            left: Math.min(...xs),
            right: Math.max(...xs),
            top: Math.min(...ys),
            bottom: Math.max(...ys)
        };
        
        // 清空SVG，重新绘制
        svg.innerHTML = '';
        
        // 添加遮挡层
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const mask = document.createElementNS('http://www.w3.org/2000/svg', 'mask');
        mask.setAttribute('id', 'cropMask');
        
        const maskRect1 = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        maskRect1.setAttribute('width', imgWidth);
        maskRect1.setAttribute('height', imgHeight);
        maskRect1.setAttribute('fill', 'white');
        mask.appendChild(maskRect1);
        
        const maskRect2 = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        maskRect2.setAttribute('x', border.left);
        maskRect2.setAttribute('y', border.top);
        maskRect2.setAttribute('width', border.right - border.left);
        maskRect2.setAttribute('height', border.bottom - border.top);
        maskRect2.setAttribute('fill', 'black');
        mask.appendChild(maskRect2);
        
        defs.appendChild(mask);
        svg.appendChild(defs);
        
        // 绘制遮挡层
        const overlay = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        overlay.setAttribute('width', imgWidth);
        overlay.setAttribute('height', imgHeight);
        overlay.setAttribute('fill', 'rgba(0,0,0,0.4)');
        overlay.setAttribute('mask', 'url(#cropMask)');
        overlay.style.pointerEvents = 'none';
        svg.appendChild(overlay);
        
        // 绘制边界线
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('id', 'cropRect');
        rect.setAttribute('x', border.left);
        rect.setAttribute('y', border.top);
        rect.setAttribute('width', border.right - border.left);
        rect.setAttribute('height', border.bottom - border.top);
        rect.setAttribute('fill', 'none');
        rect.setAttribute('stroke', '#FF8C00');
        rect.setAttribute('stroke-width', '2');
        rect.setAttribute('pointer-events', 'none');
        svg.appendChild(rect);
        
        // 添加可拖拽的四个角
        const cornerSize = 16;
        const cornerCoords = [
            { x: border.left, y: border.top, id: 'tl' },
            { x: border.right, y: border.top, id: 'tr' },
            { x: border.left, y: border.bottom, id: 'bl' },
            { x: border.right, y: border.bottom, id: 'br' }
        ];
        
        cornerCoords.forEach(corner => {
            const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            group.setAttribute('class', 'corner-handle');
            group.setAttribute('data-corner', corner.id);
            group.style.cursor = 'pointer';
            
            const square = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            square.setAttribute('x', corner.x - cornerSize / 2);
            square.setAttribute('y', corner.y - cornerSize / 2);
            square.setAttribute('width', cornerSize);
            square.setAttribute('height', cornerSize);
            square.setAttribute('fill', '#FF8C00');
            square.setAttribute('stroke', 'white');
            square.setAttribute('stroke-width', '2');
            square.style.pointerEvents = 'auto';
            
            group.appendChild(square);
            group.onmousedown = (e) => startCornerDrag(e, corner.id, svg, border, imgWidth, imgHeight);
            
            svg.appendChild(group);
        });
        
        // 显示裁剪确认按钮
        showCropConfirmButtons(border);
        
        svg.style.cursor = 'default';
        showToast('✅ 已定义边界框（可拖拽角点调整）', 'success');
    }
}

/**
 * 检测纸张边界（返回边界坐标）
 * 简化算法：使用亮度对比检测
 */
function detectPaperBoundary(ctx, width, height) {
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;
    
    // 转换为灰度
    const gray = new Uint8ClampedArray(width * height);
    for (let i = 0; i < width * height; i++) {
        const idx = i * 4;
        gray[i] = (data[idx] * 0.299 + data[idx + 1] * 0.587 + data[idx + 2] * 0.114);
    }
    
    // 简化策略：找最亮的矩形区域（通常是纸张）
    let topEdge = 0, bottomEdge = height, leftEdge = 0, rightEdge = width;
    
    // 计算亮度阈值（使用中位数）
    const sortedGray = Array.from(gray).sort((a, b) => a - b);
    const medianBrightness = sortedGray[Math.floor(sortedGray.length / 2)];
    const brightThreshold = medianBrightness + 30; // 比中位数亮30以上
    
    // 从上往下找第一个亮区域
    for (let y = 0; y < height * 0.4; y++) {
        let brightCount = 0;
        for (let x = width * 0.1; x < width * 0.9; x++) {
            if (gray[y * width + x] > brightThreshold) brightCount++;
        }
        if (brightCount > (width * 0.8) * 0.5) { // 50%的像素是亮的
            topEdge = Math.max(0, y - 20);
            break;
        }
    }
    
    // 从下往上找最后一个亮区域
    for (let y = height - 1; y > height * 0.6; y--) {
        let brightCount = 0;
        for (let x = width * 0.1; x < width * 0.9; x++) {
            if (gray[y * width + x] > brightThreshold) brightCount++;
        }
        if (brightCount > (width * 0.8) * 0.5) {
            bottomEdge = Math.min(height, y + 20);
            break;
        }
    }
    
    // 从左往右找第一个亮区域
    for (let x = 0; x < width * 0.4; x++) {
        let brightCount = 0;
        for (let y = topEdge; y < bottomEdge; y++) {
            if (gray[y * width + x] > brightThreshold) brightCount++;
        }
        if (brightCount > (bottomEdge - topEdge) * 0.5) {
            leftEdge = Math.max(0, x - 20);
            break;
        }
    }
    
    // 从右往左找最后一个亮区域
    for (let x = width - 1; x > width * 0.6; x--) {
        let brightCount = 0;
        for (let y = topEdge; y < bottomEdge; y++) {
            if (gray[y * width + x] > brightThreshold) brightCount++;
        }
        if (brightCount > (bottomEdge - topEdge) * 0.5) {
            rightEdge = Math.min(width, x + 20);
            break;
        }
    }
    
    // 安全检查：确保边界有合理的大小
    const detectedWidth = rightEdge - leftEdge;
    const detectedHeight = bottomEdge - topEdge;
    
    if (detectedWidth < width * 0.2 || detectedHeight < height * 0.2) {
        // 检测失败，使用保守的默认值：缩小8%
        const marginX = width * 0.08;
        const marginY = height * 0.08;
        return {
            top: marginY,
            bottom: height - marginY,
            left: marginX,
            right: width - marginX
        };
    }
    
    return { top: topEdge, bottom: bottomEdge, left: leftEdge, right: rightEdge };
}

/**
 * 旋转图片 - 顺时针
 */
function rotateImageClockwise() {
    const previewImg = document.getElementById('uploaded-image');
    if (!previewImg) {
        showToast('请先上传图片', 'warning');
        return;
    }
    
    imageRotation = (imageRotation + 90) % 360;
    applyImageRotation(previewImg);
}

/**
 * 旋转图片 - 逆时针
 */
function rotateImageCounterClockwise() {
    const previewImg = document.getElementById('uploaded-image');
    if (!previewImg) {
        showToast('请先上传图片', 'warning');
        return;
    }
    
    imageRotation = (imageRotation - 90 + 360) % 360;
    applyImageRotation(previewImg);
}

/**
 * 重置旋转
 */
function resetImageRotation() {
    imageRotation = 0;
    const previewImg = document.getElementById('uploaded-image');
    if (previewImg) {
        applyImageRotation(previewImg);
    }
}

/**
 * 应用旋转变换到图片
 */
function applyImageRotation(imgElement) {
    imgElement.style.transform = `rotate(${imageRotation}deg)`;
    imgElement.style.transition = 'transform 0.3s ease-in-out';
    
    // 更新旋转信息提示
    if (imageRotation !== 0) {
        showToast(`🔄 已旋转 ${imageRotation}°`, 'info');
    }
}
