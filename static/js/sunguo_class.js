// ========== 特征选择器逻辑 ==========

// 折叠/展开特征检测器
window.toggleFeatureDetector = function() {
  const detector = document.querySelector('.feature-detector-section');
  if (detector) {
    detector.classList.toggle('collapsed');
  }
};

// 特征关键词映射（与generation.py保持一致）
const featureKeywords = {
  gender: ['男孩', '女孩', '男生', '女生', '男', '女', '小伙', '姑娘', '闪男', '闪女'],
  body: ['胖', '瘦', '适中', '壮', '苗条', '强壮', '纤细', '肥胖', '削瘦', '身材', '胖嘟嘟', '壮实', '结实'],
  hair_length: ['长发', '短发', '中长发', '齐肩发', '披肩发', '长头发', '短头发', '头发'],
  hair_style: ['卷发', '直发', '波浪', '自然卷', '微卷', '卷头发', '直头发', '平头', '寸头', '光头', '马尾', '辫子', '发型'],
  skin: ['皮肤黑', '皮肤白', '黑皮肤', '白皮肤', '黑色皮肤', '白色皮肤', '肤色', '皮肤', '黑', '白', '黑黑', '白白', '黑黑的', '白白的', '黑色', '白色', '黝黑', '白皙', '深色', '浅色', '深色皮肤', '浅色皮肤'],
  eyes: ['大眼睛', '小眼睛', '眼睛大', '眼睛小', '单眼皮', '双眼皮', '眼睛', '大眼', '小眼'],
  nose: ['大鼻子', '小鼻子', '高鼻梁', '低鼻梁', '挺鼻', '鼻子大', '鼻子小', '塌鼻子', '鼻梁', '鼻子', '高高的鼻子', '高高的鼻梁'],
  mouth: ['大嘴', '小嘴', '嘴大', '嘴小', '樱桃小嘴', '嘴巴'],
  lips: ['厚嘴唇', '薄嘴唇', '嘴唇厚', '嘴唇薄', '嘴唇', '肥厚的嘴唇', '肥肥的嘴唇', '肥嘴唇'],
  ears: ['大耳朵', '小耳朵', '耳朵大', '耳朵小', '耳朵']
};

// 初始化特征选择器
function initFeatureSelector() {
  const characterForm = document.querySelector('form[data-lesson="character"]');
  if (!characterForm) return;

  const featureBtns = characterForm.querySelectorAll('.feature-btn');
  const rawPromptTextarea = characterForm.querySelector('textarea[name="raw_prompt"]');

  if (!rawPromptTextarea) return;

  // 选项点击事件：选择 → 添加到文本
  featureBtns.forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const feature = this.dataset.feature;
      const value = this.dataset.value;
      
      // 同组按钮互斥（单选效果）
      const sameGroupBtns = characterForm.querySelectorAll(`.feature-btn[data-feature="${feature}"]`);
      sameGroupBtns.forEach(b => b.classList.remove('active'));
      
      // 切换当前按钮
      this.classList.add('active');
      
      // 高亮类别标签
      const label = characterForm.querySelector(`.feature-label[data-feature="${feature}"]`);
      if (label) {
        label.classList.add('active');
      }
      
      // 删除该特征类别的所有关键词，再添加新的
      removeFeatureKeywords(rawPromptTextarea, feature);
      appendFeatureToPrompt(rawPromptTextarea, value);
      
      // 触发AI优化提示
      const optimizedTextarea = characterForm.querySelector('textarea[name="prompt"]');
      if (optimizedTextarea && rawPromptTextarea.value.trim()) {
        optimizedTextarea.placeholder = '💡 可以点击✨按钮进行AI优化';
      }
    });
  });

  // 文本框变化事件：文本 → 高亮选项
  rawPromptTextarea.addEventListener('input', function() {
    syncTextToFeatures(this.value, featureBtns);
  });

  // 初始化时检测文本并高亮
  if (rawPromptTextarea.value.trim()) {
    syncTextToFeatures(rawPromptTextarea.value, featureBtns);
  }
}

