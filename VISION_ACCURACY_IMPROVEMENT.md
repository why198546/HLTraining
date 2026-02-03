# Vision提取准确性改进

## 🎯 问题反馈

用户反馈：第二张图片明显是**蓝色裙子**、**黑色t-shirt**，但Vision提取结果不准确。

---

## 🔧 改进措施

### 1. 优化服饰提取Prompt

**改进前**:
```
"Analyze the art style and the character's outfit..."
- Clothing items (top, bottom, colors, specific details like text/patterns)
- Accessories (bags, shoes, socks, jewelry, etc.)
```

**改进后**:
```
"Analyze the art style and the character's outfit..."
- Clothing items: Describe each piece ACCURATELY (top, bottom, outerwear)
- Colors: Be PRECISE about colors - look carefully at what you see 
  (e.g., "blue skirt", "black t-shirt", "red shoes")
- Specific details: text on clothing, patterns, textures
```

**关键变化**:
- ✅ 强调 **ACCURATELY** 和 **PRECISE**
- ✅ 明确要求 "look carefully at what you see"
- ✅ 提供明确的颜色示例（blue skirt, black t-shirt）
- ✅ 调整示例输出为更简洁的格式

---

### 2. 优化人物面部提取Prompt

**改进后**:
```
"Describe this person's facial appearance..."
- Be ACCURATE and SPECIFIC about what you see
- Focus ONLY on the face and hair
- Do NOT describe: clothing, body, background, or pose
```

**关键变化**:
- ✅ 强调 **ACCURATE** 和 **SPECIFIC**
- ✅ 明确禁止描述服饰（避免混淆）

---

### 3. 增强日志输出

**新增日志**:
```python
print(f"📥 Vision返回原始文本: {response_text[:200]}...")
print(f"📝 完整描述内容: {description}")
print(f"📏 描述长度: {len(description)} 字符")
print(f"🔍 关键词检查: 是否包含颜色词汇")  # 仅服饰提取
```

**便于调试**:
- 查看完整的Vision返回文本
- 验证颜色词是否正确识别
- 追踪描述长度和质量

---

## 📊 测试方法

### 实时监控（推荐）
```bash
./scripts/monitor_prompts.sh
```

在iPad上生成图片时，终端会显示：
```
🎨 开始提取手绘作品特征...
📥 Vision返回原始文本: wearing a black t-shirt and a blue...
✅ 成功提取服饰和风格描述
📝 完整描述内容: wearing a black t-shirt and a blue pleated skirt...
📏 描述长度: 156 字符
🔍 关键词检查: 是否包含颜色词汇
```

### 查看历史日志
```bash
ssh -i ~/.ssh/wordpress_openssh root@47.95.214.47 \
  "grep '完整描述内容:' /var/www/hltraining/logs/error.log | tail -n 5"
```

---

## ✅ 预期效果

### 图片2（手绘）应该提取到：
- ✅ **black t-shirt** （黑色T恤）
- ✅ **blue skirt** 或 **blue pleated skirt** （蓝色裙子/蓝色百褶裙）
- ✅ 其他配饰（鞋子、袜子、包包等）

### 示例输出：
```
"wearing a black t-shirt and a blue pleated skirt, 
white socks with striped details, and brown shoes. 
The art style features clean color blocks with a 
flat graphic aesthetic. Casual youthful fashion style."
```

---

## 🔍 如果还是不准确

### 调试步骤：

1. **查看完整日志**:
```bash
./scripts/monitor_prompts.sh
```

2. **检查Vision返回**:
   - 查看 "📥 Vision返回原始文本"
   - 确认Gemini是否正确识别颜色

3. **可能的原因**:
   - 图片压缩导致颜色失真
   - 光照条件影响颜色识别
   - Gemini模型本身的识别误差

4. **进一步改进**:
   - 可以在Prompt中添加更多颜色示例
   - 调整图片压缩质量
   - 尝试不同的Vision模型

---

## 📝 代码位置

- **服饰提取Prompt**: [api/nano_banana.py:1342-1363](api/nano_banana.py#L1342-L1363)
- **人物面部Prompt**: [api/nano_banana.py:1282-1302](api/nano_banana.py#L1282-L1302)
- **日志输出**: 
  - 人物: Line 1314-1317
  - 服饰: Line 1378-1382

---

## 🚀 部署状态

✅ 已部署到服务器
✅ 服务正常运行
✅ 可以立即测试

---

## 💡 下一步

1. 在iPad上用相同的图片重新生成
2. 观察日志中的"完整描述内容"
3. 验证是否正确识别为"黑色t-shirt"和"蓝色裙子"
4. 如有问题，提供完整日志进行进一步调试

