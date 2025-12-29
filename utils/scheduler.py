"""
定时任务处理器 - 处理松果币的自动充值和过期检查
"""
from datetime import datetime, timedelta
from auth.models import db, User, MonthlyTokenGrant, TokenExpiry, TokenGrantLog


def init_scheduler(app):
    """初始化定时任务调度器"""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        print("⚠️  APScheduler未安装，跳过定时任务初始化")
        print("   请运行: pip install apscheduler")
        return
    
    scheduler = BackgroundScheduler()
    
    # 添加任务：每天凌晨1点检查过期币
    scheduler.add_job(
        func=check_expired_tokens,
        trigger=CronTrigger(hour=1, minute=0),
        id='check_expired_tokens',
        name='检查过期松果币',
        replace_existing=True,
        args=[app]
    )
    
    # 添加任务：每月1号凌晨2点为教师/管理员自动充值
    scheduler.add_job(
        func=grant_monthly_tokens,
        trigger=CronTrigger(day=1, hour=2, minute=0),
        id='grant_monthly_tokens',
        name='月度自动充值',
        replace_existing=True,
        args=[app]
    )
    
    # 启动调度器
    try:
        if not scheduler.running:
            scheduler.start()
            print("✅ 定时任务已启动")
            print("   - 每天凌晨1:00 检查过期币")
            print("   - 每月1号凌晨2:00 为教师/管理员充值")
    except Exception as e:
        print(f"❌ 定时任务启动失败: {e}")


def check_expired_tokens(app):
    """检查并处理过期的松果币"""
    with app.app_context():
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查过期币...")
            
            # 获取所有用户并检查其过期币
            users = User.query.all()
            total_expired = 0
            processed_count = 0
            
            for user in users:
                expired_amount = user.check_token_expiry()
                if expired_amount > 0:
                    total_expired += expired_amount
                    processed_count += 1
                    
                    # 记录到日志
                    log = TokenGrantLog(
                        user_id=user.id,
                        grant_type='token_expired',
                        tokens_granted=-expired_amount,
                        description=f'松果币过期被扣除',
                        operator_name='system'
                    )
                    db.session.add(log)
            
            db.session.commit()
            
            print(f"✅ 过期币检查完成: {processed_count}个用户，共{total_expired}个币过期")
            
        except Exception as e:
            print(f"❌ 过期币检查失败: {e}")
            db.session.rollback()


def grant_monthly_tokens(app):
    """为教师和管理员自动充值月度松果币"""
    with app.app_context():
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始月度自动充值...")
            
            # 获取所有教师和管理员
            teachers = User.query.filter(User.role.in_(['teacher', 'admin'])).all()
            granted_count = 0
            skipped_count = 0
            total_amount = 0
            
            for user in teachers:
                success = user.grant_monthly_tokens()
                if success:
                    granted_count += 1
                    total_amount += 1000
                else:
                    skipped_count += 1
            
            print(f"✅ 月度自动充值完成: {granted_count}人充值成功，{skipped_count}人跳过，共充值{total_amount}个币")
            
        except Exception as e:
            print(f"❌ 月度自动充值失败: {e}")
            db.session.rollback()


def process_guest_tokens(app, user_id, tokens_amount, source, expire_days=30):
    """处理游客赠送的松果币（带过期时间）"""
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if user:
                user.add_temporary_tokens(tokens_amount, source, expire_days)
                print(f"✅ 为用户{user.nickname}添加{tokens_amount}个临时币（{expire_days}天有效）")
            else:
                print(f"❌ 用户{user_id}不存在")
        except Exception as e:
            print(f"❌ 添加临时币失败: {e}")
            db.session.rollback()