// 删除特定特征类别的所有关键词
function removeFeatureKeywords(textarea, feature) {
  let text = textarea.value;
  const keywords = featureKeywords[feature] || [];
  
  // 遍历该特征的所有关键词，删除它们
  keywords.forEach(keyword => {
    // 处理各种可能的分隔情况
    text = text.replace(new RegExp(keyword + '[，、,\\s]*', 'g'), '');
    text = text.replace(new RegExp('[，、,\\s]*' + keyword, 'g'), '');
  });
  
  // 清理多余的标点符号和空格
  text = text.replace(/[，、,\s]+/g, '，');
  text = text.replace(/^[，、,\s]+|[，、,\s]+$/g, '');
  
  textarea.value = text;
}

// 添加特征到提示词
function appendFeatureToPrompt(textarea, value) {
  const currentText = textarea.value.trim();
  
  // 如果文本为空，直接设置
  if (!currentText) {
    textarea.value = value;
    return;
  }
  
  // 检查是否已包含该特征
  if (currentText.includes(value)) {
    return;
  }
  
  // 智能拼接：如果最后没有标点符号，加逗号
  const lastChar = currentText[currentText.length - 1];
  const needsPunctuation = !['，', '。', '、', ',', '.'].includes(lastChar);
  
  textarea.value = currentText + (needsPunctuation ? '，' : '') + value;
}

// 同步文本到特征选择器（文本→选项）
function syncTextToFeatures(text, featureBtns) {
  const characterForm = document.querySelector('form[data-lesson="character"]');
  if (!characterForm) return;
  
  const featureLabels = characterForm.querySelectorAll('.feature-label');
  
  // 清除所有激活状态
  featureBtns.forEach(btn => btn.classList.remove('active'));
  featureLabels.forEach(label => label.classList.remove('active'));
  
  // 遍历每个特征类别
  Object.keys(featureKeywords).forEach(feature => {
    const keywords = featureKeywords[feature];
    
    // 检查文本中是否包含该类别的任何关键词
    const hasFeature = keywords.some(keyword => text.includes(keyword));
    
    if (hasFeature) {
      // 类别标签高亮
      const label = characterForm.querySelector(`.feature-label[data-feature="${feature}"]`);
      if (label) {
        label.classList.add('active');
      }
      
      // 检查具体是哪个选项，对应按钮高亮
      const buttons = characterForm.querySelectorAll(`.feature-btn[data-feature="${feature}"]`);
      buttons.forEach(btn => {
        const value = btn.dataset.value;
        // 只有当文本明确包含该按钮的值时才高亮
        if (text.includes(value)) {
          btn.classList.add('active');
        }
      });
    }
  });
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
  initFeatureSelector();
});

// ========== AI优化逻辑 ==========

// 手动点击AI优化按钮
window.optimizePromptManually = async function(event) {
  console.log('🎯 AI优化按钮被点击');
  if (event) event.preventDefault();
  
  const button = event.target.closest('.ai-optimize-btn');
  const form = button.closest('form');
  const rawPromptTextarea = form.querySelector('textarea[name="raw_prompt"]');
  const optimizedPromptTextarea = form.querySelector('textarea[name="prompt"]');
  
  const rawText = rawPromptTextarea.value.trim();
  if (!rawText) {
    alert('请先输入原始提示词');
    return;
  }
  
  // 显示加载状态
  button.disabled = true;
  button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
  
  // 在右侧输入框显示提示
  optimizedPromptTextarea.value = '';
  optimizedPromptTextarea.placeholder = '✨ AI正在优化中...';
  
  try {
    await optimizePrompt(rawText, optimizedPromptTextarea, form);
    button.innerHTML = '<i class="fas fa-check"></i>';
    setTimeout(() => {
      button.disabled = false;
      button.innerHTML = '<i class="fas fa-magic"></i>';
    }, 2000);
  } catch (error) {
    console.error('AI优化失败:', error);
    button.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
    optimizedPromptTextarea.value = '';
    optimizedPromptTextarea.placeholder = '❌ 优化失败，请重试';
    setTimeout(() => {
      button.disabled = false;
      button.innerHTML = '<i class="fas fa-magic"></i>';
      optimizedPromptTextarea.placeholder = '点击左侧的AI优化按钮生成优化后的提示词...';
    }, 2000);
  }
};

