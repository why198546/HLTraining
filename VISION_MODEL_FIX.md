# Vision提取修复 - 模型404错误

## 🐛 问题原因

**错误信息**:
```
❌ 提取人物特征失败: 404 NOT_FOUND
'models/gemini-2.0-flash-exp is not found for API version v1beta'
```

**根本原因**: 
- `gemini-2.0-flash-exp` 是实验性模型
- 在 v1beta API 中不可用
- 导致Vision提取失败，返回默认的fallback值

## ✅ 解决方案

### 替换模型
```python
# 修改前
model='gemini-2.0-flash-exp'  # ❌ v1beta不支持

# 修改后  
model='gemini-1.5-flash'      # ✅ v1beta稳定支持
```

### 修改位置
- Line 1310: `extract_person_features()` 人物面部提取
- Line 1376: `extract_artwork_features()` 服饰风格提取

## 📊 现在可以测试

使用监控脚本查看实际提取结果：
```bash
./scripts/monitor_prompts.sh
```

然后在iPad上重新生成，应该能看到：
```
👤 开始提取人物特征...
📥 Vision返回原始文本: A young girl with...
✅ 成功提取人物描述
📝 完整描述内容: A young girl with round eyes, black hair...
📏 描述长度: 156 字符

🎨 开始提取手绘作品特征...
📥 Vision返回原始文本: wearing a black t-shirt and blue skirt...
✅ 成功提取服饰和风格描述
📝 完整描述内容: wearing a black t-shirt and a blue pleated skirt...
📏 描述长度: 203 字符
```

## 🎯 预期效果

**修复前的Prompt**（使用默认值）:
```
A person with natural features and a gentle appearance, 
wearing casual clothing in a simple style...
```

**修复后的Prompt**（使用实际提取）:
```
A young East Asian girl with long dark hair, round eyes, 
and a cheerful smile, wearing a black t-shirt and a blue 
pleated skirt, white socks, and brown shoes...
```

## ✅ 已部署

- ✅ 代码已更新
- ✅ 服务已重启
- ✅ 可以立即测试

现在Vision提取应该能正常工作了！🎉
