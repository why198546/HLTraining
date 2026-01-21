/**
 * 摄像头和图片上传功能 - 模块化设计
 */


let cameraStream = null;
let capturedPhotoBlob = null;
let originalCapturedPhotoBlob = null; // 原始未裁切照片
let uploadedReferenceFile = null;  // 存储参考图片文件
let availableCameras = [];  // 可用摄像头列表
let currentCameraIndex = 0;  // 当前摄像头索引

// 暴露到全局作用域供其他模块使用
window.uploadedReferenceFile = null;
window.availableCameras = availableCameras;

// 打开拍照模态框
function openCameraModal(event) {
  if (event && event.preventDefault) {
    event.preventDefault();
  }
  const modal = document.getElementById('camera-modal');
  if (modal) {
    // 强制设置样式确保正确显示
    modal.style.display = 'flex';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.zIndex = '99999';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.margin = '0';
    modal.style.padding = '0';
    
    document.body.style.overflow = 'hidden';
    
    // 初始化选项卡：默认显示上传选项卡
    initializeDefaultTab();
    
  } else {
    hldebug.error('❌ 未找到模态框元素 #camera-modal');
  }
}

// 初始化默认选项卡（上传）
function initializeDefaultTab() {
  // 隐藏所有内容
  document.querySelectorAll('.camera-tab-content').forEach(el => {
    el.classList.remove('active');
  });
  
  // 取消所有按钮的激活状态
  document.querySelectorAll('.camera-tab-btn').forEach(el => {
    el.classList.remove('active');
  });
  
  // 激活上传选项卡和按钮
  const uploadContent = document.getElementById('upload-tab');
  const uploadBtn = document.querySelector('[data-tab="upload"]');
  
  if (uploadContent) {
    uploadContent.classList.add('active');
  }
  if (uploadBtn) {
    uploadBtn.classList.add('active');
  }
}

// 确保函数在全局作用域
window.openCameraModal = openCameraModal;

// 关闭拍照模态框
function closeCameraModal() {
  const modal = document.getElementById('camera-modal');
  if (modal) {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
  }
  stopCamera();
  resetCameraUI();
}

// 切换选项卡
async function switchCameraTab(tabName) {
  // 隐藏所有内容
  document.querySelectorAll('.camera-tab-content').forEach(el => {
    el.classList.remove('active');
  });
  
  // 取消所有按钮的激活状态
  document.querySelectorAll('.camera-tab-btn').forEach(el => {
    el.classList.remove('active');
  });
  
  // 显示选中的内容
  const content = document.getElementById(tabName + '-tab');
  if (content) {
    content.classList.add('active');
  }
  
  // 激活选中的按钮
  document.querySelector('[data-tab="' + tabName + '"]').classList.add('active');
  
  // 切换到摄像头选项卡时，枚举可用摄像头并自动启动
  if (tabName === 'camera') {
    await enumerateCameras();
    // 自动启动摄像头
    await startCamera();
  } else if (tabName === 'upload') {
    // 切换回上传时，关闭摄像头
    stopCamera();
  }
}

// 枚举可用摄像头
async function enumerateCameras() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    availableCameras = devices.filter(device => device.kind === 'videoinput');
    
    // 显示或隐藏摄像头切换按钮
    const switchBtn = document.querySelector('.camera-switch-btn');
    if (switchBtn) {
      switchBtn.style.display = availableCameras.length > 1 ? 'flex' : 'none';
    }
  } catch (error) {
    hldebug.error('❌ 枚举摄像头失败:', error);
    availableCameras = [];
  }
}

