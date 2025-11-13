# 作品模态框组件架构说明

## 📁 组件文件

### 1. HTML组件
- **`templates/components/artwork_modals.html`** - 统一的模态框HTML结构
  - 作品详情模态框 (`#artworkModal`)
  - 图片放大查看模态框 (`#imageModal`)
  - 3D模型查看器 (`#modelOverlay`)

- **`templates/components/artwork_scripts.html`** - 统一的JavaScript加载
  - `model-viewer-3d.js` - 3D模型查看器功能
  - `artwork-modal.js` - 模态框核心功能
  - `gallery.js` - 事件绑定和页面特定功能

### 2. JavaScript模块
- **`static/js/artwork-modal.js`** - 统一的模态框核心功能
  - `showArtworkModal()` - 显示作品详情
  - `closeArtworkModal()` - 关闭作品详情
  - `showImageModal()` - 显示图片放大
  - `closeImageModal()` - 关闭图片放大
  - `showModelModal()` - 显示3D模型
  - `closeModelModal()` - 关闭3D模型
  - `incrementViewCount()` - 增加浏览次数

- **`static/js/gallery.js`** - 页面特定功能
  - `setupArtworkInteractions()` - 设置事件监听(支持 `#galleryGrid` 和 `#myArtworksGrid`)
  - 筛选、加载更多、点赞等功能

- **`static/js/model-viewer-3d.js`** - 3D模型渲染引擎

### 3. 数据组件
- **`templates/components/artwork_card.html`** - 作品卡片(包含data-*属性)
- **`templates/components/artwork_grid.html`** - 作品网格容器

## 🔧 使用方式

### 在页面中引用组件

```jinja
{# 在页面底部body标签前 #}
{% include 'components/artwork_modals.html' %}
{% include 'components/artwork_scripts.html' %}
```

### 设置作品网格

```jinja
{% set grid_id = 'galleryGrid' %}  {# 或 'myArtworksGrid' #}
{% include 'components/artwork_grid.html' %}
```

## 📊 当前使用页面

1. **`templates/gallery.html`** - 作品展示页
   - 网格ID: `galleryGrid`
   - 显示作者: ✅
   - 显示隐私: ❌
   - 显示操作: ❌

2. **`templates/auth/my_artworks.html`** - 我的作品页
   - 网格ID: `myArtworksGrid`
   - 显示作者: ❌
   - 显示隐私: ✅
   - 显示操作: ✅ (编辑/删除/设为公开)

## ✅ 优势

1. **单一数据源** - 修改一处,两个页面同步更新
2. **易于维护** - 模态框HTML和JavaScript逻辑集中管理
3. **一致性** - 确保所有页面的用户体验一致
4. **可扩展** - 新增使用模态框的页面只需引用组件

## 🔄 修改流程

### 修改模态框结构
编辑 `templates/components/artwork_modals.html`

### 修改模态框逻辑
编辑 `static/js/artwork-modal.js`

### 修改事件绑定
编辑 `static/js/gallery.js` 中的 `setupArtworkInteractions()`

### 添加新页面使用模态框
```jinja
{# 1. 包含作品网格 #}
{% set grid_id = 'yourGridId' %}
{% include 'components/artwork_grid.html' %}

{# 2. 引用模态框组件 #}
{% include 'components/artwork_modals.html' %}
{% include 'components/artwork_scripts.html' %}
```

## 📝 数据属性要求

作品卡片必须包含以下 `data-*` 属性:

```html
data-artwork-id          - 作品ID
data-artwork-title       - 作品标题
data-artwork-artist      - 作者名称
data-artwork-age         - 作者年龄
data-artwork-description - 作品描述
data-artwork-original    - 原始简笔画URL
data-artwork-generated   - AI生成图片URL
data-artwork-model       - 3D模型URL
data-artwork-likes       - 点赞数
data-artwork-views       - 浏览数
data-artwork-date        - 创建日期
data-artwork-session-id  - 会话ID(可选,用于显示版本历史)
data-artwork-colored-versions  - 上色版本JSON数组
data-artwork-adjusted-versions - 调整版本JSON数组
```

这些属性已在 `templates/components/artwork_card.html` 中统一定义。

## 🎯 最佳实践

1. **不要**在各个页面中重复定义模态框HTML
2. **不要**在多个地方加载相同的JavaScript文件
3. **务必**使用组件引用: `{% include 'components/...' %}`
4. **务必**在修改后测试所有使用该组件的页面
