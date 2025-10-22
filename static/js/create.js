// 创作页面相关功能
let currentStage = 1;
let generatedImageUrl = '';
let uploadedImageFile = null;

// 3D模型相关全局变量
let createModelViewer = null;

// 进度条相关变量
let progressInterval = null;
let currentProgress = 0;
let startTime = null;
let estimatedTotalTime = 150; // 预计150秒（2.5分钟）

// 3D模型控制面板相关变量
let originalMaterials = new Map(); // 存储原始材质
let currentRenderMode = 'solid'; // 当前渲染模式
let currentMaterialType = 'original'; // 当前材质类型
let backgroundVisible = true; // 背景可见性
let directionalLight = null; // 定向光源引用
let pointsObjects = []; // 存储创建的点云对象

// 填充提示词到输入框
function fillPrompt(promptText) {
    const textarea = document.getElementById('creation-prompt');
    if (textarea) {
        textarea.value = promptText;
        textarea.focus();
        
        // 添加一个轻微的动画效果
        textarea.style.transform = 'scale(1.02)';
        textarea.style.transition = 'transform 0.2s ease';
        
        setTimeout(() => {
            textarea.style.transform = 'scale(1)';
        }, 200);
    }
}

// 快速调整功能
function quickAdjust(adjustType) {
    const adjustmentTextarea = document.getElementById('adjustment-prompt');
    if (!adjustmentTextarea) return;
    
    let adjustPrompt = '';
    
    switch(adjustType) {
        case 'remove-background':
            adjustPrompt = '去除背景，让主体突出，背景变为透明或纯色';
            break;
        case 'bright-colors':
            adjustPrompt = '让颜色更加鲜艳明亮，增强色彩饱和度和对比度';
            break;
        case 'soft-colors':
            adjustPrompt = '使用柔和的色调，降低饱和度，创造温馨的感觉';
            break;
        case 'cartoon-style':
            adjustPrompt = '转换为卡通风格，线条更圆润，色彩更简洁';
            break;
        case 'add-sparkles':
            adjustPrompt = '添加闪闪发光的特效，增加星星点点的光芒效果';
            break;
        case 'change-background':
            adjustPrompt = '更换背景为彩虹、森林、蓝天白云或其他美丽的场景';
            break;
        default:
            adjustPrompt = '请描述你想要的调整效果';
    }
    
    // 如果已有内容，则追加；否则替换
    if (adjustmentTextarea.value.trim()) {
        adjustmentTextarea.value += '，' + adjustPrompt;
    } else {
        adjustmentTextarea.value = adjustPrompt;
    }
    
    // 聚焦到文本框
    adjustmentTextarea.focus();
    
    // 添加视觉反馈
    adjustmentTextarea.style.transform = 'scale(1.02)';
    adjustmentTextarea.style.transition = 'transform 0.2s ease';
    
    setTimeout(() => {
        adjustmentTextarea.style.transform = 'scale(1)';
    }, 200);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeCreatePage();
    initializeVersionsPanel();
});

// 初始化版本面板
function initializeVersionsPanel() {
    // 等待版本管理器加载完成
    setTimeout(() => {
        if (window.inlineVersionManager) {
            // 检查是否在生成阶段，如果是则显示版本面板
            const generationStage = document.getElementById('generation-stage');
            if (generationStage && generationStage.classList.contains('active')) {
                const versionsContainer = document.getElementById('versions-container');
                if (versionsContainer) {
                    // 隐藏占位符
                    const placeholder = versionsContainer.querySelector('.no-versions-placeholder');
                    if (placeholder) {
                        placeholder.style.display = 'none';
                    }
                    
                    // 注入版本管理器
                    window.inlineVersionManager.injectVersionPanelToContainer('versions-container', 2);
                }
            }
        }
    }, 500);
}

// 初始化创作页面
function initializeCreatePage() {
    // 绑定生成按钮事件
    const generateBtn = document.getElementById('generate-image');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateImage);
    }

    // 绑定3D生成按钮事件
    const generate3DBtn = document.getElementById('generate-3d');
    if (generate3DBtn) {
        generate3DBtn.addEventListener('click', generate3DModel);
    }

    // 绑定3D模型控制按钮事件
    const rotateBtn = document.getElementById('rotateModel');
    if (rotateBtn) {
        rotateBtn.addEventListener('click', toggleAutoRotation);
    }

    const resetViewBtn = document.getElementById('resetView');
    if (resetViewBtn) {
        resetViewBtn.addEventListener('click', resetCameraView);
    }

    const download3DBtn = document.getElementById('download3D');
    if (download3DBtn) {
        download3DBtn.addEventListener('click', download3DModel);
    }

    // 绑定3D模型控制面板事件
    initModelControlsPanel();

    // 设置初始阶段
    showStage(1);
}

// 显示特定阶段
function showStage(stage) {
    currentStage = stage;
    
    // 隐藏所有阶段
    const stages = document.querySelectorAll('.creation-stage');
    stages.forEach(s => {
        s.classList.remove('active');
        s.style.display = 'none';
    });
    
    // 显示指定阶段
    const targetStage = document.getElementById(`stage-${stage}`);
    if (targetStage) {
        targetStage.classList.add('active');
        targetStage.style.display = 'block';
    }
}

