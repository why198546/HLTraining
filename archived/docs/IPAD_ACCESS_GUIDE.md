# iPad 局域网访问配置指南

## ✅ 已配置的更改

### 1. **服务器监听地址**
已将 `.env` 文件中的 `HOST` 从 `127.0.0.1` 改为 `0.0.0.0`
- `127.0.0.1`: 仅本机访问
- `0.0.0.0`: 监听所有网络接口，允许局域网访问

### 2. **端口配置**
当前端口: `80` (HTTP标准端口)

---

## 🚀 使用步骤

### **步骤1: 获取电脑IP地址**

在PowerShell中运行:
```powershell
ipconfig
```

查找 `无线局域网适配器 WLAN` 或 `以太网适配器` 下的 `IPv4 地址`
例如: `192.168.1.100`

### **步骤2: 配置Windows防火墙**

#### 方法A: 快速开放端口（推荐）
```powershell
# 以管理员身份运行PowerShell，执行:
New-NetFirewallRule -DisplayName "HLTraining-HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
```

#### 方法B: 手动配置
1. 打开 `Windows Defender 防火墙`
2. 点击 `高级设置`
3. 选择 `入站规则` → `新建规则`
4. 选择 `端口` → `TCP` → 输入 `80`
5. 选择 `允许连接`
6. 命名为 `HLTraining-HTTP`

### **步骤3: 启动服务**

确保以管理员权限运行（端口80需要管理员权限）:
```powershell
.\run.ps1 start
```

### **步骤4: iPad访问**

在iPad的浏览器中访问:
```
http://192.168.1.100
```
（替换为你的实际IP地址）

---

## 🔍 故障排查

### **问题1: 无法访问**
✅ 检查电脑和iPad是否在同一Wi-Fi网络
✅ 确认防火墙规则已添加
✅ 确认服务正在运行: `.\run.ps1 status`
✅ 确认端口未被占用: `netstat -ano | findstr :80`

### **问题2: 端口80被占用**
如果端口80被占用（如IIS等），可以更改端口:

1. 修改 `.env` 文件:
```env
PORT=8080
```

2. 更新防火墙规则（以管理员运行）:
```powershell
New-NetFirewallRule -DisplayName "HLTraining-8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

3. iPad访问时加端口号:
```
http://192.168.1.100:8080
```

### **问题3: 权限不足**
端口80需要管理员权限，请以管理员身份运行PowerShell

### **问题4: iPad Safari无法访问**
- 确保使用 `http://` 而不是 `https://`
- 尝试清除Safari缓存
- 尝试使用其他浏览器（如Chrome）

---

## 📱 iPad优化建议

### **添加到主屏幕**
1. 在Safari中访问网站
2. 点击分享按钮
3. 选择 `添加到主屏幕`
4. 即可像APP一样快速启动

### **全屏模式**
1. 访问网站后点击地址栏的 `aA` 按钮
2. 选择 `隐藏工具栏`

### **手写笔优化**
当前已优化:
- ✅ 触摸压感支持
- ✅ 更大的按钮（44x44px）
- ✅ 防误触设计
- ✅ 流畅的绘图体验

---

## 🔒 安全提示

⚠️ **仅在受信任的局域网中使用**
- 此配置允许同一网络中的所有设备访问
- 不要在公共Wi-Fi中使用
- 生产环境请使用HTTPS和更严格的安全配置

---

## 🛠️ 快速命令参考

```powershell
# 查看本机IP
ipconfig

# 查看端口占用
netstat -ano | findstr :80

# 测试端口是否开放（从另一台设备）
Test-NetConnection -ComputerName 192.168.1.100 -Port 80

# 查看防火墙规则
Get-NetFirewallRule -DisplayName "HLTraining*"

# 删除防火墙规则（如需要）
Remove-NetFirewallRule -DisplayName "HLTraining-HTTP"

# 服务管理
.\run.ps1 start    # 启动
.\run.ps1 stop     # 停止
.\run.ps1 restart  # 重启
.\run.ps1 status   # 状态
.\run.ps1 log      # 查看日志
```

---

## ✨ 配置完成检查清单

- [ ] `.env` 文件 `HOST=0.0.0.0`
- [ ] 防火墙规则已添加
- [ ] 服务已启动
- [ ] 获取了电脑IP地址
- [ ] iPad和电脑在同一Wi-Fi
- [ ] iPad浏览器可以访问

完成后即可开始使用！🎉
