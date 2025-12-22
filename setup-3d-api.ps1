# 腾讯云AI3D配置脚本
# 运行此脚本来配置3D模型生成所需的API密钥

Write-Host "🎯 腾讯云AI3D服务配置助手" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已有.env文件
$envFile = ".env"
$envExists = Test-Path $envFile

if (-not $envExists) {
    Write-Host "📝 未找到.env文件，将从.env.example创建..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" $envFile
        Write-Host "✅ 已创建.env文件" -ForegroundColor Green
    } else {
        Write-Host "❌ 未找到.env.example文件" -ForegroundColor Red
        exit 1
    }
}

# 读取当前配置
$envContent = Get-Content $envFile -Raw

Write-Host ""
Write-Host "请输入腾讯云API密钥（从 https://console.cloud.tencent.com/cam/capi 获取）" -ForegroundColor Yellow
Write-Host ""

# 获取SecretId
$secretId = Read-Host "请输入 TENCENTCLOUD_SECRET_ID"
if ([string]::IsNullOrWhiteSpace($secretId)) {
    Write-Host "❌ SecretId 不能为空" -ForegroundColor Red
    exit 1
}

# 获取SecretKey
$secretKey = Read-Host "请输入 TENCENTCLOUD_SECRET_KEY"
if ([string]::IsNullOrWhiteSpace($secretKey)) {
    Write-Host "❌ SecretKey 不能为空" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "正在更新.env文件..." -ForegroundColor Yellow

# 更新或添加配置
if ($envContent -match "TENCENTCLOUD_SECRET_ID=.*") {
    $envContent = $envContent -replace "TENCENTCLOUD_SECRET_ID=.*", "TENCENTCLOUD_SECRET_ID=$secretId"
} else {
    $envContent += "`nTENCENTCLOUD_SECRET_ID=$secretId"
}

if ($envContent -match "TENCENTCLOUD_SECRET_KEY=.*") {
    $envContent = $envContent -replace "TENCENTCLOUD_SECRET_KEY=.*", "TENCENTCLOUD_SECRET_KEY=$secretKey"
} else {
    $envContent += "`nTENCENTCLOUD_SECRET_KEY=$secretKey"
}

# 保存文件
Set-Content $envFile $envContent -NoNewline

Write-Host "✅ 配置已保存到 $envFile" -ForegroundColor Green
Write-Host ""
Write-Host "🔄 请重启应用使配置生效：" -ForegroundColor Yellow
Write-Host "   1. 按 Ctrl+C 停止当前应用" -ForegroundColor White
Write-Host "   2. 运行: python run.py" -ForegroundColor White
Write-Host ""
Write-Host "📚 详细文档请查看: docs/3D_MODEL_CONFIG.md" -ForegroundColor Cyan
