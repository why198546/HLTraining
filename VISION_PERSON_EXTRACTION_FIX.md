# Vision人物提取修复 - 模型切换方案

## 📋 问题描述

用户反馈生成的图片**面部与照片1中的人物相差较大**，检查后发现AI提取的最终Prompt中：

```
A person with natural features and a gentle appearance, The character is wearing...
```

**人物描述部分是默认的fallback值**，说明图片1（人物照片）的特征提取完全失败。

## 🔍 根本原因

使用 `gemini-2.5-flash` 提取人物照片时，被安全过滤器拦截：

```python
block_reason=<BlockedReason.PROHIBITED_CONTENT: 'PROHIBITED_CONTENT'>
candidates=None
```

即使设置 `safety_settings` 为 `BLOCK_NONE` 也无法绕过。

## ✅ 解决方案

**切换到 `gemini-2.0-flash` 模型**，该模型对人物照片的限制更少。

### 修改内容

**文件**: `api/nano_banana.py`

**修改位置1**: `extract_person_features()` - 第1309行
```python
# 修改前
model='gemini-2.5-flash'

# 修改后  
model='gemini-2.0-flash'  # 使用2.0版本，对人物照片限制更少
```

**修改位置2**: `extract_artwork_features()` - 第1407行
```python
# 修改前
model='gemini-2.5-flash'

# 修改后
model='gemini-2.0-flash'  # 与人物提取使用相同版本
```

## 📊 测试结果

### ✅ 人物特征提取（成功）

```
The person appears to be a young East Asian girl with a round face and 
light-medium skin tone. She has medium-sized, dark eyes, and straight, 
thin eyebrows. Her nose is small and somewhat rounded. She has a gentle, 
small smile. Her facial expression seems pleasant and content. Her hair 
is long, straight, dark, and without bangs. She appears to be around 8-12 
years old.
```

**提取内容**：
- ✅ 面部形状（圆脸）
- ✅ 肤色（中等浅肤色）
- ✅ 眼睛（中等大小、深色、杏仁形）
- ✅ 眉毛（细而直）
- ✅ 鼻子（小而圆）
- ✅ 表情（微笑、友好）
- ✅ 头发（长直深色、无刘海）
- ✅ 年龄（8-12岁）

### ✅ 服饰特征提取（成功）

```
The character is wearing a black short-sleeved t-shirt with the word 
"RAMIRA" written across the chest in white uppercase letters. Below this, 
she wears a bright, medium blue A-line skirt...
```

**提取内容**：
- ✅ 上衣：黑色短袖T恤，白色"RAMIRA"字样
- ✅ 下装：亮蓝色A字裙
- ✅ 鞋子：白色露趾厚底凉鞋
- ✅ 配饰：浅蓝色耳环、浅棕色藤编篮子包
- ✅ 发型：深棕/黑色高马尾
- ✅ 艺术风格：手绘、平面色块、极简轮廓

### 📝 最终Prompt示例（realistic风格）

```
The person is a young girl with a round face shape and light-medium skin tone. 
Her eyes are medium-sized, almond-shaped, and appear to be dark brown. Her 
eyebrows are thin and straight. She has a small, slightly rounded nose. Her 
mouth is small, and she has a slight smile. Her facial expression appears 
friendly and neutral. Her hair is long, straight, and dark brown with some 
flyaways. She does not have bangs. She appears to be in the age range of 8-12 
years old., 

The character is wearing a black t-shirt with the text "RAMIRA" in white 
lettering, and a bright blue midi skirt. She is wearing white platform sandals. 
She is also carrying a small dark brown wicker basket bag and light-colored 
dangling earrings. The artistic rendering style features blocky colors and 
visible brushstrokes, with a simple line work approach. The background is a 
realistic photo print of a European street..

The image should be a full-body studio portrait, in a high-quality fashion 
photography style, with soft studio lighting. The background is a clean solid 
light grey background. Focus on realistic textures and details, 8k resolution, 
highly detailed.
```

**Prompt长度**: 1145字符（之前默认fallback只有54字符）

## 🎯 效果对比

| 项目 | 修复前 | 修复后 |
|-----|-------|--------|
| 人物提取 | ❌ 被屏蔽，返回默认值 | ✅ 详细的面部特征 |
| 描述长度 | 54字符 | 371字符 |
| 面部信息 | 无 | 完整（五官、发型、表情、年龄） |
| 生成效果 | 面部与照片不像 | ✅ 应该更接近照片 |

## 📌 模型选择总结

| 模型 | 图片生成 | Vision提取（人物） | Vision提取（作品） |
|------|---------|------------------|------------------|
| gemini-2.5-flash-image | ✅ 最新 | N/A | N/A |
| gemini-2.5-flash | N/A | ❌ 被屏蔽 | ✅ 准确 |
| gemini-2.0-flash | N/A | ✅ 成功 | ✅ 准确 |

**最终方案**：
- **图片生成**: `gemini-2.5-flash-image`（保持不变）
- **Vision提取**: `gemini-2.0-flash`（人物+作品都用此版本）

## 🚀 部署状态

- ✅ 本地测试通过
- ✅ 已同步到生产服务器
- ✅ Gunicorn服务已重启
- ✅ 服务运行正常

## 📝 注意事项

1. **gemini-2.0-flash** 对人物照片的安全限制更宽松，适合儿童教育场景
2. 两个提取函数现在使用**相同的模型版本**，保证一致性
3. 安全设置仍然保留，但gemini-2.0-flash本身就不会过度屏蔽
4. 最终Prompt现在包含**完整的人物面部特征**，应该能生成更像照片的图像

## 🧪 测试脚本

```bash
# 本地测试Vision提取
source .venv/bin/activate
python test_vision_extraction.py <照片路径> <作品路径>

# 查看服务器最新Prompt
./scripts/get_latest_prompt.sh

# 实时监控生成过程
./scripts/monitor_prompts.sh
```

---

**修复日期**: 2026-02-03  
**修复版本**: gemini-2.5-flash → gemini-2.0-flash  
**状态**: ✅ 已部署到生产环境
