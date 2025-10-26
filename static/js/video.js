/**
 * 视频生成功能
 */

let isGenerating = false;
let pollInterval = null;
let countdownInterval = null;

/**
 * 开始视频生成
 */
async function startVideoGeneration() {
    if (isGenerating) {
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

    isGenerating = true;
    showGenerationStatus();
    
    // 显示友好的初始化信息
    updateStatus('准备开始制作视频...', 0);
    
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

        if (data.success) {
            startCountdown(duration);
            pollVideoStatus(data.task_id);
        } else {
            throw new Error(data.error || '视频生成启动失败');
        }
    } catch (error) {
        hideGenerationStatus();
        alert('视频生成失败：' + error.message);
        isGenerating = false;
    }
}

/**
 * 开始倒计时
 */
function startCountdown(duration) {
    const totalSeconds = duration * 60; // 转换为秒
    let remainingSeconds = totalSeconds;
    
    // 显示友好的预估时间信息
    const estimatedTime = getEstimatedTime();
    updateStatus(`小AI开始工作啦！预计需要 ${estimatedTime}`, 5);
    
    countdownInterval = setInterval(() => {
        remainingSeconds--;
        const progress = ((totalSeconds - remainingSeconds) / totalSeconds) * 80; // 最多到80%
        const minutes = Math.floor(remainingSeconds / 60);
        const seconds = remainingSeconds % 60;
        
        if (remainingSeconds > 0) {
            updateStatus(`视频生成中... 剩余时间约 ${minutes}:${seconds.toString().padStart(2, '0')}`, progress);
        } else {
            clearInterval(countdownInterval);
            updateStatus('视频即将完成...', 85);
        }
    }, 1000);
}

/**
 * 轮询视频生成状态
 */
async function pollVideoStatus(taskId) {
    let pollCount = 0;
    const maxPolls = 300; // 5分钟最大轮询时间

    pollInterval = setInterval(async () => {
        try {
            pollCount++;
            
            if (pollCount > maxPolls) {
                clearInterval(pollInterval);
                clearInterval(countdownInterval);
                hideGenerationStatus();
                alert('视频生成超时，请重试');
                isGenerating = false;
                return;
            }

            const response = await fetch(`/api/video-status/${taskId}`);
            const statusData = await response.json();

            if (statusData.success && statusData.status === 'completed') {
                clearInterval(pollInterval);
                clearInterval(countdownInterval);
                updateStatus('视频生成完成！', 100);
                
                setTimeout(() => {
                    hideGenerationStatus();
                    showVideoResult(statusData.video_url);
                    isGenerating = false;
                }, 1500);
            } else if (statusData.success && statusData.status === 'failed') {
                clearInterval(pollInterval);
                clearInterval(countdownInterval);
                hideGenerationStatus();
                alert('视频生成失败：' + (statusData.error || '未知错误'));
                isGenerating = false;
            }
        } catch (error) {
            // 静默处理错误，继续轮询
        }
    }, 3000); // 每3秒检查一次
}

/**
 * 显示生成状态
 */
function showGenerationStatus() {
    const statusElement = document.getElementById('video-generation-status');
    if (statusElement) {
        statusElement.style.display = 'block';
    }
    
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
    const statusElement = document.getElementById('video-generation-status');
    if (statusElement) {
        statusElement.style.display = 'none';
    }
    
    const generateBtn = document.getElementById('generate-video-btn');
    if (generateBtn) {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> 生成视频';
    }
}

/**
 * 更新状态显示 - 儿童友好版本
 */
function updateStatus(message, progress, timeRemaining = null) {
    const messageElement = document.getElementById('status-message');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    // 更友好的儿童用户状态信息
    let friendlyMessage = message;
    if (message.includes('初始化') || message.includes('预计生成时间')) {
        friendlyMessage = '准备开始制作视频...';
    } else if (message.includes('排队') || message.includes('任务排队')) {
        friendlyMessage = '小AI正在准备工具...';
    } else if (message.includes('生成中') || message.includes('处理') || message.includes('剩余时间')) {
        friendlyMessage = '小AI正在认真画视频...';
        // 保留剩余时间信息
        if (message.includes('剩余时间约')) {
            const timeMatch = message.match(/剩余时间约\s*(\d+:\d+)/);
            if (timeMatch) {
                friendlyMessage += ` (还需要约 ${timeMatch[1]})`;
            }
        }
    } else if (message.includes('即将完成')) {
        friendlyMessage = '马上就好了，小AI正在做最后的处理...';
    } else if (message.includes('完成')) {
        friendlyMessage = '太棒了！视频制作完成！';
    }
    
    if (messageElement) {
        messageElement.textContent = friendlyMessage;
    }
    
    if (progressFill) {
        progressFill.style.width = `${progress}%`;
    }
    
    if (progressText) {
        progressText.textContent = `${Math.round(progress)}%`;
    }
}

/**
 * 获取预估制作时间
 */
function getEstimatedTime() {
    const duration = parseInt(document.getElementById('video-duration').value) || 2;
    const baseTime = duration * 15; // 每秒视频约需15秒处理时间
    const minutes = Math.floor(baseTime / 60);
    const seconds = baseTime % 60;
    
    if (minutes > 0) {
        return `${minutes}分${seconds}秒`;
    } else {
        return `${seconds}秒`;
    }
}

/**
 * 显示视频生成结果
 */
function showVideoResult(videoUrl) {
    const resultSection = document.getElementById('video-result-section');
    const videoElement = document.getElementById('generated-video');
    
    if (resultSection && videoElement) {
        videoElement.src = videoUrl;
        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * 保存视频到用户作品
 */
async function saveVideoToGallery() {
    const videoElement = document.getElementById('generated-video');
    if (!videoElement || !videoElement.src) {
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
                video_url: videoElement.src
            })
        });
        
        const result = await response.json();
        if (result.success) {
            alert('视频已保存到你的作品集！');
        } else {
            alert('保存失败：' + result.error);
        }
    } catch (error) {
        alert('保存失败，请重试');
    }
}

/**
 * 下载视频
 */
function downloadVideo() {
    const videoElement = document.getElementById('generated-video');
    if (!videoElement || !videoElement.src) {
        alert('没有可下载的视频');
        return;
    }
    
    const link = document.createElement('a');
    link.href = videoElement.src;
    link.download = `ai-video-${Date.now()}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-video-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', startVideoGeneration);
    }
    
    const saveBtn = document.getElementById('save-video-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveVideoToGallery);
    }
    
    const downloadBtn = document.getElementById('download-video-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadVideo);
    }
});