from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 检查API密钥
key = os.getenv('GEMINI_API_KEY')
if key:
    print(f'✅ GEMINI_API_KEY 已加载 (长度: {len(key)})')
    print(f'   前10个字符: {key[:10]}...')
else:
    print('❌ GEMINI_API_KEY 未找到')

# 测试NanoBananaAPI初始化
try:
    from api.nano_banana import NanoBananaAPI
    api = NanoBananaAPI()
    print(f'\n✅ NanoBananaAPI 初始化成功')
    print(f'   API客户端状态: {"已配置" if api.client else "未配置"}')
except Exception as e:
    print(f'\n❌ NanoBananaAPI 初始化失败: {e}')
