# 松果课堂相机参考图功能集成

## 功能概述

在松果课堂页面添加了相机拍照/上传图片功能，让学生可以：
1. 通过相机拍照或上传本地图片
2. 将拍摄/上传的图片作为参考图
3. 基于参考图和文字描述生成新的图片（图生图功能）

类似于 `/create/image` 页面的功能。

## 技术实现

### 前端修改

#### 1. camera-input.js
- **全局变量添加**：
  ```javascript
  let uploadedReferenceFile = null;  // 存储参考图片文件
  window.uploadedReferenceFile = null;  // 暴露到全局作用域
  ```

- **processPhoto() 函数修改**：
  ```javascript
  function processPhoto(file) {
    // 保存文件供后续表单提交使用
    uploadedReferenceFile = file;
    window.uploadedReferenceFile = file;
    
    // 显示参考图预览
    showReferenceImage(imageDataUrl, file.name);
  }
  ```

- **removeReferenceImage() 函数修改**：
  ```javascript
  function removeReferenceImage() {
    // 清除保存的文件
    uploadedReferenceFile = null;
    window.uploadedReferenceFile = null;
  }
  ```

#### 2. sunguo_class.js
- **表单提交时添加参考图片**：
  ```javascript
  formData.append('prompt', finalPrompt);
  // ... 其他参数 ...
  
  // 如果有参考图片，添加到formData
  if (window.uploadedReferenceFile) {
    formData.append('image', window.uploadedReferenceFile);
    console.log('📷 添加参考图片:', window.uploadedReferenceFile.name);
  }
  
  const resp = await fetch('/api/generate-image', {
    method: 'POST',
    body: formData
  });
  ```

### 后端支持

后端 `/api/generate_image` 接口已经支持接收参考图片：

```python
# app/routes/api_create.py
@api_create_bp.route('/api/generate_image', methods=['POST'])
def generate_image():
    # 获取上传的图片（可选）
    if 'image' in request.files:
        file = request.files['image']
        # 保存并处理图片...
```

接口同时支持：
- `prompt`: 文字描述
- `image`: 参考图片
- `style`: 风格选择
- `aspect_ratio`: 宽高比

## 工作流程

1. **用户拍照/上传**：
   - 点击相机按钮 → 打开模态框
   - 选择拍照或上传文件
   - 预览图片

2. **图片处理**：
   - 调用 `processPhoto(file)` 保存文件到 `window.uploadedReferenceFile`
   - 在页面上显示参考图预览
   - 显示图片信息和提示

3. **生成图片**：
   - 用户在"原始输入"框输入文字描述
   - （可选）点击"AI优化"按钮
   - 点击"生成4张图"按钮
   - FormData 自动包含参考图片（如果存在）
   - 后端基于文字+图片生成新图

4. **移除参考图**：
   - 点击"移除"按钮清除参考图
   - 之后的生成请求不包含图片

## 测试方法

### 本地测试

1. 启动 Flask 服务器：
   ```bash
   cd /Users/hongyuwang/code/HLTraining
   .venv/bin/python app.py
   ```

2. 打开浏览器访问：
   ```
   http://localhost:8088/sunguo-class/character
   ```

3. 登录账号（需要登录才能访问）

4. 测试流程：
   - 点击相机按钮（绿色图标，位于麦克风旁边）
   - 测试拍照功能：
     - 切换到"相机"标签
     - 点击"启动摄像头"
     - 点击"拍照"
     - 点击"使用这张照片"
   - 测试上传功能：
     - 切换到"上传"标签
     - 点击"选择文件"
     - 选择一张图片
     - 点击"使用这张照片"
   - 检查参考图显示：
     - 表单上方应该显示绿色边框的参考图区域
     - 显示上传的图片缩略图
     - 显示图片信息
   - 输入文字描述：
     ```
     一个可爱的小朋友，穿着蓝色衣服，开心地笑
     ```
   - 点击"生成4张图"
   - 查看控制台输出：
     ```
     📷 添加参考图片: camera-photo.jpg
     ```
   - 等待生成完成

### 验证要点

- [ ] 相机模态框正常显示（居中，不偏移）
- [ ] 相机功能正常（能拍照、能预览）
- [ ] 上传功能正常（能选择文件、能预览）
- [ ] 参考图显示正确（有边框、有缩略图、有移除按钮）
- [ ] 控制台显示"📷 添加参考图片"
- [ ] 生成的图片基于参考图和文字描述
- [ ] 点击"移除"按钮后参考图消失
- [ ] 移除后的生成请求不包含图片

## 文件修改清单

### 已修改文件
- `static/js/camera-input.js` - 添加参考图文件保存功能
- `static/js/sunguo_class.js` - 表单提交时包含参考图

### 无需修改的文件
- `templates/sunguo_lesson.html` - 之前已经添加了相机按钮和模态框
- `static/css/modules/page-classroom.css` - 之前已经添加了相机样式
- `app/routes/api_create.py` - 后端已经支持接收参考图

## 生产部署

### 同步到服务器

```bash
# 方式1: rsync
rsync -avz --progress \
  static/js/camera-input.js \
  static/js/sunguo_class.js \
  root@119.29.165.137:/www/wwwroot/pineguo/

# 方式2: scp
scp static/js/camera-input.js root@119.29.165.137:/www/wwwroot/pineguo/static/js/
scp static/js/sunguo_class.js root@119.29.165.137:/www/wwwroot/pineguo/static/js/
```

### 清除浏览器缓存

由于修改了 JavaScript 文件，用户需要强制刷新：
- Chrome/Safari: `Cmd + Shift + R`
- Firefox: `Ctrl + Shift + R`

或在浏览器开发者工具中禁用缓存。

## 已知问题

### SSH 连接问题
当前无法通过 rsync/scp 连接到生产服务器（119.29.165.137）：
```
kex_exchange_identification: read: Connection reset by peer
Connection reset by 119.29.165.137 port 22
```

**可能原因**：
1. 服务器防火墙规则变更
2. SSH 服务配置问题
3. 网络连接不稳定
4. IP 被临时封禁

**解决方法**：
1. 检查服务器防火墙设置
2. 联系服务器管理员
3. 使用其他方式部署（如 FTP、Web 控制面板）

## 下一步

1. ✅ **已完成**：本地实现参考图功能
2. ✅ **已完成**：集成到松果课堂表单提交
3. 🔄 **进行中**：本地测试功能
4. ⏳ **待完成**：解决 SSH 连接问题
5. ⏳ **待完成**：同步到生产环境
6. ⏳ **待完成**：生产环境测试

## 参考资料

- `/create/image` 页面实现：`templates/create_image.html`, `static/js/create_image.js`
- 后端接口：`app/routes/api_create.py` 的 `/api/generate_image`
- 相机功能文档：`IMAGE_VIEWER_FIX_V3.md`