// 启动摄像头
async function startCamera() {
  const video = document.getElementById('camera-video');
  const startBtn = document.getElementById('camera-start-btn');
  const captureBtn = document.getElementById('camera-capture-btn');

  startBtn.disabled = true;
  startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 启动中...';

  try {
    // 先枚举摄像头
    await enumerateCameras();
    
    // 如果有多个摄像头，优先使用后置摄像头
    let constraints;
    if (availableCameras.length > 1) {
      // 尝试使用后置摄像头
      const backCamera = availableCameras.find(cam => {
        const label = cam.label.toLowerCase();
        return label.includes('back') || label.includes('rear') || label.includes('后');
      });
      
      if (backCamera) {
        currentCameraIndex = availableCameras.indexOf(backCamera);
        constraints = {
          video: { deviceId: { exact: backCamera.deviceId }, width: { ideal: 1920 }, height: { ideal: 1080 } },
          audio: false
        };
      } else {
        // 使用第一个摄像头
        currentCameraIndex = 0;
        constraints = {
          video: { deviceId: { exact: availableCameras[0].deviceId }, width: { ideal: 1920 }, height: { ideal: 1080 } },
          audio: false
        };
      }
    } else {
      // 只有一个摄像头，使用默认的facingMode
      constraints = {
        video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } },
        audio: false
      };
    }
    
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    cameraStream = stream;
    video.srcObject = stream;
    startBtn.style.display = 'none';
    captureBtn.style.display = 'flex';
    
    // 显示当前摄像头信息
    if (availableCameras.length > 0) {
      const videoTrack = stream.getVideoTracks()[0];
      const settings = videoTrack.getSettings ? videoTrack.getSettings() : {};
      const facingMode = settings.facingMode || '';
      const currentCamera = availableCameras[currentCameraIndex];
      const label = currentCamera ? currentCamera.label.toLowerCase() : '';
      
      let cameraType = '摄像头';
      if (facingMode === 'user' || label.includes('front') || label.includes('前')) {
        cameraType = '前置摄像头';
      } else if (facingMode === 'environment' || label.includes('back') || label.includes('rear') || label.includes('后')) {
        cameraType = '后置摄像头';
      } else {
        cameraType = `摄像头 ${currentCameraIndex + 1}/${availableCameras.length}`;
      }
      
      updateCameraSwitchButton(cameraType);
    }
  } catch (error) {
    hldebug.error('❌ 无法访问摄像头:', error);
    startBtn.disabled = false;
    startBtn.innerHTML = '<i class="fas fa-play"></i> 启动摄像头';
    
    if (error.name === 'NotAllowedError') {
      alert('请允许访问摄像头权限');
    } else if (error.name === 'NotFoundError') {
      alert('未检测到摄像头设备');
    } else {
      alert('无法访问摄像头，请检查权限设置');
    }
  }
}

