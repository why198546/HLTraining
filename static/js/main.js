// 全局变量
let currentImage = null;
let currentMode = null; // 'text' 或 'sketch'
let currentStep = 0; // 0: 输入, 1: 图片生成, 2: 调整, 3: 3D模型生成

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
    setupEventListeners();
    updateFlowSteps();
    console.log('应用初始化完成');
}

// 设置事件监听器
function setupEventListeners() {
    // 图片上传按钮
    const addImageBtn = document.getElementById('add-image-btn');
    if (addImageBtn) {
        addImageBtn.addEventListener('click', () => {
            document.getElementById('sketch-upload').click();
        });
    }

    // 文件上传
    const sketchUpload = document.getElementById('sketch-upload');
    if (sketchUpload) {
        sketchUpload.addEventListener('change', handleImageUpload);
    }

    // 生成图片按钮
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateImage);
    }

    // 调整图片按钮
    const adjustBtn = document.getElementById('adjust-btn');
    if (adjustBtn) {
        adjustBtn.addEventListener('click', showAdjustPanel);
    }

    // 应用调整按钮
    const applyAdjustBtn = document.getElementById('apply-adjust-btn');
    if (applyAdjustBtn) {
        applyAdjustBtn.addEventListener('click', applyAdjustment);
    }

    // 确认并生成3D按钮
    const confirm3dBtn = document.getElementById('confirm-3d-btn');
    if (confirm3dBtn) {
        confirm3dBtn.addEventListener('click', confirmAndGenerate3D);
    }

    // 重新开始按钮
    const restartBtn = document.getElementById('restart-btn');
    if (restartBtn) {
        restartBtn.addEventListener('click', restartCreation);
    }

    // 下载按钮
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadCurrentImage);
    }
}

// 跳转到创作页面
function goToCreatePage() {
    window.location.href = '/create';
}

// 触发图片上传（由HTML onclick调用）
function triggerImageUpload() {
    document.getElementById('reference-image').click();
}

// 处理图片上传
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    console.log('上传图片:', file.name);

    // 验证文件类型
    if (!file.type.startsWith('image/')) {
        showMessage('请选择图片文件！', 'error');
        return;
    }

    // 显示上传的图片预览
    const reader = new FileReader();
    reader.onload = function(e) {
        console.log('图片读取完成');
        showMessage('图片已上传，点击"开始创作"生成AI图片！', 'success');
    };
    reader.readAsDataURL(file);
}

