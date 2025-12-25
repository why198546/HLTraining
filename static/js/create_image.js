// create_image.js - 图片创作页面逻辑（文字为主，图片可选）

let uploadedFile = null;
let sessionId = document.getElementById('session-id').value || null;
let generatedImageUrl = null;

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
        console.warn('Toast未初始化:', message);
        alert(message);
    }
}

// 填充提示词示例
function fillPrompt(text) {
    document.getElementById('creation-prompt').value = text;
}

// 触发图片上传
function triggerImageUpload() {
    document.getElementById('reference-image').click();
}

// 处理图片上传
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // 验证文件类型
    if (!file.type.startsWith('image/')) {
        showToast('请上传图片文件', 'error');
        return;
    }

    uploadedFile = file;
    
    // 显示预览
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('uploaded-image').src = e.target.result;
        document.getElementById('uploaded-image-preview').style.display = 'block';
    };
    reader.readAsDataURL(file);
}

// 移除上传的图片
function removeUploadedImage() {
    uploadedFile = null;
    document.getElementById('uploaded-image-preview').style.display = 'none';
    document.getElementById('reference-image').value = '';
}

// 生成图片
async function generateImage() {
    const prompt = document.getElementById('creation-prompt').value.trim();
    
    // 验证：必须有prompt或图片
    if (!prompt && !uploadedFile) {
        showToast('请输入文字描述或上传图片', 'warning');
        return;
    }

    const style = document.getElementById('image-style').value;
    const aspectRatio = document.getElementById('aspect-ratio').value;

    // 显示loading
    showLoading('正在生成图片，请稍候...');

    const formData = new FormData();
    if (prompt) formData.append('prompt', prompt);
    if (uploadedFile) formData.append('image', uploadedFile);
    formData.append('style', style);
    formData.append('aspect_ratio', aspectRatio);
    if (sessionId) formData.append('session_id', sessionId);

    try {
        const response = await fetch('/api/generate_image', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (data.success) {
            sessionId = data.session_id;
            document.getElementById('session-id').value = sessionId;
            generatedImageUrl = data.image_url;
            
            // 显示生成结果
            document.getElementById('generated-img').src = data.image_url;
            document.getElementById('result-section').style.display = 'block';
            
            // 滚动到结果区域
            document.getElementById('result-section').scrollIntoView({ behavior: 'smooth' });
            
            showToast('图片生成成功！', 'success');
        } else {
            showToast(data.message || '生成失败', 'error');
        }
    } catch (error) {
        console.error('生成失败:', error);
        showToast('生成失败，请重试', 'error');
    } finally {
        hideLoading();
    }
}

// 快速调整
async function quickAdjust(type) {
    if (!sessionId || !generatedImageUrl) {
        showToast('请先生成图片', 'warning');
        return;
    }

    showLoading(`正在${type === 'brighter' ? '提亮' : type === 'vibrant' ? '增强色彩' : '柔化'}...`);

    try {
        const response = await fetch('/api/adjust_image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                adjustment_type: type
            })
        });

        const data = await response.json();
        
        if (data.success) {
            generatedImageUrl = data.image_url;
            document.getElementById('generated-img').src = data.image_url + '?t=' + Date.now();
            showToast('调整成功！', 'success');
        } else {
            showToast(data.message || '调整失败', 'error');
        }
    } catch (error) {
        console.error('调整失败:', error);
        showToast('调整失败，请重试', 'error');
    } finally {
        hideLoading();
    }
}

// 保存作品
async function saveArtwork() {
    if (!sessionId) {
        showToast('请先生成图片', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/save_artwork', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });

        const data = await response.json();
        
        if (data.success) {
            showToast('作品已保存到作品展示', 'success');
        } else {
            showToast(data.message || '保存失败', 'error');
        }
    } catch (error) {
        console.error('保存失败:', error);
        showToast('保存失败，请重试', 'error');
    }
}

// 跳转到3D生成
function goTo3D() {
    if (!sessionId) {
        showToast('请先生成图片', 'warning');
        return;
    }
    window.location.href = `/create/3d?session_id=${sessionId}`;
}

// 跳转到视频生成
function goToVideo() {
    if (!sessionId) {
        showToast('请先生成图片', 'warning');
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
