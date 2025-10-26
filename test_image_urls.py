#!/usr/bin/env python3
"""
测试图片URL是否可以正常访问
"""

import requests
import sys
sys.path.append('.')

from app import app
from models import db, Artwork

def test_image_urls():
    """测试图片URL访问"""
    with app.app_context():
        print("🔍 测试作品图片URL访问...")
        
        # 获取所有作品
        artworks = Artwork.query.all()
        
        for artwork in artworks:
            print(f"\n📸 测试作品: {artwork.title}")
            file_urls = artwork.get_file_urls()
            
            # 测试彩色图片
            if file_urls.get('colored_image'):
                url = f"http://127.0.0.1:8080{file_urls['colored_image']}"
                print(f"   URL: {file_urls['colored_image']}")
                
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"   ✅ 彩色图片可访问 (大小: {len(response.content)} bytes)")
                    else:
                        print(f"   ❌ 彩色图片访问失败 (状态码: {response.status_code})")
                except Exception as e:
                    print(f"   ❌ 彩色图片访问异常: {str(e)}")
            
            # 测试3D模型
            if file_urls.get('model_3d'):
                url = f"http://127.0.0.1:8080{file_urls['model_3d']}"
                print(f"   3D模型URL: {file_urls['model_3d']}")
                
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"   ✅ 3D模型可访问 (大小: {len(response.content)} bytes)")
                    else:
                        print(f"   ❌ 3D模型访问失败 (状态码: {response.status_code})")
                except Exception as e:
                    print(f"   ❌ 3D模型访问异常: {str(e)}")

if __name__ == '__main__':
    test_image_urls()