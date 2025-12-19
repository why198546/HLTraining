# HLTraining 项目自动激活虚拟环境
# 将此文件放在项目根目录，每次打开 PowerShell 时自动激活虚拟环境

Write-Host "🚀 正在激活虚拟环境..." -ForegroundColor Cyan

# 检查虚拟环境是否存在
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    & .\.venv\Scripts\Activate.ps1
    Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
    Write-Host ""
    Write-Host "可用命令:" -ForegroundColor Yellow
    Write-Host "  python run.py          - 启动开发服务器"
    Write-Host "  .\app.ps1 start        - 启动生产服务(后台)"
    Write-Host "  .\app.ps1 status       - 查看服务状态"
    Write-Host "  .\app.ps1 log          - 查看日志"
    Write-Host "  .\app.ps1 stop         - 停止服务"
    Write-Host ""
} else {
    Write-Host "⚠️  未找到虚拟环境，请先创建:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv"
    Write-Host ""
}