// 切换创作步骤
function nextStep() {
    if (currentStage < 4) {
        showStage(currentStage + 1);
    }
}

// 点击上传图片按钮
function triggerImageUpload() {
    document.getElementById('image-upload').click();
}

// 显示指定阶段
function showStage(stageNumber) {
    // 隐藏所有阶段
    const allStages = document.querySelectorAll('.creation-stage');
    allStages.forEach(stage => stage.classList.remove('active'));

    // 重置所有进度步骤
    const allSteps = document.querySelectorAll('.progress-step');
    allSteps.forEach(step => step.classList.remove('active', 'completed'));

    // 显示当前阶段
    const stageId = getStageId(stageNumber);
    const currentStageElement = document.getElementById(stageId);
    
    if (currentStageElement) {
        currentStageElement.classList.add('active');
        
        // 特别检查阶段3中的图片元素
        if (stageNumber === 3) {
            const finalImageEl = document.getElementById('final-image');
            if (finalImageEl) {
                // 强制设置图片URL（无论当前src是什么）
                if (generatedImageUrl) {
                    finalImageEl.src = generatedImageUrl;
                    finalImageEl.style.display = 'block';
                    finalImageEl.style.visibility = 'visible';
                    
                    // 强制触发重新加载
                    finalImageEl.onload = () => {
                        // 图片加载成功
                    };
                    finalImageEl.onerror = (error) => {
                        console.error('图片加载失败:', error);
                    };
                }
            }
        }
    }

    // 更新进度指示器
    for (let i = 1; i <= stageNumber; i++) {
        const step = document.getElementById(`step-${i}`);
        if (step) {
            if (i < stageNumber) {
                step.classList.add('completed');
            } else if (i === stageNumber) {
                step.classList.add('active');
            }
        }
    }

    currentStage = stageNumber;
    
    // 通知内联版本管理器阶段变化
    if (window.inlineVersionManager) {
        setTimeout(() => {
            // 根据阶段获取对应的阶段ID并注入版本面板
            const stageIds = {
                1: 'input-stage',
                2: 'generation-stage', 
                3: 'model-stage'
            };
            const stageId = stageIds[stageNumber];
            if (stageId) {
                // 特殊处理生成阶段，注入到右侧版本面板
                if (stageNumber === 2) {
                    // 隐藏占位符
                    const versionsContainer = document.getElementById('versions-container');
                    if (versionsContainer) {
                        const placeholder = versionsContainer.querySelector('.no-versions-placeholder');
                        if (placeholder) {
                            placeholder.style.display = 'none';
                        }
                    }
                    window.inlineVersionManager.injectVersionPanelToContainer('versions-container', stageNumber);
                } else {
                    window.inlineVersionManager.injectVersionPanelToStage(stageId, stageNumber);
                }
            }
        }, 100);
    }
}

// 获取阶段ID
function getStageId(stageNumber) {
    const stageIds = {
        1: 'input-stage',
        2: 'generation-stage',
        3: 'model-stage'
    };
    return stageIds[stageNumber];
}

// 触发图片上传
function triggerImageUpload() {
    document.getElementById('reference-image').click();
}

// 处理图片上传
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        uploadedImageFile = file;
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('uploaded-image').src = e.target.result;
            document.getElementById('uploaded-image-preview').style.display = 'block';
        };
        reader.readAsDataURL(file);
        showMessage('图片上传成功！', 'success');
    }
}

// 移除上传的图片
function removeUploadedImage() {
    uploadedImageFile = null;
    document.getElementById('uploaded-image-preview').style.display = 'none';
    document.getElementById('reference-image').value = '';
    showMessage('已移除参考图片', 'info');
}

