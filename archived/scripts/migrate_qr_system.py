"""
数据库迁移脚本 - 添加Course和CourseEnrollment表
用于支持二维码系统的完整功能：
- Course表：存储生成的课程二维码信息
- CourseEnrollment表：记录学生扫描二维码的历史
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.models import Course, CourseEnrollment, db
from run import create_app


def migrate_qr_system():
    """迁移二维码系统数据库表"""
    print("开始二维码系统数据库迁移...")
    
    app = create_app()
    with app.app_context():
        try:
            # 创建Course和CourseEnrollment表
            print("创建Course表...")
            db.create_all()
            print("✅ Course表创建成功")
            
            print("创建CourseEnrollment表...")
            # db.create_all()会自动创建所有不存在的表
            print("✅ CourseEnrollment表创建成功")
            
            # 验证表是否创建成功
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'courses' in tables:
                print("✅ courses表已存在")
            else:
                print("❌ courses表创建失败")
                return False
            
            if 'course_enrollments' in tables:
                print("✅ course_enrollments表已存在")
            else:
                print("❌ course_enrollments表创建失败")
                return False
            
            print("\n迁移完成！新增功能：")
            print("1. ✅ 课程信息保存到数据库（不再仅依赖文件名）")
            print("2. ✅ 支持设置二维码使用次数限制")
            print("3. ✅ 支持设置二维码过期时间")
            print("4. ✅ 记录每次扫描的详细信息（谁、何时、用什么设备）")
            print("5. ✅ 防止同一用户重复扫描同一个二维码")
            print("6. ✅ 统计每个二维码的使用情况")
            print("7. ✅ 教师可查看二维码创建者和创建时间")
            
            return True
            
        except Exception as e:
            print(f"❌ 迁移失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate_qr_system()
    if success:
        print("\n🎉 二维码系统升级成功！现在可以重启应用使用新功能。")
    else:
        print("\n⚠️ 迁移过程中出现错误，请检查上面的错误信息。")
    
    sys.exit(0 if success else 1)
