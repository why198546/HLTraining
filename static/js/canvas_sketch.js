// 手绘画布功能
console.log('=== Canvas Sketch.js 已加载 ===');

let canvas, ctx;
let isDrawing = false;
let isEraser = false;
let currentColor = '#000000';
let currentSize = 5;
let currentOpacity = 1;
let generatedImageUrl = ''; // 存储生成的图片URL
let currentViewMode = 'overlay'; // 当前视图模式

// 将generatedImageUrl暴露到全局作用域，供保存功能使用
window.generatedImageUrl = '';

// Session管理系统 - 支持至少50步历史记录
class CanvasSession {
    constructor(maxHistory = 50) {
        this.history = [];
        this.currentStep = -1;
        this.maxHistory = maxHistory;
        this.sessionId = this.generateSessionId();
    }
    
    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    // 保存当前状态
    saveState(canvasDataUrl) {
        // 如果当前不在历史末尾，删除后面的历史
        if (this.currentStep < this.history.length - 1) {
            this.history = this.history.slice(0, this.currentStep + 1);
        }
        
        // 添加新状态
        this.history.push({
            dataUrl: canvasDataUrl,
            timestamp: Date.now()
        });
        
        // 限制历史记录数量
        if (this.history.length > this.maxHistory) {
            this.history.shift();
        } else {
            this.currentStep++;
        }
        
        console.log(`[Session] 已保存状态 ${this.currentStep + 1}/${this.history.length}`);
        return true;
    }
    
    // 撤销
    undo() {
        if (this.canUndo()) {
            this.currentStep--;
            console.log(`[Session] 撤销到步骤 ${this.currentStep + 1}/${this.history.length}`);
            return this.getCurrentState();
        }
        return null;
    }
    
    // 重做
    redo() {
        if (this.canRedo()) {
            this.currentStep++;
            console.log(`[Session] 重做到步骤 ${this.currentStep + 1}/${this.history.length}`);
            return this.getCurrentState();
        }
        return null;
    }
    
    // 获取当前状态
    getCurrentState() {
        if (this.currentStep >= 0 && this.currentStep < this.history.length) {
            return this.history[this.currentStep];
        }
        return null;
    }
    
    // 是否可以撤销
    canUndo() {
        return this.currentStep > 0;
    }
    
    // 是否可以重做
    canRedo() {
        return this.currentStep < this.history.length - 1;
    }
    
    // 获取历史记录信息
    getInfo() {
        return {
            sessionId: this.sessionId,
            totalSteps: this.history.length,
            currentStep: this.currentStep + 1,
            canUndo: this.canUndo(),
            canRedo: this.canRedo(),
            maxHistory: this.maxHistory
        };
    }
    
    // 清空历史
    clear() {
        this.history = [];
        this.currentStep = -1;
        console.log('[Session] 历史记录已清空');
    }
}

// 创建session实例
let canvasSession = new CanvasSession(50);

// 新增功能变量
let currentTool = 'brush'; // brush, pencil, marker, spray
let currentBrushType = 'round'; // round, square
let currentShapeTool = null; // line, rect, circle, arrow
let shapeStartPos = null;
let tempCanvas = null;
let colorHistory = ['#000000']; // 颜色历史
let pressureSensitive = true; // 压感支持
let lastPressure = 0.5; // 最后的压感值
let pressureHistory = []; // 压感历史（用于平滑）
const PRESSURE_SMOOTH_COUNT = 3; // 压感平滑窗口大小

// 缩放功能变量
let zoomLevel = 1; // 当前缩放级别
const ZOOM_STEP = 0.1; // 缩放步长
const MIN_ZOOM = 0.25; // 最小缩放25%
const MAX_ZOOM = 3; // 最大缩放300%

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('[Canvas] DOM加载完成，开始初始化...');
    
    canvas = document.getElementById('sketchCanvas');
    ctx = canvas.getContext('2d', { willReadFrequently: true });
    
    if (!canvas || !ctx) {
        console.error('[Canvas] 错误: 无法获取画布元素或上下文');
        return;
    }
    
    console.log('[Canvas] 画布元素获取成功');
    
    // 初始化画布大小
    applyResolution();
    
    // 绑定事件
    bindEvents();
    console.log('[Canvas] 事件绑定完成');
    
    // 初始化工具栏
    initializeTools();
    
    // 初始化工具栏折叠功能
    initializeToolbarToggle();
    
    // 初始化全屏功能
    initializeFullscreen();
    
    // 初始化缩放功能
    initializeZoom();
    
    // 初始化工具选项面板
    initializeToolOptions();
    
    // 检测设备和压感支持
    detectDeviceAndPressure();
    
    // 保存初始空画布状态
    saveState();
    
    // 初始化历史按钮状态
    updateHistoryButtons();
    
    // 显示session信息
    console.log('[Session] 已创建新会话:', canvasSession.getInfo());
    console.log('[Canvas] 初始化完成！可以开始绘画');
});

// 检测设备和压感支持
function detectDeviceAndPressure() {
    const isTouch = 'ontouchstart' in window;
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isAndroid = /Android/.test(navigator.userAgent);
    
    console.log('=== 设备检测 ===');
    console.log('触摸设备:', isTouch);
    console.log('iOS设备:', isIOS);
    console.log('Android设备:', isAndroid);
    console.log('User Agent:', navigator.userAgent);
    
    // 测试压感支持
    if (isTouch) {
        console.log('✅ 支持触摸事件');
        canvas.addEventListener('touchstart', function testPressure(e) {
            if (e.touches && e.touches[0]) {
                const touch = e.touches[0];
                console.log('=== 压感测试 ===');
                console.log('force:', touch.force);
                console.log('webkitForce:', touch.webkitForce);
                console.log('radiusX:', touch.radiusX);
                console.log('radiusY:', touch.radiusY);
                console.log('压感支持:', typeof touch.force !== 'undefined' || typeof touch.webkitForce !== 'undefined' ? '✅ 是' : '❌ 否');
            }
            canvas.removeEventListener('touchstart', testPressure);
        }, { once: true });
    }
}

