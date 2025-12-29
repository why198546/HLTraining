#!/usr/bin/env python
"""
系统完整性检查脚本 - 验证松果币系统的所有组件
"""
import os
import sys
import importlib.util

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - 文件不存在: {filepath}")
        return False

def check_module_import(module_path, class_name, description):
    """检查是否可以导入指定的模块和类"""
    try:
        spec = importlib.util.spec_from_file_location(module_path.replace('/', '.'), module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, class_name):
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description} - 类未找到: {class_name}")
            return False
    except Exception as e:
        print(f"❌ {description} - 导入失败: {e}")
        return False

def check_database_models():
    """检查数据库模型"""
    try:
        from app import create_app
        from auth.models import MonthlyTokenGrant, TokenExpiry, User
        
        print("✅ 数据库模型正确")
        
        # 检查 User 类是否有新方法
        required_methods = ['grant_monthly_tokens', 'check_token_expiry', 'add_temporary_tokens']
        for method in required_methods:
            if hasattr(User, method):
                print(f"   ✅ User.{method}() 方法存在")
            else:
                print(f"   ❌ User.{method}() 方法缺失")
                return False
        
        return True
    except ImportError as e:
        print(f"❌ 数据库模型导入失败: {e}")
        return False

def check_api_endpoints():
    """检查 API 端点是否存在"""
    try:
        from app import create_app
        from auth.routes import recharge_tokens, grant_monthly_tokens_api, get_token_balance
        from auth.admin_routes import (token_recharge_stats, get_token_recharge_stats, 
                                       export_token_recharge_stats)
        
        print("✅ API 端点正确")
        return True
    except ImportError as e:
        print(f"❌ API 端点导入失败: {e}")
        return False

def check_scheduler():
    """检查定时任务是否正确配置"""
    try:
        from utils.scheduler import init_scheduler, check_expired_tokens, grant_monthly_tokens
        
        print("✅ 定时任务模块正确")
        return True
    except ImportError as e:
        print(f"❌ 定时任务模块导入失败: {e}")
        return False

def check_dependencies():
    """检查依赖包是否已安装"""
    required_packages = {
        'apscheduler': 'APScheduler'
    }
    
    all_ok = True
    for package_name, display_name in required_packages.items():
        try:
            __import__(package_name)
            print(f"✅ {display_name} 已安装")
        except ImportError:
            print(f"❌ {display_name} 未安装 - 运行: pip install {package_name}")
            all_ok = False
    
    return all_ok

def check_app_integration():
    """检查应用是否正确集成了定时任务"""
    try:
        with open('app/__init__.py', 'r') as f:
            content = f.read()
            if 'init_scheduler' in content:
                print("✅ app/__init__.py 已集成定时任务")
                return True
            else:
                print("❌ app/__init__.py 未集成定时任务")
                return False
    except Exception as e:
        print(f"❌ 检查 app/__init__.py 失败: {e}")
        return False

def main():
    """执行完整性检查"""
    print("=" * 60)
    print("松果币充值系统 - 完整性检查")
    print("=" * 60)
    print()
    
    # 检查清单
    checks = [
        ("文件检查", lambda: all([
            check_file_exists('auth/models.py', '数据库模型文件'),
            check_file_exists('auth/routes.py', '用户路由文件'),
            check_file_exists('auth/admin_routes.py', '管理员路由文件'),
            check_file_exists('utils/scheduler.py', '定时任务处理器'),
            check_file_exists('templates/admin/token_recharge_stats.html', '统计页面'),
            check_file_exists('migrate_token_system.py', '数据库迁移脚本'),
            check_file_exists('COIN_RECHARGE_SYSTEM.md', '完整文档'),
            check_file_exists('COIN_RECHARGE_QUICK_START.md', '快速指南'),
        ])),
        ("依赖检查", check_dependencies),
        ("数据库模型检查", check_database_models),
        ("应用集成检查", check_app_integration),
        ("API 端点检查", check_api_endpoints),
        ("定时任务检查", check_scheduler),
    ]
    
    results = {}
    for check_name, check_func in checks:
        print(f"\n{'=' * 60}")
        print(f"【{check_name}】")
        print('=' * 60)
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            results[check_name] = False
    
    # 输出总结
    print(f"\n{'=' * 60}")
    print("检查总结")
    print('=' * 60)
    
    all_passed = True
    for check_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {check_name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 所有检查通过！系统可以部署使用。")
        print()
        print("后续步骤：")
        print("1. 运行迁移脚本: python migrate_token_system.py")
        print("2. 启动应用: python run.py")
        print("3. 访问统计页面: http://localhost/admin/token-recharge-stats")
        return 0
    else:
        print("⚠️  存在未通过的检查，请先解决上述问题。")
        print()
        print("常见问题:")
        print("- APScheduler 未安装: pip install apscheduler")
        print("- 文件缺失: 检查所有必需文件是否存在")
        print("- 模型缺失: 检查 auth/models.py 中的新模型定义")
        return 1

if __name__ == '__main__':
    sys.exit(main())