// 生成图片
async function generateImage() {
    const prompt = document.getElementById('creation-prompt').value.trim();
    const style = document.getElementById('image-style').value;
    const colorPreference = document.getElementById('color-preference').value;

    if (!prompt && !uploadedImageFile) {
        showMessage('请输入创意描述或上传参考图片', 'error');
        return;
    }

    showLoadingOverlay('AI正在创作中...');

    try {
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('style', style);
        formData.append('color_preference', colorPreference);
        
        // 添加会话ID（支持内联版本管理器）
        if (window.inlineVersionManager && window.inlineVersionManager.currentSessionId) {
            formData.append('session_id', window.inlineVersionManager.currentSessionId);
        } else if (window.versionManager && window.versionManager.currentSessionId) {
            formData.append('session_id', window.versionManager.currentSessionId);
        }
        
        // 添加版本备注
        const versionNote = document.querySelector('input[name="version_note"]')?.value || `${style}风格`;
        formData.append('version_note', versionNote);
        
        if (uploadedImageFile) {
            formData.append('sketch', uploadedImageFile);
        }

        const response = await fetch('/generate-image', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            generatedImageUrl = result.image_url;
            // 记录原始图片路径（如果有的话）
            if (result.original_image_url) {
                originalImagePath = result.original_image_url;
            }
            
            // 更新图片显示元素
            const generatedImageEl = document.getElementById('generated-image');
            const currentImageEl = document.getElementById('current-image');
            const finalImageEl = document.getElementById('final-image');
            
            // 显示调试信息
            showMessage(`图片生成成功！URL: ${result.image_url}`, 'success');
            
            if (generatedImageEl) {
                generatedImageEl.src = result.image_url;
                generatedImageEl.style.display = 'block';
                generatedImageEl.onerror = () => console.error('generated-image 加载失败');
            } else {
                console.error('未找到generated-image元素');
                showMessage('未找到generated-image元素', 'error');
            }
            if (currentImageEl) {
                currentImageEl.src = result.image_url;
                currentImageEl.style.display = 'block';
            }
            if (finalImageEl) {
                finalImageEl.src = result.image_url;
                finalImageEl.style.display = 'block';
            }
            
            // 通知版本管理器刷新（支持内联版本管理器）
            if (window.inlineVersionManager) {
                window.inlineVersionManager.onGenerationComplete();
            } else if (window.versionManager) {
                window.versionManager.onGenerationComplete();
            }
            
            // 更新生成成功状态并显示保存按钮
            updateImageGenerationSuccess(result);
            
            hideLoadingOverlay();
            showMessage('图片生成成功！', 'success');
            // 进入生成结果展示阶段
            showStage(2);
        } else {
            hideLoadingOverlay();
            showMessage(`生成失败: ${result.error}`, 'error');
        }
    } catch (error) {
        hideLoadingOverlay();
        showMessage('网络错误，请重试', 'error');
        console.error('Error:', error);
    }
}

// 重新生成图片
function regenerateImage() {
    generateImage();
}

// 显示调整面板（已合并到生成阶段，不再需要切换）
function showAdjustPanel() {
    // 调整面板已经在生成阶段显示，只需聚焦到调整输入框
    const adjustmentInput = document.getElementById('adjustment-prompt');
    if (adjustmentInput) {
        adjustmentInput.focus();
    }
}

// 确认图片（进入3D模型生成）
function confirmImage() {
    // 确保final-image显示当前生成的图片
    const finalImageEl = document.getElementById('final-image');
    if (finalImageEl && generatedImageUrl) {
        finalImageEl.src = generatedImageUrl;
        finalImageEl.style.display = 'block';
    }
    
    // 显示final-actions（包含保存按钮）
    const finalActions = document.getElementById('final-actions');
    if (finalActions) {
        finalActions.style.display = 'flex';
    }
    
    showStage(3);
}

// 跳过调整（进入3D模型生成）
function skipAdjustment() {
    // 确保final-image显示当前生成的图片
    const finalImageEl = document.getElementById('final-image');
    if (finalImageEl && generatedImageUrl) {
        finalImageEl.src = generatedImageUrl;
        finalImageEl.style.display = 'block';
    }
    
    // 显示final-actions（包含保存按钮）
    const finalActions = document.getElementById('final-actions');
    if (finalActions) {
        finalActions.style.display = 'flex';
    }
    
    showStage(3);
}

// 应用调整
async function applyAdjustment() {
    const adjustmentPrompt = document.getElementById('adjustment-prompt').value.trim();
    
    if (!adjustmentPrompt) {
        showMessage('请输入调整提示', 'error');
        return;
    }

    if (!generatedImageUrl) {
        showMessage('没有找到要调整的图片', 'error');
        return;
    }

    console.log('开始调整图片:', { adjustmentPrompt, generatedImageUrl });
    showLoadingOverlay('正在调整图片...');

    try {
        const formData = new FormData();
        formData.append('current_image', generatedImageUrl);
        formData.append('adjust_prompt', adjustmentPrompt);
        
        // 添加会话ID（支持内联版本管理器）
        if (window.inlineVersionManager && window.inlineVersionManager.currentSessionId) {
            formData.append('session_id', window.inlineVersionManager.currentSessionId);
        } else if (window.versionManager && window.versionManager.currentSessionId) {
            formData.append('session_id', window.versionManager.currentSessionId);
        }
        
        // 添加版本备注
        const versionNote = `调整：${adjustmentPrompt}`;
        formData.append('version_note', versionNote);

        console.log('发送调整请求到服务器...');
        const response = await fetch('/adjust-image', {
            method: 'POST',
            body: formData
        });

        console.log('收到服务器响应:', response.status);
        const result = await response.json();
        console.log('调整结果:', result);

        if (result.success) {
            generatedImageUrl = result.image_url;
            // 更新图片显示元素
            const generatedImageEl = document.getElementById('generated-image');
            const currentImageEl = document.getElementById('current-image');
            const finalImageEl = document.getElementById('final-image');
            
            // 主要是更新生成阶段的图片
            if (generatedImageEl) generatedImageEl.src = result.image_url;
            if (currentImageEl) currentImageEl.src = result.image_url;
            if (finalImageEl) finalImageEl.src = result.image_url;
            
            // 通知版本管理器刷新（支持内联版本管理器）
            if (window.inlineVersionManager) {
                window.inlineVersionManager.onGenerationComplete();
            } else if (window.versionManager) {
                window.versionManager.onGenerationComplete();
            }
            
            hideLoadingOverlay();
            showMessage('图片调整成功！', 'success');
            
            // 清空调整输入
            document.getElementById('adjustment-prompt').value = '';
            
            // 可以继续调整或进入下一阶段
        } else {
            hideLoadingOverlay();
            showMessage(`调整失败: ${result.error}`, 'error');
        }
    } catch (error) {
        hideLoadingOverlay();
        showMessage('网络错误，请重试', 'error');
        console.error('Error:', error);
    }
}

