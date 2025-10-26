# Flask进程管理指南

## 概述
HLTraining 现在配备了智能的Flask进程管理系统，能够检测运行状态、后台启动、自动重启等。

## 基本用法

### 1. 启动应用
```bash
# 前台启动（默认模式）
python run.py

# 后台启动
python run.py -b
# 或
python run.py --background
```

### 2. 查看状态
```bash
python run.py -i
# 或
python run.py --status
```
显示信息包括：
- 进程状态（运行中/未运行）
- 进程ID (PID)
- CPU和内存使用率
- 运行时间
- 端口占用状态
- 日志文件信息

### 3. 停止应用
```bash
python run.py -s
# 或
python run.py --stop
```

### 4. 重启应用
```bash
python run.py -r
# 或
python run.py --restart
```

## 快捷命令参考

| 命令 | 简写 | 功能 |
|------|------|------|
| `--status` | `-i` | 查看运行状态 |
| `--background` | `-b` | 后台启动 |
| `--restart` | `-r` | 重启应用 |
| `--stop` | `-s` | 停止应用 |
| `--force` | `-f` | 强制操作 |

## 智能启动特性

### 冲突检测
当已有实例运行时，启动器会：
1. 检测到已运行的实例
2. 提供选项：
   - (1) 打开浏览器访问现有实例
   - (2) 重启应用
   - (3) 退出

### 后台模式
使用 `--background` 参数可以：
- 在后台启动Flask应用
- 不阻塞终端
- 通过PID文件跟踪进程
- 写入日志文件

## 文件结构

### 进程管理文件
- `flask_manager.py` - 核心进程管理器
- `run.py` - 智能启动脚本
- `flask_app.pid` - 进程ID文件（运行时生成）
- `flask_app.log` - 应用日志文件

## 常用场景

### 开发调试
```bash
# 启动开发服务器
python run.py

# 修改代码后重启
python run.py -r
```

### 后台运行
```bash
# 后台启动
python run.py -b

# 检查状态
python run.py -i

# 停止后台服务
python run.py -s
```

### 故障排除
```bash
# 查看详细状态
python run.py -i

# 查看最新日志
tail -f flask_app.log

# 强制重启
python run.py -r
```

## 技术特性

1. **进程检测**：自动检测已运行的Flask实例
2. **端口管理**：智能检测端口占用情况
3. **优雅停止**：先发送SIGTERM，必要时强制杀死
4. **日志记录**：完整的启动和运行日志
5. **错误处理**：完善的异常处理和用户反馈

## 注意事项

- 确保虚拟环境已激活
- 首次运行会自动创建必要的文件
- 日志文件会持续增长，定期清理
- 进程管理器需要psutil依赖包

## 兼容性

- 支持 macOS、Linux、Windows
- 兼容Python 3.7+
- 自动检测虚拟环境路径