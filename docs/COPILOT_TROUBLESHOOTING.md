# GitHub Copilot 故障排除指南

## 常见问题

### 1. 无法显示模型列表

**症状**: 打开 Copilot Chat 时，模型列表无法加载或显示空白

**可能原因**:
- 网络连接问题
- 代理配置不正确
- VS Code 缓存损坏
- GitHub Copilot 认证过期

**解决方案**:

#### 快速诊断
```powershell
# 运行网络诊断脚本
.\scripts\check_network.ps1
```

#### 方案 1: 禁用代理（如果你不需要代理）
```powershell
.\scripts\fix_copilot.ps1 -DisableProxy
```

#### 方案 2: 配置正确的代理
```powershell
.\scripts\fix_copilot.ps1 -EnableProxy -ProxyUrl "http://127.0.0.1:7890"
```

#### 方案 3: 清除缓存
```powershell
.\scripts\fix_copilot.ps1 -ClearCache
```

#### 方案 4: 手动重新登录
1. 按 `Ctrl+Shift+P` 打开命令面板
2. 输入 `GitHub Copilot: Sign Out`
3. 重启 VS Code
4. 按 `Ctrl+Shift+P` 输入 `GitHub Copilot: Sign In`

### 2. 代理配置

#### 检查当前代理状态
在 `.vscode\settings.json` 中查看：
```jsonc
// 如果使用代理
"http.proxy": "http://127.0.0.1:7890",
"http.proxyStrictSSL": false,

// 如果不使用代理，确保这些行被注释
// "http.proxy": "http://127.0.0.1:7890",
// "http.proxyStrictSSL": false,
```

#### 常见代理端口
- Clash: `http://127.0.0.1:7890`
- V2Ray: `http://127.0.0.1:10809`
- Shadowsocks: `http://127.0.0.1:1080`

### 3. 网络环境检查

#### 国内网络环境
如果你在国内使用 Copilot，可能需要：
1. 使用稳定的代理工具（Clash、V2Ray 等）
2. 确保代理工具的 TUN 模式或系统代理已启用
3. 在 VS Code 中配置代理地址

#### 企业网络环境
如果在企业网络中：
1. 询问 IT 部门代理服务器地址
2. 配置企业代理：
   ```jsonc
   "http.proxy": "http://proxy.company.com:8080",
   "http.proxyStrictSSL": true,
   ```

## 预防措施

### 1. 项目工作区配置
我们已经在 `.vscode\settings.json` 中添加了完整的 Copilot 配置。每次克隆项目后，这些配置会自动生效。

### 2. 定期检查
建议每周运行一次诊断脚本：
```powershell
.\scripts\check_network.ps1
```

### 3. 保持扩展更新
1. 打开 VS Code 扩展面板 (`Ctrl+Shift+X`)
2. 搜索 "GitHub Copilot"
3. 确保扩展是最新版本

### 4. 监控网络状态
如果使用代理：
- 确保代理工具在 Copilot 使用期间保持运行
- 检查代理工具的连接状态和延迟

## 快速参考

| 问题 | 命令 |
|------|------|
| 诊断网络问题 | `.\scripts\check_network.ps1` |
| 禁用代理 | `.\scripts\fix_copilot.ps1 -DisableProxy` |
| 启用代理 | `.\scripts\fix_copilot.ps1 -EnableProxy` |
| 清除缓存 | `.\scripts\fix_copilot.ps1 -ClearCache` |
| 重新加载窗口 | `Ctrl+Shift+P` → "Reload Window" |

## 联系支持

如果以上方法都无法解决问题：
1. 查看 VS Code 输出面板 (`Ctrl+Shift+U`)
2. 选择 "GitHub Copilot" 频道查看详细日志
3. 访问 [GitHub Copilot 官方文档](https://docs.github.com/copilot)
4. 在项目仓库提交 Issue

## 相关文件

- [.vscode/settings.json](.vscode/settings.json) - VS Code 工作区配置
- [scripts/check_network.ps1](scripts/check_network.ps1) - 网络诊断脚本
- [scripts/fix_copilot.ps1](scripts/fix_copilot.ps1) - 快速修复脚本
