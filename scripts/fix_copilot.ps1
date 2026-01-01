# GitHub Copilot 快速修复脚本
# 当遇到 Copilot 问题时运行此脚本

param(
    [switch]$ClearCache,
    [switch]$DisableProxy,
    [switch]$EnableProxy,
    [string]$ProxyUrl = "http://127.0.0.1:7890"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Copilot 快速修复工具" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$settingsPath = ".vscode\settings.json"

# 清除缓存
if ($ClearCache) {
    Write-Host "清除 VS Code 缓存..." -ForegroundColor Yellow
    
    $cachePaths = @(
        "$env:APPDATA\Code\Cache",
        "$env:APPDATA\Code\CachedData",
        "$env:APPDATA\Code\Code Cache"
    )
    
    foreach ($path in $cachePaths) {
        if (Test-Path $path) {
            Write-Host "删除: $path" -ForegroundColor Gray
            Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "✅ 已删除" -ForegroundColor Green
        }
    }
    
    Write-Host "`n⚠️  请重启 VS Code 以使更改生效" -ForegroundColor Yellow
}

# 禁用代理
if ($DisableProxy) {
    Write-Host "禁用代理配置..." -ForegroundColor Yellow
    
    if (Test-Path $settingsPath) {
        $content = Get-Content $settingsPath -Raw
        
        # 注释掉代理配置
        $content = $content -replace '(\s*"http\.proxy":\s*".+")', '// $1'
        $content = $content -replace '(\s*"http\.proxyStrictSSL":\s*(true|false))', '// $1'
        
        $content | Set-Content $settingsPath -NoNewline
        Write-Host "✅ 已禁用代理配置" -ForegroundColor Green
        Write-Host "⚠️  请重新加载 VS Code 窗口: Ctrl+Shift+P -> 'Reload Window'" -ForegroundColor Yellow
    } else {
        Write-Host "❌ 未找到配置文件" -ForegroundColor Red
    }
}

# 启用代理
if ($EnableProxy) {
    Write-Host "启用代理配置: $ProxyUrl" -ForegroundColor Yellow
    
    if (Test-Path $settingsPath) {
        $content = Get-Content $settingsPath -Raw
        
        # 取消注释或添加代理配置
        if ($content -match '//\s*"http\.proxy"') {
            $content = $content -replace '//\s*("http\.proxy":\s*".+")', '$1'
            $content = $content -replace '//\s*("http\.proxyStrictSSL":\s*(true|false))', '$1'
        } else {
            # 在配置文件中添加代理设置
            $content = $content -replace '("github\.copilot\.enable":\s*{[^}]+})', "`$1,`n    `"http.proxy`": `"$ProxyUrl`",`n    `"http.proxyStrictSSL`": false"
        }
        
        $content | Set-Content $settingsPath -NoNewline
        Write-Host "✅ 已启用代理配置" -ForegroundColor Green
        Write-Host "⚠️  请重新加载 VS Code 窗口: Ctrl+Shift+P -> 'Reload Window'" -ForegroundColor Yellow
    } else {
        Write-Host "❌ 未找到配置文件" -ForegroundColor Red
    }
}

# 如果没有参数，显示帮助
if (-not ($ClearCache -or $DisableProxy -or $EnableProxy)) {
    Write-Host "使用方法：" -ForegroundColor White
    Write-Host "  .\scripts\fix_copilot.ps1 -ClearCache          # 清除 VS Code 缓存" -ForegroundColor Gray
    Write-Host "  .\scripts\fix_copilot.ps1 -DisableProxy        # 禁用代理（直连）" -ForegroundColor Gray
    Write-Host "  .\scripts\fix_copilot.ps1 -EnableProxy         # 启用代理" -ForegroundColor Gray
    Write-Host "  .\scripts\fix_copilot.ps1 -EnableProxy -ProxyUrl 'http://proxy:port'  # 自定义代理" -ForegroundColor Gray
    Write-Host "`n常见问题解决流程：" -ForegroundColor White
    Write-Host "  1. 先运行网络诊断: .\scripts\check_network.ps1" -ForegroundColor Gray
    Write-Host "  2. 尝试禁用代理: .\scripts\fix_copilot.ps1 -DisableProxy" -ForegroundColor Gray
    Write-Host "  3. 如果还不行，清除缓存: .\scripts\fix_copilot.ps1 -ClearCache" -ForegroundColor Gray
}

Write-Host "`n========================================`n" -ForegroundColor Cyan
