# 松果币图标使用指南

## 📦 可用图标尺寸

### 标准尺寸
- `songuo_coin_tiny_16x16.png` - 16×16 - 小图标、内联使用
- `songuo_coin_small_32x32.png` - 32×32 - 按钮、列表项
- `songuo_coin_medium_64x64.png` - 64×64 - 卡片、通知
- `songuo_coin_large_128x128.png` - 128×128 - 个人中心、奖励展示
- `songuo_coin_xlarge_256x256.png` - 256×256 - 大型展示、营销页面
- `songuo_coin_original.png` - 原始尺寸 - 高清展示

### 特殊用途
- `favicon.ico` - 16×16/32×32 - 浏览器标签图标
- `apple-touch-icon.png` - 180×180 - iOS主屏幕图标
- `android-chrome-192x192.png` - 192×192 - Android应用图标
- `android-chrome-512x512.png` - 512×512 - Android高清图标
- `songuo_coin_inline_24x24.png` - 24×24 - CSS内联、按钮图标
- `songuo_coin_inline_48x48.png` - 48×48 - Retina屏幕内联图标

## 🎨 使用场景

### 1. HTML中使用
```html
<!-- 导航栏松果币显示 -->
<div class="token-display">
  <img src="{{ url_for('static', filename='images/songuo_coin/songuo_coin_small_32x32.png') }}" alt="松果币">
  <span>1,234</span>
</div>

<!-- 个人中心余额展示 -->
<div class="balance-card">
  <img src="{{ url_for('static', filename='images/songuo_coin/songuo_coin_large_128x128.png') }}" alt="松果币">
  <h2>我的松果币</h2>
  <p class="amount">5,000</p>
</div>

<!-- 购买按钮 -->
<button class="buy-tokens">
  <img src="{{ url_for('static', filename='images/songuo_coin/songuo_coin_inline_24x24.png') }}" alt="">
  充值松果币
</button>
```

### 2. CSS中使用
```css
/* 按钮图标 */
.token-button::before {
  content: '';
  display: inline-block;
  width: 24px;
  height: 24px;
  background: url('/static/images/songuo_coin/songuo_coin_inline_24x24.png') no-repeat center;
  background-size: contain;
  margin-right: 8px;
}

/* 列表项图标 */
.token-item {
  list-style-image: url('/static/images/songuo_coin/songuo_coin_tiny_16x16.png');
}

/* 背景装饰 */
.token-bg {
  background: url('/static/images/songuo_coin/songuo_coin_medium_64x64.png') repeat;
  opacity: 0.1;
}
```

### 3. 网站元数据（HTML <head>）
```html
<!-- Favicon -->
<link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='images/songuo_coin/favicon.ico') }}">

<!-- Apple Touch Icon -->
<link rel="apple-touch-icon" sizes="180x180" href="{{ url_for('static', filename='images/songuo_coin/apple-touch-icon.png') }}">

<!-- Android Chrome -->
<link rel="icon" type="image/png" sizes="192x192" href="{{ url_for('static', filename='images/songuo_coin/android-chrome-192x192.png') }}">
<link rel="icon" type="image/png" sizes="512x512" href="{{ url_for('static', filename='images/songuo_coin/android-chrome-512x512.png') }}">
```

### 4. Toast通知中使用
```javascript
// 松果币获得通知
showToast({
  icon: '/static/images/songuo_coin/songuo_coin_medium_64x64.png',
  title: '恭喜获得松果币！',
  message: '+100 松果币',
  type: 'success'
});
```

### 5. 常见UI组件

#### 头部Token余额徽章
```html
<div class="header-token-badge">
  <img src="{{ url_for('static', filename='images/songuo_coin/songuo_coin_inline_24x24.png') }}" 
       alt="松果币" 
       class="token-icon">
  <span class="token-count">{{ current_user.tokens }}</span>
</div>

<style>
.header-token-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: rgba(0, 112, 74, 0.1);
  border-radius: 20px;
}
.token-icon {
  width: 20px;
  height: 20px;
}
</style>
```

#### 充值商品卡片
```html
<div class="token-package">
  <img src="{{ url_for('static', filename='images/songuo_coin/songuo_coin_xlarge_256x256.png') }}" 
       alt="松果币礼包" 
       class="package-icon">
  <h3>1000 松果币</h3>
  <p class="price">¥10.00</p>
  <button>立即购买</button>
</div>
```

#### 消费记录列表
```html
<div class="transaction-item">
  <img src="{{ url_for('static', filename='images/songuo_coin/songuo_coin_small_32x32.png') }}" 
       alt="松果币">
  <div class="details">
    <span class="action">生成AI图片</span>
    <span class="time">2分钟前</span>
  </div>
  <span class="amount">-50</span>
</div>
```

## 📱 响应式建议

```css
/* 基础尺寸 */
.token-icon {
  width: 24px;
  height: 24px;
  background-image: url('/static/images/songuo_coin/songuo_coin_inline_24x24.png');
}

/* Retina屏幕优化 */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .token-icon {
    background-image: url('/static/images/songuo_coin/songuo_coin_inline_48x48.png');
    background-size: 24px 24px;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .header-token-badge .token-icon {
    width: 20px;
    height: 20px;
  }
}
```

## 🎯 尺寸选择建议

| 使用场景 | 推荐尺寸 | 文件 |
|---------|---------|------|
| Favicon | 16×16/32×32 | favicon.ico |
| 导航栏徽章 | 24×24 | songuo_coin_inline_24x24.png |
| 按钮图标 | 24×24 | songuo_coin_inline_24x24.png |
| 列表项图标 | 16×16 | songuo_coin_tiny_16x16.png |
| 通知Toast | 64×64 | songuo_coin_medium_64x64.png |
| 个人中心 | 128×128 | songuo_coin_large_128x128.png |
| 充值商品卡 | 256×256 | songuo_coin_xlarge_256x256.png |
| 营销页面 | 256×256+ | songuo_coin_original.png |
| iOS图标 | 180×180 | apple-touch-icon.png |
| Android图标 | 192×192/512×512 | android-chrome-*.png |

## 💡 优化建议

1. **懒加载**: 对大尺寸图标使用 `loading="lazy"`
2. **预加载**: 关键图标使用 `<link rel="preload">`
3. **SVG优先**: 考虑将PNG转换为SVG获得更好缩放性
4. **CDN**: 生产环境建议使用CDN加速
5. **缓存**: 添加合适的Cache-Control头

---

**生成时间**: 自动生成  
**图标主题**: 松果币 (Songuo Coin)  
**支持透明背景**: ✅ 是
