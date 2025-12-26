# 图片输入功能增强文档

## 功能概述

在 `/create/image` 页面中，现已支持多种图片输入方式，让用户可以更灵活地添加参考图片。

## 新增功能

### 1. 📸 点击"+"按钮 - 选择上传或拍照

点击输入框右下角的"+"按钮，会弹出一个菜单：
- **上传图片**：从设备相册/文件系统选择图片
- **拍照**：直接调用摄像头拍照（移动设备支持前后摄像头切换）

**使用方法：**
1. 点击"+"按钮
2. 选择"上传图片"或"拍照"
3. 图片会自动显示在预览区域

### 2. 🖱️ 拖拽上传

支持将图片文件直接拖拽到输入框区域。

**使用方法：**
1. 从桌面或文件夹拖动图片文件
2. 移动到输入框区域（会显示"松开以上传图片"提示）
3. 松开鼠标，图片会自动上传并显示预览

### 3. 📋 粘贴图片

支持直接粘贴剪贴板中的图片。

**使用方法：**
1. 复制一张图片（从其他应用、网页、截图工具等）
2. 在输入框或页面任意位置按 `Ctrl+V` (Windows) 或 `Cmd+V` (Mac)
3. 图片会自动添加到预览区域

### 4. 🔗 粘贴图片链接

支持粘贴图片的URL链接，系统会自动下载并加载图片。

**使用方法：**
1. 复制一个图片URL（如：`https://example.com/image.jpg`）
2. 在输入框中按 `Ctrl+V` (Windows) 或 `Cmd+V` (Mac)
3. 系统会自动识别并下载图片
4. 下载完成后，图片会显示在预览区域

**支持的图片格式：**
- JPG/JPEG
- PNG
- GIF
- WEBP
- BMP
- SVG

## 技术实现

### 前端实现

**文件：** `static/js/create_image.js`

#### 1. 菜单切换功能
```javascript
function toggleImageMenu(event) {
    event.stopPropagation();
    const menu = document.getElementById('image-menu');
    if (menu) {
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    }
}
```

#### 2. 拖拽上传
```javascript
function initializeDragAndDrop() {
    const container = document.getElementById('prompt-container');
    // 监听 dragenter, dragover, dragleave, drop 事件
    // 在 drop 事件中处理文件
}
```

#### 3. 粘贴功能
```javascript
function initializePaste() {
    // 监听 paste 事件
    // 检测粘贴的是图片文件还是文本（URL）
    // 相应处理
}
```

#### 4. URL图片加载
```javascript
async function loadImageFromUrl(url) {
    // 调用后端API下载图片
    // 转换为File对象并显示预览
}
```

### 后端实现

**文件：** `app/routes/api_create.py`

#### 新增API端点：`/api/load_image_from_url`

**功能：** 从URL下载图片并转换为base64返回

**请求：**
```json
{
  "url": "https://example.com/image.jpg"
}
```

**响应：**
```json
{
  "success": true,
  "image_data": "data:image/png;base64,..."
}
```

**安全措施：**
1. 验证Content-Type确保是图片
2. 限制图片尺寸（最大2048px）
3. 设置请求超时（10秒）
4. 添加User-Agent避免被反爬虫拦截

## 用户体验优化

### 视觉反馈
- 拖拽时显示虚线边框和提示文本
- 上传/粘贴成功显示Toast提示
- Loading状态显示"正在加载图片..."

### 交互细节
- 点击页面其他地方自动关闭菜单
- 支持在页面任何地方粘贴（不仅限于输入框）
- 自动关闭菜单（选择上传/拍照后）

### 错误处理
- 无效文件格式提示
- URL下载失败提示
- 网络错误友好提示

## 兼容性

- ✅ 桌面浏览器（Chrome, Firefox, Safari, Edge）
- ✅ 移动浏览器（iOS Safari, Chrome Mobile）
- ✅ 平板设备（iPad, Android Tablet）

## 示例场景

### 场景1：手机拍照上传
小明想要给他画的小猫上色：
1. 在手机上打开网站
2. 点击"+"按钮 → 选择"拍照"
3. 拍摄他的画作
4. 输入描述"一只橙色的小猫"
5. 点击生成

### 场景2：从网上找参考图
小红想要参考网上的图片：
1. 在其他标签页找到喜欢的图片
2. 右键复制图片地址
3. 回到创作页面，在输入框粘贴
4. 系统自动加载图片
5. 输入创意描述并生成

### 场景3：使用截图工具
小华想要参考电脑上的图片：
1. 使用截图工具截取想要的部分
2. 在创作页面按 Ctrl+V 粘贴
3. 图片自动显示
4. 完善描述并生成

## 注意事项

1. **图片链接加载**
   - 需要图片URL可公开访问
   - 部分网站可能有防盗链保护
   - 建议使用图床或公开图片链接

2. **文件大小**
   - 系统会自动压缩大图片到2048px
   - 建议上传合适尺寸的图片以获得最佳效果

3. **隐私安全**
   - 所有上传的图片仅用于生成，不会公开分享
   - 图片链接加载通过服务器代理，保护用户隐私

## 后续优化方向

- [ ] 支持多图片上传（选择最佳参考图）
- [ ] 图片编辑功能（裁剪、旋转）
- [ ] 图片历史记录（最近使用）
- [ ] 从相册批量导入
- [ ] 手绘板直接输入支持
