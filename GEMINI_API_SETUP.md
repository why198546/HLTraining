# Gemini API 配置说明

## 获取 Gemini API 密钥

1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 登录您的Google账户
3. 点击 "Create API Key" 创建新的API密钥
4. 复制生成的API密钥

## 设置环境变量

### macOS/Linux:
```bash
export GEMINI_API_KEY='your-actual-api-key-here'
```

### Windows:
```cmd
set GEMINI_API_KEY=your-actual-api-key-here
```

### Python 环境中设置:
```python
import os
os.environ['GEMINI_API_KEY'] = 'your-actual-api-key-here'
```

## 或者直接在代码中设置

您也可以在 `api/nano_banana.py` 文件中直接修改：

```python
self.api_key = 'your-actual-api-key-here'  # 替换为您的真实API密钥
```

## 重要提示

- 请妥善保管您的API密钥，不要在公开的代码仓库中暴露
- 建议使用环境变量的方式设置API密钥
- API密钥有使用限制，请查看Google AI Studio的配额信息

## 测试API连接

设置完成后，运行以下命令测试：

```bash
cd /Users/hongyuwang/code/HLTraining
source .venv/bin/activate
python -c "
from api.nano_banana import NanoBananaAPI
api = NanoBananaAPI()
print('API 初始化成功!' if api.client else 'API 初始化失败，请检查密钥')
"
```