#!/bin/bash
# 启动HLTraining项目的脚本

cd /Users/hongyuwang/code/HLTraining
source .venv/bin/activate

echo "🎨 HLTraining项目环境已激活！"
echo "当前Python路径: $(which python)"
echo "可用命令:"
echo "  python app.py          - 启动Flask服务器"
echo "  python recreate_db.py  - 重建数据库"
echo "  python test_gallery.py - 测试gallery页面"

# 保持shell打开
exec zsh