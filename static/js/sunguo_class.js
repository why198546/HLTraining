document.querySelectorAll('.prompt-form').forEach(form => {
  form.querySelector('.generate-btn').addEventListener('click', async function() {
    let section = form.getAttribute('data-section');
    let lessonType = form.getAttribute('data-lesson'); // 获取课程类型：character, action, scene, practice
    let prompt = '';
    if (section === 'manual') {
      const raw = (form.prompt && form.prompt.value) ? form.prompt.value.trim() : '';
      prompt = raw;
      
      // 检查提示词中是否已经指定了国籍或地区
      const hasNationality = /外国|美国|日本|韩国|欧洲|英国|法国|德国|俄罗斯|印度|非洲|澳大利亚|加拿大|意大利|西班牙|巴西|墨西哥|阿拉伯|泰国|越南|新加坡|马来西亚|菲律宾/i.test(prompt);
      
      // 如果没有指定国籍，且提示词中包含人物相关的词，则添加"中国人"
      const hasPerson = /人|小朋友|孩子|儿童|少年|青年|男孩|女孩|学生|老师|机器人/i.test(prompt);
      
      if (!hasNationality && hasPerson && !prompt.includes('中国')) {
        prompt = '中国人形象，' + prompt;
      }
      
      // 根据课程类型添加侧重点描述
      if (lessonType === 'character') {
        // 第一节课：人物，不要背景
        prompt += '，纯白色背景，无其他元素，聚焦人物细节，全身像';
      } else if (lessonType === 'action') {
        // 第二节课：动作，简单人物，重点表现动作，不要背景
        prompt += '，纯白色背景，无其他元素，聚焦动作表现，姿势清晰，全身像';
      } else if (lessonType === 'scene') {
        // 第三节课：场景，人物和动作简化，重点表现场景
        prompt += '，人物简化或无人物，重点展现场景细节，环境氛围';
      } else if (lessonType === 'practice') {
        // 综合练习：完整生成（人物+动作+场景）
        prompt += '，完整画面，人物动作场景结合，色彩丰富';
      }
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
    resultDiv.innerHTML = '<div class="loading"><img src="/static/image/pinecone-mascot.png" alt="松果吉祥物" class="loading-logo" /></div>';
    try {
      // 复用现有的统一生图接口 /generate-image（支持纯文字 prompt）
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('expert_mode', 'true');
      formData.append('style', 'cute');
      formData.append('color_preference', 'colorful');
      formData.append('aspect_ratio', '1:1');

      const resp = await fetch('/generate-image', {
        method: 'POST',
        body: formData
      });

      const data = await resp.json();
      console.log('松果课堂生成响应:', data);
      if (data.success && data.image_url) {
        console.log('图片URL:', data.image_url);
        resultDiv.innerHTML = `
          <div class="classroom-result-inner">
            <div class="classroom-prompt">本次提示词：${escapeHtml(prompt)}</div>
            <img src="${data.image_url}?t=${Date.now()}" alt="AI生成图片" class="ai-image" onerror="console.error('图片加载失败:', this.src)" onload="console.log('图片加载成功:', this.src)" />
          </div>
        `;
      } else {
        const errorMsg = data.error || '生成失败，请重试';
        console.error('生成失败:', errorMsg);
        resultDiv.innerHTML = `<div class="error">${escapeHtml(errorMsg)}</div>`;
      }
    } catch (e) {
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
