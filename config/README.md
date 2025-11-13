# 配置文件目录

本目录包含生产环境和服务器配置文件。

## 文件说明

- `gunicorn_config.py` - Gunicorn WSGI服务器配置
  - 工作进程数量
  - 超时设置
  - 日志配置
  
- `production_config.py` - 生产环境配置
  - 数据库连接
  - 安全设置
  - 性能优化参数

## 使用说明

### Gunicorn配置

```bash
# 使用配置文件启动Gunicorn
gunicorn -c config/gunicorn_config.py app:app
```

### 生产配置

生产环境配置会在部署时自动加载。
