// create_image.js - 图片创作页面逻辑（文字为主，图片可选）

let uploadedFile = null;
let sessionId = document.getElementById('session-id').value || null;
let generatedImageUrl = null;

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', function() {
    initializeDragAndDrop();
    initializePaste();
    initializeImageViewer();
    initializePreferences();
    
    // 页面卸载时摄像头会由camera-input.js自动关闭
});

// ==================== 用户偏好设置 (localStorage) ====================
const PREFERENCE_KEYS = {
    STYLE: 'createImage_style',
    ASPECT_RATIO: 'createImage_aspectRatio'
};

/**
 * 初始化用户偏好设置
 * 从localStorage恢复上次保存的设置，并添加监听器
 */
function initializePreferences() {
    // 恢复图片风格
    const savedStyle = localStorage.getItem(PREFERENCE_KEYS.STYLE);
    if (savedStyle) {
        const styleSelect = document.getElementById('image-style');
        if (styleSelect) {
            styleSelect.value = savedStyle;
        }
    }
    
    // 恢复分辨率
    const savedAspectRatio = localStorage.getItem(PREFERENCE_KEYS.ASPECT_RATIO);
    if (savedAspectRatio) {
        const aspectRatioSelect = document.getElementById('aspect-ratio');
        if (aspectRatioSelect) {
            aspectRatioSelect.value = savedAspectRatio;
        }
    }
    
    // 添加变化监听器，自动保存设置
    const styleSelect = document.getElementById('image-style');
    if (styleSelect) {
        styleSelect.addEventListener('change', function() {
            localStorage.setItem(PREFERENCE_KEYS.STYLE, this.value);
        });
    }
    
    const aspectRatioSelect = document.getElementById('aspect-ratio');
    if (aspectRatioSelect) {
        aspectRatioSelect.addEventListener('change', function() {
            localStorage.setItem(PREFERENCE_KEYS.ASPECT_RATIO, this.value);
        });
    }
}

/**
 * 清除本地保存的偏好设置（可选功能）
 */
function clearPreferences() {
    localStorage.removeItem(PREFERENCE_KEYS.STYLE);
    localStorage.removeItem(PREFERENCE_KEYS.ASPECT_RATIO);
}

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

// 更新Loading文本（用于进度提示）
function updateLoadingMessage(message) {
    const text = document.getElementById('loading-text');
    if (text) text.textContent = message;
}

// ==================== Camera-Input.js 模块集成 ====================
// 摄像头和图片上传现在由camera-input.js模块处理
// 通过processPhoto()回调在create_image.js的displayImagePreview()中处理

/**
 * processPhoto() - camera-input.js 的回调函数
 * 处理从摄像头拍摄或文件上传的照片
 * 这个函数被camera-input.js中的usePhoto()和handleFileUpload()调用
 */
function processPhoto(file) {
    
    // 保存到全局变量供generateImage()使用
    uploadedFile = file;
    
    // 显示图片预览
    displayImagePreview(file);
    
    // 关闭摄像头模态框
    closeCameraModal();
    
    showToast('照片已添加', 'success');
}

// 拖拽上传功能 ====================
function initializeDragAndDrop() {
    const container = document.getElementById('prompt-container');
    if (!container) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        container.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        container.addEventListener(eventName, () => {
            container.classList.add('drag-over');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        container.addEventListener(eventName, () => {
            container.classList.remove('drag-over');
        }, false);
    });
    
    container.addEventListener('drop', handleDrop, false);
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        const file = files[0];
        if (file.type.startsWith('image/')) {
            uploadedFile = file;
            displayImagePreview(file);
            showToast('图片已添加', 'success');
        } else {
            showToast('请拖拽图片文件', 'error');
        }
    }
}

// ==================== 粘贴功能 ====================
function initializePaste() {
    const textarea = document.getElementById('creation-prompt');
    if (!textarea) return;
    
    // 监听粘贴事件
    textarea.addEventListener('paste', handlePaste);
    
    // 也在整个文档上监听，以支持在页面任何地方粘贴
    document.addEventListener('paste', handlePaste);
}

