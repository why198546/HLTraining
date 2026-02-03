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
  if (event) event.preventDefault();
  
  const button = event.target.closest('.ai-optimize-btn');
  const form = button.closest('form');
  const rawPromptTextarea = form.querySelector('textarea[name="raw_prompt"]');
  const optimizedPromptTextarea = form.querySelector('textarea[name="prompt"]');
  
  // 检查是否有参考图片
  const hasReferenceImage = window.uploadedReferenceFile;
  
  // 如果有参考图片但没有原始输入，提取图片特征
  if (hasReferenceImage && !rawPromptTextarea.value.trim()) {
    
    // 显示加载状态
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    rawPromptTextarea.placeholder = '📷 正在识别图片中的人物特征...';
    optimizedPromptTextarea.placeholder = '✨ AI正在分析中...';
    
    try {
      // 调用图片分析API提取人物特征
      const formData = new FormData();
      formData.append('image', window.uploadedReferenceFile);
      
      const response = await fetch('/api/analyze-image-features', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (data.success && data.features) {
        // 将提取的特征填入原始输入框
        rawPromptTextarea.value = data.features;
        rawPromptTextarea.placeholder = '手动输入或语音转录';
        
        // 直接使用提取的特征作为优化后的提示词
        optimizedPromptTextarea.value = data.features;
        optimizedPromptTextarea.placeholder = '点击左侧的AI优化按钮生成优化后的提示词...';
        
        
        button.innerHTML = '<i class="fas fa-check"></i>';
        setTimeout(() => {
          button.disabled = false;
          button.innerHTML = '<i class="fas fa-magic"></i>';
        }, 2000);
        return;
      } else {
        throw new Error(data.message || '特征提取失败');
      }
    } catch (error) {
      hldebug.error('图片特征提取失败:', error);
      alert('图片特征提取失败，请手动输入特征描述');
      rawPromptTextarea.placeholder = '手动输入或语音转录';
      optimizedPromptTextarea.placeholder = '点击左侧的AI优化按钮生成优化后的提示词...';
      button.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
      setTimeout(() => {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-magic"></i>';
      }, 2000);
      return;
    }
  }
  
  const rawText = rawPromptTextarea.value.trim();
  if (!rawText) {
    alert('请先输入原始提示词或上传参考图片');
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
    hldebug.error('AI优化失败:', error);
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
    hldebug.error('优化提示词失败:', error);
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
      hldebug.error('找不到结果窗口元素');
      return;
    }
    
    // 如果有参考图但没有提示词，自动生成默认提示词
    let autoGeneratedPrompt = false;
    if (!prompt && window.uploadedReferenceFile) {
      autoGeneratedPrompt = true;
      if (lessonType === 'character') {
        // 人物课：把图片改成手绘风格
        prompt = '把这张图片改成黑白素描手绘风格';
      } else if (lessonType === 'action') {
        prompt = '把这张图片改成黑白素描手绘风格';
      } else if (lessonType === 'scene') {
        prompt = '把这张图片改成手绘线稿风格';
      } else {
        prompt = '把这张图片改成手绘风格';
      }
    }
    
    if (!prompt) {
      resultDiv.innerHTML = '<div class="error">请先输入提示词或上传参考图片</div>';
      return;
    }
    
    // 初始化显示区域 - 4个占位符
    resultDiv.innerHTML = `
      <div class="classroom-result-inner">
        <div class="classroom-prompt">本次提示词：${escapeHtml(prompt)}</div>
        <div class="generation-progress">正在逐张生成4张图片，请稍候...</div>
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
      // 改为顺序生成：一张接一张等待完成，确保每张图片真正不同
      
      // 10项特征定义（儿童形象生成的核心特征）
      // 特征类别映射（后端返回时用索引，这里用来显示名称）
      const featureNames = ['性别', '体型', '头发长度', '头发类型', '皮肤', '眼睛', '鼻子', '嘴巴', '嘴唇', '耳朵'];
      
      // 为每个特征定义多个变化选项（用于随机组合）
      const unspecifiedVariations = {
        0: ['男孩', '女孩'],  // 性别
        1: ['胖胖的', '瘦瘦的', '正常'],  // 体型
        2: ['长发', '短发'],  // 头发长度
        3: ['卷发', '直发'],  // 头发类型
        4: ['深色皮肤', '浅色皮肤'],  // 皮肤
        5: ['大眼睛', '小眼睛'],  // 眼睛
        6: ['大鼻子', '小鼻子'],  // 鼻子
        7: ['樱桃小嘴', '大嘴巴'],  // 嘴巴
        8: ['厚嘴唇', '薄嘴唇'],  // 嘴唇
        9: ['大耳朵', '小耳朵']  // 耳朵
      };
      
      // 常识规则：对生成的特征组合进行合理性检查
      // 避免出现"男孩长发"等不合理组合
      function applyCommonSenseRules(detectedFeatures, selectedVariations) {
        // 如果检测到了性别特征（feature 0），应用相应的头发长度约束
        if (detectedFeatures && detectedFeatures[0]) {
          const detectedGender = detectedFeatures[0];
          
          // 检查是否是男孩
          if (detectedGender.includes('男孩') || detectedGender.includes('男')) {
            // 男孩通常短发，所以移除可能被随机生成的"长发"
            selectedVariations = selectedVariations.filter(v => v !== '长发' && v !== '中长发' && v !== '齐肩发' && v !== '及肩');
          }
          
          // 检查是否是女孩
          if (detectedGender.includes('女孩') || detectedGender.includes('女')) {
            // 女孩通常长发，所以移除可能被随机生成的"短发"
            selectedVariations = selectedVariations.filter(v => v !== '短发');
          }
        }
        
        // 常识规则：中国人卷发相对较少，只有30%的概率出现卷发（70%概率移除）
        // 这样可以偶尔生成一两次卷发，但不会过于频繁
        if (Math.random() < 0.7) {
          selectedVariations = selectedVariations.filter(v => v !== '卷发' && v !== '微卷发');
        }
        
        return selectedVariations;
      }
      
      // 为每张图随机生成未指定特征的组合
      function getRandomVariations(detectedFeatures) {
        // detectedFeatures 是后端返回的字典，如 {0: '男孩', 5: '大眼睛', ...}
        const specifiedFeatureIndices = new Set(Object.keys(detectedFeatures).map(k => parseInt(k)));
        
        const unspecifiedIndices = Object.keys(unspecifiedVariations)
          .map(idx => parseInt(idx))
          .filter(idx => !specifiedFeatureIndices.has(idx));
        
        // 只随机选择2-3个特征变化（避免每张都变，差异过大）
        const selectedCount = Math.random() < 0.5 ? 2 : 3;
        const selectedIndices = [];
        
        // 随机打乱并选择
        const tempIndices = [...unspecifiedIndices];
        for (let i = 0; i < Math.min(selectedCount, tempIndices.length); i++) {
          const randomIdx = Math.floor(Math.random() * (tempIndices.length - i));
          const selected = tempIndices[randomIdx];
          selectedIndices.push(selected);
          
          // 移除已选中的特征
          tempIndices.splice(randomIdx, 1);
        }
        
        // 为选中的特征随机选择一个变化
        let variations = [];
        for (const featureIdx of selectedIndices) {
          const options = unspecifiedVariations[featureIdx];
          if (options && options.length > 0) {
            const randomOption = options[Math.floor(Math.random() * options.length)];
            variations.push(randomOption);
          }
        }
        
        // 应用常识规则，移除矛盾的特征组合
        variations = applyCommonSenseRules(detectedFeatures, variations);
        
        return variations;
      }
      
      const seeds = [100, 200, 300, 400];
      const temperatures = [0.9, 1.1, 1.3, 1.5];  // 温和的temperature范围
      
      // 第一次请求：先生成一张，获取后端的特征检测结果
      let detectedFeatures = {};
      
      // 顺序生成而不是并发，确保每张图片真正不同（避免缓存/相似问题）
      for (let i = 0; i < 4; i++) {
        const formData = new FormData();
        
        // 人物课使用素描风格，其他课程使用可爱卡通风格
        let finalPrompt = prompt;
        let styleToUse = 'cute';
        let colorPreference = 'colorful';
        
        if (lessonType === 'character') {
          // 如果有参考图片
          if (window.uploadedReferenceFile) {
            // 根据是否有用户输入的特征描述，生成不同的提示词
            const userFeatures = (!autoGeneratedPrompt && prompt) ? `，特别强化以下特征：${prompt}` : '';
            
            // 四张图使用相同的基础格式（正面、素描、纯白背景）
            // 在用户未描述的特征上加入适当变化
            switch(i) {
              case 0:
                // 第一张：基础版本
                finalPrompt = `提取图片中的人物主体，正面人像，纯白色背景，无其他元素，聚焦人物细节，半身像，黑白素描风格${userFeatures}`;
                styleToUse = 'none';
                colorPreference = 'monochrome';
                break;
              case 1:
                // 第二张：不同的表情/姿态
                finalPrompt = `提取图片中的人物主体，正面人像，纯白色背景，无其他元素，聚焦人物细节，半身像，黑白素描风格，展现不同的表情或姿态${userFeatures}`;
                styleToUse = 'none';
                colorPreference = 'monochrome';
                break;
              case 2:
                // 第三张：不同的表情/衣着
                finalPrompt = `提取图片中的人物主体，正面人像，纯白色背景，无其他元素，聚焦人物细节，半身像，黑白素描风格，展现不同的衣着或装饰${userFeatures}`;
                styleToUse = 'none';
                colorPreference = 'monochrome';
                break;
              case 3:
                // 第四张：上色版本，丰富的配色
                finalPrompt = `提取图片中的人物主体，正面人像，纯白色背景，无其他元素，聚焦人物细节，半身像，色彩丰富的卡通风格，充满活力的配色${userFeatures}`;
                styleToUse = 'none';
                colorPreference = 'colorful';
                break;
            }
          } else {
            // 没有参考图片，手工输入的提示词，添加素描风格描述
            finalPrompt = prompt + '，黑白素描风格，铅笔手绘效果，线条清晰';
            styleToUse = 'realistic';  // 使用写实风格作为基础
            colorPreference = 'monochrome';  // 单色
          }
        }
        
        // 为每张图添加未指定特征的随机组合变化
        // 如果还没有获取检测特征，则跳过（第一张请求时获取）
        let randomVariations = [];
        if (i === 0) {
          // 第一张图：暂时不加随机特征，等响应后获取detected_features
          randomVariations = [];
        } else if (Object.keys(detectedFeatures).length > 0) {
          // 后续图片：使用后端返回的特征进行随机组合
          randomVariations = getRandomVariations(detectedFeatures);
        }
        
        let promptWithVariations = finalPrompt;
        
        if (randomVariations.length > 0) {
          // 在prompt开头（方括号中）明确指出随机特征，让模型更重视
          const variationStr = randomVariations.join('，');
          promptWithVariations = `[${variationStr}]${finalPrompt}，特别体现以上特征`;
        }
        
        formData.append('prompt', promptWithVariations);
        formData.append('expert_mode', 'true');
        formData.append('style', styleToUse);
        formData.append('color_preference', colorPreference);
        formData.append('aspect_ratio', '2:3');  // A4纸张比例（竖版）
        formData.append('width', '512');
        formData.append('height', '768');  // 512x768用于A4打印
        formData.append('num_images', '1');  // 每次只生成1张
        formData.append('temperature', temperatures[i].toString());  // 为每张图应用不同的temperature
        formData.append('top_p', '0.95');  // 官方默认值
        formData.append('seed', seeds[i].toString());  // 为每张图应用不同的seed
        
        // 保存这次请求的参数（用于调试显示）
        const requestParams = {
          prompt: promptWithVariations,
          temperature: temperatures[i],
          top_p: 0.95,
          seed: seeds[i],
          style: styleToUse,
          aspect_ratio: '2:3',
          width: '512',
          height: '768'
        };
        
        // 如果有参考图片，添加到formData（使用sketch字段名）
        if (window.uploadedReferenceFile) {
          formData.append('sketch', window.uploadedReferenceFile);
        }
        
        // 顺序生成：逐张等待完成（不使用Promise.all）
        let resp;
        try {
          resp = await fetch('/api/generate-image', {
            method: 'POST',
            body: formData
          });
        } catch (error) {
          hldebug.error(`第${i + 1}张生成失败:`, error);
          const placeholder = resultDiv.querySelector(`.loading-placeholder[data-index="${i}"]`);
          if (placeholder) {
            placeholder.innerHTML = `<div class="error-mini">生成失败</div>
              <div class="debug-params">参数: T=${requestParams.temperature}, seed=${requestParams.seed}</div>`;
          }
          continue;
        }
        
        // 处理响应
        let data;
        try {
          data = await resp.json();
        } catch (parseErr) {
          hldebug.error('解析响应JSON失败', parseErr);
          const placeholder = resultDiv.querySelector(`.loading-placeholder[data-index="${i}"]`);
          if (placeholder) {
            placeholder.innerHTML = `<div class="error-mini">生成失败</div>
              <div class="debug-params">参数: T=${requestParams.temperature}, seed=${requestParams.seed}</div>`;
          }
          continue;
        }

        // 在第一张请求时保存后端返回的检测特征
        if (i === 0 && data.detected_features) {
          detectedFeatures = data.detected_features;
          // hldebug.error(`📍 从后端获取检测特征: ${JSON.stringify(detectedFeatures)}`);
        }

        if (!resp.ok) {
          const serverMsg = data && data.error ? data.error : `服务器返回状态 ${resp.status}`;
          hldebug.error('生成失败:', serverMsg);
          const placeholder = resultDiv.querySelector(`.loading-placeholder[data-index="${i}"]`);
          if (placeholder) {
            placeholder.innerHTML = `<div class="error-mini">生成失败</div>
              <div class="debug-params">参数: T=${requestParams.temperature}, seed=${requestParams.seed}</div>`;
          }
          continue;
        }

        if (data.success && data.image_url) {
          // 更新对应的占位符
          const placeholder = resultDiv.querySelector(`.loading-placeholder[data-index="${i}"]`);
          if (placeholder) {
            placeholder.classList.remove('loading-placeholder');
            const imageUrl = `${data.image_url}?t=${Date.now()}`;
            
            // 生成参数显示文本
            const paramsText = requestParams ? `prompt: ${requestParams.prompt.substring(0, 100)}...
temperature: ${requestParams.temperature}
top_p: ${requestParams.top_p}
seed: ${requestParams.seed}` : '';
            
            placeholder.innerHTML = `
              <img src="${imageUrl}" alt="AI生成图片 ${i + 1}" class="ai-image-thumbnail" data-index="${i}" data-image-url="${data.image_url}" />
              <button class="image-print-btn" data-image-url="${data.image_url}" type="button" title="打印这张图片">🖨️</button>
              <button class="debug-params-toggle" type="button" title="查看API参数">P</button>
              <div class="debug-params" style="display: none;">${escapeHtml(paramsText)}</div>
            `;
            
            // 为这个P按钮立即添加事件监听（每张完成时）
            const toggleBtn = placeholder.querySelector('.debug-params-toggle');
            const paramsDiv = placeholder.querySelector('.debug-params');
            if (toggleBtn && paramsDiv) {
              // 悬停展开
              toggleBtn.addEventListener('mouseenter', () => {
                paramsDiv.style.display = 'block';
              });
              
              // 鼠标离开隐藏
              toggleBtn.addEventListener('mouseleave', () => {
                paramsDiv.style.display = 'none';
              });
              
              // 点击切换
              toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = paramsDiv.style.display !== 'none';
                paramsDiv.style.display = isVisible ? 'none' : 'block';
              });
            }
          }
        } else {
          const placeholder = resultDiv.querySelector(`.loading-placeholder[data-index="${i}"]`);
          if (placeholder) {
            placeholder.innerHTML = `<div class="error-mini">生成失败</div>
              <div class="debug-params">参数: T=${requestParams.temperature}, seed=${requestParams.seed}</div>`;
          }
        }
      }
      
      // 全部完成后隐藏进度提示
      const progressDiv = resultDiv.querySelector('.generation-progress');
      if (progressDiv) {
        progressDiv.style.display = 'none';
      }
      
      // 点击页面其他地方时隐藏参数
      document.addEventListener('click', () => {
        const allParamsDivs = resultDiv.querySelectorAll('.debug-params');
        allParamsDivs.forEach(paramsDiv => {
          paramsDiv.style.display = 'none';
        });
      });
    } catch (e) {
      hldebug.error('生成过程出错:', e);
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
    
    // ⚠️ 重要：检查viewer是否存在
    if (!this.viewer) {
      hldebug.error('❌ 找不到 #image-viewer 元素');
      return;
    }
    
    this.overlay = this.viewer.querySelector('.image-viewer-overlay');
    this.closeBtn = this.viewer.querySelector('.image-viewer-close');
    this.printBtn = this.viewer.querySelector('.image-viewer-print');
    this.prevBtn = this.viewer.querySelector('.image-viewer-prev');
    this.nextBtn = this.viewer.querySelector('.image-viewer-next');
    this.counter = this.viewer.querySelector('.image-viewer-counter');
    this.img = this.viewer.querySelector('.image-viewer-img');

    // 检查所有元素是否存在
    if (!this.overlay || !this.closeBtn || !this.img) {
      hldebug.error('❌ 图片查看器的某些元素未找到');
      return;
    }

    // 关闭按钮
    this.closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      this.close();
    });
    
    this.overlay.addEventListener('click', (e) => {
      e.stopPropagation();
      this.close();
    });
    
    // 双击图片退出viewer
    this.img.addEventListener('dblclick', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.close();
    }, { passive: false });
    
    // 打印按钮
    if (this.printBtn) {
      this.printBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.print();
      });
    }

    // 切换按钮
    if (this.prevBtn) {
      this.prevBtn.addEventListener('click', (e) => {
        console.log('⬅️ 点击上一张按钮', e);
        e.stopPropagation();
        e.preventDefault();
        this.navigate(-1);
      });
    }
    
    if (this.nextBtn) {
      this.nextBtn.addEventListener('click', (e) => {
        console.log('➡️ 点击下一张按钮', e);
        e.stopPropagation();
        e.preventDefault();
        this.navigate(1);
      });
    }

    // 键盘导航
    document.addEventListener('keydown', (e) => {
      // 只在查看器可见时处理键盘事件
      if (this.viewer.classList.contains('active')) {
        if (e.key === 'ArrowLeft') {
          e.preventDefault();
          this.navigate(-1);
        }
        if (e.key === 'ArrowRight') {
          e.preventDefault();
          this.navigate(1);
        }
        if (e.key === 'Escape') {
          e.preventDefault();
          this.close();
        }
      }
    });

    // 触摸事件：左右滑动切换图片
    this.img.addEventListener('touchstart', (e) => {
      this.touchStartX = e.touches[0].clientX;
      this.touchStartY = e.touches[0].clientY;
    }, { passive: true });

    this.img.addEventListener('touchend', (e) => {
      if (this.touchStartX === 0) return;
      
      const touchEndX = e.changedTouches[0].clientX;
      const touchEndY = e.changedTouches[0].clientY;
      const deltaX = touchEndX - this.touchStartX;
      const deltaY = touchEndY - this.touchStartY;


      // 判断是否为左右滑动（水平距离 > 垂直距离，且超过50px阈值）
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
        e.preventDefault();
        
        if (deltaX > 0) {
          // 右滑 → 显示上一张
          this.navigate(-1);
        } else {
          // 左滑 → 显示下一张
          this.navigate(1);
        }
        
        this.touchStartX = 0;
        this.touchStartY = 0;
      }
    }, { passive: false });

    // ⚠️ 重要改动：移除img元素上的所有点击事件监听
    // 原因：这些监听器会与外层的委托事件冲突，导致页面冻结
    // 所有交互都通过viewer层级的委托事件处理（见DOMContentLoaded部分）
    
  },

  open(index) {
    
    if (!this.images || this.images.length === 0) {
      hldebug.error('❌ 没有可查看的图片');
      return;
    }
    
    this.currentIndex = Math.min(index, this.images.length - 1);
    
    // ⚠️ 关键改进：使用class切换和RAF，避免竞态条件
    setTimeout(() => {
      // 第1步：添加active class（显示查看器）
      this.viewer.classList.add('active');
      document.body.style.overflow = 'hidden';
      
      // 第2步：在RAF中加载图片，确保在viewer显示之后
      requestAnimationFrame(() => {
        this.updateImage();
      });
      
    }, 0);
  },

  close() {
    
    // 移除active class（隐藏查看器）
    this.viewer.classList.remove('active');
    document.body.style.overflow = '';
    
    // 清理资源
    setTimeout(() => {
      this.currentIndex = 0;
      this.images = [];
    }, 300); // 等待CSS动画完成（可选）
  },

  navigate(direction) {
    if (!this.images || this.images.length === 0) {
      console.log('❌ navigate: 没有图片');
      return;
    }
    
    const prevIndex = this.currentIndex;
    this.currentIndex = (this.currentIndex + direction + this.images.length) % this.images.length;
    
    console.log(`🔄 导航: ${prevIndex} → ${this.currentIndex} (共 ${this.images.length} 张)`);
    
    // 只在确实改变时更新
    if (prevIndex !== this.currentIndex) {
      this.updateImage();
    }
  },

  updateImage() {
    try {
      if (!this.images || this.images.length === 0) {
        return;
      }
      
      const currentSrc = this.images[this.currentIndex];
      if (!currentSrc) {
        hldebug.error('❌ 无效的图片索引:', this.currentIndex);
        return;
      }
      
      // 第一层RAF：准备URL
      requestAnimationFrame(() => {
        // 只对 HTTP/HTTPS URL 添加缓存参数，不要改 Data URL
        let urlWithCache = currentSrc;
        if (!currentSrc.startsWith('data:') && !currentSrc.startsWith('blob:')) {
          // 这是一个 HTTP URL，添加缓存破坏参数
          urlWithCache = currentSrc.includes('?') 
            ? currentSrc + '&t=' + Date.now()
            : currentSrc + '?t=' + Date.now();
        }
        
        // 第二层RAF：实际赋值，确保不阻塞渲染
        requestAnimationFrame(() => {
          this.img.src = urlWithCache;
          
          // 计数器更新
          if (this.counter) {
            this.counter.textContent = `${this.currentIndex + 1} / ${this.images.length}`;
          }
          
          // 更新按钮显示状态
          if (this.prevBtn) {
            this.prevBtn.style.display = this.images.length > 1 ? 'flex' : 'none';
          }
          if (this.nextBtn) {
            this.nextBtn.style.display = this.images.length > 1 ? 'flex' : 'none';
          }
          
        });
      });
    } catch (error) {
      hldebug.error('❌ 更新图片时出错:', error);
    }
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
      hldebug.error('移动端打印失败:', error);
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
  
  // ==================== 简化的单一事件委托 ====================
  // 使用最简单的逻辑：检查点击目标是什么，然后处理
  document.addEventListener('click', (e) => {
    const target = e.target;
    const printBtn = target.closest('.image-print-btn');
    const thumbnail = target.closest('.ai-image-thumbnail');
    
    // 情况1：点击了打印按钮
    if (printBtn) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      
      const imageUrl = printBtn.dataset.imageUrl;
      if (imageUrl) {
        printImage(imageUrl);
      }
      return;
    }
    
    // 情况2：点击了图片（但不是打印按钮）
    if (thumbnail && !printBtn) {
      e.preventDefault();
      e.stopPropagation();
      
      // ⚠️ 关键：使用setTimeout异步处理，避免在事件处理器中阻塞
      setTimeout(() => {
        const allImages = document.querySelectorAll('.ai-image-thumbnail');
        if (allImages.length > 0) {
          ImageViewer.images = Array.from(allImages).map(img => img.src);
          ImageViewer.currentIndex = Array.from(allImages).indexOf(thumbnail);
          
          
          if (ImageViewer.currentIndex >= 0 && ImageViewer.currentIndex < ImageViewer.images.length) {
            ImageViewer.open(ImageViewer.currentIndex);
          }
        }
      }, 0);
      
      return;
    }
  }, false); // 单一冒泡监听器
});




