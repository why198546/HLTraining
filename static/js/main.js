// 全局变量
let currentFile = null;
let scene, camera, renderer, model;
let isAutoRotating = false;
let currentMode = null; // 'text-to-image' 或 'sketch-to-model'

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // 设置模式选择功能
    setupModeSelection();
    
    // 设置文件上传处理
    setupFileUpload();
    
    // 设置导航功能
    setupNavigation();
    
    // 设置按钮事件
    setupButtonEvents();
    
    // 初始化3D查看器
    init3DViewer();
}

// 模式选择功能
function selectMode(mode) {
    currentMode = mode;
    
    // 隐藏首页
    document.getElementById('home').style.display = 'none';
    
    // 隐藏所有创作区域
    document.getElementById('text-creation').style.display = 'none';
    document.getElementById('sketch-creation').style.display = 'none';
    
    // 显示对应的创作区域
    if (mode === 'text-to-image') {
        document.getElementById('text-creation').style.display = 'block';
        setupTextCreation();
    } else if (mode === 'sketch-to-model') {
        document.getElementById('sketch-creation').style.display = 'block';
        setupSketchCreation();
    }
    
    // 滚动到对应区域
    document.querySelector(`#${mode === 'text-to-image' ? 'text-creation' : 'sketch-creation'}`).scrollIntoView({
        behavior: 'smooth'
    });
}

// 设置文字创作模式
function setupTextCreation() {
    const generateBtn = document.getElementById('generate-from-text');
    generateBtn.addEventListener('click', handleTextGeneration);
}

// 设置手绘创作模式
function setupSketchCreation() {
    // 文件上传功能已经在setupFileUpload中设置
}

// 处理文字生成
function handleTextGeneration() {
    const textPrompt = document.getElementById('text-prompt').value.trim();
    const imageStyle = document.getElementById('image-style').value;
    const colorPreference = document.getElementById('color-preference').value;
    
    if (!textPrompt) {
        showMessage('请输入你的创意描述！', 'error');
        return;
    }
    
    // 构建完整的提示词
    const fullPrompt = buildTextPrompt(textPrompt, imageStyle, colorPreference);
    
    // 开始生成
    startTextToImageGeneration(fullPrompt);
}

// 构建文字提示词
function buildTextPrompt(userPrompt, style, colorPreference) {
    const styleMap = {
        'cute': '可爱卡通风格',
        'realistic': '写实风格',
        'anime': '动漫风格',
        'fantasy': '奇幻风格'
    };
    
    const colorMap = {
        'colorful': '色彩丰富',
        'pastel': '柔和色调',
        'bright': '明亮鲜艳',
        'natural': '自然色彩'
    };
    
    return `${userPrompt}，${styleMap[style]}，${colorMap[colorPreference]}，高质量，详细，专业`;
}

// 开始文字转图片生成
function startTextToImageGeneration(prompt) {
    // 显示处理步骤
    showProcessingSteps();
    updateStepStatus('step1', 'processing', '正在生成图片...');
    
    // 调用API生成图片
    fetch('/generate-from-text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prompt: prompt,
            workflow: 'text-to-image-to-model'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateStepStatus('step1', 'completed', '图片生成完成');
            updateStepStatus('step2', 'processing', '正在生成3D模型...');
            
            // 显示生成的图片
            displayGeneratedImage(data.image_path);
            
            // 继续生成3D模型
            generateModelFromImage(data.image_path);
        } else {
            handleGenerationError(data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        handleGenerationError('生成过程中出现错误');
    });
}

function setupModeSelection() {
    // 模式选择功能已经通过HTML onclick事件设置
}

function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    // 点击上传区域触发文件选择
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // 文件选择事件
    fileInput.addEventListener('change', handleFileSelect);
    
    // 拖拽上传功能
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleFileDrop);
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.remove('dragover');
}

function handleFileDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('uploadArea').classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    // 验证文件类型
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp'];
    if (!allowedTypes.includes(file.type)) {
        showMessage('请选择有效的图片文件 (PNG, JPG, JPEG, GIF, BMP)', 'error');
        return;
    }
    
    // 验证文件大小 (16MB)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        showMessage('文件大小不能超过16MB', 'error');
        return;
    }
    
    currentFile = file;
    
    // 显示预览
    displayImagePreview(file);
    
    // 根据当前模式处理文件
    if (currentMode === 'sketch-to-model') {
        // 手绘创作模式：上传文件并准备上色
        uploadFileForSketchMode(file);
    } else {
        // 兼容旧版本的默认行为
        uploadFileForSketchMode(file);
    }
}

function displayImagePreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        // 创建预览容器
        let previewContainer = document.getElementById('image-preview');
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.id = 'image-preview';
            previewContainer.className = 'image-preview-container';
            
            const uploadArea = document.getElementById('uploadArea');
            uploadArea.parentNode.insertBefore(previewContainer, uploadArea.nextSibling);
        }
        
        previewContainer.innerHTML = `
            <div class="preview-content">
                <h4>📸 预览图片</h4>
                <img src="${e.target.result}" alt="预览图片" class="preview-image">
                <p class="preview-info">文件名: ${file.name}</p>
                <p class="preview-info">大小: ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
        `;
        
        previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

// 为手绘创作模式上传文件
function uploadFileForSketchMode(file) {
    // 获取用户描述
    const description = document.getElementById('sketch-description').value.trim();
    if (!description) {
        showMessage('请先描述一下你希望AI如何处理这张图片！', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('description', description);
    formData.append('workflow', 'sketch-to-model');
    
    // 显示进度条和处理步骤
    showProcessingSteps();
    updateStepStatus('step1', 'processing', '正在上传文件...');
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateStep('step1', 'completed');
            updateProgressText('文件上传成功，开始AI处理...');
            
            // 显示原始图片
            displayOriginalImage(file);
            
            // 开始AI上色处理
            startColorization(data.filename);
        } else {
            throw new Error(data.error || '上传失败');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage(error.message, 'error');
        hideProgress();
        resetSteps();
    });
}

function startColorization(filename) {
    updateStep('step2', 'active');
    updateProgressText('AI正在为你的画作上色...');
    
    // 获取用户描述
    const description = document.getElementById('imageDescription').value.trim();
    
    fetch('/colorize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            filename: filename,
            description: description 
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateStep('step2', 'completed');
            updateProgressText('上色完成，正在生成3D模型...');
            
            // 显示上色后的图片
            displayColoredImages(data);
            
            // 开始3D模型生成
            start3DGeneration(data.colored_image);
        } else {
            throw new Error(data.error || 'AI上色失败');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        
        // 检查是否是配额限制错误
        if (error.message.includes('RESOURCE_EXHAUSTED') || error.message.includes('quota')) {
            showQuotaExhaustedMessage();
        } else {
            showMessage(error.message, 'error');
        }
        
        hideProgress();
        resetSteps();
    });
}

function start3DGeneration(coloredImageFilename) {
    updateStep('step3', 'active');
    updateProgressText('正在生成3D模型，请稍候...');
    
    fetch('/generate_3d', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image_filename: coloredImageFilename })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateStep('step3', 'completed');
            updateProgressText('所有处理完成！');
            
            // 显示3D模型
            load3DModel(data.model_file);
            
            // 显示结果区域
            setTimeout(() => {
                hideProgress();
                showResults();
            }, 1000);
        } else {
            throw new Error(data.error || '3D模型生成失败');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage(error.message, 'error');
        hideProgress();
        resetSteps();
    });
}

