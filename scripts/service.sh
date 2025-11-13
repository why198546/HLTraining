#!/bin/bash

# AI创意工坊服务管理脚本
# 用法: ./service.sh {start|stop|restart|status|logs}

# 项目路径
PROJECT_DIR="/Users/hongyuwang/code/HLTraining"
PID_FILE="$PROJECT_DIR/app.pid"
LOG_FILE="$PROJECT_DIR/logs/app.log"
ERROR_LOG_FILE="$PROJECT_DIR/logs/error.log"

# 虚拟环境Python路径
PYTHON="$PROJECT_DIR/.venv/bin/python"
APP_FILE="$PROJECT_DIR/app.py"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 确保日志目录存在
mkdir -p "$PROJECT_DIR/logs"

# 检查进程是否运行
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            # PID文件存在但进程不存在，清理PID文件
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# 启动服务
start() {
    echo -e "${BLUE}🚀 启动AI创意工坊服务...${NC}"
    
    if is_running; then
        echo -e "${YELLOW}⚠️  服务已在运行中 (PID: $(cat $PID_FILE))${NC}"
        return 1
    fi
    
    # 检查Python和虚拟环境
    if [ ! -f "$PYTHON" ]; then
        echo -e "${RED}❌ 虚拟环境不存在: $PYTHON${NC}"
        echo -e "${YELLOW}💡 请先运行: python3 -m venv .venv${NC}"
        return 1
    fi
    
    # 检查app.py
    if [ ! -f "$APP_FILE" ]; then
        echo -e "${RED}❌ 应用文件不存在: $APP_FILE${NC}"
        return 1
    fi
    
    # 切换到项目目录
    cd "$PROJECT_DIR" || exit 1
    
    # 启动应用（后台运行）
    echo -e "${BLUE}📝 日志文件: $LOG_FILE${NC}"
    nohup "$PYTHON" "$APP_FILE" > "$LOG_FILE" 2> "$ERROR_LOG_FILE" &
    
    # 保存PID
    echo $! > "$PID_FILE"
    
    # 等待启动
    sleep 2
    
    if is_running; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}✅ 服务启动成功!${NC}"
        echo -e "${GREEN}   PID: $PID${NC}"
        echo -e "${GREEN}   访问地址: http://127.0.0.1:8088${NC}"
        echo -e "${BLUE}   查看日志: tail -f $LOG_FILE${NC}"
        return 0
    else
        echo -e "${RED}❌ 服务启动失败${NC}"
        echo -e "${YELLOW}💡 查看错误日志: cat $ERROR_LOG_FILE${NC}"
        return 1
    fi
}

# 停止服务
stop() {
    echo -e "${BLUE}🛑 停止AI创意工坊服务...${NC}"
    
    if ! is_running; then
        echo -e "${YELLOW}⚠️  服务未运行${NC}"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    echo -e "${BLUE}   正在停止进程 PID: $PID${NC}"
    
    # 优雅关闭
    kill "$PID" 2>/dev/null
    
    # 等待进程结束
    for i in {1..10}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            break
        fi
        sleep 1
        echo -n "."
    done
    echo
    
    # 如果还在运行，强制关闭
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}   进程未响应，强制关闭...${NC}"
        kill -9 "$PID" 2>/dev/null
        sleep 1
    fi
    
    # 清理PID文件
    rm -f "$PID_FILE"
    
    if ! is_running; then
        echo -e "${GREEN}✅ 服务已停止${NC}"
        return 0
    else
        echo -e "${RED}❌ 服务停止失败${NC}"
        return 1
    fi
}

# 重启服务
restart() {
    echo -e "${BLUE}🔄 重启AI创意工坊服务...${NC}"
    stop
    sleep 2
    start
}

# 查看状态
status() {
    echo -e "${BLUE}📊 AI创意工坊服务状态${NC}"
    echo "=================================="
    
    if is_running; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}状态: 运行中 ✅${NC}"
        echo -e "PID: $PID"
        
        # 显示进程信息
        if command -v ps &> /dev/null; then
            echo -e "\n进程信息:"
            ps -p "$PID" -o pid,ppid,%cpu,%mem,etime,command
        fi
        
        # 显示端口监听
        if command -v lsof &> /dev/null; then
            echo -e "\n端口监听:"
            lsof -Pan -p "$PID" -i TCP 2>/dev/null | grep LISTEN || echo "  无监听端口"
        fi
        
        # 显示最近日志
        if [ -f "$LOG_FILE" ]; then
            echo -e "\n最近日志 (最后10行):"
            tail -n 10 "$LOG_FILE"
        fi
        
    else
        echo -e "${RED}状态: 未运行 ❌${NC}"
        
        # 检查是否有错误日志
        if [ -f "$ERROR_LOG_FILE" ] && [ -s "$ERROR_LOG_FILE" ]; then
            echo -e "\n${YELLOW}最近错误:${NC}"
            tail -n 10 "$ERROR_LOG_FILE"
        fi
    fi
    
    echo "=================================="
}

# 查看日志
logs() {
    if [ ! -f "$LOG_FILE" ]; then
        echo -e "${YELLOW}⚠️  日志文件不存在: $LOG_FILE${NC}"
        return 1
    fi
    
    # 参数处理
    case "$1" in
        -f|--follow)
            echo -e "${BLUE}📄 实时查看日志 (Ctrl+C 退出)${NC}"
            tail -f "$LOG_FILE"
            ;;
        -e|--error)
            echo -e "${BLUE}📄 错误日志${NC}"
            if [ -f "$ERROR_LOG_FILE" ]; then
                cat "$ERROR_LOG_FILE"
            else
                echo -e "${YELLOW}⚠️  错误日志文件不存在${NC}"
            fi
            ;;
        -n)
            LINES="${2:-50}"
            echo -e "${BLUE}📄 最近 $LINES 行日志${NC}"
            tail -n "$LINES" "$LOG_FILE"
            ;;
        *)
            echo -e "${BLUE}📄 应用日志 (最后50行)${NC}"
            tail -n 50 "$LOG_FILE"
            ;;
    esac
}

# 主函数
main() {
    case "$1" in
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        status)
            status
            ;;
        logs)
            shift
            logs "$@"
            ;;
        *)
            echo -e "${BLUE}AI创意工坊服务管理脚本${NC}"
            echo "=================================="
            echo "用法: $0 {start|stop|restart|status|logs}"
            echo ""
            echo "命令说明:"
            echo "  start    - 启动服务"
            echo "  stop     - 停止服务"
            echo "  restart  - 重启服务"
            echo "  status   - 查看服务状态"
            echo "  logs     - 查看日志"
            echo "    -f     - 实时查看日志"
            echo "    -e     - 查看错误日志"
            echo "    -n N   - 查看最近N行日志"
            echo ""
            echo "示例:"
            echo "  $0 start         # 启动服务"
            echo "  $0 status        # 查看状态"
            echo "  $0 logs -f       # 实时查看日志"
            echo "  $0 logs -n 100   # 查看最近100行日志"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
