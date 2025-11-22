/**
 * 评论功能模块 - 支持语音输入评论
 */

let currentArtworkId = null;
let commentRecognition = null;
let isCommentRecording = false;
let commentAudioBlob = null; // 存储录音音频

/**
 * 初始化评论区域
 */
function initComments(artworkId) {
    currentArtworkId = artworkId;
    
    // 加载评论列表
    loadComments(artworkId);
    
    // 绑定评论输入事件
    const commentInput = document.getElementById('commentInput');
    const submitBtn = document.getElementById('submitCommentBtn');
    const voiceBtn = document.getElementById('voiceCommentBtn');
    const charCount = document.getElementById('commentCharCount');
    
    if (commentInput) {
        commentInput.addEventListener('input', function() {
            const length = this.value.length;
            charCount.textContent = length;
            submitBtn.disabled = length === 0;
        });
        
        // 回车键发送（Shift+Enter换行）
        commentInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!submitBtn.disabled) {
                    submitComment();
                }
            }
        });
    }
    
    if (submitBtn) {
        submitBtn.addEventListener('click', submitComment);
    }
    
    if (voiceBtn) {
        voiceBtn.addEventListener('click', toggleCommentVoiceInput);
    }
}

/**
 * 加载评论列表
 */
async function loadComments(artworkId) {
    const commentsList = document.getElementById('commentsList');
    
    try {
        const response = await fetch(`/auth/artwork/${artworkId}/comments`);
        const data = await response.json();
        
        if (data.success) {
            displayComments(data.comments);
            updateCommentsCount(data.total);
        } else {
            showCommentsError('加载评论失败');
        }
    } catch (error) {
        console.error('加载评论失败:', error);
        showCommentsError('加载评论失败，请刷新重试');
    }
}

/**
 * 显示评论列表
 */
function displayComments(comments) {
    const commentsList = document.getElementById('commentsList');
    
    if (comments.length === 0) {
        commentsList.innerHTML = `
            <div class="comments-empty">
                <i class="fas fa-comment-slash"></i>
                <p>还没有评论，快来抢沙发吧！</p>
            </div>
        `;
        return;
    }
    
    commentsList.innerHTML = comments.map(comment => {
        // 调试：打印音频文件路径
        if (comment.audio_file) {
            console.log('评论音频文件:', comment.audio_file);
        }
        
        return `
        <div class="comment-item" data-comment-id="${comment.id}">
            <div class="comment-header">
                <div class="comment-user">
                    <img src="/static/avatars/${comment.user.avatar_url}" 
                         alt="${comment.user.nickname}" 
                         class="comment-avatar"
                         onerror="this.src='/static/image/default_avatar.png'">
                    <div class="comment-user-info">
                        <span class="comment-nickname">${escapeHtml(comment.user.nickname)}</span>
                        <span class="comment-age">${comment.user.age}岁</span>
                        ${comment.is_voice_comment ? '<span class="voice-badge"><i class="fas fa-microphone"></i> 语音</span>' : ''}
                    </div>
                    ${comment.audio_file ? `
                        <div class="comment-audio-inline">
                            <audio controls preload="metadata" 
                                   onerror="console.error('音频加载失败:', '${comment.audio_file}')"
                                   onloadedmetadata="console.log('音频加载成功:', '${comment.audio_file}')">
                                <source src="${comment.audio_file}" type="audio/mp4">
                                <source src="${comment.audio_file}" type="audio/webm;codecs=opus">
                                <source src="${comment.audio_file}" type="audio/webm">
                                <source src="${comment.audio_file}" type="audio/ogg">
                                您的浏览器不支持音频播放
                            </audio>
                        </div>
                    ` : `<div class="comment-content-inline">${escapeHtml(comment.content)}</div>`}
                </div>
                <div class="comment-meta">
                    <span class="comment-time">${formatCommentTime(comment.created_at)}</span>
                    ${getCommentActions(comment)}
                </div>
            </div>
            ${comment.audio_file ? `<div class="comment-text-content">${escapeHtml(comment.content)}</div>` : ''}
        </div>
    `;
    }).join('');
}

