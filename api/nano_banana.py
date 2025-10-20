import requests
import os
import json
import time
from PIL import Image
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
    
    def _encode_image_to_base64(self, image_path):
        """将图片编码为base64格式"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"图片编码错误: {str(e)}")
            return None
    
    def colorize_sketch(self, sketch_path, description=""):
        """为手绘简笔画上色 - 使用Gemini 2.5 Flash Image"""
        try:
            print("🍌 开始使用Nano Banana (Gemini)进行图像上色...")
            
            # 检查客户端
            if not self.client:
                raise Exception("Nano Banana API未配置，请检查GEMINI_API_KEY环境变量")
            
            # 读取图像
            with open(sketch_path, 'rb') as f:
                image_bytes = f.read()
            
            # 构建基于用户描述的提示词
            if description:
                prompt = f"""
请根据用户的要求为这张手绘简笔画上色：

用户要求：{description}

请按照以下标准执行：
1. 严格遵循用户的描述和要求
2. 使用鲜艳、活泼的颜色，适合10-14岁儿童
3. 保持原始线条清晰可见
4. 添加适当的阴影和高光，增强立体感
5. 背景保持简洁干净，避免杂乱元素
6. 整体风格要卡通化、可爱友好
7. 确保色彩搭配和谐，主体突出

请生成一张完全符合用户要求的上色图像！
"""
            else:
                prompt = """
请为这张手绘简笔画添加美丽的颜色，要求：
1. 使用鲜艳、活泼的颜色，适合10-14岁儿童
2. 颜色搭配要和谐，富有想象力
3. 保持原始线条清晰可见
4. 添加适当的阴影和高光，增强立体感
5. 背景保持简洁干净，纯色或简单渐变
6. 主体突出，避免背景喧宾夺主
7. 整体风格要卡通化、可爱友好

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
    
    def generate_image_from_text(self, text_prompt):
        """从文字描述生成图片 - 使用真正的Nano Banana图像生成！"""
        try:
            print(f"🎨 开始使用真正的Nano Banana (gemini-2.5-flash-image)生成图片...")
            print(f"📝 提示词: {text_prompt}")
            
            # 检查客户端
            if not self.client:
                raise Exception("Nano Banana API未配置，请检查GEMINI_API_KEY环境变量")
            
            # 使用专门的图像生成模型，支持重试机制
            max_retries = 3
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                try:
                    retry_count += 1
                    print(f"🔥 正在使用Nano Banana生成真实图片... (尝试 {retry_count}/{max_retries})")
                    
                    # 构建适合儿童的图像生成提示
                    image_prompt = f"""创建一幅适合10-14岁儿童的卡通风格插画：{text_prompt}

要求：
- 明亮温和的色彩，卡通/插画风格
- 健康正面的内容，富有创意和想象力
- 适合儿童观看，简洁清晰的构图
- 背景简洁干净，避免杂乱元素
- 主体突出，背景纯色或简单渐变
- 整体风格统一，色彩和谐"""
                    
                    print(f"📝 最终提示词: {image_prompt}")
                    
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
    def generate_image_from_sketch(self, sketch_path):
        """从手绘图片生成图片（纯图片模式）"""
        try:
            print(f"🎨 纯图片模式：为手绘图生成AI图片 - {sketch_path}")
            
            # 使用已有的上色方法
            return self.colorize_sketch(sketch_path, "")
            
        except Exception as e:
            print(f"❌ 纯图片模式生成失败: {str(e)}")
            return None

    def generate_image_from_sketch_and_text(self, sketch_path, text_prompt):
        """从手绘图片和文字描述生成图片（图片+文字模式）"""
        try:
            print(f"🎨 图片+文字模式：{sketch_path} + {text_prompt}")
            
            # 使用上色方法，传入文字描述
            return self.colorize_sketch(sketch_path, text_prompt)
            
        except Exception as e:
            print(f"❌ 图片+文字模式生成失败: {str(e)}")
            return None

    def adjust_image(self, current_image_path, adjust_prompt):
        """调整现有图片"""
        try:
            print(f"🔧 图片调整模式：{current_image_path} - 调整说明: {adjust_prompt}")
            
            if not self.client:
                raise Exception("Nano Banana API未配置，请检查GEMINI_API_KEY环境变量")
            
            # 读取当前图片
            with open(current_image_path, 'rb') as f:
                image_bytes = f.read()
            
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
                return adjusted_path
            else:
                raise Exception("未能生成调整后的图片")
                
        except Exception as e:
            print(f"❌ 图片调整失败: {str(e)}")
            return None