// AI优化提示词函数
async function optimizePrompt(rawText, targetTextarea, form) {
  const lessonType = form.getAttribute('data-lesson');
  
  try {
    // 调用现有的 organize-prompt API
    const response = await fetch('/api/organize-prompt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        voice_input: rawText,
        child_mode: true,
        filter_fillers: true
      })
    });
    
    const data = await response.json();
    
    if (data.success && data.organized_prompt) {
      let optimized = data.organized_prompt;
      
      // 清除临时的loading提示
      targetTextarea.placeholder = '点击左侧的AI优化按钮生成优化后的提示词...';
      
      // 检查是否已经指定了国籍或地区
      const hasNationality = /外国|美国|日本|韩国|欧洲|英国|法国|德国|俄罗斯|印度|非洲|澳大利亚|加拿大|意大利|西班牙|巴西|墨西哥|阿拉伯|泰国|越南|新加坡|马来西亚|菲律宾/i.test(optimized);
      
      // 如果没有指定国籍，且提示词中包含人物相关的词，则添加"中国人"
      const hasPerson = /人|小朋友|孩子|儿童|少年|青年|男孩|女孩|学生|老师|机器人/i.test(optimized);
      
      if (!hasNationality && hasPerson && !optimized.includes('中国')) {
        optimized = '中国人形象，' + optimized;
      }
      
      // 根据课程类型添加侧重点描述
      if (lessonType === 'character') {
        optimized += '，纯白色背景，无其他元素，聚焦人物细节，正面人像，半身像';
      } else if (lessonType === 'action') {
        optimized += '，纯白色背景，无其他元素，聚焦动作表现，姿势清晰，全身像';
      } else if (lessonType === 'scene') {
        optimized += '，人物简化或无人物，重点展现场景细节，环境氛围';
      } else if (lessonType === 'practice') {
        optimized += '，完整画面，人物动作场景结合，色彩丰富';
      }
      
      targetTextarea.value = optimized;
    } else {
      // 如果API调用失败，直接使用原始文本加上课程特定的后缀
      let fallback = rawText;
      
      const hasNationality = /外国|美国|日本|韩国|欧洲|英国|法国|德国|俄罗斯|印度|非洲|澳大利亚|加拿大|意大利|西班牙|巴西|墨西哥|阿拉伯|泰国|越南|新加坡|马来西亚|菲律宾/i.test(fallback);
      const hasPerson = /人|小朋友|孩子|儿童|少年|青年|男孩|女孩|学生|老师|机器人/i.test(fallback);
      
      if (!hasNationality && hasPerson && !fallback.includes('中国')) {
        fallback = '中国人形象，' + fallback;
      }
      
      if (lessonType === 'character') {
        fallback += '，纯白色背景，无其他元素，聚焦人物细节，正面人像，半身像';
      } else if (lessonType === 'action') {
        fallback += '，纯白色背景，无其他元素，聚焦动作表现，姿势清晰，全身像';
      } else if (lessonType === 'scene') {
        fallback += '，人物简化或无人物，重点展现场景细节，环境氛围';
      } else if (lessonType === 'practice') {
        fallback += '，完整画面，人物动作场景结合，色彩丰富';
      }
      
      targetTextarea.value = fallback;
    }
  } catch (error) {
    console.error('优化提示词失败:', error);
    // 失败时也显示基本的优化版本
    let fallback = rawText;
    const hasNationality = /外国|美国|日本|韩国|欧洲|英国|法国|德国|俄罗斯|印度|非洲|澳大利亚|加拿大|意大利|西班牙|巴西|墨西哥|阿拉伯|泰国|越南|新加坡|马来西亚|菲律宾/i.test(fallback);
    const hasPerson = /人|小朋友|孩子|儿童|少年|青年|男孩|女孩|学生|老师|机器人/i.test(fallback);
    
    if (!hasNationality && hasPerson && !fallback.includes('中国')) {
      fallback = '中国人形象，' + fallback;
    }
    
    if (lessonType === 'character') {
      fallback += '，纯白色背景，无其他元素，聚焦人物细节，正面人像，半身像';
    } else if (lessonType === 'action') {
      fallback += '，纯白色背景，无其他元素，聚焦动作表现，姿势清晰，全身像';
    } else if (lessonType === 'scene') {
      fallback += '，人物简化或无人物，重点展现场景细节，环境氛围';
    } else if (lessonType === 'practice') {
      fallback += '，完整画面，人物动作场景结合，色彩丰富';
    }
    
    targetTextarea.value = fallback;
  }
}