// 生成3D模型
async function generate3DModel() {
    if (!generatedImageUrl) {
        showMessage('请先生成图片', 'error');
        return;
    }

    // 切换到第3阶段（3D模型生成阶段）
    showStage(3);
    
    // 确保final-image在开始3D生成时就显示正确的图片
    const finalImageEl = document.getElementById('final-image');
    if (finalImageEl && generatedImageUrl) {
        finalImageEl.src = generatedImageUrl;
        finalImageEl.style.display = 'block';
    }

    showLoadingOverlay('正在生成3D模型，预计需要2-3分钟...');
    showProgressBar();

    try {
        const formData = new FormData();
        formData.append('image_path', generatedImageUrl);
        
        // 添加会话ID（支持内联版本管理器）
        if (window.inlineVersionManager && window.inlineVersionManager.currentSessionId) {
            formData.append('session_id', window.inlineVersionManager.currentSessionId);
        } else if (window.versionManager && window.versionManager.currentSessionId) {
            formData.append('session_id', window.versionManager.currentSessionId);
        }
        
        // 添加版本备注
        const versionNote = `3D模型 ${new Date().toLocaleTimeString()}`;
        formData.append('version_note', versionNote);
        
        // 添加可选的prompt
        const modelPrompt = document.getElementById('model-prompt');
        if (modelPrompt && modelPrompt.value.trim()) {
            formData.append('prompt', modelPrompt.value.trim());
        }
        
        // 启动进度模拟
        startProgressSimulation();
        
        const response = await fetch('/generate-3d-model', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        // 停止进度模拟
        stopProgressSimulation();

        if (result.success) {
            // 完成进度条到100%
            updateProgress(100, '生成完成！');
            
            setTimeout(() => {
                hideLoadingOverlay();
                showMessage('3D模型生成成功！', 'success');
                
                // 确保final-image显示正确的图片
                const finalImageEl = document.getElementById('final-image');
                if (finalImageEl && generatedImageUrl) {
                    finalImageEl.src = generatedImageUrl;
                    finalImageEl.style.display = 'block';
                }
                
                // 显示3D模型相关区域
                const modelActionsEl = document.getElementById('model-actions');
                if (modelActionsEl) {
                    modelActionsEl.style.display = 'block';
                }
                
                // 显示final-actions（包含保存按钮）
                const finalActions = document.getElementById('final-actions');
                if (finalActions) {
                    finalActions.style.display = 'flex';
                }
                
                // 记录3D模型文件路径
                if (result.model_url) {
                    modelFilePath = result.model_url;
                }
                
                // 加载3D模型（如果有模型文件URL）
                if (result.model_url) {
                    load3DModel(result.model_url);
                }
                
                // 通知版本管理器刷新（支持内联版本管理器）
                if (window.inlineVersionManager) {
                    window.inlineVersionManager.onGenerationComplete();
                } else if (window.versionManager) {
                    window.versionManager.onGenerationComplete();
                }
            }, 500);
        } else {
            hideLoadingOverlay();
            showMessage(`3D模型生成失败: ${result.error}`, 'error');
        }
    } catch (error) {
        stopProgressSimulation();
        hideLoadingOverlay();
        showMessage('网络错误，请重试', 'error');
        console.error('Error:', error);
    }
}

// 加载3D模型（Three.js）
function load3DModel(modelUrl) {
    // 保存当前模型URL用于下载
    window.currentModelUrl = modelUrl;
    
    // 确保ModelViewer3D模块已加载
    if (typeof ModelViewer3D === 'undefined') {
        console.error('ModelViewer3D 模块未加载');
        showMessage('3D查看器模块加载失败', 'error');
        return;
    }
    
    // 清理之前的实例
    if (createModelViewer) {
        createModelViewer.dispose();
    }
    
    // 创建新的3D查看器实例
    createModelViewer = new ModelViewer3D('modelContainer', {
        backgroundColor: 0xf0f0f0,
        enableControls: true,
        enableAutoRotate: false,
        enableAnimation: true,
        onModelLoaded: (loadedModel) => {
            console.log('3D模型加载完成:', loadedModel);
            
            // 移除加载占位符
            const container = document.getElementById('modelContainer');
            const placeholder = container.querySelector('.model-placeholder');
            if (placeholder) {
                placeholder.remove();
            }
            
            // 显示模型控制按钮和控制面板
            const modelActions = document.getElementById('model-actions');
            if (modelActions) {
                modelActions.style.display = 'flex';
            }
            
            // 显示3D模型控制面板
            showModelControlsPanel();
            
            // 保存模型引用用于其他控制函数
            window.currentModel = loadedModel;
        },
        onLoadError: (error) => {
            console.error('3D模型加载失败:', error);
            showMessage('3D模型加载失败', 'error');
        },
        onLoadProgress: (progress) => {
            // 可以在这里显示加载进度
            if (progress.loaded && progress.total) {
                const percent = Math.round((progress.loaded / progress.total) * 100);
                console.log(`模型加载进度: ${percent}%`);
            }
        }
    });
    
    // 加载模型
    createModelViewer.loadModel(modelUrl);
}

// 下载图片
function downloadImage() {
    if (generatedImageUrl) {
        const link = document.createElement('a');
        link.href = generatedImageUrl;
        link.download = 'my-ai-creation.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showMessage('图片下载开始', 'success');
    }
}

// 开始新创作
function startNewCreation() {
    // 重置所有状态
    currentStage = 1;
    generatedImageUrl = '';
    uploadedImageFile = null;
    
    // 清空表单
    const creationPrompt = document.getElementById('creation-prompt');
    const adjustmentPrompt = document.getElementById('adjustment-prompt');
    const modelPrompt = document.getElementById('model-prompt');
    const referenceImage = document.getElementById('reference-image');
    
    if (creationPrompt) creationPrompt.value = '';
    if (adjustmentPrompt) adjustmentPrompt.value = '';
    if (modelPrompt) modelPrompt.value = '';
    if (referenceImage) referenceImage.value = '';
    
    // 隐藏预览和控制区域
    const uploadedImagePreview = document.getElementById('uploaded-image-preview');
    const modelActions = document.getElementById('model-actions');
    
    if (uploadedImagePreview) uploadedImagePreview.style.display = 'none';
    if (modelActions) modelActions.style.display = 'none';
    
    // 清空图片显示
    const finalImage = document.getElementById('final-image');
    if (finalImage) finalImage.src = '';
    
    // 重置3D模型容器
    const modelContainer = document.getElementById('modelContainer');
    if (modelContainer) {
        modelContainer.innerHTML = `
            <div class="model-placeholder">
                <i class="fas fa-cube"></i>
                <p>点击下方按钮生成3D模型</p>
            </div>
        `;
    }
    
    // 返回第一阶段
    showStage(1);
    
    showMessage('已开始新的创作', 'info');
}

// 分享创作
function shareCreation() {
    if (generatedImageUrl) {
        // 这里可以实现分享功能
        showMessage('分享功能开发中...', 'info');
    }
}

// 显示加载覆盖层
function showLoadingOverlay(text = '加载中...') {
    const overlay = document.getElementById('loading-overlay');
    const loadingText = overlay.querySelector('.loading-text');
    loadingText.textContent = text;
    overlay.style.display = 'flex';
}

// 隐藏加载覆盖层
function hideLoadingOverlay() {
    document.getElementById('loading-overlay').style.display = 'none';
    hideProgressBar();
    stopProgressSimulation();
}

// 显示消息提示
function showMessage(message, type = 'info') {
    const toast = document.getElementById('message-toast');
    toast.textContent = message;
    toast.className = `message-toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 切换自动旋转
function toggleAutoRotation() {
    if (!createModelViewer || !window.currentModel) {
        showMessage('请先生成3D模型', 'warning');
        return;
    }
    
    const isRotating = createModelViewer.toggleAutoRotate();
    const rotateBtn = document.getElementById('rotateModel');
    
    if (isRotating) {
        rotateBtn.innerHTML = '<i class="fas fa-pause"></i> 停止旋转';
        rotateBtn.classList.add('active');
        showMessage('开始自动旋转', 'info');
    } else {
        rotateBtn.innerHTML = '<i class="fas fa-sync-alt"></i> 自动旋转';
        rotateBtn.classList.remove('active');
        showMessage('停止自动旋转', 'info');
    }
}

// 重置相机视角
function resetCameraView() {
    if (!createModelViewer) {
        showMessage('请先生成3D模型', 'warning');
        return;
    }
    
    // 停止自动旋转
    createModelViewer.stopAutoRotate();
    const rotateBtn = document.getElementById('rotateModel');
    if (rotateBtn) {
        rotateBtn.innerHTML = '<i class="fas fa-sync-alt"></i> 自动旋转';
        rotateBtn.classList.remove('active');
    }
    
    // 重置视角
    createModelViewer.resetView();
    
    showMessage('视角已重置', 'success');
}

// 下载3D模型
function download3DModel() {
    if (!createModelViewer) {
        showMessage('请先生成3D模型', 'warning');
        return;
    }

    const modelUrl = window.currentModelUrl;
    if (modelUrl) {
        const link = document.createElement('a');
        link.href = modelUrl;
        link.download = modelUrl.split('/').pop() || 'model.glb';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showMessage('3D模型下载开始', 'success');
    } else {
        showMessage('无法获取模型文件', 'error');
    }
}

// 进度条相关函数
function showProgressBar() {
    const progressContainer = document.getElementById('progress-container');
    if (progressContainer) {
        progressContainer.style.display = 'block';
    }
}

function hideProgressBar() {
    const progressContainer = document.getElementById('progress-container');
    if (progressContainer) {
        progressContainer.style.display = 'none';
    }
}

function updateProgress(percentage, timeText = null) {
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const progressTime = document.getElementById('progress-time');
    
    if (progressFill) {
        progressFill.style.width = percentage + '%';
    }
    
    if (progressText) {
        progressText.textContent = Math.round(percentage) + '%';
    }
    
    if (progressTime && timeText) {
        progressTime.textContent = timeText;
    }
}

function startProgressSimulation() {
    currentProgress = 0;
    startTime = Date.now();
    
    // 根据13-15次查询估算，每次查询约10-12秒，总共150秒
    progressInterval = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000; // 秒
        
        // 使用非线性进度计算，前80%较快，后20%较慢
        let targetProgress;
        if (elapsed < 60) {
            // 前60秒达到50%
            targetProgress = (elapsed / 60) * 50;
        } else if (elapsed < 120) {
            // 60-120秒达到80%
            targetProgress = 50 + ((elapsed - 60) / 60) * 30;
        } else {
            // 120秒后缓慢增长到95%
            targetProgress = 80 + Math.min(15, ((elapsed - 120) / 30) * 15);
        }
        
        // 平滑过渡到目标进度
        currentProgress = Math.min(currentProgress + 0.5, targetProgress);
        
        // 计算预估剩余时间
        let remainingTime;
        if (currentProgress < 5) {
            remainingTime = estimatedTotalTime;
        } else {
            const rate = currentProgress / elapsed;
            remainingTime = Math.max(0, (100 - currentProgress) / rate);
        }
        
        const minutes = Math.floor(remainingTime / 60);
        const seconds = Math.floor(remainingTime % 60);
        let timeText;
        
        if (minutes > 0) {
            timeText = `预估剩余: ${minutes}分${seconds}秒`;
        } else {
            timeText = `预估剩余: ${seconds}秒`;
        }
        
        updateProgress(currentProgress, timeText);
        
        // 如果达到95%就停止自动增长，等待实际完成
        if (currentProgress >= 95) {
            updateProgress(95, '即将完成...');
            clearInterval(progressInterval);
            progressInterval = null;
        }
    }, 200); // 每200ms更新一次
}

function stopProgressSimulation() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

// 初始化3D模型控制面板
function initModelControlsPanel() {
    // 渲染模式控制
    document.getElementById('renderSolid')?.addEventListener('click', () => setRenderMode('solid'));
    document.getElementById('renderWireframe')?.addEventListener('click', () => setRenderMode('wireframe'));
    document.getElementById('renderPoints')?.addEventListener('click', () => setRenderMode('points'));
    
    // 材质控制
    document.getElementById('materialOriginal')?.addEventListener('click', () => setMaterialType('original'));
    document.getElementById('materialLambert')?.addEventListener('click', () => setMaterialType('lambert'));
    document.getElementById('materialPhong')?.addEventListener('click', () => setMaterialType('phong'));
    
    // 环境控制
    document.getElementById('toggleBackground')?.addEventListener('click', toggleBackground);
    document.getElementById('lightIntensity')?.addEventListener('input', (e) => setLightIntensity(e.target.value));
    
    // 模型操作
    document.getElementById('resetModel')?.addEventListener('click', resetModelTransform);
    document.getElementById('centerModel')?.addEventListener('click', centerModel);
}

// 显示控制面板
function showModelControlsPanel() {
    const leftPanel = document.getElementById('leftControlsPanel');
    const rightPanel = document.getElementById('rightControlsPanel');
    
    if (leftPanel && rightPanel) {
        leftPanel.style.display = 'flex';
        rightPanel.style.display = 'flex';
    }
    
    // 重置渲染控制状态
    resetRenderControls();
}

// 隐藏控制面板
function hideModelControlsPanel() {
    const leftPanel = document.getElementById('leftControlsPanel');
    const rightPanel = document.getElementById('rightControlsPanel');
    
    if (leftPanel && rightPanel) {
        leftPanel.style.display = 'none';
        rightPanel.style.display = 'none';
    }
}

// 为了兼容HTML中的onclick调用
function hideModelControls() {
    hideModelControlsPanel();
}

// 设置渲染模式
function setRenderMode(mode) {
    const model = window.currentModel;
    if (!model || !createModelViewer) {
        showMessage('请先加载3D模型', 'warning');
        return;
    }
    
    currentRenderMode = mode;
    
    // 更新按钮状态
    document.querySelectorAll('#renderSolid, #renderWireframe, #renderPoints').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`render${mode.charAt(0).toUpperCase() + mode.slice(1)}`)?.classList.add('active');
    
    // 首先清理之前的点云对象
    cleanupPointsObjects();

    // 重置所有mesh的可见性
    model.traverse((child) => {
        if (child.isMesh) {
            child.visible = true;
        }
    });
    
    // 应用渲染模式
    if (mode === 'points') {
        // 点云模式：创建点云对象并隐藏原mesh
        model.traverse((child) => {
            if (child.isMesh) {
                // 创建点材质
                const pointsMaterial = new THREE.PointsMaterial({
                    color: child.material.color || 0x888888,
                    size: 0.02,
                    transparent: true,
                    opacity: 0.8
                });
                
                // 创建点几何体
                const points = new THREE.Points(child.geometry, pointsMaterial);
                points.position.copy(child.position);
                points.rotation.copy(child.rotation);
                points.scale.copy(child.scale);
                
                // 添加到场景并记录
                if (createModelViewer.scene) {
                    createModelViewer.scene.add(points);
                    pointsObjects.push(points);
                }
                
                // 隐藏原mesh
                child.visible = false;
            }
        });
    } else {
        // 实体模式和线框模式：修改材质属性
        model.traverse((child) => {
            if (child.isMesh) {
                switch (mode) {
                    case 'solid':
                        child.material.wireframe = false;
                        child.material.transparent = false;
                        child.material.opacity = 1;
                        break;
                    case 'wireframe':
                        child.material.wireframe = true;
                        child.material.transparent = true;
                        child.material.opacity = 0.8;
                        break;
                }
            }
        });
    }
    
    showMessage(`渲染模式已切换为: ${mode === 'solid' ? '实体' : mode === 'wireframe' ? '线框' : '点云'}`, 'success');
}

// 清理点云对象
function cleanupPointsObjects() {
    pointsObjects.forEach(points => {
        if (points.parent) {
            points.parent.remove(points);
        } else if (createModelViewer && createModelViewer.scene) {
            createModelViewer.scene.remove(points);
        }
        // 清理几何体和材质
        if (points.geometry) points.geometry.dispose();
        if (points.material) points.material.dispose();
    });
    pointsObjects = [];
}

// 重置渲染控制状态
function resetRenderControls() {
    // 清理点云对象
    cleanupPointsObjects();
    
    // 重置控制变量
    currentRenderMode = 'solid';
    currentMaterialType = 'original';
    originalMaterials.clear();
    
    // 重置按钮状态
    document.querySelectorAll('#renderSolid, #renderWireframe, #renderPoints').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById('renderSolid')?.classList.add('active');
    
    document.querySelectorAll('#materialOriginal, #materialLambert, #materialPhong').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById('materialOriginal')?.classList.add('active');
}

// 设置材质类型
function setMaterialType(type) {
    const model = window.currentModel;
    if (!model) {
        showMessage('请先加载3D模型', 'warning');
        return;
    }
    
    currentMaterialType = type;
    
    // 更新按钮状态
    document.querySelectorAll('#materialOriginal, #materialLambert, #materialPhong').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`material${type.charAt(0).toUpperCase() + type.slice(1)}`)?.classList.add('active');
    
    // 应用材质
    model.traverse((child) => {
        if (child.isMesh) {
            // 如果是第一次，存储原始材质
            if (!originalMaterials.has(child.uuid)) {
                originalMaterials.set(child.uuid, child.material.clone());
            }
            
            switch (type) {
                case 'original':
                    const orig = originalMaterials.get(child.uuid);
                    if (orig) child.material = orig;
                    break;
                case 'lambert':
                    child.material = new THREE.MeshLambertMaterial({
                        color: child.material.color || 0x888888,
                        wireframe: currentRenderMode === 'wireframe'
                    });
                    break;
                case 'phong':
                    child.material = new THREE.MeshPhongMaterial({
                        color: child.material.color || 0x888888,
                        shininess: 50,
                        wireframe: currentRenderMode === 'wireframe'
                    });
                    break;
            }
        }
    });
    
    showMessage(`材质已切换为: ${type === 'original' ? '原始' : type === 'lambert' ? '朗伯' : '光泽'}`, 'success');
}

// 切换背景显示
function toggleBackground() {
    if (!createModelViewer) return;
    
    const backgroundVisible = createModelViewer.toggleBackground();
    
    const backgroundText = document.getElementById('backgroundText');
    if (backgroundText) {
        backgroundText.textContent = backgroundVisible ? '显示' : '隐藏';
    }
    
    showMessage(`背景已${backgroundVisible ? '显示' : '隐藏'}`, 'success');
}

// 设置光照强度
function setLightIntensity(intensity) {
    if (createModelViewer) {
        createModelViewer.setDirectionalLightIntensity(intensity);
    }
}

// 重置模型变换
function resetModelTransform() {
    if (!createModelViewer || !window.currentModel) {
        showMessage('请先加载3D模型', 'warning');
        return;
    }
    
    const model = window.currentModel;
    model.position.set(0, 0, 0);
    model.rotation.set(0, 0, 0);
    model.scale.set(1, 1, 1);
    
    showMessage('模型变换已重置', 'success');
}

// 居中显示模型
function centerModel() {
    const model = window.currentModel;
    if (!model || !createModelViewer) {
        showMessage('请先加载3D模型', 'warning');
        return;
    }

    const camera = createModelViewer.camera;
    const controls = createModelViewer.controls;

    // 计算模型包围盒
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());

    // 将模型移动到原点
    model.position.sub(center);

    // 调整相机位置以适应模型
    const maxDim = Math.max(size.x, size.y, size.z);
    const distance = maxDim * 2;
    if (camera) {
        camera.position.set(0, 0, distance);
        camera.lookAt(0, 0, 0);
    }

    if (controls) {
        controls.target.set(0, 0, 0);
        if (controls.update) controls.update();
    }

    showMessage('模型已居中显示', 'success');
}

// 保存作品相关功能
let originalImagePath = null;  // 存储原始图片路径
let generatedImagePath = null; // 存储生成图片路径
let modelFilePath = null;      // 存储3D模型文件路径

// 显示保存作品对话框
function showSaveArtworkDialog() {
    // 检查是否有必要的图片（至少要有生成的图片）
    if (!generatedImageUrl) {
        showMessage('请先完成图片生成才能保存作品', 'error');
        return;
    }
    
    // 设置预览图片
    if (originalImagePath) {
        document.getElementById('preview-original').src = originalImagePath;
    } else {
        // 如果没有原始图片，显示占位图或隐藏
        document.getElementById('preview-original').src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="150"%3E%3Crect width="100%25" height="100%25" fill="%23f0f0f0"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999"%3E文字生成%3C/text%3E%3C/svg%3E';
    }
    document.getElementById('preview-generated').src = generatedImageUrl;
    
    // 显示对话框
    document.getElementById('save-artwork-modal').style.display = 'flex';
}

// 关闭保存作品对话框
function closeSaveArtworkDialog() {
    document.getElementById('save-artwork-modal').style.display = 'none';
    
    // 清空表单
    document.getElementById('artwork-title').value = '';
    document.getElementById('artist-name').value = '';
    document.getElementById('artist-age').value = '10';
    document.getElementById('artwork-category').value = 'animals';
    document.getElementById('artwork-description').value = '';
}

// 保存作品到作品集
async function saveArtworkToGallery() {
    try {
        // 获取表单数据
        const title = document.getElementById('artwork-title').value.trim();
        const artistName = document.getElementById('artist-name').value.trim();
        const artistAge = document.getElementById('artist-age').value;
        const category = document.getElementById('artwork-category').value;
        const description = document.getElementById('artwork-description').value.trim();
        
        // 验证必填字段
        if (!title) {
            showMessage('请输入作品标题', 'error');
            return;
        }
        
        if (!artistName) {
            showMessage('请输入创作者姓名', 'error');
            return;
        }
        
        // 显示加载状态
        const saveBtn = document.querySelector('.modal-footer .primary-btn');
        const originalText = saveBtn.innerHTML;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 保存中...';
        saveBtn.disabled = true;
        
        // 准备保存数据，处理路径格式
        const saveData = {
            original_image_path: originalImagePath ? (originalImagePath.startsWith('/') ? originalImagePath.substring(1) : originalImagePath) : null,
            generated_image_path: generatedImageUrl.startsWith('/') ? generatedImageUrl.substring(1) : generatedImageUrl,
            model_path: modelFilePath,
            title: title,
            artist_name: artistName,
            artist_age: parseInt(artistAge),
            category: category,
            description: description
        };
        
        // 发送保存请求
        const response = await fetch('/save-artwork', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(saveData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('🎉 作品已成功保存到作品集！', 'success');
            closeSaveArtworkDialog();
            
            // 显示成功弹窗
            showSuccessModal(result.artwork_id);
        } else {
            showMessage(`保存失败: ${result.error}`, 'error');
        }
        
    } catch (error) {
        showMessage(`保存失败: ${error.message}`, 'error');
    } finally {
        // 恢复按钮状态
        const saveBtn = document.querySelector('.modal-footer .primary-btn');
        saveBtn.innerHTML = originalText;
        saveBtn.disabled = false;
    }
}

// 显示保存成功弹窗
function showSuccessModal(artworkId) {
    // 创建成功弹窗HTML
    const successModal = document.createElement('div');
    successModal.className = 'modal-overlay success-modal';
    successModal.innerHTML = `
        <div class="modal-content success-content">
            <div class="success-header">
                <div class="success-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h3>🎉 保存成功！</h3>
                <p>你的作品已成功保存到作品集</p>
            </div>
            <div class="success-actions">
                <button class="secondary-btn" onclick="closeSuccessModal()">继续创作</button>
                <button class="primary-btn" onclick="goToGallery()">查看作品集</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(successModal);
    
    // 3秒后自动关闭
    setTimeout(() => {
        if (document.body.contains(successModal)) {
            closeSuccessModal();
        }
    }, 5000);
}

// 关闭成功弹窗
function closeSuccessModal() {
    const successModal = document.querySelector('.success-modal');
    if (successModal) {
        successModal.remove();
    }
}

// 前往作品集
function goToGallery() {
    window.location.href = '/gallery';
}

// 更新图片生成成功处理，记录图片路径和显示保存按钮
function updateImageGenerationSuccess(result) {
    generatedImageUrl = result.image_url;
    generatedImagePath = result.image_url;
    
    // 显示final-actions（包含保存按钮）
    const finalActions = document.getElementById('final-actions');
    if (finalActions) {
        finalActions.style.display = 'flex';
    }
}