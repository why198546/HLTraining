// 创作页面相关功能
console.log('✅ create.js 脚本已加载');

let currentStage = 1;
let generatedImageUrl = '';
let uploadedImageFile = null;

// 多视角图片存储（用于3D模型生成）
let multiViewImages = null; // {front: url, back: url, left: url, right: url}
let selectedViewForEdit = null; // 当前选中要编辑的视角 ('front', 'back', 'left', 'right')

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
    console.log('✅ DOM已加载，开始初始化...');
    
    // 测试generateVideo函数是否存在
    if (typeof generateVideo === 'function') {
        console.log('✅ generateVideo 函数已定义');
    } else {
        console.error('❌ generateVideo 函数未定义！');
    }
    
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

    // 监听风格选择器变化，显示/隐藏3D模式选择器
    const styleSelect = document.getElementById('image-style');
    const mode3DGroup = document.getElementById('3d-mode-group');
    if (styleSelect && mode3DGroup) {
        styleSelect.addEventListener('change', function() {
            if (this.value === 'model_3d') {
                mode3DGroup.style.display = 'block';
            } else {
                mode3DGroup.style.display = 'none';
            }
        });
    }

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
                // 特殊处理生成阶段，注入到版本面板
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
            // 显示快捷操作按钮
            document.getElementById('reference-quick-actions').style.display = 'block';
        };
        reader.readAsDataURL(file);
        showMessage('图片上传成功！可以直接生成视频或3D模型', 'success');
    }
}

// 移除上传的图片
function removeUploadedImage() {
    uploadedImageFile = null;
    document.getElementById('uploaded-image-preview').style.display = 'none';
    document.getElementById('reference-image').value = '';
    // 隐藏快捷操作按钮
    document.getElementById('reference-quick-actions').style.display = 'none';
    showMessage('已移除参考图片', 'info');
}

// 从参考图直接生成视频
async function generateVideoFromReference() {
    if (!uploadedImageFile) {
        showMessage('请先上传参考图片', 'error');
        return;
    }
    
    showLoadingOverlay('正在准备视频生成...');
    
    try {
        // 先上传参考图到服务器
        const formData = new FormData();
        formData.append('reference_image', uploadedImageFile);
        
        const response = await fetch('/upload-reference-image', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || '上传失败');
        }
        
        hideLoadingOverlay();
        
        // 构建视频生成页面的URL参数
        const params = new URLSearchParams({
            image_url: result.image_url,
            from_reference: 'true'
        });
        
        // 跳转到视频生成页面
        window.location.href = `/video?${params.toString()}`;
        
    } catch (error) {
        hideLoadingOverlay();
        showMessage(`上传失败：${error.message}`, 'error');
        console.error('上传参考图失败:', error);
    }
}

// 从参考图直接生成3D模型
async function generate3DFromReference() {
    if (!uploadedImageFile) {
        showMessage('请先上传参考图片', 'error');
        return;
    }
    
    showLoadingOverlay('正在生成3D模型...');
    
    try {
        // 先上传图片
        const uploadFormData = new FormData();
        uploadFormData.append('reference_image', uploadedImageFile);
        
        const uploadResponse = await fetch('/upload-reference-image', {
            method: 'POST',
            body: uploadFormData
        });
        
        const uploadResult = await uploadResponse.json();
        
        if (!uploadResult.success || !uploadResult.image_url) {
            throw new Error('图片上传失败');
        }
        
        // 转换URL为路径格式（去掉域名部分，只保留相对路径）
        const imageUrl = uploadResult.image_url;
        const imagePath = imageUrl.includes('creation_sessions') 
            ? imageUrl.substring(imageUrl.indexOf('creation_sessions'))
            : imageUrl;
        
        // 使用上传后的图片路径生成3D模型
        const formData = new FormData();
        formData.append('image_path', imagePath);
        
        // 添加3D模型提示词（如果有）
        const prompt = document.getElementById('creation-prompt').value.trim();
        if (prompt) {
            formData.append('prompt', prompt);
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
                toast.success('3D模型生成成功！');
                
                // 设置生成的图片URL（使用上传后的路径）
                generatedImageUrl = uploadResult.image_url;
                
                // 显示第三阶段（3D模型预览）
                const finalImageEl = document.getElementById('final-image');
                if (finalImageEl) {
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
                
                // 加载3D模型
                if (result.model_url) {
                    load3DModel(result.model_url);
                }
                
                // 切换到第三阶段
                showStage(3);
                
            }, 500);
        } else {
            throw new Error(result.error || '生成失败');
        }
    } catch (error) {
        stopProgressSimulation();
        hideLoadingOverlay();
        toast.error(`3D模型生成失败：${error.message}`);
        console.error('生成3D模型失败:', error);
    }
}

// 全局变量存储生成的所有图片
let generatedImagesArray = [];