// 切换摄像头
async function switchCameraDevice(event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  
  if (availableCameras.length <= 1) {
    if (typeof showToast === 'function') {
      showToast('只有一个摄像头可用', 'info');
    }
    return;
  }
  
  try {
    const switchBtn = document.querySelector('.camera-switch-btn');
    const video = document.getElementById('camera-video');
    
    if (switchBtn) {
      switchBtn.disabled = true;
      switchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    
    // 添加淡出效果
    if (video) {
      video.style.opacity = '0.5';
      video.style.transition = 'opacity 0.3s';
    }
    
    // 切换到下一个摄像头
    currentCameraIndex = (currentCameraIndex + 1) % availableCameras.length;
    const targetCamera = availableCameras[currentCameraIndex];
    
    // 停止当前流
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
    }
    
    // 启动新的流
    const constraints = {
      video: { deviceId: { exact: targetCamera.deviceId }, width: { ideal: 1920 }, height: { ideal: 1080 } },
      audio: false
    };
    
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    cameraStream = stream;
    video.srcObject = stream;
    
    // 等待视频加载完成后恢复透明度
    video.onloadedmetadata = () => {
      video.style.opacity = '1';
    };
    
    // 判断前后摄像头并显示信息
    const videoTrack = stream.getVideoTracks()[0];
    const settings = videoTrack.getSettings ? videoTrack.getSettings() : {};
    const facingMode = settings.facingMode || '';
    
    // 根据label或facingMode判断摄像头类型
    let cameraType = '摄像头';
    const label = targetCamera.label.toLowerCase();
    
    if (facingMode === 'user' || label.includes('front') || label.includes('前')) {
      cameraType = '前置摄像头';
    } else if (facingMode === 'environment' || label.includes('back') || label.includes('rear') || label.includes('后')) {
      cameraType = '后置摄像头';
    } else {
      cameraType = `摄像头 ${currentCameraIndex + 1}/${availableCameras.length}`;
    }
    
    // 更新按钮图标和提示
    updateCameraSwitchButton(cameraType);
    
    // 显示切换成功提示
    if (typeof showToast === 'function') {
      showToast(`已切换到${cameraType}`, 'success');
    }
    
    // 恢复按钮
    if (switchBtn) {
      switchBtn.disabled = false;
      switchBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
    }
  } catch (error) {
    hldebug.error('❌ 切换摄像头失败:', error);
    if (typeof showToast === 'function') {
      showToast('切换摄像头失败，请重试', 'error');
    }
    
    // 尝试回滚到上一个摄像头
    currentCameraIndex = (currentCameraIndex - 1 + availableCameras.length) % availableCameras.length;
    
    const switchBtn = document.querySelector('.camera-switch-btn');
    if (switchBtn) {
      switchBtn.disabled = false;
      switchBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
    }
    
    const video = document.getElementById('camera-video');
    if (video) {
      video.style.opacity = '1';
    }
  }
}

// 更新摄像头切换按钮的提示
function updateCameraSwitchButton(cameraType) {
  const switchBtn = document.querySelector('.camera-switch-btn');
  if (switchBtn) {
    switchBtn.title = `当前：${cameraType} (点击切换)`;
  }
  
  // 更新摄像头信息标签（如果存在）
  const cameraInfo = document.getElementById('camera-info');
  if (cameraInfo) {
    cameraInfo.textContent = cameraType;
  }
}

// 拍照
function capturePhoto() {
  const video = document.getElementById('camera-video');
  const canvas = document.getElementById('camera-canvas');
  const context = canvas.getContext('2d');

  // 使用视频流的原始分辨率
  const videoWidth = video.videoWidth;
  const videoHeight = video.videoHeight;
  
  canvas.width = videoWidth;
  canvas.height = videoHeight;
  
  // 绘制完整的视频帧
  context.drawImage(video, 0, 0, videoWidth, videoHeight);

  canvas.toBlob(async blob => {
    // 保存原始照片
    originalCapturedPhotoBlob = blob;
    capturedPhotoBlob = blob;

    // 如果勾选了“自动裁切纸张”，尝试识别并裁切
    const autoCropEl = document.getElementById('auto-crop-paper');
    const shouldAutoCrop = autoCropEl ? autoCropEl.checked : false;

    if (shouldAutoCrop) {
      try {
        const cropped = await autoCropPaperFromBlob(blob);
        if (cropped) {
          capturedPhotoBlob = cropped;
          const revertLink = document.getElementById('revert-original-link');
          if (revertLink) revertLink.style.display = 'inline-block';
          if (typeof showToast === 'function') {
            showToast('已自动识别并裁切到纸张边缘', 'success');
          }
        } else {
          const revertLink = document.getElementById('revert-original-link');
          if (revertLink) revertLink.style.display = 'none';
          if (typeof showToast === 'function') {
            showToast('未检测到清晰纸张边缘，已保留原图', 'info');
          }
        }
      } catch (err) {
        hldebug.error('自动裁切失败:', err);
      }
    } else {
      const revertLink = document.getElementById('revert-original-link');
      if (revertLink) revertLink.style.display = 'none';
    }

    stopCamera();
    showPhotoPreview();
    updateCameraUIForPreview();
  }, 'image/jpeg', 0.95);
}

