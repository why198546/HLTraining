/**
 * 视频生成功能
 */

let isGenerating = false;
let pollInterval = null;
let countdownInterval = null;

// 注意：sessionId 和 imageUrl 由 HTML 模板传递，不在这里声明

// 页面加载时初始化配置
document.addEventListener('DOMContentLoaded', function() {
    initializeFromURLParams();
});

/**
 * 从URL参数初始化配置
 */
function initializeFromURLParams() {
    const urlParams = new URLSearchParams(window.location.search);
    
    console.log('🔧 从URL参数初始化视频配置:');
    console.log('  sessionId:', sessionId);  // 使用HTML模板传递的sessionId
    console.log('  imageUrl:', imageUrl);    // 使用HTML模板传递的imageUrl
    
    // 为视频页面设置默认的动作描述提示
    const promptTextarea = document.getElementById('video-prompt');
    if (promptTextarea && !promptTextarea.value.trim()) {
        // 只有当输入框为空时才设置默认提示
        promptTextarea.placeholder = "描述你希望画面中的动作和变化，例如：角色微笑并挥手，背景中的云朵缓慢移动，整体画面温馨欢快...";
    }
    
    // 设置其他配置
    const duration = urlParams.get('duration');
    if (duration) {
        const durationSelect = document.getElementById('video-duration');
        if (durationSelect) {
            durationSelect.value = duration;
            console.log('  时长:', duration);
        }
    }
    
    const aspectRatio = urlParams.get('aspect_ratio');
    if (aspectRatio) {
        const aspectSelect = document.getElementById('aspect-ratio');
        if (aspectSelect) {
            aspectSelect.value = aspectRatio;
            console.log('  宽高比:', aspectRatio);
        }
    }
    
    const quality = urlParams.get('quality');
    if (quality) {
        const qualitySelect = document.getElementById('video-quality');
        if (qualitySelect) {
            qualitySelect.value = quality;
            console.log('  分辨率:', quality);
        }
    }
    
    const motionIntensity = urlParams.get('motion_intensity');
    if (motionIntensity) {
        const motionSelect = document.getElementById('motion-intensity');
        if (motionSelect) {
            motionSelect.value = motionIntensity;
            console.log('  运动强度:', motionIntensity);
        }
    }
    
    const model = urlParams.get('model');
    if (model) {
        const modelSelect = document.getElementById('video-model');
        if (modelSelect) {
            modelSelect.value = model;
            console.log('  模型:', model);
        }
    }
    
    // 更新时间预估
    updateTimeEstimate();
    
    console.log('✅ 视频配置初始化完成');
}

/**
 * 开始视频生成
 */
async function startVideoGeneration() {
    if (isGenerating) {
        console.warn('⚠️ 视频生成已在进行中，忽略重复请求');
        return;
    }

    const prompt = document.getElementById('video-prompt').value.trim();
    if (!prompt) {
        toast.warning('请输入视频动作描述！');
        return;
    }

    const duration = parseInt(document.getElementById('video-duration').value);
    const aspectRatio = document.getElementById('aspect-ratio').value;
    const quality = document.getElementById('video-quality').value;
    const motionIntensity = document.getElementById('motion-intensity').value;
    const model = document.getElementById('video-model').value;

    // 直接执行视频生成，不显示确认对话框
    const config = {
        prompt: prompt,
        duration: duration,
        aspectRatio: aspectRatio,
        quality: quality,
        motionIntensity: motionIntensity,
        model: model
    };
    
    console.log('🚀 直接开始生成视频，配置:', config);
    await executeVideoGeneration(config);
}

/**
 * 实际执行视频生成（确认后调用）
 */
