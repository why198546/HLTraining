#!/bin/bash

# 松果AI平台 - 统一管理脚本
# 用法: ./run.sh <command> [options]

APP_NAME="松果AI平台"
PID_FILE="app.pid"
LOG_DIR="logs"
PORT=8088

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo ""
    echo -e "${CYAN}松果AI平台 - 管理工具${NC}"
    echo "============================================================"
    echo ""
    echo -e "${YELLOW}用法:${NC}"
    echo "  ./run.sh <command> [options]"
    echo ""
    echo -e "${YELLOW}命令:${NC}"
    echo "  start       启动服务(后台守护进程)"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  status      查看运行状态"
    echo "  log         查看日志 [lines]"
    echo "  follow      实时跟踪日志"
    echo "  help        显示此帮助信息"
    echo ""
    echo -e "${YELLOW}日志选项:${NC}"
    echo "  log [N]     显示最后N行日志(默认50)"
    echo "  follow      实时跟踪日志"
    echo ""
    echo -e "${YELLOW}示例:${NC}"
    echo "  ./run.sh start              # 启动服务"
    echo "  ./run.sh status             # 查看状态"
    echo "  ./run.sh log                # 查看最后50行日志"
    echo "  ./run.sh log 100            # 查看最后100行"
    echo "  ./run.sh follow             # 实时跟踪日志"
    echo ""
}

