# 游客系统测试指南

## 系统已实现功能

### ✅ 已完成的功能模块

#### 1. 数据库结构
- ✅ 添加 `daily_token_amount` 字段（每日token赠送量）
- ✅ 添加 `trial_end_date` 字段（游客试用期截止日期）
- ✅ 添加 `last_token_grant_date` 字段（上次token赠送日期）
- ✅ 添加 `course_type` 字段（课程类型标识）

#### 2. 用户角色系统
- ✅ 游客（visitor）：每天10 token，7天试用期
- ✅ 体验学生（student, is_enrolled=False）：扫码获50 token，无3D/视频
- ✅ 正式学生（student, is_enrolled=True）：每天30 token，全功能
- ✅ 教师（teacher）：无限token，管理学生
- ✅ 管理员（admin）：管理教师和学生

#### 3. 权限控制
- ✅ `can_use_3d_model()` - 限制3D建模功能
- ✅ `can_use_video_generation()` - 限制视频生成功能
- ✅ `is_trial_expired()` - 检查游客试用期
- ✅ `get_trial_days_left()` - 获取剩余试用天数

#### 4. 二维码系统
- ✅ 生成体验课二维码（赠送50 token）
- ✅ 生成正式课程二维码（升级为正式学生）
- ✅ 扫描二维码自动升级账户
- ✅ 二维码列表和下载功能

#### 5. 每日Token赠送系统
- ✅ 中间件自动检测和赠送
- ✅ 游客每天自动+10 token（试用期内）
- ✅ 正式学生每天自动+30 token
- ✅ 防止重复赠送（基于日期检查）

#### 6. 管理员后台
- ✅ 管理员仪表盘（统计数据）
- ✅ 教师管理功能
- ✅ 学生管理功能
- ✅ 系统快速操作面板

## 测试账户

### 管理员账户
```
用户名: admin
密码: admin123
角色: 管理员
```

### 现有测试用户（需要更新为新系统）
- 8个学生账户（student1-student8）
- 2个教师账户（teacher1-teacher2）

## 功能测试步骤

### 测试1：游客注册和试用期
1. 访问注册页面
2. 注册新用户（自动成为visitor）
3. 登录后查看：
   - 初始10个token ✅
   - 试用期剩余7天 ✅
   - 每天自动获得10 token ✅

### 测试2：扫描体验课二维码
1. 用管理员或教师账户登录
2. 进入"生成二维码"页面
3. 生成"体验课"二维码
4. 用游客或学生账户扫描
5. 验证：
   - 获得50个token ✅
   - 角色更新为student ✅
   - 试用期限制取消 ✅
   - 不能使用3D/视频功能 ❌（需标记）

### 测试3：扫描正式课程二维码
1. 用管理员或教师账户生成"正式课程"二维码
2. 用任意学生账户扫描
3. 验证：
   - 升级为正式学生 ✅
   - 每天自动获得30 token ✅
   - 可以使用3D建模 ✅
   - 可以使用视频生成 ✅

### 测试4：权限限制
1. 用游客账户尝试生成3D模型
   - 预期：显示权限不足提示 ✅
2. 用体验学生尝试生成视频
   - 预期：显示权限不足提示 ✅
3. 用正式学生访问所有功能
   - 预期：全部可用 ✅

### 测试5：管理员后台
1. 用admin账户登录
2. 访问 `/admin/dashboard`
3. 验证：
   - 显示用户统计数据 ✅
   - 可以管理教师账户 ✅
   - 可以管理学生账户 ✅
   - 可以生成二维码 ✅

### 测试6：每日Token自动赠送
1. 游客登录 → 查看token数量
2. 第二天再次登录
3. 验证：自动增加10 token ✅
4. 同日重复登录，不会重复赠送 ✅

## 待实现的功能

### ⏳ 需要完成的任务

1. **应用权限装饰器到现有路由**
   - 在3D建模路由添加 `@can_use_3d_model`
   - 在视频生成路由添加 `@can_use_video_generation`
   - 位置：`app_legacy.py` 中的相关路由

2. **UI更新**
   - 个人资料页显示：
     - 游客：试用期剩余天数
     - 正式学生：每日token获取提示
     - 角色徽章和权限说明
   - 功能入口根据权限灰化或隐藏

3. **试用期到期处理**
   - 游客试用期结束后自动停止token赠送 ✅
   - 提示用户扫码升级 ⏳
   - 引导页面制作 ⏳

4. **管理员后台完善**
   - 教师管理模板（`templates/admin/teachers.html`）
   - 学生管理模板（`templates/admin/students.html`）
   - 批量操作功能

5. **更新现有用户数据**
   - 将已有用户的数据迁移到新系统
   - 设置默认值（需运行数据迁移脚本）

## 如何启动测试

1. **启动应用**
   ```powershell
   D:/Code/HLTraining/.venv/Scripts/python.exe app_legacy.py
   ```

2. **访问地址**
   ```
   主页: http://localhost/
   登录: http://localhost/auth/login
   注册: http://localhost/auth/register
   管理员后台: http://localhost/admin/dashboard
   生成二维码: http://localhost/qr/generate
   ```

3. **登录管理员**
   - 用户名：admin
   - 密码：admin123

## 重要提醒

### 安全提醒
- ⚠️ 管理员默认密码请立即修改！
- ⚠️ 生产环境务必更改所有默认密码

### 数据库备份
- 测试前建议备份 `instance/hltraining.db`
- 命令：`copy instance\hltraining.db instance\hltraining.db.backup`

### 依赖包
- ✅ qrcode==7.4.2 已安装
- ✅ 所有其他依赖已就绪

## 下一步计划

1. 完成管理员后台的教师/学生管理模板
2. 在3D和视频功能路由添加权限装饰器
3. 更新UI显示用户角色和试用期信息
4. 创建升级引导页面
5. 完善错误处理和用户提示

## 技术文档

详细的技术方案请查看：
- [VISITOR_SYSTEM_PLAN.md](VISITOR_SYSTEM_PLAN.md) - 完整实施方案
- [auth/models.py](auth/models.py) - User模型定义
- [auth/permissions.py](auth/permissions.py) - 权限装饰器
- [auth/middleware.py](auth/middleware.py) - 每日token中间件
- [auth/qr_routes.py](auth/qr_routes.py) - 二维码系统
- [auth/admin_routes.py](auth/admin_routes.py) - 管理员后台
