#!/usr/bin/env python3
"""
HLTraining v1.0 - 儿童AI培训网站启动器
适用于Windows双击运行
"""

import os
import sys
import webbrowser
import threading
import time
from app import app

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:8080')

def main():
    """主函数"""
    try:
        print("🚀 HLTraining v1.0 启动中...")
        print("📝 儿童AI培训网站")
        print("🌐 本地服务器将在 http://127.0.0.1:8080 启动")
        print("⏰ 稍等片刻，浏览器将自动打开...")
        print("🔧 关闭本窗口将停止服务器")
        print("-" * 50)
        
        # 在后台线程中延迟打开浏览器
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 启动Flask应用
        app.run(
            host='127.0.0.1',
            port=8080,
            debug=False,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("按回车键退出...")

if __name__ == '__main__':
    main()