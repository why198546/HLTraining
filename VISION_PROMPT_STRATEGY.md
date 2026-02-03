# Vision提取 + 固定模板 Prompt策略

## 📋 核心策略

**Vision + 固定风格Prompt + 变量插入**

这个策略在自动化和灵活度之间取得了完美平衡，既能保证输出质量的一致性，又能适应不同的输入图片。

---

## 🎯 三步工作流程

### 第一步：Vision提取（API调用）

#### 1.1 人物照片分析
**目标**：提取面部特征，作为人物的"基底"描述

**Vision Prompt**:
```
Describe this person's appearance in natural language, focusing on:
- Facial features (face shape, skin tone, eyes, nose, mouth, expression)
- Hair (style, color, texture, bangs if any)
- Approximate age range
- General impression

Provide a concise, continuous description suitable for image generation prompts. 
Avoid mentioning background, clothing, or body posture.
```

**返回示例**:
```
"A young East Asian girl with long, straight dark brown hair, round eyes, 
a small nose, and a cheerful smile. She appears to be around 8-12 years old."
```

#### 1.2 手绘图片分析
**目标**：提取服饰、风格信息，作为"模板"描述

**Vision Prompt**:
```
Analyze the art style and the character's outfit in this hand-drawn image. 
Provide a natural language description focusing on:
- Clothing items (top, bottom, colors, specific details like text/patterns)
- Accessories (bags, shoes, socks, jewelry, etc.)
- Overall fashion style (trendy, casual, formal, sporty, etc.)
- Body proportions and pose (if distinctive)
- Artistic rendering style (color blocks, textures, line work)

Provide a concise, continuous description suitable for image generation prompts.
Avoid mentioning facial features.
```

**返回示例**:
```
"wearing a green cropped long-sleeved top with 'LYND' text, a brown pleated 
mini skirt, white socks with yellow stripes, and chunky brown shoes, holding 
a white tote bag with 'OOH AHH' in yellow text. The art style features bold 
color blocks with a textured, acrylic paint aesthetic. The fashion style is 
trendy and youthful."
```

---

### 第二步：构建Prompt（固定模板 + 变量插入）

#### 2.1 固定模板设计

不同风格有不同的固定模板，保证输出质量的一致性：

**Realistic风格模板**:
```python
{
    "composition": "full-body studio portrait",
    "photography_style": "high-quality fashion photography style",
    "lighting": "soft studio lighting",
    "background": "clean solid light grey background",
    "quality": "realistic textures and details, 8k resolution, highly detailed"
}
```

**Cute风格模板**:
```python
{
    "composition": "full-body character illustration",
    "photography_style": "cute cartoon style with bright colors and simple lines",
    "lighting": "soft diffused lighting",
    "background": "clean pastel background",
    "quality": "child-friendly, smooth rendering, high quality"
}
```

**Anime风格模板**:
```python
{
    "composition": "full-body anime character",
    "photography_style": "anime art style with vibrant colors and expressive features",
    "lighting": "dramatic anime lighting",
    "background": "clean gradient background",
    "quality": "detailed line art, professional anime quality"
}
```

#### 2.2 变量插入

最终Prompt结构：
```
[人物描述], [服饰描述]. 
The image should be a [composition], in a [photography_style], with [lighting]. 
The background is a [background]. 
Focus on [quality].
```

#### 2.3 实际组装示例

**输入**:
- 人物描述: "A young East Asian girl with long, straight dark brown hair..."
- 服饰描述: "wearing a green cropped long-sleeved top with 'LYND' text..."
- 风格: realistic

**输出Prompt**:
```
A young East Asian girl with long, straight dark brown hair, round eyes, 
a small nose, and a cheerful smile, who appears to be around 8-12 years old, 
wearing a green cropped long-sleeved top with 'LYND' text, a brown pleated 
mini skirt, white socks with yellow stripes, and chunky brown shoes, holding 
a white tote bag with 'OOH AHH' in yellow text. 
The image should be a full-body studio portrait, in a high-quality fashion 
photography style, with soft studio lighting. 
The background is a clean solid light grey background. 
Focus on realistic textures and details, 8k resolution, highly detailed.
```

---

### 第三步：图像生成（API调用）

使用Gemini 2.5 Flash Image模型生成最终图片：