/**
 * 获取评论操作按钮
 */
function getCommentActions(comment) {
    // 检查是否可以删除（当前用户的评论或作品作者）
    const currentUserId = window.currentUserId; // 需要在模板中设置
    if (!currentUserId) return '';
    
    // 这里简化处理，实际应该检查是否是作品作者或评论作者
    return `
        <button class="comment-delete-btn" onclick="deleteComment(${comment.id})" title="删除评论">
            <i class="fas fa-trash-alt"></i>
        </button>
    `;
}

/**
 * 更新评论数量
 */
function updateCommentsCount(count) {
    const countElement = document.getElementById('commentsCount');
    if (countElement) {
        countElement.textContent = count;
    }
}

/**
 * 显示评论错误
 */
function showCommentsError(message) {
    const commentsList = document.getElementById('commentsList');
    commentsList.innerHTML = `
        <div class="comments-loading" style="color: #ef4444;">
            <i class="fas fa-exclamation-circle"></i> ${message}
        </div>
    `;
}

/**
 * 提交评论
 */
async function submitComment() {
    const commentInput = document.getElementById('commentInput');
    const content = commentInput.value.trim();
    
    if (!content) return;
    
    const submitBtn = document.getElementById('submitCommentBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发送中...';
    
    try {
        // 如果有语音录音，先上传音频
        let audioFilename = null;
        if (commentAudioBlob) {
            audioFilename = await uploadCommentAudio(commentAudioBlob);
        }
        
        const response = await fetch(`/auth/artwork/${currentArtworkId}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                is_voice_comment: !!commentAudioBlob,
                audio_file: audioFilename
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 清空输入框和音频
            commentInput.value = '';
            document.getElementById('commentCharCount').textContent = '0';
            commentAudioBlob = null;
            
            // 重新加载评论
            await loadComments(currentArtworkId);
            
            // 显示成功提示
            showToast('评论发表成功！', 'success');
        } else {
            showToast(data.message || '评论发表失败', 'error');
        }
    } catch (error) {
        console.error('提交评论失败:', error);
        showToast('网络错误，请重试', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 发表评论';
        isCommentRecording = false;
    }
}

/**
 * 上传评论音频
 */
async function uploadCommentAudio(audioBlob) {
    const formData = new FormData();
    
    // 根据blob类型确定文件扩展名
    let ext = 'webm';
    if (audioBlob.type.includes('mp4')) {
        ext = 'm4a';
    } else if (audioBlob.type.includes('ogg')) {
        ext = 'ogg';
    }
    
    formData.append('audio', audioBlob, `comment_${Date.now()}.${ext}`);
    
    try {
        const response = await fetch('/auth/upload-comment-audio', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('音频上传成功:', data.filename, '大小:', data.size, 'bytes');
            return data.filename;
        } else {
            console.error('音频上传失败:', data.message);
            return null;
        }
    } catch (error) {
        console.error('上传音频失败:', error);
        return null;
    }
}

/**
 * 删除评论
 */
async function deleteComment(commentId) {
    if (!confirm('确定要删除这条评论吗？')) return;
    
    try {
        const response = await fetch(`/auth/comments/${commentId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 重新加载评论
            await loadComments(currentArtworkId);
            showToast('评论已删除', 'success');
        } else {
            showToast(data.message || '删除失败', 'error');
        }
    } catch (error) {
        console.error('删除评论失败:', error);
        showToast('网络错误，请重试', 'error');
    }
}

/**
 * 切换语音输入
 */
let mediaRecorder = null;
let audioChunks = [];

function toggleCommentVoiceInput() {
    if (isCommentRecording) {
        stopCommentVoiceInput();
    } else {
        startCommentVoiceInput();
    }
}

/**
 * 开始语音输入
 */
async function startCommentVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        showToast('您的浏览器不支持语音识别', 'error');
        return;
    }
    
    // 请求麦克风权限并开始录音
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // 初始化音频录制，尝试多种格式
        audioChunks = [];
        
        // 检测支持的音频格式
        let mimeType = 'audio/webm';
        let fileExt = 'webm';
        
        if (MediaRecorder.isTypeSupported('audio/mp4')) {
            // Safari和iOS优先使用MP4
            mimeType = 'audio/mp4';
            fileExt = 'm4a';
        } else if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            mimeType = 'audio/webm;codecs=opus';
            fileExt = 'webm';
        } else if (MediaRecorder.isTypeSupported('audio/webm')) {
            mimeType = 'audio/webm';
            fileExt = 'webm';
        } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
            mimeType = 'audio/ogg;codecs=opus';
            fileExt = 'ogg';
        }
        
        console.log('使用音频格式:', mimeType, '扩展名:', fileExt);
        mediaRecorder = new MediaRecorder(stream, { mimeType: mimeType });
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
                console.log('录制数据块:', event.data.size, 'bytes');
            }
        };
        
        mediaRecorder.onstop = () => {
            // 创建音频Blob
            commentAudioBlob = new Blob(audioChunks, { type: mimeType });
            console.log('录音完成，总大小:', commentAudioBlob.size, 'bytes');
            
            // 停止所有音频轨道
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
        console.log('开始录音...');
        
    } catch (error) {
        console.error('无法访问麦克风:', error);
        showToast('无法访问麦克风，请检查权限设置', 'error');
        return;
    }
    
    // 初始化语音识别
    if (!commentRecognition) {
        commentRecognition = new SpeechRecognition();
        commentRecognition.lang = 'zh-CN';
        commentRecognition.continuous = true;
        commentRecognition.interimResults = true;
        
        commentRecognition.onresult = function(event) {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            
            const commentInput = document.getElementById('commentInput');
            if (commentInput) {
                commentInput.value = transcript;
                commentInput.dispatchEvent(new Event('input'));
            }
        };
        
        commentRecognition.onerror = function(event) {
            console.error('语音识别错误:', event.error);
            stopCommentVoiceInput();
            showToast('语音识别出错，请重试', 'error');
        };
        
        commentRecognition.onend = function() {
            if (isCommentRecording) {
                stopCommentVoiceInput();
            }
        };
    }
    
    try {
        commentRecognition.start();
        isCommentRecording = true;
        
        const voiceBtn = document.getElementById('voiceCommentBtn');
        voiceBtn.classList.add('recording');
        voiceBtn.innerHTML = '<i class="fas fa-stop-circle"></i> <span>停止录音</span>';
        
    } catch (error) {
        console.error('启动语音识别失败:', error);
        showToast('无法启动语音识别', 'error');
    }
}

