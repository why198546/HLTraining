#!/usr/bin/env python3
"""
生成松果课堂参考示例图片
使用Nano Banana API为每个示例生成真实图片
"""

import os
import sys
import requests
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.nano_banana import NanoBananaAPI

# 定义所有示例及其提示词（与模板中的提示词一致）
EXAMPLES = {
    'character': [
        {
            'filename': 'character_kid.png',
            'prompt': '一个10岁的小朋友，短发，圆脸，大眼睛，微笑，穿蓝色校服，卡通插画，干净背景',
            'style': 'cartoon'
        },
        {
            'filename': 'character_robot.png',
            'prompt': '一个可爱的小机器人，圆润外形，发光眼睛，配色清爽，卡通插画，简洁背景',
            'style': 'cartoon'
        },
        {
            'filename': 'character_explorer.png',
            'prompt': '一个勇敢的小探险家，戴红色帽子，背小背包，表情自信，卡通插画，明亮色彩',
            'style': 'cartoon'
        }
    ],
    'action': [
        {
            'filename': 'action_run.png',
            'prompt': '一个小朋友在操场上跑步，全身，姿势自然，四肢完整，表情开心，卡通插画，干净背景',
            'style': 'cartoon'
        },
        {
            'filename': 'action_jump.png',
            'prompt': '一个小朋友跳跃起来，双手举高，全身，动作夸张但自然，卡通插画，明亮色彩',
            'style': 'cartoon'
        },
        {
            'filename': 'action_wave.png',
            'prompt': '一个可爱的小机器人挥手打招呼，半身，动作清晰，表情友好，卡通插画，简洁背景',
            'style': 'cartoon'
        }
    ],
    'scene': [
        {
            'filename': 'scene_classroom.png',
            'prompt': '明亮的教室，黑板、课桌、窗户，阳光照进来，色彩丰富，卡通插画，画面简洁',
            'style': 'cartoon'
        },
        {
            'filename': 'scene_park.png',
            'prompt': '阳光明媚的公园，草地、大树、小路，天空有白云，色彩明亮，卡通插画，主体突出',
            'style': 'cartoon'
        },
        {
            'filename': 'scene_living.png',
            'prompt': '温馨的家里客厅，沙发、地毯、窗帘，暖色灯光，画面干净，卡通插画，细节适中',
            'style': 'cartoon'
        }
    ],
    'practice': [
        {
            'filename': 'practice_1.png',
            'prompt': '一个小朋友，短发，微笑，穿蓝色校服；正在操场上跑步，全身，姿势自然，四肢完整；背景简单；卡通插画，色彩明亮',
            'style': 'cartoon'
        },
        {
            'filename': 'practice_2.png',
            'prompt': '一个可爱的小机器人；挥手打招呼，半身；背景是阳光明媚的公园，有草地和大树；卡通插画，清爽配色，主体突出',
            'style': 'cartoon'
        },
        {
            'filename': 'practice_3.png',
            'prompt': '一个认真听课的小朋友，表情专注；坐在课桌前；明亮的教室里有黑板和窗户，阳光照进来；卡通插画，细节适中，画面干净',
            'style': 'cartoon'
        }
    ]
}

def main():
    # 创建输出目录
    output_dir = project_root / 'static' / 'images' / 'sunguo_examples'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化API
    api = NanoBananaAPI()
    
    print("🎨 开始生成松果课堂参考示例图片...")
    print(f"📁 输出目录: {output_dir}")
    print()
    
    total = sum(len(examples) for examples in EXAMPLES.values())
    current = 0
    
    for category, examples in EXAMPLES.items():
        print(f"\n📂 {category.upper()} 类别:")
        print("-" * 60)
        
        for example in examples:
            current += 1
            filename = example['filename']
            prompt = example['prompt']
            style = example['style']
            
            print(f"[{current}/{total}] 生成: {filename}")
            print(f"  提示词: {prompt}")
            
            try:
                # 调用API生成图片 - 使用generate_image_from_text方法
                result = api.generate_image_from_text(
                    text_prompt=prompt,
                    style=style,
                    aspect_ratio='1:1'  # 正方形，适合示例卡片
                )
                
                if result:
                    # result是图片路径字符串
                    output_path = output_dir / filename
                    
                    # 复制生成的图片到目标目录
                    import shutil
                    shutil.copy2(result, output_path)
                    
                    print(f"  ✅ 成功: {output_path}")
                else:
                    print(f"  ❌ 失败: API返回None")
                
                # 添加延迟避免API限流
                time.sleep(2)
                    
            except Exception as e:
                print(f"  ❌ 异常: {str(e)}")
                import traceback
                traceback.print_exc()
            
            print()
    
    print("=" * 60)
    print("🎉 所有图片生成完成！")
    print(f"📁 图片位置: {output_dir}")

if __name__ == '__main__':
    main()
