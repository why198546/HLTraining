// 创作页面相关功能
let currentStage = 1;
let generatedImageUrl = '';
let uploadedImageFile = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeCreatePage();
});

// 初始化创作页面
function initializeCreatePage() {
    // 绑定生成按钮事件
    const generateBtn = document.getElementById('generate-image');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateImage);
    }

    // 绑定3D生成按钮事件
    const generate3DBtn = document.getElementById('generate-3d');
    if (generate3DBtn) {
        generate3DBtn.addEventListener('click', generate3DModel);
    }

    // 设置初始阶段
    showStage(1);
}

// 显示指定阶段
function showStage(stageNumber) {
    // 隐藏所有阶段
    const allStages = document.querySelectorAll('.creation-stage');
    allStages.forEach(stage => stage.classList.remove('active'));

    // 重置所有进度步骤
    const allSteps = document.querySelectorAll('.progress-step');
    allSteps.forEach(step => step.classList.remove('active', 'completed'));

    // 显示当前阶段
    const currentStageElement = document.getElementById(getStageId(stageNumber));
    if (currentStageElement) {
        currentStageElement.classList.add('active');
    }

    // 更新进度指示器
    for (let i = 1; i <= stageNumber; i++) {
        const step = document.getElementById(`step-${i}`);
        if (step) {
            if (i < stageNumber) {
                step.classList.add('completed');
            } else if (i === stageNumber) {
                step.classList.add('active');
            }
        }
    }

    currentStage = stageNumber;
}

// 获取阶段ID
function getStageId(stageNumber) {
    const stageIds = {
        1: 'input-stage',
        2: 'generation-stage',
        3: 'adjustment-stage',
        4: 'model-stage'
    };
    return stageIds[stageNumber];
}

// 触发图片上传
function triggerImageUpload() {
    document.getElementById('reference-image').click();
}

// 处理图片上传
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        uploadedImageFile = file;
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('uploaded-image').src = e.target.result;
            document.getElementById('uploaded-image-preview').style.display = 'block';
        };
        reader.readAsDataURL(file);
        showMessage('图片上传成功！', 'success');
    }
}

// 移除上传的图片
function removeUploadedImage() {
    uploadedImageFile = null;
    document.getElementById('uploaded-image-preview').style.display = 'none';
    document.getElementById('reference-image').value = '';
    showMessage('已移除参考图片', 'info');
}

// 生成图片
async function generateImage() {
    const prompt = document.getElementById('creation-prompt').value.trim();
    const style = document.getElementById('image-style').value;
    const colorPreference = document.getElementById('color-preference').value;

    if (!prompt && !uploadedImageFile) {
        showMessage('请输入创意描述或上传参考图片', 'error');
        return;
    }

    showLoadingOverlay('AI正在创作中...');

    try {
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('style', style);
        formData.append('color_preference', colorPreference);
        
        if (uploadedImageFile) {
            formData.append('sketch', uploadedImageFile);
        }

        const response = await fetch('/generate-image', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            generatedImageUrl = result.image_url;
            document.getElementById('generated-image').src = result.image_url;
            document.getElementById('current-image').src = result.image_url;
            document.getElementById('final-image').src = result.image_url;
            
            hideLoadingOverlay();
            showMessage('图片生成成功！', 'success');
            showStage(2);
        } else {
            hideLoadingOverlay();
            showMessage(`生成失败: ${result.error}`, 'error');
        }
    } catch (error) {
        hideLoadingOverlay();
        showMessage('网络错误，请重试', 'error');
        console.error('Error:', error);
    }
}

// 重新生成图片
function regenerateImage() {
    generateImage();
}

// 显示调整面板
function showAdjustPanel() {
    showStage(3);
}

// 确认图片（跳过调整）
function confirmImage() {
    showStage(4);
}

// 跳过调整
function skipAdjustment() {
    showStage(4);
}