async function handlePaste(e) {
    const items = e.clipboardData.items;
    
    for (let item of items) {
        // 处理粘贴的图片
        if (item.type.startsWith('image/')) {
            e.preventDefault();
            const file = item.getAsFile();
            if (file) {
                uploadedFile = file;
                displayImagePreview(file);
                showToast('图片已粘贴', 'success');
            }
            return;
        }
        
        // 处理粘贴的文本（可能是图片链接）
        if (item.type === 'text/plain') {
            item.getAsString(async (text) => {
                // 检查是否是图片URL
                if (isImageUrl(text)) {
                    e.preventDefault();
                    await loadImageFromUrl(text);
                }
            });
        }
    }
}

function isImageUrl(url) {
    // 检查是否是图片URL
    try {
        const urlObj = new URL(url);
        const pathname = urlObj.pathname.toLowerCase();
        return /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i.test(pathname) || 
               /image/i.test(url);
    } catch {
        return false;
    }
}

async function loadImageFromUrl(url) {
    try {
        showLoading('正在加载图片...');
        
        // 通过代理加载图片（避免跨域问题）
        const response = await fetch('/api/load_image_from_url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 将base64转换为Blob
            const blob = await fetch(data.image_data).then(r => r.blob());
            const file = new File([blob], 'pasted-image.png', { type: 'image/png' });
            uploadedFile = file;
            displayImagePreview(file);
            showToast('图片链接已加载', 'success');
        } else {
            showToast(data.message || '加载图片失败', 'error');
        }
    } catch (error) {
        hldebug.error('加载图片失败:', error);
        showToast('加载图片失败，请检查链接是否有效', 'error');
    } finally {
        hideLoading();
    }
}

// ==================== 图片预览显示 ====================
function displayImagePreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const imgSrc = e.target.result;
        const previewImg = document.getElementById('uploaded-image');
        previewImg.src = imgSrc;
        document.getElementById('uploaded-image-preview').style.display = 'block';
        
        // 加载完成后分析宽高比和纸张
        previewImg.onload = function() {
            analyzeImageAndUpdateAspectRatio(previewImg);
        };
    };
    reader.readAsDataURL(file);
}

/**
 * 分析图片的宽高比，自动匹配最接近的分辨率选项
 */
function analyzeImageAndUpdateAspectRatio(imgElement) {
    const width = imgElement.naturalWidth;
    const height = imgElement.naturalHeight;
    const aspectRatio = width / height;
    
    // 定义可用的分辨率选项及其宽高比
    const ratioOptions = [
        { value: '512x512', ratio: 1.0, label: '1:1' },
        { value: '768x512', ratio: 1.5, label: '3:2 横屏' },
        { value: '512x768', ratio: 0.667, label: '2:3 竖屏' },
        { value: '1024x576', ratio: 1.778, label: '16:9 横屏' },
        { value: '576x1024', ratio: 0.563, label: '9:16 竖屏' },
        { value: '1024x1024', ratio: 1.0, label: '1:1' }
    ];
    
    // 找出最接近的宽高比
    let bestMatch = ratioOptions[0];
    let minDifference = Math.abs(aspectRatio - bestMatch.ratio);
    
    for (let option of ratioOptions) {
        const difference = Math.abs(aspectRatio - option.ratio);
        if (difference < minDifference) {
            minDifference = difference;
            bestMatch = option;
        }
    }
    
    // 自动选择最匹配的分辨率
    const aspectRatioSelect = document.getElementById('aspect-ratio');
    aspectRatioSelect.value = bestMatch.value;
    localStorage.setItem(PREFERENCE_KEYS.ASPECT_RATIO, bestMatch.value);
    
    // 显示提示信息
    const detectedRatio = (width > height ? width / height : height / width).toFixed(2);
    showToast(`📐 检测到宽高比: ${detectedRatio} → 自动选择 ${bestMatch.label}`, 'info');
    
    // 显示裁剪工具提示
    showCropToolHint();
}


// 移除上传的图片
// 移除上传的图片
function removeUploadedImage() {
    uploadedFile = null;
    const previewContainer = document.getElementById('uploaded-image-preview');
    if (previewContainer) {
        previewContainer.style.display = 'none';
        // 同时移除任何纸张边界线SVG
        const svg = previewContainer.querySelector('svg');
        if (svg) {
            svg.remove();
        }
    }
}

