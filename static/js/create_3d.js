// create_3d.js - 3D模型生成页面（支持两种模式）
let sessionId = document.getElementById('session-id').value;
let modelViewer = null;
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
            load3DModel(result.model_url);
            showToast('3D模型生成成功！', 'success');
        } else {
            showToast(result.message || '生成失败', 'error');
        }
    } catch (error) {
        hldebug.error('生成失败:', error);
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
            load3DModel(result.model_url);
            showToast('3D模型生成成功！', 'success');
        } else {
            showToast(result.message || '生成失败', 'error');
        }
    } catch (error) {
        hldebug.error('生成失败:', error);
        showToast('网络错误，请重试', 'error');
    } finally {
        hideLoading();
    }
}

// 加载3D模型
function load3DModel(modelUrl) {
    const container = document.getElementById('model-container');
    
    // 初始化Three.js场景
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    
    // 添加光源
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // 加载GLTF模型
    const loader = new THREE.GLTFLoader();
    loader.load(modelUrl, (gltf) => {
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
        
        modelViewer = { scene, camera, renderer, controls };
    }, undefined, (error) => {
        hldebug.error('模型加载失败:', error);
        showToast('模型加载失败', 'error');
    });
}

// 下载模型
function downloadModel() {
    if (!sessionId) {
        showToast('请先生成模型', 'warning');
        return;
    }
    window.location.href = `/api/download_model/${sessionId}`;
}

// 继续生成视频
function continueToVideo() {
    if (!sessionId) {
        showToast('请先生成3D模型', 'warning');
        return;
    }
    window.location.href = `/create/video?session_id=${sessionId}`;
}

// Loading显示/隐藏
function showLoading(text) {
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}