// 应用分辨率
function applyResolution() {
    const select = document.getElementById('resolutionSelect');
    const [width, height] = select.value.split('x').map(Number);
    
    console.log(`[Canvas] 应用分辨率: ${width}x${height}`);
    
    // 保存旧的画布内容（如果有）
    let hasContent = false;
    const tempCanvas = document.createElement('canvas');
    if (canvas.width > 0 && canvas.height > 0) {
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.drawImage(canvas, 0, 0);
        hasContent = true;
    }
    
    // 设置新的画布尺寸
    canvas.width = width;
    canvas.height = height;
    
    // 设置白色背景层尺寸
    const whiteBackground = document.getElementById('whiteBackground');
    if (whiteBackground) {
        whiteBackground.style.width = width + 'px';
        whiteBackground.style.height = height + 'px';
    }
    
    // 设置canvas-box尺寸以匹配画布
    const canvasBox = document.getElementById('canvasBox');
    if (canvasBox) {
        canvasBox.style.width = width + 'px';
        canvasBox.style.height = height + 'px';
    }
    
    // 如果有旧内容，尝试恢复
    if (hasContent && tempCanvas.width > 0) {
        const scale = Math.min(width / tempCanvas.width, height / tempCanvas.height);
        const scaledWidth = tempCanvas.width * scale;
        const scaledHeight = tempCanvas.height * scale;
        const x = (width - scaledWidth) / 2;
        const y = (height - scaledHeight) / 2;
        ctx.drawImage(tempCanvas, x, y, scaledWidth, scaledHeight);
    }
    
    // 隐藏提示
    const hint = document.querySelector('.canvas-hint');
    if (hint) hint.style.display = 'none';
    
    console.log(`[Canvas] 画布实际尺寸: ${canvas.width}x${canvas.height}`);
    console.log(`[Canvas] 画布可以绘制: ${canvas.getContext ? '✓' : '✗'}`);
}

// 绑定事件
function bindEvents() {
    // 分辨率应用按钮
    document.getElementById('applyResolution').addEventListener('click', applyResolution);
    
    // 画布绘图事件
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
    
    // 触摸事件支持
    canvas.addEventListener('touchstart', handleTouch);
    canvas.addEventListener('touchmove', handleTouch);
    canvas.addEventListener('touchend', handleTouch);
    canvas.addEventListener('touchcancel', handleTouch);
    
    // 工具按钮
    const imageFileInput = document.getElementById('imageFileInput');
    if (imageFileInput) {
        imageFileInput.addEventListener('change', handleImageImport);
    }
    
    const eraserBtn = document.getElementById('eraserBtn');
    if (eraserBtn) {
        eraserBtn.addEventListener('click', toggleEraser);
    }
    
    const undoBtn = document.getElementById('undoBtn');
    if (undoBtn) {
        undoBtn.addEventListener('click', undo);
    }
    
    const redoBtn = document.getElementById('redoBtn');
    if (redoBtn) {
        redoBtn.addEventListener('click', redo);
    }
    
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearCanvas);
    }
    
    // 生成按钮
    document.getElementById('generateBtn').addEventListener('click', generateImage);
    
    // 视图模式切换
    document.getElementById('overlayModeBtn').addEventListener('click', () => switchViewMode('overlay'));
    document.getElementById('sideBySideBtn').addEventListener('click', () => switchViewMode('side'));
    document.getElementById('hideModeBtn').addEventListener('click', () => switchViewMode('hide'));
    
    // 叠加模式控制
    document.getElementById('toggleSketchLayer').addEventListener('change', toggleSketchLayer);
    document.getElementById('toggleGeneratedLayer').addEventListener('change', toggleGeneratedLayer);
    document.getElementById('generatedOpacitySlider').addEventListener('input', updateGeneratedOpacity);
    document.getElementById('compareSlider').addEventListener('input', updateCompareSlider);
    
    // 结果操作按钮
    document.getElementById('regenerateBtn').addEventListener('click', regenerateImage);
    document.getElementById('clearBackgroundBtn').addEventListener('click', clearBackground);
    document.getElementById('downloadGeneratedBtn').addEventListener('click', downloadGenerated);
    document.getElementById('exportVideoBtn').addEventListener('click', exportAnimatedVideo);
    document.getElementById('saveToGalleryBtn').addEventListener('click', saveToGallery);
    document.getElementById('newSketchBtn').addEventListener('click', newSketch);
}

// 初始化工具栏
function initializeTools() {
    const brushSize = document.getElementById('brushSize');
    const brushColor = document.getElementById('brushColor');
    const brushOpacity = document.getElementById('brushOpacity');
    
    // 画笔大小
    if (brushSize) {
        brushSize.addEventListener('input', (e) => {
            brushSize = parseInt(e.target.value);
            document.getElementById('brushSizeValue').textContent = brushSize;
        });
    }
    
    // 大小预设按钮
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const size = parseInt(e.target.dataset.size);
            brushSize = size;
            const sizeInput = document.getElementById('brushSize');
            if (sizeInput) sizeInput.value = size;
            const sizeValue = document.getElementById('brushSizeValue');
            if (sizeValue) sizeValue.textContent = size;
        });
    });
    
    // 画笔颜色
    if (brushColor) {
        brushColor.addEventListener('input', (e) => {
            currentColor = e.target.value;
            isEraser = false;
            const eraserBtn = document.getElementById('eraserBtn');
            if (eraserBtn) eraserBtn.classList.remove('active');
            addColorToHistory(currentColor);
        });
    }
    
    // 快速颜色选择
    document.querySelectorAll('.color-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const color = e.target.dataset.color;
            if (color) {
                currentColor = color;
                if (brushColor) brushColor.value = color;
                isEraser = false;
                const eraserBtn = document.getElementById('eraserBtn');
                if (eraserBtn) eraserBtn.classList.remove('active');
                addColorToHistory(color);
                // 高亮当前颜色
                document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            }
        });
    });
    
    // 透明度
    if (brushOpacity) {
        brushOpacity.addEventListener('input', (e) => {
            currentOpacity = e.target.value / 100;
            const opacityValue = document.getElementById('brushOpacityValue');
            if (opacityValue) opacityValue.textContent = e.target.value;
        });
    }
    
    // 笔触类型按钮
    const roundBtn = document.getElementById('roundBtn');
    if (roundBtn) {
        roundBtn.addEventListener('click', () => {
            currentBrushType = 'round';
            document.querySelectorAll('.brush-type-btn').forEach(btn => btn.classList.remove('active'));
            roundBtn.classList.add('active');
        });
    }
    
    const squareBtn = document.getElementById('squareBtn');
    if (squareBtn) {
        squareBtn.addEventListener('click', () => {
            currentBrushType = 'square';
            document.querySelectorAll('.brush-type-btn').forEach(btn => btn.classList.remove('active'));
            squareBtn.classList.add('active');
        });
    }
    
    // 形状工具按钮
    const lineBtn = document.getElementById('lineBtn');
    if (lineBtn) lineBtn.addEventListener('click', () => selectShapeTool('line'));
    
    const rectBtn = document.getElementById('rectBtn');
    if (rectBtn) rectBtn.addEventListener('click', () => selectShapeTool('rect'));
    
    const circleBtn = document.getElementById('circleBtn');
    if (circleBtn) circleBtn.addEventListener('click', () => selectShapeTool('circle'));
    
    const arrowBtn = document.getElementById('arrowBtn');
    if (arrowBtn) arrowBtn.addEventListener('click', () => selectShapeTool('arrow'));
    
    // 初始化颜色历史
    updateColorHistory();
}

// 开始绘画
function startDrawing(e) {
    isDrawing = true;
    const pos = getMousePos(e);
    
    // 如果是形状工具，记录起始点
    if (currentShapeTool) {
        shapeStartPos = pos;
    } else {
        ctx.beginPath();
        ctx.moveTo(pos.x, pos.y);
    }
}

