# 图片预处理优化 - 解决参考图变黑白问题

## 🐛 问题描述

**现象**：用户上传彩色参考图片，输入提示词"去除背景，保留主体"，返回的却是黑白图片。

**原因**：`preprocess_sketch()` 函数会将所有上传的图片都进行灰度化+二值化处理，这个处理是为手绘线稿设计的，但对彩色参考图也错误地应用了。

```python
# 旧代码 - 无差别处理所有图片
def preprocess_sketch(image_path):
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 二值化处理（变成纯黑白）
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
```

---

## ✅ 解决方案

### 1. 智能判断图片类型

新增智能检测算法，自动区分：
- **手绘线稿**：需要预处理（灰度化、二值化）
- **彩色参考图**：保持原图不处理

### 2. 检测算法

基于三个维度判断：

| 维度 | 手绘线稿特征 | 彩色参考图特征 |
|------|------------|---------------|
| **饱和度** | 低（< 30） | 高（> 50） |
| **灰度层次** | 少（< 100种） | 多（> 100种） |
| **颜色分布** | 单一 | 丰富 |

```python
# 计算平均饱和度
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
h, s, v = cv2.split(hsv)
avg_saturation = np.mean(s)

# 计算灰度层次
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
unique_values = len(np.unique(gray))

# 判断逻辑
if avg_saturation > 50:
    # 彩色图，不处理
    return image_path
elif avg_saturation < 30 and unique_values < 100:
    # 手绘线稿，进行预处理
    # 执行灰度化+二值化
else:
    # 不确定，保守处理，保持原图
    return image_path
```

### 3. 新函数签名

```python
def preprocess_sketch(image_path, force_process=False):
    """智能预处理图片
    
    Args:
        image_path: 图片路径
        force_process: 是否强制处理（默认False，会自动判断）
    
    Returns:
        str: 处理后的图片路径，如果不需要处理则返回原路径
    """
```

---

## 📊 效果对比

### 处理前
```
用户上传彩色照片 → preprocess_sketch() 
  → 灰度化 → 二值化 → 黑白图片 ❌
```

### 处理后
```
用户上传彩色照片 → preprocess_sketch() 
  → 检测饱和度=80 → 判定为彩色参考图 
  → 返回原图路径 ✅

用户上传手绘线稿 → preprocess_sketch() 
  → 检测饱和度=15 → 判定为手绘线稿 
  → 灰度化+二值化 → 增强后的线稿 ✅
```

---

## 🔧 修改的文件

### 1. app/utils.py
- **修改前**: 无差别处理所有图片
- **修改后**: 智能判断+选择性处理
- **新增**: numpy导入，用于图像分析

```python
import numpy as np

def preprocess_sketch(image_path, force_process=False):
    # 智能检测逻辑...
    if avg_saturation > 50:
        print("✅ 检测到彩色参考图，保持原图不处理")
        return image_path
    # ...
```

### 2. app/routes/api/generation.py
- **修改**: 调用预处理函数时传入 `force_process=False`
- **效果**: 启用智能判断

```python
# 智能预处理：自动判断是否需要处理
processed_sketch = preprocess_sketch(sketch_path, force_process=False)
```

---

## 🎯 使用场景

### 场景A：用户上传彩色参考图
```
输入: 彩色照片 + 提示词"去除背景，保留主体"
检测: 平均饱和度=85
判断: ✅ 彩色参考图
处理: 保持原图
输出: AI基于彩色图生成去除背景的结果
```

### 场景B：用户上传手绘线稿
```
输入: 黑白线稿 + 提示词"可爱的小猫"
检测: 平均饱和度=8, 灰度层次=45
判断: ✅ 手绘线稿
处理: 灰度化+二值化增强
输出: AI基于增强后的线稿生成彩色图
```

### 场景C：强制处理模式
```python
# 如果某些特殊情况需要强制处理，可以设置参数
processed = preprocess_sketch(image_path, force_process=True)
```

---

## 📝 日志输出

修改后的日志更详细，便于调试：

```
📁 图片已保存: uploads/abc123_photo.jpg
📊 图片分析 - 平均饱和度: 82.3, 灰度层次: 245
✅ 检测到彩色参考图，保持原图不处理
```

或

```
📁 图片已保存: uploads/def456_sketch.jpg
📊 图片分析 - 平均饱和度: 12.5, 灰度层次: 68
📝 检测到手绘线稿，进行预处理
🎨 开始预处理手绘线稿...
✅ 预处理完成: uploads/def456_sketch_processed.jpg
```

---

## 🧪 测试建议

### 测试用例1：彩色照片
1. 上传一张彩色照片
2. 输入提示词"去除背景"
3. **预期**: 返回彩色的去除背景结果

### 测试用例2：手绘线稿
1. 上传一张黑白手绘线稿
2. 输入提示词"上色"
3. **预期**: 线稿被正确增强并上色

### 测试用例3：低饱和度照片
1. 上传一张低饱和度的灰色调照片
2. 输入提示词"增强色彩"
3. **预期**: 保持原图（不会被错误处理成黑白）

---

## ⚠️ 注意事项

### 1. 边界情况
如果图片类型不明确（饱和度30-50之间），系统会**保守处理，保持原图**，以避免错误处理用户的彩色图片。

### 2. 性能影响
- 新增的检测逻辑耗时约 10-50ms（取决于图片大小）
- 相比AI生成时间（几秒到几十秒），影响可忽略

### 3. 兼容性
- 保持向后兼容：原有的 `preprocess_sketch(path)` 调用仍然有效
- 默认行为：智能判断（更安全）
- 可选行为：强制处理（向后兼容）

---

## 📚 相关文档

- [参考图片处理流程](REFERENCE_IMAGE_FLOW.md)
- [图片生成API文档](../api/README.md)

---

*修复日期: 2025-12-23*
*影响版本: v2.0+*
