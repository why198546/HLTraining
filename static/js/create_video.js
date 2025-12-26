// create_video.js - 视频生成页面（支持两种模式）
let sessionId = document.getElementById('session-id').value;
let selectedRatio = '16:9';
let uploadedImageForVideo = null;

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

// 比例按钮绑定
document.querySelectorAll('.ratio-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.ratio-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        selectedRatio = this.dataset.ratio;
    });
});

// 切换输入标签页
function switchVideoTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.style.display = 'none');
    
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    document.getElementById(`${tab}-input`).style.display = 'block';
}

// 处理图片上传（独立模式）
function handleImageUploadForVideo(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        showToast('请上传图片文件', 'error');
        return;
    }
    
    uploadedImageForVideo = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('uploaded-img-video').src = e.target.result;
        document.getElementById('uploaded-preview-video').style.display = 'block';
    };
    reader.readAsDataURL(file);
}

// 基于session生成视频（有源图片）
async function generateVideo() {
    if (!sessionId) {
        showToast('无效的session', 'error');
        return;
    }

    const prompt = document.getElementById('video-prompt').value.trim();
    const duration = document.querySelector('input[name="duration"]:checked').value;

    showLoading('正在生成视频，请稍候（约1-3分钟）...');

    try {
        const response = await fetch('/api/generate_video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                prompt: prompt,
                aspect_ratio: selectedRatio,
                duration: parseInt(duration)
            })
        });

        const result = await response.json();
        
        if (result.success) {
            // 显示视频预览
            const videoElement = document.getElementById('generated-video');
            videoElement.src = result.video_url;
            document.getElementById('preview-section').style.display = 'block';
            
            videoElement.scrollIntoView({ behavior: 'smooth' });
            showToast('视频生成成功！', 'success');
        } else {
            showToast(result.message || '视频生成失败', 'error');
        }
    } catch (error) {
        hldebug.error('生成失败:', error);
        showToast('网络错误，请重试', 'error');
    } finally {
        hideLoading();
    }
}

// 直接生成视频（独立模式）
async function generateVideoDirect() {
    const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
    const duration = document.querySelector('input[name="duration"]:checked').value;
    
    const formData = new FormData();
    formData.append('aspect_ratio', selectedRatio);
    formData.append('duration', duration);
    
    if (activeTab === 'text') {
        const prompt = document.getElementById('video-prompt-text').value.trim();
        if (!prompt) {
            showToast('请输入视频描述', 'warning');
            return;
        }
        formData.append('prompt', prompt);
    } else {
        if (!uploadedImageForVideo) {
            showToast('请上传图片', 'warning');
            return;
        }
        formData.append('image', uploadedImageForVideo);
        
        const prompt = document.getElementById('video-prompt-image').value.trim();
        if (prompt) {
            formData.append('prompt', prompt);
        }
    }
    
    showLoading('正在生成视频，请稍候（约1-3分钟）...');
    
    try {
        const response = await fetch('/api/generate_video_direct', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            sessionId = result.session_id;
            document.getElementById('session-id').value = sessionId;
            
            // 显示视频预览
            const videoElement = document.getElementById('generated-video');
            videoElement.src = result.video_url;
            document.getElementById('preview-section').style.display = 'block';
            
            videoElement.scrollIntoView({ behavior: 'smooth' });
            showToast('视频生成成功！', 'success');
        } else {
            showToast(result.message || '视频生成失败', 'error');
        }
    } catch (error) {
        hldebug.error('生成失败:', error);
        showToast('网络错误，请重试', 'error');
    } finally {
        hideLoading();
    }
}

// 下载视频
function downloadVideo() {
    if (!sessionId) {
        showToast('请先生成视频', 'warning');
        return;
    }
    window.location.href = `/api/download_video/${sessionId}`;
}

// 保存并完成
async function saveAndFinish() {
    if (!sessionId) {
        showToast('请先生成视频', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/finalize_artwork', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });

        const result = await response.json();
        
        if (result.success) {
            showToast('作品已保存！', 'success');
            setTimeout(() => {
                window.location.href = '/gallery';
            }, 1500);
        } else {
            showToast(result.message || '保存失败', 'error');
        }
    } catch (error) {
        hldebug.error('保存失败:', error);
        showToast('保存失败，请重试', 'error');
    }
}

// Loading显示/隐藏
function showLoading(text) {
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}
