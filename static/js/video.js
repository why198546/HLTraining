/**
 * 视频生成页面交互逻辑
 */

let currentVideoUrl = null;
let isGenerating = false;

// 页面加载完成
document.addEventListener('DOMContentLoaded', function() {
    console.log('视频生成页面已加载');
    console.log('Session ID:', sessionId);
    console.log('Source Image:', imageUrl);
    
    // 初始化事件监听
    initEventListeners();
});

/**
 * 初始化事件监听器
 */
function initEventListeners() {
    const generateBtn = document.getElementById('generate-video-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', startVideoGeneration);
    }
}

/**
 * 开始视频生成
 */
async function startVideoGeneration() {
    if (isGenerating) {
        console.log('视频生成中，请等待...');
        return;
    }

    const prompt = document.getElementById('video-prompt').value.trim();
    if (!prompt) {
        alert('请输入视频动作描述！');
        return;
    }

    const duration = parseInt(document.getElementById('video-duration').value);
    const aspectRatio = document.getElementById('aspect-ratio').value;
    const quality = document.getElementById('video-quality').value;
    const motionIntensity = document.getElementById('motion-intensity').value;

    console.log('开始生成视频:', {
        prompt,
        duration,
        aspectRatio,
        quality,
        motionIntensity,
        imageUrl
    });

    isGenerating = true;
    showGenerationStatus();
    updateStatus('正在准备生成...', 0);

    try {
        const response = await fetch('/api/generate-video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                image_url: imageUrl,
                prompt: prompt,
                duration: duration,
                aspect_ratio: aspectRatio,
                quality: quality,
                motion_intensity: motionIntensity
            })
        });

        const data = await response.json();
        console.log('API响应:', data);

        if (data.success) {
            // 开始轮询任务状态，传入实际的视频时长
            const actualDuration = parseInt(duration);
            // Veo 3.1会将5秒调整为8秒，需要考虑这个
            const adjustedDuration = actualDuration === 5 ? 8 : actualDuration;
            pollVideoStatus(data.task_id, adjustedDuration);
        } else {
            throw new Error(data.error || '视频生成启动失败');
        }
    } catch (error) {
        console.error('视频生成错误:', error);
        hideGenerationStatus();
        alert('视频生成失败：' + error.message);
        isGenerating = false;
    }
}

/**
 * 轮询视频生成状态
 */
async function pollVideoStatus(taskId, duration = 8) {
    // 根据视频时长估算生成时间
    // 基准：8秒视频约需72秒（1分12秒）
    const baseTime = 72; // 8秒视频的基准时间（秒）
    const baseDuration = 8; // 基准视频时长
    const estimatedTime = Math.round((duration / baseDuration) * baseTime);
    const maxAttempts = Math.ceil(estimatedTime * 1.5); // 预留50%缓冲时间
    
    let attempts = 0;
    let startTime = Date.now();

    const checkStatus = async () => {
        if (attempts >= maxAttempts) {
            hideGenerationStatus();
            alert('视频生成超时，请重试');
            isGenerating = false;
            return;
        }

        try {
            const response = await fetch(`/api/video-status/${taskId}`);
            const data = await response.json();
            
            console.log('状态检查:', data);

            if (data.status === 'completed') {
                // 生成完成
                updateStatus('生成完成！', 100);
                setTimeout(() => {
                    hideGenerationStatus(); // 恢复按钮状态
                    showVideoResult(data.video_url);
                    isGenerating = false;
                }, 500);
            } else if (data.status === 'failed') {
                // 生成失败
                hideGenerationStatus();
                alert('视频生成失败：' + (data.error || '未知错误'));
                isGenerating = false;
            } else {
                // 继续等待 - 计算进度和剩余时间
                const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
                const progress = Math.min((elapsedTime / estimatedTime) * 90, 95); // 最多显示95%
                const remainingTime = Math.max(0, estimatedTime - elapsedTime);
                
                // 格式化剩余时间
                const minutes = Math.floor(remainingTime / 60);
                const seconds = remainingTime % 60;
                const timeText = minutes > 0 
                    ? `预计还需 ${minutes}分${seconds}秒` 
                    : `预计还需 ${seconds}秒`;
                
                updateStatus(`生成中... ${timeText}`, progress);
                attempts++;
                setTimeout(checkStatus, 1000);
            }
        } catch (error) {
            console.error('状态检查错误:', error);
            attempts++;
            setTimeout(checkStatus, 1000);
        }
    };

    checkStatus();
}

/**
 * 显示生成状态
 */
function showGenerationStatus() {
    const statusSection = document.getElementById('video-generation-status');
    const resultSection = document.getElementById('video-result-section');
    
    if (statusSection) statusSection.style.display = 'block';
    if (resultSection) resultSection.style.display = 'none';
    
    // 禁用生成按钮
    const generateBtn = document.getElementById('generate-video-btn');
    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 生成中...';
    }
}

/**
 * 隐藏生成状态
 */
function hideGenerationStatus() {
    const statusSection = document.getElementById('video-generation-status');
    if (statusSection) statusSection.style.display = 'none';
    
    // 恢复生成按钮
    const generateBtn = document.getElementById('generate-video-btn');
    if (generateBtn) {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> 生成视频';
    }
}

/**
 * 更新生成状态
 */
function updateStatus(message, progress) {
    const statusMessage = document.getElementById('status-message');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    if (statusMessage) statusMessage.textContent = message;
    if (progressFill) progressFill.style.width = progress + '%';
    if (progressText) progressText.textContent = Math.round(progress) + '%';
}

/**
 * 显示视频结果
 */
function showVideoResult(videoUrl) {
    currentVideoUrl = videoUrl;
    
    const statusSection = document.getElementById('video-generation-status');
    const resultSection = document.getElementById('video-result-section');
    const videoElement = document.getElementById('generated-video');
    
    if (statusSection) statusSection.style.display = 'none';
    if (resultSection) resultSection.style.display = 'block';
    
    if (videoElement) {
        videoElement.src = videoUrl;
        videoElement.load();
    }
    
    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * 下载视频
 */
function downloadVideo() {
    if (!currentVideoUrl) {
        alert('没有可下载的视频');
        return;
    }
    
    const a = document.createElement('a');
    a.href = currentVideoUrl;
    a.download = 'ai-generated-video.mp4';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

/**
 * 保存到作品集
 */
async function saveToGallery() {
    if (!currentVideoUrl) {
        alert('没有可保存的视频');
        return;
    }
    
    try {
        const response = await fetch('/api/save-video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                video_url: currentVideoUrl,
                prompt: document.getElementById('video-prompt').value
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('视频已保存到作品集！');
        } else {
            throw new Error(data.error || '保存失败');
        }
    } catch (error) {
        console.error('保存错误:', error);
        alert('保存失败：' + error.message);
    }
}

/**
 * 重新生成视频
 */
function regenerateVideo() {
    const resultSection = document.getElementById('video-result-section');
    if (resultSection) resultSection.style.display = 'none';
    
    currentVideoUrl = null;
    
    // 滚动到配置区域
    const configSection = document.querySelector('.video-config-section');
    if (configSection) {
        configSection.scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * 返回创作页面
 */
function backToCreate() {
    window.location.href = '/create';
}
