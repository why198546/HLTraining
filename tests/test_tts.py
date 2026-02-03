"""
测试Gemini TTS功能
"""
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.chdir(project_root)

from dotenv import load_dotenv

load_dotenv()

from api.tts_service import TTSService


def test_tts():
    """测试TTS基本功能"""
    print("=" * 60)
    print("Gemini TTS 功能测试")
    print("=" * 60)
    
    # 初始化TTS服务
    tts = TTSService()
    
    if not tts.client:
        print("❌ TTS客户端初始化失败，请检查GEMINI_API_KEY")
        return
    
    # 测试文本
    test_text = """
    你对发型的观察很仔细！
    
    作品亮点：
    发型线条流畅自然
    层次感把握得很好
    整体造型很有美感
    
    改进建议：
    可以尝试更丰富的发型变化
    注意高光和阴影的处理
    继续保持你的创作热情
    """
    
    print(f"\n📝 测试文本:\n{test_text}\n")
    print("🎤 开始生成语音（使用Flash模型）...\n")
    
    # 测试Flash模型
    result_flash = tts.generate_feedback_audio(
        feedback_text=test_text,
        use_pro_model=False,
        voice_name='Puck'
    )
    
    if result_flash:
        print(f"✅ Flash模型测试成功!")
        print(f"   模型: {result_flash['model']}")
        print(f"   语音: {result_flash['voice_name']}")
        print(f"   文本长度: {result_flash['text_length']} 字符")
        print(f"   音频大小: {len(result_flash['audio_base64'])} bytes (base64)")
        
        # 保存音频文件（可选）
        save_audio = input("\n是否保存音频文件到本地？(y/n): ").lower() == 'y'
        if save_audio:
            import base64
            audio_bytes = base64.b64decode(result_flash['audio_base64'])
            output_file = 'test_output/tts_test_flash.mp3'
            os.makedirs('test_output', exist_ok=True)
            with open(output_file, 'wb') as f:
                f.write(audio_bytes)
            print(f"💾 音频已保存到: {output_file}")
    else:
        print("❌ Flash模型测试失败")
        return
    
    # 是否测试Pro模型
    test_pro = input("\n是否测试Pro模型？(y/n): ").lower() == 'y'
    if test_pro:
        print("\n🎤 开始生成语音（使用Pro模型）...\n")
        result_pro = tts.generate_feedback_audio(
            feedback_text=test_text,
            use_pro_model=True,
            voice_name='Puck'
        )
        
        if result_pro:
            print(f"✅ Pro模型测试成功!")
            print(f"   模型: {result_pro['model']}")
            print(f"   语音: {result_pro['voice_name']}")
            print(f"   音频大小: {len(result_pro['audio_base64'])} bytes (base64)")
        else:
            print("❌ Pro模型测试失败")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == '__main__':
    test_tts()
