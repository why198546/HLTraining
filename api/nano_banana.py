import requests
import os
import json
import time
from PIL import Image, ImageOps
import base64
import io
from google import genai
from google.genai import types

class NanoBananaAPI:
    """Nano Banana API类 - 使用Gemini 2.5 Flash Image (真正的Nano Banana模型)"""
    
    def __init__(self):
        # 从环境变量获取API密钥，优先使用Gemini密钥
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('NANO_BANANA_API_KEY', 'your-nano-banana-api-key-here')
        self.upload_folder = 'uploads'
        
        # 初始化新的Google Gen AI客户端
        try:
            self.client = genai.Client(api_key=self.api_key)
            print("✅ Google Gen AI 客户端初始化成功 (Gemini 2.5 Flash Image)")
        except Exception as e:
            print(f"❌ Google Gen AI 客户端初始化失败: {str(e)}")
            self.client = None
    
    def colorize_sketch(self, sketch_path, description="", style="cute", color_preference="colorful", expert_mode=False, aspect_ratio="1:1"):
        """为手绘简笔画上色 - 使用Gemini 2.5 Flash Image模型（真正的Nano Banana）"""
        try:
            print("🎨 开始使用Gemini 2.5 Flash Image (Nano Banana) 进行图像上色...")
            print(f"🎨 风格: {style}, 色彩偏好: {color_preference}, Expert模式: {expert_mode}, 高宽比: {aspect_ratio}")
            
            # 检查客户端
            if not self.client:
                raise Exception("Google Gen AI客户端未配置，请检查GEMINI_API_KEY环境变量")
            
            # 读取图像
            with open(sketch_path, 'rb') as f:
                image_bytes = f.read()
            
            # Expert模式：直接使用用户输入的prompt，不添加任何额外内容
            if expert_mode:
                prompt = description if description else "为这张图片上色"
            else:
                # 风格映射
                style_prompts = {
                    'cute': '可爱卡通风格',
                    'realistic': '写实风格',
                    'anime': '日式动漫风格',
                    'fantasy': '奇幻风格'
                }
                
                # 色彩偏好映射
                color_prompts = {
                    'colorful': '色彩丰富鲜艳',
                    'soft': '柔和色调',
                    'bright': '明亮鲜艳',
                    'natural': '自然色彩'
                }
                
                style_desc = style_prompts.get(style, style_prompts['cute'])
                color_desc = color_prompts.get(color_preference, color_prompts['colorful'])
                
                # 简化的提示词构建，保持原始意图
                if description:
                    prompt = f"为这张手绘简笔画上色: {description}, {style_desc}, {color_desc}"
                else:
                    prompt = f"为这张手绘简笔画添加美丽的颜色, {style_desc}, {color_desc}, 适合儿童观看"
            
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
                    
                    # 使用Gemini 2.5 Flash Image - 这才是真正的Nano Banana！
                    config = types.GenerateContentConfig(
                        response_modalities=["IMAGE"],  # 明确要求返回图片
                        temperature=0.7
                    )
                    
                    response = self.client.models.generate_content(
                        model='models/gemini-2.5-flash-image',  # 使用Gemini 2.5 Flash Image
                        contents=[
                            prompt,
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type='image/png'
                            )
                        ],
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
                        last_error = "响应中没有candidates"
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
                        
                        # 调整图片尺寸以匹配aspect_ratio
                        if aspect_ratio != "1:1":
                            width, height = image.size
                            ratio_parts = aspect_ratio.split(':')
                            target_ratio = int(ratio_parts[0]) / int(ratio_parts[1])
                            current_ratio = width / height
                            
                            # 如果比例不匹配，调整尺寸
                            if abs(current_ratio - target_ratio) > 0.1:
                                if target_ratio > current_ratio:
                                    # 需要更宽
                                    new_width = int(height * target_ratio)
                                    new_height = height
                                else:
                                    # 需要更高
                                    new_width = width
                                    new_height = int(width / target_ratio)
                                
                                # 创建新画布
                                new_image = Image.new('RGB', (new_width, new_height), (255, 255, 255))
                                # 将原图居中粘贴
                                x_offset = (new_width - width) // 2
                                y_offset = (new_height - height) // 2
                                new_image.paste(image, (x_offset, y_offset))
                                image = new_image
                                print(f"📐 调整图片尺寸以匹配 {aspect_ratio}")
                        
                        # 保存上色后的图像
                        base_name = os.path.splitext(os.path.basename(sketch_path))[0]
                        colored_filename = f"{base_name}_colored.jpg"
                        output_path = os.path.join(self.upload_folder, colored_filename)
                        
                        # 保存图片
                        image.save(output_path, 'JPEG', quality=95)
                        
                        print(f"✅ Gemini上色完成: {output_path}")
                        print(f"📐 高宽比: {aspect_ratio}")
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

    def generate_image_from_text(self, text_prompt, style="cute", color_preference="colorful", expert_mode=False, aspect_ratio="1:1"):
        """从文字描述生成图片 - 使用Gemini 2.5 Flash Image官方API，原生高宽比支持！"""
        try:
            print(f"🎨 开始使用Gemini 2.5 Flash Image官方API生成图片...")
            print(f"📝 提示词: {text_prompt}")
            print(f"🎨 风格: {style}, 色彩偏好: {color_preference}, Expert模式: {expert_mode}")
            print(f"📐 原生高宽比: {aspect_ratio}")
            
            # 检查客户端
            if not self.client:
                raise Exception("Google Gen AI客户端未配置，请检查GEMINI_API_KEY环境变量")
            
            # Expert模式：直接使用用户输入的prompt
            if expert_mode:
                image_prompt = text_prompt
                print(f"⚡ Expert模式 - 原始prompt: {image_prompt}")
            else:
                # 风格映射
                style_prompts = {
                    'cute': '可爱卡通风格',
                    'realistic': '写实风格',
                    'anime': '日式动漫风格',
                    'fantasy': '奇幻风格'
                }
                
                # 色彩偏好映射
                color_prompts = {
                    'colorful': '色彩丰富鲜艳',
                    'soft': '柔和色调',
                    'bright': '明亮鲜艳',
                    'natural': '自然色彩'
                }
                
                style_desc = style_prompts.get(style, style_prompts['cute'])
                color_desc = color_prompts.get(color_preference, color_prompts['colorful'])
                
                # 简化的提示词构建，保持原始意图
                image_prompt = f"{text_prompt}, {style_desc}, {color_desc}, 适合儿童观看的内容"
            
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
                    
                    generate_content_config = types.GenerateContentConfig(
                        response_modalities=[
                            "IMAGE",
                            "TEXT",
                        ],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,  # 原生高宽比支持！
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
    
    def generate_image_from_sketch(self, sketch_path, style="cute", color_preference="colorful", expert_mode=False, aspect_ratio="1:1"):
        """从手绘图片生成图片（纯图片模式）"""
        try:
            print(f"🎨 纯图片模式：为手绘图生成AI图片 - {sketch_path}")
            
            # 使用已有的上色方法，传入风格参数和expert_mode
            return self.colorize_sketch(sketch_path, "", style=style, color_preference=color_preference, expert_mode=expert_mode, aspect_ratio=aspect_ratio)
            
        except Exception as e:
            print(f"❌ 纯图片模式生成失败: {str(e)}")
            return None

    def generate_image_from_sketch_and_text(self, sketch_path, text_prompt, style="cute", color_preference="colorful", expert_mode=False, aspect_ratio="1:1"):
        """从手绘图片和文字描述生成图片（图片+文字模式）"""
        try:
            print(f"🎨 图片+文字模式：为手绘图生成AI图片 - {sketch_path}")
            
            # 使用已有的上色方法，传入文字描述和expert_mode
            return self.colorize_sketch(sketch_path, text_prompt, style=style, color_preference=color_preference, expert_mode=expert_mode, aspect_ratio=aspect_ratio)
            
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