/**
 * 停止语音输入
 */
function stopCommentVoiceInput() {
    if (commentRecognition) {
        commentRecognition.stop();
    }
    
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
    }
    
    isCommentRecording = false;
    
    const voiceBtn = document.getElementById('voiceCommentBtn');
    if (voiceBtn) {
        voiceBtn.classList.remove('recording');
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i> <span>语音输入</span>';
    }
}

/**
 * 格式化评论时间
 */
function formatCommentTime(timeStr) {
    const time = new Date(timeStr);
    const now = new Date();
    const diff = now - time;
    
    const minute = 60 * 1000;
    const hour = 60 * minute;
    const day = 24 * hour;
    
    if (diff < minute) {
        return '刚刚';
    } else if (diff < hour) {
        return Math.floor(diff / minute) + '分钟前';
    } else if (diff < day) {
        return Math.floor(diff / hour) + '小时前';
    } else if (diff < 7 * day) {
        return Math.floor(diff / day) + '天前';
    } else {
        return time.toLocaleDateString('zh-CN');
    }
}

/**
 * HTML转义
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 显示提示消息
 */
function showToast(message, type = 'info') {
    // 如果已有toast函数，使用现有的
    if (typeof showMessage === 'function') {
        showMessage(message, type);
        return;
    }
    
    // 简单的alert作为后备
    alert(message);
}
