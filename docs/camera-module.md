# 摄像头模块使用指南

## 模块化设计

摄像头功能已统一到独立的CSS和JS模块，确保各处表现一致。

## CSS模块

### 文件位置
`static/css/modules/camera.css`

### 引入方式
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/modules/camera.css') }}">
```

### 主要样式类

#### 1. 标签页系统
- `.camera-tabs` - 标签页容器
- `.camera-tab-btn` - 标签按钮
- `.camera-tab-btn.active` - 激活状态
- `.camera-tab-content` - 标签内容
- `.camera-tab-content.active` - 显示状态

#### 2. 预览区域
- `.camera-preview-area` - 预览容器（4:3比例）
- `.camera-preview-container` - 内部容器
- `#camera-video` - 视频流元素
- `#camera-canvas` - 拍照画布

#### 3. 控制按钮
- `.camera-switch-btn` - 摄像头切换按钮（z-index: 1000）
- `.camera-btn` - 通用按钮样式
- `.camera-btn-primary` - 主要操作按钮
- `.camera-btn-secondary` - 次要操作按钮

#### 4. 信息显示
- `.camera-info-overlay` - 信息覆盖层
- `.camera-info-text` - 信息文本

## HTML结构示例

```html
<!-- 摄像头容器 -->
<div class="camera-section">
    <!-- 标签页 -->
    <div class="camera-tabs">
        <button class="camera-tab-btn active" data-tab="upload">📁 上传图片</button>
        <button class="camera-tab-btn" data-tab="camera">📷 拍照</button>
    </div>
    
    <!-- 拍照标签内容 -->
    <div class="camera-tab-content active" id="camera-tab-content">
        <div class="camera-preview-area">
            <div class="camera-preview-container">
                <video id="camera-video" autoplay playsinline></video>
                <canvas id="camera-canvas"></canvas>
                
                <!-- 摄像头信息 -->
                <div class="camera-info-overlay">
                    <span id="camera-info" class="camera-info-text"></span>
                </div>
                
                <!-- 切换按钮 -->
                <button class="camera-switch-btn" onclick="switchCameraDevice(event)">
                    <i class="fas fa-sync-alt"></i>
                </button>
            </div>
        </div>
        
        <!-- 控制按钮 -->
        <div class="camera-controls">
            <button id="camera-start-btn" class="camera-btn camera-btn-primary">
                <i class="fas fa-play"></i> 启动摄像头
            </button>
            <button id="camera-capture-btn" class="camera-btn camera-btn-primary" style="display:none;">
                <i class="fas fa-camera"></i> 拍照
            </button>
        </div>
    </div>
</div>
```

## Z-Index 层级

为避免元素遮挡，统一使用以下层级：

- 摄像头切换按钮：`z-index: 1000`（最高优先级）
- 摄像头信息显示：`z-index: 100`
- 裁剪确认按钮：`z-index: 100`
- SVG覆盖层：`pointer-events: none`（不拦截事件）

## 使用的页面

1. `/create/image` - 图片创作页面
2. `/classroom/lesson/<id>` - 课堂页面
3. 其他需要拍照功能的页面

## 响应式断点

- 桌面：默认样式
- 平板（≤768px）：按钮尺寸略小
- 手机（≤480px）：进一步优化触摸体验

## 注意事项

1. **不要在页面内联样式中重复定义**摄像头相关样式
2. **统一引用** `camera.css` 模块
3. **保持z-index一致性**，避免遮挡问题
4. 使用标准的HTML结构，确保JS功能正常
