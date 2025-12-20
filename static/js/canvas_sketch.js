// 手绘画布功能
let canvas, ctx;
let isDrawing = false;
let isEraser = false;
let currentColor = '#000000';
let currentSize = 5;
let currentOpacity = 1;
let drawingHistory = [];
let historyStep = -1;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    canvas = document.getElementById('sketchCanvas');
    ctx = canvas.getContext('2d');
    
    // 初始化画布大小
    applyResolution();
    
    // 绑定事件
    bindEvents();
    
    // 初始化工具栏
    initializeTools();
});

// 应用分辨率
function applyResolution() {
    const select = document.getElementById('resolutionSelect');
    const [width, height] = select.value.split('x').map(Number);
    
    canvas.width = width;
    canvas.height = height;
    
    // 设置画布背景为白色
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 保存初始状态
    saveState();
    
    // 隐藏提示
    document.querySelector('.canvas-hint').style.display = 'none';
    
    console.log(`画布分辨率设置为: ${width}x${height}`);
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
    canvas.addEventListener('touchend', stopDrawing);
    
    // 工具按钮
    document.getElementById('eraserBtn').addEventListener('click', toggleEraser);
    document.getElementById('clearBtn').addEventListener('click', clearCanvas);
    document.getElementById('undoBtn').addEventListener('click', undo);
    
    // 生成按钮
    document.getElementById('generateBtn').addEventListener('click', generateImage);
    
    // 视图模式切换
    document.getElementById('sideBySideBtn').addEventListener('click', () => switchViewMode('side'));
    document.getElementById('overlayBtn').addEventListener('click', () => switchViewMode('overlay'));
    
    // 叠加模式控制
    document.getElementById('toggleSketchLayer').addEventListener('change', toggleLayer);
    document.getElementById('toggleGeneratedLayer').addEventListener('change', toggleLayer);
    document.getElementById('overlaySlider').addEventListener('input', updateOverlay);
    
    // 结果操作按钮
    document.getElementById('downloadSketchBtn').addEventListener('click', downloadSketch);
    document.getElementById('downloadGeneratedBtn').addEventListener('click', downloadGenerated);
    document.getElementById('saveToGalleryBtn').addEventListener('click', saveToGallery);
    document.getElementById('newSketchBtn').addEventListener('click', newSketch);
}

// 初始化工具栏
function initializeTools() {
    const brushSize = document.getElementById('brushSize');
    const brushColor = document.getElementById('brushColor');
    const brushOpacity = document.getElementById('brushOpacity');
    
    brushSize.addEventListener('input', (e) => {
        currentSize = e.target.value;
        document.getElementById('brushSizeValue').textContent = currentSize;
    });
    
    brushColor.addEventListener('input', (e) => {
        currentColor = e.target.value;
        isEraser = false;
        document.getElementById('eraserBtn').classList.remove('active');
    });
    
    brushOpacity.addEventListener('input', (e) => {
        currentOpacity = e.target.value / 100;
        document.getElementById('brushOpacityValue').textContent = e.target.value;
    });
}

// 开始绘画
function startDrawing(e) {
    isDrawing = true;
    const pos = getMousePos(e);
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
}

// 绘画
function draw(e) {
    if (!isDrawing) return;
    
    const pos = getMousePos(e);
    
    ctx.lineWidth = currentSize;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    if (isEraser) {
        ctx.globalCompositeOperation = 'destination-out';
    } else {
        ctx.globalCompositeOperation = 'source-over';
        ctx.strokeStyle = currentColor;
    }
    
    ctx.globalAlpha = currentOpacity;
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
}