// 应用调整
async function applyAdjustment() {
    const adjustmentPrompt = document.getElementById('adjustment-prompt').value.trim();
    
    if (!adjustmentPrompt) {
        showMessage('请输入调整提示', 'error');
        return;
    }

    showLoadingOverlay('正在调整图片...');

    try {
        const formData = new FormData();
        formData.append('current_image', generatedImageUrl);
        formData.append('adjust_prompt', adjustmentPrompt);

        const response = await fetch('/adjust-image', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            generatedImageUrl = result.image_url;
            document.getElementById('current-image').src = result.image_url;
            document.getElementById('final-image').src = result.image_url;
            
            hideLoadingOverlay();
            showMessage('图片调整成功！', 'success');
            
            // 清空调整输入
            document.getElementById('adjustment-prompt').value = '';
            
            // 可以继续调整或进入下一阶段
        } else {
            hideLoadingOverlay();
            showMessage(`调整失败: ${result.error}`, 'error');
        }
    } catch (error) {
        hideLoadingOverlay();
        showMessage('网络错误，请重试', 'error');
        console.error('Error:', error);
    }
}

// 生成3D模型
async function generate3DModel() {
    showLoadingOverlay('正在生成3D模型，这可能需要几分钟...');

    try {
        const formData = new FormData();
        formData.append('image_path', generatedImageUrl);
        
        const response = await fetch('/generate-3d-model', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            hideLoadingOverlay();
            showMessage('3D模型生成成功！', 'success');
            
            // 显示3D模型预览区域
            document.getElementById('model-preview-area').style.display = 'block';
            document.getElementById('final-actions').style.display = 'flex';
            
            // 加载3D模型（如果有模型文件URL）
            if (result.model_url) {
                load3DModel(result.model_url);
            }
        } else {
            hideLoadingOverlay();
            showMessage(`3D模型生成失败: ${result.error}`, 'error');
        }
    } catch (error) {
        hideLoadingOverlay();
        showMessage('网络错误，请重试', 'error');
        console.error('Error:', error);
    }
}

// 加载3D模型（Three.js）
function load3DModel(modelUrl) {
    const container = document.getElementById('modelContainer');
    
    // 创建Three.js场景
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    
    renderer.setSize(container.offsetWidth, container.offsetHeight);
    renderer.setClearColor(0xf0f0f0);
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // 添加光源
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);

    // 加载模型
    const loader = new THREE.GLTFLoader();
    loader.load(modelUrl, function(gltf) {
        scene.add(gltf.scene);
        
        // 调整相机位置
        camera.position.z = 5;
        
        // 添加控制器
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        
        // 渲染循环
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
        animate();
        
        // 移除加载占位符
        const placeholder = container.querySelector('.model-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
    }, undefined, function(error) {
        console.error('3D模型加载失败:', error);
        showMessage('3D模型加载失败', 'error');
    });
}

// 下载图片
function downloadImage() {
    if (generatedImageUrl) {
        const link = document.createElement('a');
        link.href = generatedImageUrl;
        link.download = 'my-ai-creation.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showMessage('图片下载开始', 'success');
    }
}

// 开始新创作
function startNewCreation() {
    // 重置所有状态
    currentStage = 1;
    generatedImageUrl = '';
    uploadedImageFile = null;
    
    // 清空表单
    document.getElementById('creation-prompt').value = '';
    document.getElementById('adjustment-prompt').value = '';
    document.getElementById('reference-image').value = '';
    
    // 隐藏预览
    document.getElementById('uploaded-image-preview').style.display = 'none';
    document.getElementById('model-preview-area').style.display = 'none';
    document.getElementById('final-actions').style.display = 'none';
    
    // 返回第一阶段
    showStage(1);
    
    showMessage('已开始新的创作', 'info');
}

// 分享创作
function shareCreation() {
    if (generatedImageUrl) {
        // 这里可以实现分享功能
        showMessage('分享功能开发中...', 'info');
    }
}

// 显示加载覆盖层
function showLoadingOverlay(text = '加载中...') {
    const overlay = document.getElementById('loading-overlay');
    const loadingText = overlay.querySelector('.loading-text');
    loadingText.textContent = text;
    overlay.style.display = 'flex';
}

// 隐藏加载覆盖层
function hideLoadingOverlay() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// 显示消息提示
function showMessage(message, type = 'info') {
    const toast = document.getElementById('message-toast');
    toast.textContent = message;
    toast.className = `message-toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}