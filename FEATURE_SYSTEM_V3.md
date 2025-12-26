# 松果课堂 - 人物生成特征系统 V3.0

## 📋 功能概述

此版本实现了**后端驱动的智能特征检测和常识约束系统**，确保：
- ✅ 用户指定的特征保持一致（4张图保持相同）
- ✅ 未指定的特征随机变化（增加多样性）
- ✅ 应用常识规则（性别与头发长度的合理搭配）
- ✅ 前端无重复检测（信息来源唯一）

## 🔧 技术架构

### 后端流程 (Python)

**文件**: `app/routes/api/generation.py`

```python
def analyze_and_generate_variations(prompt_text, num_variations=4):
    """
    分析用户提示词，检测10个核心特征
    
    返回值:
    - variations: 为每张图生成不同特征组合的描述
    - mentioned_features: 检测到的特征字典 {索引: 关键词}
    """
    
    # 10个特征定义 (含关键词和变化选项)
    features = {
        0: 'gender',       # 男孩/女孩
        1: 'body',         # 胖/瘦/正常
        2: 'hair_length',  # 长发/短发
        3: 'hair_style',   # 卷发/直发
        4: 'skin',         # 深色/浅色皮肤
        5: 'eyes',         # 大眼睛/小眼睛
        6: 'nose',         # 大鼻子/小鼻子
        7: 'mouth',        # 樱桃小嘴/大嘴巴
        8: 'lips',         # 厚嘴唇/薄嘴唇
        9: 'ears'          # 大耳朵/小耳朵
    }
    
    # 特征检测: 遍历keywords，找到matches
    mentioned_features = {}  # {0: '男孩', 2: '长发', 5: '大眼睛'}
    
    # 生成variations: 为未提及的特征生成随机组合描述
    variations = ['，补充特征：...' for i in range(num_variations)]
    
    return variations, mentioned_features
```

**API响应格式**:
```json
{
  "success": true,
  "image_urls": [...],
  "detected_features": {0: "男孩", 2: "长发", 5: "大眼睛"},
  "message": "成功生成4张图片"
}
```

### 前端流程 (JavaScript)

**文件**: `static/js/Sunguo_class.js`

#### 1️⃣ 初始化 (第一张图)
```javascript
let detectedFeatures = {};  // 从API响应中获取

// 第一张图：不添加随机特征，等待获取detected_features
for (let i = 0; i < 4; i++) {
  if (i === 0) {
    randomVariations = [];  // 第一张不变化
  } else {
    randomVariations = getRandomVariations(detectedFeatures);  // 后续3张随机变化
  }
  
  // ... 调用API生成图片 ...
  
  if (i === 0 && data.detected_features) {
    detectedFeatures = data.detected_features;  // 保存检测结果
  }
}
```

#### 2️⃣ 智能随机特征 (后续三张图)
```javascript
function getRandomVariations(detectedFeatures) {
  // 1. 找出未检测到的特征索引
  const specifiedIndices = new Set(Object.keys(detectedFeatures).map(k => parseInt(k)));
  const unspecifiedIndices = [0,1,2,...,9].filter(i => !specifiedIndices.has(i));
  
  // 2. 从未检测特征中随机选2-3个
  const selectedIndices = randomSelect(unspecifiedIndices, 2-3);
  
  // 3. 为每个特征随机选择一个变化选项
  let variations = [];
  for (const idx of selectedIndices) {
    const options = unspecifiedVariations[idx];  // ['长发', '短发']等
    variations.push(randomChoice(options));
  }
  
  // 4. 应用常识规则
  variations = applyCommonSenseRules(detectedFeatures, variations);
  
  return variations;
}
```

#### 3️⃣ 常识规则
```javascript
function applyCommonSenseRules(detectedFeatures, selectedVariations) {
  // 如果检测到性别，应用头发长度约束
  if (detectedFeatures && detectedFeatures[0]) {
    const gender = detectedFeatures[0];
    
    if (gender.includes('男孩') || gender.includes('男')) {
      // 男孩通常短发，移除长发变化
      selectedVariations = selectedVariations.filter(v => 
        !['长发', '中长发', '齐肩发'].includes(v)
      );
    }
    
    if (gender.includes('女孩') || gender.includes('女')) {
      // 女孩通常长发，移除短发变化
      selectedVariations = selectedVariations.filter(v => v !== '短发');
    }
  }
  
  return selectedVariations;
}
```

## 📊 10个核心特征

