# CSS模块化迁移 - 测试清单

## ✅ 快速验证步骤

### 1️⃣ 视觉检查 (必做)
访问以下关键页面，确认：
- ✅ 背景是星巴克绿色（无紫色闪烁）
- ✅ 页面布局正常
- ✅ 按钮、卡片样式正确
- ✅ 响应式设计工作正常

#### 关键页面列表
```
http://localhost/                          # 首页 (core.css)
http://localhost/gallery                   # 作品展示 (core + gallery)
http://localhost/create                    # AI创作 (core + create)
http://localhost/auth/login                # 登录页 (core + auth)
http://localhost/sunguo_class              # 松果课堂 (core + classroom)
http://localhost/canvas_projects           # 画布项目 (core + canvas)
http://localhost/auth/parent_dashboard     # 家长中心 (core + auth)
http://localhost/auth/teacher_dashboard    # 教师面板 (core + auth)
```

### 2️⃣ 性能检查 (建议)
打开Chrome DevTools → Network标签：

#### 检查CSS加载
1. 刷新页面 (Ctrl+F5 清除缓存)
2. 查看CSS文件大小：
   ```
   ✅ core.css: ~28 KB
   ✅ page-XXX.css: 18-84 KB
   ❌ style.css: 279 KB (不应再加载)
   ```

#### 性能指标
- **FCP (首次内容绘制)**: < 1.5秒 ✅
- **LCP (最大内容绘制)**: < 2.5秒 ✅
- **CLS (累积布局偏移)**: < 0.1 ✅

### 3️⃣ 功能测试 (重点)

#### 导航功能
- [ ] 顶部导航菜单点击正常
- [ ] 移动端汉堡菜单展开/收起
- [ ] 用户头像下拉菜单显示

#### 表单样式
- [ ] 登录/注册表单显示正常
- [ ] 输入框焦点效果
- [ ] 按钮悬停效果
- [ ] 错误提示样式

#### 卡片组件
- [ ] 作品卡片悬停放大效果
- [ ] 课程卡片样式正确
- [ ] 学生卡片布局正常

#### 动画效果
- [ ] 页面加载渐入动画
- [ ] 按钮点击反馈
- [ ] 工具提示显示

### 4️⃣ 响应式测试

#### 桌面端 (1920x1080)
- [ ] 首页布局
- [ ] 作品展示网格
- [ ] 创作页面工具栏

#### 平板端 (768x1024)
- [ ] 导航菜单适配
- [ ] 卡片网格响应式
- [ ] 侧边栏显示

#### 手机端 (375x667)
- [ ] 汉堡菜单
- [ ] 单列布局
- [ ] 触摸友好按钮

### 5️⃣ 浏览器兼容性 (可选)
- [ ] Chrome/Edge (主要)
- [ ] Firefox
- [ ] Safari (iOS)
- [ ] Mobile Chrome (Android)

## 🐛 问题排查指南

### 问题1: 样式混乱/缺失
**症状**: 页面布局破坏，按钮无样式  
**原因**: CSS文件未正确加载  
**解决**:
```bash
# 检查文件是否存在
ls static/css/modules/

# 确认Flask静态文件路由
# 访问: http://localhost/static/css/modules/core.css
# 应该能看到CSS内容
```

### 问题2: 仍然看到紫色闪烁
**症状**: 刷新页面时短暂显示紫色背景  
**原因**: 内联CSS未生效  
**解决**:
```html
<!-- 确认<head>中有这段代码 -->
<style>
  :root { 
    --primary: #00704A; 
    --secondary: #008C54; 
  }
  body { 
    background: linear-gradient(135deg, #00704A 0%, #008C54 100%); 
  }
</style>
```

### 问题3: 缓存导致旧样式
**症状**: 更新CSS后页面样式未改变  
**解决**:
```bash
# 方法1: 强制刷新
Ctrl + F5 (Windows)
Cmd + Shift + R (Mac)

# 方法2: 清除浏览器缓存
DevTools → Application → Clear storage

# 方法3: 添加版本参数 (防止缓存)
# 修改模板：
# core.css?v=20240101
```

### 问题4: 某个页面加载279KB原CSS
**症状**: Network面板显示style.css  
**原因**: 该页面未迁移  
**解决**:
```bash
# 查找未迁移的页面
grep -r "css/style.css" templates/

# 更新为模块化CSS
<link rel="stylesheet" href="{{ url_for('static', filename='css/modules/core.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/modules/page-XXX.css') }}">
```

## 📊 性能对比测试

### 使用Chrome Lighthouse
1. 打开Chrome DevTools (F12)
2. 切换到 Lighthouse 标签
3. 选择 "Performance" 类别
4. 点击 "Analyze page load"

#### 期望分数
- **Performance**: 90+ 分 ✅
- **Best Practices**: 85+ 分 ✅
- **SEO**: 85+ 分 ✅

### 网络限速测试 (模拟慢速连接)
DevTools → Network → Throttling:
- **Fast 3G**: 首页 < 3秒 ✅
- **Slow 3G**: 首页 < 6秒 ✅

## 🔄 回滚方案 (万一出问题)

如果迁移后发现严重问题：

### 快速回滚步骤
```bash
# 1. 使用查找替换恢复所有模板
# 将: css/modules/core.css 和 css/modules/page-*.css
# 改回: css/style.css

# 2. 重启Flask应用
python run.py

# 3. 清除浏览器缓存
Ctrl + F5
```

### PowerShell批量回滚脚本
```powershell
# 恢复主要页面
$files = @(
  "templates/index.html",
  "templates/gallery.html",
  "templates/create.html",
  "templates/sunguo_class.html"
)

foreach ($file in $files) {
  $content = Get-Content $file -Raw
  $content = $content -replace 'css/modules/core\.css.*?>\s*<link rel="stylesheet"[^>]*css/modules/page-\w+\.css', 'css/style.css'
  Set-Content $file $content -NoNewline
}

Write-Host "回滚完成！请重启服务器" -ForegroundColor Green
```

## ✅ 完成确认

迁移验证完成后，在此打勾：

- [ ] 所有关键页面视觉正常
- [ ] CSS文件大小符合预期（27-84KB）
- [ ] 无紫色闪烁现象
- [ ] 响应式布局正常
- [ ] 动画和交互效果正常
- [ ] 性能指标达标
- [ ] 浏览器兼容性测试通过

## 📝 发现的问题记录

| 页面 | 问题描述 | 严重程度 | 状态 |
|------|---------|---------|------|
| 示例 | 按钮悬停效果缺失 | 低 | 已修复 |
|  |  |  |  |
|  |  |  |  |

---

**测试日期**: __________  
**测试人员**: __________  
**测试环境**: Windows / Mac / Linux  
**浏览器**: Chrome / Firefox / Safari  
**测试结果**: ✅ 通过 / ❌ 失败