// 生成图片
async function generateImage() {
    console.log('🚀 generateImage 函数被调用');
    const prompt = document.getElementById('creation-prompt').value.trim();
    const style = document.getElementById('image-style').value;
    const colorPreference = document.getElementById('color-preference').value;
    const expertMode = document.getElementById('expert-mode').checked;
    const aspectRatio = document.getElementById('aspect-ratio').value;
    const mode3D = document.getElementById('3d-mode')?.value; // 获取3D模式
    
    console.log(`📝 参数: prompt="${prompt}", style="${style}", file=${uploadedImageFile ? 'yes' : 'no'}, originalPath=${originalImagePath}`);

    // 允许三种情况：1)有prompt 2)有uploadedImageFile 3)有originalImagePath（生成更多）
    if (!prompt && !uploadedImageFile && !originalImagePath) {
        console.log('❌ 验证失败：缺少必要输入');
        showMessage('请输入创意描述或上传参考图片', 'error');
        return;
    }

    // 检查是否是多视角模式
    if (style === 'model_3d' && mode3D === 'multi') {
        // 调用多视角生成
        await generateMultiViewImages(prompt, colorPreference, aspectRatio);
        return;
    }

    // 单图模式（包括普通风格和3D单图模式）
    console.log('📤 准备发送请求到 /api/generate-image');
    showLoadingOverlay('AI正在创作中...');

    try {
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('style', style);
        formData.append('color_preference', colorPreference);
        formData.append('expert_mode', expertMode);
        formData.append('aspect_ratio', aspectRatio);
        // 不添加num_images，使用默认值1，松果课堂会传入4
        
        // 添加会话ID（支持内联版本管理器）
        if (window.inlineVersionManager && window.inlineVersionManager.currentSessionId) {
            formData.append('session_id', window.inlineVersionManager.currentSessionId);
        } else if (window.versionManager && window.versionManager.currentSessionId) {
            formData.append('session_id', window.versionManager.currentSessionId);
        }
        
        // 添加版本备注
        const versionNote = document.querySelector('input[name="version_note"]')?.value || `${style}风格`;
        formData.append('version_note', versionNote);
        
        // 优先使用新上传的文件，否则使用原始图片路径（生成更多功能）
        if (uploadedImageFile) {
            formData.append('sketch', uploadedImageFile);
        } else if (originalImagePath) {
            // 传递原始图片路径，让后端重用
            formData.append('original_image_path', originalImagePath);
        }

        console.log('🌐 发送 fetch 请求...');
        const response = await fetch('/api/generate-image', {
            method: 'POST',
            body: formData
        });
        
        console.log(`📥 收到响应: status=${response.status}`);
        const result = await response.json();
        console.log('📦 响应数据:', result);

        if (result.success) {
            // 主创作页面只使用单张图片
            generatedImagesArray = [result.image_url];
            generatedImageUrl = result.image_url;
            
            console.log(`✅ 图片生成成功`);
            
            // 记录原始图片路径（如果有的话）
            if (result.original_image_url) {
                originalImagePath = result.original_image_url;
            } else if (uploadedImageFile && !originalImagePath) {
                originalImagePath = result.image_url;
            }
            
            // 更新主图片显示
            const generatedImageEl = document.getElementById('generated-image');
            const currentImageEl = document.getElementById('current-image');
            const finalImageEl = document.getElementById('final-image');
            
            showMessage('图片生成成功！', 'success');
            
            if (generatedImageEl) {
                generatedImageEl.src = result.image_url;
                generatedImageEl.style.display = 'block';
                generatedImageEl.onerror = () => console.error('generated-image 加载失败');
            } else {
                console.error('未找到generated-image元素');
            }
            if (currentImageEl) {
                currentImageEl.src = result.image_url;
                currentImageEl.style.display = 'block';
            }
            if (finalImageEl) {
                finalImageEl.src = result.image_url;
                finalImageEl.style.display = 'block';
            }
            
            // 主创作页面不显示缩略图
            
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

// 生成多视角图片
async function generateMultiViewImages(prompt, colorPreference, aspectRatio) {
    showLoadingOverlay('正在生成多视角图片（正、反、左、右）...');

    try {
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('color_preference', colorPreference);
        formData.append('aspect_ratio', aspectRatio);
        
        // 添加会话ID
        if (window.inlineVersionManager && window.inlineVersionManager.currentSessionId) {
            formData.append('session_id', window.inlineVersionManager.currentSessionId);
        } else if (window.versionManager && window.versionManager.currentSessionId) {
            formData.append('session_id', window.versionManager.currentSessionId);
        }

        const response = await fetch('/generate-multi-view', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success && result.images) {
            // 显示多视角结果
            displayMultiViewResults(result.images);
            
            hideLoadingOverlay();
            showMessage('多视角图片生成成功！', 'success');
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

// 显示多视角结果
function displayMultiViewResults(images) {
    const generatedImageEl = document.getElementById('generated-image');
    if (!generatedImageEl) return;
    
    // 存储多视角图片用于3D模型生成
    multiViewImages = {
        front: images.front,
        back: images.back,
        left: images.left,
        right: images.right
    };
    console.log('✅ 多视角图片已存储:', multiViewImages);
    
    // 创建多视角网格显示 - 添加可点击功能
    const multiViewHTML = `
        <div class="multi-view-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div class="view-item" data-view="front" onclick="selectViewForEdit('front')" style="cursor: pointer; position: relative;">
                <img src="${images.front}" alt="正面视角" style="width: 100%; border-radius: 8px; border: 3px solid transparent; transition: border-color 0.3s;">
                <p style="text-align: center; margin-top: 0.5rem; font-weight: bold;">正面</p>
            </div>
            <div class="view-item" data-view="back" onclick="selectViewForEdit('back')" style="cursor: pointer; position: relative;">
                <img src="${images.back}" alt="背面视角" style="width: 100%; border-radius: 8px; border: 3px solid transparent; transition: border-color 0.3s;">
                <p style="text-align: center; margin-top: 0.5rem; font-weight: bold;">背面</p>
            </div>
            <div class="view-item" data-view="left" onclick="selectViewForEdit('left')" style="cursor: pointer; position: relative;">
                <img src="${images.left}" alt="左侧视角" style="width: 100%; border-radius: 8px; border: 3px solid transparent; transition: border-color 0.3s;">
                <p style="text-align: center; margin-top: 0.5rem; font-weight: bold;">左侧</p>
            </div>
            <div class="view-item" data-view="right" onclick="selectViewForEdit('right')" style="cursor: pointer; position: relative;">
                <img src="${images.right}" alt="右侧视角" style="width: 100%; border-radius: 8px; border: 3px solid transparent; transition: border-color 0.3s;">
                <p style="text-align: center; margin-top: 0.5rem; font-weight: bold;">右侧</p>
            </div>
        </div>
        <div style="margin-top: 1rem; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
            <p style="margin: 0; color: #666; font-size: 0.9em;">
                <i class="fas fa-info-circle"></i> 提示：点击任意视角图片可选中并单独调整
            </p>
        </div>
    `;
    
    // 替换单图显示为多视角网格
    generatedImageEl.outerHTML = `<div id="generated-image">${multiViewHTML}</div>`;
    
    // 保存第一张图片URL用于后续操作
    generatedImageUrl = images.front;
}

// 重新生成图片
function regenerateImage() {
    generateImage();
}

// 生成更多图片
function generateMoreImages() {
    // 触发多张图片生成
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
    // 检查是否有多视角图片
    if (multiViewImages) {
        // 多视角模式：显示所有4张图片
        const finalImageSection = document.querySelector('.final-image-section .image-preview-container');
        if (finalImageSection) {
            finalImageSection.innerHTML = `
                <div class="multi-view-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                    <div class="view-item">
                        <img src="${multiViewImages.front}" alt="正面视角" style="width: 100%; border-radius: 8px;">
                        <p style="text-align: center; margin-top: 0.25rem; font-size: 0.85em; font-weight: bold;">正面</p>
                    </div>
                    <div class="view-item">
                        <img src="${multiViewImages.back}" alt="背面视角" style="width: 100%; border-radius: 8px;">
                        <p style="text-align: center; margin-top: 0.25rem; font-size: 0.85em; font-weight: bold;">背面</p>
                    </div>
                    <div class="view-item">
                        <img src="${multiViewImages.left}" alt="左侧视角" style="width: 100%; border-radius: 8px;">
                        <p style="text-align: center; margin-top: 0.25rem; font-size: 0.85em; font-weight: bold;">左侧</p>
                    </div>
                    <div class="view-item">
                        <img src="${multiViewImages.right}" alt="右侧视角" style="width: 100%; border-radius: 8px;">
                        <p style="text-align: center; margin-top: 0.25rem; font-size: 0.85em; font-weight: bold;">右侧</p>
                    </div>
                </div>
            `;
        }
    } else {
        // 单图模式：确保final-image显示当前生成的图片
        const finalImageEl = document.getElementById('final-image');
        if (finalImageEl && generatedImageUrl) {
            finalImageEl.src = generatedImageUrl;
            finalImageEl.style.display = 'block';
        }
    }
    
    // 显示final-actions（包含保存按钮）
    const finalActions = document.getElementById('final-actions');
    if (finalActions) {
        finalActions.style.display = 'flex';
    }
    
    showStage(3);
}

// 生成视频
function generateVideo() {
    if (!generatedImageUrl) {
        showMessage('请先生成图片', 'error');
        return;
    }
    
    // 获取会话ID
    const sessionId = window.inlineVersionManager?.currentSessionId || 
                     window.versionManager?.currentSessionId || 
                     '';
    
    if (!sessionId) {
        showMessage('会话ID缺失，请刷新页面重试', 'error');
        return;
    }

    // 构建视频生成页面的URL参数
    const params = new URLSearchParams({
        session_id: sessionId,
        image_url: generatedImageUrl
        // 不传递图片生成的prompt，让用户在视频页面重新输入视频相关的动作描述
    });

    // 跳转到视频生成页面
    window.location.href = `/video?${params.toString()}`;
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

// 选择要编辑的视角
function selectViewForEdit(viewName) {
    if (!multiViewImages) {
        showMessage('没有多视角图片', 'error');
        return;
    }
    
    selectedViewForEdit = viewName;
    console.log(`✅ 选中视角: ${viewName}`);
    
    // 更新视觉反馈 - 高亮选中的视角
    const viewItems = document.querySelectorAll('.view-item');
    viewItems.forEach(item => {
        const img = item.querySelector('img');
        if (item.dataset.view === viewName) {
            // 选中状态：蓝色边框
            img.style.borderColor = '#4CAF50';
            img.style.boxShadow = '0 0 10px rgba(76, 175, 80, 0.5)';
        } else {
            // 未选中状态：透明边框
            img.style.borderColor = 'transparent';
            img.style.boxShadow = 'none';
        }
    });
    
    // 更新提示信息
    const viewNameMap = {
        'front': '正面',
        'back': '背面',
        'left': '左侧',
        'right': '右侧'
    };
    showMessage(`已选中${viewNameMap[viewName]}视角，可在下方输入调整提示`, 'info');
}

// 应用调整
// 应用调整
async function applyAdjustment() {
    const adjustmentPrompt = document.getElementById('adjustment-prompt').value.trim();
    
    if (!adjustmentPrompt) {
        showMessage('请输入调整提示', 'error');
        return;
    }

    // 检查是否是多视角模式且有选中的视角
    if (multiViewImages && selectedViewForEdit) {
        // 多视角单独编辑模式
        await adjustSingleView(selectedViewForEdit, adjustmentPrompt);
        return;
    }

    // 单图模式
    if (!generatedImageUrl) {
        showMessage('没有找到要调整的图片', 'error');
        console.error('❌ generatedImageUrl 为空');
        return;
    }

    showLoadingOverlay('正在调整图片...');

    try {
        const expertMode = document.getElementById('expert-mode').checked;
        
        const formData = new FormData();
        formData.append('current_image', generatedImageUrl);
        formData.append('adjust_prompt', adjustmentPrompt);
        formData.append('expert_mode', expertMode);
        
        // 添加会话ID（支持内联版本管理器）
        if (window.inlineVersionManager && window.inlineVersionManager.currentSessionId) {
            formData.append('session_id', window.inlineVersionManager.currentSessionId);
        } else if (window.versionManager && window.versionManager.currentSessionId) {
            formData.append('session_id', window.versionManager.currentSessionId);
        }
        
        // 添加版本备注
        const versionNote = `调整：${adjustmentPrompt}`;
        formData.append('version_note', versionNote);

        const response = await fetch('/adjust-image', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

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

// 调整单个视角
async function adjustSingleView(viewName, adjustmentPrompt) {
    if (!multiViewImages || !multiViewImages[viewName]) {
        showMessage('视角图片不存在', 'error');
        return;
    }

    const viewNameMap = {
        'front': '正面',
        'back': '背面',
        'left': '左侧',
        'right': '右侧'
    };

    showLoadingOverlay(`正在调整${viewNameMap[viewName]}视角...`);

    try {
        const expertMode = document.getElementById('expert-mode').checked;
        
        const formData = new FormData();
        formData.append('current_image', multiViewImages[viewName]);
        formData.append('adjust_prompt', adjustmentPrompt);
        formData.append('expert_mode', expertMode);
        
        // 添加会话ID
        if (window.inlineVersionManager && window.inlineVersionManager.currentSessionId) {
            formData.append('session_id', window.inlineVersionManager.currentSessionId);
        } else if (window.versionManager && window.versionManager.currentSessionId) {
            formData.append('session_id', window.versionManager.currentSessionId);
        }
        
        // 添加版本备注
        const versionNote = `调整${viewNameMap[viewName]}：${adjustmentPrompt}`;
        formData.append('version_note', versionNote);

        const response = await fetch('/adjust-image', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            // 更新multiViewImages中的对应视角
            multiViewImages[viewName] = result.image_url;
            
            // 更新显示
            const viewItem = document.querySelector(`.view-item[data-view="${viewName}"]`);
            if (viewItem) {
                const img = viewItem.querySelector('img');
                if (img) {
                    img.src = result.image_url;
                }
            }
            
            // 通知版本管理器刷新
            if (window.inlineVersionManager) {
                window.inlineVersionManager.onGenerationComplete();
            } else if (window.versionManager) {
                window.versionManager.onGenerationComplete();
            }
            
            hideLoadingOverlay();
            showMessage(`${viewNameMap[viewName]}视角调整成功！`, 'success');
            
            // 清空调整输入
            document.getElementById('adjustment-prompt').value = '';
            
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
    
    // 检查是否有多视角图片并显示
    if (multiViewImages) {
        // 多视角模式：显示所有4张图片
        const finalImageSection = document.querySelector('.final-image-section .image-preview-container');
        if (finalImageSection) {
            finalImageSection.innerHTML = `
                <div class="multi-view-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                    <div class="view-item">
                        <img src="${multiViewImages.front}" alt="正面视角" style="width: 100%; border-radius: 8px;">
                        <p style="text-align: center; margin-top: 0.25rem; font-size: 0.85em; font-weight: bold;">正面</p>
                    </div>
                    <div class="view-item">
                        <img src="${multiViewImages.back}" alt="背面视角" style="width: 100%; border-radius: 8px;">
                        <p style="text-align: center; margin-top: 0.25rem; font-size: 0.85em; font-weight: bold;">背面</p>
                    </div>
                    <div class="view-item">
                        <img src="${multiViewImages.left}" alt="左侧视角" style="width: 100%; border-radius: 8px;">
                        <p style="text-align: center; margin-top: 0.25rem; font-size: 0.85em; font-weight: bold;">左侧</p>
                    </div>
                    <div class="view-item">
                        <img src="${multiViewImages.right}" alt="右侧视角" style="width: 100%; border-radius: 8px;">
                        <p style="text-align: center; margin-top: 0.25rem; font-size: 0.85em; font-weight: bold;">右侧</p>
                    </div>
                </div>
            `;
        }
    } else {
        // 单图模式：确保final-image显示正确的图片
        const finalImageEl = document.getElementById('final-image');
        if (finalImageEl && generatedImageUrl) {
            finalImageEl.src = generatedImageUrl;
            finalImageEl.style.display = 'block';
        }
    }

    showLoadingOverlay('正在生成3D模型，预计需要2-3分钟...');
    showProgressBar();

    try {
        const formData = new FormData();
        
        // 检查是否有多视角图片
        if (multiViewImages) {
            console.log('🎨 使用多视角模式生成3D模型');
            // 传递所有4个视角的图片
            formData.append('multi_view', 'true');
            formData.append('front_image', multiViewImages.front);
            formData.append('back_image', multiViewImages.back);
            formData.append('left_image', multiViewImages.left);
            formData.append('right_image', multiViewImages.right);
        } else {
            console.log('🎨 使用单图模式生成3D模型');
            // 单图模式
            formData.append('image_path', generatedImageUrl);
        }
        
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
    document.getElementById('fullscreenBtn')?.addEventListener('click', toggleFullscreen);
    document.getElementById('autoRotateBtn')?.addEventListener('click', toggleModelAutoRotate);
    document.getElementById('resetModel')?.addEventListener('click', resetModelTransform);
    document.getElementById('centerModel')?.addEventListener('click', centerModel);
}

// 切换全屏
function toggleFullscreen() {
    const modelContainer = document.getElementById('modelContainer');
    if (!modelContainer) {
        showMessage('模型容器未找到', 'error');
        return;
    }
    
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    const icon = fullscreenBtn.querySelector('i');
    
    if (!document.fullscreenElement) {
        // 进入全屏
        if (modelContainer.requestFullscreen) {
            modelContainer.requestFullscreen();
        } else if (modelContainer.webkitRequestFullscreen) {
            modelContainer.webkitRequestFullscreen();
        } else if (modelContainer.msRequestFullscreen) {
            modelContainer.msRequestFullscreen();
        }
        
        // 更新按钮图标
        icon.classList.remove('fa-expand');
        icon.classList.add('fa-compress');
        fullscreenBtn.title = '退出全屏';
        
        // 调整模型查看器尺寸
        if (createModelViewer) {
            setTimeout(() => {
                createModelViewer.onWindowResize();
            }, 100);
        }
    } else {
        // 退出全屏
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
        
        // 更新按钮图标
        icon.classList.remove('fa-compress');
        icon.classList.add('fa-expand');
        fullscreenBtn.title = '全屏显示';
        
        // 调整模型查看器尺寸
        if (createModelViewer) {
            setTimeout(() => {
                createModelViewer.onWindowResize();
            }, 100);
        }
    }
}

// 监听全屏状态变化
document.addEventListener('fullscreenchange', handleFullscreenChange);
document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
document.addEventListener('mozfullscreenchange', handleFullscreenChange);
document.addEventListener('MSFullscreenChange', handleFullscreenChange);

function handleFullscreenChange() {
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    if (!fullscreenBtn) return;
    
    const icon = fullscreenBtn.querySelector('i');
    
    if (!document.fullscreenElement) {
        // 已退出全屏
        icon.classList.remove('fa-compress');
        icon.classList.add('fa-expand');
        fullscreenBtn.title = '全屏显示';
        
        // 调整模型查看器尺寸
        if (createModelViewer) {
            setTimeout(() => {
                createModelViewer.onWindowResize();
            }, 100);
        }
    }
}

// 切换自动旋转
function toggleModelAutoRotate() {
    if (!createModelViewer) {
        showMessage('请先加载3D模型', 'error');
        return;
    }
    
    createModelViewer.toggleAutoRotate();
    const btn = document.getElementById('autoRotateBtn');
    if (btn) {
        btn.classList.toggle('active');
    }
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
async function showSaveArtworkDialog() {
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
    
    // 重置表单为加载状态
    const titleInput = document.getElementById('artwork-title');
    const categorySelect = document.getElementById('artwork-category');
    const descriptionTextarea = document.getElementById('artwork-description');
    
    titleInput.value = '';
    titleInput.placeholder = 'AI正在生成标题...';
    titleInput.readOnly = true;
    
    categorySelect.value = '';
    categorySelect.disabled = true;
    
    descriptionTextarea.value = '';
    descriptionTextarea.placeholder = 'AI正在创作小故事...';
    descriptionTextarea.readOnly = true;
    
    // 显示加载图标
    document.getElementById('title-loading').classList.add('active');
    document.getElementById('category-loading').classList.add('active');
    document.getElementById('description-loading').classList.add('active');
    
    // 调用AI生成作品信息
    try {
        const prompt = document.getElementById('creation-prompt').value.trim();
        
        const response = await fetch('/api/generate-artwork-info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt: prompt })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 填充AI生成的信息
            titleInput.value = result.title;
            titleInput.placeholder = '给你的作品起个好听的名字';
            titleInput.readOnly = false;
            
            categorySelect.value = result.category;
            categorySelect.disabled = false;
            
            descriptionTextarea.value = result.description;
            descriptionTextarea.placeholder = '介绍一下你的创作想法和故事...';
            descriptionTextarea.readOnly = false;
            
            console.log('✅ AI生成作品信息成功:', result);
        } else {
            throw new Error(result.error || '生成失败');
        }
    } catch (error) {
        console.error('❌ AI生成作品信息失败:', error);
        // 失败时允许用户手动输入
        titleInput.placeholder = '请输入作品标题';
        titleInput.readOnly = false;
        
        categorySelect.value = 'other';
        categorySelect.disabled = false;
        
        descriptionTextarea.placeholder = '请输入作品介绍...';
        descriptionTextarea.readOnly = false;
        
        showMessage('AI生成失败，请手动填写', 'warning');
    } finally {
        // 隐藏加载图标
        document.getElementById('title-loading').classList.remove('active');
        document.getElementById('category-loading').classList.remove('active');
        document.getElementById('description-loading').classList.remove('active');
    }
}

// 关闭保存作品对话框
function closeSaveArtworkDialog() {
    document.getElementById('save-artwork-modal').style.display = 'none';
    
    // 清空表单
    document.getElementById('artwork-title').value = '';
    document.getElementById('artwork-category').value = 'animals';
    document.getElementById('artwork-description').value = '';
}

// 保存作品到作品集
async function saveArtworkToGallery() {
    // 保存按钮的原始文本（在外部定义，避免作用域问题）
    let originalText = '<i class="fas fa-heart"></i> 保存到作品集';
    
    try {
        // 获取表单数据
        const title = document.getElementById('artwork-title').value.trim();
        const category = document.getElementById('artwork-category').value;
        const description = document.getElementById('artwork-description').value.trim();
        
        // 验证必填字段
        if (!title) {
            showMessage('请输入作品标题', 'error');
            return;
        }
        
        // 显示加载状态
        const saveBtn = document.querySelector('.modal-footer .primary-btn');
        if (saveBtn) {
            originalText = saveBtn.innerHTML; // 保存实际的原始文本
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 保存中...';
            saveBtn.disabled = true;
        }
        
        // 获取会话ID
        const sessionId = window.inlineVersionManager?.currentSessionId || window.versionManager?.currentSessionId;
        if (!sessionId) {
            showMessage('保存失败：缺少会话ID，请刷新页面重试', 'error');
            return;
        }
        
        // 准备保存数据，处理路径格式
        // 姓名和年龄从后端session获取，不需要前端传递
        const saveData = {
            session_id: sessionId,
            original_image_path: originalImagePath ? (originalImagePath.startsWith('/') ? originalImagePath.substring(1) : originalImagePath) : null,
            generated_image_path: generatedImageUrl.startsWith('/') ? generatedImageUrl.substring(1) : generatedImageUrl,
            model_path: modelFilePath,
            title: title,
            category: category,
            description: description
            // artist_name 和 artist_age 将从后端session中获取
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
        console.error('保存作品错误:', error);
        showMessage(`保存失败: ${error.message}`, 'error');
    } finally {
        // 恢复按钮状态
        const saveBtn = document.querySelector('.modal-footer .primary-btn');
        if (saveBtn) {
            saveBtn.innerHTML = originalText;
            saveBtn.disabled = false;
        }
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

// ========== 图片添加菜单功能 ==========

// 检测是否是移动设备
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// 检测是否是Mac电脑
function isMacComputer() {
    return navigator.platform.toUpperCase().indexOf('MAC') >= 0 && !isMobileDevice();
}

// 检测是否支持摄像头API
function isCameraSupported() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
}

// 切换图片菜单显示/隐藏
function toggleImageMenu() {
    const menu = document.getElementById('image-menu');
    if (menu) {
        menu.classList.toggle('show');
    }
}

// 关闭图片菜单
function closeImageMenu() {
    const menu = document.getElementById('image-menu');
    if (menu) {
        menu.classList.remove('show');
    }
}

// 点击页面其他地方关闭菜单
document.addEventListener('click', function(event) {
    const menu = document.getElementById('image-menu');
    const addBtn = document.querySelector('.add-image-btn');
    
    if (menu && addBtn && !menu.contains(event.target) && !addBtn.contains(event.target)) {
        menu.classList.remove('show');
    }
});

// 拍摄图片（智能调用摄像头）
async function captureImage() {
    closeImageMenu();
    
    // 方案1: 移动设备 - 使用input capture（最简单）
    if (isMobileDevice()) {
        console.log('📱 移动设备: 使用input capture');
        const cameraInput = document.getElementById('camera-capture');
        if (cameraInput) {
            cameraInput.click();
        }
        return;
    }
    
    // 方案2: 桌面设备支持摄像头API - 使用getUserMedia
    if (isCameraSupported()) {
        console.log('💻 桌面设备: 使用getUserMedia API');
        try {
            await openCameraDialog();
        } catch (error) {
            console.error('摄像头调用失败，回退到文件选择:', error);
            // 如果失败，回退到文件选择
            const cameraInput = document.getElementById('camera-capture');
            if (cameraInput) {
                cameraInput.removeAttribute('capture');
                cameraInput.click();
            }
        }
        return;
    }
    
    // 方案3: 不支持摄像头 - 使用普通文件选择
    console.log('📁 不支持摄像头: 使用文件选择');
    const cameraInput = document.getElementById('camera-capture');
    if (cameraInput) {
        cameraInput.removeAttribute('capture');
        cameraInput.click();
    }
}

// 打开摄像头对话框（桌面端）
async function openCameraDialog() {
    return new Promise(async (resolve, reject) => {
        let stream = null;
        
        try {
            let videoConstraints = {
                width: { ideal: 1920 },
                height: { ideal: 1080 }
            };
            
            // Mac电脑：优先查找FaceTime HD摄像头
            if (isMacComputer()) {
                console.log('🍎 检测到Mac电脑，正在查找FaceTime HD摄像头...');
                
                try {
                    // 获取所有视频输入设备
                    const devices = await navigator.mediaDevices.enumerateDevices();
                    const videoDevices = devices.filter(device => device.kind === 'videoinput');
                    
                    console.log('📹 可用摄像头列表：', videoDevices.map(d => d.label || d.deviceId));
                    
                    // 查找FaceTime HD摄像头
                    const facetimeCamera = videoDevices.find(device => 
                        device.label.toLowerCase().includes('facetime') ||
                        device.label.toLowerCase().includes('built-in')
                    );
                    
                    if (facetimeCamera) {
                        console.log('✅ 找到FaceTime HD摄像头:', facetimeCamera.label);
                        videoConstraints.deviceId = { exact: facetimeCamera.deviceId };
                    } else {
                        console.log('⚠️ 未找到FaceTime摄像头，使用默认摄像头');
                    }
                } catch (enumError) {
                    console.log('⚠️ 枚举设备失败，使用默认摄像头:', enumError);
                }
            } else {
                // 非Mac设备：使用后置摄像头
                videoConstraints.facingMode = 'environment';
            }
            
            // 请求摄像头权限
            console.log('🎥 请求摄像头权限，配置：', videoConstraints);
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: videoConstraints
            });
            
            console.log('✅ 摄像头访问成功');
            
            // 创建摄像头对话框
            const dialog = document.createElement('div');
            dialog.className = 'camera-dialog';
            dialog.innerHTML = `
                <div class="camera-dialog-content">
                    <div class="camera-dialog-header">
                        <h3><i class="fas fa-camera"></i> 拍摄图片</h3>
                        <button class="camera-close-btn" onclick="closeCameraDialog()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="camera-preview-container">
                        <video id="camera-video" autoplay playsinline></video>
                        <canvas id="camera-canvas" style="display: none;"></canvas>
                    </div>
                    <div class="camera-dialog-footer">
                        <button class="camera-capture-btn" onclick="takeCameraPhoto()">
                            <i class="fas fa-camera"></i> 拍摄
                        </button>
                        <button class="camera-cancel-btn" onclick="closeCameraDialog()">
                            取消
                        </button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(dialog);
            
            // 将视频流连接到video元素
            const video = document.getElementById('camera-video');
            video.srcObject = stream;
            
            // 保存stream引用以便后续关闭
            dialog.cameraStream = stream;
            
            resolve();
            
        } catch (error) {
            console.error('摄像头访问失败:', error);
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            reject(error);
        }
    });
}

// 拍摄照片
async function takeCameraPhoto() {
    const video = document.getElementById('camera-video');
    const canvas = document.getElementById('camera-canvas');
    
    if (!video || !canvas) return;
    
    // 设置canvas尺寸
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // 绘制当前帧到canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    // 转换为Blob
    canvas.toBlob(async (blob) => {
        try {
            // 创建File对象
            const file = new File([blob], `camera_${Date.now()}.jpg`, { type: 'image/jpeg' });
            
            // 压缩图片
            showMessage('正在处理图片...', 'info');
            const compressedFile = await compressImage(file);
            
            // 使用压缩后的文件
            uploadedImageFile = compressedFile;
            
            // 显示预览
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = document.getElementById('uploaded-image-preview');
                const img = document.getElementById('uploaded-image');
                
                if (preview && img) {
                    img.src = e.target.result;
                    preview.style.display = 'block';
                    showMessage('图片拍摄成功！', 'success');
                }
            };
            reader.readAsDataURL(compressedFile);
            
            // 关闭摄像头对话框
            closeCameraDialog();
            
        } catch (error) {
            console.error('处理照片失败:', error);
            showMessage('图片处理失败，请重试', 'error');
        }
    }, 'image/jpeg', 0.95);
}

// 关闭摄像头对话框
function closeCameraDialog() {
    const dialog = document.querySelector('.camera-dialog');
    if (dialog) {
        // 停止摄像头
        if (dialog.cameraStream) {
            dialog.cameraStream.getTracks().forEach(track => track.stop());
        }
        // 移除对话框
        dialog.remove();
    }
}

// 处理摄像头拍摄的图片（移动端）
async function handleCameraCapture(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
        // 显示加载状态
        showMessage('正在处理图片...', 'info');

        // 压缩图片
        const compressedFile = await compressImage(file);
        
        // 使用压缩后的文件
        uploadedImageFile = compressedFile;
        
        // 显示预览
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('uploaded-image-preview');
            const img = document.getElementById('uploaded-image');
            
            if (preview && img) {
                img.src = e.target.result;
                preview.style.display = 'block';
                showMessage('图片拍摄成功！', 'success');
            }
        };
        reader.readAsDataURL(compressedFile);

    } catch (error) {
        console.error('处理拍摄图片失败:', error);
        showMessage('图片处理失败，请重试', 'error');
    }
}

// 压缩图片
function compressImage(file, maxWidth = 1024, maxHeight = 1024, quality = 0.8) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const img = new Image();
            
            img.onload = function() {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;
                
                // 计算缩放比例
                if (width > maxWidth || height > maxHeight) {
                    const ratio = Math.min(maxWidth / width, maxHeight / height);
                    width *= ratio;
                    height *= ratio;
                }
                
                canvas.width = width;
                canvas.height = height;
                
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                
                // 转换为blob
                canvas.toBlob(function(blob) {
                    if (blob) {
                        // 创建新的File对象
                        const compressedFile = new File([blob], file.name, {
                            type: 'image/jpeg',
                            lastModified: Date.now()
                        });
                        resolve(compressedFile);
                    } else {
                        reject(new Error('图片压缩失败'));
                    }
                }, 'image/jpeg', quality);
            };
            
            img.onerror = function() {
                reject(new Error('图片加载失败'));
            };
            
            img.src = e.target.result;
        };
        
        reader.onerror = function() {
            reject(new Error('文件读取失败'));
        };
        
        reader.readAsDataURL(file);
    });
}

// 显示图片URL对话框
function showImageUrlDialog() {
    closeImageMenu();
    const modal = document.getElementById('image-url-modal');
    if (modal) {
        modal.style.display = 'flex';
        // 清空输入框
        const input = document.getElementById('image-url-input');
        if (input) {
            input.value = '';
            input.focus();
        }
    }
}

// 关闭图片URL对话框
function closeImageUrlDialog() {
    const modal = document.getElementById('image-url-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 从URL加载图片
async function loadImageFromUrl() {
    const input = document.getElementById('image-url-input');
    const url = input ? input.value.trim() : '';
    
    if (!url) {
        showMessage('请输入图片链接', 'error');
        return;
    }
    
    // 验证URL格式
    try {
        new URL(url);
    } catch (e) {
        showMessage('请输入有效的图片链接', 'error');
        return;
    }
    
    try {
        closeImageUrlDialog();
        showMessage('正在加载图片...', 'info');
        
        // 通过后端代理下载图片
        const response = await fetch('/api/fetch-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 显示预览
            const preview = document.getElementById('uploaded-image-preview');
            const img = document.getElementById('uploaded-image');
            
            if (preview && img) {
                img.src = result.image_url;
                preview.style.display = 'block';
                showMessage('图片加载成功！', 'success');
                
                // 保存图片路径供后续使用
                originalImagePath = result.image_url;
            }
        } else {
            showMessage(result.error || '图片加载失败', 'error');
        }
        
    } catch (error) {
        console.error('加载图片失败:', error);
        showMessage('图片加载失败，请检查链接是否正确', 'error');
    }
}

// 关闭图片菜单
function closeImageMenu() {
    const menu = document.getElementById('image-menu');
    if (menu) {
        menu.classList.remove('show');
    }
}

// 显示生成的多张图片缩略图
function displayGeneratedThumbnails(imageUrls) {
    console.log('📸 显示生成的缩略图:', imageUrls);
    
    // 找到缩略图网格容器
    const thumbnailsGrid = document.querySelector('.thumbnails-grid');
    if (!thumbnailsGrid) {
        console.error('未找到缩略图网格容器');
        return;
    }
    
    // 清空现有缩略图
    thumbnailsGrid.innerHTML = '';
    
    // 为每张图片创建缩略图
    imageUrls.forEach((url, index) => {
        const thumbnailSlot = document.createElement('div');
        thumbnailSlot.className = 'thumbnail-slot';
        thumbnailSlot.style.cursor = 'pointer';
        
        const img = document.createElement('img');
        img.src = url;
        img.alt = `生成图片 ${index + 1}`;
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        img.style.borderRadius = '8px';
        img.style.transition = 'transform 0.2s, box-shadow 0.2s';
        
        // 鼠标悬停效果
        img.onmouseenter = () => {
            img.style.transform = 'scale(1.05)';
            img.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
        };
        img.onmouseleave = () => {
            img.style.transform = 'scale(1)';
            img.style.boxShadow = 'none';
        };
        
        // 点击缩略图切换到该图片
        img.onclick = () => {
            console.log(`🖱️ 选择图片 ${index + 1}`);
            selectGeneratedImage(url);
        };
        
        thumbnailSlot.appendChild(img);
        thumbnailsGrid.appendChild(thumbnailSlot);
    });
    
    // 如果图片少于5张，填充空白占位符
    for (let i = imageUrls.length; i < 5; i++) {
        const thumbnailSlot = document.createElement('div');
        thumbnailSlot.className = 'thumbnail-slot';
        const placeholder = document.createElement('div');
        placeholder.className = 'thumbnail-placeholder';
        placeholder.textContent = i + 1;
        thumbnailSlot.appendChild(placeholder);
        thumbnailsGrid.appendChild(thumbnailSlot);
    }
}

// 选择某张生成的图片作为主图
function selectGeneratedImage(url) {
    generatedImageUrl = url;
    
    // 更新所有显示图片的元素
    const generatedImageEl = document.getElementById('generated-image');
    const currentImageEl = document.getElementById('current-image');
    const finalImageEl = document.getElementById('final-image');
    
    if (generatedImageEl) {
        generatedImageEl.src = url;
    }
    if (currentImageEl) {
        currentImageEl.src = url;
    }
    if (finalImageEl) {
        finalImageEl.src = url;
    }
    
    showMessage('已切换到选中的图片', 'success');
}