| 索引 | 特征 | 检测关键词 | 变化选项 |
|------|------|-----------|---------|
| 0 | 性别 | 男孩/女孩/男/女 | - |
| 1 | 体型 | 胖/瘦/壮/纤细 | 胖胖的/瘦瘦的/正常 |
| 2 | 头发长度 | 长发/短发/中长发 | 短发/中长发/长发 |
| 3 | 头发风格 | 卷发/直发/波浪 | 直发/微卷/卷发 |
| 4 | 皮肤 | 深色/浅色/黑/白 | 皮肤白皙/偏黑/中等 |
| 5 | 眼睛 | 大眼睛/小眼睛 | 大眼睛/小眼睛/中等 |
| 6 | 鼻子 | 大鼻子/小鼻子 | 小巧/高挺/中等/秀气 |
| 7 | 嘴巴 | 大嘴/小嘴/樱桃小嘴 | 适中/小嘴/饱满/秀气 |
| 8 | 嘴唇 | 厚嘴唇/薄嘴唇 | 薄/适中/厚/自然 |
| 9 | 耳朵 | 大耳朵/小耳朵 | 小/适中/大/秀气 |

## 🧪 测试验证

已通过以下测试：

✅ **后端特征检测** (`test_feature_detection.py`)
- 正确检测多个特征组合
- 返回正确的索引-关键词映射

✅ **常识规则** (`test_common_sense_rules.js`)
- 男孩 + 长发变化 → 移除长发
- 女孩 + 短发变化 → 移除短发  
- 无性别检测 → 保留所有头发变化

✅ **API响应格式** (`test_api_response_format.py`)
- detected_features正确序列化为JSON
- 前端能正确解析和使用

## 🔄 工作示例

**用户输入**: "我想要一个男孩，大眼睛，长发的形象"

### 第1张 (获取特征)
- Prompt: `[原始提示]黑白素描风格...`
- 响应: `detected_features: {0: '男孩', 2: '长发', 5: '大眼睛'}`

### 第2张 (随机变化)
- 未指定特征: {1, 3, 4, 6, 7, 8, 9}
- 随机选: {1: '体型', 3: '头发风格'}
- 随机值: ['胖胖的', '卷发']
- 常识规则: [通过 - 性别已定，不涉及头发长度]
- Prompt: `[胖胖的，卷发]原始提示...特别体现以上特征`

### 第3张
- 随机选: {4: '皮肤', 7: '嘴巴'}
- 随机值: ['浅色皮肤', '大嘴巴']
- 常识规则: [通过]
- Prompt: `[浅色皮肤，大嘴巴]...`

### 第4张 (上色版本)
- 随机选: {1, 5} - 但{5}已指定，所以跳过
- 最终: {1: '体型'}
- 随机值: ['正常']
- Prompt: `[正常身材]色彩丰富的卡通风格...`

**结果**: 4张图都是男孩、长发、大眼睛，但体型、头发风格、皮肤等随机变化

## ⚙️ 部署步骤

1. **拉取最新代码**
   ```bash
   git pull origin main
   ```

2. **验证后端改动**
   ```bash
   python3 -m py_compile app/routes/api/generation.py
   ```

3. **验证前端改动**
   ```bash
   node -c static/js/Sunguo_class.js
   ```

4. **重启Flask服务**
   ```bash
   python run.py
   ```

5. **运行测试**
   ```bash
   python3 test_feature_detection.py
   python3 test_api_response_format.py
   node test_common_sense_rules.js
   ```

## 📝 关键改动清单

### `app/routes/api/generation.py`
- 修改了 `analyze_and_generate_variations()` 函数返回值
- 添加 `detected_features` 到API响应JSON

### `static/js/Sunguo_class.js`
- ✅ 移除了前端的 `featureCategories` 定义和重复检测代码
- ✅ 新增 `applyCommonSenseRules()` 常识规则函数
- ✅ 修改生成流程，第一张获取detected_features，后续图片使用它
- ✅ 修改 `getRandomVariations()` 使用后端检测结果而非前端检测

## 🎯 预期效果

✅ **用户指定的特征保持一致** - 4张图都遵循用户输入
✅ **未指定特征随机变化** - 增加图片多样性
✅ **避免不合理组合** - 应用性别-头发的常识约束
✅ **单一信息来源** - 只从后端获取特征，无重复检测
✅ **性能优化** - 减少前端重复计算

## 🚀 下一步优化方向

- [ ] 增加更多常识规则（例如：年龄与体型搭配）
- [ ] 支持用户自定义常识约束
- [ ] 添加特征矛盾冲突检测
- [ ] 支持更复杂的特征组合逻辑
