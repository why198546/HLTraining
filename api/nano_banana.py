import requests
import os
import json
import time
from PIL import Image, ImageOps
import base64
import io
import google.generativeai as genai

class NanoBananaAPI:
    """Nano Banana API类 - 使用Gemini 2.5 Flash Image实现"""
    
    def __init__(self):
        # 从环境变量获取API密钥，优先使用Gemini密钥
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('NANO_BANANA_API_KEY', 'your-nano-banana-api-key-here')
        self.upload_folder = 'uploads'
        
        # 初始化Gemini客户端
        try:
            genai.configure(api_key=self.api_key)
            # 使用真正的Nano Banana模型！
            self.client = genai.GenerativeModel('gemini-2.5-flash-image')  # 这就是Nano Banana！
            print("✅ Nano Banana (gemini-2.5-flash-image) API 客户端初始化成功")
        except Exception as e:
            print(f"❌ Nano Banana API 初始化失败: {str(e)}")
            self.client = None
    
    def convert_image_for_video(self, image_path, aspect_ratio='16:9', padding_mode='ai'):
        """
        将图片转换为指定宽高比，用于视频生成
        
        Args:
            image_path: 原始图片路径
            aspect_ratio: 目标宽高比，支持 '16:9' (横屏) 和 '9:16' (竖屏)
            padding_mode: 填充模式
                - 'black': 黑边填充（电影式黑边）
                - 'blur': 模糊边缘填充（自然过渡）
                - 'ai': AI智能填充（默认，使用AI生成新像素）
            
        Returns:
            转换后的图片路径，如果转换失败则返回原路径
        """
        try:
            from PIL import ImageFilter
            
            # 打开原图
            img = Image.open(image_path)
            original_width, original_height = img.size
            
            print(f"📐 原始图片尺寸: {original_width}x{original_height}")
            print(f"� 目标宽高比: {aspect_ratio}")
            print(f"�🎨 填充模式: {padding_mode}")
            
            # 计算目标尺寸
            if aspect_ratio == '16:9':
                # 横屏：宽 > 高
                target_height = original_height
                target_width = int(target_height * 16 / 9)
                is_landscape = True
            elif aspect_ratio == '9:16':
                # 竖屏：高 > 宽
                target_width = original_width
                target_height = int(target_width * 16 / 9)
                is_landscape = False
            else:
                print(f"⚠️ 不支持的宽高比: {aspect_ratio}，使用原图")
                return image_path
            
            print(f"🎯 目标尺寸: {target_width}x{target_height}")
            
            # 如果原图已经符合或超过目标比例，进行裁剪
            if is_landscape:
                # 横屏模式：检查宽度
                if original_width / original_height >= 16 / 9:
                    print("✂️ 图片已经足够宽，进行中心裁剪")
                    left = (original_width - target_width) // 2
                    img_converted = img.crop((left, 0, left + target_width, target_height))
                else:
                    # 需要左右填充
                    padding_width = (target_width - original_width) // 2
                    img_converted = self._apply_horizontal_padding(
                        img, target_width, target_height, padding_width, padding_mode
                    )
            else:
                # 竖屏模式：检查高度
                if original_height / original_width >= 16 / 9:
                    print("✂️ 图片已经足够高，进行中心裁剪")
                    top = (original_height - target_height) // 2
                    img_converted = img.crop((0, top, target_width, top + target_height))
                else:
                    # 需要上下填充
                    padding_height = (target_height - original_height) // 2
                    img_converted = self._apply_vertical_padding(
                        img, target_width, target_height, padding_height, padding_mode
                    )
            
            # 保存转换后的图片
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            ratio_str = aspect_ratio.replace(':', '_')
            output_filename = f"{base_name}_{ratio_str}_{padding_mode}.png"
            output_path = os.path.join(self.upload_folder, output_filename)
            
            img_converted.save(output_path)
            print(f"✅ 图片已转换为{aspect_ratio}: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"❌ 图片转换失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return image_path  # 转换失败时返回原图
    
    def _apply_horizontal_padding(self, img, target_width, target_height, padding_width, padding_mode):
        """横向填充（用于16:9横屏）"""
        from PIL import ImageFilter
        
        if padding_mode == 'black':
            print("⬛ 使用黑边填充（横向）")
            canvas = Image.new('RGB', (target_width, target_height), (0, 0, 0))
            canvas.paste(img, (padding_width, 0))
            return canvas
            
        elif padding_mode == 'ai':
            print("🤖 使用AI智能填充（横向）")
            return self._ai_horizontal_padding(img, target_width, target_height, padding_width)
            
        else:  # blur
            print("🌫️ 使用模糊边缘填充（横向）")
            canvas = Image.new('RGB', (target_width, target_height), (240, 240, 240))
            
            if padding_width > 10:
                edge_width = min(50, img.width // 4)
                
                # 左边缘
                left_edge = img.crop((0, 0, edge_width, img.height))
                left_edge_blurred = left_edge.filter(ImageFilter.GaussianBlur(radius=15))
                left_edge_resized = left_edge_blurred.resize((padding_width, img.height))
                canvas.paste(left_edge_resized, (0, 0))
                
                # 右边缘
                right_edge = img.crop((img.width - edge_width, 0, img.width, img.height))
                right_edge_blurred = right_edge.filter(ImageFilter.GaussianBlur(radius=15))
                right_edge_resized = right_edge_blurred.resize((padding_width, img.height))
                canvas.paste(right_edge_resized, (target_width - padding_width, 0))
            
            canvas.paste(img, (padding_width, 0))
            return canvas
    
    def _apply_vertical_padding(self, img, target_width, target_height, padding_height, padding_mode):
        """纵向填充（用于9:16竖屏）"""
        from PIL import ImageFilter
        
        if padding_mode == 'black':
            print("⬛ 使用黑边填充（纵向）")
            canvas = Image.new('RGB', (target_width, target_height), (0, 0, 0))
            canvas.paste(img, (0, padding_height))
            return canvas
            
        elif padding_mode == 'ai':
            print("🤖 使用AI智能填充（纵向）")
            return self._ai_vertical_padding(img, target_width, target_height, padding_height)
            
        else:  # blur
            print("🌫️ 使用模糊边缘填充（纵向）")
            canvas = Image.new('RGB', (target_width, target_height), (240, 240, 240))
            
            if padding_height > 10:
                edge_height = min(50, img.height // 4)
                
                # 上边缘
                top_edge = img.crop((0, 0, img.width, edge_height))
                top_edge_blurred = top_edge.filter(ImageFilter.GaussianBlur(radius=15))
                top_edge_resized = top_edge_blurred.resize((img.width, padding_height))
                canvas.paste(top_edge_resized, (0, 0))
                
                # 下边缘
                bottom_edge = img.crop((0, img.height - edge_height, img.width, img.height))
                bottom_edge_blurred = bottom_edge.filter(ImageFilter.GaussianBlur(radius=15))
                bottom_edge_resized = bottom_edge_blurred.resize((img.width, padding_height))
                canvas.paste(bottom_edge_resized, (0, target_height - padding_height))
            
            canvas.paste(img, (0, padding_height))
            return canvas
    
    def _ai_horizontal_padding(self, img, target_width, target_height, padding_width):
        """使用AI智能填充横向边缘（生成新像素，而非拉伸）"""
        try:
            print("🔮 正在使用AI生成横向边缘填充...")
            
            # 创建提示词，让AI扩展图片边缘
            extend_prompt = """
请将这张图片的左右两侧自然延伸，创建一个更宽的16:9版本。要求：
1. 保持中心主体完整
2. 左右两侧使用与图片边缘相协调的背景自然延伸  
3. 确保过渡自然，看起来像原本就是宽屏图片
4. 保持原图的风格和色调
5. 不要添加新的主要元素，只是背景延伸
"""
            
            # 调用Gemini进行图像扩展
            response = self.client.generate_content([
                extend_prompt,
                img
            ])
            
            # 提取生成的图像
            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]
            
            if image_parts:
                # 加载AI生成的扩展图像
                ai_img = Image.open(io.BytesIO(image_parts[0]))
                
                # 调整到目标尺寸
                ai_img_resized = ai_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                print("✨ AI横向填充完成")
                return ai_img_resized
            else:
                print("⚠️ AI填充失败，回退到模糊填充")
                return self._apply_horizontal_padding(img, target_width, target_height, padding_width, 'blur')
                
        except Exception as e:
            print(f"⚠️ AI填充出错: {str(e)}, 回退到模糊填充")
            return self._apply_horizontal_padding(img, target_width, target_height, padding_width, 'blur')
    
    def _ai_vertical_padding(self, img, target_width, target_height, padding_height):
        """使用AI智能填充纵向边缘（生成新像素，而非拉伸）"""
        try:
            print("🔮 正在使用AI生成纵向边缘填充...")
            
            # 创建提示词，让AI扩展图片边缘
            extend_prompt = """
请将这张图片的上下两侧自然延伸，创建一个更高的9:16版本。要求：
1. 保持中心主体完整
2. 上下两侧使用与图片边缘相协调的背景自然延伸
3. 确保过渡自然，看起来像原本就是竖屏图片
4. 保持原图的风格和色调
5. 不要添加新的主要元素，只是背景延伸
"""
            
            # 调用Gemini进行图像扩展
            response = self.client.generate_content([
                extend_prompt,
                img
            ])
            
            # 提取生成的图像
            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]
            
            if image_parts:
                # 加载AI生成的扩展图像
                ai_img = Image.open(io.BytesIO(image_parts[0]))
                
                # 调整到目标尺寸
                ai_img_resized = ai_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                print("✨ AI纵向填充完成")
                return ai_img_resized
            else:
                print("⚠️ AI填充失败，回退到模糊填充")
                return self._apply_vertical_padding(img, target_width, target_height, padding_height, 'blur')
                
        except Exception as e:
            print(f"⚠️ AI填充出错: {str(e)}, 回退到模糊填充")
            return self._apply_vertical_padding(img, target_width, target_height, padding_height, 'blur')
    
    def _encode_image_to_base64(self, image_path):
        """将图片编码为base64格式"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"图片编码错误: {str(e)}")
            return None
    
    def colorize_sketch(self, sketch_path, description="", style="cute", color_preference="colorful", expert_mode=False):
        """为手绘简笔画上色 - 使用Gemini 2.5 Flash Image"""
        try:
            print("🍌 开始使用Nano Banana (Gemini)进行图像上色...")
            print(f"🎨 风格: {style}, 色彩偏好: {color_preference}, Expert模式: {expert_mode}")
            
            # 检查客户端
            if not self.client:
                raise Exception("Nano Banana API未配置，请检查GEMINI_API_KEY环境变量")
            
            # 读取图像
            with open(sketch_path, 'rb') as f:
                image_bytes = f.read()
            
            # Expert模式：直接使用用户输入的prompt，不添加任何额外内容
            if expert_mode:
                prompt = description if description else "为这张图片上色"
                print(f"⚡ Expert模式 - 原始prompt: {prompt}")
            else:
                # 风格映射
                style_prompts = {
                    'cute': '可爱卡通风格，圆润的线条，柔和的造型，Q版比例，大眼睛，萌系表情',
                    'realistic': '写实风格，真实的光影效果，细腻的质感，准确的比例，自然的色彩过渡',
                    'anime': '日式动漫风格，清晰的线条，大眼睛，丰富的色块，高对比度，夸张的表情和动作',
                    'fantasy': '奇幻风格，魔法光效，梦幻色彩，神秘氛围，炫目的视觉效果，超现实元素'
                }
                
                # 色彩偏好映射
                color_prompts = {
                    'colorful': '色彩丰富鲜艳，饱和度高，多种颜色和谐搭配，充满活力',
                    'soft': '柔和色调，低饱和度，温柔的粉色系、米色系或淡蓝色系，宁静温馨',
                    'bright': '明亮鲜艳的颜色，高亮度，高对比度，充满能量，让人眼前一亮',
                    'natural': '自然色彩，大地色系，贴近真实物体的颜色，舒适自然'
                }
                
                style_desc = style_prompts.get(style, style_prompts['cute'])
                color_desc = color_prompts.get(color_preference, color_prompts['colorful'])
                
                # 构建基于用户描述的提示词
                if description:
                    prompt = f"""
请根据用户的要求为这张手绘简笔画上色：

用户要求：{description}

风格要求：{style_desc}
色彩要求：{color_desc}

请按照以下标准执行：
1. 严格遵循用户的描述、风格和色彩要求
2. 适合10-14岁儿童审美
3. 保持原始线条清晰可见
4. 添加适当的阴影和高光，增强立体感
5. 背景保持简洁干净，避免杂乱元素
6. 确保整体风格统一，符合选定的风格特点
7. 色彩搭配和谐，主体突出

请生成一张完全符合要求的上色图像！
"""
                else:
                    prompt = f"""
请为这张手绘简笔画添加美丽的颜色，要求：

风格要求：{style_desc}
色彩要求：{color_desc}

基本标准：
1. 适合10-14岁儿童审美
2. 保持原始线条清晰可见
3. 添加适当的阴影和高光，增强立体感
4. 背景保持简洁干净，纯色或简单渐变
5. 主体突出，避免背景喧宾夺主
6. 确保整体风格统一，符合选定的风格特点
7. 色彩搭配和谐

请生成一张完全上色的图像！
"""
            
            print(f"🎨 用户描述：{description or '使用默认风格'}")
            
            # 将图像转换为PIL Image对象
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            response = self.client.generate_content([
                prompt,
                pil_image
            ])
            
            # 提取生成的图像
            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]
            
            if image_parts:
                # 保存图像
                base_name = os.path.splitext(os.path.basename(sketch_path))[0]
                colored_filename = f"{base_name}_colored.png"
                output_path = os.path.join(self.upload_folder, colored_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(image_parts[0])
                
                print(f"✅ Nano Banana上色完成: {output_path}")
                
                # 不再自动转换为16:9，保持原始1024x1024
                return output_path
            else:
                raise Exception("未能从Gemini响应中提取图像")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Nano Banana上色错误: {error_msg}")
            
            # 检查是否是配额耗尽错误
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                print("⚠️  API配额已耗尽，请稍后再试")
                # 可以在这里添加额外的配额耗尽处理逻辑
            
            return None
    
    def generate_figurine_style(self, colored_image_path, description=""):
        """生成手办风格图片 - 使用Gemini 2.5 Flash Image"""
        try:
            print("🏺 开始使用Nano Banana (Gemini)生成手办风格...")
            
            # 检查客户端
            if not self.client:
                raise Exception("Nano Banana API未配置，请检查GEMINI_API_KEY环境变量")
            
            # 读取图像
            with open(colored_image_path, 'rb') as f:
                image_bytes = f.read()
            
            # 构建手办风格提示词
            figurine_prompt = f"""
请将这张图像转换为手办(figurine)风格，特点如下：
1. 塑料或树脂材质的光泽感和质感
2. 鲜艳、饱和的颜色，如同塑料玩具
3. 平滑的表面，减少细节纹理
4. 增强的对比度和立体感
5. 适合作为收藏品展示的精致外观
6. 保持可爱、友好的外观，适合儿童
7. 增加轻微的反光效果，模拟塑料材质
8. 保持原始构图和主要特征不变

{f'用户额外要求：{description}' if description else ''}

请生成一张具有手办质感的图像。
"""
            
            print(f"🎯 用户描述：{description or '使用默认手办风格'}")
            
            # 将图像转换为PIL Image对象
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            response = self.client.generate_content([
                figurine_prompt,
                pil_image
            ])
            
            # 提取生成的图像
            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]
            
            if image_parts:
                # 保存图像
                base_name = os.path.splitext(os.path.basename(colored_image_path))[0]
                figurine_filename = f"{base_name}_figurine.png"
                output_path = os.path.join(self.upload_folder, figurine_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(image_parts[0])
                
                print(f"✅ Nano Banana手办风格生成完成: {output_path}")
                
                # 不再自动转换为16:9，保持原始尺寸
                return output_path
            else:
                raise Exception("未能从Gemini响应中提取图像")
                
        except Exception as e:
            print(f"❌ Nano Banana手办风格生成错误: {str(e)}")
            raise e
    
    def check_api_status(self):
        """检查Nano Banana (Gemini) API状态"""
        try:
            return self.client is not None and self.api_key != 'your-nano-banana-api-key-here'
        except Exception as e:
            print(f"API状态检查失败: {str(e)}")
            return False
    
    def generate_image_from_text(self, text_prompt, style="cute", color_preference="colorful", expert_mode=False):
        """从文字描述生成图片 - 使用真正的Nano Banana图像生成！"""
        try:
            print(f"🎨 开始使用真正的Nano Banana (gemini-2.5-flash-image)生成图片...")
            print(f"📝 提示词: {text_prompt}")
            print(f"🎨 风格: {style}, 色彩偏好: {color_preference}, Expert模式: {expert_mode}")
            
            # 检查客户端
            if not self.client:
                raise Exception("Nano Banana API未配置，请检查GEMINI_API_KEY环境变量")
            
            # Expert模式：直接使用用户输入的prompt
            if expert_mode:
                image_prompt = text_prompt
                print(f"⚡ Expert模式 - 原始prompt: {image_prompt}")
            else:
                # 风格映射
                style_prompts = {
                    'cute': '可爱卡通风格，圆润的线条，柔和的造型，Q版比例',
                    'realistic': '写实风格，真实的光影效果，细腻的质感',
                    'anime': '日式动漫风格，清晰的线条，大眼睛，高对比度',
                    'fantasy': '奇幻风格，魔法光效，梦幻色彩，炫目的视觉效果'
                }
                
                # 色彩偏好映射
                color_prompts = {
                    'colorful': '色彩丰富鲜艳，饱和度高，充满活力',
                    'soft': '柔和色调，低饱和度，温柔的粉色系或米色系',
                    'bright': '明亮鲜艳的颜色，高亮度，高对比度',
                    'natural': '自然色彩，大地色系，贴近真实物体的颜色'
                }
                
                style_desc = style_prompts.get(style, style_prompts['cute'])
                color_desc = color_prompts.get(color_preference, color_prompts['colorful'])
                
                # 构建适合儿童的图像生成提示，加入风格和色彩偏好
                image_prompt = f"""创建一幅适合10-14岁儿童的插画：{text_prompt}

风格要求：{style_desc}
色彩要求：{color_desc}

基本要求：
- 适合儿童观看，健康正面的内容
- 富有创意和想象力
- 简洁清晰的构图
- 背景简洁干净，避免杂乱元素
- 主体突出，背景纯色或简单渐变
- 整体风格统一，色彩和谐"""
            
            print(f"📝 最终提示词: {image_prompt}")
            
            # 使用专门的图像生成模型，支持重试机制
            max_retries = 3
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                try:
                    retry_count += 1
                    print(f"🔥 正在使用Nano Banana生成真实图片... (尝试 {retry_count}/{max_retries})")
                    
                    # 使用正确的客户端API调用方式
                    # 创建图像生成专用模型 - 使用正确的Nano Banana模型
                    image_gen_client = genai.GenerativeModel('gemini-2.5-flash-image')
                    response = image_gen_client.generate_content(image_prompt)
                    
                    # 检查是否成功生成图片
                    print(f"🔍 响应检查: response={bool(response)}")
                    if response:
                        print(f"🔍 candidates: {hasattr(response, 'candidates')} - {bool(response.candidates) if hasattr(response, 'candidates') else 'N/A'}")
                        
                    if response and hasattr(response, 'candidates') and response.candidates:
                        print(f"🔍 候选项数量: {len(response.candidates)}")
                        if response.candidates[0].content and response.candidates[0].content.parts:
                            print(f"🔍 内容部分数量: {len(response.candidates[0].content.parts)}")
                            for i, part in enumerate(response.candidates[0].content.parts):
                                print(f"🔍 Part {i}: text={bool(part.text)}, inline_data={bool(part.inline_data)}")
                        
                        # 查找返回的图像数据
                        image_parts = [
                            part.inline_data.data
                            for part in response.candidates[0].content.parts
                            if part.inline_data
                        ]
                        
                        if image_parts:
                            # 保存图片数据到文件
                            timestamp = int(time.time())
                            filename = f"nano_banana_text_{timestamp}.png"
                            filepath = os.path.join(self.upload_folder, filename)
                            
                            # 处理Gemini返回的图像数据
                            from io import BytesIO
                            
                            # Gemini返回的是原始字节数据，不是base64编码的
                            image_data = image_parts[0]  # 直接使用bytes数据
                            image = Image.open(BytesIO(image_data))
                            image.save(filepath)
                            
                            print(f"✅ Nano Banana真实图片生成并保存成功: {filepath}")
                            
                            # 不再自动转换为16:9，保持原始尺寸
                            return filepath
                        else:
                            error_msg = "响应中没有找到图片数据"
                            print(f"⚠️ {error_msg}")
                            if retry_count < max_retries:
                                print(f"🔄 将进行第 {retry_count + 1} 次重试...")
                                last_error = Exception(error_msg)
                                continue
                            else:
                                raise Exception(error_msg)
                    else:
                        error_msg = "Nano Banana未返回有效响应"
                        print(f"⚠️ {error_msg}")
                        if retry_count < max_retries:
                            print(f"🔄 将进行第 {retry_count + 1} 次重试...")
                            last_error = Exception(error_msg)
                            continue
                        else:
                            raise Exception(error_msg)
                            
                except Exception as img_error:
                    last_error = img_error
                    print(f"⚠️ 第 {retry_count} 次尝试失败: {img_error}")
                    if retry_count < max_retries:
                        print(f"🔄 将进行第 {retry_count + 1} 次重试...")
                        continue
                    else:
                        print(f"❌ 所有 {max_retries} 次重试都失败了")
                        break
                        
            # 如果所有重试都失败，降级到艺术指导方案
            print("🔄 降级使用艺术指导方案...")
            
            try:
                # 降级方案：使用原有的艺术指导方法
                art_prompt = f"""
作为一位专业的儿童美术老师，请根据以下描述为10-14岁的孩子创作一幅详细的绘画作品：

{text_prompt}

请提供详细的绘画步骤和色彩搭配建议：
1. 画面构图布局
2. 主要元素的形状和位置
3. 具体的颜色搭配（RGB值）
4. 绘画技巧和细节处理
5. 整体风格建议

要求内容健康正面，适合儿童，富有创意和教育意义。
"""
                
                # 调用Gemini获取艺术指导
                response = self.client.generate_content([art_prompt])
            
                if response and hasattr(response, 'candidates') and response.candidates:
                    art_guidance = response.candidates[0].content.parts[0].text
                    print(f"🎨 AI艺术指导: {art_guidance}")
                    
                    # 如果无法生成图片，直接抛出异常说明降级到艺术指导
                    raise Exception("没有图片数据，使用备用方案")
                else:
                    raise Exception("未能从Gemini获取艺术指导")
            except Exception as art_error:
                # 如果艺术指导也失败，抛出原始图片生成错误
                raise last_error if last_error else art_error
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Nano Banana文字生成图片错误: {error_msg}")
            
            # 检查是否是配额耗尽错误
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                print("⚠️  API配额已耗尽，请稍后再试")
            
            # AI服务不可用时直接返回错误
            raise e
    


    # 新的统一工作流程方法
    def generate_image_from_sketch(self, sketch_path, style="cute", color_preference="colorful", expert_mode=False):
        """从手绘图片生成图片（纯图片模式）"""
        try:
            print(f"🎨 纯图片模式：为手绘图生成AI图片 - {sketch_path}")
            
            # 使用已有的上色方法，传入风格参数和expert_mode
            return self.colorize_sketch(sketch_path, "", style=style, color_preference=color_preference, expert_mode=expert_mode)
            
        except Exception as e:
            print(f"❌ 纯图片模式生成失败: {str(e)}")
            return None

    def generate_image_from_sketch_and_text(self, sketch_path, text_prompt, style="cute", color_preference="colorful", expert_mode=False):
        """从手绘图片和文字描述生成图片（图片+文字模式）"""
        try:
            print(f"🎨 图片+文字模式：为手绘图生成AI图片 - {sketch_path}")
            
            # 使用已有的上色方法，传入文字描述和expert_mode
            return self.colorize_sketch(sketch_path, text_prompt, style=style, color_preference=color_preference, expert_mode=expert_mode)
            
        except Exception as e:
            print(f"❌ 图片+文字模式生成失败: {str(e)}")
            return None

    def adjust_image(self, current_image_path, adjust_prompt, expert_mode=False):
        """调整现有图片"""
        try:
            print(f"🔧 图片调整模式：{current_image_path} - 调整说明: {adjust_prompt}")
            print(f"⚡ Expert模式: {expert_mode}")
            
            if not self.client:
                raise Exception("Nano Banana API未配置，请检查GEMINI_API_KEY环境变量")
            
            # 读取当前图片
            with open(current_image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Expert模式：直接使用用户输入的prompt
            if expert_mode:
                prompt = adjust_prompt
                print(f"⚡ Expert模式 - 原始prompt: {prompt}")
            else:
                # 构建调整提示词
                prompt = f"""
请根据用户的调整要求修改这张图片：

用户调整要求：{adjust_prompt}

请按照以下标准执行：
1. 严格按照用户的调整要求进行修改
2. 保持图片的整体风格和质量
3. 确保修改后的图片适合10-14岁儿童
4. 保持色彩鲜艳和谐
5. 如果是颜色调整，要确保搭配合理
6. 如果是内容调整，要保持原有的基本构图

请生成调整后的图片！
"""
            
            # 将图像转换为PIL Image对象
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            response = self.client.generate_content([
                prompt,
                pil_image
            ])
            
            # 提取生成的图像
            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]
            
            if image_parts:
                # 保存调整后的图像
                timestamp = int(time.time())
                base_name = os.path.splitext(os.path.basename(current_image_path))[0]
                adjusted_filename = f"{base_name}_adjusted_{timestamp}.png"
                adjusted_path = os.path.join(self.upload_folder, adjusted_filename)
                
                # 保存图像
                with open(adjusted_path, 'wb') as f:
                    f.write(image_parts[0])
                
                print(f"✅ 图片调整完成: {adjusted_path}")
                
                # 不再自动转换为16:9，保持原始尺寸
                return adjusted_path
            else:
                raise Exception("未能生成调整后的图片")
                
        except Exception as e:
            print(f"❌ 图片调整失败: {str(e)}")
            return None