// 压感平滑函数
function smoothPressure(rawPressure) {
    // 过滤异常值：如果压感突然跳变超过0.3，使用上一次的值
    if (pressureHistory.length > 0) {
        const lastValue = pressureHistory[pressureHistory.length - 1];
        if (Math.abs(rawPressure - lastValue) > 0.3) {
            console.log(`压感异常跳变: ${lastValue.toFixed(2)} -> ${rawPressure.toFixed(2)}, 已过滤`);
            rawPressure = lastValue;
        }
    }
    
    // 添加到历史记录
    pressureHistory.push(rawPressure);
    if (pressureHistory.length > PRESSURE_SMOOTH_COUNT) {
        pressureHistory.shift();
    }
    
    // 计算移动平均
    const sum = pressureHistory.reduce((a, b) => a + b, 0);
    const smoothed = sum / pressureHistory.length;
    
    lastPressure = smoothed;
    return smoothed;
}

// 绘画
function draw(e) {
    if (!isDrawing) return;
    
    const pos = getMousePos(e);
    
    // 如果是形状工具，不用持续绘制
    if (currentShapeTool) {
        return;
    }
    
    // 获取压力值
    let pressure = 1.0;
    if (pressureSensitive) {
        let rawPressure = 1.0;
        let pressureDetected = false;
        
        // 方法1: 从原始触摸事件获取
        if (e.originalTouchEvent && e.originalTouchEvent.touches && e.originalTouchEvent.touches[0]) {
            const touch = e.originalTouchEvent.touches[0];
            // iOS Safari 支持 force (0-1)
            if (typeof touch.force !== 'undefined' && touch.force > 0) {
                rawPressure = touch.force;
                pressureDetected = true;
            }
            // Android Chrome 支持 webkitForce
            else if (typeof touch.webkitForce !== 'undefined' && touch.webkitForce > 0) {
                rawPressure = touch.webkitForce;
                pressureDetected = true;
            }
        }
        // 方法2: 直接从事件获取（兼容处理）
        else if (e.touches && e.touches[0]) {
            const touch = e.touches[0];
            if (typeof touch.force !== 'undefined' && touch.force > 0) {
                rawPressure = touch.force;
                pressureDetected = true;
            } else if (typeof touch.webkitForce !== 'undefined' && touch.webkitForce > 0) {
                rawPressure = touch.webkitForce;
                pressureDetected = true;
            }
        }
        
        // 如果检测到压感，应用平滑算法
        if (pressureDetected) {
            // 限制压力值范围 0.1-1.0
            rawPressure = Math.max(0.1, Math.min(1.0, rawPressure));
            // 应用平滑算法
            pressure = smoothPressure(rawPressure);
        } else {
            // 如果无法读取压感，使用上一次的值
            pressure = lastPressure;
        }
        
        // 更新压感指示器
        updatePressureIndicator(pressure);
    }
    
    ctx.lineWidth = currentSize * pressure;
    ctx.lineCap = currentBrushType === 'round' ? 'round' : 'square';
    ctx.lineJoin = currentBrushType === 'round' ? 'round' : 'miter';
    
    if (isEraser) {
        ctx.globalCompositeOperation = 'destination-out';
    } else {
        ctx.globalCompositeOperation = 'source-over';
        ctx.strokeStyle = currentColor;
    }
    
    ctx.globalAlpha = currentOpacity;
    
    // 根据不同工具类型绘制
    switch (currentTool) {
        case 'brush':
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
            break;
        case 'pencil':
            ctx.lineWidth = currentSize * 0.5 * pressure; // 铅笔更细
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
            break;
        case 'marker':
            ctx.globalAlpha = currentOpacity * 0.6; // 马克笔有透明度
            ctx.lineWidth = currentSize * 1.5 * pressure; // 马克笔更宽
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
            break;
        case 'spray':
            drawSpray(pos.x, pos.y, currentSize * pressure);
            break;
    }
    
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
}

// 停止绘画
function stopDrawing(e) {
    if (isDrawing) {
        // 如果是形状工具，绘制最终形状
        if (currentShapeTool && shapeStartPos && e) {
            const pos = getMousePos(e);
            drawShape(shapeStartPos.x, shapeStartPos.y, pos.x, pos.y, currentShapeTool);
            shapeStartPos = null;
        }
        
        isDrawing = false;
        ctx.globalAlpha = 1;
        saveState();
        
        // 清理压感历史
        pressureHistory = [];
        lastPressure = 0.5;
    }
}

// 获取鼠标位置
function getMousePos(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
    };
}

// 触摸事件处理
function handleTouch(e) {
    e.preventDefault();
    
    // touchend时直接停止绘制，不读取压感
    if (e.type === 'touchend' || e.type === 'touchcancel') {
        stopDrawing(null);
        // 重置压感历史
        pressureHistory = [];
        lastPressure = 0.5;
        return;
    }
    
    const touch = e.touches[0];
    if (!touch) return;
    
    // 根据触摸事件类型分发对应的鼠标事件
    let eventType;
    if (e.type === 'touchstart') {
        eventType = 'mousedown';
        // touchstart时重置压感历史
        pressureHistory = [];
    } else if (e.type === 'touchmove') {
        eventType = 'mousemove';
    }
    
    const mouseEvent = new MouseEvent(eventType, {
        clientX: touch.clientX,
        clientY: touch.clientY,
        bubbles: true
    });
    
    // 将原始触摸事件附加到鼠标事件上，用于压感检测
    mouseEvent.originalTouchEvent = e;
    canvas.dispatchEvent(mouseEvent);
}

// 切换橡皮擦
function toggleEraser() {
    isEraser = !isEraser;
    const btn = document.getElementById('eraserBtn');
    btn.classList.toggle('active', isEraser);
}