// 显示照片预览
function showPhotoPreview() {
  const previewArea = document.querySelector('.camera-preview-area');
  if (!previewArea || !capturedPhotoBlob) return;

  const preview = document.createElement('img');
  preview.src = URL.createObjectURL(capturedPhotoBlob);
  preview.style.width = '100%';
  preview.style.height = '100%';
  preview.style.objectFit = 'contain';

  previewArea.innerHTML = '';
  previewArea.appendChild(preview);
}

// 重新拍照
function retakePhoto() {
  capturedPhotoBlob = null;
  resetCameraUI();
  startCamera();
}

// 还原原始未裁切照片
function revertOriginalPhoto() {
  if (originalCapturedPhotoBlob) {
    capturedPhotoBlob = originalCapturedPhotoBlob;
    showPhotoPreview();
    const revertLink = document.getElementById('revert-original-link');
    if (revertLink) revertLink.style.display = 'none';
  }
}
window.revertOriginalPhoto = revertOriginalPhoto;

// ========== 纸张自动识别与裁切 ==========
// 动态加载 OpenCV.js（仅在需要时加载）
function loadOpenCV() {
  return new Promise((resolve, reject) => {
    if (window.cv && typeof window.cv.Mat !== 'undefined') {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://docs.opencv.org/4.x/opencv.js';
    script.async = true;
    script.onload = () => {
      // 等待 OpenCV 初始化
      const checkReady = () => {
        if (window.cv && window.cv.getBuildInformation) {
          resolve();
        } else {
          setTimeout(checkReady, 50);
        }
      };
      checkReady();
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

// 将 Blob 转换为 HTMLImageElement
function blobToImage(blob) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(img);
    };
    img.onerror = err => {
      URL.revokeObjectURL(url);
      reject(err);
    };
    img.src = url;
  });
}

// 自动识别纸张并裁切
async function autoCropPaperFromBlob(blob) {
  try {
    await loadOpenCV();
    const img = await blobToImage(blob);

    // 读取到 OpenCV Mat
    const src = cv.imread(img);
    const original = src.clone();
    const gray = new cv.Mat();
    const blur = new cv.Mat();
    const edges = new cv.Mat();

    cv.cvtColor(src, gray, cv.COLOR_RGBA2GRAY, 0);
    cv.GaussianBlur(gray, blur, new cv.Size(5, 5), 0, 0, cv.BORDER_DEFAULT);
    cv.Canny(blur, edges, 75, 200, 3, false);

    // 找轮廓
    const contours = new cv.MatVector();
    const hierarchy = new cv.Mat();
    cv.findContours(edges, contours, hierarchy, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE);

    let maxArea = 0;
    let docContour = null;
    for (let i = 0; i < contours.size(); i++) {
      const cnt = contours.get(i);
      const peri = cv.arcLength(cnt, true);
      const approx = new cv.Mat();
      cv.approxPolyDP(cnt, approx, 0.02 * peri, true);
      if (approx.rows === 4) {
        const area = cv.contourArea(approx);
        if (area > maxArea) {
          maxArea = area;
          if (docContour) docContour.delete();
          docContour = approx; // 保存四边形
        } else {
          approx.delete();
        }
      } else {
        approx.delete();
      }
      cnt.delete();
    }

    let resultBlob = null;
    if (docContour && maxArea > (src.rows * src.cols) * 0.1) {
      // 提取四个点并排序（tl,tr,br,bl）
      const pts = [];
      for (let r = 0; r < docContour.rows; r++) {
        const x = docContour.intPtr(r, 0)[0];
        const y = docContour.intPtr(r, 0)[1];
        pts.push({ x, y });
      }
      // 根据 x+y 与 x-y 进行排序
      const sumSorted = [...pts].sort((a, b) => (a.x + a.y) - (b.x + b.y));
      const diffSorted = [...pts].sort((a, b) => (a.x - a.y) - (b.x - b.y));
      const tl = sumSorted[0];
      const br = sumSorted[3];
      const tr = diffSorted[0];
      const bl = diffSorted[3];

      const widthA = Math.hypot(br.x - bl.x, br.y - bl.y);
      const widthB = Math.hypot(tr.x - tl.x, tr.y - tl.y);
      const maxWidth = Math.max(widthA, widthB) | 0;
      const heightA = Math.hypot(tr.x - br.x, tr.y - br.y);
      const heightB = Math.hypot(tl.x - bl.x, tl.y - bl.y);
      const maxHeight = Math.max(heightA, heightB) | 0;

      const srcTri = cv.matFromArray(4, 1, cv.CV_32FC2, [
        tl.x, tl.y,
        tr.x, tr.y,
        br.x, br.y,
        bl.x, bl.y
      ]);
      const dstTri = cv.matFromArray(4, 1, cv.CV_32FC2, [
        0, 0,
        maxWidth - 1, 0,
        maxWidth - 1, maxHeight - 1,
        0, maxHeight - 1
      ]);

      const M = cv.getPerspectiveTransform(srcTri, dstTri);
      const warped = new cv.Mat();
      cv.warpPerspective(original, warped, M, new cv.Size(maxWidth, maxHeight), cv.INTER_LINEAR, cv.BORDER_CONSTANT, new cv.Scalar());

      // 写入到 canvas 并导出 blob
      const tmpCanvas = document.createElement('canvas');
      cv.imshow(tmpCanvas, warped);
      resultBlob = await new Promise(res => tmpCanvas.toBlob(res, 'image/jpeg', 0.95));

      // 释放资源
      srcTri.delete(); dstTri.delete(); M.delete(); warped.delete();
    }

    // 清理
    original.delete(); src.delete(); gray.delete(); blur.delete(); edges.delete();
    contours.delete(); hierarchy.delete();
    if (docContour) docContour.delete();

    return resultBlob; // 若识别失败返回 null
  } catch (e) {
    hldebug.error('autoCropPaperFromBlob error', e);
    return null;
  }
}

// 使用拍照
function usePhoto() {
  if (!capturedPhotoBlob) return;
  const file = new File([capturedPhotoBlob], 'camera-photo.jpg', { type: 'image/jpeg' });
  processPhoto(file);
  closeCameraModal();
}

// 触发文件选择
function triggerFileInput() {
  document.getElementById('file-input').click();
}

// 处理文件上传
function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  if (!file.type.startsWith('image/')) {
    alert('请选择一个图片文件');
    return;
  }

  if (file.size > 10 * 1024 * 1024) {
    alert('文件大小不能超过 10MB');
    return;
  }

  showUploadPreview(file);
}

