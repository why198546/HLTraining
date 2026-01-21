#!/usr/bin/env python3
"""
测试后端API返回值格式
"""

import json

def test_api_response_format():
    """测试API返回值中的detected_features格式"""
    
    # 模拟API返回值
    api_response = {
        'success': True,
        'image_url': '/uploads/test.png',
        'image_urls': ['/uploads/test1.png', '/uploads/test2.png', '/uploads/test3.png', '/uploads/test4.png'],
        'image_path': '/uploads/test.png',
        'version_id': None,
        'detected_features': {0: '男孩', 2: '长发', 5: '大眼睛'},  # 这是后端返回的格式
        'message': '成功生成 4 张图片！'
    }
    
    print("API响应模拟:")
    print(json.dumps(api_response, ensure_ascii=False, indent=2))
    print()
    
    # 验证detected_features的格式
    detected = api_response['detected_features']
    print(f"✅ detected_features: {detected}")
    print(f"✅ 类型: {type(detected)}")
    print()
    
    # 前端使用这个detected_features的方式
    print("前端使用方式:")
    print("-" * 60)
    
    # 方法1: 检查特定特征是否被检测到
    if 0 in detected:
        print(f"✅ 检测到了性别特征: {detected[0]}")
    
    if 2 in detected:
        print(f"✅ 检测到了头发长度特征: {detected[2]}")
    
    # 方法2: 获取所有检测到的特征索引
    detected_indices = set(detected.keys())
    print(f"✅ 检测到的特征索引集合: {detected_indices}")
    
    # 方法3: 过滤未检测到的特征
    all_features = set(range(10))  # 0-9
    undetected_indices = all_features - detected_indices
    print(f"✅ 未检测到的特征索引: {undetected_indices}")
    
    # 验证常识规则
    print()
    print("常识规则验证:")
    print("-" * 60)
    
    # 检查性别和头发长度是否矛盾
    if 0 in detected and 2 in detected:
        gender = detected[0]
        hair_length = detected[2]
        
        if '男孩' in gender or '男' in gender:
            print(f"✅ 性别: 男孩")
            if '长发' in hair_length:
                print(f"⚠️ 警告: 男孩但检测到长发，这在现实中不常见")
            else:
                print(f"✅ 头发长度: {hair_length} (合理)")
        
        if '女孩' in gender or '女' in gender:
            print(f"✅ 性别: 女孩")
            if '短发' in hair_length:
                print(f"⚠️ 警告: 女孩但检测到短发，这在现实中不太常见")
            else:
                print(f"✅ 头发长度: {hair_length} (合理)")

if __name__ == '__main__':
    test_api_response_format()