// 停止绘画
function stopDrawing() {
    if (isDrawing) {
        isDrawing = false;
        ctx.globalAlpha = 1;
        saveState();
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
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent(e.type === 'touchstart' ? 'mousedown' : 'mousemove', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
}

// 切换橡皮擦
function toggleEraser() {
    isEraser = !isEraser;
    const btn = document.getElementById('eraserBtn');
    btn.classList.toggle('active', isEraser);
}

// 清空画布
function clearCanvas() {
    if (confirm('确定要清空画布吗？')) {
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        saveState();
    }
}

// 保存状态
function saveState() {
    historyStep++;
    if (historyStep < drawingHistory.length) {
        drawingHistory.length = historyStep;
    }
    drawingHistory.push(canvas.toDataURL());
}

// 撤销
function undo() {
    if (historyStep > 0) {
        historyStep--;
        const img = new Image();
        img.src = drawingHistory[historyStep];
        img.onload = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
        };
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
        // 将画布转换为blob
        const sketchBlob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
        
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
        
        // 显示结果
        displayResults(canvas.toDataURL(), data.image_url);
        
    } catch (error) {
        console.error('生成失败:', error);
        alert(`生成失败：${error.message}`);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// 显示结果
function displayResults(sketchUrl, generatedUrl) {
    // 显示结果区域
    document.getElementById('resultSection').style.display = 'block';
    
    // 设置左右对比图片
    document.getElementById('sketchImageSide').src = sketchUrl;
    document.getElementById('generatedImageSide').src = generatedUrl;
    
    // 设置叠加对比图片并确保尺寸一致
    const sketchOverlay = document.getElementById('sketchImageOverlay');
    const generatedOverlay = document.getElementById('generatedImageOverlay');
    const overlayContainer = document.querySelector('.overlay-container');
    
    // 加载草图
    sketchOverlay.onload = function() {
        // 设置容器尺寸为图片的实际尺寸
        overlayContainer.style.width = sketchOverlay.naturalWidth + 'px';
        overlayContainer.style.height = sketchOverlay.naturalHeight + 'px';
        
        // 确保生成图也是相同尺寸
        generatedOverlay.style.width = sketchOverlay.naturalWidth + 'px';
        generatedOverlay.style.height = sketchOverlay.naturalHeight + 'px';
        sketchOverlay.style.width = sketchOverlay.naturalWidth + 'px';
        sketchOverlay.style.height = sketchOverlay.naturalHeight + 'px';
        
        console.log(`叠加容器尺寸: ${sketchOverlay.naturalWidth}x${sketchOverlay.naturalHeight}`);
    };
    
    sketchOverlay.src = sketchUrl;
    generatedOverlay.src = generatedUrl;
    
    // 滚动到结果区域
    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
}

// 切换视图模式
function switchViewMode(mode) {
    const sideBySideView = document.getElementById('sideBySideView');
    const overlayView = document.getElementById('overlayView');
    const sideBySideBtn = document.getElementById('sideBySideBtn');
    const overlayBtn = document.getElementById('overlayBtn');
    
    if (mode === 'side') {
        sideBySideView.style.display = 'grid';
        overlayView.style.display = 'none';
        sideBySideBtn.classList.add('active');
        overlayBtn.classList.remove('active');
    } else {
        sideBySideView.style.display = 'none';
        overlayView.style.display = 'block';
        sideBySideBtn.classList.remove('active');
        overlayBtn.classList.add('active');
    }
}

// 切换图层
function toggleLayer() {
    const sketchLayer = document.querySelector('.sketch-layer');
    const showSketch = document.getElementById('toggleSketchLayer').checked;
    sketchLayer.style.display = showSketch ? 'block' : 'none';
}

// 更新叠加效果
function updateOverlay() {
    const slider = document.getElementById('overlaySlider');
    const sketchLayer = document.querySelector('.sketch-layer');
    const sliderLine = document.querySelector('.overlay-slider-line');
    
    const percentage = slider.value;
    sketchLayer.style.clipPath = `inset(0 ${100 - percentage}% 0 0)`;
    sliderLine.style.left = `${percentage}%`;
}

// 下载草图
function downloadSketch() {
    const link = document.createElement('a');
    link.download = `sketch_${Date.now()}.png`;
    link.href = canvas.toDataURL();
    link.click();
}

// 下载生成图
function downloadGenerated() {
    const img = document.getElementById('generatedImageSide');
    const link = document.createElement('a');
    link.download = `generated_${Date.now()}.png`;
    link.href = img.src;
    link.click();
}

// 保存到作品集
async function saveToGallery() {
    const generatedImg = document.getElementById('generatedImageSide');
    const prompt = document.getElementById('promptInput').value;
    
    try {
        // 将图片URL转换为blob
        const response = await fetch(generatedImg.src);
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
        // 清空画布
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        drawingHistory = [];
        historyStep = -1;
        saveState();
        
        // 清空提示词
        document.getElementById('promptInput').value = '';
        
        // 隐藏结果区域
        document.getElementById('resultSection').style.display = 'none';
        
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}
