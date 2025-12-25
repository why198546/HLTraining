"""
松果币图标生成脚本
将原始松果图标转换为多个尺寸，方便在网站各处使用
"""
import os

from PIL import Image

# 定义输出尺寸
SIZES = {
    'tiny': 16,      # 小图标 (favicon, 内联图标)
    'small': 32,     # 按钮、列表项
    'medium': 64,    # 卡片、通知
    'large': 128,    # 个人中心、奖励展示
    'xlarge': 256,   # 大型展示、营销页面
    'original': None # 保留原始尺寸
}

def create_songuo_coin_icons(input_image_path, output_dir='static/images/songuo_coin'):
    """
    生成不同尺寸的松果币图标
    
    Args:
        input_image_path: 输入图片路径
        output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 打开原始图片
    try:
        img = Image.open(input_image_path)
        print(f"✓ 成功加载原始图片: {img.size[0]}x{img.size[1]} ({img.mode})")
        
        # 确保是RGBA模式（支持透明背景）
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            print(f"  转换为RGBA模式")
        
        # 保存原始尺寸
        original_path = os.path.join(output_dir, 'songuo_coin_original.png')
        img.save(original_path, 'PNG', optimize=True)
        print(f"✓ 原始尺寸: {original_path}")
        
        # 生成各种尺寸
        for size_name, size in SIZES.items():
            if size is None:
                continue  # 跳过原始尺寸（已保存）
            
            # 调整尺寸（保持宽高比，高质量缩放）
            resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # 保存PNG（带透明背景）
            output_path = os.path.join(output_dir, f'songuo_coin_{size_name}_{size}x{size}.png')
            resized_img.save(output_path, 'PNG', optimize=True)
            print(f"✓ {size_name.capitalize():8} ({size}x{size}): {output_path}")
        
        # 生成特殊用途的版本
        print("\n生成特殊版本:")
        
        # Favicon (ICO格式，16x16和32x32)
        favicon_sizes = [(16, 16), (32, 32)]
        favicon_images = [img.resize(size, Image.Resampling.LANCZOS) for size in favicon_sizes]
        favicon_path = os.path.join(output_dir, 'favicon.ico')
        favicon_images[0].save(favicon_path, format='ICO', sizes=favicon_sizes)
        print(f"✓ Favicon: {favicon_path}")
        
        # Apple Touch Icon (180x180)
        apple_icon = img.resize((180, 180), Image.Resampling.LANCZOS)
        apple_path = os.path.join(output_dir, 'apple-touch-icon.png')
        apple_icon.save(apple_path, 'PNG', optimize=True)
        print(f"✓ Apple Touch Icon (180x180): {apple_path}")
        
        # Android Chrome Icon (192x192, 512x512)
        android_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
        android_192_path = os.path.join(output_dir, 'android-chrome-192x192.png')
        android_192.save(android_192_path, 'PNG', optimize=True)
        print(f"✓ Android Icon (192x192): {android_192_path}")
        
        android_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
        android_512_path = os.path.join(output_dir, 'android-chrome-512x512.png')
        android_512.save(android_512_path, 'PNG', optimize=True)
        print(f"✓ Android Icon (512x512): {android_512_path}")
        
        # 内联SVG尺寸（用于CSS背景等）
        inline_24 = img.resize((24, 24), Image.Resampling.LANCZOS)
        inline_24_path = os.path.join(output_dir, 'songuo_coin_inline_24x24.png')
        inline_24.save(inline_24_path, 'PNG', optimize=True)
        print(f"✓ 内联图标 (24x24): {inline_24_path}")
        
        inline_48 = img.resize((48, 48), Image.Resampling.LANCZOS)
        inline_48_path = os.path.join(output_dir, 'songuo_coin_inline_48x48.png')
        inline_48.save(inline_48_path, 'PNG', optimize=True)
        print(f"✓ 内联图标 (48x48): {inline_48_path}")
        
        print(f"\n✅ 成功生成所有松果币图标！")
        print(f"📁 输出目录: {os.path.abspath(output_dir)}")
        
        # 生成使用说明
        generate_usage_guide(output_dir)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

def generate_usage_guide(output_dir):
    """生成使用说明文档"""
    guide_path = os.path.join(output_dir, 'USAGE_GUIDE.md')
    
    guide_content = """# 松果币图标使用指南

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
"""
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"\n📖 使用指南已生成: {guide_path}")

if __name__ == '__main__':
    import sys

    # 检查命令行参数
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        # 默认输入路径
        input_path = 'static/images/songuo_coin_source.png'
        print(f"使用默认输入路径: {input_path}")
    
    # 检查文件是否存在
    if not os.path.exists(input_path):
        print(f"❌ 错误: 找不到输入文件 '{input_path}'")
        print(f"\n使用方法:")
        print(f"  python {sys.argv[0]} <输入图片路径>")
        print(f"\n示例:")
        print(f"  python {sys.argv[0]} songuo_coin_original.png")
        sys.exit(1)
    
    # 生成图标
    create_songuo_coin_icons(input_path)
