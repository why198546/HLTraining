# 权限管理系统文档

## 功能概述

本次更新实现了完整的权限管理系统，包括：

### 1. 视频生成权限控制
- **限制：** 只有老师角色可以使用视频生成功能
- **实现：** 使用 `@teacher_required` 装饰器保护视频生成路由
- **路由：** `/api/generate-video`

### 2. 课程访问权限控制
- **报名要求：** 学生需要先报名才能访问松果课堂内容
- **课程顺序：** 学生必须按顺序完成课程
  - 第1节课：报名后直接访问
  - 第2-4节课：需要前一节课老师确认后才能访问
- **实现：** 使用 `@enrolled_required` 装饰器和课程进度检查
- **路由：** `/sunguo-class/<lesson_key>`

### 3. 图片生成令牌系统
- **默认令牌：** 每个新注册用户获得50个图片生成令牌
- **令牌消耗：** 每次生成图片消耗1个令牌
- **余额不足：** 令牌用完后无法生成图片，需要老师充值
- **实现：** 使用 `@image_token_required` 装饰器和 `consume_image_token()` 函数
- **路由：** `/generate-image`

## 数据库变更

### User 模型新增字段
```python
image_token_remaining = db.Column(db.Integer, default=50)  # 剩余图片生成令牌
is_enrolled = db.Column(db.Boolean, default=False)  # 是否已报名上课
```

### 新增 CourseProgress 模型
```python
class CourseProgress(db.Model):
    """课程进度追踪"""
    user_id              # 学生ID
    lesson_number        # 课程编号（1,2,3,4）
    lesson_key          # 课程标识（character, action, scene, practice）
    is_completed        # 是否完成
    is_confirmed        # 老师是否确认
    confirmed_by        # 确认老师的ID
    confirmed_at        # 确认时间
    started_at          # 开始时间
    completed_at        # 完成时间
    notes              # 老师备注
```

## 教师管理功能

### 管理后台页面
- **入口：** `/auth/teacher/dashboard`
- **功能：** 
  - 查看学生统计信息
  - 查看最近注册的学生
  - 快速访问学生管理

### 学生管理页面
- **入口：** `/auth/teacher/students`
- **功能：**
  - 查看所有学生列表
  - 设置学生报名状态
  - 为学生充值图片生成令牌
  - 查看学生详细信息

### 学生详情页面
- **入口：** `/auth/teacher/student/<student_id>`
- **功能：**
  - 查看学生基本信息
  - 管理图片生成令牌
  - 查看课程进度
  - 确认学生完成课程
  - 取消课程确认
  - 添加老师备注

## API 接口

### 设置学生报名
```
POST /auth/teacher/enroll-student/<student_id>
```

### 为学生充值令牌
```
POST /auth/teacher/add-tokens/<student_id>
Body: { "amount": 50 }
```

### 确认学生完成课程
```
POST /auth/teacher/confirm-lesson
Body: {
    "student_id": 1,
    "lesson_number": 1,
    "notes": "表现很好"
}
```

### 取消课程确认
```
POST /auth/teacher/unconfirm-lesson
Body: {
    "student_id": 1,
    "lesson_number": 1
}
```

## 使用流程

### 学生使用流程
1. 注册账号（自动获得50个图片生成令牌）
2. 等待老师设置为"已报名"状态
3. 访问第1节课开始学习
4. 完成第1节课后，等待老师确认
5. 老师确认后，可以访问第2节课
6. 依次完成后续课程

### 老师管理流程
1. 登录教师账号
2. 访问教师管理后台
3. 查看学生列表，设置学生为"已报名"
4. 查看学生课程进度
5. 确认学生完成的课程
6. 为令牌用完的学生充值

## 安装与迁移

### 运行数据库迁移
```powershell
python migrations/add_permission_system.py
```

这将：
- 创建 `course_progress` 表
- 为现有用户添加默认的令牌（50个）和报名状态（false）

### 设置第一个教师账号
如果需要将现有用户设置为教师：
```python
# 在 Python 控制台或脚本中
from auth.models import User, db
from app import create_app

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='教师用户名').first()
    user.role = 'teacher'
    db.session.commit()
```

## 权限装饰器

### @teacher_required
要求用户必须是教师角色

### @image_token_required
检查用户是否还有图片生成令牌

### @enrolled_required
要求用户必须已报名上课

### @lesson_access_required(lesson_number)
检查用户是否有权限访问指定课程

## 辅助函数

### consume_image_token(user)
消耗一个图片生成令牌

### add_image_tokens(user, amount)
为用户添加图片生成令牌（教师操作）

## 注意事项

1. **老师权限：** 老师可以访问所有课程和功能，不受限制
2. **令牌消耗：** 只有成功生成图片才会消耗令牌
3. **课程顺序：** 学生必须按1→2→3→4的顺序完成课程
4. **数据一致性：** 取消课程确认后，学生需要重新完成该课程

## 文件清单

### 新增文件
- `auth/permissions.py` - 权限装饰器和辅助函数
- `migrations/add_permission_system.py` - 数据库迁移脚本
- `templates/auth/teacher_dashboard.html` - 教师管理后台
- `templates/auth/teacher_students.html` - 学生管理页面
- `templates/auth/teacher_student_detail.html` - 学生详情页面

### 修改文件
- `auth/models.py` - 添加权限字段和CourseProgress模型
- `auth/routes.py` - 添加教师管理路由
- `app_legacy.py` - 添加权限检查到相关路由
