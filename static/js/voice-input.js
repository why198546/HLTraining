/**
 * 语音输入模块 - 支持语音识别和AI整理
 */

let recognition = null;
let isRecording = false;
let voiceTranscript = '';
let microphonePermissionGranted = false;
let recognitionState = 'idle'; // 'idle', 'starting', 'recording', 'stopping', 'processing'
let recognitionAbortingPromise = null; // 用于追踪 abort 操作

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
    recognition.maxAlternatives = 3; // 获取多个备选结果
    
    // 增加暂停容忍时间，适应儿童断断续续说话
    // 注意：这些属性不是标准API，但Chrome支持
    if (recognition.continuous) {
        console.log('✅ 连续模式已启用，适合儿童断断续续说话');
    }
    
    recognition.onstart = function() {
        console.log('语音识别已启动');
        isRecording = true;
        updateVoiceButtonState('recording');
        
        // 显示录音状态指示器
        const indicator = document.getElementById('voice-recording-indicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
    };
    
    recognition.onresult = function(event) {
        let interimTranscript = '';
        let finalTranscript = '';
        
        // 累积所有最终结果，支持断断续续说话
        for (let i = 0; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else if (i >= event.resultIndex) {
                // 只累加新的临时结果
                interimTranscript += transcript;
            }
        }
        
        // 如果有新的最终结果，添加到已有内容后面
        if (finalTranscript) {
            if (voiceTranscript && !voiceTranscript.endsWith(finalTranscript.substring(0, Math.min(10, finalTranscript.length)))) {
                // 检测停顿，添加逗号和空格连接
                voiceTranscript = (voiceTranscript + '，' + finalTranscript).trim();
            } else if (!voiceTranscript) {
                voiceTranscript = finalTranscript;
            }
            console.log('📝 累积语音内容:', voiceTranscript);
        }
        
        // 实时显示识别结果（包含临时结果）
        const promptTextarea = document.getElementById('creation-prompt');
        if (promptTextarea) {
            const displayText = voiceTranscript + (interimTranscript ? ' ' + interimTranscript : '');
            promptTextarea.value = displayText;
            // 添加视觉提示
            promptTextarea.style.borderColor = interimTranscript ? '#4CAF50' : '';
        }
    };
    
    recognition.onerror = function(event) {
        console.error('语音识别错误:', event.error);
        console.error('错误详情:', event);
        isRecording = false;
        recognitionState = 'idle';
        updateVoiceButtonState('error');
        
        let errorMessage = '语音识别出错';
        let shouldShowGuide = false;
        
        switch(event.error) {
            case 'no-speech':
                errorMessage = '⚠️ 未检测到语音\n\n请检查:\n1. 麦克风是否正常工作\n2. 是否给予了麦克风权限\n3. 周围环境是否过于嘈杂';
                break;
            case 'audio-capture':
                errorMessage = '❌ 无法访问麦克风\n\n请检查:\n1. 麦克风硬件是否正常\n2. 其他应用是否占用了麦克风\n3. 重启浏览器后重试';
                shouldShowGuide = true;
                break;
            case 'not-allowed':
                errorMessage = '❌ 麦克风权限被拒绝\n\n请允许网站使用麦克风:\n1. 点击地址栏左侧的 ⓘ 图标\n2. 找到"麦克风"选项\n3. 选择"允许"';
                shouldShowGuide = true;
                break;
            case 'network':
                errorMessage = '❌ 网络错误\n\n请检查您的网络连接后重试';
                break;
            case 'service-not-allowed':
                errorMessage = '❌ 浏览器不允许使用语音识别服务\n\n请:\n1. 刷新页面\n2. 检查网络连接\n3. 重试';
                break;
            case 'bad-grammar':
                errorMessage = '⚠️ 语音识别配置错误\n\n请刷新页面后重试';
                break;
            case 'aborted':
                // 用户主动停止，不显示错误
                console.log('用户主动停止了语音识别');
                recognitionState = 'idle';
                return;
            default:
                errorMessage = `❌ 错误: ${event.error}\n\n请重试或刷新页面后使用其他浏览器`;
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
        console.log('🏁 语音识别已结束');
        console.log(`状态转换: recognitionState ${recognitionState} -> idle`);
        
        const wasRecording = isRecording;
        isRecording = false;
        recognitionState = 'idle';
        
        // 隐藏录音状态指示器
        const indicator = document.getElementById('voice-recording-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
        
        // 重置输入框边框颜色
        const promptTextarea = document.getElementById('creation-prompt');
        if (promptTextarea) {
            promptTextarea.style.borderColor = '';
        }
        
        if (wasRecording) {
            // 如果是用户主动停止，进行AI整理
            console.log('💭 准备进行 AI 整理...');
            processVoiceInput();
        }
        
        updateVoiceButtonState('idle');
    };
    
    return recognition;
}

/**
 * 开始语音输入
 */
async function startVoiceInput() {
    console.log(`📊 当前状态: recording=${isRecording}, recognitionState=${recognitionState}`);
    
    // 如果已经在录音，则停止
    if (isRecording) {
        try {
            console.log('🛑 停止语音识别...');
            console.log('📊 累积的语音内容:', voiceTranscript);
            recognitionState = 'stopping';
            if (recognition) {
                recognition.stop();
                showNotification('🎤 录音已停止，正在整理...', 'info');
            }
        } catch (error) {
            console.error('停止语音识别失败:', error);
        }
        return;
    }
    
    // 防止重复启动
    if (recognitionState === 'starting' || recognitionState === 'recording') {
        console.warn('⚠️ 语音识别已经在运行中');
        showNotification('语音识别已在运行中，请稍候...', 'warning');
        return;
    }
    
    // 重置状态
    voiceTranscript = '';
    recognitionState = 'starting';
    
    try {
        // 确保识别对象存在
        if (!recognition) {
            console.log('🔧 初始化新的识别对象...');
            recognition = initVoiceRecognition();
            if (!recognition) {
                showNotification('❌ 您的浏览器不支持语音识别功能\n\n推荐使用最新版 Chrome 浏览器', 'error');
                recognitionState = 'idle';
                return;
            }
        }
        
        // 如果识别对象可能处于不正确状态，先 abort 再等待
        if (recognitionState === 'starting') {
            console.log('🔄 清理可能存在的旧状态...');
            try {
                recognition.abort();
                // 等待 abort 完成
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (e) {
                console.log('abort 没有产生错误（这是预期的）');
            }
        }
        
        // 现在开始识别
        console.log('📢 调用 recognition.start()...');
        recognition.start();
        isRecording = true;
        recognitionState = 'recording';
        showNotification('🎤 请开始说话...', 'info');
        
    } catch (error) {
        console.error('❌ 启动语音识别失败:', error);
        console.error('错误类型:', error.name);
        console.error('错误信息:', error.message);
        console.error('完整错误:', error);
        
        isRecording = false;
        recognitionState = 'idle';
        
        let errorMessage = '启动语音识别失败';
        
        // 详细的错误处理
        if (error.name === 'InvalidStateError') {
            console.log('💡 InvalidStateError 原因分析：');
            console.log('  1. 可能识别对象已在使用中');
            console.log('  2. 可能浏览器内部状态不一致');
            console.log('  3. 尝试重新创建识别对象...');
            
            errorMessage = '⚠️ 语音识别状态异常\n\n正在尝试修复...\n\n请:\n1. 稍候几秒\n2. 重新点击麦克风\n3. 如果继续失败，请刷新页面';
            
            // 尝试重置识别对象
            recognition = null;
            recognitionState = 'idle';
            
        } else if (error.name === 'NotAllowedError' || error.message?.includes('not-allowed')) {
            errorMessage = '❌ 麦克风权限被拒绝\n\n请点击浏览器地址栏左侧的设置图标，允许使用麦克风';
        } else if (error.message?.includes('NotSupportedError')) {
            errorMessage = '❌ 您的浏览器不支持语音识别\n\n请使用最新版 Chrome 浏览器';
        } else if (error.message?.includes('AbortError')) {
            errorMessage = '⚠️ 语音识别被中断\n\n请重试';
        } else if (error.message?.includes('NetworkError')) {
            errorMessage = '❌ 网络错误\n\n请检查网络连接后重试';
        } else if (error.message?.includes('failed to execute') || error.message?.includes('start')) {
            errorMessage = '⚠️ 启动语音识别失败\n\n请:\n1. 刷新页面\n2. 检查麦克风权限\n3. 关闭其他使用麦克风的应用\n4. 重试';
        } else {
            errorMessage = `❌ 启动失败: ${error.message || error.name || '未知错误'}\n\n请:\n1. 刷新页面\n2. 检查麦克风权限\n3. 重试`;
        }
        
        showNotification(errorMessage, 'error');
        updateVoiceButtonState('idle');
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
                voice_input: voiceTranscript,
                child_mode: true,  // 启用儿童模式
                filter_fillers: true  // 过滤语气词
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
    
    // 支持多行信息 (用 \n 换行)
    const lines = message.split('\n');
    notification.innerHTML = lines.map(line => `<div>${line}</div>`).join('');
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // 错误消息显示时间更长
    const displayTime = type === 'error' ? 5000 : 3000;
    
    // 移除
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, displayTime);
    
    // 错误时也打印到控制台便于远程调试
    console.log(`[${type.toUpperCase()}] ${message.replace(/\n/g, ' ')}`);
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

/**
 * 松果课堂专用：获取当前表单的textarea
 */
function getSunguoFormTextareas(event) {
    const button = event.target.closest('.voice-input-btn');
    if (!button) return null;
    
    const form = button.closest('form');
    if (!form) return null;
    
    const rawPrompt = form.querySelector('textarea[name="raw_prompt"]');
    const optimizedPrompt = form.querySelector('textarea[name="prompt"]');
    
    return { rawPrompt, optimizedPrompt, form };
}

/**
 * 松果课堂语音输入启动（支持双栏结构）
 */
window.startVoiceInput = async function(event) {
    if (event) event.preventDefault();
    
    // 检查是否为松果课堂页面（有raw_prompt字段）
    const sunguoTextareas = getSunguoFormTextareas(event);
    const isSunguoClass = sunguoTextareas && sunguoTextareas.rawPrompt;
    
    console.log(`📊 当前状态: recording=${isRecording}, recognitionState=${recognitionState}, 松果课堂=${isSunguoClass}`);
    
    // 如果已经在录音，则停止
    if (isRecording) {
        try {
            console.log('🛑 停止语音识别...');
            console.log('📊 累积的语音内容:', voiceTranscript);
            recognitionState = 'stopping';
            if (recognition) {
                recognition.stop();
                showNotification('🎤 录音已停止，正在整理...', 'info');
            }
        } catch (error) {
            console.error('停止语音识别失败:', error);
        }
        return;
    }
    
    // 防止重复启动
    if (recognitionState === 'starting' || recognitionState === 'recording') {
        console.warn('⚠️ 语音识别已经在运行中');
        showNotification('语音识别已在运行中，请稍候...', 'warning');
        return;
    }
    
    // 重置状态
    voiceTranscript = '';
    recognitionState = 'starting';
    
    try {
        // 确保识别对象存在
        if (!recognition) {
            console.log('🔧 初始化新的识别对象...');
            recognition = initVoiceRecognition();
            if (!recognition) {
                showNotification('❌ 您的浏览器不支持语音识别功能\n\n推荐使用最新版 Chrome 浏览器', 'error');
                recognitionState = 'idle';
                return;
            }
        }
        
        // 为松果课堂设置特定的结果处理
        if (isSunguoClass) {
            recognition.onresult = function(event) {
                let finalTranscript = '';
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                if (finalTranscript) {
                    if (voiceTranscript && !voiceTranscript.endsWith(finalTranscript.substring(0, Math.min(10, finalTranscript.length)))) {
                        // 检测停顿，添加逗号和空格连接
                        voiceTranscript = (voiceTranscript + '，' + finalTranscript).trim();
                    } else if (!voiceTranscript) {
                        voiceTranscript = finalTranscript;
                    }
                    console.log('📝 累积语音内容:', voiceTranscript);
                }
                
                // 实时显示到原始输入框
                if (sunguoTextareas.rawPrompt) {
                    const displayText = voiceTranscript + (interimTranscript ? ' ' + interimTranscript : '');
                    sunguoTextareas.rawPrompt.value = displayText;
                    sunguoTextareas.rawPrompt.style.borderColor = interimTranscript ? '#4CAF50' : '';
                    
                    // 触发input事件，让自动优化逻辑工作
                    sunguoTextareas.rawPrompt.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };
            
            recognition.onend = async function() {
                console.log('🏁 语音识别结束，voiceTranscript:', voiceTranscript);
                isRecording = false;
                
                // 隐藏录音指示器
                const indicator = document.getElementById('voice-recording-indicator');
                if (indicator) {
                    indicator.style.display = 'none';
                }
                
                if (recognitionState === 'stopping') {
                    recognitionState = 'processing';
                    await processSunguoVoiceInput(sunguoTextareas);
                } else {
                    recognitionState = 'idle';
                    updateVoiceButtonState('idle');
                }
                
                // 重置边框颜色
                if (sunguoTextareas.rawPrompt) {
                    sunguoTextareas.rawPrompt.style.borderColor = '';
                }
            };
        }
        
        // 清理可能存在的旧状态
        if (recognitionState === 'starting') {
            console.log('🔄 清理可能存在的旧状态...');
            try {
                recognition.abort();
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (e) {
                console.log('abort 没有产生错误（这是预期的）');
            }
        }
        
        // 显示录音指示器
        const indicator = document.getElementById('voice-recording-indicator');
        if (indicator) {
            indicator.style.display = 'flex';
        }
        
        // 开始识别
        console.log('📢 调用 recognition.start()...');
        recognition.start();
        isRecording = true;
        recognitionState = 'recording';
        updateVoiceButtonState('recording');
        showNotification('🎤 请开始说话...', 'info');
        
    } catch (error) {
        console.error('❌ 启动语音识别失败:', error);
        isRecording = false;
        recognitionState = 'idle';
        updateVoiceButtonState('idle');
        
        const indicator = document.getElementById('voice-recording-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
        
        if (error.name === 'InvalidStateError') {
            showNotification('语音识别服务忙，请稍后再试', 'warning');
        } else {
            showNotification('启动语音识别失败: ' + error.message, 'error');
        }
    }
};

/**
 * 处理松果课堂语音输入（自动优化已由input事件触发）
 */
async function processSunguoVoiceInput(textareas) {
    console.log('🤖 松果课堂语音处理完成，原始内容:', voiceTranscript);
    
    if (!voiceTranscript || voiceTranscript.trim() === '') {
        showNotification('未识别到有效内容', 'warning');
        updateVoiceButtonState('idle');
        return;
    }
    
    // 确保原始输入框有内容
    if (textareas.rawPrompt && !textareas.rawPrompt.value.trim()) {
        textareas.rawPrompt.value = voiceTranscript;
        // 触发input事件来启动AI优化
        textareas.rawPrompt.dispatchEvent(new Event('input', { bubbles: true }));
    }
    
    showNotification('✨ 语音录入完成！AI正在优化中...', 'success');
    updateVoiceButtonState('idle');
    recognitionState = 'idle';
}
