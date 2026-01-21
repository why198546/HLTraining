# 测试文件目录

本目录包含项目的正式测试文件。

## 📋 测试文件说明

### test_api_response_format.py
- **功能**：测试后端API返回值格式
- **用途**：验证 `detected_features` 等字段的数据结构
- **运行**：`python tests/test_api_response_format.py`

### test_feature_detection.py
- **功能**：测试特征检测和变化生成逻辑
- **用途**：验证核心业务逻辑，包括10个特征的检测和变化生成
- **运行**：`python tests/test_feature_detection.py`

## 🚀 运行测试

```bash
# 激活虚拟环境
.\activate.ps1

# 运行单个测试
python tests/test_api_response_format.py

# 运行所有测试
python -m pytest tests/
```

## 📝 编写新测试

新的测试文件应遵循以下命名规范：
- 文件名：`test_<feature_name>.py`
- 测试函数：`test_<specific_function>()`
- 放置位置：`tests/` 目录

## 📚 相关文档

- 归档的调试文件：`archived/tests/`
- 项目文档：`docs/`
