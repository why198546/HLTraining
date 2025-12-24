# 3D模型格式优化 - GLB预览 + STL打印

## 问题描述
用户报告404错误，并提出需要STL格式用于3D打印：
```
GET http://localhost/models/image_v1_40a833af_ai3d_3f967255.glb 404 (NOT FOUND)
```

## 解决方案

### 1. 统一使用GLB格式 ✅
**原因**: 
- GLB是GLTF的二进制格式，完美支持Three.js的GLTFLoader
- 包含完整的材质、纹理信息
- 文件更小，加载更快
- 适合Web 3D预览

**修改**:
```python
# api/hunyuan3d.py
params = {
    "ImageBase64": image_base64,
    "ResultFormat": "GLB"  # 改为GLB格式（原为STL）
}
```

### 2. 自动生成STL版本 ✅
**功能**: 下载GLB后自动转换并保存STL版本

**实现**:
```python
# api/hunyuan3d.py
def _download_3d_model(self, model_url, image_path):
    # 下载并保存GLB
    with open(glb_path, 'wb') as f:
        f.write(response.content)
    
    # 自动生成STL版本
    stl_path = self._convert_glb_to_stl(glb_path)
    return glb_path

def _convert_glb_to_stl(self, glb_path):
    import trimesh
    mesh = trimesh.load(glb_path)
    stl_path = glb_path.replace('.glb', '.stl')
    mesh.export(stl_path)
    return stl_path
```

### 3. 添加STL下载端点 ✅
**路由**: `/download-stl/<path:model_path>`

**功能**: 
- 如果STL已存在，直接下载
- 如果不存在，从GLB实时转换

**代码**:
```python
# app/routes/model3d.py
@model3d_bp.route('/download-stl/<path:model_path>', methods=['GET'])
def download_stl(model_path):
    stl_path = model_path.replace('.glb', '.stl')
    
    if not os.path.exists(stl_path):
        import trimesh
        mesh = trimesh.load(model_path)
        mesh.export(stl_path)
    
    return send_file(stl_path, as_attachment=True)
```

### 4. 前端下载选项菜单 ✅
**功能**: 用户可选择下载GLB或STL格式

**UI**:
```
┌─────────────────────────┐
│   选择下载格式           │
├─────────────────────────┤
│ 📦 GLB格式 (Web预览)    │
├─────────────────────────┤
│ 🖨️ STL格式 (3D打印)     │
├─────────────────────────┤
│       取消              │
└─────────────────────────┘
```

**实现**:
```javascript
// static/js/create.js
function download3DModel() {
    // 显示格式选择菜单
    menu.innerHTML = `
        <button data-format="glb">GLB格式 (Web预览)</button>
        <button data-format="stl">STL格式 (3D打印)</button>
    `;
    
    // GLB: 直接下载
    // STL: 调用 /download-stl/<model_path>
}
```

## 技术细节

### 格式对比

| 格式 | 用途 | 优点 | 缺点 |
|-----|------|------|------|
| **GLB** | Web 3D预览 | • 支持材质/纹理<br>• Three.js原生支持<br>• 文件小 | 不适合3D打印 |
| **STL** | 3D打印 | • 行业标准<br>• 打印机通用<br>• 结构简单 | 无材质信息 |

### 文件流程

```
腾讯云AI3D API (GLB)
    ↓
下载到 uploads/3d_models/xxx.glb
    ↓
trimesh自动转换 → uploads/3d_models/xxx.stl
    ↓
前端预览: GLB (Three.js)
用户下载: 可选 GLB 或 STL
```

### Trimesh库
**安装**: `pip install trimesh`

**功能**:
- 加载/导出多种3D格式 (GLB, STL, OBJ, PLY等)
- 网格修复和优化
- 3D几何运算

**使用**:
```python
import trimesh
mesh = trimesh.load('model.glb')
mesh.export('model.stl')  # 自动检测格式
```

## 使用指南

### 前端下载
```javascript
// 用户点击"下载3D模型"按钮
download3DModel();  // 显示格式选择菜单

// 选择GLB: 直接下载
// 选择STL: 后端实时转换并下载
```

### 后端API
```bash
# 下载STL格式
GET /download-stl/image_v1_xxx_ai3d_xxx.glb

# 返回 image_v1_xxx_ai3d_xxx.stl 文件
```

## 文件结构

生成的3D模型文件：
```
uploads/3d_models/
├── image_v1_xxx_ai3d_abc123.glb  ← Web预览（主文件）
└── image_v1_xxx_ai3d_abc123.stl  ← 3D打印（自动生成）
```

## 404错误修复

原404错误原因：
1. ~~API设置为STL但下载函数保存为GLB~~
2. ~~前端查看器只支持GLB/GLTF~~

修复后：
- ✅ API生成GLB格式
- ✅ 文件正确保存为GLB
- ✅ 前端GLTFLoader正常加载
- ✅ STL通过trimesh实时转换

## 注意事项

1. **trimesh依赖**: 
   - 必须安装: `pip install trimesh`
   - 如未安装，STL下载会返回500错误

2. **文件大小**:
   - GLB通常比STL小30-50%
   - 建议限制上传图片大小（当前10MB）

3. **转换时间**:
   - GLB→STL转换通常 < 1秒
   - 首次下载STL可能需要等待转换

4. **3D打印建议**:
   - 使用STL格式
   - 检查模型厚度（推荐 >2mm）
   - 建议在切片软件中添加支撑

## 后续优化建议

1. **预生成STL**: 生成GLB后立即转换STL，避免首次下载等待
2. **格式预览**: 在下载菜单显示文件大小对比
3. **批量下载**: 支持同时下载GLB和STL
4. **打印预检**: 添加模型打印适配性检查

## 相关文档
- [3D_API_FIX.md](./3D_API_FIX.md) - API修复详情
- [3D_MODEL_CONFIG.md](./3D_MODEL_CONFIG.md) - 配置说明
- [Trimesh文档](https://trimesh.org/)

---

**修复时间**: 2025-12-23  
**修复人**: GitHub Copilot  
**状态**: ✅ 已解决
