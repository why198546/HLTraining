import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    
    print('🔍 检查可用的Gemini模型:')
    try:
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f'✅ {model.name} - {model.display_name}')
    except Exception as e:
        print(f'❌ 获取模型列表失败: {str(e)}')
else:
    print('❌ 未找到API密钥')