document.querySelectorAll('.prompt-form').forEach(form => {
  form.querySelector('.generate-btn').addEventListener('click', async function() {
    let section = form.getAttribute('data-section');
    let lessonType = form.getAttribute('data-lesson'); // 获取课程类型：character, action, scene, practice
    let prompt = '';
    if (section === 'manual') {
      // 优先使用优化后的prompt（右侧框）
      const promptTextarea = form.querySelector('textarea[name="prompt"]');
      const rawPromptTextarea = form.querySelector('textarea[name="raw_prompt"]');
      
      prompt = promptTextarea ? promptTextarea.value.trim() : '';
      
      // 如果优化后的prompt为空，使用原始输入
      if (!prompt && rawPromptTextarea) {
        const rawPrompt = rawPromptTextarea.value.trim();
        if (rawPrompt) {
          console.log('⚠️ 没有AI优化内容，直接使用原始输入');
          // 直接使用原始输入，并添加课程特定后缀
          prompt = rawPrompt;
          
          // 检查是否已经指定了国籍或地区
          const hasNationality = /外国|美国|日本|韩国|欧洲|英国|法国|德国|俄罗斯|印度|非洲|澳大利亚|加拿大|意大利|西班牙|巴西|墨西哥|阿拉伯|泰国|越南|新加坡|马来西亚|菲律宾/i.test(prompt);
          const hasPerson = /人|小朋友|孩子|儿童|少年|青年|男孩|女孩|学生|老师|机器人/i.test(prompt);
          
          if (!hasNationality && hasPerson && !prompt.includes('中国')) {
            prompt = '中国人形象，' + prompt;
          }
          
          // 根据课程类型添加侧重点描述
          if (lessonType === 'character') {
            prompt += '，纯白色背景，无其他元素，聚焦人物细节，正面人像，半身像';
          } else if (lessonType === 'action') {
            prompt += '，纯白色背景，无其他元素，聚焦动作表现，姿势清晰，全身像';
          } else if (lessonType === 'scene') {
            prompt += '，人物简化或无人物，重点展现场景细节，环境氛围';
          } else if (lessonType === 'practice') {
            prompt += '，完整画面，人物动作场景结合，色彩丰富';
          }
        }
      }
      
      // prompt已经在AI优化时处理好了，或者使用了原始输入
    } else if (section === 'mix') {
      const themeInput = (form.theme && form.theme.value) ? form.theme.value.trim() : '';

      const hair = form.hair ? form.hair.value : '';
      const head = form.head ? form.head.value : '';
      const eyes = form.eyes ? form.eyes.value : '';
      const nose = form.nose ? form.nose.value : '';
      const clothes = form.clothes ? form.clothes.value : '';
      const action = form.action ? form.action.value : '';
      const scene = form.scene ? form.scene.value : '';

      const characterCore = [hair, head, eyes, nose].filter(Boolean).join('');
      const characterText = characterCore || clothes ? `一个${characterCore}${clothes ? `，穿着${clothes}` : ''}的人物` : '';

      const parts = [];
      if (characterText) parts.push(characterText);
      if (action) parts.push(`正在${action}`);
      if (scene) parts.push(`在${scene}`);

      const autoPrompt = parts.length ? `${parts.join('，')}，卡通插画，色彩丰富，适合儿童观看` : '';

      // 支持直接输入：
      // - 如果用户填了自由输入，就在自动组合基础上追加（或仅使用输入）
      // - 如果没填，就用自动组合生成一条完整提示词
      if (themeInput) {
        prompt = autoPrompt ? `${autoPrompt}，${themeInput}` : themeInput;
      } else {
        prompt = autoPrompt;
      }
    }

    const resultDiv = form.closest('.class-section')?.querySelector('.classroom-result');
    
    if (!resultDiv) {
      console.error('找不到结果窗口元素');
      return;
    }
    
    if (!prompt) {
      resultDiv.innerHTML = '<div class="error">请先输入提示词，再点击生成</div>';
      return;
    }
    
    // 初始化显示区域 - 4个占位符
    resultDiv.innerHTML = `
      <div class="classroom-result-inner">
        <div class="classroom-prompt">本次提示词：${escapeHtml(prompt)}</div>
        <div class="generated-images-grid">
          <div class="generated-image-item loading-placeholder" data-index="0">
            <img src="/static/image/pinecone-mascot.png" class="loading-logo" />
          </div>
          <div class="generated-image-item loading-placeholder" data-index="1">
            <img src="/static/image/pinecone-mascot.png" class="loading-logo" />
          </div>
          <div class="generated-image-item loading-placeholder" data-index="2">
            <img src="/static/image/pinecone-mascot.png" class="loading-logo" />
          </div>
          <div class="generated-image-item loading-placeholder" data-index="3">
            <img src="/static/image/pinecone-mascot.png" class="loading-logo" />
          </div>
        </div>
      </div>
    `;
    
    try {
      // 逐张生成图片
      for (let i = 0; i < 4; i++) {
        console.log(`📤 生成第 ${i+1}/4 张图片...`);
        
        const formData = new FormData();
        
        // 人物课使用素描风格，其他课程使用可爱卡通风格
        let finalPrompt = prompt;
        let styleToUse = 'cute';
        let colorPreference = 'colorful';
        
        if (lessonType === 'character') {
          // 人物课添加素描风格描述
          finalPrompt = prompt + '，黑白素描风格，铅笔手绘效果，线条清晰';
          styleToUse = 'realistic';  // 使用写实风格作为基础
          colorPreference = 'monochrome';  // 单色
        }
        
        formData.append('prompt', finalPrompt);
        formData.append('expert_mode', 'true');
        formData.append('style', styleToUse);
        formData.append('color_preference', colorPreference);
        formData.append('aspect_ratio', '1:1');
        formData.append('width', '512');  // 使用512x512快速生成
        formData.append('height', '512');
        formData.append('num_images', '1');  // 每次只生成1张
        
        const resp = await fetch('/api/generate-image', {
          method: 'POST',
          body: formData
        });

        let data;
        try {
          data = await resp.json();
        } catch (parseErr) {
          console.error('解析响应JSON失败', parseErr);
          // 只更新当前占位符为错误
          const placeholder = resultDiv.querySelector(`.loading-placeholder[data-index="${i}"]`);
          if (placeholder) {
            placeholder.innerHTML = '<div class="error-mini">生成失败</div>';
          }
          continue;
        }

        console.log(`✅ 第 ${i+1} 张图片响应:`, data);

        if (!resp.ok) {
          const serverMsg = data && data.error ? data.error : `服务器返回状态 ${resp.status}`;
          console.error('生成失败:', serverMsg);
          const placeholder = resultDiv.querySelector(`.loading-placeholder[data-index="${i}"]`);
          if (placeholder) {
            placeholder.innerHTML = '<div class="error-mini">生成失败</div>';
          }
          continue;
        }

        if (data.success && data.image_url) {
          // 更新对应的占位符
          const placeholder = resultDiv.querySelector(`.loading-placeholder[data-index="${i}"]`);
          if (placeholder) {
            placeholder.classList.remove('loading-placeholder');
            const imageUrl = `${data.image_url}?t=${Date.now()}`;
            placeholder.innerHTML = `
              <img src="${imageUrl}" alt="AI生成图片 ${i + 1}" class="ai-image-thumbnail" />
              <button class="image-print-btn" onclick="printImage('${data.image_url}')" title="打印这张图片">🖨️</button>
            `;
          }
        } else {
          const placeholder = resultDiv.querySelector(`.loading-placeholder[data-index="${i}"]`);
          if (placeholder) {
            placeholder.innerHTML = '<div class="error-mini">生成失败</div>';
          }
        }
      }
    } catch (e) {
      console.error('生成过程出错:', e);
      resultDiv.innerHTML = '<div class="error">生成失败，请检查网络或稍后再试</div>';
    }
  });
});

