/**
 * 语音输入模块 - 支持语音识别和AI整理
 */

let recognition = null;
let isRecording = false;
let voiceTranscript = '';
let microphonePermissionGranted = false;

/**
 * 检查麦克风权限
 */
async function checkMicrophonePermission() {
    try {
        // 检查浏览器是否支持权限API
        if (navigator.permissions && navigator.permissions.query) {
            const permissionStatus = await navigator.permissions.query({ name: 'microphone' });
            
            if (permissionStatus.state === 'granted') {
                microphonePermissionGranted = true;
                console.log('✅ 麦克风权限已授予');
                return true;
            } else if (permissionStatus.state === 'prompt') {
                console.log('⚠️ 需要请求麦克风权限');
                return false;
            } else {
                console.log('❌ 麦克风权限被拒绝');
                return false;
            }
        }
    } catch (error) {
        console.log('无法检查麦克风权限:', error);
    }
    return false;
}

/**
 * 显示权限引导提示
 */
function showPermissionGuide() {
    // 检查是否已经存在引导界面
    if (document.getElementById('permissionGuide')) {
        return;
    }
    
    const guideHtml = `
        <div class="permission-guide-overlay" id="permissionGuide">
            <div class="permission-guide-content">
                <div class="guide-icon">🎤</div>
                <h3>麦克风权限设置</h3>
                <p>看起来麦克风权限被拒绝了。请按以下步骤设置：</p>
                <div class="guide-steps">
                    <div class="guide-step">
                        <span class="step-number">1</span>
                        <span>点击地址栏左侧的网站设置图标</span>
                    </div>
                    <div class="guide-step">
                        <span class="step-number">2</span>
                        <span>找到"麦克风"选项</span>
                    </div>
                    <div class="guide-step">
                        <span class="step-number">3</span>
                        <span>选择"<strong>允许</strong>"</span>
                    </div>
                    <div class="guide-step">
                        <span class="step-number">4</span>
                        <span>刷新页面后重试</span>
                    </div>
                </div>
                <p class="guide-note">💡 设置为"允许"后，将不会再次询问</p>
                <button class="guide-close-btn" onclick="closePermissionGuide()">我知道了</button>
            </div>
        </div>
    `;
    
    // 添加到页面
    const guideElement = document.createElement('div');
    guideElement.innerHTML = guideHtml;
    document.body.appendChild(guideElement.firstElementChild);
}

/**
 * 关闭权限引导
 */
function closePermissionGuide() {
    const guide = document.getElementById('permissionGuide');
    if (guide) {
        guide.remove();
    }
}

/**
 * 初始化语音识别
 */
function initVoiceRecognition() {
    // 检查浏览器支持
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        console.error('浏览器不支持语音识别');
        return null;
    }
    
    recognition = new SpeechRecognition();
    recognition.lang = 'zh-CN'; // 设置为中文
    recognition.continuous = true; // 持续识别
    recognition.interimResults = true; // 显示中间结果
    
    recognition.onstart = function() {
        console.log('语音识别已启动');
        isRecording = true;
        updateVoiceButtonState('recording');
    };
    
    recognition.onresult = function(event) {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        voiceTranscript = finalTranscript || interimTranscript;
        
        // 实时显示识别结果
        const promptTextarea = document.getElementById('creation-prompt');
        if (promptTextarea) {
            promptTextarea.value = voiceTranscript;
        }
    };
    
    recognition.onerror = function(event) {
        console.error('语音识别错误:', event.error);
        isRecording = false;
        updateVoiceButtonState('error');
        
        let errorMessage = '语音识别出错';
        let shouldShowGuide = false;
        
        switch(event.error) {
            case 'no-speech':
                errorMessage = '未检测到语音，请重试';
                break;
            case 'audio-capture':
                errorMessage = '无法访问麦克风';
                shouldShowGuide = true;
                break;
            case 'not-allowed':
                errorMessage = '请在浏览器中允许使用麦克风';
                shouldShowGuide = true;
                break;
            case 'aborted':
                // 用户主动停止，不显示错误
                return;
        }
        
        showNotification(errorMessage, 'error');
        
        // 只在权限相关错误时显示引导
        if (shouldShowGuide) {
            setTimeout(() => {
                showPermissionGuide();
            }, 500);
        }
    };
    
    recognition.onend = function() {
        console.log('语音识别已结束');
        if (isRecording) {
            // 如果是用户主动停止，进行AI整理
            processVoiceInput();
        }
        isRecording = false;
        updateVoiceButtonState('idle');
    };
    
    return recognition;
}