```python
config = types.GenerateContentConfig(
    response_modalities=["IMAGE"],
    temperature=0.9,
    top_p=0.95
)

contents = [
    structured_prompt,
    types.Part.from_bytes(data=image1_bytes, mime_type='image/png'),
    types.Part.from_bytes(data=image2_bytes, mime_type='image/png')
]

response = client.models.generate_content(
    model='models/gemini-2.5-flash-image',
    contents=contents,
    config=config
)
```

---

## ✅ 策略优势

### 1. **灵活性高**
- 为不同的照片和手绘图分别调用Vision
- 动态生成独特的描述
- 适应各种输入组合

### 2. **质量一致**
- 固定模板保证背景、灯光、构图一致
- 无论手绘风格如何变化，输出都是"真实照片"风格
- 专业的摄影术语确保高质量

### 3. **减少冗余**
- Vision只提取必要信息
- 避免复杂的JSON结构
- 自然语言描述更适合图像生成

### 4. **易于扩展**
- 新增风格只需添加模板
- 调整模板参数即可优化效果
- 可以为特定场景预设风格库

---

## 🔧 代码实现

### 文件位置
`api/nano_banana.py`

### 核心函数

1. **extract_person_features(image_path)** 
   - 行: 1267-1317
   - 返回: 自然语言描述字符串

2. **extract_artwork_features(image_path)**
   - 行: 1329-1402
   - 返回: 自然语言描述字符串

3. **build_structured_prompt(person_description, outfit_description, lesson_type, style)**
   - 行: 1404-1477
   - 返回: 完整的Prompt字符串

4. **combine_with_vision_extraction(image1_path, image2_path, lesson_type, style, aspect_ratio)**
   - 行: 1479-1622
   - 返回: (图片路径, 特征信息字典)

---

## 📊 监控和调试

### 查看最新生成的Prompt

**方法1：查询最近一次**
```bash
./scripts/get_latest_prompt.sh
```

**方法2：实时监控**
```bash
./scripts/monitor_prompts.sh
# 然后在iPad上生成图片，终端会实时显示
```

### 日志输出示例

```
🚀 开始三步自动化流程：Vision提取 + 结构化Prompt + 图像生成

【第一步】Vision提取特征...
👤 开始提取人物特征...
📥 Vision返回: A young East Asian girl...
✅ 成功提取人物描述
📝 描述内容: A young East Asian girl with...

🎨 开始提取手绘作品特征...
📥 Vision返回: wearing a green cropped...
✅ 成功提取服饰和风格描述
📝 描述内容: wearing a green cropped long-sleeved top...

【第二步】构建Prompt（固定模板+变量插入）...
🔨 开始构建Prompt（固定模板+变量插入）...
✅ Prompt构建完成
📝 完整Prompt (全文): A young East Asian girl with long...

【第三步】生成图像...
🔥 调用Gemini 2.5 Flash Image生成...
📋 使用的完整提示词：
A young East Asian girl with long, straight dark brown hair...
📋 提示词长度: 489 字符
✅ 成功生成图片
```

---

## 🎨 进一步优化建议

### 1. Prompt精炼
对Vision返回的描述进行后处理：
- 移除口语化表达
- 合并相似形容词
- 提取关键信息

### 2. 参数调整
实验不同的API参数：
```python
config = types.GenerateContentConfig(
    response_modalities=["IMAGE"],
    temperature=0.9,      # 创意程度 (0.0-1.0)
    top_p=0.95,          # 多样性控制 (0.0-1.0)
)
```

### 3. 多轮优化
基于生成结果迭代改进：
1. 生成初版图片
2. 用Vision分析生成图
3. 微调Prompt重新生成

### 4. 预设风格库
为常见手绘风格定义固定片段：
```python
art_style_presets = {
    "pop_art": "Pop Art style with bold colors and graphic patterns",
    "watercolor": "soft watercolor painting aesthetic with gentle gradients",
    "anime": "Japanese anime art style with cel shading"
}
```

---

## 📝 总结

这个策略的核心是**分离关注点**：

1. **Vision负责理解** - 提取关键信息
2. **固定模板负责质量** - 保证输出标准
3. **变量插入负责灵活性** - 适应不同输入

通过这种方式，我们可以批量高效地生成高质量的融合图片，同时保持对输出结果的可控性。

---

**部署时间**: 2026-02-03 18:26
**版本**: v2.0 - 自然语言描述 + 固定模板策略