function escapeHtml(text) {
  return String(text)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

console.log('🚀 松果课堂JS加载完成');
console.log('✅ optimizePromptManually 已定义:', typeof window.optimizePromptManually);

// 全屏图片查看器
const ImageViewer = {
  viewer: null,
  overlay: null,
  closeBtn: null,
  prevBtn: null,
  nextBtn: null,
  counter: null,
  img: null,
  images: [],
  currentIndex: 0,
  touchStartX: 0,
  touchStartY: 0,
  doubleClickTimer: null,
  lastClickTime: 0,

  init() {
    this.viewer = document.getElementById('image-viewer');
    this.overlay = this.viewer.querySelector('.image-viewer-overlay');
    this.closeBtn = this.viewer.querySelector('.image-viewer-close');
    this.printBtn = this.viewer.querySelector('.image-viewer-print');
    this.prevBtn = this.viewer.querySelector('.image-viewer-prev');
    this.nextBtn = this.viewer.querySelector('.image-viewer-next');
    this.counter = this.viewer.querySelector('.image-viewer-counter');
    this.img = this.viewer.querySelector('.image-viewer-img');

    // 关闭按钮
    this.closeBtn.addEventListener('click', () => this.close());
    this.overlay.addEventListener('click', () => this.close());
    
    // 打印按钮
    this.printBtn.addEventListener('click', () => this.print());

    // 切换按钮
    this.prevBtn.addEventListener('click', () => this.navigate(-1));
    this.nextBtn.addEventListener('click', () => this.navigate(1));

    // 键盘导航
    document.addEventListener('keydown', (e) => {
      if (this.viewer.style.display !== 'none') {
        if (e.key === 'ArrowLeft') this.navigate(-1);
        if (e.key === 'ArrowRight') this.navigate(1);
        if (e.key === 'Escape') this.close();
      }
    });

    // 双击关闭
    this.img.addEventListener('click', (e) => {
      const now = Date.now();
      const timeDiff = now - this.lastClickTime;
      
      if (timeDiff < 300) {
        // 双击
        this.close();
      }
      this.lastClickTime = now;
    });

    // 触摸滑动
    this.img.addEventListener('touchstart', (e) => {
      this.touchStartX = e.touches[0].clientX;
      this.touchStartY = e.touches[0].clientY;
    });

    this.img.addEventListener('touchend', (e) => {
      const touchEndX = e.changedTouches[0].clientX;
      const touchEndY = e.changedTouches[0].clientY;
      const deltaX = touchEndX - this.touchStartX;
      const deltaY = touchEndY - this.touchStartY;

      // 水平滑动距离大于垂直滑动，且超过50px
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
        if (deltaX > 0) {
          this.navigate(-1); // 右滑显示上一张
        } else {
          this.navigate(1); // 左滑显示下一张
        }
      }
    });

    // 为生成的图片添加点击事件（使用事件委托）
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('ai-image-thumbnail')) {
        const allImages = document.querySelectorAll('.ai-image-thumbnail');
        this.images = Array.from(allImages).map(img => img.src);
        this.currentIndex = Array.from(allImages).indexOf(e.target);
        this.open(this.currentIndex);
      }
    });
  },

  open(index) {
    this.currentIndex = index;
    this.updateImage();
    this.viewer.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  },

  close() {
    this.viewer.style.display = 'none';
    document.body.style.overflow = '';
  },

  navigate(direction) {
    this.currentIndex = (this.currentIndex + direction + this.images.length) % this.images.length;
    this.updateImage();
  },

  updateImage() {
    this.img.src = this.images[this.currentIndex];
    this.counter.textContent = `${this.currentIndex + 1} / ${this.images.length}`;
    
    // 更新按钮显示状态
    this.prevBtn.style.display = this.images.length > 1 ? 'flex' : 'none';
    this.nextBtn.style.display = this.images.length > 1 ? 'flex' : 'none';
  },

  print() {
    printImage(this.images[this.currentIndex]);
  }
};

