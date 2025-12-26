# Bamboo Studio 集成指南

## 功能概述

网站现在支持将生成的3D模型直接在**Bamboo Studio**（拓竹切片软件）中打开，实现一键导入3D打印工作流。

## 已实现功能

### 1. 模型格式
- ✅ 默认生成 **STL格式** 模型
- ✅ STL是3D打印行业标准，所有切片软件都支持

### 2. 界面功能
在3D模型查看器中新增两个按钮：

#### 🔗 在Bamboo Studio中打开
- 使用 `bambustudio://` 协议直接调用本地软件
- 自动传递STL文件URL到Bamboo Studio
- 如果软件未安装，会提示用户下载

#### 📥 下载STL
- 直接下载STL文件到本地
- 可手动导入到任何3D打印软件

## 使用方法

### 第一次使用（需要配置Bamboo Studio）

#### 步骤1：安装Bamboo Studio
1. 访问拓竹官网：https://bambulab.cn
2. 下载并安装最新版本的Bamboo Studio

#### 步骤2：配置URL协议（如需）
Windows系统通常会自动注册协议，如果没有：

1. 创建注册表文件 `bamboo-protocol.reg`：
```reg
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\bambustudio]
@="URL:Bamboo Studio Protocol"
"URL Protocol"=""

[HKEY_CLASSES_ROOT\bambustudio\shell]

[HKEY_CLASSES_ROOT\bambustudio\shell\open]

[HKEY_CLASSES_ROOT\bambustudio\shell\open\command]
@="\"C:\\Program Files\\Bamboo Studio\\bambustudio.exe\" \"%1\""
```

2. 双击运行注册表文件

#### 步骤3：测试功能
1. 在网站上生成一个3D模型
2. 点击 "查看3D模型"
3. 点击 "在Bamboo Studio中打开"
4. 首次使用时浏览器会询问是否允许打开外部应用
5. 点击"允许"

### 日常使用流程

```
网站生成3D模型 → 查看模型 → 点击"在Bamboo Studio中打开" 
→ 模型自动加载到切片软件 → 开始切片打印
```

## 工作原理

### URL协议调用
```javascript
bambustudio://open?url=http://yoursite.com/models/model.stl
```

### 实现细节
1. 用户点击按钮
2. 前端生成完整的模型URL
3. 使用iframe触发自定义协议
4. 操作系统调用Bamboo Studio
5. Bamboo Studio下载并打开模型

### 降级处理
如果Bamboo Studio未安装或协议未注册：
- 1.5秒后自动检测
- 提示用户安装软件或直接下载STL文件
- 提供手动下载选项

## 兼容性

### 支持的3D打印软件
虽然按钮名称是"Bamboo Studio"，但生成的STL文件可用于：

| 软件 | 协议支持 | 手动导入 |
|------|---------|---------|
| Bamboo Studio | ✅ | ✅ |
| Cura | ❌ | ✅ |
| PrusaSlicer | ❌ | ✅ |
| Simplify3D | ❌ | ✅ |
| 其他切片软件 | ❌ | ✅ |

### 支持的导出格式
当前API配置支持（可在代码中切换）：
- ✅ **STL** - 当前默认
- ⭕ OBJ - 支持但未启用
- ⭕ GLB - 支持但未启用
- ⭕ USDZ - 支持但未启用
- ⭕ FBX - 支持但未启用

## 故障排查

### 问题1：点击按钮没反应
**可能原因**：
- Bamboo Studio未安装
- URL协议未注册

**解决方法**：
1. 确认已安装Bamboo Studio
2. 检查注册表中是否有 `bambustudio://` 协议
3. 使用"下载STL"按钮手动下载

### 问题2：浏览器拦截
**可能原因**：
- 浏览器安全设置阻止外部协议

**解决方法**：
1. 在浏览器提示框中选择"允许"
2. Chrome：设置 → 隐私和安全 → 网站设置 → 其他内容设置 → 协议处理程序
3. Firefox：选项 → 应用程序 → 找到 bambustudio 协议

### 问题3：模型在软件中打不开
**可能原因**：
- 模型文件损坏
- 网络传输问题

**解决方法**：
1. 重新生成3D模型
2. 使用"下载STL"直接下载到本地
3. 手动导入到Bamboo Studio

## 技术细节

### 修改的文件
1. **api/hunyuan3d.py** - 模型格式改为STL
2. **templates/components/artwork_modals.html** - 添加按钮
3. **static/js/artwork-modal.js** - 添加功能函数
4. **static/css/style.css** - 按钮样式

### 代码位置
```python
# api/hunyuan3d.py
"ResultFormat": "STL"  # 第113行和第220行
```

```javascript
// static/js/artwork-modal.js
function openInBambooStudio() { ... }  // 第625行
function downloadModel() { ... }       // 第668行
```

## 未来改进

### 可能的增强功能
- [ ] 支持多种切片软件的协议
- [ ] 一键切片并发送到打印机
- [ ] 支持选择导出格式（STL/OBJ/3MF）
- [ ] 批量下载多个模型
- [ ] 云端切片服务
- [ ] 打印预估时间和材料用量

## 参考链接

- [拓竹官网](https://bambulab.cn)
- [Bamboo Studio下载](https://bambulab.cn/download)
- [STL格式规范](https://en.wikipedia.org/wiki/STL_(file_format))
- [MakerWorld平台](https://makerworld.com.cn)

## 支持

如有问题，请：
1. 查看本文档的故障排查部分
2. 检查浏览器控制台的错误信息
3. 确认Bamboo Studio是否正常运行
4. 尝试手动下载STL文件测试

---

**版本**: 1.0  
**更新日期**: 2025-12-22  
**状态**: ✅ 已完成并测试
