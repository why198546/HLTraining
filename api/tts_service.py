"""
文本转语音服务 - 使用Gemini TTS模型
"""
import base64
import io
import os
import re
import struct
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class TTSService:
    """文本转语音服务类 - 使用Gemini TTS"""
    
    def __init__(self):
        # Gemini API配置
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        print(f"🔊 TTS服务初始化:")
        print(f"  Gemini API Key: {'✅' if self.api_key else '❌'}")
        
        # 初始化Gemini客户端
        try:
            if not self.api_key or self.api_key == 'your-api-key-here':
                raise Exception("Gemini API密钥未配置")
            self.client = genai.Client(api_key=self.api_key)
            print("✅ Gemini TTS客户端初始化成功")
        except Exception as e:
            print(f"❌ Gemini TTS客户端初始化失败: {str(e)}")
            self.client = None
    
    def _parse_audio_mime_type(self, mime_type):
        """
        解析音频MIME类型，提取采样率和位深度
        参考Gemini官方示例代码
        
        Args:
            mime_type: 音频MIME类型字符串 (如 "audio/L16;rate=24000")
        
        Returns:
            dict: 包含 bits_per_sample 和 rate 的字典
        """
        bits_per_sample = 16  # 默认16-bit
        rate = 24000  # 默认24kHz
        
        # 解析MIME类型参数
        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            # 提取采样率
            if param.lower().startswith("rate="):
                try:
                    rate_str = param.split("=", 1)[1]
                    rate = int(rate_str)
                except (ValueError, IndexError):
                    pass
            # 从 audio/L16 格式提取位深度
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass
        
        return {"bits_per_sample": bits_per_sample, "rate": rate}
    
    def _convert_pcm_to_wav(self, pcm_data, audio_mime='audio/L16;codec=pcm;rate=24000'):
        """
        将PCM音频数据转换为标准WAV格式
        参考Gemini官方示例代码
        
        Args:
            pcm_data: 原始PCM字节数据
            audio_mime: 音频MIME类型，包含采样率和位深度信息
        
        Returns:
            bytes: WAV格式的音频数据
        """
        # 解析MIME类型参数
        params = self._parse_audio_mime_type(audio_mime)
        bits_per_sample = params["bits_per_sample"]
        sample_rate = params["rate"]
        
        # WAV文件参数
        num_channels = 1  # 单声道
        data_size = len(pcm_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size  # 36字节头部 + 数据大小
        
        # 创建WAV文件头 (RIFF格式)
        # 参考: http://soundfile.sapp.org/doc/WaveFormat/
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",           # ChunkID
            chunk_size,        # ChunkSize (文件大小 - 8字节)
            b"WAVE",           # Format
            b"fmt ",           # Subchunk1ID
            16,                # Subchunk1Size (PCM格式为16)
            1,                 # AudioFormat (1 = PCM)
            num_channels,      # NumChannels
            sample_rate,       # SampleRate
            byte_rate,         # ByteRate
            block_align,       # BlockAlign
            bits_per_sample,   # BitsPerSample
            b"data",           # Subchunk2ID
            data_size          # Subchunk2Size (音频数据大小)
        )
        
        # 返回完整的WAV文件 (头部 + PCM数据)
        return header + pcm_data

    
    def text_to_speech_gemini(self, text, model='gemini-2.5-flash-preview-tts', 
                             voice_name='Puck', language='zh-CN'):
        """
        使用Gemini TTS生成语音
        
        Args:
            text: 要转换的文本
            model: TTS模型
                - gemini-2.5-flash-preview-tts: 快速模型（推荐，中文支持好且便宜）
                - gemini-2.5-pro-preview-tts: 专业模型（更高质量，价格贵一倍）
            voice_name: 语音名称
                Gemini TTS支持的语音（适合儿童教学）：
                - Puck: 温柔女声（默认，适合给孩子讲解）
                - Charon: 稳重男声
                - Kore: 活泼女声
                - Fenrir: 年轻男声
                - Aoede: 柔和女声
            language: 语言代码 (zh-CN中文)
        
        Returns:
            base64编码的音频数据
        """
        try:
            if not self.client:
                raise Exception("Gemini客户端未初始化")
            
            print(f"🎤 Gemini TTS ({model}): {text[:30]}...")
            print(f"   语音: {voice_name}, 语言: {language}")
            
            # 配置TTS请求
            config = types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name
                        )
                    )
                )
            )
            
            # 调用Gemini TTS API
            response = self.client.models.generate_content(
                model=f'models/{model}',
                contents=text,
                config=config
            )
            
            # 提取音频数据
            if not response or not hasattr(response, 'candidates') or not response.candidates:
                raise Exception("TTS返回无效响应")
            
            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not candidate.content:
                raise Exception("响应中没有音频内容")
            
            # 提取音频部分和mime type
            audio_data = None
            audio_mime = 'audio/wav'  # Gemini TTS默认返回WAV
            
            for part in candidate.content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    audio_data = part.inline_data.data
                    # 获取mime type
                    if hasattr(part.inline_data, 'mime_type'):
                        audio_mime = part.inline_data.mime_type
                    break
            
            if not audio_data:
                raise Exception("响应中没有音频数据")
            
            # 检查是否是PCM格式需要转换
            print(f"📦 原始音频格式: {audio_mime}, 大小: {len(audio_data)} bytes")
            
            if 'pcm' in audio_mime.lower() or 'L16' in audio_mime:
                print(f"🔄 检测到PCM格式，转换为WAV...")
                wav_data = self._convert_pcm_to_wav(audio_data, audio_mime)
                print(f"✅ 转换完成，原始大小: {len(audio_data)} bytes, WAV大小: {len(wav_data)} bytes")
                
                # 验证WAV头部
                if wav_data[:4] == b'RIFF' and wav_data[8:12] == b'WAVE':
                    print(f"✅ WAV头部验证成功")
                    audio_data = wav_data
                    audio_mime = 'audio/wav'
                else:
                    print(f"❌ WAV头部验证失败，保留原始数据")
            
            # Gemini返回的音频是bytes，转换为base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            print(f"✅ Gemini TTS生成成功 (音频大小: {len(audio_data)} bytes, 格式: {audio_mime})")
            print(f"📤 Base64长度: {len(audio_base64)} 字符")
            return {
                'audio_base64': audio_base64,
                'mime_type': audio_mime
            }
                
        except Exception as e:
            print(f"❌ Gemini TTS失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_feedback_audio(self, feedback_text, teacher_id=None, 
                               use_pro_model=False, voice_name='Puck'):
        """
        为AI点评生成语音
        
        Args:
            feedback_text: 点评文本
            teacher_id: 教师ID（保留参数，未来可用于自定义语音）
            use_pro_model: 是否使用Pro模型（默认False使用Flash模型）
            voice_name: 语音名称（默认Puck温柔女声）
        
        Returns:
            {
                'audio_base64': 'base64编码的音频',
                'model': 'gemini-2.5-flash-preview-tts' or 'gemini-2.5-pro-preview-tts',
                'voice_name': '使用的语音名称',
                'text_length': 文本长度
            }
        """
        try:
            # 清理文本中的emoji和特殊符号
            clean_text = re.sub(r'[🌟✨💡🎯💪🔥❤️👍]', '', feedback_text)
            
            # 如果文本太长，分段处理（Gemini TTS建议每次不超过5000字符）
            max_length = 5000
            if len(clean_text) > max_length:
                clean_text = clean_text[:max_length] + "..."
                print(f"⚠️ 文本过长，已截取前{max_length}字符")
            
            # 选择模型
            model = 'gemini-2.5-pro-preview-tts' if use_pro_model else 'gemini-2.5-flash-preview-tts'
            
            print(f"🎤 生成点评语音:")
            print(f"   模型: {model}")
            print(f"   语音: {voice_name}")
            print(f"   文本长度: {len(clean_text)} 字符")
            
            # 调用Gemini TTS
            tts_result = self.text_to_speech_gemini(
                text=clean_text,
                model=model,
                voice_name=voice_name,
                language='zh-CN'
            )
            
            if tts_result and 'audio_base64' in tts_result:
                return {
                    'audio_base64': tts_result['audio_base64'],
                    'mime_type': tts_result.get('mime_type', 'audio/wav'),
                    'model': model,
                    'voice_name': voice_name,
                    'text_length': len(clean_text)
                }
            else:
                return None
                
        except Exception as e:
            print(f"❌ 生成点评语音失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


# 创建全局实例
tts_service = TTSService()


def get_tts_service():
    """获取TTS服务实例"""
    return tts_service