// 显示上传预览
function showUploadPreview(file) {
  const preview = document.getElementById('upload-preview');
  const previewImg = document.getElementById('upload-preview-img');

  const reader = new FileReader();
  reader.onload = e => {
    previewImg.src = e.target.result;
    preview.style.display = 'block';
    preview.dataset.file = JSON.stringify({
      name: file.name,
      type: file.type,
      size: file.size
    });
  };
  reader.readAsDataURL(file);
}

// 清除上传预览
function clearUploadPreview() {
  const preview = document.getElementById('upload-preview');
  const fileInput = document.getElementById('file-input');
  preview.style.display = 'none';
  fileInput.value = '';
}

// 使用上传的照片
function useUploadedPhoto() {
  const previewImg = document.getElementById('upload-preview-img');
  const src = previewImg.src;
  
  if (!src) return;

  // 从 data URL 获取文件名
  const canvas = document.createElement('canvas');
  const img = new Image();
  img.onload = function() {
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
    
    canvas.toBlob(blob => {
      const file = new File([blob], 'uploaded-image.jpg', { type: 'image/jpeg' });
      processPhoto(file);
      closeCameraModal();
    }, 'image/jpeg', 0.95);
  };
  img.src = src;
}

// 处理照片
function processPhoto(file) {
  
  // 保存文件供后续表单提交使用（同时保存到本地变量和全局变量）
  uploadedReferenceFile = file;
  window.uploadedReferenceFile = file;
  
  const reader = new FileReader();
  reader.onload = e => {
    const imageDataUrl = e.target.result;
    
    // 1. 在页面上显示参考图片
    showReferenceImage(imageDataUrl, file.name);
    
    // 2. 生成AI图片描述
    generateAIDescription(file, imageDataUrl);
  };
  reader.readAsDataURL(file);
}

