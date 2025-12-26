"""测试松果币生成记录功能"""
import sys
sys.path.insert(0, '/Users/hongyuwang/code/HLTraining')

from datetime import datetime, timedelta
import random
from app import create_app
from auth.models import db, User, TokenGrantLog

app = create_app()

with app.app_context():
    # 获取所有学生
    students = User.query.filter(User.role.in_(['student', 'visitor'])).limit(10).all()
    
    if not students:
        print("❌ 没有找到学生用户")
        sys.exit(1)
    
    print(f"✅ 找到 {len(students)} 个用户")
    
    # 生成测试数据
    grant_types = [
        ('daily_grant', 10, '每日自动赠送'),
        ('daily_grant', 30, '每日自动赠送'),
        ('qr_scan_trial', 50, '扫描体验课二维码'),
        ('qr_scan_formal', 0, '扫描正式课二维码'),
        ('admin_manual', 100, '管理员手动增加'),
        ('teacher_manual', 50, '教师手动增加'),
    ]
    
    # 创建最近30天的测试数据
    for i in range(30):
        date = datetime.utcnow() - timedelta(days=i)
        
        # 每天为一些用户生成记录
        for student in random.sample(students, min(5, len(students))):
            grant_type, tokens, desc = random.choice(grant_types)
            
            log = TokenGrantLog(
                user_id=student.id,
                grant_type=grant_type,
                tokens_granted=tokens,
                description=f'{desc} {tokens} 松果币',
                created_at=date
            )
            db.session.add(log)
    
    db.session.commit()
    
    # 统计
    total_logs = TokenGrantLog.query.count()
    print(f"✅ 测试数据生成成功！")
    print(f"   总记录数: {total_logs}")
    
    # 按类型统计
    from sqlalchemy import func
    stats = db.session.query(
        TokenGrantLog.grant_type,
        func.count(TokenGrantLog.id).label('count'),
        func.sum(TokenGrantLog.tokens_granted).label('total')
    ).group_by(TokenGrantLog.grant_type).all()
    
    print("\n按来源统计：")
    for stat in stats:
        print(f"  {stat.grant_type}: {stat.count} 次，共 {stat.total} 松果币")
