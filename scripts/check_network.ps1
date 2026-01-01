# GitHub Copilot 网络诊断脚本
# 用于检测和诊断 Copilot 连接问题

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Copilot 网络诊断工具" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. 检查基本网络连接
Write-Host "1. 检查基本网络连接..." -ForegroundColor Yellow
try {
    $ping = Test-Connection -ComputerName github.com -Count 2 -Quiet
    if ($ping) {
        Write-Host "✅ GitHub 网络连接正常" -ForegroundColor Green
    } else {
        Write-Host "❌ 无法连接到 GitHub" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ 网络连接测试失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. 检查 GitHub Copilot API 连接
Write-Host "`n2. 检查 GitHub Copilot API..." -ForegroundColor Yellow
$copilotUrls = @(
    "https://api.github.com",
    "https://copilot-proxy.githubusercontent.com"
)

foreach ($url in $copilotUrls) {
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 10 -UseBasicParsing
        Write-Host "✅ $url - 状态码: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "❌ $url - 连接失败" -ForegroundColor Red
        Write-Host "   错误: $($_.Exception.Message)" -ForegroundColor DarkRed
    }
}

# 3. 检查代理设置
Write-Host "`n3. 检查系统代理设置..." -ForegroundColor Yellow
$proxySettings = [System.Net.WebRequest]::GetSystemWebProxy()
$proxyUri = $proxySettings.GetProxy("https://github.com")

if ($proxyUri -eq "https://github.com") {
    Write-Host "✅ 未配置系统代理（直连）" -ForegroundColor Green
} else {
    Write-Host "⚠️  检测到系统代理: $proxyUri" -ForegroundColor Yellow
    Write-Host "   如果 Copilot 无法工作，请检查代理配置" -ForegroundColor Yellow
}

# 4. 检查环境变量
Write-Host "`n4. 检查代理环境变量..." -ForegroundColor Yellow
$proxyEnvVars = @("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "NO_PROXY", "no_proxy")
$foundProxy = $false

foreach ($var in $proxyEnvVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Host "⚠️  发现环境变量 $var = $value" -ForegroundColor Yellow
        $foundProxy = $true
    }
}

if (-not $foundProxy) {
    Write-Host "✅ 未配置代理环境变量" -ForegroundColor Green
}

# 5. 检查 VS Code 配置
Write-Host "`n5. 检查 VS Code 工作区配置..." -ForegroundColor Yellow
$settingsPath = ".vscode\settings.json"

if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
    
    if ($settings.'http.proxy') {
        Write-Host "⚠️  VS Code 代理配置: $($settings.'http.proxy')" -ForegroundColor Yellow
    } else {
        Write-Host "✅ VS Code 未配置代理" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  未找到 VS Code 工作区配置文件" -ForegroundColor Yellow
}

# 6. 建议
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "诊断建议" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n如果 Copilot 无法显示模型列表，请尝试：" -ForegroundColor White
Write-Host "1. 重启 VS Code" -ForegroundColor Gray
Write-Host "2. 检查 GitHub Copilot 扩展是否已登录" -ForegroundColor Gray
Write-Host "3. 如果使用代理，确保代理配置正确" -ForegroundColor Gray
Write-Host "4. 临时禁用代理测试：在 .vscode\settings.json 中注释掉 http.proxy" -ForegroundColor Gray
Write-Host "5. 清除 VS Code 缓存：关闭 VS Code，删除 %APPDATA%\Code\Cache" -ForegroundColor Gray
Write-Host "6. 重新登录 GitHub Copilot：Ctrl+Shift+P -> 'GitHub Copilot: Sign Out'" -ForegroundColor Gray

Write-Host "`n========================================`n" -ForegroundColor Cyan
