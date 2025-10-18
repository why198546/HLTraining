// 全局变量
let currentFile = null;
let scene, camera, renderer, model;
let isAutoRotating = false;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // 设置文件上传处理
    setupFileUpload();
    
    // 设置导航功能
    setupNavigation();
    
    // 设置按钮事件
    setupButtonEvents();
    
    // 初始化3D查看器
    init3DViewer();
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
    if (file.size > 16 * 1024 * 1024) {
        showMessage('文件太大，请选择小于16MB的图片', 'error');
        return;
    }
    
    currentFile = file;
    uploadFile(file);
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // 显示进度条和处理步骤
    showProgress();
    updateStep('step1', 'active');
    
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
    
    fetch('/colorize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filename: filename })
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
        showMessage(error.message, 'error');
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
        document.getElementById('coloredImage').src = `/download/${data.colored_image}`;
        
        // 设置下载按钮
        document.getElementById('downloadColored').onclick = () => {
            downloadFile(data.colored_image);
        };
    }
    
    if (data.figurine_image) {
        document.getElementById('figurineImage').src = `/download/${data.figurine_image}`;
        
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