// 显示参考图片
function showReferenceImage(dataUrl, fileName) {
  const form = document.querySelector('.prompt-form');
  if (!form) return;
  
  // 查找或创建参考图片容器
  let refContainer = form.querySelector('.reference-image-container');
  if (!refContainer) {
    refContainer = document.createElement('div');
    refContainer.className = 'reference-image-container';
    refContainer.style.cssText = `
      margin: 15px 0;
      padding: 15px;
      background: #f8f9fa;
      border-radius: 12px;
      border: 2px dashed #00704A;
    `;
    
    // 插入到原始输入框之前
    const rawPromptSection = form.querySelector('.prompt-section');
    if (rawPromptSection) {
      rawPromptSection.parentNode.insertBefore(refContainer, rawPromptSection);
    }
  }
  
  refContainer.innerHTML = `
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
      <span style="font-weight: 600; color: #00704A;">📷 参考图片</span>
      <button type="button" onclick="removeReferenceImage()" style="
        background: #ff4757;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 12px;
      ">
        <i class="fas fa-times"></i> 移除
      </button>
    </div>
    <img src="${dataUrl}" alt="${fileName}" style="
      max-width: 100%;
      max-height: 200px;
      border-radius: 10px;
      object-fit: contain;
      background: white;
      padding: 5px;
    ">
    <div class="image-description" style="
      margin-top: 10px;
      padding: 10px;
      background: white;
      border-radius: 8px;
      font-size: 14px;
      color: #666;
    ">
      <i class="fas fa-spinner fa-spin"></i> 正在识别图片内容...
    </div>
  `;
}

// 移除参考图片
function removeReferenceImage() {
  const container = document.querySelector('.reference-image-container');
  if (container) {
    container.remove();
  }
  // 清除保存的文件
  uploadedReferenceFile = null;
  window.uploadedReferenceFile = null;
}
window.removeReferenceImage = removeReferenceImage;

// 生成AI图片描述
async function generateAIDescription(file, imageDataUrl) {
  const descContainer = document.querySelector('.image-description');
  if (!descContainer) return;
  
  try {
    // TODO: 这里应该调用实际的图片识别API
    // 现在先用简单的客户端分析
    descContainer.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 正在分析图片...';
    
    const img = new Image();
    img.onload = function() {
      const width = img.width;
      const height = img.height;
      
      let desc = '图片信息：';
      
      // 分析尺寸和比例
      if (Math.abs(width - height) < Math.max(width, height) * 0.2) {
        desc += '正方形构图';
      } else if (width > height) {
        desc += `横向构图 (${width}×${height})`;
      } else {
        desc += `纵向构图 (${width}×${height})`;
      }
      
      // 提示用户
      desc += '。\n💡 提示：请根据图片内容，在下方"原始输入"框中详细描述图片中的人物、场景、动作等要素，或直接生成素描效果。';
      
      descContainer.innerHTML = desc.replace(/\n/g, '<br>');
      descContainer.style.whiteSpace = 'pre-line';
      
      // 不自动填充输入框，让用户自己决定是否输入
    };
    img.src = imageDataUrl;
    
  } catch (error) {
    hldebug.error('生成描述失败:', error);
    descContainer.innerHTML = '⚠️ 无法识别图片内容，请手动描述';
  }
}

