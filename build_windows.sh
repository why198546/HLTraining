#!/bin/bash
# HLTraining v1.0 打包脚本

echo "🚀 开始打包 HLTraining v1.0..."

# 检查是否安装了pyinstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller 未安装，正在安装..."
    pip install pyinstaller
fi

# 创建打包目录
echo "📁 创建打包目录..."
mkdir -p dist/HLTraining-v1.0-Windows

# 清理之前的构建
echo "🧹 清理之前的构建..."
rm -rf build dist/HLTraining

# 使用PyInstaller打包
echo "📦 开始打包..."
pyinstaller HLTraining.spec --clean

# 检查打包是否成功
if [ -d "dist/HLTraining" ]; then
    echo "✅ 打包成功！"
    
    # 复制额外文件
    echo "📋 复制说明文档..."
    cp WINDOWS_INSTALL_GUIDE.md "dist/HLTraining/"
    cp README.md "dist/HLTraining/"
    cp .env.example "dist/HLTraining/"
    
    # 创建启动批处理文件
    echo "⚡ 创建启动脚本..."
    cat > "dist/HLTraining/启动HLTraining.bat" << 'EOF'
@echo off
chcp 65001 > nul
title HLTraining v1.0 - 儿童AI培训网站
echo.
echo 🚀 HLTraining v1.0 启动中...
echo 📝 儿童AI培训网站
echo.
echo ⏰ 请稍等，正在启动服务器...
echo 🌐 浏览器将自动打开网站
echo 🔧 关闭此窗口将停止服务器
echo.
HLTraining.exe
pause
EOF
    
    # 重命名目录
    mv "dist/HLTraining" "dist/HLTraining-v1.0-Windows"
    
    echo "📁 打包完成！位置：dist/HLTraining-v1.0-Windows/"
    echo ""
    echo "📝 打包内容："
    echo "   ├── HLTraining.exe          # 主程序"
    echo "   ├── 启动HLTraining.bat      # 启动脚本（推荐使用）"
    echo "   ├── WINDOWS_INSTALL_GUIDE.md # 安装使用说明"
    echo "   ├── README.md               # 项目说明"
    echo "   ├── .env.example            # 环境变量模板"
    echo "   └── 其他依赖文件..."
    echo ""
    echo "🎯 使用方法："
    echo "   1. 解压到任意目录"
    echo "   2. 双击'启动HLTraining.bat'或'HLTraining.exe'"
    echo "   3. 等待浏览器自动打开网站"
    echo ""
    echo "✅ 可以创建zip压缩包进行分发！"
else
    echo "❌ 打包失败，请检查错误信息"
fi