// 生成图片
async function generateImage() {
    try {
        console.log('开始生成图片...');
        showLoading('正在生成图片...');
        currentStep = 1;
        updateFlowSteps();

        const formData = new FormData();
        const promptText = document.getElementById('creation-prompt').value.trim();
        const uploadedFile = document.getElementById('reference-image').files[0];

        if (promptText) {
            formData.append('prompt', promptText);
            console.log('添加提示词:', promptText);
        }

        if (uploadedFile) {
            formData.append('sketch', uploadedFile);
            console.log('添加图片文件:', uploadedFile.name);
        }

        console.log('发送请求到 /generate-image');
        const response = await fetch('/generate-image', {
            method: 'POST',
            body: formData
        });

        console.log('收到响应:', response.status);
        const result = await response.json();
        console.log('响应数据:', result);

        if (result.success) {
            currentImage = result.image_path;
            displayGeneratedImage(result.image_path);
            showImageActions();
            showMessage('图片生成成功！', 'success');
        } else {
            throw new Error(result.error || '图片生成失败');
        }

    } catch (error) {
        console.error('生成图片错误:', error);
        showMessage('图片生成失败：' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 显示生成的图片
function displayGeneratedImage(imagePath) {
    const resultArea = document.getElementById('result-area');
    const generatedImage = document.getElementById('generated-image');
    
    console.log('显示图片:', imagePath);
    
    if (generatedImage && imagePath) {
        generatedImage.src = imagePath + '?t=' + Date.now(); // 防止缓存
        resultArea.style.display = 'block';
        console.log('图片显示完成');
    }
}

// 显示图片操作按钮
function showImageActions() {
    const actionsDiv = document.getElementById('image-actions');
    if (actionsDiv) {
        actionsDiv.style.display = 'block';
        console.log('显示操作按钮');
    }
}

// 显示调整面板
function showAdjustPanel() {
    const adjustPanel = document.getElementById('adjust-panel');
    if (adjustPanel) {
        adjustPanel.style.display = 'block';
        adjustPanel.scrollIntoView({ behavior: 'smooth' });
        console.log('显示调整面板');
    }
}

// 应用调整
async function applyAdjustment() {
    try {
        const adjustPrompt = document.getElementById('adjust-prompt').value.trim();
        
        if (!adjustPrompt) {
            showMessage('请输入调整说明！', 'error');
            return;
        }

        if (!currentImage) {
            showMessage('没有可调整的图片！', 'error');
            return;
        }

        console.log('开始调整图片:', adjustPrompt);
        showLoading('正在调整图片...');

        const formData = new FormData();
        formData.append('current_image', currentImage);
        formData.append('adjust_prompt', adjustPrompt);

        const response = await fetch('/adjust-image', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            currentImage = result.image_path;
            displayGeneratedImage(result.image_path);
            showMessage('图片调整成功！', 'success');
            
            // 清空调整输入框
            document.getElementById('adjust-prompt').value = '';
        } else {
            throw new Error(result.error || '图片调整失败');
        }

    } catch (error) {
        console.error('调整图片错误:', error);
        showMessage('图片调整失败：' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 确认并生成3D模型
async function confirmAndGenerate3D() {
    try {
        if (!currentImage) {
            showMessage('没有可生成3D模型的图片！', 'error');
            return;
        }

        console.log('开始生成3D模型');
        showLoading('正在生成3D模型...');
        currentStep = 3;
        updateFlowSteps();

        const formData = new FormData();
        formData.append('image_path', currentImage);

        const response = await fetch('/generate-3d-model', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            display3DModel(result.model_path);
            showMessage('3D模型生成成功！', 'success');
        } else {
            throw new Error(result.error || '3D模型生成失败');
        }

    } catch (error) {
        console.error('生成3D模型错误:', error);
        showMessage('3D模型生成失败：' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// 显示3D模型
function display3DModel(modelPath) {
    const modelArea = document.getElementById('model-result-area');
    const modelViewer = document.getElementById('model-viewer');
    
    if (modelViewer && modelPath) {
        modelViewer.src = modelPath;
        modelArea.style.display = 'block';
        modelArea.scrollIntoView({ behavior: 'smooth' });
        console.log('显示3D模型');
    }
}

// 返回首页
function backToHome() {
    // 隐藏创作工作区
    document.getElementById('creation-workspace').style.display = 'none';
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    console.log('返回首页');
}

// 重新开始创作
function restartCreation() {
    // 重置全局变量
    currentImage = null;
    currentMode = null;
    currentStep = 0;

    // 清空输入
    document.getElementById('creation-prompt').value = '';
    document.getElementById('reference-image').value = '';
    const adjustPrompt = document.getElementById('adjust-prompt');
    if (adjustPrompt) adjustPrompt.value = '';

    // 隐藏所有结果区域
    document.getElementById('creation-workspace').style.display = 'none';
    const resultArea = document.getElementById('result-area');
    if (resultArea) resultArea.style.display = 'none';
    
    const imageActions = document.getElementById('image-actions');
    if (imageActions) imageActions.style.display = 'none';
    
    const adjustPanel = document.getElementById('adjust-panel');
    if (adjustPanel) adjustPanel.style.display = 'none';
    
    const modelArea = document.getElementById('model-result-area');
    if (modelArea) modelArea.style.display = 'none';

    // 更新流程步骤
    updateFlowSteps();

    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    showMessage('已重新开始！', 'info');
    console.log('重新开始创作');
}

// 下载当前图片
function downloadCurrentImage() {
    if (!currentImage) {
        showMessage('没有可下载的图片！', 'error');
        return;
    }

    const link = document.createElement('a');
    link.href = currentImage;
    link.download = 'generated_image_' + Date.now() + '.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showMessage('图片下载开始！', 'success');
}

// 更新流程步骤显示
function updateFlowSteps() {
    const steps = document.querySelectorAll('.flow-step');
    steps.forEach((step, index) => {
        step.classList.remove('active', 'completed');
        
        if (index < currentStep) {
            step.classList.add('completed');
        } else if (index === currentStep) {
            step.classList.add('active');
        }
    });
}

// 显示加载状态
function showLoading(message = '处理中...') {
    // 创建或显示加载遮罩
    let loadingOverlay = document.getElementById('loading-overlay');
    if (!loadingOverlay) {
        loadingOverlay = createLoadingOverlay();
    }
    
    const loadingText = loadingOverlay.querySelector('.loading-text');
    if (loadingText) {
        loadingText.textContent = message;
    }
    
    loadingOverlay.style.display = 'flex';
    console.log('显示加载状态:', message);
}

// 隐藏加载状态
function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
    console.log('隐藏加载状态');
}

// 创建加载遮罩
function createLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <div class="loading-text">处理中...</div>
        </div>
    `;
    document.body.appendChild(overlay);
    return overlay;
}

// 显示消息提示
function showMessage(message, type = 'info') {
    // 创建消息元素
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-toast message-${type}`;
    messageDiv.textContent = message;

    // 添加到页面
    document.body.appendChild(messageDiv);

    // 显示动画
    setTimeout(() => {
        messageDiv.classList.add('show');
    }, 100);

    // 自动隐藏
    setTimeout(() => {
        messageDiv.classList.remove('show');
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 300);
    }, 3000);
    
    console.log(`消息提示 [${type}]:`, message);
}

// 工具函数：验证文件类型
function validateFileType(file, allowedTypes) {
    return allowedTypes.some(type => file.type.includes(type));
}

// 工具函数：格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 错误处理
window.addEventListener('error', function(e) {
    console.error('JavaScript错误:', e.error);
    showMessage('发生了一个错误，请刷新页面重试', 'error');
});

// 未处理的Promise拒绝
window.addEventListener('unhandledrejection', function(e) {
    console.error('未处理的Promise拒绝:', e.reason);
    showMessage('网络请求失败，请检查网络连接', 'error');
});