// 处理图片导入
function handleImageImport(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
        alert('请选择图片文件！');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(event) {
        const img = new Image();
        img.onload = function() {
            // 询问用户导入方式
            const choice = confirm(
                '导入图片选项：\n\n' +
                '【确定】- 作为底图（可在上面绘制）\n' +
                '【取消】- 直接导入到画布（替换当前内容）\n\n' +
                '提示：iPad用户可以在备忘录等应用画好后导入'
            );
            
            if (choice) {
                // 作为底图
                importAsBackground(img);
            } else {
                // 导入到画布
                importToCanvas(img);
            }
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
    
    // 重置文件输入，允许重复选择同一文件
    e.target.value = '';
}

// 将图片导入为底图
function importAsBackground(img) {
    const backgroundImg = document.getElementById('generatedBackground');
    backgroundImg.src = img.src;
    backgroundImg.style.display = 'block';
    generatedImageUrl = img.src;
    window.generatedImageUrl = img.src;
    
    // 显示结果控制区域
    document.getElementById('resultSection').style.display = 'block';
    document.getElementById('overlayControls').style.display = 'flex';
    
    // 设置为叠加模式
    switchViewMode('overlay');
    
    // 提示用户
    console.log('图片已作为底图导入，现在可以在上面绘制了！');
    
    // iPad自动关闭工具栏
    if (window.innerWidth <= 1366) {
        const toolbar = document.getElementById('canvasToolbar');
        if (toolbar) {
            toolbar.classList.remove('active');
        }
    }
}

// 将图片直接导入到画布
function importToCanvas(img) {
    // 调整图片大小以适应画布
    const scale = Math.min(
        canvas.width / img.width,
        canvas.height / img.height
    );
    const scaledWidth = img.width * scale;
    const scaledHeight = img.height * scale;
    const x = (canvas.width - scaledWidth) / 2;
    const y = (canvas.height - scaledHeight) / 2;
    
    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 绘制图片
    ctx.drawImage(img, x, y, scaledWidth, scaledHeight);
    
    // 保存状态
    saveState();
    
    console.log('图片已导入到画布！');
    
    // iPad自动关闭工具栏
    if (window.innerWidth <= 1366) {
        const toolbar = document.getElementById('canvasToolbar');
        if (toolbar) {
            toolbar.classList.remove('active');
        }
    }
}

// 清空画布
function clearCanvas() {
    if (confirm('确定要清空画布吗？')) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        saveState();
    }
}

// 保存状态
function saveState() {
    const dataUrl = canvas.toDataURL();
    canvasSession.saveState(dataUrl);
    updateHistoryButtons();
}

// 撤销
function undo() {
    const state = canvasSession.undo();
    if (state) {
        restoreFromState(state.dataUrl);
        updateHistoryButtons();
    }
}

// 重做
function redo() {
    const state = canvasSession.redo();
    if (state) {
        restoreFromState(state.dataUrl);
        updateHistoryButtons();
    }
}

// 从状态恢复
function restoreFromState(dataUrl) {
    const img = new Image();
    img.src = dataUrl;
    img.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
    };
}

// 更新历史按钮状态
function updateHistoryButtons() {
    const info = canvasSession.getInfo();
    
    const undoBtn = document.getElementById('undoBtn');
    const redoBtn = document.getElementById('redoBtn');
    
    if (undoBtn) {
        undoBtn.disabled = !info.canUndo;
        undoBtn.classList.toggle('disabled', !info.canUndo);
        undoBtn.title = info.canUndo ? `撤销 (${info.currentStep}/${info.totalSteps})` : '撤销 (无可撤销操作)';
    }
    
    if (redoBtn) {
        redoBtn.disabled = !info.canRedo;
        redoBtn.classList.toggle('disabled', !info.canRedo);
        redoBtn.title = info.canRedo ? `重做 (${info.currentStep}/${info.totalSteps})` : '重做 (无可重做操作)';
    }
    
    // 在控制台显示session信息（调试用）
    if (info.totalSteps > 0) {
        console.log(`[History] 步骤: ${info.currentStep}/${info.totalSteps} | 撤销: ${info.canUndo} | 重做: ${info.canRedo}`);
    }
}

// 选择绘图工具
function selectTool(tool) {
    const btn = document.getElementById(tool + 'Btn');
    if (!btn) return;
    
    const wasActive = btn.classList.contains('active');
    
    // 隐藏所有选项面板
    document.querySelectorAll('.tool-options-panel').forEach(panel => {
        panel.style.display = 'none';
    });
    
    // 如果工具已经激活，显示其选项面板
    if (wasActive) {
        const optionsPanel = document.getElementById(tool + 'Options');
        if (optionsPanel) {
            optionsPanel.style.display = 'block';
        }
    } else {
        // 否则激活该工具
        currentTool = tool;
        currentShapeTool = null;
        isEraser = false;
        
        // 更新按钮状态
        document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('eraserBtn').classList.remove('active');
    }
}

