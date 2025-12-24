"""测试路径映射"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils import normalize_path_for_url

# 测试各种路径格式
test_paths = [
    "uploads/3d_models/test.glb",
    "uploads\\3d_models\\test.glb",
    "models/test.glb",
    "models\\test.glb",
    "D:\\Code\\HLTraining\\uploads\\3d_models\\test.glb",
]

print("=" * 60)
print("测试路径标准化函数")
print("=" * 60)

for path in test_paths:
    normalized = normalize_path_for_url(path)
    print(f"\n输入: {path}")
    print(f"输出: {normalized}")
    print(f"✅ 应该是: /uploads/3d_models/test.glb")

print("\n" + "=" * 60)
