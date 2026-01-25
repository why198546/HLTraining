# Bug修复：移除非松果课堂第2节课中的骨骼图提示

## 问题描述
在 `https://training.hlylsj.com/create/image` 页面生成图片时，系统错误地提示用户需要绘制骨骼图。但骨骼图功能应该只在松果课堂第2节课（动作课）中使用，其他场景应该直接支持纯文字或参考图生成。

## 根本原因
在 `api/nano_banana.py` 的 `generate_image_from_reference` 方法中，有强制检查要求必须提供骨架参考图：

```python
# 旧代码（第54-55行）
if not sketch_path or not os.path.exists(sketch_path):
    raise Exception(f"必须提供有效的骨架参考图: {sketch_path}")
```

这个检查被应用到所有调用该方法的场景，包括：
- `/create/image` 页面的通用图片生成
- 松果课堂各个课程的生成
- 需要用户上传参考图的任何场景

## 解决方案

### 1. 修改 `nano_banana.py` 中的 `generate_image_from_reference` 方法
- 添加 `require_skeleton` 参数（默认为 `False`）
- 只有当 `require_skeleton=True` 时才强制要求骨架参考图
- 当参考图不存在且 `require_skeleton=False` 时，返回 `None` 而不是抛出异常

```python
def generate_image_from_reference(self, sketch_path, description="", style="cute", aspect_ratio="512x512", temperature=1, top_p=0.95, seed=None, require_skeleton=False):
    # ...检查逻辑...
    # 仅在特定课程时强制要求骨架参考图（如松果课堂第2节课）
    if require_skeleton and (not sketch_path or not os.path.exists(sketch_path)):
        raise Exception(f"该课程需要提供有效的骨架参考图: {sketch_path}")
    
    # 如果没有参考图且不要求骨骼图，则直接生成提示词图片
    if not sketch_path or not os.path.exists(sketch_path):
        print(f"⚠️ 未提供参考图，将使用纯文字模式生成图片")
        return None  # 返回None表示应该使用纯文字生成
```

### 2. 修改 `generate_image_from_sketch` 和 `generate_image_from_sketch_and_text` 方法
- 添加参考图存在性检查
- 当参考图不存在时直接返回 `None`
- 调用 `generate_image_from_reference` 时传入 `require_skeleton=False`

```python
def generate_image_from_sketch(self, sketch_path, style="cute", aspect_ratio="1:1"):
    if not sketch_path or not os.path.exists(sketch_path):
        print(f"⚠️ 参考图不存在，转换为纯文字模式生成")
        return None
    
    return self.generate_image_from_reference(sketch_path, "", style=style, aspect_ratio=aspect_ratio, require_skeleton=False)
```

### 3. 修改 `app/routes/api/generation.py` 中的生成逻辑
- 当参考图模式返回 `None` 时，自动回退到纯文字生成
- 无需用户干预，系统自动选择合适的生成模式

```python
# 图片+文字模式
generated_image_path = nano_banana.generate_image_from_sketch_and_text(...)
# 如果参考图不存在或生成失败，自动回退到纯文字模式
if not generated_image_path:
    print(f"🔄 参考图模式失败，自动回退到纯文字模式")
    generated_image_path = nano_banana.generate_image_from_text(...)
```

## 修改的文件
1. **api/nano_banana.py**
   - `generate_image_from_reference` 方法（第41行）
   - `generate_image_from_sketch` 方法（第649行）
   - `generate_image_from_sketch_and_text` 方法（第661行）

2. **app/routes/api/generation.py**
   - 生成逻辑中的自动回退处理（第246-276行）

## 对松果课堂第2节课的影响
松果课堂第2节课（动作课）仍然保持原有的功能：
- 使用 `sunguo_lesson_action_v1_canvas.html` 或 `sunguo_lesson_action_v2_puppet_enhanced.html`
- 这些模板中的生成逻辑可以在需要时通过设置 `require_skeleton=True` 来强制要求骨骼图
- 目前这些模板调用的是 `/api/generate-image` 接口，通过客户端处理骨骼图的有无

## 测试步骤
1. 访问 `https://training.hlylsj.com/create/image`
2. 输入文字描述，点击"生成图片"
   - 预期：直接生成图片，不提示需要骨骼图 ✅
3. 上传参考图片，输入文字描述，点击"生成图片"
   - 预期：基于参考图生成图片 ✅
4. 上传参考图片，不输入文字，点击"生成图片"
   - 预期：直接生成图片，不提示需要骨骼图 ✅

## 向后兼容性
- 所有现有的调用都会继续工作
- 默认行为（`require_skeleton=False`）确保不会强制要求参考图
- 如果未来需要某个特定场景强制要求骨骼图，只需设置 `require_skeleton=True`

## 相关代码片段位置
- 松果课堂第2节课模板：`templates/sunguo_lesson_action_v1_canvas.html` (第505行)
- 松果课堂生成逻辑：`static/js/sunguo_class.js` (第400-800行)