// 选择笔触类型
function selectBrushType(type) {
    currentBrushType = type;
    document.querySelectorAll('.brush-type-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(type + 'Btn').classList.add('active');
}

// 选择形状工具
function selectShapeTool(shape) {
    currentShapeTool = shape;
    currentTool = 'shape';
    isEraser = false;
    
    // 更新按钮状态
    document.querySelectorAll('.shape-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(shape + 'Btn').classList.add('active');
    document.querySelectorAll('.tool-mode-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById('eraserBtn').classList.remove('active');
}

// 绘制喷雾效果
function drawSpray(x, y, radius) {
    const density = 20;
    for (let i = 0; i < density; i++) {
        const angle = Math.random() * Math.PI * 2;
        const distance = Math.random() * radius;
        const sprayX = x + Math.cos(angle) * distance;
        const sprayY = y + Math.sin(angle) * distance;
        
        ctx.fillStyle = currentColor;
        ctx.globalAlpha = currentOpacity * 0.5;
        ctx.fillRect(sprayX, sprayY, 1, 1);
    }
}

// 绘制形状
function drawShape(x1, y1, x2, y2, shape) {
    ctx.globalCompositeOperation = 'source-over';
    ctx.strokeStyle = currentColor;
    ctx.lineWidth = currentSize;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.globalAlpha = currentOpacity;
    
    ctx.beginPath();
    
    switch (shape) {
        case 'line':
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            break;
        case 'rect':
            const width = x2 - x1;
            const height = y2 - y1;
            ctx.rect(x1, y1, width, height);
            break;
        case 'circle':
            const radius = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
            ctx.arc(x1, y1, radius, 0, Math.PI * 2);
            break;
        case 'arrow':
            drawArrow(x1, y1, x2, y2);
            return; // drawArrow已经包含stroke
    }
    
    ctx.stroke();
}

// 绘制箭头
function drawArrow(x1, y1, x2, y2) {
    const headLength = Math.min(currentSize * 3, 20);
    const angle = Math.atan2(y2 - y1, x2 - x1);
    
    // 绘制线条
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
    
    // 绘制箭头
    ctx.beginPath();
    ctx.moveTo(x2, y2);
    ctx.lineTo(
        x2 - headLength * Math.cos(angle - Math.PI / 6),
        y2 - headLength * Math.sin(angle - Math.PI / 6)
    );
    ctx.moveTo(x2, y2);
    ctx.lineTo(
        x2 - headLength * Math.cos(angle + Math.PI / 6),
        y2 - headLength * Math.sin(angle + Math.PI / 6)
    );
    ctx.stroke();
}

// 添加颜色到历史记录
function addColorToHistory(color) {
    if (!colorHistory.includes(color)) {
        colorHistory.unshift(color);
        if (colorHistory.length > 10) {
            colorHistory.pop();
        }
        updateColorHistory();
    }
}

// 更新颜色历史显示
function updateColorHistory() {
    const historyContainer = document.getElementById('colorHistory');
    historyContainer.innerHTML = '';
    
    colorHistory.forEach(color => {
        const btn = document.createElement('button');
        btn.className = 'color-history-btn';
        btn.style.background = color;
        if (color === '#FFFFFF' || color === '#ffffff') {
            btn.style.border = '1px solid #ddd';
        }
        btn.title = color;
        btn.addEventListener('click', () => {
            currentColor = color;
            document.getElementById('brushColor').value = color;
            isEraser = false;
            document.getElementById('eraserBtn').classList.remove('active');
        });
        historyContainer.appendChild(btn);
    });
}

// 更新压感指示器
function updatePressureIndicator(pressure) {
    const indicator = document.getElementById('pressureIndicator');
    if (!indicator || indicator.style.display === 'none') return;
    
    const barFill = document.getElementById('pressureBarFill');
    const valueDisplay = document.getElementById('pressureValue');
    
    if (barFill && valueDisplay) {
        // 更新进度条
        const percentage = (pressure * 100).toFixed(0);
        barFill.style.width = percentage + '%';
        
        // 根据压力值改变颜色
        if (pressure < 0.3) {
            barFill.style.background = '#4CAF50'; // 绿色-轻
        } else if (pressure < 0.7) {
            barFill.style.background = '#FF9800'; // 橙色-中
        } else {
            barFill.style.background = '#f44336'; // 红色-重
        }
        
        // 更新数值显示
        valueDisplay.textContent = pressure.toFixed(2);
    }
}

// 生成图片
async function generateImage() {
    const prompt = document.getElementById('promptInput').value.trim();
    
    if (!prompt) {
        alert('请输入提示词！');
        return;
    }
    
    // 检查画布是否为空
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    let isEmpty = true;
    for (let i = 0; i < data.length; i += 4) {
        if (data[i] !== 255 || data[i+1] !== 255 || data[i+2] !== 255) {
            isEmpty = false;
            break;
        }
    }
    
    if (isEmpty) {
        alert('请先在画布上绘制一些内容！');
        return;
    }
    
    // 显示加载提示
    document.getElementById('loadingOverlay').style.display = 'flex';
    
    try {
        // 创建一个临时canvas，将透明背景的sketch合成到白色背景上
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        const tempCtx = tempCanvas.getContext('2d');
        
        // 先填充白色背景
        tempCtx.fillStyle = 'white';
        tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
        
        // 然后将sketch内容绘制上去
        tempCtx.drawImage(canvas, 0, 0);
        
        // 将合成后的画布转换为blob
        const sketchBlob = await new Promise(resolve => tempCanvas.toBlob(resolve, 'image/png'));
        
        // 获取当前分辨率
        const resolution = document.getElementById('resolutionSelect').value;
        const [width, height] = resolution.split('x').map(Number);
        
        // 创建FormData
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('sketch', sketchBlob, 'sketch.png');
        formData.append('width', width);
        formData.append('height', height);
        formData.append('style', 'realistic');
        formData.append('color_preference', 'colorful');
        
        console.log(`生成图片分辨率: ${width}x${height}`);
        
        // 调用API生成图片
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`服务器错误 (${response.status})`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || '生成失败');
        }
        
        // 创建带白色背景的sketch用于显示对比
        const displayCanvas = document.createElement('canvas');
        displayCanvas.width = canvas.width;
        displayCanvas.height = canvas.height;
        const displayCtx = displayCanvas.getContext('2d');
        displayCtx.fillStyle = 'white';
        displayCtx.fillRect(0, 0, displayCanvas.width, displayCanvas.height);
        displayCtx.drawImage(canvas, 0, 0);
        
        // 显示结果
        displayResults(displayCanvas.toDataURL(), data.image_url);
        
    } catch (error) {
        console.error('生成失败:', error);
        alert(`生成失败：${error.message}`);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 显示结果
function displayResults(sketchUrl, generatedUrl) {
    // 保存生成的图片URL（同时更新全局变量供保存功能使用）
    generatedImageUrl = generatedUrl;
    window.generatedImageUrl = generatedUrl;
    
    console.log('生成图片URL已保存:', generatedUrl);
    
    // 显示结果区域
    document.getElementById('resultSection').style.display = 'block';
    
    // 设置并排对比图片
    document.getElementById('sketchImageSide').src = sketchUrl;
    document.getElementById('generatedImageSide').src = generatedUrl;
    
    // 将生成的图片设置为canvas背景
    const backgroundImg = document.getElementById('generatedBackground');
    const whiteBackground = document.getElementById('whiteBackground');
    
    backgroundImg.onload = function() {
        // 确保图片与canvas尺寸一致
        backgroundImg.style.width = canvas.width + 'px';
        backgroundImg.style.height = canvas.height + 'px';
        whiteBackground.style.width = canvas.width + 'px';
        whiteBackground.style.height = canvas.height + 'px';
        backgroundImg.style.display = 'block';
        
        console.log(`分层设置完成: ${canvas.width}x${canvas.height}`);
        console.log('z-index: 白色背景(1) < 生成图(2) < 手绘线条(3)');
    };
    backgroundImg.src = generatedUrl;
    
    // 默认显示叠放模式
    switchViewMode('overlay');
    
    // 滚动到结果区域
    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
}

// 切换视图模式
function switchViewMode(mode) {
    currentViewMode = mode;
    
    const sideBySideView = document.getElementById('sideBySideView');
    const overlayHint = document.getElementById('overlayHint');
    const overlayControls = document.getElementById('overlayControls');
    const overlayModeBtn = document.getElementById('overlayModeBtn');
    const sideBySideBtn = document.getElementById('sideBySideBtn');
    const hideModeBtn = document.getElementById('hideModeBtn');
    const backgroundImg = document.getElementById('generatedBackground');
    
    // 移除所有按钮的active状态
    overlayModeBtn.classList.remove('active');
    sideBySideBtn.classList.remove('active');
    hideModeBtn.classList.remove('active');
    
    if (mode === 'overlay') {
        // 叠放模式：在canvas底层显示生成图
        sideBySideView.style.display = 'none';
        overlayHint.style.display = 'block';
        overlayControls.style.display = 'block';
        backgroundImg.style.display = 'block';
        overlayModeBtn.classList.add('active');
        
        // 滚动到画布区域
        document.querySelector('.canvas-section').scrollIntoView({ behavior: 'smooth' });
    } else if (mode === 'side') {
        // 并排模式
        sideBySideView.style.display = 'grid';
        overlayHint.style.display = 'none';
        overlayControls.style.display = 'none';
        backgroundImg.style.display = 'none';
        sideBySideBtn.classList.add('active');
    } else if (mode === 'hide') {
        // 隐藏模式
        sideBySideView.style.display = 'none';
        overlayHint.style.display = 'none';
        overlayControls.style.display = 'none';
        backgroundImg.style.display = 'none';
        hideModeBtn.classList.add('active');
    }
}

// 重新生成图片
async function regenerateImage() {
    const prompt = document.getElementById('promptInput').value.trim();
    
    if (!prompt) {
        alert('请输入提示词！');
        return;
    }
    
    // 直接调用生成函数
    await generateImage();
}

// 清除背景图
function clearBackground() {
    if (confirm('确定要清除背景图吗？')) {
        const backgroundImg = document.getElementById('generatedBackground');
        backgroundImg.style.display = 'none';
        backgroundImg.src = '';
        generatedImageUrl = '';
        window.generatedImageUrl = '';
        
        // 隐藏结果区域
        document.getElementById('resultSection').style.display = 'none';
        document.getElementById('overlayControls').style.display = 'none';
        
        // 滚动到画布
        document.querySelector('.canvas-section').scrollIntoView({ behavior: 'smooth' });
    }
}

// 切换手绘线条图层
function toggleSketchLayer() {
    const showSketch = document.getElementById('toggleSketchLayer').checked;
    canvas.style.opacity = showSketch ? '1' : '0';
}

// 切换生成图片图层
function toggleGeneratedLayer() {
    const showGenerated = document.getElementById('toggleGeneratedLayer').checked;
    const backgroundImg = document.getElementById('generatedBackground');
    backgroundImg.style.opacity = showGenerated ? document.getElementById('generatedOpacitySlider').value / 100 : '0';
}

// 更新生成图片透明度
function updateGeneratedOpacity() {
    const slider = document.getElementById('generatedOpacitySlider');
    const value = slider.value;
    const backgroundImg = document.getElementById('generatedBackground');
    
    if (document.getElementById('toggleGeneratedLayer').checked) {
        backgroundImg.style.opacity = value / 100;
    }
    
    document.getElementById('opacityValue').textContent = value;
}

// 更新对比滑块
function updateCompareSlider() {
    const slider = document.getElementById('compareSlider');
    const value = slider.value;
    const backgroundImg = document.getElementById('generatedBackground');
    
    // 使用clip-path实现左右对比效果
    backgroundImg.style.clipPath = `inset(0 ${100 - value}% 0 0)`;
    
    document.getElementById('compareValue').textContent = value;
}

// 下载生成图
function downloadGenerated() {
    if (!generatedImageUrl) {
        alert('没有可下载的生成图！');
        return;
    }
    
    const link = document.createElement('a');
    link.download = `generated_${Date.now()}.png`;
    link.href = generatedImageUrl;
    link.click();
}

// 保存到作品集
async function saveToGallery() {
    if (!generatedImageUrl) {
        alert('没有可保存的生成图！');
        return;
    }
    
    const prompt = document.getElementById('promptInput').value;
    
    try {
        // 将图片URL转换为blob
        const response = await fetch(generatedImageUrl);
        const blob = await response.blob();
        
        // 创建FormData
        const formData = new FormData();
        formData.append('image', blob, 'artwork.png');
        formData.append('title', prompt);
        formData.append('description', '手绘画布生成');
        
        // 调用保存API
        const saveResponse = await fetch('/api/save-artwork', {
            method: 'POST',
            body: formData
        });
        
        const data = await saveResponse.json();
        
        if (data.success) {
            alert('保存成功！');
        } else {
            throw new Error(data.error || '保存失败');
        }
    } catch (error) {
        console.error('保存失败:', error);
        alert(`保存失败：${error.message}`);
    }
}

// 新建画布
function newSketch() {
    if (confirm('确定要新建画布吗？当前内容将被清空。')) {
        // 清空画布（透明背景）
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawingHistory = [];
        historyStep = -1;
        saveState();
        
        // 清空提示词
        document.getElementById('promptInput').value = '';
        
        // 清除背景图
        const backgroundImg = document.getElementById('generatedBackground');
        backgroundImg.style.display = 'none';
        backgroundImg.src = '';
        generatedImageUrl = '';
        window.generatedImageUrl = '';
        
        // 隐藏结果区域
        document.getElementById('resultSection').style.display = 'none';
        document.getElementById('overlayControls').style.display = 'none';
        
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// 初始化工具栏折叠功能
function initializeToolbarToggle() {
    const toolbar = document.getElementById('canvasToolbar');
    const toggleBtn = document.getElementById('toolbarToggle');
    const closeBtn = document.getElementById('toolbarClose');
    
    if (!toolbar || !toggleBtn) return; // PC端没有这些元素
    
    // 点击折叠按钮打开工具栏
    toggleBtn.addEventListener('click', () => {
        toolbar.classList.add('active');
    });
    
    // 点击关闭按钮关闭工具栏
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            toolbar.classList.remove('active');
        });
    }
    
    // 点击工具栏外部区域关闭（iPad专用）
    document.addEventListener('click', (e) => {
        if (toolbar.classList.contains('active')) {
            const isClickInside = toolbar.contains(e.target) || (toggleBtn && toggleBtn.contains(e.target));
            if (!isClickInside) {
                toolbar.classList.remove('active');
            }
        }
    });
    
    // 选择工具后自动关闭工具栏（iPad专用）
    const toolButtons = toolbar.querySelectorAll('.tool-mode-btn, .brush-type-btn, .shape-btn, .action-btn');
    toolButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // 延迟关闭，让用户看到选择效果
            setTimeout(() => {
                if (window.innerWidth <= 1366) {
                    toolbar.classList.remove('active');
                }
            }, 300);
        });
    });
}

