document.querySelectorAll('.prompt-form').forEach(form => {
  form.querySelector('.generate-btn').addEventListener('click', async function() {
    let section = form.getAttribute('data-section');
    let prompt = '';
    if (section === 'manual') {
      const raw = (form.prompt && form.prompt.value) ? form.prompt.value.trim() : '';
      prompt = raw;
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

    const resultDiv = document.getElementById('classroom-result');
    if (!prompt) {
      resultDiv.innerHTML = '<div class="error">请先输入提示词，再点击生成</div>';
      return;
    }
    resultDiv.innerHTML = '<div class="loading">AI正在生成图片，请稍候...</div>';
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