function displayOriginalImage(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('originalImage').src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function displayColoredImages(data) {
    if (data.colored_image) {
        document.getElementById('coloredImage').src = `/uploads/${data.colored_image}`;
        
        // 设置下载按钮
        document.getElementById('downloadColored').onclick = () => {
            downloadFile(data.colored_image);
        };
    }
    
    if (data.figurine_image) {
        document.getElementById('figurineImage').src = `/uploads/${data.figurine_image}`;
        
        // 设置下载按钮
        document.getElementById('downloadFigurine').onclick = () => {
            downloadFile(data.figurine_image);
        };
    }
}

function load3DModel(modelFilename) {
    const container = document.getElementById('modelContainer');
    
    // 清除之前的内容
    container.innerHTML = '';
    
    // 设置Three.js场景
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setClearColor(0xf0f0f0);
    container.appendChild(renderer.domElement);
    
    // 添加光照
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // 加载GLTF模型
    const loader = new THREE.GLTFLoader();
    loader.load(`/download/${modelFilename}`, function(gltf) {
        model = gltf.scene;
        scene.add(model);
        
        // 调整模型位置和大小
        const box = new THREE.Box3().setFromObject(model);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        const maxDim = Math.max(size.x, size.y, size.z);
        const scale = 2 / maxDim;
        model.scale.multiplyScalar(scale);
        
        model.position.copy(center).multiplyScalar(-scale);
        
        // 设置相机位置
        camera.position.set(0, 0, 3);
        camera.lookAt(0, 0, 0);
        
        // 添加轨道控制
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.1;
        
        // 开始渲染循环
        animate();
        
    }, undefined, function(error) {
        console.error('3D模型加载失败:', error);
        container.innerHTML = '<p>3D模型加载失败，请重试</p>';
    });
    
    // 设置下载按钮
    document.getElementById('download3D').onclick = () => {
        downloadFile(modelFilename);
    };
}

function animate() {
    requestAnimationFrame(animate);
    
    if (model && isAutoRotating) {
        model.rotation.y += 0.01;
    }
    
    renderer.render(scene, camera);
}

function init3DViewer() {
    // 设置自动旋转按钮
    document.getElementById('rotateModel').addEventListener('click', function() {
        isAutoRotating = !isAutoRotating;
        this.innerHTML = isAutoRotating ? 
            '<i class="fas fa-pause"></i> 停止旋转' : 
            '<i class="fas fa-sync-alt"></i> 自动旋转';
    });
}

function showProgress() {
    document.getElementById('progressContainer').style.display = 'block';
    document.getElementById('processingSteps').style.display = 'flex';
    updateProgressBar(0);
}

function hideProgress() {
    document.getElementById('progressContainer').style.display = 'none';
    document.getElementById('processingSteps').style.display = 'none';
}

function updateProgressBar(percentage) {
    document.getElementById('progressFill').style.width = percentage + '%';
}

function updateProgressText(text) {
    document.getElementById('progressText').textContent = text;
}

function updateStep(stepId, status) {
    const step = document.getElementById(stepId);
    step.className = 'step ' + status;
    
    // 更新进度条
    const steps = ['step1', 'step2', 'step3'];
    const currentIndex = steps.indexOf(stepId);
    
    if (status === 'completed') {
        updateProgressBar((currentIndex + 1) * 33.33);
    } else if (status === 'active') {
        updateProgressBar(currentIndex * 33.33 + 10);
    }
}

function resetSteps() {
    const steps = ['step1', 'step2', 'step3'];
    steps.forEach(stepId => {
        document.getElementById(stepId).className = 'step';
    });
}

function showResults() {
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
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
        background: ${type === 'error' ? '#ff6b6b' : '#4CAF50'};
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
            document.body.removeChild(messageEl);
        }, 300);
    }, 3000);
}