// 初始化工具选项面板
function initializeToolOptions() {
    // 画笔选项
    const brushSizeSlider = document.getElementById('brushSize');
    const brushSizeValue = document.getElementById('brushSizeValue');
    const brushOpacitySlider = document.getElementById('brushOpacity');
    const brushOpacityValue = document.getElementById('brushOpacityValue');
    
    if (brushSizeSlider) {
        brushSizeSlider.addEventListener('input', (e) => {
            brushSize = parseInt(e.target.value);
            brushSizeValue.textContent = brushSize;
        });
    }
    
    if (brushOpacitySlider) {
        brushOpacitySlider.addEventListener('input', (e) => {
            brushOpacity = parseInt(e.target.value);
            brushOpacityValue.textContent = brushOpacity + '%';
        });
    }
    
    // 铅笔选项
    const pencilSizeSlider = document.getElementById('pencilSize');
    const pencilSizeValue = document.getElementById('pencilSizeValue');
    
    if (pencilSizeSlider) {
        pencilSizeSlider.addEventListener('input', (e) => {
            brushSize = parseInt(e.target.value);
            pencilSizeValue.textContent = brushSize;
        });
    }
    
    // 马克笔选项
    const markerSizeSlider = document.getElementById('markerSize');
    const markerSizeValue = document.getElementById('markerSizeValue');
    const markerOpacitySlider = document.getElementById('markerOpacity');
    const markerOpacityValue = document.getElementById('markerOpacityValue');
    
    if (markerSizeSlider) {
        markerSizeSlider.addEventListener('input', (e) => {
            brushSize = parseInt(e.target.value);
            markerSizeValue.textContent = brushSize;
        });
    }
    
    if (markerOpacitySlider) {
        markerOpacitySlider.addEventListener('input', (e) => {
            brushOpacity = parseInt(e.target.value);
            markerOpacityValue.textContent = brushOpacity + '%';
        });
    }
    
    // 喷枪选项
    const sprayRangeSlider = document.getElementById('sprayRange');
    const sprayRangeValue = document.getElementById('sprayRangeValue');
    const sprayDensitySlider = document.getElementById('sprayDensity');
    const sprayDensityValue = document.getElementById('sprayDensityValue');
    
    if (sprayRangeSlider) {
        sprayRangeSlider.addEventListener('input', (e) => {
            sprayRange = parseInt(e.target.value);
            sprayRangeValue.textContent = sprayRange;
        });
    }
    
    if (sprayDensitySlider) {
        sprayDensitySlider.addEventListener('input', (e) => {
            sprayDensity = parseInt(e.target.value);
            sprayDensityValue.textContent = sprayDensity;
        });
    }
    
    // 点击工具栏外部或画布时关闭选项面板
    document.addEventListener('click', (e) => {
        const isToolbarClick = e.target.closest('.canvas-toolbar');
        const isOptionsPanel = e.target.closest('.tool-options-panel');
        
        if (!isToolbarClick && !isOptionsPanel) {
            document.querySelectorAll('.tool-options-panel').forEach(panel => {
                panel.style.display = 'none';
            });
        }
    });
}
// 初始化工具栏折叠功能
function initializeToolbarToggle() {
    const toggleButtons = document.querySelectorAll('.toolbar-toggle');
    
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const target = btn.dataset.target;
            const toolbar = target === 'left' ? 
                document.querySelector('.left-toolbar') : 
                document.querySelector('.right-toolbar');
            
            toolbar.classList.toggle('collapsed');
        });
    });
}