// 旧的简单生成描述函数（保留作为备用）
function generateDescription(img) {
  const width = img.width;
  const height = img.height;
  let desc = '参考图片：';
  
  if (Math.abs(width - height) < Math.max(width, height) * 0.2) {
    desc += '正方形构图，';
  } else if (width > height) {
    desc += '横向构图，';
  } else {
    desc += '纵向构图，';
  }
  
  desc += '可根据照片调整描述';
  return desc;
}

// 添加到提示词框
function addToPrompt(description) {
  const form = document.querySelector('.prompt-form');
  if (!form) return;
  
  const rawPrompt = form.querySelector('textarea[name="raw_prompt"]');
  if (!rawPrompt) return;
  
  const currentText = rawPrompt.value.trim();
  if (currentText && !currentText.includes('参考')) {
    rawPrompt.value = currentText + '；' + description;
  } else if (!currentText) {
    rawPrompt.value = description;
  }
  
  rawPrompt.dispatchEvent(new Event('input', { bubbles: true }));
}

// 停止摄像头
function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
  }
  
  const video = document.getElementById('camera-video');
  if (video) {
    video.srcObject = null;
  }
}

// 重置摄像头UI
function resetCameraUI() {
  const video = document.getElementById('camera-video');
  const startBtn = document.getElementById('camera-start-btn');
  const captureBtn = document.getElementById('camera-capture-btn');
  const retakeBtn = document.getElementById('camera-retake-btn');
  const useBtn = document.getElementById('camera-use-btn');
  const revertLink = document.getElementById('revert-original-link');

  if (video) video.srcObject = null;
  
  if (startBtn) {
    startBtn.style.display = 'flex';
    startBtn.disabled = false;
    startBtn.innerHTML = '<i class="fas fa-play"></i> 启动摄像头';
  }
  if (captureBtn) captureBtn.style.display = 'none';
  if (retakeBtn) retakeBtn.style.display = 'none';
  if (useBtn) useBtn.style.display = 'none';

  capturedPhotoBlob = null;
  originalCapturedPhotoBlob = null;
  if (revertLink) revertLink.style.display = 'none';
}

// 更新摄像头UI为预览状态
function updateCameraUIForPreview() {
  const startBtn = document.getElementById('camera-start-btn');
  const captureBtn = document.getElementById('camera-capture-btn');
  const retakeBtn = document.getElementById('camera-retake-btn');
  const useBtn = document.getElementById('camera-use-btn');

  if (startBtn) startBtn.style.display = 'none';
  if (captureBtn) captureBtn.style.display = 'none';
  if (retakeBtn) retakeBtn.style.display = 'flex';
  if (useBtn) useBtn.style.display = 'flex';
}

// 初始化拖拽上传
document.addEventListener('DOMContentLoaded', function() {
  const uploadArea = document.querySelector('.upload-area');
  if (uploadArea) {
    uploadArea.addEventListener('dragover', e => {
      e.preventDefault();
      uploadArea.style.borderColor = '#00704A';
      uploadArea.style.background = '#f0f7f4';
    });

    uploadArea.addEventListener('dragleave', () => {
      uploadArea.style.borderColor = '#ddd';
      uploadArea.style.background = '#fafafa';
    });

    uploadArea.addEventListener('drop', e => {
      e.preventDefault();
      uploadArea.style.borderColor = '#ddd';
      uploadArea.style.background = '#fafafa';

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        const fileInput = document.getElementById('file-input');
        fileInput.files = files;
        handleFileUpload({ target: fileInput });
      }
    });
  }
  
  // 关闭按钮点击背景也能关闭
  const modal = document.getElementById('camera-modal');
  if (modal) {
    modal.querySelector('.camera-modal-overlay').addEventListener('click', closeCameraModal);
  }
});