// 生成图片
async function generateImage() {
    const prompt = document.getElementById('creation-prompt').value.trim();
    
    // 验证：必须有prompt、图片或已有session
    if (!prompt && !uploadedFile && !sessionId) {
        showToast('请输入文字描述或上传图片', 'warning');
        return;
    }
    
    // 如果只有图片没有prompt，提示用户
    if (uploadedFile && !prompt) {
    }

    const style = document.getElementById('image-style').value;
    const aspectRatio = document.getElementById('aspect-ratio').value;

    // 显示loading，告诉用户预计时间
    showLoading('正在生成图片，通常需要10-30秒，请稍候...');
    
    // 启动进度提示（每5秒更新一次）
    let progressMessages = ['正在思考构图...', '正在上色...', '正在优化细节...', '即将完成...'];
    let msgIndex = 0;
    let progressInterval = setInterval(() => {
        msgIndex = (msgIndex + 1) % progressMessages.length;
        updateLoadingMessage(progressMessages[msgIndex]);
    }, 5000);

    const formData = new FormData();
    if (prompt) formData.append('prompt', prompt);
    // 如果有新上传的图片，就上传它（使用sketch字段以兼容后端API）
    if (uploadedFile) {
        formData.append('sketch', uploadedFile);
    }
    formData.append('style', style);
    formData.append('aspect_ratio', aspectRatio);
    if (sessionId) formData.append('session_id', sessionId);

    try {
        // 使用通用的 /api/generate-image 端点（连字符），而不是松果课堂专用的 /api/generate_image（下划线）
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            body: formData
        });

        // 优先处理非200状态，给出更友好的提示
        if (!response.ok) {
            let serverMsg = null;
            try {
                const errData = await response.json();
                serverMsg = errData?.error || errData?.message;
            } catch (_) {}
            clearInterval(progressInterval);
            
            // 根据状态码给出不同提示
            let userMessage = serverMsg || '生成失败，请稍后重试';
            if (response.status === 503) {
                userMessage = serverMsg || 'AI服务暂时不可用，请检查网络连接';
            } else if (response.status === 504) {
                userMessage = serverMsg || 'AI服务响应超时，请重试';
            } else if (response.status === 400) {
                userMessage = serverMsg || '请输入文字描述或上传图片';
            }
            
            hldebug.warn(`生成失败，HTTP ${response.status}:`, serverMsg || response.statusText);
            showToast(userMessage, 'error');
            return;
        }

        const data = await response.json();
        
        if (data.success) {
            clearInterval(progressInterval); // 停止进度提示
            sessionId = data.session_id;
            document.getElementById('session-id').value = sessionId;
            generatedImageUrl = data.image_url;
            
            // 清空uploadedFile，避免File对象重复使用
            // 后续生成会通过sessionId从服务器恢复图片
            uploadedFile = null;
            
            // 显示生成结果
            document.getElementById('generated-img').src = data.image_url;
            document.getElementById('result-section').style.display = 'block';
            
            // 滚动到结果区域
            document.getElementById('result-section').scrollIntoView({ behavior: 'smooth' });
            
            showToast('图片生成成功！', 'success');
        } else {
            clearInterval(progressInterval); // 停止进度提示
            hldebug.info('生成失败，服务器返回:', data);
            showToast(data.error || data.message || '生成失败', 'error');
        }
    } catch (error) {
        clearInterval(progressInterval); // 停止进度提示
        hldebug.error('生成失败，捕获异常:', error);
        showToast('生成失败，请检查网络连接后重试', 'error');
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
        hldebug.error('调整失败:', error);
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
        hldebug.error('保存失败:', error);
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

// ==================== 图片查看器初始化 ====================
function initializeImageViewer() {
    // 初始化ImageViewer（来自sunguo_class.js）
    if (typeof ImageViewer !== 'undefined') {
        ImageViewer.init();
    } else {
    }
    
    // 给生成的图片添加点击事件
    const generatedImg = document.getElementById('generated-img');
    if (generatedImg) {
        generatedImg.addEventListener('click', function() {
            if (this.src && this.src !== '') {
                // 设置图片数组（只有一张图片）
                if (typeof ImageViewer !== 'undefined') {
                    ImageViewer.images = [this.src];
                    ImageViewer.currentIndex = 0;
                    ImageViewer.open(0);
                } else {
                    hldebug.error('❌ ImageViewer未定义');
                }
            }
        });
    }
}
