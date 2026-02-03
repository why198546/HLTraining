import base64
import io
import json
import os
import time

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, ImageOps

# 确保环境变量在模块导入时就加载
load_dotenv()

class NanoBananaAPI:
    """Nano Banana API类 - 使用Gemini 2.5 Flash Image (真正的Nano Banana模型)"""
    
    def __init__(self):
        # 确保环境变量加载
        load_dotenv(override=True)  # 强制重新加载
        
        # 从环境变量获取API密钥，优先使用Gemini密钥
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('NANO_BANANA_API_KEY', 'your-nano-banana-api-key-here')
        self.upload_folder = 'uploads'
        
        print(f"🔑 API密钥检查: GEMINI_API_KEY={'已设置' if os.getenv('GEMINI_API_KEY') else '未设置'}")
        print(f"🔑 环境变量值前10个字符: {os.getenv('GEMINI_API_KEY')[:10] if os.getenv('GEMINI_API_KEY') else 'None'}")
        print(f"🔑 最终API密钥长度: {len(self.api_key) if self.api_key else 0}")
        
        # 初始化新的Google Gen AI客户端
        try:
            if not self.api_key or self.api_key == 'your-nano-banana-api-key-here':
                raise Exception("API密钥未配置或使用默认值")
            self.client = genai.Client(api_key=self.api_key)
            print("✅ Google Gen AI 客户端初始化成功 (Gemini 2.5 Flash Image)")
        except Exception as e:
            print(f"❌ Google Gen AI 客户端初始化失败: {str(e)}")
            self.client = None
    
    def combine_two_images(self, image1_path, image2_path, description, style="cute", aspect_ratio="512x512"):
        """融合两张图片 - 将第二张图的特征应用到第一张图上
        
        Args:
            image1_path: 第一张图片路径（基础图，如照片）
            image2_path: 第二张图片路径（参考图，如画作）
            description: 融合指令描述
            style: 输出风格
            aspect_ratio: 输出尺寸
        
        Returns:
            生成图片的路径
        """
        try:
            print("🎨 开始使用Gemini 2.5 Flash Image 融合两张图片...")
            print(f"📁 基础图: {image1_path}")
            print(f"📁 参考图: {image2_path}")
            print(f"📝 融合指令: {description}")
            
            # 检查客户端
            if not self.client:
                raise Exception("Google Gen AI客户端未配置，请检查GEMINI_API_KEY环境变量")
            
            # 读取并压缩两张图片（减少API传输时间）
            from io import BytesIO

            from PIL import Image

            # 读取并压缩图片1
            img1 = Image.open(image1_path)
            if img1.width > 1024 or img1.height > 1024:
                ratio = min(1024 / img1.width, 1024 / img1.height)
                new_size = (int(img1.width * ratio), int(img1.height * ratio))
                img1 = img1.resize(new_size, Image.Resampling.LANCZOS)
                print(f"📏 图1已压缩到: {new_size}")
            
            # 转换为字节
            buffer1 = BytesIO()
            img1.save(buffer1, format='PNG', optimize=True)
            image1_bytes = buffer1.getvalue()
            
            # 读取并压缩图片2
            img2 = Image.open(image2_path)
            if img2.width > 1024 or img2.height > 1024:
                ratio = min(1024 / img2.width, 1024 / img2.height)
                new_size = (int(img2.width * ratio), int(img2.height * ratio))
                img2 = img2.resize(new_size, Image.Resampling.LANCZOS)
                print(f"📏 图2已压缩到: {new_size}")
            
            buffer2 = BytesIO()
            img2.save(buffer2, format='PNG', optimize=True)
            image2_bytes = buffer2.getvalue()
            
            print(f"✅ 已读取两张图片")
            print(f"   图1: {len(image1_bytes)} 字节")
            print(f"   图2: {len(image2_bytes)} 字节")
            
            # 构建提示词
            prompt = description
            print(f"📝 最终提示词: {prompt}")
            
            # 配置
            config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                temperature=0.9,
                top_p=0.95
            )
            
            # 构建内容 - 提示词在前，两张图片在后（按Gemini要求的顺序）
            contents = [
                prompt,
                types.Part.from_bytes(data=image1_bytes, mime_type='image/png'),
                types.Part.from_bytes(data=image2_bytes, mime_type='image/png')
            ]
            
            print(f"🔥 正在调用Gemini 2.5 Flash Image...")
            
            # 调用API
            response = self.client.models.generate_content(
                model='models/gemini-2.5-flash-image',
                contents=contents,
                config=config
            )
            
            # 提取生成的图像
            if not response or not hasattr(response, 'candidates') or not response.candidates:
                print("❌ API返回无效响应")
                return None
            
            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not candidate.content:
                print("❌ 响应中没有content")
                return None
            
            # 提取图片数据
            image_parts = [
                part.inline_data.data
                for part in candidate.content.parts
                if hasattr(part, 'inline_data') and part.inline_data
            ]
            
            if not image_parts:
                print("❌ 响应中没有生成图片")
                return None
            
            print("✅ 成功生成融合图片")
            
            # 保存图片
            from io import BytesIO

            from PIL import Image
            image = Image.open(BytesIO(image_parts[0]))
            
            # 保存到uploads文件夹
            import uuid
            output_filename = f"combined_{uuid.uuid4().hex}.jpg"
            output_path = os.path.join(self.upload_folder, 'combined', output_filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            image.save(output_path, 'JPEG', quality=95)
            print(f"✅ 图片已保存: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"❌ 图片融合失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_image_from_reference(self, sketch_path, description="", style="cute", aspect_ratio="512x512", temperature=1, top_p=0.95, seed=None, require_skeleton=False):
        """参考图+文字描述生成图片 - 使用Gemini 2.5 Flash Image模型
        
        功能：
        1. 基于参考图（sketch_path）生成新图片
        2. 可选文字描述（description）引导生成
        3. 支持多种风格和高宽比
        4. style="none" 时不添加任何系统提示词（专家模式）
        5. temperature参数控制生成的创意程度（0.0-1.0）
        6. seed参数用于控制随机性（不同seed会产生不同结果）
        7. require_skeleton参数：仅在特定课程（如松果课堂第2节课）时需要骨骼参考图
        """
        try:
            print("🎨 开始使用Gemini 2.5 Flash Image 进行参考图生成...")
            print(f"🎨 风格: {style}, 高宽比: {aspect_ratio}, 需要骨骼图: {require_skeleton}")
            
            # 检查客户端
            if not self.client:
                raise Exception("Google Gen AI客户端未配置，请检查GEMINI_API_KEY环境变量")
            
            # 仅在特定课程时强制要求骨架参考图（如松果课堂第2节课）
            if require_skeleton and (not sketch_path or not os.path.exists(sketch_path)):
                raise Exception(f"该课程需要提供有效的骨架参考图: {sketch_path}")
            
            # 如果没有参考图且不要求骨骼图，则直接生成提示词图片
            if not sketch_path or not os.path.exists(sketch_path):
                # 不再抛出异常，改为纯文字生成
                print(f"⚠️ 未提供参考图，将使用纯文字模式生成图片")
                return None  # 返回None表示应该使用纯文字生成
            
            print(f"📁 图片路径: {sketch_path}")
            
            # 读取图像
            file_size = os.path.getsize(sketch_path)
            print(f"📊 文件大小: {file_size / 1024:.1f} KB")
            
            with open(sketch_path, 'rb') as f:
                image_bytes = f.read()
            
            print(f"✅ 已读取图片，字节数: {len(image_bytes)}")
            
            # 验证图片内容
            try:
                import io

                from PIL import Image
                img = Image.open(io.BytesIO(image_bytes))
                print(f"📐 图片尺寸: {img.width} x {img.height}")
                print(f"🎨 图片模式: {img.mode}")
            except Exception as e:
                print(f"⚠️ 图片验证失败: {e}")
            
            # style="none" 时为专家模式，直接使用用户输入
            if style == "none":
                prompt = description if description else "为这张图片上色"
                print(f"⚡ 专家模式 - 原始 prompt: {prompt}")
            else:
                # 风格映射 - 简化提示词，加快生成速度
                style_prompts = {
                    'cute': '卡通',
                    'realistic': '写实',
                    'anime': '动漫',
                    'fantasy': '奇幻',
                    'model_3d': '白色背景，清晰主体'
                }
                
                style_desc = style_prompts.get(style, style_prompts['cute'])
                
                # 构建提示词
                if description:
                    # 如果用户提示词中包含中文，直接使用
                    # Gemini 2.5对中文理解很好，尤其是美术术语
                    if any('\u4e00' <= c <= '\u9fff' for c in description):
                        prompt = f"请仔细按照这个描述上色：{description}。风格：{style_desc}。"
                    else:
                        # 如果是英文，使用更强的指示
                        prompt = f"Follow this description precisely: {description}. Style: {style_desc}."
                else:
                    prompt = f"给这张素描上色，保持线条结构。风格：{style_desc}"
            
            print(f"🎨 用户描述：{description or '使用默认风格'}")
            print(f"📝 上色提示词: {prompt}")
            
            # 使用Gemini模型进行图像上色（支持图片输入）
            max_retries = 3
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                try:
                    retry_count += 1
                    print(f"🔥 正在使用Gemini 2.5 Flash Image (Nano Banana)... (尝试 {retry_count}/{max_retries})")
                    
                    # 将分辨率转换为比例格式（Gemini API 需要）
                    if 'x' in aspect_ratio:
                        width, height = map(int, aspect_ratio.split('x'))
                        # 计算最简比例
                        from math import gcd
                        divisor = gcd(width, height)
                        ratio_str = f"{width // divisor}:{height // divisor}"
                    else:
                        ratio_str = aspect_ratio
                    
                    # 使用Gemini 2.5 Flash Image - 更接近官网设置
                    config_kwargs = {
                        'response_modalities': ["IMAGE"],  # 明确要求返回图片
                        'temperature': 0.8,  # 降低temperature以加快生成
                        'top_p': 0.9,  # 稍微降低多样性以加快生成
                    }
                    
                    # 只在需要时指定宽高比（可能是限制因素）
                    if aspect_ratio and aspect_ratio != "512x512":
                        config_kwargs['image_config'] = types.ImageConfig(
                            aspect_ratio=ratio_str,
                        )
                    
                    # 如果提供了seed参数，添加到配置中
                    if seed is not None:
                        config_kwargs['seed'] = int(seed)
                    
                    config = types.GenerateContentConfig(**config_kwargs)
                    
                    print(f"🔥 正在调用Gemini 2.5 Flash Image...")
                    print(f"   📝 提示词: {prompt[:80]}...")
                    print(f"   📊 配置: temperature={temperature}, top_p={top_p}, ratio={ratio_str}")
                    # 必须附加骨架图
                    print(f"   🖼️ 发送图片: {len(image_bytes)} 字节")
                    
                    contents = [
                        prompt,
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type='image/png'
                        )
                    ]

                    response = self.client.models.generate_content(
                        model='models/gemini-2.5-flash-image',  # 使用Gemini 2.5 Flash Image
                        contents=contents,
                        config=config
                    )
                    
                    # 检查响应是否有效
                    print(f"🔍 响应对象: {response is not None}")
                    if not response:
                        print("❌ 响应为空")
                        last_error = "API返回空响应"
                        continue
                    
                    print(f"🔍 candidates存在: {hasattr(response, 'candidates')}")
                    if not hasattr(response, 'candidates') or not response.candidates:
                        print("❌ 响应中没有candidates")
                        if hasattr(response, 'prompt_feedback'):
                            print(f"   反馈信息: {response.prompt_feedback}")
                        last_error = "响应中没有candidates（可能被过滤或模型不支持此格式）"
                        continue
                    
                    print(f"🔍 candidates数量: {len(response.candidates)}")
                    candidate = response.candidates[0]
                    
                    print(f"🔍 content存在: {hasattr(candidate, 'content')}")
                    if not hasattr(candidate, 'content') or not candidate.content:
                        print("❌ candidate中没有content")
                        last_error = "candidate中没有content"
                        continue
                    
                    print(f"🔍 parts存在: {hasattr(candidate.content, 'parts')}")
                    if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                        print("❌ content中没有parts")
                        last_error = "content中没有parts"
                        continue
                    
                    print(f"🔍 parts数量: {len(candidate.content.parts)}")
                    
                    # 提取生成的图像
                    image_parts = [
                        part.inline_data.data
                        for part in candidate.content.parts
                        if hasattr(part, 'inline_data') and part.inline_data
                    ]
                    
                    print(f"🔍 提取到的图片数量: {len(image_parts)}")
                    
                    if image_parts:
                        print("✅ 成功生成图片")
                        
                        # 将生成的图像转换为PIL图像
                        from io import BytesIO
                        image = Image.open(BytesIO(image_parts[0]))
                        
                        # 调整图片尺寸以匹配指定分辨率
                        if 'x' in aspect_ratio:
                            # 解析具体分辨率（如 "512x512"）
                            target_width, target_height = map(int, aspect_ratio.split('x'))
                            width, height = image.size
                            
                            # 如果尺寸不匹配，调整图片
                            if width != target_width or height != target_height:
                                # 计算缩放比例，保持宽高比
                                scale = min(target_width / width, target_height / height)
                                new_width = int(width * scale)
                                new_height = int(height * scale)
                                
                                # 缩放图片
                                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                
                                # 创建目标尺寸的白色画布
                                new_image = Image.new('RGB', (target_width, target_height), (255, 255, 255))
                                # 将缩放后的图片居中粘贴
                                x_offset = (target_width - new_width) // 2
                                y_offset = (target_height - new_height) // 2
                                new_image.paste(image, (x_offset, y_offset))
                                image = new_image
                                print(f"📐 调整图片尺寸至 {aspect_ratio}")
                        
                        # 保存上色后的图像
                        base_name = os.path.splitext(os.path.basename(sketch_path))[0]
                        # 为每张图添加UUID确保唯一性（防止覆盖）
                        import uuid
                        colored_filename = f"{base_name}_colored_{uuid.uuid4().hex}.jpg"
                        output_path = os.path.join(self.upload_folder, colored_filename)
                        
                        # 保存图片
                        image.save(output_path, 'JPEG', quality=95)
                        
                        print(f"✅ Gemini上色完成: {output_path}")
                        print(f"📐 高宽比: {aspect_ratio}")
                        print(f"🆔 文件名: {colored_filename}")
                        return output_path
                    else:
                        # 检查是否有文本响应
                        text_parts = [
                            part.text
                            for part in candidate.content.parts
                            if hasattr(part, 'text') and part.text
                        ]
                        if text_parts:
                            print(f"⚠️ Gemini返回了文本而非图片: {text_parts[0][:200]}")
                            last_error = f"Gemini返回文本响应: {text_parts[0][:100]}"
                        else:
                            print("⚠️ 响应中没有生成图片或文本")
                            last_error = "响应中没有图片或文本数据"
                    
                except Exception as e:
                    last_error = str(e)
                    print(f"⚠️ 尝试 {retry_count} 失败: {last_error}")
                    if retry_count < max_retries:
                        print(f"🔄 等待2秒后重试...")
                        time.sleep(2)
                    
            # 如果所有重试都失败了
            print(f"❌ 所有重试都失败了，最后错误: {last_error}")
            
            # 检查是否是配额耗尽错误
            if "429" in str(last_error) or "RESOURCE_EXHAUSTED" in str(last_error) or "quota" in str(last_error).lower():
                print("⚠️  API配额已耗尽，请稍后再试")
            
            return None
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Imagen上色错误: {error_msg}")
            
            # 检查是否是配额耗尽错误
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                print("⚠️  API配额已耗尽，请稍后再试")
            
            return None
    
    def generate_figurine_style(self, colored_image_path, description=""):
        """生成手办风格图片 - 使用Gemini 2.5 Flash Image"""
        try:
            print("🏺 开始使用Gemini生成手办风格...")
            
            # 检查客户端
            if not self.client:
                raise Exception("Google Gen AI客户端未配置，请检查GEMINI_API_KEY环境变量")
            
            # 读取彩色图像
            with open(colored_image_path, 'rb') as f:
                image_bytes = f.read()
            
            # 构建手办风格提示词
            figurine_prompt = f"""将这张图片转换为手办风格的三维立体效果：

基本要求：
1. 保持原始角色的特征和颜色
2. 添加手办的立体质感和材质效果
3. 增加适当的阴影和高光
4. 背景简洁，突出手办主体
5. 整体呈现手办玩具的质感

风格特点：
- 三维立体效果
- 塑料/树脂材质质感
- 精细的细节表现
- 柔和的光影效果
- 适合儿童的可爱风格

{f'用户补充描述：{description}' if description else ''}

请生成一张精美的手办风格图片！"""
            
            # 将图像转换为PIL Image对象
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # 创建聊天实例并发送消息
            chat = self.client.chats.create(model="gemini-2.5-flash-image")
            response = chat.send_message([figurine_prompt, pil_image])
            
            # 提取生成的图像
            image_parts = []
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        image_parts.append(part.inline_data.data)
            
            if image_parts:
                # 保存图像
                base_name = os.path.splitext(os.path.basename(colored_image_path))[0]
                figurine_filename = f"{base_name}_figurine.png"
                output_path = os.path.join(self.upload_folder, figurine_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(image_parts[0])
                
                print(f"✅ 手办风格生成完成: {output_path}")
                return output_path
            else:
                raise Exception("未能从Gemini响应中提取图像")
                
        except Exception as e:
            print(f"❌ 手办风格生成错误: {str(e)}")
            return None
    
    def generate_artwork_description(self, image_path, user_prompt=""):
        """为作品生成描述文本 - 使用Gemini 2.5 Flash"""
        try:
            print("📝 开始使用Gemini生成作品描述...")
            
            # 检查客户端
            if not self.client:
                raise Exception("Google Gen AI客户端未配置，请检查GEMINI_API_KEY环境变量")
            
            # 读取图像
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # 构建描述生成提示词
            description_prompt = f"""请为这张儿童创作的艺术作品生成一段简洁而富有创意的描述：

要求：
1. 用儿童能够理解的简单语言
2. 突出作品的创意和想象力
3. 描述画面中的主要元素和色彩
4. 体现积极正面的情感
5. 长度控制在50-100字之间
6. 适合10-14岁儿童阅读

{f'用户提示：{user_prompt}' if user_prompt else ''}

请生成一段温馨而富有想象力的作品描述！"""
            
            # 将图像转换为PIL Image对象
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # 使用文本生成模型
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[description_prompt, pil_image]
            )
            
            if response.text:
                print(f"✅ 作品描述生成完成: {response.text}")
                return response.text.strip()
            else:
                raise Exception("未能从Gemini响应中提取文本")
                
        except Exception as e:
            print(f"❌ 作品描述生成错误: {str(e)}")
            return "这是一幅充满创意和想象力的作品，展现了小艺术家独特的视角和丰富的色彩感。"
    
    def _sanitize_prompt_for_children(self, prompt):
        """为儿童内容优化提示词，避免触发内容过滤器"""
        
        # 定义可能被过滤的词汇和其儿童友好的替代词
        sensitive_replacements = {
            # 角色相关
            "奥特曼": "银红色超级英雄",
            "假面骑士": "面具英雄",
            "战士": "英雄",
            "勇士": "英雄",
            
            # 动作相关
            "战斗": "行动",
            "打斗": "动作",
            "攻击": "动作",
            "格斗": "运动",
            "战争": "冒险",
            
            # 武器相关
            "剑": "能量棒",
            "刀": "工具",
            "枪": "光线发射器",
            "武器": "道具",
            
            # 其他可能敏感的词
            "危险": "刺激",
            "恐怖": "神秘",
            "暴力": "活力"
        }
        
        # 特殊角色的详细替换规则
        character_descriptions = {
            "奥特曼": "银红色的友善超级英雄，胸前有发光的圆形能量指示器",
            "假面骑士": "戴着酷炫面具的英雄角色",
        }
        
        # 首先检查是否有完整的角色描述需要替换
        original_prompt = prompt
        for character, description in character_descriptions.items():
            if character in prompt:
                # 如果包含特定角色，进行更智能的替换
                prompt = prompt.replace(character, description)
                print(f"🔄 角色替换: '{character}' -> '{description}'")
        
        # 然后进行词汇级别的替换
        for sensitive, replacement in sensitive_replacements.items():
            if sensitive in prompt and sensitive not in character_descriptions:
                prompt = prompt.replace(sensitive, replacement)
                print(f"🔄 词汇替换: '{sensitive}' -> '{replacement}'")
        
        # 如果进行了替换，输出提示
        if prompt != original_prompt:
            print(f"⚡ 提示词优化完成，避免内容过滤器")
            print(f"📝 原始: {original_prompt}")
            print(f"📝 优化: {prompt}")
        
        return prompt

    def generate_image_from_text(self, text_prompt, style="cute", aspect_ratio="512x512"):
        """从文字描述生成图片 - 使用Gemini 2.5 Flash Image官方API，原生高宽比支持！"""
        try:
            print(f"🎨 开始使用Gemini 2.5 Flash Image官方API生成图片...")
            print(f"📝 提示词: {text_prompt}")
            print(f"🎨 风格: {style}")
            print(f"📐 原生高宽比: {aspect_ratio}")
            
            # 检查客户端
            if not self.client:
                raise Exception("Google Gen AI客户端未配置，请检查GEMINI_API_KEY环境变量")
            
            # style="none" 时为专家模式，直接使用用户输入
            if style == "none":
                image_prompt = text_prompt
                print(f"⚡ 专家模式 - 原始prompt: {image_prompt}")
            else:
                # 风格映射
                style_prompts = {
                    'cute': '可爱卡通风格',
                    'realistic': '写实风格',
                    'anime': '日式动漫风格',
                    'fantasy': '奇幻风格',
                    'model_3d': '3D模型专用，纯白色或浅灰色单色背景，主体清晰居中，无任何背景装饰、天空、地面或环境元素'
                }
                
                style_desc = style_prompts.get(style, style_prompts['cute'])
                
                # 对于3D模型风格，强制移除背景描述
                if style == 'model_3d':
                    # 移除常见的背景关键词
                    background_keywords = ['背景', '场景', '环境', '在...上', '在...里', '周围', '旁边']
                    clean_prompt = text_prompt
                    for keyword in background_keywords:
                        if keyword in clean_prompt:
                            # 简单处理：如果包含背景关键词，尝试提取主体
                            parts = clean_prompt.split('，')
                            clean_parts = [p for p in parts if not any(k in p for k in background_keywords)]
                            if clean_parts:
                                clean_prompt = '，'.join(clean_parts)
                            break
                    
                    # 强制纯白色背景
                    image_prompt = f"{clean_prompt}, {style_desc}, 纯白色背景，完全没有任何背景元素，角色居中，完整身体，正面视角"
                    print(f"🎯 3D模式 - 清理后的提示词: {image_prompt}")
                else:
                    # 简化的提示词构建，保持原始意图
                    image_prompt = f"{text_prompt}, {style_desc}"
            
            print(f"📝 最终提示词: {image_prompt}")
            
            # 使用支持重试机制的imagen模型
            max_retries = 3
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                try:
                    retry_count += 1
                    print(f"🔥 正在使用Gemini 2.5 Flash Image生成图片... (尝试 {retry_count}/{max_retries})")
                    
                    # 使用Gemini 2.5 Flash Image模型 - 官方方式支持原生高宽比
                    print(f"🔍 详细调用信息:")
                    print(f"  模型: gemini-2.5-flash-image")
                    print(f"  提示词: {image_prompt}")
                    print(f"  原生高宽比: {aspect_ratio}")
                    
                    # 由于现在有原生高宽比支持，我们不需要在提示词中添加高宽比信息
                    final_prompt = image_prompt
                    
                    print(f"  最终提示词: {final_prompt}")
                    
                    # 使用官方推荐的方式：generate_content_stream with GenerateContentConfig
                    contents = [
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(text=final_prompt),
                            ],
                        ),
                    ]
                    
                    # 将分辨率转换为比例格式（Gemini API 需要）
                    if 'x' in aspect_ratio:
                        width, height = map(int, aspect_ratio.split('x'))
                        # 计算最简比例
                        from math import gcd
                        divisor = gcd(width, height)
                        ratio_str = f"{width // divisor}:{height // divisor}"
                    else:
                        ratio_str = aspect_ratio
                    
                    generate_content_config = types.GenerateContentConfig(
                        response_modalities=[
                            "IMAGE",
                            "TEXT",
                        ],
                        image_config=types.ImageConfig(
                            aspect_ratio=ratio_str,  # 使用比例格式
                        ),
                    )
                    
                    print(f"🔍 使用官方API配置:")
                    print(f"  响应模式: IMAGE, TEXT")
                    print(f"  图像配置高宽比: {aspect_ratio}")
                    
                    # 使用stream方式获取响应
                    image_data = None
                    response_text = ""
                    
                    for chunk in self.client.models.generate_content_stream(
                        model="gemini-2.5-flash-image",
                        contents=contents,
                        config=generate_content_config,
                    ):
                        if (
                            chunk.candidates is None
                            or chunk.candidates[0].content is None
                            or chunk.candidates[0].content.parts is None
                        ):
                            continue
                        
                        # 检查是否有图像数据
                        if (chunk.candidates[0].content.parts[0].inline_data and 
                            chunk.candidates[0].content.parts[0].inline_data.data):
                            inline_data = chunk.candidates[0].content.parts[0].inline_data
                            image_data = inline_data.data
                            print(f"🎉 成功获取图像数据! 数据大小: {len(image_data)} bytes")
                            print(f"📄 MIME类型: {inline_data.mime_type}")
                        else:
                            # 文本响应
                            if hasattr(chunk, 'text') and chunk.text:
                                response_text += chunk.text
                    
                    if image_data:
                        # 保存生成的图像
                        timestamp = int(time.time())
                        generated_filename = f"generated_text_image_{timestamp}.png"
                        output_path = os.path.join(self.upload_folder, generated_filename)
                        
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        
                        print(f"✅ 文字生成图片完成: {output_path}")
                        print(f"📐 原生高宽比支持: {aspect_ratio}")
                        print(f"🎯 提示词回顾: {final_prompt}")
                        if response_text:
                            print(f"💬 AI响应文本: {response_text}")
                        return output_path
                    else:
                        print(f"❌ 没有找到图像数据在响应中")
                        last_error = f"Gemini 2.5 Flash Image响应中没有图像数据"
                    
                except Exception as e:
                    last_error = str(e)
                    print(f"⚠️ 尝试 {retry_count} 失败: {last_error}")
                    if retry_count < max_retries:
                        print(f"🔄 等待2秒后重试...")
                        time.sleep(2)
                    
            # 如果所有重试都失败了
            print(f"❌ 所有重试都失败了，最后错误: {last_error}")
            return None
                
        except Exception as e:
            print(f"❌ 文字生成图片错误: {str(e)}")
            return None
    
    def generate_image_from_sketch(self, sketch_path, style="cute", aspect_ratio="1:1"):
        """从手绘图片生成图片（纯图片模式）"""
        try:
            print(f"🎨 纯图片模式：为手绘图生成AI图片 - {sketch_path}")
            
            # 检查sketch_path是否有效
            if not sketch_path or not os.path.exists(sketch_path):
                print(f"⚠️ 参考图不存在，转换为纯文字模式生成")
                # 返回None表示应该使用纯文字生成
                return None
            
            # 使用参考图生成方法，传入风格参数
            # require_skeleton=False 表示这不是需要骨骼图的课程
            return self.generate_image_from_reference(sketch_path, "", style=style, aspect_ratio=aspect_ratio, require_skeleton=False)
            
        except Exception as e:
            print(f"❌ 纯图片模式生成失败: {str(e)}")
            return None

    def generate_image_from_sketch_and_text(self, sketch_path, text_prompt, style="cute", aspect_ratio="1:1"):
        """从手绘图片和文字描述生成图片（图片+文字模式）"""
        try:
            print(f"🎨 图片+文字模式：为手绘图生成AI图片 - {sketch_path}")
            
            # 检查sketch_path是否有效
            if not sketch_path or not os.path.exists(sketch_path):
                print(f"⚠️ 参考图不存在，转换为纯文字模式生成")
                # 返回None表示应该使用纯文字生成
                return None
            
            # 使用参考图生成方法，传入文字描述
            # require_skeleton=False 表示这不是需要骨骼图的课程
            return self.generate_image_from_reference(sketch_path, text_prompt, style=style, aspect_ratio=aspect_ratio, require_skeleton=False)
            
        except Exception as e:
            print(f"❌ 图片+文字模式生成失败: {str(e)}")
            return None
    
    def adjust_image(self, image_path, adjust_prompt, expert_mode=False):
        """调整现有图片 - 使用Gemini 2.5 Flash Image根据调整说明重新生成图片"""
        try:
            print(f"🔧 开始调整图片: {image_path}")
            print(f"📝 调整说明: {adjust_prompt}")
            print(f"⚡ Expert模式: {expert_mode}")
            
            # 检查客户端
            if not self.client:
                raise Exception("Google Gen AI客户端未配置，请检查GEMINI_API_KEY环境变量")
            
            # 读取原始图像
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # 将图像转换为PIL Image对象
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # 获取原始图片的宽高比
            original_width, original_height = pil_image.size
            
            # 计算宽高比并转换为字符串格式
            if original_width > original_height:
                # 横向图片
                aspect_ratio = "16:9"
            elif original_height > original_width:
                # 纵向图片
                aspect_ratio = "9:16"
            else:
                # 正方形
                aspect_ratio = "1:1"
            
            print(f"📐 原始图片尺寸: {original_width}x{original_height}, 使用宽高比: {aspect_ratio}")
            
            # 构建调整提示词
            if expert_mode:
                # Expert模式：直接使用用户的调整说明
                final_prompt = f"根据以下要求调整这张图片：{adjust_prompt}"
            else:
                # 标准模式：构建详细的调整提示词
                final_prompt = f"""请根据以下要求调整这张图片：

调整要求：{adjust_prompt}

注意事项：
1. 保持图片的主体元素和整体构图
2. 根据调整要求进行相应的修改
3. 确保调整后的图片适合儿童观看
4. 保持色彩明亮、风格可爱
5. 图片质量要清晰、细节丰富

请生成调整后的图片！"""
            
            print(f"📝 调整提示词: {final_prompt}")
            
            # 使用Gemini 2.5 Flash Image模型 - 使用简化API
            # 直接传入prompt和图片，使用原始图片的宽高比
            generate_content_config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                ),
            )
            
            # 使用stream方式获取响应
            image_data = None
            
            for chunk in self.client.models.generate_content_stream(
                model="gemini-2.5-flash-image",
                contents=[final_prompt, pil_image],
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                
                # 检查是否有图像数据
                if (chunk.candidates[0].content.parts[0].inline_data and 
                    chunk.candidates[0].content.parts[0].inline_data.data):
                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    image_data = inline_data.data
                    print(f"🎉 成功获取调整后的图像数据!")
            
            if image_data:
                # 保存调整后的图像
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                timestamp = int(time.time())
                adjusted_filename = f"{base_name}_adjusted_{timestamp}.png"
                output_path = os.path.join(self.upload_folder, adjusted_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                
                print(f"✅ 图片调整完成: {output_path}")
                return output_path
            else:
                raise Exception("未能从响应中获取调整后的图片")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 图片调整错误: {error_msg}")
            
            # 检查是否是配额耗尽错误
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                print("⚠️ API配额已耗尽，请稍后再试")
            
            return None

    def split_multi_view_image(self, image_path):
        """将2x2网格图片分割成4个独立的视角图片
        
        Args:
            image_path: 包含4个视角的网格图片路径
            
        Returns:
            dict: {'front': path, 'back': path, 'left': path, 'right': path}
        """
        try:
            print(f"🔪 开始分割多视角网格图片: {image_path}")
            
            # 加载图片
            img = Image.open(image_path)
            width, height = img.size
            print(f"📐 原图尺寸: {width}x{height}")
            
            # 计算每个象限的尺寸
            half_width = width // 2
            half_height = height // 2
            
            # 定义裁剪区域 (left, top, right, bottom)
            # 2x2布局：左上=正面，右上=背面，左下=左侧，右下=右侧
            crop_boxes = {
                'front': (0, 0, half_width, half_height),                    # 左上
                'back': (half_width, 0, width, half_height),                 # 右上
                'left': (0, half_height, half_width, height),                # 左下
                'right': (half_width, half_height, width, height)            # 右下
            }
            
            results = {}
            timestamp = int(time.time())
            
            for view_name, box in crop_boxes.items():
                print(f"✂️ 裁剪{view_name}视角: {box}")
                
                # 裁剪象限
                quadrant = img.crop(box)
                
                # 保存裁剪后的图片
                filename = f"view_{view_name}_{timestamp}.png"
                output_path = os.path.join(self.upload_folder, filename)
                quadrant.save(output_path)
                
                results[view_name] = output_path
                print(f"💾 {view_name}视角已保存: {output_path}")
            
            print(f"✅ 成功分割为4个视角图片")
            return results
            
        except Exception as e:
            print(f"❌ 图片分割错误: {str(e)}")
            return None

    def generate_multi_view_images(self, text_prompt, color_preference="colorful", aspect_ratio="1:1"):
        """生成多视角图片（正、反、左、右）用于3D建模
        
        新方法：生成一张2x2网格图片包含所有4个视角，然后自动分割
        这样可以确保角色完美一致性
        
        Args:
            text_prompt: 角色描述（背景描述会被忽略）
            color_preference: 色彩偏好
            aspect_ratio: 高宽比（将被设置为1:1以适应2x2网格）
            
        Returns:
            dict: {'front': path, 'back': path, 'left': path, 'right': path} 或 None
        """
        try:
            print(f"🎨 开始生成多视角网格图片用于3D建模...")
            print(f"📝 角色描述: {text_prompt}")
            
            # 检查客户端
            if not self.client:
                raise Exception("Google Gen AI客户端未配置，请检查GEMINI_API_KEY环境变量")
            
            # 提取角色主体描述，忽略背景
            background_keywords = ['背景', '场景', '环境', '在...上', '在...里', '周围', '旁边']
            clean_prompt = text_prompt
            for keyword in background_keywords:
                if keyword in clean_prompt:
                    parts = clean_prompt.split('，')
                    clean_parts = [p for p in parts if not any(k in p for k in background_keywords)]
                    if clean_parts:
                        clean_prompt = '，'.join(clean_parts)
                    break
            
            print(f"🎯 清理后的角色描述: {clean_prompt}")
            
            # 构建2x2网格布局提示词
            grid_prompt = f"""Character turnaround reference sheet in 2x2 grid layout.
{clean_prompt}

LAYOUT REQUIREMENTS:
- 2x2 grid showing the SAME SINGLE character from 4 different angles
- Top-left: front view (正面视角)
- Top-right: back view (背面视角)
- Bottom-left: left side view (左侧面视角)
- Bottom-right: right side view (右侧面视角)

CHARACTER REQUIREMENTS:
- ONLY ONE character, same character in all 4 views
- Solo figure, isolated subject, no duplicates, no group
- Pure white background for all 4 views
- Professional 3D model reference sheet style
- Character centered in each view, full body visible
- Maintain perfect character consistency across all views

STYLE:
- 3D模型专用风格
- 纯白色背景，完全没有任何背景元素
- 高清晰度，专业角色设定集风格
- 适合3D建模使用

CRITICAL: All 4 views must show the EXACT SAME character, just from different angles.
禁止出现多个不同的角色，必须是同一个角色的4个视角。"""
            
            print(f"📝 网格提示词: {grid_prompt}")
            
            # 生成2x2网格图片
            max_retries = 3
            retry_count = 0
            last_error = None
            image_data = None
            
            while retry_count < max_retries and not image_data:
                try:
                    retry_count += 1
                    print(f"🔥 尝试生成网格图片 {retry_count}/{max_retries}...")
                    
                    contents = [
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(text=grid_prompt),
                            ],
                        ),
                    ]
                    
                    # 使用1:1比例以适应2x2网格
                    generate_content_config = types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(
                            aspect_ratio="1:1",
                        ),
                    )
                    
                    # 使用stream方式获取响应
                    for chunk in self.client.models.generate_content_stream(
                        model="gemini-2.5-flash-image",
                        contents=contents,
                        config=generate_content_config,
                    ):
                        if (
                            chunk.candidates is None
                            or chunk.candidates[0].content is None
                            or chunk.candidates[0].content.parts is None
                        ):
                            continue
                        
                        # 检查是否有图像数据
                        if (chunk.candidates[0].content.parts[0].inline_data and 
                            chunk.candidates[0].content.parts[0].inline_data.data):
                            inline_data = chunk.candidates[0].content.parts[0].inline_data
                            image_data = inline_data.data
                            print(f"✅ 网格图片生成成功!")
                            break
                    
                    if image_data:
                        # 保存网格图片
                        timestamp = int(time.time())
                        grid_filename = f"multiview_grid_{timestamp}.png"
                        grid_path = os.path.join(self.upload_folder, grid_filename)
                        
                        with open(grid_path, 'wb') as f:
                            f.write(image_data)
                        
                        print(f"💾 网格图片已保存: {grid_path}")
                        
                        # 分割网格图片为4个独立视角
                        split_results = self.split_multi_view_image(grid_path)
                        
                        if split_results:
                            print(f"🎉 多视角图片生成完成!")
                            return split_results
                        else:
                            last_error = "图片分割失败"
                    else:
                        last_error = "响应中没有图像数据"
                        
                except Exception as e:
                    last_error = str(e)
                    print(f"⚠️ 尝试 {retry_count} 失败: {last_error}")
                    if retry_count < max_retries:
                        print(f"⏳ 等待3秒后重试...")
                        time.sleep(3)
            
            # 所有重试都失败
            print(f"❌ 多视角图片生成失败: {last_error}")
            return None
            
        except Exception as e:
            print(f"❌ 多视角图片生成错误: {str(e)}")
            return None
    
    def analyze_artwork_with_vision(self, image_path, lesson_type, aspects, prompt_override=None):
        """使用Gemini Vision分析学生作品
        
        Args:
            image_path: 作品图片路径
            lesson_type: 课程类型（如'formal_hairstyle'）
            aspects: 评价维度列表（如['发型的线条流畅度', '发丝的层次感', '整体造型的美感']）
        
        Returns:
            dict: 包含分析结果的字典
            {
                'highlights': [亮点1, 亮点2, 亮点3],
                'suggestions': [建议1, 建议2, 建议3],
                'overall': '总体评价'
            }
        """
        try:
            print(f"🔍 开始使用Gemini Vision分析作品...")
            print(f"📁 图片路径: {image_path}")
            print(f"📚 课程类型: {lesson_type}")
            print(f"📊 评价维度: {aspects}")
            
            # 检查客户端
            if not self.client:
                raise Exception("Google Gen AI客户端未配置")
            
            # 读取并压缩图片
            from io import BytesIO

            from PIL import Image
            
            img = Image.open(image_path)
            if img.width > 1024 or img.height > 1024:
                ratio = min(1024 / img.width, 1024 / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"📏 图片已压缩到: {new_size}")
            
            buffer = BytesIO()
            img.save(buffer, format='PNG', optimize=True)
            image_bytes = buffer.getvalue()
            
            # 构建分析提示词
            if prompt_override:
                prompt = prompt_override
            else:
                prompt = f"""你是一位专业的儿童美术教师，正在点评一位10-14岁学生的AI生成作品。

课程主题：{lesson_type.replace('formal_', '').replace('_', ' ')}

请从以下3个维度分析这幅作品：
1. {aspects[0]}
2. {aspects[1]}
3. {aspects[2]}

要求：
1. 语气温和友好，适合儿童阅读
2. 多鼓励，少批评
3. 具体指出画面中的优点（至少3个）
4. 给出可操作的改进建议（至少3个）
5. 用简洁的语言总结整体印象

请以JSON格式返回：
{{
    "highlights": ["具体亮点1", "具体亮点2", "具体亮点3"],
    "suggestions": ["具体建议1", "具体建议2", "具体建议3"],
    "overall": "一句话总体评价"
}}

注意：
- highlights要具体描述画面中的优点，不要泛泛而谈
- suggestions要给出明确的改进方向，让孩子知道下次怎么做
- 语言要简单直白，避免专业术语"""

            print(f"📝 分析提示词已构建")
            
            # 配置
            config = types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.9
            )
            
            # 构建内容
            contents = [
                types.Part.from_bytes(data=image_bytes, mime_type='image/png'),
                prompt
            ]
            
            print(f"🔥 正在调用Gemini 2.5 Flash分析...")
            
            # 调用API
            response = self.client.models.generate_content(
                model='models/gemini-2.5-flash',
                contents=contents,
                config=config
            )
            
            if not response or not response.text:
                print("❌ Vision分析返回空结果")
                return None
            
            # 解析JSON响应
            import re
            response_text = response.text.strip()
            
            # 提取JSON（可能被markdown代码块包裹）
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            
            try:
                result = json.loads(response_text)
                print("✅ Vision分析完成")
                print(f"   亮点数量: {len(result.get('highlights', []))}")
                print(f"   建议数量: {len(result.get('suggestions', []))}")
                return result
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON解析失败，尝试提取文本: {e}")
                # 如果JSON解析失败，返回原始文本
                return {
                    'highlights': ['作品很有创意', '色彩运用大胆', '整体效果不错'],
                    'suggestions': ['可以注意细节处理', '尝试更多风格', '继续保持创作热情'],
                    'overall': response_text[:100]
                }
            
        except Exception as e:
            print(f"❌ Vision分析错误: {str(e)}")
            return None    
    def extract_person_features(self, image_path):
        """第一步：提取人物特征（面部、发型、年龄等）
        
        Args:
            image_path: 人物照片路径
        
        Returns:
            dict: 结构化的人物特征信息
        """
        try:
            print("👤 开始提取人物特征...")
            
            if not self.client:
                raise Exception("Vision API未初始化")
            
            # 读取图片
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Vision提取提示词 - 只提取面部相貌特征（自然语言描述）
            prompt = """Describe this person's facial appearance in natural language, focusing ONLY on:
- Face shape and skin tone
- Eyes: size, shape, color if visible
- Eyebrows: shape and thickness
- Nose: size and shape
- Mouth and smile
- Facial expression
- Hair: style, length, color, texture, bangs if any
- Approximate age range and gender appearance

IMPORTANT:
- Be ACCURATE and SPECIFIC about what you see
- Focus ONLY on the face and hair
- Do NOT describe: clothing, body, background, or pose

Example format:
"A young East Asian girl with long, straight dark brown hair, round eyes, a small nose, and a cheerful smile. She appears to be around 8-12 years old."

Your description:"""
            
            # 调用 Gemini Vision
            contents = [
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
            ]
            
            # 配置安全设置 - 允许处理人物照片
            config = types.GenerateContentConfig(
                safety_settings=[
                    types.SafetySetting(
                        category='HARM_CATEGORY_HARASSMENT',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_HATE_SPEECH',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                        threshold='BLOCK_ONLY_HIGH'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_DANGEROUS_CONTENT',
                        threshold='BLOCK_NONE'
                    ),
                ]
            )
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',  # 使用2.0版本，对人物照片限制更少
                contents=contents,
                config=config
            )
            
            # 检查响应
            if not response or not hasattr(response, 'text') or response.text is None:
                print(f"⚠️ Vision API返回空响应或无text属性")
                print(f"📋 Response对象: {response}")
                if hasattr(response, 'candidates'):
                    print(f"📋 Candidates: {response.candidates}")
                if hasattr(response, 'prompt_feedback'):
                    print(f"📋 Prompt Feedback: {response.prompt_feedback}")
                raise Exception("Vision API返回空响应")
            
            response_text = response.text.strip()
            print(f"📥 Vision返回原始文本: {response_text[:200]}...")
            
            # 直接返回自然语言描述（清理引号）
            description = response_text.strip().strip('"').strip("'")
            print(f"✅ 成功提取人物描述")
            print(f"📝 完整描述内容: {description}")
            print(f"📏 描述长度: {len(description)} 字符")
            return description
            
        except Exception as e:
            print(f"❌ 提取人物特征失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # 返回基础描述
            return "A person with natural features and a gentle appearance"
    
    def extract_artwork_features(self, image_path):
        """第一步：提取手绘作品特征（服饰、形体、姿势等）
        
        Args:
            image_path: 手绘作品路径
        
        Returns:
            dict: 结构化的作品特征信息
        """
        try:
            print("🎨 开始提取手绘作品特征...")
            
            if not self.client:
                raise Exception("Vision API未初始化")
            
            # 读取图片
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Vision提取提示词 - 只提取体态、动作、衣着特征（自然语言描述）
            prompt = """Analyze the art style and the character's outfit in this hand-drawn image. Provide a natural language description focusing on:
- Clothing items: Describe each piece ACCURATELY (top, bottom, outerwear)
- Colors: Be PRECISE about colors - look carefully at what you see (e.g., "blue skirt", "black t-shirt", "red shoes")
- Specific details: text on clothing, patterns, textures
- Accessories: bags, shoes, socks, jewelry, hats, etc.
- Body proportions and pose if distinctive
- Artistic rendering style: color blocks, textures, line work, painting technique

IMPORTANT: 
- Pay close attention to the ACTUAL COLORS in the image
- Describe clothing items accurately as you see them
- Avoid mentioning facial features

Example format:
"wearing a black t-shirt and a blue pleated skirt, white socks with yellow stripes, and brown chunky shoes, holding a tote bag. The art style features bold color blocks with a flat, graphic aesthetic. The fashion style is casual and youthful."

Your description:"""
            
            # 调用 Gemini Vision
            contents = [
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
            ]
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',  # 与人物提取使用相同版本
                contents=contents
            )
            
            response_text = response.text.strip()
            print(f"📥 Vision返回原始文本: {response_text[:200]}...")
            
            # 直接返回自然语言描述（清理引号）
            description = response_text.strip().strip('"').strip("'")
            print(f"✅ 成功提取服饰和风格描述")
            print(f"📝 完整描述内容: {description}")
            print(f"📏 描述长度: {len(description)} 字符")
            print(f"🔍 关键词检查: 是否包含颜色词汇")
            return description
            
        except Exception as e:
            print(f"❌ 提取手绘作品特征失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # 返回基础描述
            return "wearing casual clothing in a simple style"
    
    def build_structured_prompt(self, person_description, outfit_description, lesson_type, style="realistic"):
        """使用固定模板+变量插入构建Prompt
        
        核心策略：固定模板保证风格一致性，变量插入保证灵活性
        
        Args:
            person_description: 人物描述（自然语言）
            outfit_description: 服饰描述（自然语言）
            lesson_type: 课程类型
            style: 输出风格（realistic/cute/anime等）
        
        Returns:
            str: 构建好的完整Prompt
        """
        try:
            print("🔨 开始构建Prompt（固定模板+变量插入）...")
            
            # 如果描述为空，使用默认值
            if not person_description:
                person_description = "A person with natural features"
            if not outfit_description:
                outfit_description = "wearing casual clothing"
            
            # 风格映射：固定的风格控制模板
            style_templates = {
                "realistic": {
                    "composition": "full-body studio portrait",
                    "photography_style": "high-quality fashion photography style",
                    "lighting": "soft studio lighting",
                    "background": "clean solid light grey background",
                    "quality": "realistic textures and details, 8k resolution, highly detailed"
                },
                "cute": {
                    "composition": "full-body character illustration",
                    "photography_style": "cute cartoon style with bright colors and simple lines",
                    "lighting": "soft diffused lighting",
                    "background": "clean pastel background",
                    "quality": "child-friendly, smooth rendering, high quality"
                },
                "anime": {
                    "composition": "full-body anime character",
                    "photography_style": "anime art style with vibrant colors and expressive features",
                    "lighting": "dramatic anime lighting",
                    "background": "clean gradient background",
                    "quality": "detailed line art, professional anime quality"
                }
            }
            
            # 获取风格模板（默认realistic）
            template = style_templates.get(style, style_templates["realistic"])
            
            # 构建最终Prompt：明确指示如何使用两张参考图
            final_prompt = f"""Create a character image using the following reference images and descriptions:

REFERENCE IMAGE 1 (Person's face and features to preserve):
{person_description}
→ Keep the facial features, skin tone, hair style, and overall appearance from the first reference image.

REFERENCE IMAGE 2 (Outfit and style to preserve):
{outfit_description}
→ Keep the clothing style, colors, body proportions, pose, and artistic rendering from the second reference image.

Generate a {template['composition']}, in a {template['photography_style']}, with {template['lighting']}. 
The background should be a {template['background']}. 
Focus on {template['quality']}.

IMPORTANT: Combine the person's facial appearance from Image 1 with the outfit and body styling from Image 2."""
            
            print(f"✅ Prompt构建完成")
            print(f"📝 完整Prompt (前300字): {final_prompt[:300]}...")
            print(f"📝 完整Prompt (全文): {final_prompt}")
            
            return final_prompt
            
        except Exception as e:
            print(f"❌ 构建Prompt失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def combine_with_vision_extraction(self, image1_path, image2_path, lesson_type, style="realistic", aspect_ratio="512x512"):
        """三步自动化流程：Vision提取 + 结构化Prompt + 图像生成
        
        Args:
            image1_path: 人物照片路径
            image2_path: 手绘作品路径
            lesson_type: 课程类型
            style: 输出风格
            aspect_ratio: 输出尺寸
        
        Returns:
            tuple: (生成图片路径, 提取的特征信息)
        """
        try:
            print("="*60)
            print("🚀 开始三步自动化流程：Vision提取 + 结构化Prompt + 图像生成")
            print("="*60)
            
            # 第一步：Vision提取特征（自然语言描述）
            print("\n【第一步】Vision提取特征...")
            person_description = self.extract_person_features(image1_path)
            outfit_description = self.extract_artwork_features(image2_path)
            
            print(f"✅ 特征提取完成")
            print(f"📝 人物描述: {person_description[:100]}...")
            print(f"📝 服饰描述: {outfit_description[:100]}...")
            
            # 第二步：构建Prompt（固定模板+变量插入）
            print("\n【第二步】构建Prompt（固定模板+变量插入）...")
            
            structured_prompt = self.build_structured_prompt(
                person_description,
                outfit_description,
                lesson_type,
                style
            )
            
            if not structured_prompt:
                print("❌ Prompt构建失败，返回None")
                return None, None
            
            # 第三步：生成图像
            print("\n【第三步】生成图像...")
            
            # 读取并压缩图片
            from io import BytesIO
            img1 = Image.open(image1_path)
            if img1.width > 1024 or img1.height > 1024:
                ratio = min(1024 / img1.width, 1024 / img1.height)
                new_size = (int(img1.width * ratio), int(img1.height * ratio))
                img1 = img1.resize(new_size, Image.Resampling.LANCZOS)
            
            buffer1 = BytesIO()
            img1.save(buffer1, format='PNG', optimize=True)
            image1_bytes = buffer1.getvalue()
            
            img2 = Image.open(image2_path)
            if img2.width > 1024 or img2.height > 1024:
                ratio = min(1024 / img2.width, 1024 / img2.height)
                new_size = (int(img2.width * ratio), int(img2.height * ratio))
                img2 = img2.resize(new_size, Image.Resampling.LANCZOS)
            
            buffer2 = BytesIO()
            img2.save(buffer2, format='PNG', optimize=True)
            image2_bytes = buffer2.getvalue()
            
            # 配置
            config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                temperature=0.9,
                top_p=0.95
            )
            
            # 构建内容（提示词 + 两张图片）
            contents = [
                structured_prompt,
                types.Part.from_bytes(data=image1_bytes, mime_type='image/png'),
                types.Part.from_bytes(data=image2_bytes, mime_type='image/png')
            ]
            
            print(f"🔥 调用Gemini 2.5 Flash Image生成...")
            print(f"📋 使用的完整提示词：")
            print(f"{structured_prompt}")
            print(f"📋 提示词长度: {len(structured_prompt)} 字符")
            
            # 调用API
            response = self.client.models.generate_content(
                model='models/gemini-2.5-flash-image',
                contents=contents,
                config=config
            )
            
            # 提取生成的图像
            if not response or not hasattr(response, 'candidates') or not response.candidates:
                print("❌ API返回无效响应")
                return None, None
            
            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not candidate.content:
                print("❌ 响应中没有content")
                return None, None
            
            # 提取图片数据
            image_parts = [
                part.inline_data.data
                for part in candidate.content.parts
                if hasattr(part, 'inline_data') and part.inline_data
            ]
            
            if not image_parts:
                print("❌ 响应中没有生成图片")
                return None, None
            
            print("✅ 成功生成图片")
            
            # 保存图片
            image = Image.open(BytesIO(image_parts[0]))
            
            import uuid
            output_filename = f"combined_{uuid.uuid4().hex}.jpg"
            output_path = os.path.join(self.upload_folder, 'combined', output_filename)
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path, 'JPEG', quality=95)
            
            print(f"✅ 图片已保存: {output_path}")
            print("="*60)
            print("🎉 三步自动化流程完成")
            print("="*60)
            
            # 返回结果和提取的特征
            return output_path, {
                'person_description': person_description,
                'outfit_description': outfit_description,
                'prompt': structured_prompt
            }
            
        except Exception as e:
            print(f"❌ 三步自动化流程失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None