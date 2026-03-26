# 技术栈说明

## 后端框架
- **FastAPI** (v0.115.x) - 现代异步 Python Web 框架，支持自动 API 文档生成
- **Uvicorn** - ASGI 服务器，用于运行 FastAPI 应用

## 数据验证
- **Pydantic** (v2.x) - 数据模型定义与校验（FastAPI 内置依赖）

## 前端
- **Jinja2** - 服务端模板渲染
- **原生 HTML + CSS + JavaScript** - 轻量前端，无需复杂框架

## 数据处理
- **openpyxl** - Excel 文件读取与解析
- **python-multipart** - 文件上传支持

## 外部 API 调用
- **httpx** - 异步 HTTP 客户端，用于调用外部服务接口

## 测试
- **pytest** - 单元测试框架
- **pytest-asyncio** - 异步测试支持
- **httpx** - 用于 FastAPI TestClient

## 项目结构
```
├── TECH_STACK.md          # 技术栈说明（本文件）
├── PRD.md                 # 需求文档
├── main.py                # 应用入口
├── pyproject.toml         # 项目配置
├── app/
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py      # API 路由定义
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py     # Pydantic 数据模型
│   ├── services/
│   │   ├── __init__.py
│   │   ├── parser.py      # 内容解析服务
│   │   ├── extractor.py   # 订单信息提取服务
│   │   ├── validator.py   # 数据校验服务
│   │   └── processor.py   # 主处理流程编排
│   ├── external/
│   │   ├── __init__.py
│   │   ├── ai_client.py   # AI 解析接口客户端
│   │   ├── customer_client.py  # 客户查询接口客户端
│   │   ├── inventory_client.py # 库存查询接口客户端
│   │   └── price_client.py     # 价格查询接口客户端
│   ├── static/
│   │   ├── style.css      # 样式文件
│   │   └── app.js         # 前端交互逻辑
│   └── templates/
│       └── index.html     # 主页面模板
└── tests/
    ├── __init__.py
    ├── test_parser.py     # 解析服务测试
    ├── test_validator.py  # 校验服务测试
    └── test_api.py        # API 接口测试
```

## Python 版本
- Python >= 3.13
