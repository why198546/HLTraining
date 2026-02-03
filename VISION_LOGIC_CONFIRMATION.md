# Vision提取逻辑确认

## ✅ 当前实现逻辑

### 第一步：分别提取两张图片的不同特征

```python
# 图片1（真实照片）- 提取面部特征
person_description = self.extract_person_features(image1_path)
# 返回：「A young East Asian girl with long, straight dark brown hair, 
#       round eyes, a small nose, and a cheerful smile...」

# 图片2（手绘作品）- 提取服饰和风格
outfit_description = self.extract_artwork_features(image2_path)
# 返回：「wearing a green cropped long-sleeved top with 'LYND' text, 
#       a brown pleated mini skirt, white socks...」
```

✅ **确认：分别提取不同特征**
- 图片1 → **只提取面部**（脸型、五官、发型、年龄、性别）
- 图片2 → **只提取服饰**（衣服、配饰、姿势、艺术风格）

---

### 第二步：构建结构化Prompt

```python
structured_prompt = self.build_structured_prompt(
    person_description,   # 面部描述
    outfit_description,   # 服饰描述
    lesson_type,
    style
)
# 返回：「A young East Asian girl..., wearing a green cropped top... 
#       The image should be a full-body studio portrait...」
```

✅ **确认：融合两个描述 + 固定模板**

---

### 第三步：生成图像（关键部分）

```python
# 读取并压缩两张原始图片
img1 = Image.open(image1_path)  # 照片
img2 = Image.open(image2_path)  # 手绘

# 构建API调用内容
contents = [
    structured_prompt,           # 文本提示词（包含面部+服饰描述）
    types.Part.from_bytes(data=image1_bytes, mime_type='image/png'),  # 原始照片
    types.Part.from_bytes(data=image2_bytes, mime_type='image/png')   # 原始手绘
]

# 调用Gemini 2.5 Flash Image
response = self.client.models.generate_content(
    model='models/gemini-2.5-flash-image',
    contents=contents,
    config=config
)
```

✅ **确认：同时提供两张原始图片 + 构建的提示词**

---

## 📊 完整数据流

```
┌─────────────────────────────────────────────────────────────┐
│                     第一步：特征提取                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  图片1 (照片)                    图片2 (手绘)                │
│  1000001604.jpg                 1000001600.jpg              │
│       │                              │                      │
│       │ Vision API                   │ Vision API           │
│       │ (gemini-2.0-flash-exp)      │ (gemini-2.0-flash-exp)│
│       ↓                              ↓                      │
│  面部描述文本                    服饰描述文本                │
│  "A young girl with..."         "wearing green top..."     │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   第二步：Prompt构建                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  面部描述 + 服饰描述 + 固定模板                              │
│       │         │           │                               │
│       └─────────┴───────────┘                               │
│                 ↓                                            │
│        结构化完整Prompt                                       │
│  "A young girl..., wearing green top...,                    │
│   The image should be full-body studio portrait..."         │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    第三步：图像生成                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Gemini 2.5 Flash Image API                                 │
│                                                              │
│  输入1: 结构化Prompt（文本）                                 │
│  输入2: 原始照片（image1_bytes）                             │
│  输入3: 原始手绘（image2_bytes）                             │
│                 │                                            │
│                 ↓                                            │
│         生成的融合图片                                       │
│    combined_xxxxx.jpg                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 为什么这样设计？

### 1. **Vision提取 ≠ 最终输入**
- Vision的作用：**理解图片内容** → 生成文本描述
- 最终生成：**还是用原图** → 保证视觉准确性

### 2. **文本描述 + 原图 = 最强组合**
- 文本描述：告诉AI **关注什么**（面部 vs 服饰）
- 原始图片：提供 **视觉参考**（具体细节）
- 固定模板：控制 **输出质量**（摄影风格、背景、灯光）

### 3. **多模态输入的优势**
```python
contents = [
    "A young girl with round eyes...",  # 文本引导
    <照片二进制数据>,                    # 视觉参考1（面部）
    <手绘二进制数据>                     # 视觉参考2（服饰）
]
```

Gemini 2.5 Flash Image可以同时处理：
- 文本指令（关注重点）
- 图片1的视觉细节（真实面容）
- 图片2的视觉细节（服饰风格）

---

## ✅ 总结确认

### ✔️ 问题1：是否分别提取不同特征？
**答：是的！**
- `extract_person_features(图1)` → **只提取面部**
- `extract_artwork_features(图2)` → **只提取服饰和风格**

### ✔️ 问题2：生图时用什么？
**答：三样东西！**
1. **构建的Prompt**（面部描述 + 服饰描述 + 固定模板）
2. **原始照片图片**（image1_bytes）
3. **原始手绘图片**（image2_bytes）

---

## 🔍 代码位置验证

### Line 1493-1495: 分别提取
```python
person_description = self.extract_person_features(image1_path)
outfit_description = self.extract_artwork_features(image2_path)
```

### Line 1501-1506: 构建Prompt
```python
structured_prompt = self.build_structured_prompt(
    person_description,
    outfit_description,
    lesson_type,
    style
)
```

### Line 1519-1538: 读取两张原图
```python
img1 = Image.open(image1_path)  # 照片原图
# ... 压缩处理 ...
image1_bytes = buffer1.getvalue()

img2 = Image.open(image2_path)  # 手绘原图
# ... 压缩处理 ...
image2_bytes = buffer2.getvalue()
```

### Line 1546-1551: 三个输入一起传给API
```python
contents = [
    structured_prompt,           # 1. 文本Prompt
    types.Part.from_bytes(data=image1_bytes, mime_type='image/png'),  # 2. 照片
    types.Part.from_bytes(data=image2_bytes, mime_type='image/png')   # 3. 手绘
]
```

---

## 💡 这样设计的理由

1. **文本描述清晰指引** → AI知道从哪张图学什么
2. **原图提供视觉细节** → 比文字更准确（如具体发型、服装图案）
3. **固定模板保证质量** → 输出风格统一

这是**多模态AI的最佳实践**：文本引导 + 视觉参考！