async function executeVideoGeneration(config) {
    console.log('🎬 开始视频生成:');
    console.log(`   提示词: ${config.prompt}`);
    console.log(`   时长: ${config.duration}秒`);
    console.log(`   宽高比: ${config.aspectRatio}`);
    console.log(`   分辨率: ${config.quality}`);
    console.log(`   运动强度: ${config.motionIntensity}`);
    console.log(`   AI模型: ${config.model}`);

    isGenerating = true;
    showGenerationStatus();
    
    // 显示数据准备阶段
    updateStatus('正在翻译提示词...', 1);
    
    try {
        console.log('📤 发送视频生成请求...');
        
        // 模拟数据准备时间
        await new Promise(resolve => setTimeout(resolve, 1000));
        updateStatus('正在上传到AI模型...', 3);
        
        const response = await fetch('/api/generate-video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                image_url: imageUrl,
                prompt: config.prompt,
                duration: config.duration,
                aspect_ratio: config.aspectRatio,
                quality: config.quality,
                motion_intensity: config.motionIntensity,
                model: config.model
            })
        });

        console.log(`📡 服务器响应状态: ${response.status}`);
        
        if (!response.ok) {
            // 特殊处理配额错误
            if (response.status === 429) {
                const errorData = await response.json();
                if (errorData.error_type === 'quota_exceeded') {
                    throw new Error(`🚫 API配额不足：${errorData.error}`);
                }
            }
            throw new Error(`HTTP错误: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        console.log('📊 服务器响应数据:', data);

        if (data.success) {
            console.log(`✅ 视频生成任务已启动: ${data.task_id}`);
            startCountdown(config.duration, config.quality, config.model);
            pollVideoStatus(data.task_id);
        } else {
            throw new Error(data.error || '视频生成启动失败');
        }
    } catch (error) {
        console.error('❌ 视频生成请求失败:', error);
        hideGenerationStatus();
        
        let errorMessage = '视频生成失败：' + error.message;
        if (error.message.includes('网络') || error.message.includes('Network')) {
            errorMessage = '网络连接异常，请检查网络连接后重试';
        } else if (error.message.includes('HTTP错误: 500')) {
            errorMessage = '服务器内部错误，请稍后重试';
        } else if (error.message.includes('HTTP错误: 413')) {
            errorMessage = '图片文件过大，请选择较小的图片';
        }
        
        alert(errorMessage);
        isGenerating = false;
    }
}

/**
 * 开始倒计时
 */
function startCountdown(duration, quality = '720p', model = 'veo-3.1-fast-generate-preview') {  // 默认快速版
    // 根据分辨率调整预估时间
    let baseMultiplier = 15; // 720p基础倍数
    
    if (quality === '1080p') {
        baseMultiplier = 25; // 1080p需要更长时间，约1.67倍
    }
    
    // 根据模型调整时间（快速版更快）
    if (model === 'veo-3.1-fast-generate-preview') {
        baseMultiplier = Math.round(baseMultiplier * 0.7); // 快速版约快30%
    }
    
    // 添加数据准备时间
    const preparationTime = 15; // 15秒准备时间
    const estimatedSeconds = duration * baseMultiplier + preparationTime;
    let remainingSeconds = estimatedSeconds;
    
    // 显示友好的预估时间信息
    const estimatedTime = getEstimatedTime(duration, quality, model);
    updateStatus(`小AI开始工作啦！预计需要 ${estimatedTime}`, 5);
    
    const modelName = model === 'veo-3.1-fast-generate-preview' ? '快速版' : '标准版';
    console.log(`🕐 开始倒计时: ${duration}秒${quality}${modelName}视频预计需要${estimatedSeconds}秒(${Math.floor(estimatedSeconds/60)}分${estimatedSeconds%60}秒)`);
    
    // 动态倒计时，每秒减少
    countdownInterval = setInterval(() => {
        remainingSeconds--;
        const progress = ((estimatedSeconds - remainingSeconds) / estimatedSeconds) * 80; // 最多到80%
        const minutes = Math.floor(remainingSeconds / 60);
        const seconds = remainingSeconds % 60;
        
        if (remainingSeconds > 0) {
            updateStatus(`视频生成中... 剩余时间约 ${minutes}:${seconds.toString().padStart(2, '0')}`, progress);
        } else {
            clearInterval(countdownInterval);
            updateStatus('视频即将完成...', 85);
        }
    }, 1000);  // 每1秒更新一次
}

/**
 * 轮询视频生成状态
 */
async function pollVideoStatus(taskId) {
    let pollCount = 0;
    const maxPolls = 300; // 5分钟最大轮询时间
    
    console.log(`🔄 开始轮询任务状态: ${taskId}`);

    pollInterval = setInterval(async () => {
        try {
            pollCount++;
            console.log(`📊 轮询第${pollCount}次，任务ID: ${taskId}`);
            
            if (pollCount > maxPolls) {
                clearInterval(pollInterval);
                clearInterval(countdownInterval);
                hideGenerationStatus();
                const errorMsg = `视频生成超时（轮询${pollCount}次，约${Math.floor(pollCount*3/60)}分钟）`;
                console.error(`❌ ${errorMsg}`);
                alert(errorMsg + '，请重试');
                isGenerating = false;
                return;
            }

            const response = await fetch(`/api/video-status/${taskId}`);
            const statusData = await response.json();
            
            console.log(`📊 状态响应:`, statusData);

            if (statusData.success && statusData.status === 'completed') {
                clearInterval(pollInterval);
                clearInterval(countdownInterval);
                console.log(`✅ 视频生成完成: ${statusData.video_url}`);
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
                
                const errorDetails = statusData.error || '未知错误';
                console.error(`❌ 视频生成失败:`, statusData);
                
                // 更详细的错误信息
                let userMessage = '视频生成失败：' + errorDetails;
                if (errorDetails.includes('content_safety') || errorDetails.includes('content_safety_violation')) {
                    userMessage = '提示词内容触发了安全过滤器，请尝试使用更温和的描述词汇';
                } else if (errorDetails.includes('timeout') || errorDetails.includes('超时')) {
                    userMessage = '视频生成超时，请稍后重试';
                } else if (errorDetails.includes('quota') || errorDetails.includes('配额')) {
                    userMessage = 'API配额不足，请稍后重试';
                }
                
                alert(userMessage);
                isGenerating = false;
            } else if (statusData.success && statusData.status === 'content_filtered') {
                clearInterval(pollInterval);
                clearInterval(countdownInterval);
                hideGenerationStatus();
                
                console.warn(`⚠️ 内容被过滤:`, statusData);
                alert('提示词内容触发了安全过滤器，请尝试使用更温和的描述词汇');
                isGenerating = false;
            } else if (!statusData.success) {
                // API调用失败
                console.error(`❌ API调用失败:`, statusData);
                
                // 如果连续失败多次，停止轮询
                if (pollCount > 10) {
                    clearInterval(pollInterval);
                    clearInterval(countdownInterval);
                    hideGenerationStatus();
                    alert('网络连接异常，请检查网络后重试');
                    isGenerating = false;
                }
            } else {
                // 继续处理中
                console.log(`⏳ 视频生成中... (${pollCount}/${maxPolls})`);
                if (statusData.message) {
                    updateStatus(statusData.message, statusData.progress || 50);
                }
            }
        } catch (error) {
            console.error(`❌ 轮询状态时出错:`, error);
            
            // 如果网络错误连续发生多次，停止轮询
            if (pollCount > 20) {
                clearInterval(pollInterval);
                clearInterval(countdownInterval);
                hideGenerationStatus();
                alert('网络连接异常，请检查网络后重试');
                isGenerating = false;
            }
        }
    }, 3000); // 每3秒检查一次
}

/**
 * 显示生成状态
 */
function showGenerationStatus() {
    const generateBtn = document.getElementById('generate-video-btn');
    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.classList.add('generating');
        generateBtn.style.background = '#6b7280'; // 灰色
        generateBtn.innerHTML = `
            <i class="fas fa-spinner fa-spin"></i>
            <span>生成中...</span>
            <span id="generation-progress">0%</span>
        `;
    }
}

/**
 * 隐藏生成状态，恢复按钮
 */
function hideGenerationStatus() {
    const generateBtn = document.getElementById('generate-video-btn');
    const btnEstimate = document.getElementById('btn-estimate');
    
    if (generateBtn) {
        generateBtn.disabled = false;
        generateBtn.classList.remove('generating');
        generateBtn.style.background = ''; // 恢复原色
        generateBtn.innerHTML = `
            <i class="fas fa-wand-magic-sparkles"></i>
            <span id="btn-text">生成视频</span>
            <span id="btn-estimate" class="btn-estimate">${btnEstimate ? btnEstimate.textContent : ''}</span>
        `;
    }
}

/**
 * 更新按钮进度
 */
function updateButtonProgress(progress, message = '') {
    const generateBtn = document.getElementById('generate-video-btn');
    const progressEl = document.getElementById('generation-progress');
    
    if (generateBtn && generateBtn.classList.contains('generating')) {
        // 计算渐变色：从灰色(107, 114, 128)到蓝色(99, 102, 241)
        const grayR = 107, grayG = 114, grayB = 128;
        const blueR = 99, blueG = 102, blueB = 241;
        
        const ratio = Math.min(progress / 100, 1);
        const r = Math.round(grayR + (blueR - grayR) * ratio);
        const g = Math.round(grayG + (blueG - grayG) * ratio);
        const b = Math.round(grayB + (blueB - grayB) * ratio);
        
        generateBtn.style.background = `rgb(${r}, ${g}, ${b})`;
        
        if (progressEl) {
            progressEl.textContent = `${Math.round(progress)}%`;
        }
        
        if (message) {
            const btnText = generateBtn.querySelector('span:not(#generation-progress)');
            if (btnText) {
                btnText.textContent = message;
            }
        }
    }
}

/**
 * 更新状态显示 - 儿童友好版本
 */
function updateStatus(message, progress, timeRemaining = null) {
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
    
    // 更新按钮状态而不是单独的进度条
    updateButtonProgress(friendlyMessage, progress, timeRemaining);
}

/**
 * 获取预估制作时间
 */
function getEstimatedTime(duration = null, quality = null, model = null) {
    // 如果没有传参数，从页面元素获取
    if (duration === null) {
        duration = parseInt(document.getElementById('video-duration').value) || 4;
    }
    if (quality === null) {
        quality = document.getElementById('video-quality').value || '720p';
    }
    if (model === null) {
        model = document.getElementById('video-model').value || 'veo-3.1-fast-generate-preview';  // 改为默认快速版
    }
    
    // 根据分辨率调整处理时间
    let baseMultiplier = 15; // 720p基础倍数：每秒视频需要15秒处理
    
    if (quality === '1080p') {
        baseMultiplier = 25; // 1080p需要更长时间：每秒视频需要25秒处理
    }
    
    // 根据模型调整时间（快速版更快）
    if (model === 'veo-3.1-fast-generate-preview') {
        baseMultiplier = Math.round(baseMultiplier * 0.7); // 快速版约快30%
    }
    
    // 数据准备和发送时间（固定15秒）
    const preparationTime = 15;
    
    const baseTime = duration * baseMultiplier + preparationTime;  // 添加准备时间
    const minutes = Math.floor(baseTime / 60);
    const seconds = baseTime % 60;
    
    let result = '';
    if (minutes > 0) {
        result = `${minutes}分`;
        if (seconds > 0) {
            result += `${seconds}秒`;
        }
    } else {
        result = `${seconds}秒`;
    }
    
    // 添加模型和分辨率说明
    const modelNote = model === 'veo-3.1-fast-generate-preview' ? ' (快速版)' : '';
    const qualityNote = quality === '1080p' ? ' (高清)' : '';
    return result + modelNote + qualityNote;
    return result + qualityNote;
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
        toast.warning('没有可保存的视频');
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
            toast.success('视频已保存到你的作品集！');
        } else {
            toast.error('保存失败：' + result.error);
        }
    } catch (error) {
        toast.error('保存失败，请重试');
    }
}

/**
 * 下载视频
 */
function downloadVideo() {
    const videoElement = document.getElementById('generated-video');
    if (!videoElement || !videoElement.src) {
        toast.warning('没有可下载的视频');
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
    
    // 添加时间预估更新监听器
    const durationSelect = document.getElementById('video-duration');
    const qualitySelect = document.getElementById('video-quality');
    const modelSelect = document.getElementById('video-model');
    
    if (durationSelect) {
        durationSelect.addEventListener('change', updateTimeEstimate);
    }
    
    if (qualitySelect) {
        qualitySelect.addEventListener('change', updateTimeEstimate);
    }
    
    if (modelSelect) {
        modelSelect.addEventListener('change', updateTimeEstimate);
    }
    
    // 初始化时间预估显示
    updateTimeEstimate();
});

/**
 * 更新时间预估显示
 */
function updateTimeEstimate() {
    const duration = parseInt(document.getElementById('video-duration').value) || 4;
    const quality = document.getElementById('video-quality').value || '720p';
    const model = document.getElementById('video-model').value || 'veo-3.1-generate-preview';
    
    const estimatedTime = getEstimatedTime(duration, quality, model);
    const btnEstimate = document.getElementById('btn-estimate');
    const generateBtn = document.getElementById('generate-video-btn');
    
    if (btnEstimate) {
        // 移除质量说明，只显示时间
        const timeOnly = estimatedTime.replace(/ \(.*\)$/, '');
        const isFastModel = model === 'veo-3.1-fast-generate-preview';
        const speedNote = isFastModel ? '快速生成' : '标准生成';
        btnEstimate.textContent = ` (预估${timeOnly}·${speedNote})`;
    }
    
    console.log(`⏱️ 时间预估更新: ${duration}秒${quality}视频 (${model}) -> ${estimatedTime}`);
}

/**
 * 显示视频生成确认对话框
 */
async function showVideoGenerationConfirmDialog(config) {
    console.log('🔍 准备显示确认对话框，翻译提示词...');
    
    // 先翻译提示词
    let translatedPrompt = config.prompt;
    try {
        const response = await fetch('/api/translate-prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: config.prompt
            })
        });

        if (response.ok) {
            const result = await response.json();
            translatedPrompt = result.translated_prompt;
            console.log('✅ 提示词翻译完成:', translatedPrompt);
        }
    } catch (error) {
        console.warn('⚠️ 翻译提示词失败，使用原始提示词:', error);
    }

    // 创建模态框
    const modal = document.createElement('div');
    modal.id = 'video-generation-confirm-modal';
    modal.className = 'video-config-modal';
    modal.innerHTML = `
        <div class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3><i class="fas fa-video"></i> 确认视频生成参数</h3>
                    <button class="modal-close" onclick="closeVideoGenerationConfirmModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="modal-body">
                    <div class="config-grid">
                        <div class="config-item">
                            <label for="confirm-prompt">提示词（已翻译）：</label>
                            <textarea id="confirm-prompt" rows="4">${translatedPrompt}</textarea>
                        </div>
                        
                        <div class="config-item">
                            <label for="confirm-duration">视频时长：</label>
                            <select id="confirm-duration">
                                <option value="4" ${config.duration === 4 ? 'selected' : ''}>4秒</option>
                                <option value="8" ${config.duration === 8 ? 'selected' : ''}>8秒</option>
                                <option value="12" ${config.duration === 12 ? 'selected' : ''}>12秒</option>
                            </select>
                        </div>
                        
                        <div class="config-item">
                            <label for="confirm-aspect-ratio">宽高比：</label>
                            <select id="confirm-aspect-ratio">
                                <option value="16:9" ${config.aspectRatio === '16:9' ? 'selected' : ''}>16:9 (横向)</option>
                                <option value="9:16" ${config.aspectRatio === '9:16' ? 'selected' : ''}>9:16 (竖向)</option>
                                <option value="1:1" ${config.aspectRatio === '1:1' ? 'selected' : ''}>1:1 (方形)</option>
                            </select>
                        </div>
                        
                        <div class="config-item">
                            <label for="confirm-quality">分辨率：</label>
                            <select id="confirm-quality">
                                <option value="720p" ${config.quality === '720p' ? 'selected' : ''}>720p (标清)</option>
                                <option value="1080p" ${config.quality === '1080p' ? 'selected' : ''}>1080p (高清)</option>
                            </select>
                        </div>
                        
                        <div class="config-item">
                            <label for="confirm-motion-intensity">运动强度：</label>
                            <select id="confirm-motion-intensity">
                                <option value="低" ${config.motionIntensity === '低' ? 'selected' : ''}>低</option>
                                <option value="中" ${config.motionIntensity === '中' ? 'selected' : ''}>中</option>
                                <option value="高" ${config.motionIntensity === '高' ? 'selected' : ''}>高</option>
                            </select>
                        </div>
                        
                        <div class="config-item">
                            <label for="confirm-model">AI模型：</label>
                            <select id="confirm-model">
                                <option value="veo-3.1-fast-generate-preview" ${config.model === 'veo-3.1-fast-generate-preview' ? 'selected' : ''}>Veo 3.1 快速模式</option>
                                <option value="veo-3.1-generate-preview" ${config.model === 'veo-3.1-generate-preview' ? 'selected' : ''}>Veo 3.1 标准模式</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeVideoGenerationConfirmModal()">取消</button>
                    <button class="btn btn-primary" onclick="confirmVideoGenerationExecution()">
                        <i class="fas fa-play"></i>
                        确认生成
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    
    // 显示模态框
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

/**
 * 关闭视频生成确认对话框
 */
function closeVideoGenerationConfirmModal() {
    const modal = document.getElementById('video-generation-confirm-modal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

/**
 * 确认执行视频生成
 */
function confirmVideoGenerationExecution() {
    // 获取用户修改后的配置
    const finalConfig = {
        prompt: document.getElementById('confirm-prompt').value.trim(),
        duration: parseInt(document.getElementById('confirm-duration').value),
        aspectRatio: document.getElementById('confirm-aspect-ratio').value,
        quality: document.getElementById('confirm-quality').value,
        motionIntensity: document.getElementById('confirm-motion-intensity').value,
        model: document.getElementById('confirm-model').value
    };

    console.log('✅ 用户确认生成，最终配置:', finalConfig);

    // 关闭模态框
    closeVideoGenerationConfirmModal();

    // 执行视频生成
    executeVideoGeneration(finalConfig);
}