/**
 * 开始语音输入
 */
async function startVoiceInput() {
    if (!recognition) {
        recognition = initVoiceRecognition();
        if (!recognition) {
            showNotification('您的浏览器不支持语音识别功能', 'error');
            return;
        }
    }
    
    if (isRecording) {
        // 停止录音
        recognition.stop();
    } else {
        // 开始录音时不显示引导，让浏览器自然弹出权限请求
        voiceTranscript = '';
        try {
            recognition.start();
            showNotification('🎤 请开始说话...', 'info');
        } catch (error) {
            console.error('启动语音识别失败:', error);
            
            // 如果是权限错误，显示友好提示
            if (error.message && (error.message.includes('not-allowed') || error.name === 'NotAllowedError')) {
                showNotification('请在浏览器弹窗中点击"允许"以使用麦克风', 'warning');
            } else {
                showNotification('启动语音识别失败，请重试', 'error');
            }
        }
    }
}

/**
 * 处理语音输入 - 使用AI整理成清晰的prompt
 */
async function processVoiceInput() {
    if (!voiceTranscript || voiceTranscript.trim().length === 0) {
        showNotification('未识别到有效内容', 'warning');
        return;
    }
    
    updateVoiceButtonState('processing');
    showNotification('🤖 AI正在整理您的创意...', 'info');
    
    try {
        const response = await fetch('/api/organize-prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                voice_input: voiceTranscript
            })
        });
        
        if (!response.ok) {
            throw new Error('AI整理失败');
        }
        
        const data = await response.json();
        
        if (data.success) {
            const promptTextarea = document.getElementById('creation-prompt');
            if (promptTextarea) {
                promptTextarea.value = data.organized_prompt;
                
                // 添加动画效果
                promptTextarea.classList.add('highlight-update');
                setTimeout(() => {
                    promptTextarea.classList.remove('highlight-update');
                }, 2000);
            }
            
            showNotification('✨ 创意整理完成！', 'success');
        } else {
            throw new Error(data.error || 'AI整理失败');
        }
        
    } catch (error) {
        console.error('AI整理错误:', error);
        showNotification('AI整理失败，已保留原始语音内容', 'warning');
    } finally {
        updateVoiceButtonState('idle');
    }
}

/**
 * 更新语音按钮状态
 */
function updateVoiceButtonState(state) {
    const voiceBtn = document.getElementById('voice-input-btn');
    if (!voiceBtn) return;
    
    const icon = voiceBtn.querySelector('i');
    
    // 移除所有状态类
    voiceBtn.classList.remove('recording', 'processing');
    
    switch(state) {
        case 'recording':
            voiceBtn.classList.add('recording');
            icon.className = 'fas fa-stop';
            voiceBtn.title = '停止录音';
            break;
        case 'processing':
            voiceBtn.classList.add('processing');
            icon.className = 'fas fa-spinner';
            voiceBtn.title = 'AI整理中...';
            break;
        case 'error':
        case 'idle':
        default:
            icon.className = 'fas fa-microphone';
            voiceBtn.title = '语音输入';
            break;
    }
}

/**
 * 显示通知消息
 */
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `voice-notification ${type}`;
    notification.textContent = message;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // 3秒后移除
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查浏览器支持
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        const voiceBtn = document.getElementById('voice-input-btn');
        if (voiceBtn) {
            voiceBtn.disabled = true;
            voiceBtn.title = '您的浏览器不支持语音识别';
            voiceBtn.style.opacity = '0.5';
        }
    }
    
    // 检测是否为Safari浏览器
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    if (isSafari) {
        const safariHint = document.getElementById('safari-voice-hint');
        if (safariHint) {
            safariHint.style.display = 'block';
        }
    }
    
    // 不在页面加载时检查权限，避免每次刷新都弹窗
    // 只在用户点击麦克风按钮时才请求权限
});
