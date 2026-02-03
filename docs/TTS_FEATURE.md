# AI点评语音播放功能 (TTS)

## 功能概述

为AI老师点评添加了语音播放功能，使用Gemini TTS模型将文字点评转换为语音，让孩子们可以听到温柔的AI老师声音。

---

## 技术实现

### 使用的TTS模型

1. **gemini-2.5-flash-preview-tts** (默认)
   - ✅ 中文支持优秀
   - ✅ 价格便宜（是Pro模型的一半）
   - ✅ 速度快
   - 推荐用于生产环境

2. **gemini-2.5-pro-preview-tts** (备用)
   - 更高质量
   - 价格贵一倍
   - 可通过参数切换

### 支持的语音角色

Gemini TTS提供多种语音选择：

- **Puck** (默认) - 温柔女声，适合给孩子讲解
- **Kore** - 活泼女声
- **Aoede** - 柔和女声
- **Charon** - 稳重男声
- **Fenrir** - 年轻男声

---

## 代码结构

### 1. TTS服务模块
**文件**: `api/tts_service.py`

```python
# 核心方法
class TTSService:
    def text_to_speech_gemini(text, model, voice_name)
    def generate_feedback_audio(feedback_text, teacher_id, use_pro_model, voice_name)
```

**功能**:
- 初始化Gemini客户端
- 调用TTS API生成语音
- 返回base64编码的音频数据

### 2. 后端API
**文件**: `app/routes/formal_lesson.py`

**接口**: `POST /api/artwork-feedback`

**新增参数**:
- `enable_tts`: 是否生成语音（默认true）

**新增返回字段**:
```json
{
  "audio": "base64编码的音频数据",
  "has_audio": true,
  "tts_model": "gemini-2.5-flash-preview-tts",
  "tts_voice": "Puck"
}
```

### 3. 前端实现
**文件**: `templates/sunguo_formal_lesson.html`

**UI组件**:
- 🔊 播放语音按钮（金黄色）
- 暂停/播放状态切换
- 音量图标动画效果

**JavaScript功能**:
```javascript
// 音频播放控制
function toggleAudio()

// 自动显示音频按钮
if (data.has_audio && data.audio) {
  audioElement.src = 'data:audio/mp3;base64,' + data.audio;
  audioPlayBtn.style.display = 'inline-block';
}
```

---

## 使用流程

### 学生端使用

1. **上传作品**
   - 点击"上传作品"按钮
   - 选择作品图片

2. **等待分析**
   - AI Vision分析图片内容
   - 生成个性化点评文字
   - TTS生成语音（约2-5秒）

3. **查看/收听点评**
   - 阅读文字点评
   - 点击"🔊 播放语音"听AI老师讲解
   - 可随时暂停/继续播放

### 教师端管理

未来可扩展：
- 选择不同语音角色
- 上传教师语音样本（声音克隆）
- 自定义语速和音调

---

## 配置说明

### 环境变量
需要在`.env`文件中配置：

```env
# Gemini API密钥（必需）
GEMINI_API_KEY=your_gemini_api_key_here
```

### 模型选择

在`formal_lesson.py`中修改：

```python
# 使用Flash模型（推荐）
audio_result = tts.generate_feedback_audio(
    feedback_text=feedback,
    use_pro_model=False,  # False=Flash, True=Pro
    voice_name='Puck'
)
```

### 语音角色

在调用时指定：

```python
voice_name='Puck'   # 温柔女声（默认）
voice_name='Kore'   # 活泼女声
voice_name='Charon' # 稳重男声
```

---

## 性能优化

### 1. 文本预处理
```python
# 清理emoji和特殊符号
clean_text = re.sub(r'[🌟✨💡🎯💪🔥❤️👍]', '', feedback_text)

# 长度限制（防止超时）
if len(clean_text) > 5000:
    clean_text = clean_text[:5000] + "..."
```

### 2. 异步处理
- Vision分析和TTS生成顺序执行
- 总耗时约5-10秒
- 前端显示loading状态

### 3. 错误降级
- 如果TTS失败，仍返回文字点评
- `has_audio=false`时隐藏播放按钮

---

## 未来扩展

### 1. 声音克隆（待实现）
使用教师的声音样本训练自定义语音：
- 上传5-10分钟清晰录音
- 使用Custom Neural Voice
- 每位教师有独特声音

### 2. 多语言支持
- 英语点评配英文TTS
- 其他语言扩展

### 3. 语音交互
- 学生语音提问
- AI语音回答
- 实时对话

### 4. 离线缓存
- 常用点评预生成音频
- 本地缓存减少API调用

---

## API成本

### Gemini TTS定价（参考）

- **Flash模型**: $0.025/1K字符
- **Pro模型**: $0.05/1K字符

### 示例成本计算

一条点评约500字符：
- Flash: $0.0125/条
- Pro: $0.025/条

1000条点评：
- Flash: $12.5
- Pro: $25

**建议**: 生产环境使用Flash模型，中文效果已经很好。

---

## 故障排查

### 问题1: 音频按钮不显示
- 检查`has_audio`是否为true
- 查看后端日志TTS是否生成成功
- 验证GEMINI_API_KEY是否配置

### 问题2: 音频无法播放
- 检查浏览器控制台错误
- 验证base64数据是否完整
- 测试音频格式兼容性

### 问题3: TTS生成慢
- 检查网络连接
- 考虑使用Flash模型
- 减少文本长度

---

## 开发日志

**2026-02-03**
- ✅ 集成Gemini TTS API
- ✅ 添加语音播放UI
- ✅ 实现播放/暂停控制
- ✅ 优化音频按钮样式
- ✅ 添加错误处理和降级

---

## 相关文件

- `api/tts_service.py` - TTS服务实现
- `app/routes/formal_lesson.py` - 点评接口
- `templates/sunguo_formal_lesson.html` - 前端页面
- `docs/TTS_FEATURE.md` - 本文档

---

## 测试建议

1. **基础测试**
   - 上传作品 → 获得点评 → 播放语音
   - 验证文字和语音内容一致

2. **边界测试**
   - 超长文本（>5000字符）
   - 包含emoji的文本
   - 网络异常情况

3. **用户体验**
   - 音频质量评估
   - 语速是否适合儿童
   - UI交互流畅度

---

**功能状态**: ✅ 已完成并可用
**维护人员**: AI Development Team
**更新日期**: 2026-02-03
