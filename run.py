#!/usr/bin/env python3
"""
HLTraining v1.0 - 儿童AI培训网站智能启动器
支持进程管理和智能启动
"""

import os
import sys
import webbrowser
import threading
import time
import argparse
from flask_manager import FlaskProcessManager

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:8080')

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='HLTraining Flask应用启动器')
    parser.add_argument('--background', '-b', action='store_true', help='后台启动')
    parser.add_argument('--stop', '-s', action='store_true', help='停止运行的实例')
    parser.add_argument('--restart', '-r', action='store_true', help='重启应用')
    parser.add_argument('--status', '-i', action='store_true', help='查看运行状态')
    parser.add_argument('--force', '-f', action='store_true', help='强制操作')
    
    args = parser.parse_args()
    
    # 初始化进程管理器
    manager = FlaskProcessManager()
    
    # 处理命令行参数
    if args.status:
        manager.status()
        return
    
    if args.stop:
        print("🛑 停止Flask应用...")
        if manager.stop():
            print("✅ 应用已停止")
        else:
            print("❌ 停止失败或应用未运行")
        return
    
    if args.restart:
        print("🔄 重启Flask应用...")
        if manager.restart():
            print("✅ 应用已重启")
            if not args.background:
                # 打开浏览器
                browser_thread = threading.Thread(target=open_browser)
                browser_thread.daemon = True
                browser_thread.start()
        else:
            print("❌ 重启失败")
        return
    
    # 默认启动逻辑
    try:
        print("🚀 HLTraining v1.0 启动中...")
        print("📝 儿童AI培训网站")
        print("🌐 本地服务器: http://127.0.0.1:8080")
        print("-" * 50)
        
        # 检查是否已有实例运行
        proc = manager.get_running_process()
        if proc:
            print(f"⚠️ 检测到已运行的实例 (PID: {proc.pid})")
            
            if args.background:
                print("✅ 应用已在后台运行")
                return
            else:
                choice = input("选择操作: (1)打开浏览器 (2)重启 (3)退出 [1]: ").strip()
                if choice in ['', '1']:
                    print("🌐 打开浏览器...")
                    webbrowser.open('http://127.0.0.1:8080')
                    return
                elif choice == '2':
                    print("🔄 重启应用...")
                    if not manager.restart(background=False):
                        print("❌ 重启失败")
                        return
                else:
                    print("👋 退出")
                    return
        
        # 启动新实例
        if args.background:
            print("🔧 后台启动模式...")
            if manager.start_background():
                print("✅ 应用已在后台启动")
                print("💡 使用 'python run.py --status' 查看状态")
                print("💡 使用 'python run.py --stop' 停止应用")
            else:
                print("❌ 后台启动失败")
        else:
            print("⏰ 稍等片刻，浏览器将自动打开...")
            print("🔧 关闭本窗口将停止服务器")
            
            # 在后台线程中延迟打开浏览器
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # 前台启动
            manager.start_foreground()
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("按回车键退出...")

if __name__ == '__main__':
    main()