// 初始化全屏功能
function initializeFullscreen() {
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    const canvasSection = document.querySelector('.canvas-section');
    
    if (fullscreenBtn && canvasSection) {
        fullscreenBtn.addEventListener('click', () => {
            if (!document.fullscreenElement) {
                // 进入全屏
                canvasSection.requestFullscreen().then(() => {
                    canvasSection.classList.add('fullscreen');
                    fullscreenBtn.querySelector('i').classList.remove('fa-expand');
                    fullscreenBtn.querySelector('i').classList.add('fa-compress');
                }).catch(err => {
                    console.error('全屏失败:', err);
                });
            } else {
                // 退出全屏
                document.exitFullscreen();
            }
        });
        
        // 监听全屏变化（包括ESC键退出）
        document.addEventListener('fullscreenchange', () => {
            if (!document.fullscreenElement) {
                canvasSection.classList.remove('fullscreen');
                fullscreenBtn.querySelector('i').classList.remove('fa-compress');
                fullscreenBtn.querySelector('i').classList.add('fa-expand');
            }
        });
    }
}

// 初始化缩放功能
function initializeZoom() {
    const zoomInBtn = document.getElementById('zoomInBtn');
    const zoomOutBtn = document.getElementById('zoomOutBtn');
    const zoomResetBtn = document.getElementById('zoomResetBtn');
    const zoomLevelDisplay = document.getElementById('zoomLevel');
    const canvasBox = document.getElementById('canvasBox');
    const canvasWrapper = document.getElementById('canvasWrapper');
    
    // 检查必需元素
    if (!zoomLevelDisplay || !canvasBox || !canvasWrapper) {
        console.warn('[Zoom] 缩放功能元素未找到，跳过初始化');
        return;
    }

    // 更新缩放显示和应用缩放
    function updateZoomDisplay() {
        const percentage = Math.round(zoomLevel * 100);
        zoomLevelDisplay.textContent = `${percentage}%`;
        
        // 应用缩放到canvas容器
        canvasBox.style.transform = `scale(${zoomLevel})`;
    }

    // 放大
    if (zoomInBtn) {
        zoomInBtn.addEventListener('click', () => {
            if (zoomLevel < MAX_ZOOM) {
                zoomLevel = Math.min(MAX_ZOOM, zoomLevel + ZOOM_STEP);
                updateZoomDisplay();
            }
        });
    }

    // 缩小
    if (zoomOutBtn) {
        zoomOutBtn.addEventListener('click', () => {
            if (zoomLevel > MIN_ZOOM) {
                zoomLevel = Math.max(MIN_ZOOM, zoomLevel - ZOOM_STEP);
                updateZoomDisplay();
            }
        });
    }

    // 重置
    if (zoomResetBtn) {
        zoomResetBtn.addEventListener('click', () => {
            zoomLevel = 1;
            updateZoomDisplay();
        });
    }

    // 鼠标滚轮缩放（在canvas区域直接滚轮即可）
    canvasWrapper.addEventListener('wheel', (e) => {
        e.preventDefault();
        
        // 滚轮向上放大，向下缩小
        if (e.deltaY < 0) {
            // 放大
            if (zoomLevel < MAX_ZOOM) {
                zoomLevel = Math.min(MAX_ZOOM, zoomLevel + ZOOM_STEP);
                updateZoomDisplay();
            }
        } else {
            // 缩小
            if (zoomLevel > MIN_ZOOM) {
                zoomLevel = Math.max(MIN_ZOOM, zoomLevel - ZOOM_STEP);
                updateZoomDisplay();
            }
        }
    }, { passive: false });

    // 触摸手势缩放（双指缩放）
    let touchStartDistance = 0;
    let touchStartZoom = 1;

    canvasWrapper.addEventListener('touchstart', (e) => {
        if (e.touches.length === 2) {
            e.preventDefault();
            // 计算两指距离
            const touch1 = e.touches[0];
            const touch2 = e.touches[1];
            touchStartDistance = Math.hypot(
                touch2.clientX - touch1.clientX,
                touch2.clientY - touch1.clientY
            );
            touchStartZoom = zoomLevel;
        }
    }, { passive: false });

    canvasWrapper.addEventListener('touchmove', (e) => {
        if (e.touches.length === 2) {
            e.preventDefault();
            // 计算当前两指距离
            const touch1 = e.touches[0];
            const touch2 = e.touches[1];
            const currentDistance = Math.hypot(
                touch2.clientX - touch1.clientX,
                touch2.clientY - touch1.clientY
            );
            
            // 计算缩放比例
            const scale = currentDistance / touchStartDistance;
            let newZoom = touchStartZoom * scale;
            
            // 限制在最小和最大缩放范围内
            newZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, newZoom));
            
            if (newZoom !== zoomLevel) {
                zoomLevel = newZoom;
                updateZoomDisplay();
            }
        }
    }, { passive: false });

    canvasWrapper.addEventListener('touchend', (e) => {
        if (e.touches.length < 2) {
            touchStartDistance = 0;
        }
    }, { passive: false });

    // 初始化显示
    updateZoomDisplay();
}

