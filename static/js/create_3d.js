// create_3d.js - 3D模型生成页面（支持两种模式）
let sessionId = document.getElementById('session-id').value;
let viewer = null;
let uploadedImageFor3D = null;

// Loading 函数
function showLoading(message = '加载中...') {
    const overlay = document.getElementById('loading-overlay');
    const text = document.getElementById('loading-text');
    if (overlay) {
        if (text) text.textContent = message;
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'none';
}

// Toast辅助函数
function showToast(message, type = 'info') {
    if (window.toast) {
        window.toast.show(message, type);
    } else {
        alert(message);
    }
}

// 切换输入标签页
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.style.display = 'none');
    
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    document.getElementById(`${tab}-input`).style.display = 'block';
}

// 处理图片上传（独立模式）
function handleImageUploadFor3D(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        showToast('请上传图片文件', 'error');
        return;
    }
    
    uploadedImageFor3D = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('uploaded-img-3d').src = e.target.result;
        document.getElementById('uploaded-preview-3d').style.display = 'block';
    };
    reader.readAsDataURL(file);
}

// 初始化拖拽上传，避免浏览器默认打开图片
document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.getElementById('model-image');

    if (!uploadArea || !fileInput) return;

    const resetHover = () => {
        uploadArea.style.borderColor = '#00704A';
        uploadArea.style.background = '#f8f8f8';
    };

    ['dragenter', 'dragover'].forEach(evt => {
        uploadArea.addEventListener(evt, e => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.style.borderColor = '#004f35';
            uploadArea.style.background = '#e8f5e9';
        });
    });

    ['dragleave', 'drop'].forEach(evt => {
        uploadArea.addEventListener(evt, e => {
            e.preventDefault();
            e.stopPropagation();
            resetHover();
        });
    });

    uploadArea.addEventListener('drop', e => {
        const files = e.dataTransfer ? e.dataTransfer.files : null;
        if (!files || !files.length) return;

        // DataTransfer更可靠地写入file input
        const dt = new DataTransfer();
        dt.items.add(files[0]);
        fileInput.files = dt.files;

        handleImageUploadFor3D({ target: fileInput });
    });

    // 防止将图片拖到页面其他位置时被浏览器直接打开
    ['dragover', 'drop'].forEach(evt => {
        document.addEventListener(evt, e => {
            e.preventDefault();
        });
    });
});

// 初始化模型查看器
document.addEventListener('DOMContentLoaded', () => {
    viewer = ModelViewer.init({
        containerId: 'model-container',
        shellId: 'model-viewer-shell',
        fullscreenShellId: 'fullscreen-viewer-shell',
        fullscreenWrapperId: 'fullscreen-viewer',
        metaIds: {
            name: 'model-meta-name',
            size: 'model-meta-size',
            meshes: 'model-meta-meshes',
            tris: 'model-meta-tris',
            fullscreenName: 'fullscreen-meta-name'
        }
    });
});

// 基于session生成3D（有源图片）
async function generate3D() {
    if (!sessionId) {
        showToast('无效的session', 'error');
        return;
    }
    
    const quality = document.querySelector('input[name="model-quality"]:checked').value;
    
    showLoading('正在生成3D模型，请稍候...');
    
    try {
        const response = await fetch('/api/generate_3d', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                quality: quality
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('preview-section').style.display = 'block';
            if (viewer) viewer.loadModel(result.model_url);
            showToast('3D模型生成成功！', 'success');
        } else {
            showToast(result.message || '生成失败', 'error');
        }
    } catch (error) {
        console.error('生成失败:', error);
        showToast('网络错误，请重试', 'error');
    } finally {
        hideLoading();
    }
}

// 直接生成3D（独立模式）
async function generate3DDirect() {
    const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
    const quality = document.querySelector('input[name="model-quality"]:checked').value;
    
    const formData = new FormData();
    formData.append('quality', quality);
    
    if (activeTab === 'text') {
        const prompt = document.getElementById('model-prompt').value.trim();
        if (!prompt) {
            showToast('请输入模型描述', 'warning');
            return;
        }
        formData.append('prompt', prompt);
    } else {
        if (!uploadedImageFor3D) {
            showToast('请上传图片', 'warning');
            return;
        }
        formData.append('image', uploadedImageFor3D);
    }
    
    showLoading('正在生成3D模型，请稍候...');
    
    try {
        const response = await fetch('/api/generate_3d_direct', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            sessionId = result.session_id;
            document.getElementById('session-id').value = sessionId;
            document.getElementById('preview-section').style.display = 'block';
            if (viewer) viewer.loadModel(result.model_url);
            showToast('3D模型生成成功！', 'success');
        } else {
            showToast(result.message || '生成失败', 'error');
        }
    } catch (error) {
        console.error('生成失败:', error);
        showToast('网络错误，请重试', 'error');
    } finally {
        hideLoading();
    }
}

// 加载3D模型（委托给模块化查看器）
function load3DModel(modelUrl) {
    if (!viewer) return;
    viewer.loadModel(modelUrl);
}

// 下载模型
function downloadModel() {
    if (!sessionId) {
        showToast('请先生成模型', 'warning');
        return;
    }
    window.location.href = `/api/download_model/${sessionId}`;
}

function downloadStl() {
    if (!sessionId) {
        showToast('请先生成模型', 'warning');
        return;
    }
    window.location.href = `/api/download_model/${sessionId}?format=stl`;
}

// 继续生成视频
function continueToVideo() {
    if (!sessionId) {
        showToast('请先生成3D模型', 'warning');
        return;
    }
    window.location.href = `/create/video?session_id=${sessionId}`;
}

// 全屏入口/出口（委托给模块化查看器）
function enterFullscreenViewer() {
    if (viewer) viewer.enterFullscreen();
}

function exitFullscreenViewer() {
    if (viewer) viewer.exitFullscreen();
}
