# iPad局域网访问 - 快速配置脚本

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "   iPad局域网访问 - 快速配置向导" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否以管理员权限运行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ 需要管理员权限来配置防火墙" -ForegroundColor Red
    Write-Host "请右键点击PowerShell，选择'以管理员身份运行'" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit
}

Write-Host "✅ 已以管理员权限运行" -ForegroundColor Green
Write-Host ""

# 步骤1: 获取本机IP地址
Write-Host "📡 步骤1: 获取本机IP地址" -ForegroundColor Yellow
Write-Host "----------------------------------------"

$ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.IPAddress -ne '127.0.0.1' -and $_.PrefixOrigin -eq 'Dhcp' -or $_.PrefixOrigin -eq 'Manual'
} | Select-Object IPAddress, InterfaceAlias

if ($ipAddresses.Count -eq 0) {
    Write-Host "❌ 未找到有效的IP地址" -ForegroundColor Red
    pause
    exit
}

Write-Host "找到以下IP地址:" -ForegroundColor Green
$ipAddresses | ForEach-Object {
    Write-Host "  • $($_.IPAddress) ($($_.InterfaceAlias))" -ForegroundColor Cyan
}

$primaryIP = $ipAddresses[0].IPAddress
Write-Host ""
Write-Host "将使用: $primaryIP" -ForegroundColor Green
Write-Host ""

# 步骤2: 检查.env配置
Write-Host "⚙️  步骤2: 检查服务器配置" -ForegroundColor Yellow
Write-Host "----------------------------------------"

$envFile = ".\.env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    if ($envContent -match "HOST=0\.0\.0\.0") {
        Write-Host "✅ HOST已配置为 0.0.0.0（允许局域网访问）" -ForegroundColor Green
    } else {
        Write-Host "⚠️  HOST未配置为 0.0.0.0" -ForegroundColor Yellow
        Write-Host "正在更新配置..." -ForegroundColor Yellow
        $envContent = $envContent -replace "HOST=127\.0\.0\.1", "HOST=0.0.0.0"
        Set-Content -Path $envFile -Value $envContent
        Write-Host "✅ 配置已更新" -ForegroundColor Green
    }
    
    # 获取端口配置
    if ($envContent -match "PORT=(\d+)") {
        $port = $matches[1]
        Write-Host "✅ 端口配置: $port" -ForegroundColor Green
    } else {
        $port = "80"
        Write-Host "⚠️  使用默认端口: 80" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ 未找到.env文件" -ForegroundColor Red
    pause
    exit
}
Write-Host ""

# 步骤3: 配置防火墙
Write-Host "🔥 步骤3: 配置Windows防火墙" -ForegroundColor Yellow
Write-Host "----------------------------------------"

$ruleName = "HLTraining-Port$port"

# 检查规则是否已存在
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if ($existingRule) {
    Write-Host "⚠️  防火墙规则已存在" -ForegroundColor Yellow
    $response = Read-Host "是否重新创建? (Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Remove-NetFirewallRule -DisplayName $ruleName
        Write-Host "已删除旧规则" -ForegroundColor Yellow
    } else {
        Write-Host "保持现有规则" -ForegroundColor Green
        Write-Host ""
        $skipFirewall = $true
    }
}

if (-not $skipFirewall) {
    try {
        New-NetFirewallRule -DisplayName $ruleName `
            -Direction Inbound `
            -Protocol TCP `
            -LocalPort $port `
            -Action Allow `
            -Profile Private,Domain `
            -Description "允许局域网访问HLTraining平台" | Out-Null
        Write-Host "✅ 防火墙规则创建成功" -ForegroundColor Green
    } catch {
        Write-Host "❌ 防火墙规则创建失败: $($_.Exception.Message)" -ForegroundColor Red
        pause
        exit
    }
}
Write-Host ""

# 步骤4: 检查端口占用
Write-Host "🔍 步骤4: 检查端口占用" -ForegroundColor Yellow
Write-Host "----------------------------------------"

$portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

if ($portInUse) {
    Write-Host "⚠️  端口 $port 已被占用" -ForegroundColor Yellow
    $portInUse | ForEach-Object {
        $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        Write-Host "  • 进程: $($process.ProcessName) (PID: $($_.OwningProcess))" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "建议:" -ForegroundColor Yellow
    Write-Host "  1. 停止占用端口的程序" -ForegroundColor Yellow
    Write-Host "  2. 或修改.env文件中的PORT配置" -ForegroundColor Yellow
} else {
    Write-Host "✅ 端口 $port 可用" -ForegroundColor Green
}
Write-Host ""

# 步骤5: 显示访问信息
Write-Host "📱 步骤5: iPad访问信息" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "请在iPad浏览器中访问:" -ForegroundColor Green
Write-Host ""
if ($port -eq "80") {
    Write-Host "  http://$primaryIP" -ForegroundColor Cyan -BackgroundColor Black
} else {
    Write-Host "  http://$primaryIP`:$port" -ForegroundColor Cyan -BackgroundColor Black
}
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 提示信息
Write-Host "📋 注意事项:" -ForegroundColor Yellow
Write-Host "  1. 确保iPad和电脑连接到同一Wi-Fi网络" -ForegroundColor White
Write-Host "  2. 如果无法访问，检查电脑的Wi-Fi是否开启" -ForegroundColor White
Write-Host "  3. 某些杀毒软件可能阻止访问，请临时关闭测试" -ForegroundColor White
Write-Host ""

# 询问是否启动服务
$response = Read-Host "是否现在启动服务? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "正在启动服务..." -ForegroundColor Green
    .\run.ps1 start
    Write-Host ""
    Write-Host "✅ 配置完成！现在可以从iPad访问了" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "提示: 稍后运行 .\run.ps1 start 启动服务" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
pause
