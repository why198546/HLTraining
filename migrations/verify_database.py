#!/usr/bin/env python3
"""
数据库结构验证脚本
用于检查数据库结构是否与模型定义一致
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from auth.models import db
import sqlalchemy as sa


def verify_database_structure():
    """验证数据库结构"""
    app = create_app()
    
    with app.app_context():
        inspector = sa.inspect(db.engine)
        
        print('=' * 60)
        print('数据库结构验证报告')
        print('=' * 60)
        print()
        
        # 获取所有表
        tables = inspector.get_table_names()
        print(f'📊 数据库表数量: {len(tables)}')
        print()
        
        # 定义期望的表结构
        expected_tables = {
            'users': [
                'id', 'username', 'nickname', 'birth_date', 'gender',
                'contact_phone', 'mailing_address', 'parent_email',
                'avatar_url', 'password_hash', 'is_verified',
                'verification_token', 'created_at', 'last_login',
                'role', 'color_preference', 'privacy_settings',
                'image_token_remaining', 'is_enrolled', 'daily_token_amount',
                'trial_end_date', 'last_token_grant_date', 'course_type',
                'feedback_templates'  # 新增字段
            ],
            'artworks': [
                'id', 'session_id', 'title', 'description',
                'original_sketch', 'colored_image', 'figurine_image',
                'model_3d', 'video_file', 'all_colored_versions',
                'all_adjusted_versions', 'artist_name', 'artist_age',
                'category', 'style_type', 'color_preference',
                'expert_mode', 'prompt_text', 'video_prompt',
                'video_aspect_ratio', 'video_padding_mode',
                'status', 'created_at', 'updated_at', 'user_id',
                'is_featured', 'is_public', 'featured_at',
                'view_count', 'like_count', 'vote_count'
            ],
            'canvas_projects': [
                'id', 'project_id', 'user_id', 'title', 'project_type',
                'description', 'thumbnail', 'width', 'height',
                'canvas_data', 'chat_history', 'created_at', 'updated_at',
                'last_accessed', 'last_opened_at', 'image_count', 'is_deleted'
            ],
            'course_progress': [
                'id', 'user_id', 'lesson_number', 'lesson_key',
                'is_completed', 'is_confirmed', 'confirmed_by',
                'confirmed_at', 'started_at', 'completed_at', 'notes'
            ],
            'courses': [
                'id', 'course_code', 'course_name', 'course_key',
                'course_type', 'created_by', 'created_at', 'max_uses',
                'current_uses', 'expires_at', 'tokens_reward',
                'is_active', 'qr_image_path', 'description'
            ],
            'token_grant_logs': [
                'id', 'user_id', 'grant_type', 'tokens_granted',
                'created_at', 'description', 'operator_id',
                'operator_name', 'related_id', 'related_info'
            ],
            'token_usage_logs': [
                'id', 'user_id', 'usage_type', 'tokens_used',
                'created_at', 'description'
            ],
            'monthly_token_grants': [
                'id', 'user_id', 'grant_year', 'grant_month',
                'tokens_amount', 'granted_at'
            ],
            'token_expiries': [
                'id', 'user_id', 'grant_log_id', 'tokens_amount',
                'grant_source', 'expire_date', 'is_expired',
                'expired_at', 'created_at'
            ]
        }
        
        all_ok = True
        
        # 检查每个表
        for table_name, expected_columns in expected_tables.items():
            print(f'🔍 检查表: {table_name}')
            
            if table_name not in tables:
                print(f'   ❌ 表不存在！')
                all_ok = False
                continue
            
            # 获取实际列
            actual_columns = [col['name'] for col in inspector.get_columns(table_name)]
            
            # 检查缺失的列
            missing = set(expected_columns) - set(actual_columns)
            if missing:
                print(f'   ❌ 缺少字段: {", ".join(missing)}')
                all_ok = False
            
            # 检查多余的列
            extra = set(actual_columns) - set(expected_columns)
            if extra:
                print(f'   ⚠️  额外字段: {", ".join(extra)}')
            
            if not missing and not extra:
                print(f'   ✅ 结构正确 ({len(actual_columns)} 个字段)')
            
            print()
        
        # 总结
        print('=' * 60)
        if all_ok:
            print('✅ 数据库结构验证通过！')
            return 0
        else:
            print('❌ 数据库结构存在问题，请检查上述错误')
            return 1


def check_specific_field(table_name, field_name):
    """检查特定字段是否存在"""
    app = create_app()
    
    with app.app_context():
        inspector = sa.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        
        if field_name in columns:
            print(f'✅ {table_name}.{field_name} 存在')
            
            # 获取字段详情
            for col in inspector.get_columns(table_name):
                if col['name'] == field_name:
                    print(f'   类型: {col["type"]}')
                    print(f'   可空: {col["nullable"]}')
                    if col.get('default'):
                        print(f'   默认值: {col["default"]}')
            return True
        else:
            print(f'❌ {table_name}.{field_name} 不存在')
            return False


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 2:
        # 检查特定字段
        table = sys.argv[1]
        field = sys.argv[2]
        check_specific_field(table, field)
    else:
        # 完整验证
        exit_code = verify_database_structure()
        sys.exit(exit_code)