// 检测是否为移动设备
function isMobileDevice() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// 打印单张图片的辅助函数
async function printImage(imageSrc) {
  const isMobile = isMobileDevice();
  
  if (isMobile) {
    // 移动端：尝试使用分享API或直接下载
    try {
      // 先尝试获取图片作为Blob
      const response = await fetch(imageSrc);
      const blob = await response.blob();
      
      // 尝试使用Web Share API（如果支持）
      if (navigator.share && navigator.canShare && navigator.canShare({ files: [new File([blob], 'ai-image.png', { type: blob.type })] })) {
        const file = new File([blob], 'ai-image.png', { type: blob.type });
        await navigator.share({
          title: 'AI生成图片',
          text: '分享或打印这张图片',
          files: [file]
        });
      } else {
        // 降级方案：下载图片
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai-image-${Date.now()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // 提示用户
        showToast('图片已下载，请在相册中打开并使用系统打印功能', 'success');
      }
    } catch (error) {
      console.error('移动端打印失败:', error);
      // 最终降级方案：直接打开图片
      window.open(imageSrc, '_blank');
      showToast('已在新标签页打开图片，请使用浏览器菜单中的打印功能', 'info');
    }
  } else {
    // 桌面端：使用传统打印方式
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      alert('请允许弹出窗口以打印图片');
      return;
    }
    
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>打印图片</title>
        <style>
          body {
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
          }
          img {
            max-width: 100%;
            height: auto;
            display: block;
          }
          @media print {
            body {
              padding: 0;
            }
            img {
              max-width: 100%;
              page-break-inside: avoid;
            }
          }
        </style>
      </head>
      <body>
        <img src="${imageSrc}" onload="window.print();" />
      </body>
      </html>
    `);
    printWindow.document.close();
  }
}

// Toast提示函数（如果页面中没有的话）
function showToast(message, type = 'info') {
  // 检查是否已有Toast容器
  let toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    toastContainer.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 10000;
    `;
    document.body.appendChild(toastContainer);
  }
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.style.cssText = `
    background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    animation: slideIn 0.3s ease;
    max-width: 300px;
    word-wrap: break-word;
  `;
  toast.textContent = message;
  
  toastContainer.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => {
      toastContainer.removeChild(toast);
    }, 300);
  }, 4000);
}

// 初始化图片查看器
document.addEventListener('DOMContentLoaded', () => {
  ImageViewer.init();
});