# 启动服务
start_service() {
    echo -e "${GREEN}正在启动服务...${NC}"
    
    # 检查是否已经运行
    if [ -f "$PID_FILE" ]; then
        APP_PID=$(cat "$PID_FILE")
        if kill -0 "$APP_PID" 2>/dev/null; then
            echo -e "${YELLOW}服务已在运行 (PID: $APP_PID)${NC}"
            echo -e "${YELLOW}如需重启，请运行: ./run.sh restart${NC}"
            return
        fi
    fi
    
    # 创建日志目录
    mkdir -p "$LOG_DIR"
    
    # 生成日志文件名
    LOG_FILE="$LOG_DIR/app_$(date +%Y%m%d_%H%M%S).log"
    ERROR_LOG="$LOG_DIR/error.log"
    
    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        echo -e "${RED}错误: 未找到虚拟环境 .venv${NC}"
        echo "请先运行: python -m venv .venv"
        exit 1
    fi
    
    # 激活虚拟环境并启动服务
    echo "日志文件: $LOG_FILE"
    
    # 后台启动
    nohup bash -c "source .venv/bin/activate && python run.py" > "$LOG_FILE" 2> "$ERROR_LOG" &
    
    APP_PID=$!
    echo $APP_PID > "$PID_FILE"
    
    # 等待几秒检查是否启动成功
    sleep 3
    
    if kill -0 "$APP_PID" 2>/dev/null; then
        echo -e "${GREEN}服务启动成功！${NC}"
        echo ""
        echo -e "${CYAN}进程信息:${NC}"
        echo "  PID: $APP_PID"
        echo "  日志: $LOG_FILE"
        echo ""
        echo -e "${WHITE}访问地址: http://127.0.0.1:$PORT${NC}"
        echo ""
        echo "查看状态: ./run.sh status"
        echo "查看日志: ./run.sh log"
        echo ""
    else
        echo -e "${RED}启动失败！请查看日志：${NC}"
        echo "  $LOG_FILE"
        echo "  $ERROR_LOG"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# 停止服务
stop_service() {
    echo -e "${YELLOW}正在停止服务...${NC}"
    
    STOPPED=false
    
    # 从PID文件停止
    if [ -f "$PID_FILE" ]; then
        APP_PID=$(cat "$PID_FILE")
        if kill -0 "$APP_PID" 2>/dev/null; then
            kill "$APP_PID"
            echo -e "${GREEN}已停止进程 (PID: $APP_PID)${NC}"
            STOPPED=true
        fi
        rm -f "$PID_FILE"
    fi
    
    # 查找并停止所有相关进程
    PYTHON_PIDS=$(pgrep -f "python.*run.py")
    if [ -n "$PYTHON_PIDS" ]; then
        for PID in $PYTHON_PIDS; do
            kill "$PID" 2>/dev/null
            echo -e "${GREEN}已停止进程 (PID: $PID)${NC}"
            STOPPED=true
        done
    fi
    
    # 清理端口
    if lsof -ti:$PORT >/dev/null 2>&1; then
        lsof -ti:$PORT | xargs kill -9 2>/dev/null
        echo -e "${GREEN}已清理端口 $PORT${NC}"
    fi
    
    if [ "$STOPPED" = true ]; then
        echo -e "${GREEN}服务已停止${NC}"
    else
        echo -e "${YELLOW}未找到运行中的服务${NC}"
    fi
}

# 重启服务
restart_service() {
    echo -e "${CYAN}正在重启服务...${NC}"
    echo ""
    stop_service
    sleep 2
    start_service
}

# 显示状态
show_status() {
    echo ""
    echo -e "${CYAN}运行状态${NC}"
    echo "============================================================"
    echo ""
    
    if [ -f "$PID_FILE" ]; then
        APP_PID=$(cat "$PID_FILE")
        if kill -0 "$APP_PID" 2>/dev/null; then
            echo -e "${GREEN}状态: 运行中${NC}"
            echo "进程ID: $APP_PID"
            
            # 获取内存使用
            if command -v ps >/dev/null; then
                MEM=$(ps -o rss= -p "$APP_PID" 2>/dev/null)
                if [ -n "$MEM" ]; then
                    MEM_MB=$((MEM / 1024))
                    echo "内存使用: ${MEM_MB} MB"
                fi
            fi
            
            # 获取运行时间
            if command -v ps >/dev/null; then
                UPTIME=$(ps -o etime= -p "$APP_PID" 2>/dev/null | tr -d ' ')
                if [ -n "$UPTIME" ]; then
                    echo "运行时间: $UPTIME"
                fi
            fi
            
            echo -e "${WHITE}访问地址: http://127.0.0.1:$PORT${NC}"
            
            # 检查端口
            if lsof -ti:$PORT >/dev/null 2>&1; then
                echo -e "${GREEN}端口状态: $PORT 端口已监听${NC}"
            else
                echo -e "${YELLOW}端口状态: $PORT 端口未监听${NC}"
            fi
        else
            echo -e "${RED}状态: 进程已终止${NC}"
            echo "运行 ./run.sh start 重新启动"
        fi
    else
        echo -e "${RED}状态: 未运行${NC}"
        echo "运行 ./run.sh start 启动服务"
    fi
    
    echo ""
    
    # 显示最新日志信息
    if [ -d "$LOG_DIR" ]; then
        LATEST_LOG=$(ls -t "$LOG_DIR"/app_*.log 2>/dev/null | head -1)
        if [ -n "$LATEST_LOG" ]; then
            echo "最新日志: $(basename "$LATEST_LOG")"
            if command -v stat >/dev/null; then
                # macOS 和 Linux 的 stat 命令不同
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    SIZE=$(stat -f%z "$LATEST_LOG")
                    MTIME=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$LATEST_LOG")
                else
                    SIZE=$(stat -c%s "$LATEST_LOG")
                    MTIME=$(stat -c "%y" "$LATEST_LOG" | cut -d. -f1)
                fi
                SIZE_KB=$((SIZE / 1024))
                echo "  大小: ${SIZE_KB} KB"
                echo "  修改: $MTIME"
            fi
            echo ""
            echo "查看日志: ./run.sh log"
        fi
    fi
    echo ""
}

# 查看日志
show_log() {
    LINES=${1:-50}
    
    if [ ! -d "$LOG_DIR" ]; then
        echo -e "${RED}日志目录不存在${NC}"
        return
    fi
    
    LATEST_LOG=$(ls -t "$LOG_DIR"/app_*.log 2>/dev/null | head -1)
    
    if [ -z "$LATEST_LOG" ]; then
        echo -e "${RED}未找到日志文件${NC}"
        return
    fi
    
    echo ""
    echo -e "${CYAN}日志文件: $(basename "$LATEST_LOG")${NC}"
    echo "============================================================"
    echo ""
    
    tail -n "$LINES" "$LATEST_LOG"
    
    echo ""
    echo "============================================================"
    echo -e "${CYAN}显示最后 $LINES 行${NC}"
    echo "实时跟踪: ./run.sh follow"
    echo "更多行数: ./run.sh log 100"
    echo ""
}

# 实时跟踪日志
follow_log() {
    if [ ! -d "$LOG_DIR" ]; then
        echo -e "${RED}日志目录不存在${NC}"
        return
    fi
    
    LATEST_LOG=$(ls -t "$LOG_DIR"/app_*.log 2>/dev/null | head -1)
    
    if [ -z "$LATEST_LOG" ]; then
        echo -e "${RED}未找到日志文件${NC}"
        return
    fi
    
    echo ""
    echo -e "${CYAN}日志文件: $(basename "$LATEST_LOG")${NC}"
    echo "============================================================"
    echo -e "${YELLOW}实时跟踪模式 (按 Ctrl+C 退出)${NC}"
    echo ""
    
    tail -f "$LATEST_LOG"
}

# 主命令处理
COMMAND=${1:-help}

case "$COMMAND" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    log)
        show_log "$2"
        ;;
    follow)
        follow_log
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}未知命令: $COMMAND${NC}"
        show_help
        exit 1
        ;;
esac
