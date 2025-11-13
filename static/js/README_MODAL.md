# 作品模态框架构说明

## 文件结构

### 1. artwork-modal.js (统一模态框模块)
**用途**: 提供统一的作品模态框功能，供所有页面共享使用

**包含功能**:
- `showArtworkModal(element)` - 显示作品详情模态框
- `closeArtworkModal()` - 关闭作品详情模态框
- `showImageModal(imageSrc, title)` - 在模态框上叠加显示图片
- `closeImageOverlay()` - 关闭图片叠加层
- `showModelModal(modelSrc, title)` - 显示3D模型查看器
- `closeModelModal()` - 关闭3D模型查看器
- `incrementViewCount(artworkId)` - 增加作品浏览次数
- `handleImageClick(img)` - 处理图片点击切换显示模式
- `toggleImageMode(img)` - 双击切换图片显示模式

**特性**:
- 自动解析 `data-artwork-*` 属性
- 支持版本历史显示 (coloredVersions, adjustedVersions)
- 响应式图片查看 (缩略图/适应窗口/原始大小)
- 集成3D模型查看器
- 自动处理滚动锁定和恢复

### 2. gallery.js (作品展示页面专用)
**用途**: gallery.html 页面特定的功能

**包含功能**:
- 作品筛选功能
- 瀑布流布局
- 加载更多作品
- 点赞功能 (`likeArtwork`)
- 占位图生成
- 作品卡片交互

**注意**: 
- **不再包含**模态框相关函数
- 所有模态框功能都调用 artwork-modal.js 中的函数

### 3. model-viewer-3d.js (3D模型查看器)
**用途**: 提供3D模型的渲染和交互功能

**使用**: 被 artwork-modal.js 调用

## 页面使用方式

### Gallery 页面 (templates/gallery.html)
```html
<script src="{{ url_for('static', filename='js/model-viewer-3d.js') }}"></script>
<script src="{{ url_for('static', filename='js/artwork-modal.js') }}"></script>
<script src="{{ url_for('static', filename='js/gallery.js') }}"></script>
```

### My Artworks 页面 (templates/auth/my_artworks.html)
```html
<script src="{{ url_for('static', filename='js/model-viewer-3d.js') }}"></script>
<script src="{{ url_for('static', filename='js/artwork-modal.js') }}"></script>
<script src="{{ url_for('static', filename='js/gallery.js') }}"></script>
```

**两个页面使用相同的脚本顺序**，确保:
1. 先加载3D模型查看器
2. 再加载统一模态框模块
3. 最后加载页面特定功能

## 数据属性要求

作品卡片必须包含以下 `data-*` 属性:

**基本属性** (两个页面都需要):
- `data-artwork-id`: 作品ID (可选，用于浏览计数)
- `data-artwork-title`: 作品标题
- `data-artwork-artist`: 作者名字
- `data-artwork-age`: 作者年龄
- `data-artwork-date`: 创作日期
- `data-artwork-description`: 作品描述
- `data-artwork-original`: 原始简笔画URL
- `data-artwork-generated`: AI生成图片URL
- `data-artwork-model`: 3D模型文件URL
- `data-artwork-likes`: 点赞数
- `data-artwork-views`: 浏览次数

**版本历史属性** (可选):
- `data-artwork-session-id`: 创作会话ID
- `data-artwork-colored-versions`: JSON数组，上色版本文件名
- `data-artwork-adjusted-versions`: JSON数组，调整版本文件名

## 优势

1. **代码复用**: 两个页面共享同一套模态框代码，减少重复
2. **维护简单**: 修改一处，两个页面同步更新
3. **功能一致**: 确保用户体验统一
4. **易于扩展**: 新增页面只需引入 artwork-modal.js
5. **清晰分工**: 
   - artwork-modal.js = 通用模态框
   - gallery.js = 页面特定功能
   - model-viewer-3d.js = 3D渲染

## 开发建议

- 修改模态框功能 → 编辑 `artwork-modal.js`
- 修改gallery页面特定功能 → 编辑 `gallery.js`
- 修改3D模型显示 → 编辑 `model-viewer-3d.js`
- **不要**在 gallery.js 中重复定义模态框函数
