#!/usr/bin/env python3
"""
Flask应用进程管理器
提供启动、停止、重启、状态检查等功能
"""

import os
import sys
import signal
import psutil
import time
import subprocess
from pathlib import Path

class FlaskProcessManager:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.venv_python = self.project_dir / ".venv" / "bin" / "python"
        self.app_script = self.project_dir / "app.py"
        self.pid_file = self.project_dir / "flask_app.pid"
        self.log_file = self.project_dir / "flask_app.log"
        self.port = 8080
        
    def get_running_process(self):
        """获取当前运行的Flask进程"""
        try:
            # 首先检查PID文件
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    proc = psutil.Process(pid)
                    if proc.is_running() and 'app.py' in ' '.join(proc.cmdline()):
                        return proc
                else:
                    # PID文件存在但进程不存在，删除过期的PID文件
                    self.pid_file.unlink()
            
            # 如果PID文件不存在或无效，搜索所有Python进程
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if (proc.info['name'] == 'python' and 
                        proc.info['cmdline'] and 
                        'app.py' in ' '.join(proc.info['cmdline']) and
                        str(self.project_dir) in ' '.join(proc.info['cmdline'])):
                        return proc
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return None
        except Exception as e:
            print(f"检查进程时出错: {e}")
            return None
    
    def is_port_in_use(self):
        """检查端口是否被占用"""
        try:
            import socket
            # 尝试连接到端口
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', self.port))
                return result == 0
        except Exception:
            return False
    
    def kill_port_process(self):
        """杀死占用端口的进程"""
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr.port == self.port and conn.status == 'LISTEN':
                    proc = psutil.Process(conn.pid)
                    print(f"杀死占用端口{self.port}的进程: PID {conn.pid}")
                    proc.terminate()
                    time.sleep(1)
                    if proc.is_running():
                        proc.kill()
        except Exception as e:
            print(f"杀死端口进程时出错: {e}")
    
    def start_background(self):
        """在后台启动Flask应用"""
        proc = self.get_running_process()
        if proc:
            print(f"✅ Flask应用已经在运行 (PID: {proc.pid})")
            return True
        
        # 检查并清理端口
        if self.is_port_in_use():
            print("🔄 端口被占用，正在清理...")
            self.kill_port_process()
            time.sleep(2)
        
        print("🚀 启动Flask应用...")
        
        try:
            # 启动后台进程
            with open(self.log_file, 'w') as log:
                process = subprocess.Popen(
                    [str(self.venv_python), str(self.app_script)],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    cwd=str(self.project_dir),
                    start_new_session=True  # 创建新的进程组
                )
            
            # 保存PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # 等待应用启动
            print("⏳ 等待应用启动...")
            for i in range(10):
                time.sleep(1)
                if self.is_port_in_use():
                    print(f"✅ Flask应用已启动 (PID: {process.pid})")
                    print(f"🌐 访问地址: http://127.0.0.1:{self.port}")
                    print(f"📝 日志文件: {self.log_file}")
                    return True
                print(f"   等待中... ({i+1}/10)")
            
            print("❌ 应用启动超时")
            return False
            
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False
    
    def start_foreground(self):
        """在前台启动Flask应用"""
        proc = self.get_running_process()
        if proc:
            print(f"📱 将后台进程(PID: {proc.pid})调到前台...")
            # 先停止后台进程
            self.stop()
            time.sleep(2)
        
        # 检查并清理端口
        if self.is_port_in_use():
            print("🔄 端口被占用，正在清理...")
            self.kill_port_process()
            time.sleep(2)
        
        print("🚀 在前台启动Flask应用...")
        print("💡 按 Ctrl+C 可以停止应用")
        
        try:
            # 删除PID文件（因为这是前台进程）
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            # 前台运行
            os.chdir(str(self.project_dir))
            os.execv(str(self.venv_python), [str(self.venv_python), str(self.app_script)])
            
        except Exception as e:
            print(f"❌ 前台启动失败: {e}")
            return False
    
    def stop(self):
        """停止Flask应用"""
        proc = self.get_running_process()
        if not proc:
            print("ℹ️  没有运行的Flask应用")
            return True
        
        print(f"🛑 停止Flask应用 (PID: {proc.pid})")
        
        try:
            # 发送SIGTERM信号
            proc.terminate()
            
            # 等待进程结束
            for i in range(5):
                if not proc.is_running():
                    break
                time.sleep(1)
            
            # 如果还没结束，强制杀死
            if proc.is_running():
                print("💥 强制停止进程...")
                proc.kill()
                time.sleep(1)
            
            # 清理PID文件
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            print("✅ Flask应用已停止")
            return True
            
        except Exception as e:
            print(f"❌ 停止失败: {e}")
            return False
    
    def restart(self):
        """重启Flask应用"""
        print("🔄 重启Flask应用...")
        self.stop()
        time.sleep(2)
        return self.start_background()
    
    def status(self):
        """检查Flask应用状态"""
        proc = self.get_running_process()
        port_used = self.is_port_in_use()
        
        print("📊 Flask应用状态:")
        print("-" * 40)
        
        if proc:
            print(f"🟢 进程状态: 运行中 (PID: {proc.pid})")
            try:
                print(f"📈 CPU使用率: {proc.cpu_percent():.1f}%")
                memory_mb = proc.memory_info().rss / 1024 / 1024
                print(f"💾 内存使用: {memory_mb:.1f}MB")
                print(f"⏰ 运行时间: {time.time() - proc.create_time():.0f}秒")
            except Exception:
                pass
        else:
            print("🔴 进程状态: 未运行")
        
        if port_used:
            print(f"🌐 端口{self.port}: 已占用")
        else:
            print(f"🌐 端口{self.port}: 空闲")
        
        if self.log_file.exists():
            print(f"📝 日志文件: {self.log_file}")
            print(f"📄 日志大小: {self.log_file.stat().st_size / 1024:.1f}KB")
        
        return proc is not None
    
    def logs(self, lines=20):
        """显示日志"""
        if not self.log_file.exists():
            print("📝 没有日志文件")
            return
        
        print(f"📝 最近{lines}行日志:")
        print("-" * 40)
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    print(line.rstrip())
        except Exception as e:
            print(f"❌ 读取日志失败: {e}")

def main():
    """主函数"""
    manager = FlaskProcessManager()
    
    if len(sys.argv) < 2:
        print("🛠️  Flask进程管理器")
        print("=" * 50)
        print("用法:")
        print(f"  {sys.argv[0]} start     - 后台启动Flask应用")
        print(f"  {sys.argv[0]} fg        - 前台启动Flask应用")
        print(f"  {sys.argv[0]} stop      - 停止Flask应用")
        print(f"  {sys.argv[0]} restart   - 重启Flask应用")
        print(f"  {sys.argv[0]} status    - 查看应用状态")
        print(f"  {sys.argv[0]} logs      - 查看应用日志")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        manager.start_background()
    elif command == 'fg':
        manager.start_foreground()
    elif command == 'stop':
        manager.stop()
    elif command == 'restart':
        manager.restart()
    elif command == 'status':
        manager.status()
    elif command == 'logs':
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        manager.logs(lines)
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()