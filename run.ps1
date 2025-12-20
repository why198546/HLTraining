# 松果AI平台 - 统一管理脚本
# 用法: .\run.ps1 <command> [options]

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [int]$Lines = 50,
    [switch]$Follow
)

$APP_NAME = "松果AI平台"
$PID_FILE = "app.pid"
$LOG_DIR = "logs"

function Show-Help {
    Write-Host ""
    Write-Host "松果AI平台 - 管理工具" -ForegroundColor Cyan
    Write-Host ("=" * 60)
    Write-Host ""
    Write-Host "用法:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 <command> [options]"
    Write-Host ""
    Write-Host "命令:" -ForegroundColor Yellow
    Write-Host "  start       启动服务(后台守护进程)"
    Write-Host "  stop        停止服务"
    Write-Host "  restart     重启服务"
    Write-Host "  status      查看运行状态"
    Write-Host "  log         查看日志"
    Write-Host "  help        显示此帮助信息"
    Write-Host ""
    Write-Host "日志选项:" -ForegroundColor Yellow
    Write-Host "  -Lines <N>  显示最后N行日志(默认50)"
    Write-Host "  -Follow     实时跟踪日志"
    Write-Host ""
    Write-Host "示例:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 start              # 启动服务"
    Write-Host "  .\run.ps1 status             # 查看状态"
    Write-Host "  .\run.ps1 log                # 查看最后50行日志"
    Write-Host "  .\run.ps1 log -Lines 100     # 查看最后100行"
    Write-Host "  .\run.ps1 log -Follow        # 实时跟踪日志"
    Write-Host ""
}

function Start-Service {
    Write-Host "正在启动服务..." -ForegroundColor Green
    
    if (Test-Path $PID_FILE) {
        $appPid = Get-Content $PID_FILE -ErrorAction SilentlyContinue
        if ($appPid) {
            $process = Get-Process -Id $appPid -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "服务已在运行 (PID: $appPid)" -ForegroundColor Yellow
                Write-Host "如需重启，请运行: .\run.ps1 restart" -ForegroundColor Yellow
                return
            }
        }
    }
    
    if (-not (Test-Path $LOG_DIR)) {
        New-Item -ItemType Directory -Path $LOG_DIR | Out-Null
    }
    
    $logFile = Join-Path $LOG_DIR "app_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    $errorLog = Join-Path $LOG_DIR "error.log"
    
    # 创建启动脚本（激活虚拟环境并启动应用）
    $startScript = @"