function showQuotaExhaustedMessage() {
    // 创建详细的配额耗尽提示
    const modal = document.createElement('div');
    modal.className = 'quota-modal';
    modal.innerHTML = `
        <div class="quota-modal-content">
            <div class="quota-modal-header">
                <i class="fas fa-clock"></i>
                <h3>AI服务暂时不可用</h3>
            </div>
            <div class="quota-modal-body">
                <p><strong>🤖 Nano Banana AI 配额已用完</strong></p>
                <p>免费版每天有使用限制，请尝试以下解决方案：</p>
                <ul>
                    <li>⏰ 等待配额重置（通常在UTC时间每天重置）</li>
                    <li>🔄 几分钟后再次尝试</li>
                    <li>⭐ 考虑升级到付费版本获得更多配额</li>
                </ul>
                <p class="quota-tip">💡 建议在配额重置后再来体验AI上色功能！</p>
            </div>
            <div class="quota-modal-footer">
                <button class="quota-close-btn" onclick="closeQuotaModal()">我知道了</button>
            </div>
        </div>
    `;
    
    // 添加样式
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 20000;
        animation: fadeIn 0.3s ease;
    `;
    
    document.body.appendChild(modal);
}

function closeQuotaModal() {
    const modal = document.querySelector('.quota-modal');
    if (modal) {
        modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(modal);
        }, 300);
    }
}

function downloadFile(filename) {
    const link = document.createElement('a');
    link.href = `/download/${filename}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function resetUpload() {
    // 重置表单
    document.getElementById('fileInput').value = '';
    currentFile = null;
    
    // 隐藏结果区域
    document.getElementById('results').style.display = 'none';
    
    // 重置步骤
    resetSteps();
    hideProgress();
    
    // 滚动到上传区域
    document.getElementById('upload').scrollIntoView({ behavior: 'smooth' });
}

function shareResults() {
    if (navigator.share) {
        navigator.share({
            title: 'AI创意工坊 - 我的作品',
            text: '看看我用AI创作的作品！',
            url: window.location.href
        });
    } else {
        // 复制链接到剪贴板
        navigator.clipboard.writeText(window.location.href).then(() => {
            showMessage('链接已复制到剪贴板！', 'success');
        });
    }
}

function scrollToUpload() {
    document.getElementById('upload').scrollIntoView({ behavior: 'smooth' });
}

function setupNavigation() {
    // 设置导航链接的平滑滚动
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
}

function setupButtonEvents() {
    // 设置窗口大小调整事件
    window.addEventListener('resize', function() {
        if (renderer && camera) {
            const container = document.getElementById('modelContainer');
            const width = container.clientWidth;
            const height = container.clientHeight;
            
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
        }
    });
}

// 添加CSS动画样式
const style = document.createElement('style');
style.textContent = `
@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
}
`;
document.head.appendChild(style);

// 新的辅助函数
function showProcessingSteps() {
    const steps = document.getElementById('processingSteps');
    if (steps) {
        steps.style.display = 'flex';
        resetStepStatuses();
    }
}

function updateStepStatus(stepId, status, message = '') {
    const step = document.getElementById(stepId);
    if (!step) return;
    
    const statusEl = step.querySelector('.step-status');
    if (!statusEl) return;
    
    // 清除之前的状态
    step.classList.remove('processing', 'completed', 'error');
    
    // 添加新状态
    step.classList.add(status);
    
    // 更新状态图标和文字
    switch(status) {
        case 'processing':
            statusEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            if (message) statusEl.innerHTML += ` ${message}`;
            break;
        case 'completed':
            statusEl.innerHTML = '<i class="fas fa-check" style="color: #4CAF50;"></i>';
            if (message) statusEl.innerHTML += ` ${message}`;
            break;
        case 'error':
            statusEl.innerHTML = '<i class="fas fa-times" style="color: #ff6b6b;"></i>';
            if (message) statusEl.innerHTML += ` ${message}`;
            break;
        default:
            statusEl.innerHTML = '';
    }
}

function resetStepStatuses() {
    const steps = ['step1', 'step2', 'step3'];
    steps.forEach(stepId => {
        const step = document.getElementById(stepId);
        if (step) {
            step.classList.remove('processing', 'completed', 'error');
            const statusEl = step.querySelector('.step-status');
            if (statusEl) {
                statusEl.innerHTML = '';
            }
        }
    });
}

function displayImagePreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        // 如果有图片预览区域，显示预览
        const previewArea = document.querySelector('.image-preview');
        if (previewArea) {
            previewArea.innerHTML = `
                <img src="${e.target.result}" alt="预览图片" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <p style="margin-top: 8px; color: #666; font-size: 0.9rem;">${file.name}</p>
            `;
        }
    };
    reader.readAsDataURL(file);
}

