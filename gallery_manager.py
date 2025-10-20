import json
import os
from datetime import datetime
import uuid
import shutil

class GalleryManager:
    def __init__(self, data_file='gallery_data.json', gallery_folder='static/gallery'):
        self.data_file = data_file
        self.gallery_folder = gallery_folder
        self.ensure_directories()
        
    def ensure_directories(self):
        """确保必要的目录存在"""
        os.makedirs(self.gallery_folder, exist_ok=True)
        os.makedirs(os.path.join(self.gallery_folder, 'images'), exist_ok=True)
        os.makedirs(os.path.join(self.gallery_folder, 'models'), exist_ok=True)
        
    def load_gallery_data(self):
        """加载作品集数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_gallery_data(self, data):
        """保存作品集数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_artwork(self, original_image_path, generated_image_path, model_path=None, 
                     title="我的作品", artist_name="小朋友", artist_age=10, 
                     category="其他", description=""):
        """保存作品到作品集"""
        try:
            # 生成唯一ID
            artwork_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            # 创建作品目录
            artwork_dir = os.path.join(self.gallery_folder, artwork_id)
            os.makedirs(artwork_dir, exist_ok=True)
            
            # 复制图片文件
            original_filename = None
            generated_filename = f"generated_{artwork_id}.png"
            
            # 只有当原始图片存在时才复制
            if original_image_path and os.path.exists(original_image_path):
                original_filename = f"original_{artwork_id}.png"
                original_dest = os.path.join(artwork_dir, original_filename)
                shutil.copy2(original_image_path, original_dest)
            
            generated_dest = os.path.join(artwork_dir, generated_filename)
            shutil.copy2(generated_image_path, generated_dest)
            
            # 处理3D模型文件（如果存在）
            model_filename = None
            if model_path and os.path.exists(model_path):
                model_filename = f"model_{artwork_id}.glb"
                model_dest = os.path.join(artwork_dir, model_filename)
                shutil.copy2(model_path, model_dest)
            
            # 创建作品数据
            artwork_data = {
                'id': artwork_id,
                'title': title,
                'artist_name': artist_name,
                'artist_age': artist_age,
                'category': category,
                'description': description,
                'created_at': timestamp.isoformat(),
                'original_image': f"gallery/{artwork_id}/{original_filename}" if original_filename else None,
                'generated_image': f"gallery/{artwork_id}/{generated_filename}",
                'model_file': f"gallery/{artwork_id}/{model_filename}" if model_filename else None,
                'likes': 0,
                'views': 0
            }
            
            # 加载现有数据并添加新作品
            gallery_data = self.load_gallery_data()
            gallery_data.insert(0, artwork_data)  # 新作品排在前面
            
            # 保存数据
            self.save_gallery_data(gallery_data)
            
            return {
                'success': True,
                'artwork_id': artwork_id,
                'message': '作品已成功保存到作品集！'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'保存作品失败: {str(e)}'
            }
    
    def get_all_artworks(self, category=None, limit=None):
        """获取所有作品"""
        data = self.load_gallery_data()
        
        # 按分类筛选
        if category and category != 'all':
            data = [artwork for artwork in data if artwork.get('category') == category]
        
        # 限制数量
        if limit:
            data = data[:limit]
            
        return data
    
    def get_artwork_by_id(self, artwork_id):
        """根据ID获取作品"""
        data = self.load_gallery_data()
        for artwork in data:
            if artwork['id'] == artwork_id:
                return artwork
        return None
    
    def increment_views(self, artwork_id):
        """增加浏览次数"""
        data = self.load_gallery_data()
        for artwork in data:
            if artwork['id'] == artwork_id:
                artwork['views'] = artwork.get('views', 0) + 1
                self.save_gallery_data(data)
                break
    
    def toggle_like(self, artwork_id):
        """切换点赞状态（简化版本，实际应该基于用户）"""
        data = self.load_gallery_data()
        for artwork in data:
            if artwork['id'] == artwork_id:
                artwork['likes'] = artwork.get('likes', 0) + 1
                self.save_gallery_data(data)
                return artwork['likes']
        return 0