`$env:PYTHONIOENCODING='utf-8'
# 激活虚拟环境
& .\.venv\Scripts\Activate.ps1
# 启动应用
python run.py
"@
    $startScript | Out-File -FilePath "temp_start.ps1" -Encoding UTF8
    
    # 启动进程
    $processInfo = Start-Process -FilePath "powershell" -ArgumentList "-ExecutionPolicy Bypass -File temp_start.ps1" -WorkingDirectory $PSScriptRoot -RedirectStandardOutput $logFile -RedirectStandardError $errorLog -WindowStyle Hidden -PassThru
    
    Start-Sleep -Seconds 3
    
    if ($processInfo.HasExited) {
        Write-Host "启动失败！请查看日志：" -ForegroundColor Red
        Write-Host "  $logFile" -ForegroundColor Red
        Write-Host "  $errorLog" -ForegroundColor Red
        return
    }
    
    $processInfo.Id | Out-File -FilePath $PID_FILE -Encoding UTF8
    
    Write-Host "服务启动成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "进程信息:" -ForegroundColor Cyan
    Write-Host "  PID: $($processInfo.Id)"
    Write-Host "  日志: $logFile"
    Write-Host ""
    Write-Host "访问地址: http://127.0.0.1" -ForegroundColor White
    Write-Host ""
    Write-Host "查看状态: .\run.ps1 status"
    Write-Host "查看日志: .\run.ps1 log"
    Write-Host ""
}

function Stop-Service {
    Write-Host "正在停止服务..." -ForegroundColor Yellow
    
    $stopped = $false
    
    if (Test-Path $PID_FILE) {
        $appPid = Get-Content $PID_FILE -ErrorAction SilentlyContinue
        if ($appPid) {
            $process = Get-Process -Id $appPid -ErrorAction SilentlyContinue
            if ($process) {
                Stop-Process -Id $appPid -Force
                Write-Host "已停止进程 (PID: $appPid)" -ForegroundColor Green
                $stopped = $true
            }
            Remove-Item $PID_FILE -ErrorAction SilentlyContinue
        }
    }
    
    if (-not $stopped) {
        $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*run.py*"}
        
        if ($pythonProcesses) {
            foreach ($proc in $pythonProcesses) {
                Stop-Process -Id $proc.Id -Force
                Write-Host "已停止进程 (PID: $($proc.Id))" -ForegroundColor Green
                $stopped = $true
            }
        }
    }
    
    if ($stopped) {
        Write-Host "服务已停止" -ForegroundColor Green
    } else {
        Write-Host "未找到运行中的服务" -ForegroundColor Yellow
    }
}

function Restart-Service {
    Write-Host "正在重启服务..." -ForegroundColor Cyan
    Write-Host ""
    Stop-Service
    Start-Sleep -Seconds 2
    Start-Service
}

function Show-Status {
    Write-Host ""
    Write-Host "运行状态" -ForegroundColor Cyan
    Write-Host ("=" * 60)
    Write-Host ""
    
    if (Test-Path $PID_FILE) {
        $appPid = Get-Content $PID_FILE -ErrorAction SilentlyContinue
        if ($appPid) {
            $process = Get-Process -Id $appPid -ErrorAction SilentlyContinue
            
            if ($process) {
                Write-Host "状态: 运行中" -ForegroundColor Green
                Write-Host "进程ID: $appPid"
                Write-Host "内存使用: $([math]::Round($process.WorkingSet64 / 1MB, 2)) MB"
                
                $uptime = (Get-Date) - $process.StartTime
                Write-Host "运行时间: $($uptime.Days)天 $($uptime.Hours)小时 $($uptime.Minutes)分钟"
                Write-Host "访问地址: http://127.0.0.1" -ForegroundColor White
                
                $connection = Get-NetTCPConnection -LocalPort 80 -ErrorAction SilentlyContinue
                if ($connection) {
                    Write-Host "端口状态: 80 端口已监听" -ForegroundColor Green
                } else {
                    Write-Host "端口状态: 80 端口未监听" -ForegroundColor Yellow
                }
            } else {
                Write-Host "状态: 进程已终止" -ForegroundColor Red
                Write-Host "运行 .\run.ps1 start 重新启动"
            }
        }
    } else {
        Write-Host "状态: 未运行" -ForegroundColor Red
        Write-Host "运行 .\run.ps1 start 启动服务"
    }
    
    Write-Host ""
    
    if (Test-Path $LOG_DIR) {
        $latestLog = Get-ChildItem "$LOG_DIR\app_*.log" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        
        if ($latestLog) {
            Write-Host "最新日志: $($latestLog.Name)"
            Write-Host "  大小: $([math]::Round($latestLog.Length / 1KB, 2)) KB"
            Write-Host "  修改: $($latestLog.LastWriteTime)"
            Write-Host ""
            Write-Host "查看日志: .\run.ps1 log"
        }
    }
    Write-Host ""
}

function Show-Log {
    if (-not (Test-Path $LOG_DIR)) {
        Write-Host "日志目录不存在" -ForegroundColor Red
        return
    }
    
    $latestLog = Get-ChildItem "$LOG_DIR\app_*.log" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if (-not $latestLog) {
        Write-Host "未找到日志文件" -ForegroundColor Red
        return
    }
    
    Write-Host ""
    Write-Host "日志文件: $($latestLog.Name)" -ForegroundColor Cyan
    Write-Host ("=" * 60)
    Write-Host ""
    
    if ($Follow) {
        Write-Host "实时跟踪模式 (按 Ctrl+C 退出)" -ForegroundColor Yellow
        Write-Host ""
        Get-Content $latestLog.FullName -Wait -Tail $Lines
    } else {
        Get-Content $latestLog.FullName -Tail $Lines
        Write-Host ""
        Write-Host ("=" * 60)
        Write-Host "显示最后 $Lines 行" -ForegroundColor Cyan
        Write-Host "实时跟踪: .\run.ps1 log -Follow"
        Write-Host "更多行数: .\run.ps1 log -Lines 100"
        Write-Host ""
    }
}

switch ($Command.ToLower()) {
    "start"   { Start-Service }
    "stop"    { Stop-Service }
    "restart" { Restart-Service }
    "status"  { Show-Status }
    "log"     { Show-Log }
    "help"    { Show-Help }
    default   { 
        Write-Host "未知命令: $Command" -ForegroundColor Red
        Show-Help 
    }
}