function displayGeneratedImage(imagePath) {
    console.log('显示生成的图片:', imagePath);
    
    // 显示结果区域
    const resultsSection = document.getElementById('results');
    if (resultsSection) {
        resultsSection.style.display = 'block';
        
        // 滚动到结果区域
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
        // 显示AI生成的图片
        const generatedImg = document.getElementById('coloredImage');
        if (generatedImg) {
            const imageUrl = `/uploads/${imagePath}`;
            console.log('设置图片URL:', imageUrl);
            generatedImg.src = imageUrl;
            
            // 添加加载事件处理
            generatedImg.onload = function() {
                console.log('图片加载成功');
            };
            
            generatedImg.onerror = function() {
                console.error('图片加载失败:', imageUrl);
                showMessage('图片加载失败，请检查文件是否存在', 'error');
            };
        }
        
        // 隐藏原始简笔画区域（因为是文字生成）
        const originalItem = document.querySelector('.result-item:first-child');
        if (originalItem && currentMode === 'text-to-image') {
            originalItem.style.display = 'none';
        }
        
        // 隐藏手办风格区域（暂时只显示生成的图片）
        const figurineItem = document.querySelector('.result-item:nth-child(3)');
        if (figurineItem && currentMode === 'text-to-image') {
            figurineItem.style.display = 'none';
        }
    }
}

function generateModelFromImage(imagePath) {
    updateStepStatus('step3', 'processing', '正在生成3D模型...');
    
    // 调用3D模型生成API
    fetch('/generate-3d-model', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_path: imagePath
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateStepStatus('step3', 'completed', '3D模型生成完成');
            // 显示3D模型
            load3DModel(data.model_path);
            showMessage('创作完成！你的作品真棒！', 'success');
        } else {
            updateStepStatus('step3', 'error', '3D模型生成失败');
            showMessage('3D模型生成失败，但你的图片已经完成上色了！', 'warning');
        }
    })
    .catch(error => {
        console.error('3D model generation error:', error);
        updateStepStatus('step3', 'error', '生成失败');
        showMessage('3D模型生成遇到问题，但图片生成成功了！', 'warning');
    });
}

function handleGenerationError(errorMessage) {
    // 检查是否是配额耗尽错误
    if (errorMessage.includes('RESOURCE_EXHAUSTED') || 
        errorMessage.includes('quota') || 
        errorMessage.includes('配额') ||
        errorMessage.includes('limit')) {
        showQuotaExhaustedMessage();
    } else {
        showMessage(`生成失败: ${errorMessage}`, 'error');
    }
    
    // 重置所有步骤状态
    resetStepStatuses();
}

// 返回首页函数
function backToHome() {
    // 隐藏所有创作区域
    document.getElementById('text-creation').style.display = 'none';
    document.getElementById('sketch-creation').style.display = 'none';
    
    // 显示首页
    document.getElementById('home').style.display = 'block';
    
    // 重置当前模式
    currentMode = null;
    
    // 滚动到首页顶部
    document.getElementById('home').scrollIntoView({
        behavior: 'smooth'
    });
    
    // 重置表单
    resetForms();
}

function resetForms() {
    // 重置文字创作表单
    const textPrompt = document.getElementById('text-prompt');
    if (textPrompt) textPrompt.value = '';
    
    // 重置手绘创作表单
    const sketchDescription = document.getElementById('sketch-description');
    if (sketchDescription) sketchDescription.value = '';
    
    // 重置文件输入
    const fileInput = document.getElementById('fileInput');
    if (fileInput) fileInput.value = '';
    
    // 重置当前文件
    currentFile = null;
    
    // 隐藏处理步骤
    const processingSteps = document.getElementById('processingSteps');
    if (processingSteps) processingSteps.style.display = 'none';
    
    // 重置步骤状态
    resetStepStatuses();
}