// 导出MP4视频动画功能
async function exportAnimatedVideo() {
    console.log('=== 开始导出MP4视频 ===');
    console.log('generatedImageUrl:', generatedImageUrl);
    console.log('window.generatedImageUrl:', window.generatedImageUrl);
    
    // 检查两个变量，优先使用window.generatedImageUrl（项目恢复时设置的）
    const imageUrl = window.generatedImageUrl || generatedImageUrl;
    
    if (!imageUrl) {
        toast.warning('请先生成图片再导出视频');
        return;
    }
    
    // 同步两个变量
    generatedImageUrl = imageUrl;
    window.generatedImageUrl = imageUrl;

    try {
        // 显示加载提示
        const loadingOverlay = document.getElementById('loadingOverlay');
        const loadingText = loadingOverlay.querySelector('p');
        loadingText.textContent = '正在准备导出视频...';
        loadingOverlay.style.display = 'flex';

        // 创建临时画布用于渲染动画帧
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        const tempCtx = tempCanvas.getContext('2d');

        // 获取生成的图片元素（正确的ID是generatedBackground）
        const generatedImage = document.getElementById('generatedBackground');
        if (!generatedImage) {
            throw new Error('找不到生成的图片元素');
        }

        // 如果图片还未加载完成，等待加载
        if (!generatedImage.complete || !generatedImage.naturalWidth) {
            loadingText.textContent = '等待图片加载完成...';
            await new Promise((resolve, reject) => {
                generatedImage.onload = resolve;
                generatedImage.onerror = () => reject(new Error('图片加载失败'));
                setTimeout(() => reject(new Error('图片加载超时')), 10000);
            });
        }

        console.log('图片已就绪，尺寸:', generatedImage.naturalWidth, 'x', generatedImage.naturalHeight);

        // 动画参数 - 4个阶段，每个阶段1秒，30fps流畅动画
        const fps = 30;  // 30帧每秒，更流畅
        const stageDuration = 1;  // 每阶段1秒
        const framesPerStage = fps * stageDuration;  // 每阶段30帧
        const totalStages = 4;
        const totalFrames = framesPerStage * totalStages;  // 总共120帧

        console.log(`准备录制视频: ${totalFrames}帧, ${fps}fps, 总时长${totalStages}秒`);

        // 使用MediaRecorder录制canvas
        const stream = tempCanvas.captureStream(fps);
        
        // 尝试使用H264编码的MP4，如果不支持则使用WebM
        let mimeType = 'video/webm;codecs=h264';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = 'video/webm;codecs=vp9';
            if (!MediaRecorder.isTypeSupported(mimeType)) {
                mimeType = 'video/webm';
            }
        }
        
        console.log('使用编码格式:', mimeType);
        
        const mediaRecorder = new MediaRecorder(stream, {
            mimeType: mimeType,
            videoBitsPerSecond: 2500000  // 2.5Mbps，平衡质量和文件大小
        });

        const chunks = [];
        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) {
                chunks.push(e.data);
            }
        };

        mediaRecorder.onstop = async () => {
            console.log('录制完成，生成视频文件...');
            const blob = new Blob(chunks, { type: mimeType });
            console.log('视频大小:', (blob.size / 1024).toFixed(2), 'KB');
            
            // 确定文件扩展名
            const ext = mimeType.includes('h264') ? 'mp4' : 'webm';
            
            // 下载视频
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `sketch-animation-${Date.now()}.${ext}`;
            link.click();
            
            URL.revokeObjectURL(link.href);
            loadingOverlay.style.display = 'none';
            loadingText.textContent = 'AI正在生成图片，请稍候...';
            toast.success('视频导出成功！');
        };

        // 开始录制
        mediaRecorder.start();
        loadingText.textContent = '正在录制视频... 0%';

        // 渲染动画帧
        let currentFrame = 0;
        const frameInterval = 1000 / fps;

        const renderFrame = () => {
            if (currentFrame >= totalFrames) {
                mediaRecorder.stop();
                return;
            }

            // 清空临时画布
            tempCtx.clearRect(0, 0, tempCanvas.width, tempCanvas.height);
            
            // 第一步：绘制白色背景
            tempCtx.fillStyle = '#ffffff';
            tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);

            // 计算当前阶段和进度
            const stage = Math.floor(currentFrame / framesPerStage);
            const frameInStage = currentFrame % framesPerStage;
            const stageProgress = frameInStage / (framesPerStage - 1);
            
            let opacity, comparePosition;
            
            if (stage === 0) {
                // 阶段1: 透明度 100% → 0%
                opacity = 1 - stageProgress;
                comparePosition = 1;
            } else if (stage === 1) {
                // 阶段2: 透明度 0% → 100%
                opacity = stageProgress;
                comparePosition = 1;
            } else if (stage === 2) {
                // 阶段3: 从右向左删除
                opacity = 1;
                comparePosition = 1 - stageProgress;
            } else {
                // 阶段4: 从左向右恢复
                opacity = 1;
                comparePosition = stageProgress;
            }

            // 第二步：绘制生成的图片
            tempCtx.save();
            
            if (stage === 0 || stage === 1) {
                // 透明度控制
                tempCtx.globalAlpha = opacity;
                tempCtx.drawImage(generatedImage, 0, 0, tempCanvas.width, tempCanvas.height);
            } else {
                // 对比滑块控制
                const sliderX = tempCanvas.width * comparePosition;
                
                tempCtx.beginPath();
                tempCtx.rect(0, 0, sliderX, tempCanvas.height);
                tempCtx.clip();
                
                tempCtx.globalAlpha = 1;
                tempCtx.drawImage(generatedImage, 0, 0, tempCanvas.width, tempCanvas.height);
                
                // 分割线
                tempCtx.strokeStyle = '#ffffff';
                tempCtx.lineWidth = 3;
                tempCtx.shadowColor = 'rgba(0,0,0,0.5)';
                tempCtx.shadowBlur = 5;
                tempCtx.beginPath();
                tempCtx.moveTo(sliderX, 0);
                tempCtx.lineTo(sliderX, tempCanvas.height);
                tempCtx.stroke();
                tempCtx.shadowColor = 'transparent';
            }
            
            tempCtx.restore();

            // 第三步：绘制sketch层
            tempCtx.globalAlpha = 1;
            tempCtx.drawImage(canvas, 0, 0);

            // 更新进度
            currentFrame++;
            const progress = Math.round((currentFrame / totalFrames) * 100);
            loadingText.textContent = `正在录制视频... ${progress}%`;

            // 下一帧
            setTimeout(renderFrame, frameInterval);
        };

        // 开始渲染
        renderFrame();

    } catch (error) {
        console.error('导出视频失败:', error);
        console.error('错误详情:', error.stack);
        
        let errorMessage = '导出视频失败: ';
        if (error.message.includes('图片加载')) {
            errorMessage += '生成的图片加载失败，请重新生成图片后再试';
        } else if (error.message.includes('找不到')) {
            errorMessage += '找不到生成的图片，请先生成图片';
        } else {
            errorMessage += error.message;
        }
        
        toast.error(errorMessage);
        
        const loadingOverlay = document.getElementById('loadingOverlay');
        const loadingText = loadingOverlay.querySelector('p');
        loadingOverlay.style.display = 'none';
        loadingText.textContent = 'AI正在生成图片，请稍候...';
    }
}